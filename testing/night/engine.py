"""Engine driver: one UCI process, one move at a time, browser-safe budget."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import chess

from controller.book import BookError, OpeningBook
from controller.engine_client import EngineClient, EngineError, SearchInfo
from controller.game import emergency_priority
from controller.runtime import auto_profile, has_syzygy, runtime_options
from testing.night.config import RunSpec


@dataclass
class MoveChoice:
    uci: str
    san: str
    source: str  # book | engine | fallback
    elapsed_ms: int
    info: SearchInfo | None = None


class EngineDriver:
    def __init__(self, spec: RunSpec):
        if not spec.engine.exists():
            raise FileNotFoundError(f"engine não encontrado: {spec.engine}")
        if not spec.engine.is_file():
            raise FileNotFoundError(f"engine não é arquivo: {spec.engine}")
        self.spec = spec
        self.book: OpeningBook | None = None
        if spec.book and Path(spec.book).exists():
            try:
                self.book = OpeningBook(spec.book)
            except BookError:
                self.book = None
        self.engine: EngineClient | None = None
        self.options: dict[str, int | str] = {}

    # --- lifecycle ---------------------------------------------------------

    def open(self) -> None:
        self.options = self._options()
        self._start()

    def _options(self) -> dict[str, int | str]:
        auto_threads, auto_hash = auto_profile()
        options = runtime_options(
            self.spec.syzygy,
            threads=self.spec.threads
            if self.spec.threads is not None
            else auto_threads,
            hash_mb=self.spec.hash_mb if self.spec.hash_mb is not None else auto_hash,
        )
        # The browser path needs a small UCI allowance, not the 4 s physical
        # board reserve used by the tournament controller.
        options["Move Overhead"] = self.spec.move_overhead_ms
        if not has_syzygy(self.spec.syzygy):
            options.pop("SyzygyPath", None)
        return options

    def _start(self) -> None:
        self.engine = EngineClient(self.spec.engine)
        self.engine.start()
        self.engine.handshake(timeout=10)
        for name, value in self.options.items():
            self.engine.set_option(name, value)
        self.engine.is_ready(timeout=30)
        self.engine.send("ucinewgame")
        self.engine.is_ready(timeout=30)

    def _restart(self) -> None:
        if self.engine is not None:
            try:
                self.engine.quit()
            except (EngineError, OSError):
                pass
        self._start()

    def close(self) -> None:
        if self.engine is not None:
            try:
                self.engine.quit()
            except (EngineError, OSError):
                pass
            self.engine = None
        if self.book is not None:
            self.book.close()
            self.book = None

    # --- move selection ----------------------------------------------------

    def choose(
        self,
        board: chess.Board,
        our_color: chess.Color,
        wtime_ms: int,
        btime_ms: int,
        inc_ms: int,
    ) -> MoveChoice:
        started = time.monotonic()

        book_move = self._book_move(board)
        if book_move is not None:
            return MoveChoice(
                uci=book_move.uci(),
                san=board.san(book_move),
                source="book",
                elapsed_ms=int((time.monotonic() - started) * 1000),
            )

        try:
            return self._search(board, our_color, wtime_ms, btime_ms, inc_ms, started)
        except (EngineError, OSError) as first:
            try:
                self._restart()
                return self._search(
                    board, our_color, wtime_ms, btime_ms, inc_ms, started
                )
            except (EngineError, OSError):
                move = max(
                    board.legal_moves, key=lambda m: emergency_priority(board, m)
                )
                return MoveChoice(
                    uci=move.uci(),
                    san=board.san(move),
                    source="fallback",
                    elapsed_ms=int((time.monotonic() - started) * 1000),
                    info=None,
                )
            finally:
                # Keep the original failure visible in logs through the source.
                _ = first

    def _book_move(self, board: chess.Board) -> chess.Move | None:
        if self.book is None:
            return None
        move = self.book.pick(board)
        if move is not None and move in board.legal_moves:
            return move
        return None

    def _search(
        self,
        board: chess.Board,
        our_color: chess.Color,
        wtime_ms: int,
        btime_ms: int,
        inc_ms: int,
        started: float,
    ) -> MoveChoice:
        assert self.engine is not None
        remaining = wtime_ms if our_color == chess.WHITE else btime_ms
        remaining = max(1, remaining)
        # Hard controller cap only; YoulossTM inside the engine chooses the
        # actual target. Leave 1.5 s for click handling and clock drain.
        hard_cap_ms = max(400, min(remaining * 0.25, remaining - 1500))
        if self.spec.max_move_ms:
            hard_cap_ms = min(hard_cap_ms, self.spec.max_move_ms)
        timeout_s = hard_cap_ms / 1000.0
        go = (
            f"go wtime {max(1, wtime_ms)} btime {max(0, btime_ms)} "
            f"winc {inc_ms} binc {inc_ms}"
        )
        info = self.engine.search(
            f"position fen {board.fen()}",
            go,
            timeout_s,
            stop_grace=1.0,
        )
        try:
            move = chess.Move.from_uci(info.bestmove)
        except ValueError as exc:
            raise EngineError(f"bestmove malformado: {info.bestmove!r}") from exc
        if move not in board.legal_moves:
            raise EngineError(f"engine devolveu lance ilegal: {info.bestmove}")
        return MoveChoice(
            uci=move.uci(),
            san=board.san(move),
            source="engine",
            elapsed_ms=int((time.monotonic() - started) * 1000),
            info=info,
        )

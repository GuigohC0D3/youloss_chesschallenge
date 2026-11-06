"""Interface local: tabuleiro + campo do lance do adversário.

`python -m controller.web` sobe um servidor só em 127.0.0.1 e abre o navegador.
Digitar o lance do adversário dispara a busca; nosso lance aparece em seguida e
já entra no tabuleiro. Sem rede externa e sem dependências além de python-chess.

O relógio físico é a referência. O interno é estimativa: cada transição desconta
`clock_latency_s` (digitar o lance dele; executar o nosso), e o operador corrige
pela tela quando divergir.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import webbrowser
from dataclasses import dataclass
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

import chess
import chess.svg

from controller.book import OpeningBook
from controller.clock import ClockFormatError, GameClock, parse_mmss, parse_tc
from controller.engine_client import EngineClient, EngineError, SearchInfo
from controller.game import (
    MAX_THINK_FRACTION,
    MIN_USEFUL_SEARCH_MS,
    STOP_GRACE_S,
    emergency_priority,
)
from controller.game_log import GameLog, format_eval, log_path
from controller.main import DEFAULT_BOOK, DEFAULT_ENGINE, DEFAULT_LOGS, DEFAULT_SYZYGY, open_engine
from controller.runtime import auto_profile, has_syzygy, runtime_options
from controller.state import (
    GameState,
    StateError,
    latest_unfinished,
    load_state,
    save_state,
    state_path_for,
)

UI_FILE = Path(__file__).with_name("web_ui.html")
MAX_BODY_BYTES = 64 * 1024
_COORD_MOVE = re.compile(r"^([a-h][1-8])[-x]?([a-h][1-8])=?([a-z]?)$")
# Letras em português: Rei, Dama, Torre, Bispo, Cavalo.
_PT_PIECE = {"R": "K", "D": "Q", "T": "R", "C": "N", "B": "B"}
_PT_PROMOTION = {"d": "q", "t": "r", "c": "n"}


class MoveInputError(ValueError):
    pass


class ActionError(Exception):
    """Ação recusada; a mensagem vai direto para o operador."""


def _try_san(board: chess.Board, text: str) -> chess.Move | None:
    try:
        return board.parse_san(text)
    except ValueError:
        return None


def _portuguese_san(text: str) -> str:
    out = _PT_PIECE.get(text[0], text[0]) + text[1:]
    return re.sub(r"=([DTCB])", lambda m: "=" + _PT_PIECE[m.group(1)], out)


def parse_move(board: chess.Board, raw: str) -> chess.Move:
    """Aceita e2e4, e2-e4, e7e8q, e7e8=D, Nf3, Cf3, exd5, O-O e 0-0."""
    text = raw.strip().replace(" ", "")
    if not text:
        raise MoveInputError("digite o lance do adversário")
    if re.fullmatch(r"[0oO]-?[0oO](-?[0oO])?[+#]?", text):
        text = "O-O-O" if text.lower().count("o") + text.count("0") == 3 else "O-O"

    coord = _COORD_MOVE.match(text.lower())
    if coord:
        origin, target, promo = coord.groups()
        promo = _PT_PROMOTION.get(promo, promo)
        try:
            move = chess.Move.from_uci(origin + target + promo)
        except ValueError as exc:
            raise MoveInputError(f"promoção inválida em {raw!r}") from exc
        if move in board.legal_moves:
            return move
        if not promo and chess.Move.from_uci(origin + target + "q") in board.legal_moves:
            raise MoveInputError(f"{raw}: falta a peça da promoção (ex.: {origin}{target}q)")
        raise MoveInputError(f"{raw}: lance ilegal nesta posição")

    english = _try_san(board, text)
    portuguese = _try_san(board, _portuguese_san(text))
    if english and portuguese and english != portuguese:
        raise MoveInputError(
            f"{raw} é ambíguo entre inglês e português; digite casa de origem e destino"
        )
    move = english or portuguese
    if move is None:
        raise MoveInputError(f"{raw}: lance ilegal ou não reconhecido nesta posição")
    return move


@dataclass
class OurMove:
    uci: str
    san: str
    source: str
    depth: int = 0
    nodes: int = 0
    evaluation: str = ""
    pv: str = ""


class WebSession:
    """Uma partida por vez. Métodos públicos são seguros entre threads HTTP."""

    def __init__(
        self,
        engine_factory: Callable[[], EngineClient],
        options: dict[str, int | str],
        logs_dir: Path,
        book_path: Path | None = None,
        clock_latency_s: float = 2.0,
        ponder: bool = True,
    ):
        self._factory = engine_factory
        self.ponder = ponder
        # Lance do adversário previsto enquanto o engine pensa no tempo dele.
        self._ponder_move: chess.Move | None = None
        self.options = options
        self.logs_dir = Path(logs_dir)
        self.book_path = book_path
        self.latency_ms = round(clock_latency_s * 1000)
        self._lock = threading.RLock()
        self.engine: EngineClient | None = None
        self.engine_name = "?"
        self.book = OpeningBook(book_path)
        self.state: GameState | None = None
        self.state_path: Path | None = None
        self.board = chess.Board()
        self.clock: GameClock | None = None
        self.log: GameLog | None = None
        self.thinking = False
        self.our_move: OurMove | None = None
        self.warning = ""
        self.version = 0
        self._generation = 0
        self._worker: threading.Thread | None = None

    # --- ciclo de vida -----------------------------------------------------

    def open(self) -> str:
        self.engine = self._factory()
        self.engine_name = open_engine(self.engine, self.options)
        return self.engine_name

    def close(self) -> None:
        with self._lock:
            self._generation += 1
            worker = self._worker
            if self.thinking and self.engine is not None:
                self._safe_stop()
        if worker is not None:
            worker.join(STOP_GRACE_S + 1)
        with self._lock:
            if self.engine is not None:
                self._cancel_ponder()
            if self.state is not None and not self.state.finished:
                self._save()
            self._close_log()
            if self.engine is not None:
                self.engine.quit()
            self.book.close()

    def _close_log(self) -> None:
        if self.log is not None:
            self.log.close()
            self.log = None

    def _safe_stop(self) -> None:
        try:
            self.engine.send("stop")
        except (EngineError, OSError):
            pass

    def _cancel_ponder(self) -> None:
        """Encerra o ponder e consome o `bestmove` dele, para não confundir a próxima busca."""
        if self._ponder_move is None:
            return
        self._ponder_move = None
        try:
            self.engine.send("stop")
            self.engine.read_until("bestmove", STOP_GRACE_S + 1)
        except (EngineError, OSError) as exc:
            if self.log is not None:
                self.log.note(f"incident ponder stop failure={exc}; restart")
            try:
                self.engine.quit()
            except (EngineError, OSError):
                pass
            try:
                self.open()
            except (EngineError, OSError):
                pass  # a próxima busca tenta de novo e, se falhar, sai lance de emergência

    def _start_ponder(self, info: SearchInfo | None) -> None:
        """Depois do nosso lance, pensa na posição após o lance previsto do adversário."""
        if not self.ponder or info is None or not info.ponder or self.state.finished:
            return
        try:
            expected = chess.Move.from_uci(info.ponder)
        except ValueError:
            return
        if expected not in self.board.legal_moves:
            return
        us = self._us()
        ours = max(self.clock.remaining(us), 0)
        theirs = max(self.clock.remaining(not us), 0)
        wtime, btime = (ours, theirs) if us == chess.WHITE else (theirs, ours)
        inc = self.clock.inc_ms
        moves = [m.uci() for m in self.board.move_stack] + [expected.uci()]
        try:
            self.engine.send(f"position fen {self.state.start_fen} moves " + " ".join(moves))
            self.engine.send(f"go ponder wtime {wtime} btime {btime} winc {inc} binc {inc}")
        except (EngineError, OSError):
            return
        self._ponder_move = expected

    def _touch(self) -> None:
        self.version += 1

    def _us(self) -> chess.Color:
        return chess.WHITE if self.state.color == "white" else chess.BLACK

    def _save(self) -> None:
        self.state.moves = [m.uci() for m in self.board.move_stack]
        self.state.white_ms = self.clock.remaining(chess.WHITE)
        self.state.black_ms = self.clock.remaining(chess.BLACK)
        save_state(self.state, self.state_path)

    def _require_game(self) -> None:
        if self.state is None or self.state.finished:
            raise ActionError("nenhuma partida em andamento")

    def _charge_latency(self, color: chess.Color) -> None:
        self.clock.set(color, self.clock.remaining(color) - self.latency_ms)

    # --- ações -------------------------------------------------------------

    def start_game(self, color: str, opponent: str, game: int, tc: str) -> None:
        if color not in ("white", "black"):
            raise ActionError("escolha brancas ou pretas")
        opponent = opponent.strip() or "adversario"
        try:
            base_ms, inc_ms = parse_tc(tc)
        except ClockFormatError as exc:
            raise ActionError(f"tempo inválido: {exc}") from exc
        if game < 1:
            raise ActionError("número da partida inválido")
        with self._lock:
            if self.state is not None and not self.state.finished:
                raise ActionError("já existe partida em andamento; encerre-a antes")
            path = log_path(self.logs_dir, opponent, game, date.today())
            if path.exists():
                raise ActionError(
                    f"já existe log para {opponent}, partida {game} hoje; use outro número"
                )
            self._close_log()
            self.state = GameState(
                color=color, opponent=opponent, game=game, base_ms=base_ms,
                inc_ms=inc_ms, white_ms=base_ms, black_ms=base_ms, log_path=str(path),
            )
            self.state_path = state_path_for(path)
            self.board = chess.Board()
            self.clock = GameClock(base_ms, inc_ms)
            self.our_move = None
            self.warning = ""
            self.log = GameLog(path)
            self.log.header(
                engine=self.engine_name, color=color, opponent=opponent, game=game,
                tc=tc, start_fen=self.state.start_fen,
            )
            self._new_engine_game()
            self.clock.start(chess.WHITE)
            self._save()
            self._touch()
            if self._us() == chess.WHITE:
                self._start_thinking()

    def resume_game(self) -> None:
        with self._lock:
            if self.state is not None and not self.state.finished:
                raise ActionError("já existe partida em andamento")
            path = latest_unfinished(self.logs_dir)
            if path is None:
                raise ActionError("nenhuma partida para retomar")
            try:
                state = load_state(path)
            except StateError as exc:
                raise ActionError(f"estado inválido: {exc}") from exc
            self._close_log()
            self.state, self.state_path = state, path
            self.board = state.board()
            self.clock = GameClock(state.base_ms, state.inc_ms)
            self.clock.set(chess.WHITE, state.white_ms)
            self.clock.set(chess.BLACK, state.black_ms)
            self.our_move = None
            self.warning = "Partida retomada: confira o tabuleiro e corrija os relógios."
            self.log = GameLog(state.log_path)
            self.log.note("resume via web")
            self._new_engine_game()
            self.clock.start(self.board.turn)
            self._touch()
            if self.board.turn == self._us():
                self._start_thinking()

    def _new_engine_game(self) -> None:
        self._cancel_ponder()
        self.engine.send("ucinewgame")
        self.engine.is_ready(timeout=30)

    def opponent_move(self, text: str) -> None:
        with self._lock:
            self._require_game()
            if self.thinking:
                raise ActionError("aguarde o nosso lance")
            if self.board.turn == self._us():
                raise ActionError("é a nossa vez; use Desfazer se houve engano")
            try:
                move = parse_move(self.board, text)
            except MoveInputError as exc:
                raise ActionError(str(exc)) from exc
            mover = "white" if self.board.turn == chess.WHITE else "black"
            move_no = self.board.fullmove_number
            self.board.push(move)
            spent = self.clock.press()
            self._charge_latency(self._us())
            self.log.opponent_move(move_no, mover, move.uci(), spent)
            self.our_move = None
            self._save()
            self._touch()
            if not self._finish_if_over():
                self._start_thinking()

    def undo(self) -> None:
        """Volta para antes do último lance do adversário, para redigitá-lo."""
        with self._lock:
            if self.state is None:
                raise ActionError("nenhuma partida em andamento")
            if not self.board.move_stack:
                raise ActionError("nada a desfazer")
            worker = None
            if self.thinking:
                self._generation += 1
                self._safe_stop()
                worker = self._worker
        if worker is not None:
            worker.join(STOP_GRACE_S + 1)
        with self._lock:
            self._cancel_ponder()
            us = self._us()
            popped = []
            if self.board.turn != us:  # último lance foi o nosso
                popped.append(self.board.pop())
            if self.board.move_stack:  # brancas: nosso 1º lance não tem lance dele antes
                popped.append(self.board.pop())
            if self.state.finished:
                self.state.result = None
                self.state.reason = None
                if self.log is None:
                    self.log = GameLog(self.state.log_path)
            self.log.note("undo " + " ".join(m.uci() for m in popped))
            self.our_move = None
            self.clock.start(self.board.turn)
            self.warning = "Lance desfeito: confira os relógios com o físico."
            self._save()
            self._touch()
            if self.board.turn == us:
                self._start_thinking()

    def set_clock(self, ours: str, theirs: str) -> None:
        with self._lock:
            self._require_game()
            try:
                ours_ms, theirs_ms = parse_mmss(ours), parse_mmss(theirs)
            except ClockFormatError as exc:
                raise ActionError(f"use mm:ss ({exc})") from exc
            us = self._us()
            self.clock.set(us, ours_ms)
            self.clock.set(not us, theirs_ms)
            self.log.note(f"clock nos={ours} adv={theirs}")
            self.warning = ""
            self._save()
            self._touch()

    def finish(self, outcome: str, reason: str) -> None:
        with self._lock:
            self._require_game()
            if outcome == "draw":
                result = "1/2-1/2"
            elif outcome in ("win", "loss"):
                white_won = (outcome == "win") == (self.state.color == "white")
                result = "1-0" if white_won else "0-1"
            else:
                raise ActionError("resultado inválido")
            self._generation += 1
            if self.thinking:
                self._safe_stop()
            else:
                self._cancel_ponder()
            self._record_result(result, reason.strip() or "operador")

    def _record_result(self, result: str, reason: str) -> None:
        self.state.result = result
        self.state.reason = reason
        self.clock.stop()
        self.log.result(result, reason)
        self._save()
        self._touch()

    def _finish_if_over(self) -> bool:
        outcome = self.board.outcome()
        if outcome is None:
            return False
        self._record_result(outcome.result(), outcome.termination.name.lower())
        return True

    # --- busca -------------------------------------------------------------

    def _start_thinking(self) -> None:
        self.thinking = True
        self._generation += 1
        self._worker = threading.Thread(
            target=self._think,
            args=(self._generation, self.board.copy(stack=True)),
            daemon=True,
        )
        self._worker.start()

    def _think(self, generation: int, board: chess.Board) -> None:
        move: chess.Move | None = None
        source = "fallback"
        info: SearchInfo | None = None
        problem = ""
        try:
            legal = list(board.legal_moves)
            book_move = self.book.pick(board)
            will_search = len(legal) > 1 and book_move not in legal
            with self._lock:
                pondered = self._ponder_move
                hit = (
                    pondered is not None and will_search
                    and bool(board.move_stack) and board.peek() == pondered
                )
                if pondered is not None and not hit:
                    self._cancel_ponder()
                self._ponder_move = None
            if len(legal) == 1:
                move, source = legal[0], "forced"
            elif book_move in legal:
                move, source = book_move, "book"
            else:
                info = self._search_with_retry(board, legal, generation, ponderhit=hit)
                if info is not None:
                    move = chess.Move.from_uci(info.bestmove)
                    source = "ponderhit" if hit else "engine"
        except (EngineError, OSError) as exc:
            problem = f"Engine falhou ({exc}). Lance de emergência: confira antes de jogar."
        with self._lock:
            self.thinking = False
            if generation != self._generation:
                return  # desfeito ou encerrado durante a busca
            if move is None:
                move = max(
                    legal, key=lambda m: (emergency_priority(board, m), m.uci())
                )
                source = "fallback"
                if not problem:
                    problem = (
                        "Relógio interno no limite: lance imediato sem busca. "
                        "Confira o físico e corrija."
                    )
            self.warning = problem or self.warning
            self._apply_our_move(move, source, info)

    def _search_with_retry(
        self, board: chess.Board, legal: list[chess.Move], generation: int,
        ponderhit: bool = False,
    ) -> SearchInfo | None:
        try:
            if ponderhit:
                return self._ponderhit_once(board, legal)
            return self._search_once(board, legal)
        except (EngineError, OSError) as first:
            with self._lock:
                if generation != self._generation:
                    raise
                if self.log is not None:
                    self.log.note(f"incident engine failure={first}; restart")
                try:
                    self.engine.quit()
                except (EngineError, OSError):
                    pass
                self.open()
            return self._search_once(board, legal)

    def _search_once(
        self, board: chess.Board, legal: list[chess.Move]
    ) -> SearchInfo | None:
        us = board.turn
        ours = self.clock.remaining(us)
        available = ours - round(STOP_GRACE_S * 1000) - self.latency_ms
        if ours <= 0 or available < MIN_USEFUL_SEARCH_MS:
            return None
        theirs = max(self.clock.remaining(not us), 0)
        wtime, btime = (ours, theirs) if us == chess.WHITE else (theirs, ours)
        inc = self.clock.inc_ms
        position = f"position fen {self.state.start_fen}"
        if board.move_stack:
            position += " moves " + " ".join(m.uci() for m in board.move_stack)
        timeout = min(ours * MAX_THINK_FRACTION, available) / 1000
        info = self.engine.search(
            position,
            f"go wtime {wtime} btime {btime} winc {inc} binc {inc}",
            timeout,
            stop_grace=STOP_GRACE_S,
        )
        return self._checked(info, legal)

    def _ponderhit_once(
        self, board: chess.Board, legal: list[chess.Move]
    ) -> SearchInfo:
        """O adversário jogou o lance previsto: a busca do ponder vira a nossa."""
        ours = self.clock.remaining(board.turn)
        available = ours - round(STOP_GRACE_S * 1000) - self.latency_ms
        if ours <= 0 or available < MIN_USEFUL_SEARCH_MS:
            # Sem tempo para continuar: o que o ponder já achou vale mais que um lance cego.
            self.engine.send("stop")
            return self._checked(self.engine.wait_bestmove(STOP_GRACE_S, STOP_GRACE_S), legal)
        self.engine.send("ponderhit")
        timeout = min(ours * MAX_THINK_FRACTION, available) / 1000
        return self._checked(self.engine.wait_bestmove(timeout, STOP_GRACE_S), legal)

    def _checked(self, info: SearchInfo, legal: list[chess.Move]) -> SearchInfo:
        try:
            move = chess.Move.from_uci(info.bestmove)
        except ValueError as exc:
            raise EngineError(f"bestmove malformado: {info.bestmove!r}") from exc
        if move not in legal:
            raise EngineError(f"engine devolveu lance ilegal: {info.bestmove}")
        return info

    def _apply_our_move(
        self, move: chess.Move, source: str, info: SearchInfo | None
    ) -> None:
        mover = "white" if self.board.turn == chess.WHITE else "black"
        move_no = self.board.fullmove_number
        san = self.board.san(move)
        self.our_move = OurMove(uci=move.uci(), san=san, source=source)
        if info is not None:
            self.our_move.depth = info.depth
            self.our_move.nodes = info.nodes
            self.our_move.evaluation = format_eval(info.score_cp, info.score_mate)
            self.our_move.pv = " ".join(info.pv[:6])
        self.board.push(move)
        spent = self.clock.press()
        self._charge_latency(not self.board.turn)
        self.log.our_move(move_no, mover, move.uci(), source, spent, info)
        self._save()
        self._touch()
        if not self._finish_if_over():
            self._start_ponder(info)

    # --- leitura -----------------------------------------------------------

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            data: dict[str, object] = {
                "version": self.version,
                "engine": self.engine_name,
                "threads": self.options.get("Threads"),
                "hash_mb": self.options.get("Hash"),
                "syzygy": "SyzygyPath" in self.options,
            }
            if self.state is None:
                data["phase"] = "setup"
                data["resume"] = self._resume_candidate()
                return data
            us = self._us()
            data.update(
                phase="finished" if self.state.finished else "playing",
                thinking=self.thinking,
                color=self.state.color,
                opponent=self.state.opponent,
                game=self.state.game,
                fen=self.board.fen(),
                our_turn=self.board.turn == us,
                ours_ms=self.clock.remaining(us),
                theirs_ms=self.clock.remaining(not us),
                running=(
                    None if self.clock.running is None
                    else "ours" if self.clock.running == us else "theirs"
                ),
                our_move=self._our_move_dict(),
                moves=self._san_moves(),
                warning=self.warning,
                result=self.state.result,
                reason=self.state.reason,
                claim_draw=not self.state.finished and self.board.can_claim_draw(),
                log=self.state.log_path,
                board_svg=self._board_svg(us),
            )
            data["resume"] = self._resume_candidate() if self.state.finished else None
            return data

    def _resume_candidate(self) -> dict[str, object] | None:
        path = latest_unfinished(self.logs_dir)
        if path is None:
            return None
        try:
            state = load_state(path)
        except StateError:
            return None
        return {"opponent": state.opponent, "game": state.game, "plies": len(state.moves)}

    def _our_move_dict(self) -> dict[str, object] | None:
        if self.our_move is None:
            return None
        move = self.our_move
        return {
            "san": move.san,
            "from": move.uci[:2],
            "to": move.uci[2:4],
            "promotion": move.uci[4:],
            "source": move.source,
            "depth": move.depth,
            "nodes": move.nodes,
            "eval": move.evaluation,
            "pv": move.pv,
        }

    def _san_moves(self) -> list[str]:
        replay = chess.Board(self.state.start_fen)
        out = []
        for move in self.board.move_stack:
            out.append(replay.san(move))
            replay.push(move)
        return out

    def _board_svg(self, us: chess.Color) -> str:
        last = self.board.peek() if self.board.move_stack else None
        arrows = []
        if self.our_move is not None and last is not None and last.uci() == self.our_move.uci:
            arrows.append(chess.svg.Arrow(last.from_square, last.to_square, color="#1f6f43cc"))
        check = self.board.king(self.board.turn) if self.board.is_check() else None
        return chess.svg.board(
            self.board,
            orientation=us,
            lastmove=last,
            arrows=arrows,
            check=check,
            colors={
                "square light": "#ece6d6",
                "square dark": "#8a9a7b",
                "square light lastmove": "#e3d27a",
                "square dark lastmove": "#b5ad56",
                "margin": "#23282b",
                "coord": "#f2f0ea",
            },
        )


class _Handler(BaseHTTPRequestHandler):
    session: WebSession
    allowed_hosts: set[str]

    def log_message(self, *args: object) -> None:
        pass

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: object) -> None:
        self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

    def _host_ok(self) -> bool:
        # Bloqueia DNS rebinding: outra página não fala com o servidor pelo nome dela.
        return self.headers.get("Host", "") in self.allowed_hosts

    def do_GET(self) -> None:
        if not self._host_ok():
            self._json(403, {"error": "host recusado"})
        elif self.path == "/":
            self._send(200, UI_FILE.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/state":
            self._json(200, self.session.snapshot())
        else:
            self._json(404, {"error": "não encontrado"})

    def do_POST(self) -> None:
        # application/json força preflight CORS, que nunca é aprovado aqui.
        if not self._host_ok() or self.headers.get("Content-Type") != "application/json":
            self._json(403, {"error": "requisição recusada"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY_BYTES:
            self._json(413, {"error": "corpo grande demais"})
            return
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(body, dict):
                raise ValueError
            self._dispatch(body)
        except ValueError:
            self._json(400, {"error": "requisição inválida"})
        except ActionError as exc:
            self._json(400, {"error": str(exc)})
        except (EngineError, OSError) as exc:
            self._json(500, {"error": f"falha: {exc}"})
        else:
            self._json(200, self.session.snapshot())

    def _dispatch(self, body: dict[str, object]) -> None:
        s = self.session
        if self.path == "/api/start":
            s.start_game(
                str(body.get("color", "")), str(body.get("opponent", "")),
                int(body.get("game", 1)), str(body.get("tc", "1500+0")),
            )
        elif self.path == "/api/move":
            s.opponent_move(str(body.get("move", "")))
        elif self.path == "/api/undo":
            s.undo()
        elif self.path == "/api/clock":
            s.set_clock(str(body.get("ours", "")), str(body.get("theirs", "")))
        elif self.path == "/api/finish":
            s.finish(str(body.get("outcome", "")), str(body.get("reason", "")))
        elif self.path == "/api/resume":
            s.resume_game()
        else:
            raise ActionError("rota desconhecida")


def make_server(session: WebSession, port: int) -> ThreadingHTTPServer:
    """Liga em 127.0.0.1, tentando portas seguintes se a pedida estiver ocupada."""
    last_error: OSError | None = None
    for candidate in range(port, port + 10) if port else [0]:
        handler = type("Handler", (_Handler,), {"session": session, "allowed_hosts": set()})
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), handler)
        except OSError as exc:
            last_error = exc
            continue
        bound = server.server_address[1]
        handler.allowed_hosts = {f"127.0.0.1:{bound}", f"localhost:{bound}"}
        server.daemon_threads = True
        return server
    raise OSError(f"nenhuma porta livre a partir de {port}: {last_error}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m controller.web")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true")
    p.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    p.add_argument("--syzygy", type=Path, default=DEFAULT_SYZYGY)
    p.add_argument("--logs", type=Path, default=DEFAULT_LOGS)
    p.add_argument("--book", type=Path)
    p.add_argument("--threads", type=int)
    p.add_argument("--hash", type=int, dest="hash_mb", metavar="MB")
    p.add_argument("--clock-latency", type=float, default=2.0)
    p.add_argument("--no-ponder", action="store_true", help="não pensa no tempo do adversário")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    auto_threads, auto_hash = auto_profile()
    options = runtime_options(
        args.syzygy,
        threads=args.threads if args.threads is not None else auto_threads,
        hash_mb=args.hash_mb if args.hash_mb is not None else auto_hash,
    )
    book = args.book or (DEFAULT_BOOK if DEFAULT_BOOK.exists() else None)
    session = WebSession(
        lambda: EngineClient(args.engine), options, args.logs, book, args.clock_latency,
        ponder=not args.no_ponder,
    )
    try:
        name = session.open()
    except EngineError as exc:
        print(f"ERRO: engine não abriu: {exc}", file=sys.stderr)
        return 2
    server = make_server(session, args.port)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    tablebase = "com" if has_syzygy(args.syzygy) else "sem"
    print(
        f"{name} | {options['Threads']} threads | {options['Hash']} MiB | "
        f"{tablebase} tablebases\nAbra {url}  (Ctrl-C encerra)",
        flush=True,
    )
    if not args.no_browser:
        threading.Timer(0.3, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nencerrando; a partida fica salva para retomar", flush=True)
    finally:
        server.server_close()
        session.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Series runner: game lifecycle, turn loop, recovery, and telemetry."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import chess

from controller.clock import parse_tc
from testing.night.board import BoardError, board_from_san, cross_check, result_for
from testing.night.chesscom import (
    ChessComError,
    ChessComSession,
    MoveRejected,
    Snapshot,
)
from testing.night.config import RunSpec
from testing.night.engine import EngineDriver, MoveChoice
from testing.night.recorder import Recorder


class ClockTracker:
    """Fallback clock estimate; parsed page clocks always win."""

    def __init__(self, base_ms: int, inc_ms: int, now=time.monotonic):
        self._now = now
        self.base_ms = base_ms
        self.inc_ms = inc_ms
        self._ms = {chess.WHITE: base_ms, chess.BLACK: base_ms}
        self._running: chess.Color | None = chess.WHITE
        self._since = now()

    def _settle(self) -> None:
        if self._running is not None:
            t = self._now()
            self._ms[self._running] -= int((t - self._since) * 1000)
            self._since = t

    def remaining(self, color: chess.Color) -> int:
        ms = self._ms[color]
        if color == self._running:
            ms -= int((self._now() - self._since) * 1000)
        return ms

    def press(self, mover: chess.Color) -> None:
        self._settle()
        self._ms[mover] += self.inc_ms
        self._running = not mover
        self._since = self._now()

    def sync(self, white_ms: int | None, black_ms: int | None) -> None:
        if white_ms is not None:
            self._ms[chess.WHITE] = white_ms
        if black_ms is not None:
            self._ms[chess.BLACK] = black_ms


def modal_result(
    text: str, our_username: str, our_color: chess.Color
) -> tuple[str, str] | None:
    low = (text or "").lower()
    if not low:
        return None
    if "draw" in low or "empate" in low:
        return "1/2-1/2", "draw"
    if "you won" in low or "você venceu" in low:
        return ("1-0" if our_color == chess.WHITE else "0-1"), "win"
    if "you lost" in low or "você perdeu" in low:
        return ("0-1" if our_color == chess.WHITE else "1-0"), "loss"
    if our_username and f"{our_username.lower()} won" in low:
        return ("1-0" if our_color == chess.WHITE else "0-1"), "win"
    if " won" in low or " venceu" in low:
        return ("0-1" if our_color == chess.WHITE else "1-0"), "loss"
    if "resign" in low or "abandon" in low or "time out" in low or "desist" in low:
        return ("0-1" if our_color == chess.WHITE else "1-0"), "loss"
    return None


@dataclass
class GameOutcome:
    number: int
    color: str
    result: str
    reason: str
    plies: int
    pgn: Path | None
    failed: bool = False


class NightRunner:
    def __init__(self, spec: RunSpec, recorder: Recorder):
        self.spec = spec
        self.recorder = recorder
        self.engine = EngineDriver(spec)
        self.session = ChessComSession(spec)
        self.base_ms, self.inc_ms = parse_tc(spec.tc)
        self._last_engine_error = ""

    # --- lifecycle ---------------------------------------------------------

    def run(self) -> str:
        self.engine.open()
        self.recorder.event("engine_ready", options=self.engine.options)
        self.session.connect()
        try:
            self.session.ensure_logged_in(navigate=not self.spec.attach)
            initial = self.session.wait_for_board() if self.spec.attach else None
            return self._run_series(initial=initial)
        finally:
            self.session.close()
            self.engine.close()

    def _run_series(self, initial: Snapshot | None = None) -> str:
        deadline = (
            time.monotonic() + self.spec.max_hours * 3600
            if self.spec.max_hours > 0
            else None
        )
        consecutive_failures = 0
        game_no = 0
        stop = "max_games"
        snap = initial
        while True:
            if self.spec.max_games and game_no >= self.spec.max_games:
                stop = "max_games"
                break
            if deadline is not None and time.monotonic() >= deadline:
                stop = "max_hours"
                break
            game_no += 1
            desired = self._desired_color(game_no)
            try:
                if snap is None:
                    snap = self.session.start_game(desired)
                outcome = self._play_game(game_no, snap)
                if outcome.failed:
                    consecutive_failures += 1
                    snap = None
                    if consecutive_failures >= self.spec.max_consecutive_failures:
                        stop = "consecutive_failures"
                        break
                else:
                    consecutive_failures = 0
                    # Start the next game through the selector so the requested
                    # side is applied. Rematch does not guarantee color.
                    snap = None
            except (ChessComError, TimeoutError, BoardError, OSError) as exc:
                consecutive_failures += 1
                snap = None
                self._failure(game_no, type(exc).__name__, str(exc))
                if consecutive_failures >= self.spec.max_consecutive_failures:
                    stop = "consecutive_failures"
                    break
                try:
                    self.session.goto("https://www.chess.com/play/computer")
                except Exception:
                    pass
            if self.spec.pause_between_games_s:
                time.sleep(self.spec.pause_between_games_s)
        return stop

    def _desired_color(self, game_no: int) -> str:
        if self.spec.color_mode == "alternate":
            return "white" if game_no % 2 == 1 else "black"
        return self.spec.color_mode

    # --- one game ----------------------------------------------------------

    def _stabilize_board(
        self, start_fen: str, snap: Snapshot, attempts: int = 4
    ) -> tuple[chess.Board, Snapshot]:
        last_error: BoardError | None = None
        for attempt in range(attempts):
            try:
                return board_from_san(start_fen, snap.sans), snap
            except BoardError as exc:
                last_error = exc
                if attempt == attempts - 1:
                    break
                time.sleep(0.2)
                snap = self.session.snapshot()
        assert last_error is not None
        raise last_error

    def _play_game(self, number: int, snap: Snapshot) -> GameOutcome:
        our_color = snap.our_color
        start_fen = chess.STARTING_FEN
        try:
            board, snap = self._stabilize_board(start_fen, snap)
        except BoardError as exc:
            self._failure(number, "board_initial", str(exc))
            return GameOutcome(
                number=number,
                color="white" if our_color == chess.WHITE else "black",
                result="*",
                reason="board_error",
                plies=0,
                pgn=None,
                failed=True,
            )
        tracker = ClockTracker(self.base_ms, self.inc_ms)
        tracker.sync(snap.clock_ms(chess.WHITE), snap.clock_ms(chess.BLACK))
        self.recorder.game_start(
            number,
            bot=self.spec.bot,
            tc=self.spec.tc,
            color="white" if our_color == chess.WHITE else "black",
            orientation=snap.orientation,
            username=snap.our_username,
            start_fen=start_fen,
            url=snap.url,
            engine=str(self.spec.engine),
            options=self.engine.options,
        )
        started = time.monotonic()
        result = "*"
        reason = "unfinished"
        failed = False
        last_ply = snap.ply
        pending_retry = 0

        while True:
            if (
                self.spec.max_hours > 0
                and time.monotonic() - started > self.spec.max_hours * 3600
            ):
                reason = "time_cap"
                break
            snap = self.session.snapshot()
            try:
                board, snap = self._stabilize_board(start_fen, snap)
            except BoardError as exc:
                self._failure(number, "board_reconstruct", str(exc))
                failed = True
                reason = "board_error"
                break

            if snap.sans and not cross_check(board, snap.pieces):
                # The board can still be mid-animation; give it one settle
                # window before treating the mismatch as real.
                time.sleep(0.2)
                settled = self.session.snapshot()
                try:
                    settled_board = board_from_san(start_fen, settled.sans)
                except BoardError:
                    settled_board = None
                if settled_board is not None and cross_check(
                    settled_board, settled.pieces
                ):
                    snap, board = settled, settled_board
                else:
                    self.recorder.event(
                        "board_mismatch",
                        game=number,
                        ply=board.ply(),
                        fen=board.fen(),
                        source="san",
                    )

            done = result_for(board, our_color)
            if done is not None:
                result, reason = done
                break
            modal = modal_result(snap.modal_text, snap.our_username, our_color)
            if modal is not None and board.ply() > 0:
                result, reason = modal
                break

            if snap.ply > last_ply:
                self._record_new_plies(number, board, snap, last_ply, our_color)
                last_ply = snap.ply
                tracker.press(our_color if board.turn != our_color else not our_color)

            if board.turn != our_color:
                try:
                    snap = self.session.wait_for_ply(snap.ply, self.spec.move_timeout_s)
                except TimeoutError as exc:
                    self._failure(
                        number,
                        "opponent_timeout",
                        str(exc),
                        screenshot=self.session.screenshot(
                            self.recorder.failures_dir
                            / f"g{number:04d}_opponent_timeout.png"
                        ),
                    )
                    failed = True
                    reason = "opponent_timeout"
                    break
                try:
                    board, snap = self._stabilize_board(start_fen, snap)
                except BoardError as exc:
                    self._failure(number, "board_after_opponent", str(exc))
                    failed = True
                    reason = "board_error"
                    break
                done = result_for(board, our_color)
                if done is not None:
                    result, reason = done
                    break
                modal = modal_result(snap.modal_text, snap.our_username, our_color)
                if modal is not None and board.ply() > 0:
                    result, reason = modal
                    break
                continue

            # our turn
            if self.spec.dry_run:
                choice = self._choose(board, our_color, snap, tracker)
                self.recorder.event(
                    "dry_run_move",
                    game=number,
                    ply=board.ply(),
                    uci=choice.uci,
                    san=choice.san,
                    source=choice.source,
                    fen=board.fen(),
                )
                result, reason = "*", "dry_run"
                break
            try:
                choice = self._choose(board, our_color, snap, tracker)
                snap_after = self.session.play(chess.Move.from_uci(choice.uci))
            except MoveRejected as exc:
                pending_retry += 1
                self._failure(
                    number,
                    "move_rejected",
                    str(exc),
                    screenshot=self.session.screenshot(
                        self.recorder.failures_dir / f"g{number:04d}_move_rejected.png"
                    ),
                )
                if pending_retry >= self.spec.max_attempts_per_game:
                    failed = True
                    reason = "move_rejected"
                    break
                continue
            except (ChessComError, OSError) as exc:
                self._failure(number, "move_error", str(exc))
                pending_retry += 1
                if pending_retry >= self.spec.max_attempts_per_game:
                    failed = True
                    reason = "move_error"
                    break
                continue

            if snap_after.ply <= snap.ply:
                pending_retry += 1
                self._failure(number, "move_not_registered", choice.uci)
                if pending_retry >= self.spec.max_attempts_per_game:
                    failed = True
                    reason = "move_not_registered"
                    break
                continue

            self._record_our_move(
                number, board, snap_after, choice, our_color, snap, tracker
            )
            # The bot may reply before the next snapshot. Record only our ply
            # now; the following loop iteration records any reply from here.
            last_ply = snap.ply + 1
            tracker.press(our_color)
            pending_retry = 0
            if self.spec.attach and self.spec.dry_run:
                break

        pgn = self._write_game_pgn(number, start_fen, board, result, reason, our_color)
        self.recorder.game_end(
            number,
            result=result,
            reason=reason,
            color="white" if our_color == chess.WHITE else "black",
            plies=board.ply(),
            wall_s=round(time.monotonic() - started, 1),
            pgn=str(pgn) if pgn else None,
            failed=failed,
        )
        if failed:
            self.session.resign()
        return GameOutcome(
            number=number,
            color="white" if our_color == chess.WHITE else "black",
            result=result,
            reason=reason,
            plies=board.ply(),
            pgn=pgn,
            failed=failed,
        )

    # --- move plumbing -----------------------------------------------------

    def _choose(
        self,
        board: chess.Board,
        our_color: chess.Color,
        snap: Snapshot,
        tracker: ClockTracker,
    ) -> MoveChoice:
        wtime = snap.clock_ms(chess.WHITE)
        btime = snap.clock_ms(chess.BLACK)
        tracker.sync(wtime, btime)
        if wtime is None:
            wtime = tracker.remaining(chess.WHITE)
        if btime is None:
            btime = tracker.remaining(chess.BLACK)
        try:
            return self.engine.choose(board, our_color, wtime, btime, self.inc_ms)
        except Exception as exc:
            self._last_engine_error = f"{type(exc).__name__}: {exc}"
            self.recorder.event("engine_error", error=self._last_engine_error)
            raise

    def _record_new_plies(
        self,
        number: int,
        board: chess.Board,
        snap: Snapshot,
        previous_ply: int,
        our_color: chess.Color,
    ) -> None:
        replay = chess.Board(chess.STARTING_FEN)
        for san in snap.sans:
            replay.push_san(san)
        our_name = "white" if our_color == chess.WHITE else "black"
        for index in range(previous_ply, snap.ply):
            san = snap.sans[index]
            mover = "white" if index % 2 == 0 else "black"
            self.recorder.move(
                game=number,
                ply=index + 1,
                color=mover,
                san=san,
                uci=replay.move_stack[index].uci(),
                source="opponent" if mover != our_name else "ours_unrecorded",
                spent_ms=snap.spent_ms(index + 1),
                eval_before=None,
                eval_after=None,
            )

    def _record_our_move(
        self,
        number: int,
        board: chess.Board,
        after: Snapshot,
        choice: MoveChoice,
        our_color: chess.Color,
        before: Snapshot,
        tracker: ClockTracker,
    ) -> None:
        ply = before.ply + 1
        rendered = after.sans[ply - 1] if ply <= len(after.sans) else choice.san
        actual_san = rendered
        actual_uci = choice.uci
        if rendered != choice.san:
            try:
                actual_move = board.parse_san(rendered)
                actual_uci = actual_move.uci()
            except ValueError:
                actual_san, actual_uci = choice.san, choice.uci
            self.recorder.event(
                "move_san_mismatch",
                game=number,
                expected=choice.san,
                rendered=rendered,
                actual_uci=actual_uci,
            )
        color_name = "white" if our_color == chess.WHITE else "black"
        spent = after.spent_ms(ply) or choice.elapsed_ms
        info = choice.info
        position_after = board.copy(stack=False)
        position_after.push(chess.Move.from_uci(actual_uci))
        self.recorder.move(
            game=number,
            ply=ply,
            color=color_name,
            san=actual_san,
            uci=actual_uci,
            engine_uci=choice.uci if actual_uci != choice.uci else None,
            source=choice.source,
            engine_ms=choice.elapsed_ms,
            spent_ms=spent,
            depth=info.depth if info else 0,
            seldepth=info.seldepth if info else 0,
            nodes=info.nodes if info else 0,
            eval_cp=info.score_cp if info else None,
            eval_mate=info.score_mate if info else None,
            pv=list(info.pv) if info else [],
            fen_before=board.fen(),
            fen_after=position_after.fen(),
            clocks_before={
                "white_ms": before.clock_ms(chess.WHITE),
                "black_ms": before.clock_ms(chess.BLACK),
            },
            clocks_after={
                "white_ms": after.clock_ms(chess.WHITE),
                "black_ms": after.clock_ms(chess.BLACK),
            },
        )

    def _write_game_pgn(
        self,
        number: int,
        start_fen: str,
        board: chess.Board,
        result: str,
        reason: str,
        our_color: chess.Color,
    ) -> Path | None:
        moves = [move.uci() for move in board.move_stack]
        headers = {
            "Event": "Youloss night vs chess.com",
            "Site": "chess.com/play/computer",
            "Date": time.strftime("%Y.%m.%d"),
            "Round": str(number),
            "White": "Youloss" if our_color == chess.WHITE else self.spec.bot,
            "Black": self.spec.bot if our_color == chess.WHITE else "Youloss",
            "Result": result,
            "TimeControl": self.spec.tc,
            "Termination": reason,
        }
        try:
            return self.recorder.write_pgn(
                number, start_fen=start_fen, moves_uci=moves, headers=headers
            )
        except Exception as exc:
            self.recorder.event("pgn_error", game=number, error=str(exc))
            return None

    def _failure(
        self, number: int, label: str, detail: str, screenshot: Path | None = None
    ) -> None:
        self.recorder.failure(label, screenshot=screenshot, game=number, detail=detail)

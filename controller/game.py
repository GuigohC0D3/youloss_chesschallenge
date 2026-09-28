"""Loop da partida: nosso lance (forçado/book/engine), lance do adversário e comandos."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import chess

from controller.book import OpeningBook
from controller.clock import ClockFormatError, GameClock, format_mmss, parse_mmss
from controller.engine_client import EngineClient, EngineError, SearchInfo
from controller.game_log import GameLog
from controller.state import GameState, save_state

HELP = """comandos:
  <uci>                     lance do adversário (ex. e2e4, e7e8q)
  undo                      desfaz o último meio-lance (pausa se virar nossa vez)
  fen <FEN>                 ressincroniza com o tabuleiro físico (pausa se for nossa vez)
  clock <nós mm:ss> <adv mm:ss>   sincroniza com o relógio físico
  board                     tabuleiro, FEN e relógios
  go                        retoma: engine joga (quando pausado na nossa vez)
  resign nos|adv            registra abandono (nosso ou do adversário)
  draw                      registra empate acordado
  quit                      sai sem resultado (retomar com start --resume)"""

# Teto de pensamento do spec (maximum <= 0.25 * restante); além disso o controller manda stop.
MAX_THINK_FRACTION = 0.25


def color_name(color: chess.Color) -> str:
    return "white" if color == chess.WHITE else "black"


class Game:
    def __init__(
        self,
        state: GameState,
        state_path: Path,
        engine: EngineClient,
        book: OpeningBook,
        log: GameLog,
        clock: GameClock,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
        paused: bool = False,
        safety_margin_s: float = 2.0,
    ):
        self.state = state
        self.state_path = Path(state_path)
        self.engine = engine
        self.book = book
        self.log = log
        self.clock = clock
        self.input_fn = input_fn
        self.out = output_fn
        self.paused = paused
        self.safety_margin_s = safety_margin_s
        self.board = state.board()
        self.us = state.us()
        self.running = True
        self._commands: dict[str, Callable[[str], None]] = {
            "quit": self._cmd_quit,
            "undo": self._cmd_undo,
            "fen": self._cmd_fen,
            "clock": self._cmd_clock,
            "board": self.show_board,
            "go": self._cmd_go,
            "resign": self._cmd_resign,
            "draw": self._cmd_draw,
            "help": lambda arg: self.out(HELP),
        }

    def run(self) -> str | None:
        """Joga até o fim da partida ou `quit`. Retorna o resultado, ou None se interrompida."""
        if self.clock.running is None:
            self.clock.start(self.board.turn)
        while self.running:
            outcome = self.board.outcome()
            if outcome is not None:
                self._finish(outcome.result(), outcome.termination.name.lower())
                break
            if self.board.turn == self.us and not self.paused:
                self._play_our_move()
            else:
                self._prompt()
        return self.state.result

    # --- nosso lance -------------------------------------------------------

    def _play_our_move(self) -> None:
        legal = list(self.board.legal_moves)
        info: SearchInfo | None = None
        book_move = self.book.pick(self.board)
        if len(legal) == 1:
            move, source = legal[0], "forced"
        elif book_move is not None and book_move in legal:
            move, source = book_move, "book"
        else:
            info = self._search()
            try:
                move = chess.Move.from_uci(info.bestmove)
            except ValueError as exc:
                raise EngineError(f"bestmove malformado: {info.bestmove!r}") from exc
            if move not in legal:
                raise EngineError(f"engine devolveu lance ilegal: {info.bestmove}")
            source = "engine"
        move_no, color = self.board.fullmove_number, self.board.turn
        spent = self.clock.press()
        self._push(move)
        self.out(f"\n>>> NOSSO LANCE: {move.uci()}   ({source}, {spent / 1000:.1f}s)\n")
        self.log.our_move(move_no, color_name(color), move.uci(), source, spent, info)

    def _search(self) -> SearchInfo:
        white = self.clock.remaining(chess.WHITE)
        black = self.clock.remaining(chess.BLACK)
        inc = self.clock.inc_ms
        ours = white if self.us == chess.WHITE else black
        timeout = max(ours, 0) * MAX_THINK_FRACTION / 1000 + self.safety_margin_s
        position = f"position fen {self.state.start_fen}"
        if self.state.moves:
            position += " moves " + " ".join(self.state.moves)
        go = f"go wtime {max(white, 1)} btime {max(black, 1)} winc {inc} binc {inc}"
        info = self.engine.search(position, go, timeout)
        if info.stopped:
            self.out(f"AVISO: engine passou de {timeout:.1f}s; stop enviado")
        return info

    # --- vez do adversário / comandos -------------------------------------

    def _prompt(self) -> None:
        if self.board.turn == self.us:
            who = "NÓS (pausado: 'go' para jogar)"
        else:
            who = "adversário"
        dots = "." if self.board.turn == chess.WHITE else "..."
        try:
            line = self.input_fn(f"[{self.board.fullmove_number}{dots}] vez: {who} > ")
        except EOFError:
            line = "quit"
        text = line.strip()
        if not text:
            return
        cmd, _, arg = text.partition(" ")
        handler = self._commands.get(cmd.lower())
        if handler is not None:
            handler(arg.strip())
        else:
            self._opponent_move(text)

    def _opponent_move(self, text: str) -> None:
        if self.board.turn == self.us:
            self.out("é a nossa vez: use 'go' para o engine jogar")
            return
        uci = text.lower()
        try:
            move = chess.Move.from_uci(uci)
        except ValueError:
            self.out(f"entrada inválida: {text!r} (lance UCI como e2e4 ou e7e8q, ou 'help')")
            return
        if move not in self.board.legal_moves:
            promo = chess.Move(move.from_square, move.to_square, chess.QUEEN)
            hint = ""
            if move.promotion is None and promo in self.board.legal_moves:
                hint = " (promoção? informe a peça, ex. e7e8q)"
            self.out(f"lance ilegal: {uci}{hint}")
            return
        move_no, color = self.board.fullmove_number, self.board.turn
        spent = self.clock.press()
        self._push(move)
        self.paused = False
        self.log.opponent_move(move_no, color_name(color), move.uci(), spent)

    def _cmd_quit(self, arg: str) -> None:
        self._save()
        self.out(f"partida interrompida; estado em {self.state_path}. "
                 "Retome com: python -m controller.main start --resume")
        self.running = False

    def _cmd_undo(self, arg: str) -> None:
        if not self.state.moves:
            self.out("nada a desfazer")
            return
        undone = self.state.moves.pop()
        self.board = self.state.board()
        self.clock.start(self.board.turn)
        self.paused = True
        self._save()
        self.log.note(f"undo {undone}")
        self.show_board()

    def _cmd_fen(self, arg: str) -> None:
        try:
            board = chess.Board(arg)
        except ValueError as exc:
            self.out(f"FEN inválida: {exc}")
            return
        if not board.is_valid():
            self.out(f"FEN inválida: {board.status()!r}")
            return
        self.board = board
        self.state.start_fen, self.state.moves = board.fen(), []
        self.clock.start(board.turn)
        self.paused = True
        self._save()
        self.log.note(f'fen "{board.fen()}"')
        self.show_board()

    def _cmd_clock(self, arg: str) -> None:
        parts = arg.split()
        if len(parts) != 2:
            self.out("uso: clock <nosso mm:ss> <adv mm:ss>")
            return
        try:
            ours, theirs = parse_mmss(parts[0]), parse_mmss(parts[1])
        except ClockFormatError as exc:
            self.out(str(exc))
            return
        self.clock.set(self.us, ours)
        self.clock.set(not self.us, theirs)
        self._save()
        self.log.note(f"clock nos={parts[0]} adv={parts[1]}")
        self.out(self._clock_line())

    def _cmd_go(self, arg: str) -> None:
        if self.board.turn != self.us:
            self.out("vez do adversário: digite o lance dele")
            return
        self.paused = False

    def _cmd_resign(self, arg: str) -> None:
        who = arg.lower().replace("ó", "o")
        if who not in ("nos", "adv"):
            self.out("uso: resign nos|adv")
            return
        loser = self.us if who == "nos" else (not self.us)
        result = "0-1" if loser == chess.WHITE else "1-0"
        self._finish(result, "resign_us" if who == "nos" else "resign_opponent")

    def _cmd_draw(self, arg: str) -> None:
        self._finish("1/2-1/2", "draw_agreed")

    def show_board(self, arg: str = "") -> None:
        self.out(f"{self.board}\nFEN: {self.board.fen()}\n{self._clock_line()}")

    def _clock_line(self) -> str:
        ours = format_mmss(self.clock.remaining(self.us))
        theirs = format_mmss(self.clock.remaining(not self.us))
        return f"relógio: nós {ours} | adv {theirs}"

    # --- estado ------------------------------------------------------------

    def _push(self, move: chess.Move) -> None:
        self.board.push(move)
        self.state.moves.append(move.uci())
        self._save()

    def _save(self) -> None:
        self.state.white_ms = self.clock.remaining(chess.WHITE)
        self.state.black_ms = self.clock.remaining(chess.BLACK)
        save_state(self.state, self.state_path)

    def _finish(self, result: str, reason: str) -> None:
        self.state.result, self.state.reason = result, reason
        self._save()
        self.log.result(result, reason)
        self.out(f"FIM DE PARTIDA: {result} ({reason})")
        self.running = False

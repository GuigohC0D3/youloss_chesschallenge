"""Loop da partida: proposta nossa (forçado/book/engine), confirmação e lance do adversário.

Relógio físico (manual) é autoritativo; o `GameClock` interno é só estimativa.
Protocolo explícito:
  `begin` ................. inicia o relógio no lado a mover (partida nova).
  `press` ................. o adversário jogou e apertou o relógio físico:
                            liquida o tempo dele e liga o nosso (uma vez).
  `<uci>` ................. lance do adversário (só após `press`; não troca o relógio).
  `go` .................... propõe nosso lance (só com nosso relógio correndo).
  `played` ................ confirma a proposta após jogar no tabuleiro físico
                            (avanço único; troca o relógio para o adversário).
Proposta x confirmação são separadas: nada avança board/histórico nem loga
`move=` antes de `played`. `resume` exige `fen` + `clock` e nunca auto-confirma.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Callable

import chess

from controller.book import OpeningBook
from controller.clock import ClockFormatError, GameClock, format_mmss, parse_mmss
from controller.engine_client import EngineClient, EngineError, SearchInfo
from controller.game_log import GameLog
from controller.state import GameState, save_state

HELP = """comandos:
  begin                     inicia o relógio no lado a mover (partida nova)
  press <nós mm:ss> [adv]   o adversário apertou o físico: leitura física obrigatória, deduz latência conservadora e liga o nosso
  <uci>                     lance do adversário após `press` (ex. e2e4, e7e8q)
  go                        propõe nosso lance (só com nosso relógio correndo, na nossa vez)
  played                    confirma a proposta após jogar no físico (avanço único)
  undo                      desfaz o último meio-lance (para o relógio; exige 'clock' novo)
  fen <FEN>                 ressincroniza com o tabuleiro físico (para o relógio; exige 'clock' novo)
  clock <nós mm:ss> <adv mm:ss> [nos|adv|stop]   sincroniza com o relógio físico
                                                   após estimativa expirada, leia o físico e use `nos`
  board                     tabuleiro, FEN e relógios
  resign nos|adv            registra abandono (nosso ou do adversário)
  draw                      registra empate acordado
  quit                      sai sem resultado (retomar com start --resume)"""

# Teto de pensamento do spec (maximum <= 0.25 * restante); além disso o controller manda stop.
MAX_THINK_FRACTION = 0.25
# Graça de stop limitada: total busca + stop + reserva precisa caber no restante.
STOP_GRACE_S = 1.0
# Orçamento mínimo útil de busca: abaixo disso usa fallback imediato
# (sem flag enquanto houver tempo) em vez de estourar o teto com o piso.
MIN_USEFUL_SEARCH_MS = 100
# Latência conservadora de leitura e digitação do relógio físico na transição para a nossa vez:
# 1.0s de granularidade de display (segundos truncados) + 1.0s de observação/digitação.
# Padrão provisório até medição em rehearsal com operadores.
DEFAULT_CLOCK_LATENCY_S = 2.0
_EMERGENCY_PIECE_VALUE = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20_000,
}


def emergency_priority(board: chess.Board, move: chess.Move) -> int:
    """Cheap one-ply move ordering for the no-search low-time path."""
    mover = board.piece_at(move.from_square)
    if mover is None:
        return -1_000_000
    score = 0
    if board.is_attacked_by(not board.turn, move.from_square):
        score += _EMERGENCY_PIECE_VALUE[mover.piece_type] // 3
    if move.promotion:
        score += _EMERGENCY_PIECE_VALUE[move.promotion] - _EMERGENCY_PIECE_VALUE[chess.PAWN]
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        captured_value = (
            _EMERGENCY_PIECE_VALUE[victim.piece_type]
            if victim is not None
            else _EMERGENCY_PIECE_VALUE[chess.PAWN]
        )
        score += 2 * captured_value - _EMERGENCY_PIECE_VALUE[mover.piece_type] // 3
    if board.is_castling(move):
        score += 40

    gives_check = board.gives_check(move)
    board.push(move)
    try:
        if gives_check:
            score += 300
            if board.is_checkmate():
                score += 1_000_000
        landed = board.piece_at(move.to_square)
        if landed is not None and board.is_attacked_by(board.turn, move.to_square):
            score -= 3 * _EMERGENCY_PIECE_VALUE[landed.piece_type] // 4
    finally:
        board.pop()
    return score


class _SearchRefused(Exception):
    """Recusa de dispatch: relógio cruzou o limite após a leitura inicial."""

    def __init__(self, reason: str, ours_ms: int):
        super().__init__(reason)
        self.reason = reason  # "flag" | "fallback"
        self.ours_ms = ours_ms


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
        needs_reconciliation: bool = False,
        clock_latency_s: float = DEFAULT_CLOCK_LATENCY_S,
    ):
        if (
            not math.isfinite(clock_latency_s)
            or clock_latency_s < 0.0
            or clock_latency_s > 60.0
        ):
            raise ValueError(
                f"latência de relógio fora da faixa [0.0, 60.0]s ou não finita: {clock_latency_s!r}"
            )
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
        self.clock_latency_s = clock_latency_s
        self.clock_latency_ms = round(clock_latency_s * 1000)
        self.board = state.board()
        self.us = state.us()
        self.running = True
        self._low_margin_fallback = False
        # Partida nova exige `begin`; resume exige `fen` + `clock`.
        self._begun = False if not needs_reconciliation else True
        self._needs_fen = needs_reconciliation
        self._needs_clock = needs_reconciliation
        self._opp_spent: int | None = None
        self._physical_read_required = False
        self._physical_flag_pending = False
        self._emergency_candidate: tuple[str, chess.Move, SearchInfo | None] | None = None
        self._commands: dict[str, Callable[[str], None]] = {
            "quit": self._cmd_quit,
            "undo": self._cmd_undo,
            "fen": self._cmd_fen,
            "clock": self._cmd_clock,
            "board": self.show_board,
            "go": self._cmd_go,
            "begin": self._cmd_begin,
            "press": self._cmd_press,
            "played": self._cmd_played,
            "resign": self._cmd_resign,
            "draw": self._cmd_draw,
            "help": lambda arg: self.out(HELP),
        }

    @property
    def begun(self) -> bool:
        """Whether play is reconciled and the physical game has begun."""
        return self._begun and not (self._needs_fen or self._needs_clock)

    def run(self) -> str | None:
        """Joga até o fim da partida ou `quit`. Retorna o resultado, ou None se interrompida."""
        # Nunca auto-inicia: o relógio físico manda. `begin` (nova) ou
        # `fen`+`clock` (resume) + eventos explícitos ligam o interno.
        while self.running:
            outcome = self.board.outcome()
            if outcome is not None:
                self._finish(outcome.result(), outcome.termination.name.lower())
                break
            if (
                self.board.turn == self.us
                and not self.paused
                and self._begun
                and not self._needs_fen
                and not self._needs_clock
                and self.state.pending_uci is None
                and self.clock.running == self.us
            ):
                self._propose_our_move()
            else:
                self._prompt()
        return self.state.result

    # --- nossa proposta (NÃO avança o tabuleiro) -----------------------------

    def _finish_flag(self, ours_ms: int, *, source: str) -> None:
        self.log.note(f"physical flag confirmed nos={ours_ms}ms source={source}")
        result = "0-1" if self.us == chess.WHITE else "1-0"
        self._finish(result, "flag")

    def _require_physical_clock(self, ours_ms: int) -> None:
        """Pause on an expired estimate; only a fresh physical reading can flag."""
        self.clock.stop()
        self._needs_clock = True
        self._physical_read_required = True
        self._low_margin_fallback = False
        self._save()
        self.log.note(
            f"clock-sync-recovery estimated_ours_ms={ours_ms} "
            f"latency_allowance_ms={self.clock_latency_ms} physical_read_required=true"
        )
        self.out(
            f"estimativa interna expirou ({ours_ms} ms); flag não confirmada. "
            "Leia o relógio físico e sincronize com `clock <nós mm:ss> "
            "<adv mm:ss> nos`; 00:00 físico confirmado encerra a partida."
        )

    def _propose_fallback_lowtime(
        self, legal: list[chess.Move], ours_ms: int, reserve_ms: int, stop_ms: int
    ) -> None:
        # Reserva/stop não cabem com margem útil mas ainda há tempo:
        # escolha determinística sem busca.
        # Se houver candidato de engine validado para a posição exata atual,
        # prefere esse candidato revalidando a legalidade.
        cached_move: chess.Move | None = None
        cached_info: SearchInfo | None = None
        if self._emergency_candidate is not None:
            cand_fen, cand_move, cand_info = self._emergency_candidate
            if cand_fen == self.board.fen() and cand_move in legal:
                cached_move = cand_move
                cached_info = cand_info
            else:
                self._emergency_candidate = None

        if cached_move is not None:
            move = cached_move
            source = "fallback"
            self._store_proposal(move, source, cached_info)
            self.log.note(
                f"fallback-lowtime candidate=cached source=cached restante={ours_ms}ms reserva={reserve_ms}ms "
                f"stop={stop_ms}ms uci={move.uci()}"
            )
            self.out(
                f"\n>>> PROPOSTA IMEDIATA (fallback-lowtime [cached]): {move.uci()}   "
                f"(reserva de operador/relógio não cabe; jogue no físico e confirme com 'played')\n"
            )
        else:
            move = min(
                legal,
                key=lambda candidate: (-self._emergency_priority(candidate), candidate.uci()),
            )
            source = "fallback"
            self._store_proposal(move, source, None)
            self.log.note(
                f"fallback-lowtime restante={ours_ms}ms reserva={reserve_ms}ms "
                f"stop={stop_ms}ms uci={move.uci()}"
            )
            self.out(
                f"\n>>> PROPOSTA IMEDIATA (fallback-lowtime): {move.uci()}   "
                f"(reserva de operador/relógio não cabe; jogue no físico e confirme com 'played')\n"
            )

    def _emergency_priority(self, move: chess.Move) -> int:
        return emergency_priority(self.board, move)

    def _propose_our_move(self) -> None:
        if self.state.pending_uci is not None:
            self.out(
                f"proposta pendente: {self.state.pending_uci} "
                f"({self.state.pending_source}); jogue no físico e confirme com 'played'"
            )
            return
        legal = list(self.board.legal_moves)
        if not legal:
            return
        stop_ms = round(STOP_GRACE_S * 1000)
        reserve_ms = round(self.safety_margin_s * 1000)
        ours = self.clock.remaining(self.us)
        if ours <= 0:
            self._require_physical_clock(ours)
            return
        if self._low_margin_fallback:
            self._low_margin_fallback = False
            rem = max(1, ours)
            self._propose_fallback_lowtime(legal, rem, reserve_ms, stop_ms)
            return
        info: SearchInfo | None = None
        book_move = self.book.pick(self.board)
        if len(legal) == 1:
            move, source = legal[0], "forced"
        elif book_move is not None and book_move in legal:
            move, source = book_move, "book"
        else:
            stop_ms = round(STOP_GRACE_S * 1000)
            reserve_ms = round(self.safety_margin_s * 1000)
            # O relógio pode ter cruzado o limite durante a seleção de book:
            # releitura fresca imediatamente antes do dispatch.
            fresh = self.clock.remaining(self.us)
            if fresh <= 0:
                self._require_physical_clock(fresh)
                return
            avail_ms = fresh - stop_ms - reserve_ms
            if avail_ms < MIN_USEFUL_SEARCH_MS:
                self._propose_fallback_lowtime(legal, fresh, reserve_ms, stop_ms)
                return
            try:
                info = self._search(
                    timeout_ms=min(fresh * MAX_THINK_FRACTION, avail_ms)
                )
            except _SearchRefused as exc:
                if exc.reason == "flag":
                    self._require_physical_clock(exc.ours_ms)
                else:
                    self._propose_fallback_lowtime(
                        legal, exc.ours_ms, reserve_ms, stop_ms
                    )
                return
            try:
                move = chess.Move.from_uci(info.bestmove)
            except ValueError as exc:
                self._emergency_candidate = None
                raise EngineError(f"bestmove malformado: {info.bestmove!r}") from exc
            if move not in legal:
                self._emergency_candidate = None
                raise EngineError(f"engine devolveu lance ilegal: {info.bestmove}")
            source = "engine"
            self._emergency_candidate = (self.board.fen(), move, info)
        self._store_proposal(move, source, info)
        self.out(
            f"\n>>> PROPOSTA: {move.uci()}   ({source}) — "
            f"jogue no tabuleiro físico e confirme com 'played'\n"
        )

    def _store_proposal(
        self, move: chess.Move, source: str, info: SearchInfo | None
    ) -> None:
        self.state.pending_uci = move.uci()
        self.state.pending_source = source
        if info is not None:
            self.state.pending_depth = info.depth
            self.state.pending_seldepth = info.seldepth
            self.state.pending_nodes = info.nodes
            self.state.pending_score_cp = info.score_cp
            self.state.pending_score_mate = info.score_mate
            self.state.pending_pv = list(info.pv)
        else:
            self.state.pending_depth = 0
            self.state.pending_seldepth = 0
            self.state.pending_nodes = 0
            self.state.pending_score_cp = None
            self.state.pending_score_mate = None
            self.state.pending_pv = [move.uci()]
        self._save()
        move_no = self.board.fullmove_number
        self.log.note(
            f"proposal move={move_no} color={color_name(self.board.turn)} "
            f"uci={move.uci()} source={source}"
        )

    def _search(self, timeout_ms: float) -> SearchInfo:
        # Releitura fresca: o relógio pode ter cruzado reserva/mínimo ou
        # zerado durante a seleção de book. Recusa sem chamar o engine.
        fresh = self.clock.remaining(self.us)
        stop_ms = round(STOP_GRACE_S * 1000)
        reserve_ms = round(self.safety_margin_s * 1000)
        avail_ms = fresh - stop_ms - reserve_ms
        if fresh <= 0:
            raise _SearchRefused("flag", fresh)
        if avail_ms < MIN_USEFUL_SEARCH_MS:
            raise _SearchRefused("fallback", fresh)
        # timeout herdado pode estar obsoleto: limita ao orçamento fresco,
        # mantendo fração configurada, stop grace e reserva.
        timeout_ms = min(timeout_ms, fresh * MAX_THINK_FRACTION, avail_ms)
        theirs = self.clock.remaining(not self.us)
        inc = self.clock.inc_ms
        # Tempos honestos: expiry (<=0) nem chega aqui (pede leitura física).
        # Nosso tempo (>0) vai com piso 1ms; o do adversário vai com piso 0
        # para nunca mascarar um estouro dele como tempo positivo.
        ours = fresh
        theirs_side = theirs
        ours_sent, theirs_sent = max(ours, 1), max(theirs_side, 0)
        wtime, btime = (
            (ours_sent, theirs_sent)
            if self.us == chess.WHITE
            else (theirs_sent, ours_sent)
        )
        timeout = timeout_ms / 1000
        # timeout_ms já respeita avail (search + stop + reserva <= restante);
        # sem piso que estoure o teto (o chamador garante >= MIN_USEFUL_SEARCH_MS).
        position = f"position fen {self.state.start_fen}"
        if self.state.moves:
            position += " moves " + " ".join(self.state.moves)
        go = f"go wtime {wtime} btime {btime} winc {inc} binc {inc}"
        try:
            info = self.engine.search(position, go, timeout, stop_grace=STOP_GRACE_S)
        except Exception:
            self._emergency_candidate = None
            raise
        if info.stopped:
            self.out(f"AVISO: engine passou de {timeout:.1f}s; stop enviado")
        return info

    # --- vez do adversário / comandos -------------------------------------

    def _prompt(self) -> None:
        if not self._begun:
            who = "NÓS/adv (use 'begin' para iniciar o relógio)"
        elif self._needs_fen and self._needs_clock:
            who = "resume (use 'fen <FEN>' e 'clock <nós mm:ss> <adv mm:ss> [nos|adv|stop]')"
        elif self._needs_fen:
            who = "resume (use 'fen <FEN>')"
        elif self._physical_read_required:
            who = "estimativa expirada (leia o físico; use 'clock <nós> <adv> nos')"
        elif self._needs_clock:
            who = "relógio parado (use 'clock <nós mm:ss> <adv mm:ss> [nos|adv|stop]')"
        elif self.state.pending_uci is not None:
            who = (
                f"NÓS (proposta {self.state.pending_uci}: "
                "jogue no físico e confirme com 'played')"
            )
        elif self.board.turn == self.us:
            who = "NÓS (pausado: 'go' para propor)"
        else:
            who = "adversário (use 'press' e depois o lance UCI)"
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
        if (
            self._physical_flag_pending
            and handler is not None
            and cmd.lower() != "help"
        ):
            self._physical_flag_pending = False
            self._finish_flag(0, source="press")
        elif handler is not None:
            handler(arg.strip())
        else:
            self._opponent_move(text)

    def _needs_reconciliation_msg(self) -> bool:
        if self._needs_fen and self._needs_clock:
            self.out(
                "resume: ressincronize com 'fen <FEN>' e "
                "'clock <nós mm:ss> <adv mm:ss> [nos|adv|stop]'"
            )
            return True
        if self._needs_fen:
            self.out("ressincronize com 'fen <FEN>'")
            return True
        if self._physical_read_required:
            self.out(
                "estimativa expirada: leia o relógio físico e sincronize com "
                "'clock <nós mm:ss> <adv mm:ss> nos'"
            )
            return True
        if self._needs_clock:
            self.out(
                "relógio parado: ressincronize com "
                "'clock <nós mm:ss> <adv mm:ss> [nos|adv|stop]'"
            )
            return True
        return False

    def _cmd_begin(self, arg: str) -> None:
        if self._begun:
            self.out("partida já iniciada")
            return
        if self._needs_fen or self._needs_clock:
            self.out(
                "resume: ressincronize com 'fen <FEN>' e 'clock <nós mm:ss> <adv mm:ss>'"
            )
            return
        self.clock.start(self.board.turn)
        self._begun = True
        self.paused = False
        self.log.note(f"begin turno={color_name(self.board.turn)}")
        self._save()
        self.out(
            f"relógio iniciado ({color_name(self.board.turn)} a mover)\n{self._clock_line()}"
        )

    def _cmd_press(self, arg: str) -> None:
        if not self._begun:
            self.out("partida ainda não começou: use 'begin'")
            return
        if self._needs_reconciliation_msg():
            return
        if self.board.turn == self.us:
            self.out("não é a vez do adversário: 'press' só na vez dele")
            return
        if self.clock.running is None:
            self.out("relógio parado: use 'begin' (nova) ou 'fen'+'clock' (resume)")
            return
        if self.clock.running != self.board.turn:
            self.out(
                "relógio do outro lado: 'press' já registrado? digite o lance UCI do adversário"
            )
            return
        parts = arg.split()
        if len(parts) < 1 or len(parts) > 2:
            self.out(
                "uso: press <nosso mm:ss> [adv mm:ss] (leitura física obrigatória)"
            )
            return
        try:
            ours_ms = parse_mmss(parts[0])
        except ClockFormatError as exc:
            self.out(str(exc))
            return
        theirs_ms: int | None = None
        if len(parts) == 2:
            try:
                theirs_ms = parse_mmss(parts[1])
            except ClockFormatError as exc:
                self.out(str(exc))
                return

        # Encerra o relógio do adversário (o press no físico parou a vez dele)
        if theirs_ms is not None:
            prev_theirs = self.clock.remaining(not self.us)
            spent = max(0, prev_theirs - theirs_ms)
            self.clock.set(not self.us, theirs_ms)
        else:
            spent = self.clock.press()

        self._opp_spent = spent

        # Transição para o nosso relógio: com leitura física obrigatória, deduz latência conservadora
        # de display e digitação. Leitura física positiva com margem baixa ativa _low_margin_fallback,
        # que contorna a inferência de flag interno e força proposta imediata de fallback.
        # Quando a dedução de latência consome a leitura (estimativa <= 0), o relógio interno é
        # limitado ao piso de 1 segundo (não 1 ms). O limiar de margem baixa é a soma de
        # stop grace + reserva do operador + busca mínima útil (stop_ms + reserve_ms + MIN_USEFUL_SEARCH_MS).
        conservative = ours_ms - self.clock_latency_ms
        stop_ms = round(STOP_GRACE_S * 1000)
        reserve_ms = round(self.safety_margin_s * 1000)
        min_search_ms = stop_ms + reserve_ms + MIN_USEFUL_SEARCH_MS

        if ours_ms > 0 and conservative < min_search_ms:
            self._low_margin_fallback = True
            adjusted = max(1, conservative)
            settled = min(ours_ms, 1000) if conservative <= 0 else conservative
            if conservative <= 0:
                self.log.note(
                    f"press adv jogou spent_ms={spent} physical_ours={parts[0]} "
                    f"latency_allowance_ms={self.clock_latency_ms} conservative_ours_ms={conservative} "
                    f"adjusted_estimate_ms={adjusted} "
                    "(floor 1s: leitura física positiva, fallback sem flag prematuro)"
                )
                self.out(
                    f"relógio: leitura física positiva ({parts[0]}), mas latência conservadora "
                    f"(-{self.clock_latency_s:.1f}s) zera a margem — fallback imediato ativado (sem flag)"
                )
            else:
                self.log.note(
                    f"press adv jogou spent_ms={spent} physical_ours={parts[0]} "
                    f"latency_allowance_ms={self.clock_latency_ms} conservative_ours_ms={conservative} "
                    f"adjusted_estimate_ms={adjusted} "
                    "(margem baixa positiva: fallback imediato sem busca e sem flag por overhead)"
                )
                self.out(
                    f"relógio sincronizado com leitura física "
                    f"(-{self.clock_latency_s:.1f}s latência conservadora deduzida)"
                )
        elif ours_ms > 0:
            self._low_margin_fallback = False
            settled = conservative
            self.log.note(
                f"press adv jogou spent_ms={spent} physical_ours={parts[0]} "
                f"latency_allowance_ms={self.clock_latency_ms} conservative_ours_ms={settled} "
                f"adjusted_estimate_ms={settled}"
            )
            self.out(
                f"relógio sincronizado com leitura física "
                f"(-{self.clock_latency_s:.1f}s latência conservadora deduzida)"
            )
        else:
            self._low_margin_fallback = False
            settled = 0
            self._physical_flag_pending = True
            self.log.note(
                f"press adv jogou spent_ms={spent} physical_ours={parts[0]} flag físico zerado"
            )
            self.out("relógio físico zerado (flag)")

        self.clock.set(self.us, settled)
        self.clock.start(self.us)
        self._save()
        self.out(self._clock_line())

    def _cmd_played(self, arg: str) -> None:
        if not self._begun:
            self.out("partida ainda não começou: use 'begin'")
            return
        if self._needs_reconciliation_msg():
            return
        pending = self.state.pending_uci
        source = self.state.pending_source
        if pending is None or source is None:
            self.out("sem proposta pendente: use 'go' para gerar uma proposta")
            return
        if self.board.turn != self.us:
            self.out("não é a nossa vez: 'played' só na nossa vez")
            return
        if self.clock.running != self.us:
            self.out(
                "nosso relógio não está correndo: 'played' só com nosso relógio correndo"
            )
            return
        ours = self.clock.remaining(self.us)
        if ours <= 0:
            self._require_physical_clock(ours)
            return
        try:
            move = chess.Move.from_uci(pending)
        except ValueError:
            self.out(f"proposta inválida: {pending!r} (use 'undo' para descartar)")
            return
        if move not in self.board.legal_moves:
            self.out(
                f"proposta {pending} ilegal na posição atual: use 'undo' para descartar"
            )
            return
        info: SearchInfo | None = None
        if source == "engine":
            info = SearchInfo(
                bestmove=pending,
                depth=self.state.pending_depth,
                seldepth=self.state.pending_seldepth,
                nodes=self.state.pending_nodes,
                score_cp=self.state.pending_score_cp,
                score_mate=self.state.pending_score_mate,
                pv=list(self.state.pending_pv) or [pending],
            )
        move_no, color = self.board.fullmove_number, self.board.turn
        spent = self.clock.press()
        self.board.push(move)
        self._emergency_candidate = None
        self.state.moves.append(move.uci())
        self.state.pending_uci = None
        self.state.pending_source = None
        self.state.pending_depth = 0
        self.state.pending_seldepth = 0
        self.state.pending_nodes = 0
        self.state.pending_score_cp = None
        self.state.pending_score_mate = None
        self.state.pending_pv = []
        # Durabilidade por lance: o `move=` vai antes do commit do estado,
        # para que um crash/erro de escrita nunca deixe estado confirmado
        # sem seu registro. A proposta pendente continua persistida antes
        # (em `_store_proposal`), só a confirmação inverte log→save.
        self.log.our_move(move_no, color_name(color), move.uci(), source, spent, info)
        self._save()
        self.out(
            f"\n>>> LANCE CONFIRMADO: {move.uci()}   ({source}, {spent / 1000:.1f}s)\n"
        )

    def _opponent_move(self, text: str) -> None:
        if not self._begun:
            self.out("partida ainda não começou: use 'begin'")
            return
        if self._needs_reconciliation_msg():
            return
        if self.board.turn == self.us:
            self.out("é a nossa vez: use 'go' para propor e 'played' para confirmar")
            return
        if self.clock.running is None:
            self.out(
                "relógio parado: registre 'press' após o adversário apertar o físico"
            )
            return
        if self.clock.running != self.us:
            self.out(
                "relógio do adversário ainda correndo: registre 'press' antes do lance"
            )
            return
        uci = text.lower()
        try:
            move = chess.Move.from_uci(uci)
        except ValueError:
            self.out(
                f"entrada inválida: {text!r} (lance UCI como e2e4 ou e7e8q, ou 'help')"
            )
            return
        if move not in self.board.legal_moves:
            promo = chess.Move(move.from_square, move.to_square, chess.QUEEN)
            hint = ""
            if move.promotion is None and promo in self.board.legal_moves:
                hint = " (promoção? informe a peça, ex. e7e8q)"
            self.out(f"lance ilegal: {uci}{hint}")
            return
        move_no, color = self.board.fullmove_number, self.board.turn
        # `press` já trocou o relógio uma vez; aqui NÃO troca de novo.
        spent = self._opp_spent if self._opp_spent is not None else 0
        self._opp_spent = None
        self._push(move)
        self._emergency_candidate = None
        self.paused = False
        # Durabilidade por lance: `move=` antes do commit do estado.
        self.log.opponent_move(move_no, color_name(color), move.uci(), spent)
        self._save()
        if self._physical_flag_pending:
            self._physical_flag_pending = False
            outcome = self.board.outcome()
            if outcome is not None:
                self._finish(outcome.result(), outcome.termination.name.lower())
            else:
                self._finish_flag(0, source="press")
            return
        ours_after = self.clock.remaining(self.us)
        if ours_after <= 0:
            self._require_physical_clock(ours_after)
            return

    def _cmd_quit(self, arg: str) -> None:
        if self._physical_flag_pending:
            self._physical_flag_pending = False
            self._finish_flag(0, source="press")
            return
        self._save()
        if self.begun and not self.state.finished:
            self.out(
                "partida interrompida após começar; as regras estipulam derrota por falha "
                "de software. Não retome; informe o árbitro."
            )
        else:
            self.out(
                f"partida interrompida antes de começar; estado em {self.state_path}. "
                "Pode reabrir com --resume para diagnóstico."
            )
        self.running = False

    def _cmd_undo(self, arg: str) -> None:
        if not self.state.moves:
            if self.state.pending_uci is None:
                self.out("nada a desfazer")
                return
            discarded_first = self.state.pending_uci
            self.state.pending_uci = None
            self.state.pending_source = None
            self.state.pending_depth = 0
            self.state.pending_seldepth = 0
            self.state.pending_nodes = 0
            self.state.pending_score_cp = None
            self.state.pending_score_mate = None
            self.state.pending_pv = []
            self._opp_spent = None
            self._physical_read_required = False
            self._physical_flag_pending = False
            # Fail closed: para o relógio interno e exige 'clock' novo com
            # seleção explícita; tabuleiro/histórico inalterados (sem lances).
            self.clock.stop()
            self.paused = True
            self._needs_clock = True
            self._low_margin_fallback = False
            if self._emergency_candidate is not None and self._emergency_candidate[0] != self.board.fen():
                self._emergency_candidate = None
            self._save()
            self.log.note(f"undo (proposta {discarded_first} descartada)")
            self.show_board()
            return
        undone = self.state.moves.pop()
        discarded = self.state.pending_uci
        self.state.pending_uci = None
        self.state.pending_source = None
        self.state.pending_depth = 0
        self.state.pending_seldepth = 0
        self.state.pending_nodes = 0
        self.state.pending_score_cp = None
        self.state.pending_score_mate = None
        self.state.pending_pv = []
        self._opp_spent = None
        self._physical_read_required = False
        self._physical_flag_pending = False
        self.board = self.state.board()
        if self._emergency_candidate is not None and self._emergency_candidate[0] != self.board.fen():
            self._emergency_candidate = None
        # Fail closed: para o relógio interno e exige 'clock' novo com
        # seleção explícita (a omissão preserva o parado).
        self.clock.stop()
        self.paused = True
        self._needs_clock = True
        self._low_margin_fallback = False
        self._save()
        if discarded:
            self.log.note(f"undo {undone} (proposta {discarded} descartada)")
        else:
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
        discarded = self.state.pending_uci
        self.board = board
        self.state.start_fen, self.state.moves = board.fen(), []
        self.state.pending_uci = None
        self.state.pending_source = None
        self.state.pending_depth = 0
        self.state.pending_seldepth = 0
        self.state.pending_nodes = 0
        self.state.pending_score_cp = None
        self.state.pending_score_mate = None
        self.state.pending_pv = []
        self._opp_spent = None
        self._physical_read_required = False
        self._physical_flag_pending = False
        # Fail closed: para o relógio interno e exige 'clock' novo com
        # seleção explícita (a omissão preserva o parado).
        self.clock.stop()
        self.paused = True
        self._needs_fen = False
        self._needs_clock = True
        self._low_margin_fallback = False
        if self._emergency_candidate is not None and self._emergency_candidate[0] != self.board.fen():
            self._emergency_candidate = None
        self._save()
        if discarded:
            self.log.note(f'fen "{board.fen()}" (proposta {discarded} descartada)')
        else:
            self.log.note(f'fen "{board.fen()}"')
        self.show_board()

    def _cmd_clock(self, arg: str) -> None:
        parts = arg.split()
        if len(parts) not in (2, 3):
            self.out("uso: clock <nosso mm:ss> <adv mm:ss> [nos|adv|stop]")
            return
        try:
            ours, theirs = parse_mmss(parts[0]), parse_mmss(parts[1])
        except ClockFormatError as exc:
            self.out(str(exc))
            return
        select = parts[2].lower().replace("ó", "o") if len(parts) == 3 else None
        if select is not None and select not in ("nos", "adv", "stop"):
            self.out("uso: clock <nosso mm:ss> <adv mm:ss> [nos|adv|stop]")
            return

        recovery = self._physical_read_required
        recovery_fallback = False
        if recovery:
            if select != "nos":
                self.out(
                    "leia o relógio físico agora e sincronize nosso tempo com "
                    "'clock <nós mm:ss> <adv mm:ss> nos'"
                )
                return
            if ours == 0:
                self.clock.set(self.us, 0)
                self.clock.set(not self.us, theirs)
                self._needs_clock = False
                self._physical_read_required = False
                self._finish_flag(0, source="clock")
                return

            conservative = ours - self.clock_latency_ms
            min_useful_ms = (
                round(STOP_GRACE_S * 1000)
                + round(self.safety_margin_s * 1000)
                + MIN_USEFUL_SEARCH_MS
            )
            recovery_fallback = conservative < min_useful_ms
            if conservative <= 0:
                # A positive physical display can be consumed by the typing
                # allowance. Keep it out of the search path and propose now.
                ours = min(ours, 1000)
            else:
                ours = conservative

        self.clock.set(self.us, ours)
        self.clock.set(not self.us, theirs)
        if select == "nos":
            self.clock.start(self.us)
        elif select == "adv":
            self.clock.start(not self.us)
        elif select == "stop":
            self.clock.stop()
        # Omitido preserva o estado parado/correndo atual.
        self._needs_clock = False
        self._physical_read_required = False
        self._low_margin_fallback = recovery_fallback
        self._save()
        if recovery:
            self.log.note(
                f"clock-sync-recovery physical_ours={parts[0]} "
                f"latency_allowance_ms={self.clock_latency_ms} "
                f"adjusted_estimate_ms={ours} fallback={str(recovery_fallback).lower()}"
            )
            if recovery_fallback:
                self.out(
                    f"leitura física positiva ({parts[0]}); latência conservadora "
                    f"(-{self.clock_latency_s:.1f}s) deixa pouco tempo — "
                    "fallback imediato ativado, sem busca e sem flag prematura"
                )
            else:
                self.out(
                    f"relógio sincronizado com leitura física "
                    f"(-{self.clock_latency_s:.1f}s latência conservadora deduzida)"
                )
        elif select is None:
            self.log.note(f"clock nos={parts[0]} adv={parts[1]}")
        else:
            self.log.note(f"clock nos={parts[0]} adv={parts[1]} sel={select}")
        self.out(self._clock_line())

    def _cmd_go(self, arg: str) -> None:
        if not self._begun:
            self.out("partida ainda não começou: use 'begin'")
            return
        if self._needs_reconciliation_msg():
            return
        if self.state.pending_uci is not None:
            self.out(
                f"proposta pendente: {self.state.pending_uci} "
                "— jogue no físico e confirme com 'played'"
            )
            return
        if self.board.turn != self.us:
            self.out("vez do adversário: registre 'press' e digite o lance dele")
            return
        if self.clock.running != self.us:
            self.out(
                "nosso relógio não está correndo: use 'begin' ou aguarde 'press' do adversário"
            )
            return
        self.paused = False

    def _cmd_resign(self, arg: str) -> None:
        who = arg.lower().replace("ó", "o")
        if who not in ("nos", "adv"):
            self.out("uso: resign nos|adv")
            return
        loser = self.us if who == "nos" else (not self.us)
        result = "0-1" if loser == chess.WHITE else "1-0"
        reason = "resign_us" if who == "nos" else "resign_opponent"
        if self._confirm(f"encerrar a partida com {result} ({reason})?"):
            self._finish(result, reason)

    def _cmd_draw(self, arg: str) -> None:
        if self._confirm("encerrar a partida com empate acordado (1/2-1/2)?"):
            self._finish("1/2-1/2", "draw_agreed")

    def _confirm(self, question: str) -> bool:
        # Encerrar não tem volta (o resume recusa partida encerrada): exige confirmação.
        try:
            answer = self.input_fn(f"{question} [s/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() in ("s", "sim", "y", "yes"):
            return True
        self.out("cancelado; a partida continua")
        return False

    def show_board(self, arg: str = "") -> None:
        self.out(f"{self.board}\nFEN: {self.board.fen()}\n{self._clock_line()}")

    def _clock_line(self) -> str:
        ours = format_mmss(self.clock.remaining(self.us))
        theirs = format_mmss(self.clock.remaining(not self.us))
        return f"relógio: nós {ours} | adv {theirs}"

    # --- estado ------------------------------------------------------------

    def _push(self, move: chess.Move) -> None:
        # Só avança em memória; o chamador registra `move=` no log antes
        # de comitar com `_save()` (durabilidade por lance).
        self.board.push(move)
        self.state.moves.append(move.uci())

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

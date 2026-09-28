"""CLI do operador: `python -m controller.main start ...`."""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Callable

import chess

from controller.book import BookError, OpeningBook
from controller.clock import ClockFormatError, GameClock, parse_tc
from controller.engine_client import EngineClient, EngineError
from controller.game import Game
from controller.game_log import GameLog, log_path
from controller.runtime import runtime_options
from controller.state import (
    GameState, StateError, latest_unfinished, load_state, save_state, state_path_for,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENGINE = ROOT / "bin" / "youloss.exe"
DEFAULT_BOOK = ROOT / "assets" / "book.bin"
DEFAULT_SYZYGY = ROOT / "assets" / "syzygy"
DEFAULT_LOGS = ROOT / "logs"


class UsageError(Exception):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m controller.main")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start", help="inicia ou retoma uma partida")
    s.add_argument("--color", choices=["white", "black"], help="nosso lado")
    s.add_argument("--tc", default="900+10", help="base+inc em segundos (padrão 900+10)")
    s.add_argument("--opponent", default="adversario")
    s.add_argument("--game", type=int, default=1)
    s.add_argument("--resume", nargs="?", const="latest", metavar="STATE",
                   help="retoma a última partida em andamento (ou o .state.json dado)")
    s.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    s.add_argument("--book", type=Path, help=f"book Polyglot (padrão {DEFAULT_BOOK} se existir)")
    s.add_argument("--no-book", action="store_true")
    s.add_argument("--syzygy", type=Path, default=DEFAULT_SYZYGY)
    s.add_argument("--logs", type=Path, default=DEFAULT_LOGS)
    s.add_argument("--threads", type=int)
    s.add_argument("--hash", type=int, dest="hash_mb", metavar="MB")
    return parser


def _new_state(args: argparse.Namespace) -> tuple[GameState, Path]:
    if not args.color:
        raise UsageError("informe --color white|black (ou use --resume)")
    base_ms, inc_ms = parse_tc(args.tc)
    path = log_path(args.logs, args.opponent, args.game, date.today())
    if path.exists():
        raise UsageError(f"log já existe: {path} (use --resume ou outro --game)")
    state = GameState(color=args.color, opponent=args.opponent, game=args.game,
                      base_ms=base_ms, inc_ms=inc_ms, white_ms=base_ms, black_ms=base_ms,
                      log_path=str(path))
    # Nada é gravado aqui: estado e log só nascem depois que o engine abrir,
    # para que uma falha no início permita repetir o mesmo `start`.
    return state, state_path_for(path)


def _resumed_state(args: argparse.Namespace) -> tuple[GameState, Path]:
    if args.resume == "latest":
        state_path = latest_unfinished(args.logs)
        if state_path is None:
            raise UsageError(f"nenhuma partida em andamento em {args.logs}")
    else:
        state_path = Path(args.resume)
    state = load_state(state_path)
    if state.finished:
        raise UsageError(f"partida já encerrada ({state.result}): {state_path}")
    return state, state_path


def _book_path(args: argparse.Namespace) -> Path | None:
    if args.no_book:
        return None
    if args.book is not None:
        return args.book
    return DEFAULT_BOOK if DEFAULT_BOOK.exists() else None


def _recovery_hint(state_path: Path) -> str:
    if state_path.exists():
        return (f"estado salvo em {state_path}; "
                "retome com: python -m controller.main start --resume")
    return "nada foi gravado; corrija o problema e repita o mesmo start"


def open_engine(engine: EngineClient, options: dict[str, int | str]) -> str:
    engine.start()
    info = engine.handshake(timeout=10)
    for name, value in options.items():
        engine.set_option(name, value)
    engine.is_ready(timeout=30)  # alocar Hash grande leva alguns segundos
    engine.send("ucinewgame")
    engine.is_ready(timeout=30)
    return info.get("name", "?")


def main(
    argv: list[str] | None = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    engine_factory: Callable[[Path], EngineClient] = EngineClient,
) -> int:
    args = build_parser().parse_args(argv)
    resumed = args.resume is not None
    book_path = _book_path(args)
    try:
        book = OpeningBook(book_path)
        state, state_path = _resumed_state(args) if resumed else _new_state(args)
    except (UsageError, StateError, ClockFormatError, BookError) as exc:
        output_fn(f"ERRO: {exc}")
        return 2

    options = runtime_options(args.syzygy, threads=args.threads, hash_mb=args.hash_mb)
    if book_path is None:
        output_fn("AVISO: sem book (--book ou assets/book.bin)")
    if "SyzygyPath" not in options:
        output_fn(f"AVISO: sem tablebases em {args.syzygy}")

    clock = GameClock(state.base_ms, state.inc_ms)
    clock.set(chess.WHITE, state.white_ms)
    clock.set(chess.BLACK, state.black_ms)
    log: GameLog | None = None
    engine = engine_factory(args.engine)
    try:
        name = open_engine(engine, options)
        if not resumed:
            state_path.parent.mkdir(parents=True, exist_ok=True)
            save_state(state, state_path)
        log = GameLog(state.log_path)
        if resumed:
            log.note("resume")
        else:
            log.header(engine=name, color=state.color, opponent=state.opponent,
                       game=state.game, tc=args.tc, start_fen=state.start_fen)
        game = Game(state, state_path, engine, book, log, clock,
                    input_fn=input_fn, output_fn=output_fn, paused=resumed)
        output_fn(f"{name} | nós: {state.color} | adversário: {state.opponent} | log: {log.path}")
        if resumed:
            game.show_board()
        game.run()
    except (EngineError, OSError) as exc:
        kind = "DO ENGINE" if isinstance(exc, EngineError) else "DE E/S"
        output_fn(f"ERRO {kind}: {exc}\n{_recovery_hint(state_path)}")
        return 2
    except KeyboardInterrupt:
        output_fn(f"\ninterrompido; {_recovery_hint(state_path)}")
        return 130
    finally:
        engine.quit()
        if log is not None:
            log.close()
        book.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

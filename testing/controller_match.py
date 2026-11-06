#!/usr/bin/env python3
"""Match em tempo real entre duas configurações completas do controller web.

Cada lado é um WebSession de verdade (livro, ponder, relógio interno, latência),
como na partida do torneio. Um repassa o lance do outro via `opponent_move`.
Sem árbitro externo: perde no tempo quem tiver o próprio relógio interno abaixo de zero.
Adjudica empate em repetição tripla, regra dos 50 lances ou avaliação morta prolongada,
e vitória quando os dois engines concordam com vantagem decisiva.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import chess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from controller.engine_client import EngineClient  # noqa: E402
from controller.main import DEFAULT_SYZYGY  # noqa: E402
from controller.runtime import runtime_options  # noqa: E402
from controller.web import WebSession  # noqa: E402

DECISIVE_CP = 500
DECISIVE_PLIES = 4
DEAD_CP = 10
DEAD_PLIES = 20
DEAD_AFTER_PLY = 60


def make(engine: Path, book: Path, ponder: bool, logs: Path, threads: int, hash_mb: int):
    options = runtime_options(DEFAULT_SYZYGY, threads=threads, hash_mb=hash_mb)
    session = WebSession(
        lambda: EngineClient(engine), options, logs, book, clock_latency_s=2.0, ponder=ponder,
    )
    session.open()
    return session


def white_cp(move: dict, mover: chess.Color) -> int | None:
    text = move.get("eval") or ""
    if text.startswith("M") or text.startswith("-M") or text.startswith("#"):
        value = -100000 if text.startswith("-") else 100000
    else:
        try:
            value = round(float(text) * 100)
        except ValueError:
            return None
    return value if mover == chess.WHITE else -value


def wait(session: WebSession) -> None:
    while session.thinking:
        time.sleep(0.02)


def play(white: WebSession, black: WebSession, names: tuple[str, str], game: int, tc: str,
         operator_s: float) -> dict[str, object]:
    white.start_game("white", names[1], game, tc)
    black.start_game("black", names[0], game, tc)
    sides = {chess.WHITE: white, chess.BLACK: black}
    board = chess.Board()
    evals: list[int | None] = []
    stats = {names[0]: {"ponderhit": 0, "engine": 0, "fallback": 0, "think_s": 0.0},
             names[1]: {"ponderhit": 0, "engine": 0, "fallback": 0, "think_s": 0.0}}
    label = {chess.WHITE: names[0], chess.BLACK: names[1]}
    result, reason = None, ""
    while result is None:
        mover = board.turn
        session = sides[mover]
        started = time.monotonic()
        wait(session)
        stats[label[mover]]["think_s"] += time.monotonic() - started
        if session.clock.remaining(mover) < 0:
            result, reason = ("0-1" if mover == chess.WHITE else "1-0"), f"tempo {label[mover]}"
            break
        move = session.snapshot()["our_move"]
        source = move["source"]
        if source in stats[label[mover]]:
            stats[label[mover]][source] += 1
        uci = move["from"] + move["to"] + move["promotion"]
        board.push_uci(uci)
        evals.append(white_cp(move, mover) if source in ("engine", "ponderhit") else None)
        outcome = board.outcome(claim_draw=True)
        if outcome is not None:
            result, reason = outcome.result(), outcome.termination.name.lower()
            break
        recent = [e for e in evals[-DECISIVE_PLIES:] if e is not None]
        if len(recent) == DECISIVE_PLIES and (min(recent) >= DECISIVE_CP or max(recent) <= -DECISIVE_CP):
            result, reason = ("1-0" if recent[0] > 0 else "0-1"), "adjudicada vitória"
            break
        tail = evals[-DEAD_PLIES:]
        if (len(board.move_stack) >= DEAD_AFTER_PLY and len(tail) == DEAD_PLIES
                and all(e is not None and abs(e) <= DEAD_CP for e in tail)):
            result, reason = "1/2-1/2", "adjudicado empate morto"
            break
        time.sleep(operator_s)  # operador executa o lance e o outro digita
        sides[not mover].opponent_move(uci)
    for side in (white, black):
        wait(side)
        if side.state is not None and not side.state.finished:
            side.finish("draw", "fim do match")
    return {
        "game": game, "white": names[0], "black": names[1], "result": result, "reason": reason,
        "plies": len(board.move_stack),
        "clock_left_s": {label[c]: round(sides[c].clock.remaining(c) / 1000) for c in sides},
        "stats": stats, "pgn_moves": " ".join(m.uci() for m in board.move_stack),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--new-engine", type=Path, default=ROOT / "bin" / "stockfish")
    parser.add_argument("--new-book", type=Path, default=ROOT / "assets" / "book.bin")
    parser.add_argument("--base-engine", type=Path, required=True)
    parser.add_argument("--base-book", type=Path, required=True)
    parser.add_argument("--games", type=int, default=2)
    parser.add_argument("--tc", default="600+0")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--hash", type=int, default=1024)
    parser.add_argument("--operator-s", type=float, default=2.0)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    new = make(args.new_engine, args.new_book, True, args.out / "new", args.threads, args.hash)
    base = make(args.base_engine, args.base_book, False, args.out / "base", args.threads, args.hash)
    score = 0.0
    try:
        with (args.out / "games.jsonl").open("a") as out:
            for game in range(1, args.games + 1):
                new_white = game % 2 == 1
                pair = (new, base) if new_white else (base, new)
                names = ("new", "base") if new_white else ("base", "new")
                rec = play(*pair, names, game, args.tc, args.operator_s)
                if rec["result"] == "1/2-1/2":
                    score += 0.5
                elif (rec["result"] == "1-0") == new_white:
                    score += 1
                out.write(json.dumps(rec) + "\n")
                out.flush()
                print(json.dumps({k: rec[k] for k in rec if k != "pgn_moves"}), flush=True)
    finally:
        new.close()
        base.close()
    print(f"new: {score}/{args.games}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

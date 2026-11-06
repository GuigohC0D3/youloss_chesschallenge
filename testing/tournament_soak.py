#!/usr/bin/env python3
"""Simula um dia de torneio: partidas seguidas em tempo real pelo WebSession.

Usa o mesmo perfil, livro e tablebases da partida real. Grava cada lance em JSONL
(tempo, NPS, profundidade, relógio, swap, energia) para mostrar se o desempenho cai
ao longo das horas. O adversário é um Stockfish de 1 thread com tempo fixo por lance.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from controller.engine_client import EngineClient  # noqa: E402
from controller.main import DEFAULT_BOOK, DEFAULT_ENGINE, DEFAULT_SYZYGY  # noqa: E402
from controller.runtime import auto_profile, runtime_options  # noqa: E402
from controller.web import WebSession  # noqa: E402


def machine_state() -> dict[str, object]:
    swap = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True).stdout
    used = re.search(r"used = ([\d.]+)M", swap)
    power = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True).stdout
    therm = subprocess.run(["pmset", "-g", "therm"], capture_output=True, text=True).stdout
    limit = re.search(r"CPU_Speed_Limit\s*=\s*(\d+)", therm)
    return {
        "swap_mb": float(used.group(1)) if used else None,
        "ac": "AC Power" in power,
        "cpu_speed_limit": int(limit.group(1)) if limit else None,
    }


def play_game(session, opponent, color, game, tc, opp_ms, deadline, out) -> dict[str, object]:
    session.start_game(color, "soak", game, tc)
    started = time.monotonic()
    longest = 0.0
    fallbacks = 0
    while not session.state.finished and time.monotonic() < deadline:
        wait_start = time.monotonic()
        while session.thinking:
            time.sleep(0.02)
        think = time.monotonic() - wait_start
        snap = session.snapshot()
        move = snap["our_move"]
        if move:
            longest = max(longest, think)
            fallbacks += move["source"] == "fallback"
            nps = round(move["nodes"] / think) if think > 0.5 and move["nodes"] else None
            record = {
                "game": game, "color": color, "t": round(time.time()), "ply": len(snap["moves"]),
                "san": move["san"], "source": move["source"], "think_s": round(think, 2),
                "depth": move["depth"], "nodes": move["nodes"], "nps": nps, "eval": move["eval"],
                "ours_s": round(snap["ours_ms"] / 1000, 1), **machine_state(),
            }
            out.write(json.dumps(record) + "\n")
            out.flush()
        if session.state.finished:
            break
        moves = " ".join(m.uci() for m in session.board.move_stack)
        position = "position startpos" + (f" moves {moves}" if moves else "")
        reply = opponent.search(position, f"go movetime {opp_ms}", opp_ms / 1000 + 10)
        session.opponent_move(reply.bestmove)
    if not session.state.finished:
        session.finish("draw", "soak-deadline")
    snap = session.snapshot()
    return {
        "game": game, "color": color, "result": snap["result"], "reason": snap["reason"],
        "plies": len(snap["moves"]), "wall_s": round(time.monotonic() - started),
        "longest_think_s": round(longest, 1), "ours_left_s": round(snap["ours_ms"] / 1000),
        "fallbacks": fallbacks, "warning": snap["warning"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=6)
    parser.add_argument("--tc", default="1500+0")
    parser.add_argument("--hours", type=float, default=3.0)
    parser.add_argument("--opponent-ms", type=int, default=2000)
    parser.add_argument("--opponent-engine", type=Path, default=ROOT / "bin" / "stockfish_sf19")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--stock-tm", action="store_true", help="usa o gerenciador original")
    parser.add_argument("--threads", type=int, help="padrão: perfil automático")
    parser.add_argument("--logs", type=Path, help="pasta dos logs de partida (padrão: temporária)")
    args = parser.parse_args()

    threads, hash_mb = auto_profile()
    threads = args.threads or threads
    options = runtime_options(DEFAULT_SYZYGY, threads=threads, hash_mb=hash_mb)
    if args.stock_tm:
        options["YoulossTM"] = "false"
    book = DEFAULT_BOOK if DEFAULT_BOOK.exists() else None
    print(json.dumps({"options": options, "book": str(book)}), flush=True)

    opponent = EngineClient(args.opponent_engine)
    opponent.start()
    opponent.handshake(timeout=10)
    opponent.set_option("Threads", 1)
    opponent.set_option("Hash", 64)
    opponent.is_ready(timeout=10)

    deadline = time.monotonic() + args.hours * 3600
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, args.out.open("a", encoding="utf-8") as out:
        logs = args.logs or tmp
        session = WebSession(
            lambda: EngineClient(DEFAULT_ENGINE), options, Path(logs), book, clock_latency_s=2.0
        )
        print(session.open(), flush=True)
        try:
            for game in range(1, args.games + 1):
                if time.monotonic() >= deadline:
                    break
                color = "white" if game % 2 else "black"
                summary = play_game(
                    session, opponent, color, game, args.tc, args.opponent_ms, deadline, out
                )
                print(json.dumps(summary, ensure_ascii=False), flush=True)
        finally:
            session.close()
            opponent.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())

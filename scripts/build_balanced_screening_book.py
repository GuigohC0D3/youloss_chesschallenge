#!/usr/bin/env python3
"""Build a balanced screening opening book (testing/openings/balanced_gm_v1.epd).

Screening default (UHO_Lichess_4852_v1.epd) is a deliberately imbalanced suite:
paired games from it routinely hand one side >=1.0 pawn at the book exit, which
produces structural losses unrelated to playing strength. Tournament day uses
the sound GM lines compiled into assets/book.bin instead.

This builder reuses those same lines (OPENING_LINES in build_opening_book.py),
emits every position from ply >= MIN_PLY, and keeps only positions whose
Stockfish evaluation magnitude is within --cp-cap centipawns, so a paired
(color-swapped) start position is genuinely balanced.

Output is an EPD/FEN file consumable by fastchess: -openings file=... format=epd.
"""

from __future__ import annotations

import argparse
import importlib.util
import statistics
import subprocess
import sys
from pathlib import Path

import chess

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENGINE = Path("/tmp/youloss-benchmark/stockfish/stockfish-macos-universal")
DEFAULT_OUT = ROOT / "testing" / "openings" / "balanced_gm_v1.epd"
MIN_PLY = 6


def load_opening_lines() -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "build_opening_book", ROOT / "scripts" / "build_opening_book.py"
    )
    if spec is None or spec.loader is None:
        raise SystemExit("FAIL: cannot load scripts/build_opening_book.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.OPENING_LINES)


def collect_positions(lines: list[str]) -> list[tuple[str, int]]:
    positions: dict[str, int] = {}
    for line in lines:
        board = chess.Board()
        for san in line.split():
            board.push_san(san)
            if board.ply() >= MIN_PLY:
                positions.setdefault(board.fen(), board.ply())
    return sorted(positions.items(), key=lambda item: (item[1], item[0]))


class EngineEvaluator:
    def __init__(self, engine_path: Path, depth: int) -> None:
        self.depth = depth
        self.proc = subprocess.Popen(
            [str(engine_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        self._send("uci")
        self._expect("uciok")
        self._send("setoption name Threads value 1")
        self._send("setoption name Hash value 64")
        self._send("isready")
        self._expect("readyok")

    def _send(self, line: str) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def _expect(self, token: str) -> list[str]:
        assert self.proc.stdout is not None
        collected: list[str] = []
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("engine terminated while waiting for " + token)
            collected.append(line.rstrip())
            if token in line:
                return collected

    def evaluate(self, fen: str) -> int | None:
        self._send("position fen " + fen)
        self._send(f"go depth {self.depth}")
        lines = self._expect("bestmove")
        score: int | None = None
        for line in lines:
            if " score cp " in line and f" depth {self.depth}" in line:
                try:
                    score = int(line.split(" score cp ", 1)[1].split()[0])
                except (ValueError, IndexError):
                    score = None
        return score

    def close(self) -> None:
        if self.proc.poll() is None:
            self._send("quit")
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--depth", type=int, default=14)
    parser.add_argument("--cp-cap", type=int, default=40)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if not args.engine.is_file():
        raise SystemExit(f"FAIL: engine not found: {args.engine}")

    lines = load_opening_lines()
    positions = collect_positions(lines)
    print(
        f"source lines={len(lines)} candidate positions={len(positions)} "
        f"(min ply {MIN_PLY})",
        flush=True,
    )

    evaluator = EngineEvaluator(args.engine, args.depth)
    kept: list[tuple[str, int]] = []
    rejected = 0
    mated = 0
    try:
        for index, (fen, ply) in enumerate(positions, start=1):
            score = evaluator.evaluate(fen)
            if score is None:
                rejected += 1
            elif abs(score) > args.cp_cap:
                rejected += 1
            else:
                kept.append((fen, abs(score)))
            if index % 200 == 0:
                print(f"evaluated {index}/{len(positions)}", flush=True)
    finally:
        evaluator.close()

    if not kept:
        raise SystemExit("FAIL: no position survived the balance filter")
    del mated

    kept.sort()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(fen + "\n" for fen, _ in kept))

    magnitudes = [score for _, score in kept]
    print(f"kept={len(kept)} rejected={rejected}")
    print(
        "balance: mean |cp|={:.1f} median={:.1f} max={}".format(
            statistics.mean(magnitudes),
            statistics.median(magnitudes),
            max(magnitudes),
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

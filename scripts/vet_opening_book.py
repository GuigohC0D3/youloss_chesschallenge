#!/usr/bin/env python3
"""Build assets/book.bin from the repertoire, keeping only moves the engine accepts.

Each move inside the book horizon is checked with a fixed-depth search. A move is
dropped when it loses too much against the best move or leaves the mover clearly
worse; anything after a dropped move becomes unreachable and is dropped with it.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

import chess
import chess.polyglot

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from controller.book import MAX_BOOK_PLY  # noqa: E402
from controller.engine_client import EngineClient  # noqa: E402
from scripts.build_opening_book import BOOK_PATH, OPENING_LINES, encode_polyglot_move  # noqa: E402

MAX_LOSS_CP = 35
MIN_SCORE_CP = -50


def collect_tree() -> dict[str, tuple[chess.Board, set[chess.Move]]]:
    """Position EPD -> moves the repertoire plays there, up to the book horizon.

    EPD drops the move counters, so transpositions that differ only in them share one entry,
    as they share one Polyglot key.
    """
    tree: dict[str, tuple[chess.Board, set[chess.Move]]] = {}
    for line in OPENING_LINES:
        board = chess.Board()
        for token in line.split()[:MAX_BOOK_PLY]:
            move = board.parse_san(token)
            key = board.epd()
            tree.setdefault(key, (board.copy(stack=False), set()))[1].add(move)
            board.push(move)
    return tree


def score_cp(engine: EngineClient, board: chess.Board, depth: int) -> int:
    """Score from the point of view of the side to move."""
    if board.is_game_over():
        return 0
    info = engine.search(f"position fen {board.fen()}", f"go depth {depth}", timeout=300)
    if info.score_mate is not None:
        return 30000 if info.score_mate > 0 else -30000
    return info.score_cp or 0


def reachable_keep(tree, verdicts) -> dict[str, list[tuple[chess.Move, int]]]:
    kept: dict[str, list[tuple[chess.Move, int]]] = {}
    stack = [chess.Board()]
    seen = set()
    while stack:
        board = stack.pop()
        key = board.epd()
        if key in seen or key not in tree:
            continue
        seen.add(key)
        for move in sorted(tree[key][1], key=lambda m: m.uci()):
            loss, ok = verdicts[(key, move)]
            if not ok:
                continue
            kept.setdefault(key, []).append((move, loss))
            child = board.copy(stack=False)
            child.push(move)
            stack.append(child)
    return kept


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--depth", type=int, default=20)
    parser.add_argument("--threads", type=int, default=6)
    parser.add_argument("--hash", type=int, default=1024)
    parser.add_argument("--output", type=Path, default=BOOK_PATH)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    tree = collect_tree()
    total = sum(len(moves) for _, moves in tree.values())
    print(f"{len(OPENING_LINES)} lines, {len(tree)} positions, {total} moves", flush=True)

    verdicts: dict[tuple[str, chess.Move], tuple[int, bool]] = {}
    rejected: list[str] = []
    with EngineClient(args.engine) as engine:
        engine.handshake(timeout=10)
        engine.set_option("Threads", args.threads)
        engine.set_option("Hash", args.hash)
        engine.is_ready(timeout=30)
        for key, (board, moves) in tree.items():
            best = score_cp(engine, board, args.depth)
            for move in moves:
                child = board.copy(stack=False)
                child.push(move)
                after = -score_cp(engine, child, args.depth)
                loss = max(0, best - after)
                ok = loss <= MAX_LOSS_CP and after >= MIN_SCORE_CP
                verdicts[(key, move)] = (loss, ok)
                if not ok:
                    san = board.san(move)
                    rejected.append(f"`{key}` {san}: after {after} cp, best {best} cp")
                    print("REJECT", rejected[-1], flush=True)

    kept = reachable_keep(tree, verdicts)
    entries = []
    for key, moves in kept.items():
        hash_key = chess.polyglot.zobrist_hash(chess.Board(f"{key} 0 1"))
        for move, loss in moves:
            weight = max(1, 100 - loss)
            entries.append((hash_key, encode_polyglot_move(move), weight))
    entries.sort()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as handle:
        for hash_key, code, weight in entries:
            handle.write(struct.pack(">QHHI", hash_key, code, weight, 0))

    with chess.polyglot.open_reader(args.output) as reader:
        for key, moves in kept.items():
            board = chess.Board(f"{key} 0 1")
            found = {entry.move for entry in reader.find_all(board)}
            if found != {move for move, _ in moves}:
                raise SystemExit(f"book readback mismatch at {key}: {found}")

    summary = (
        f"{len(entries)} moves kept across {len(kept)} positions; "
        f"{len(rejected)} rejected of {total} (depth {args.depth}, "
        f"loss <= {MAX_LOSS_CP} cp, score >= {MIN_SCORE_CP} cp)."
    )
    print(summary)
    if args.report:
        lines = ["# Checagem do livro de aberturas", "", summary, "", "## Rejeitados", ""]
        lines += [f"- {item}" for item in rejected] or ["- nenhum"]
        args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Gera um book Polyglot mínimo para testes (sem promoção nem roque)."""
from __future__ import annotations

import struct
from pathlib import Path

import chess
import chess.polyglot


def write_book(path: Path, entries: list[tuple[chess.Board, str, int]]) -> None:
    rows = []
    for board, uci, weight in entries:
        move = chess.Move.from_uci(uci)
        raw = move.to_square | (move.from_square << 6)
        rows.append((chess.polyglot.zobrist_hash(board), raw, weight))
    rows.sort()
    with open(path, "wb") as f:
        for key, raw, weight in rows:
            f.write(struct.pack(">QHHI", key, raw, weight, 0))

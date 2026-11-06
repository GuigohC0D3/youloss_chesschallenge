#!/usr/bin/env python3
"""Remove do livro as nossas escolhas que levam a posições secas de empate.

O livro guarda lances dos dois lados, mas só é consultado na nossa vez. Tirar uma
entrada muda só o que *nós* escolhemos naquela posição; se o adversário jogar o
lance removido, as entradas seguintes continuam no livro.
Motivo: em 2026-11-06 os quatro empates contra outros Stockfish vieram da Inglesa,
da Berlinense e da Espanhola Aberta (avaliação 0,00 antes do lance 20).
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
from scripts.build_opening_book import encode_polyglot_move  # noqa: E402

# (lances até a posição, lance que deixamos de escolher)
DROP: list[tuple[str, str]] = [
    # brancas: só 1.e4, com linhas abertas
    ("", "Nf3"), ("", "c4"), ("", "d4"),
    ("e4 c5", "Nc3"), ("e4 c5", "c3"),
    ("e4 c5 Nf3 Nc6", "Bb5"),
    ("e4 e5 Nf3 Nc6", "Bb5"),          # evita a Berlinense
    ("e4 e5 Nf3 Nc6 Bc4 Bc5", "b4"),
    ("e4 e5 Nf3 Nc6 Bc4 Nf6", "d4"),
    ("e4 c6 d4 d5", "exd5"),
    # pretas: Siciliana contra 1.e4, Cf6 contra 1.d4
    ("e4", "e5"), ("e4", "e6"), ("e4", "c6"),
    ("d4", "d5"),
    ("c4", "c5"),
]


def drop_keys() -> set[tuple[int, int]]:
    keys = set()
    for path, san in DROP:
        board = chess.Board()
        for token in path.split():
            board.push_san(token)
        keys.add((chess.polyglot.zobrist_hash(board), encode_polyglot_move(board.parse_san(san))))
    return keys


def prune(src: Path, dst: Path) -> tuple[int, int]:
    drop = drop_keys()
    data = src.read_bytes()
    kept = bytearray()
    removed = 0
    for off in range(0, len(data), 16):
        key, code, _w, _l = struct.unpack(">QHHI", data[off:off + 16])
        if (key, code) in drop:
            removed += 1
            continue
        kept += data[off:off + 16]
    if removed != len(drop):
        raise SystemExit(f"esperava remover {len(drop)} entradas, removi {removed}")
    dst.write_bytes(bytes(kept))
    return removed, len(kept) // 16


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", type=Path, default=ROOT / "assets" / "book.bin")
    parser.add_argument("--output", type=Path, default=ROOT / "assets" / "book.bin")
    args = parser.parse_args()
    removed, left = prune(args.book, args.output)
    print(f"removidas {removed} entradas; restam {left}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

import random
from collections import Counter

import chess
import pytest

from controller.book import BookError, OpeningBook, game_ply
from controller.tests.polyglot import write_book

# Giuoco Piano: 16 meios-lances.
LINE = [
    "e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "c2c3", "g8f6",
    "d2d4", "e5d4", "c3d4", "c5b4", "c1d2", "b4d2", "b1d2", "d7d5",
]


def board_after(n: int) -> chess.Board:
    board = chess.Board()
    for uci in LINE[:n]:
        board.push_uci(uci)
    return board


def test_game_ply():
    assert game_ply(chess.Board()) == 0
    assert game_ply(board_after(1)) == 1
    assert game_ply(board_after(16)) == 16


def test_varies_moves_by_weight(tmp_path):
    path = tmp_path / "b.bin"
    write_book(path, [(chess.Board(), "d2d4", 30), (chess.Board(), "e2e4", 70)])
    book = OpeningBook(path, rng=random.Random(7))
    picks = Counter(book.pick(chess.Board()).uci() for _ in range(2000))
    book.close()
    assert set(picks) == {"d2d4", "e2e4"}
    assert 0.25 < picks["d2d4"] / 2000 < 0.35


def test_single_entry_is_always_picked(tmp_path):
    path = tmp_path / "b.bin"
    write_book(path, [(chess.Board(), "e2e4", 1)])
    book = OpeningBook(path)
    assert {book.pick(chess.Board()) for _ in range(20)} == {chess.Move.from_uci("e2e4")}
    book.close()


def test_cut_at_ply_16(tmp_path):
    path = tmp_path / "b.bin"
    write_book(path, [(board_after(15), "d7d5", 1), (board_after(16), "e4d5", 1)])
    book = OpeningBook(path)
    assert book.pick(board_after(15)) == chess.Move.from_uci("d7d5")
    assert book.pick(board_after(16)) is None
    book.close()


def test_unknown_position_returns_none(tmp_path):
    path = tmp_path / "b.bin"
    write_book(path, [(chess.Board(), "e2e4", 1)])
    book = OpeningBook(path)
    assert book.pick(board_after(1)) is None
    book.close()


def test_no_book():
    assert OpeningBook(None).pick(chess.Board()) is None


def test_empty_book_file(tmp_path):
    path = tmp_path / "vazio.bin"
    path.write_bytes(b"")
    assert OpeningBook(path).pick(chess.Board()) is None


def test_missing_book_raises(tmp_path):
    with pytest.raises(BookError, match="nao_existe.bin"):
        OpeningBook(tmp_path / "nao_existe.bin")

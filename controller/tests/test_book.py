import chess
import pytest

from controller.book import BookError, OpeningBook, game_ply
from controller.tests.polyglot import write_book

# Giuoco Piano: 10 meios-lances.
LINE = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "c2c3", "g8f6", "d2d4", "e5d4"]


def board_after(n: int) -> chess.Board:
    board = chess.Board()
    for uci in LINE[:n]:
        board.push_uci(uci)
    return board


def test_game_ply():
    assert game_ply(chess.Board()) == 0
    assert game_ply(board_after(1)) == 1
    assert game_ply(board_after(10)) == 10


def test_picks_highest_weight(tmp_path):
    path = tmp_path / "b.bin"
    write_book(path, [(chess.Board(), "d2d4", 5), (chess.Board(), "e2e4", 9)])
    book = OpeningBook(path)
    assert book.pick(chess.Board()) == chess.Move.from_uci("e2e4")
    book.close()


def test_cut_at_ply_10(tmp_path):
    path = tmp_path / "b.bin"
    write_book(path, [(board_after(9), "e5d4", 1), (board_after(10), "c3d4", 1)])
    book = OpeningBook(path)
    assert book.pick(board_after(9)) == chess.Move.from_uci("e5d4")
    assert book.pick(board_after(10)) is None
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

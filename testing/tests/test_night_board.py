"""Pure-function tests for the chess.com night harness."""

from __future__ import annotations

from pathlib import Path

import chess
import pytest

from testing.night.board import (
    BoardError,
    board_from_pieces,
    board_from_san,
    cross_check,
    normalize_san,
    pieces_from_classes,
    result_for,
)
from testing.night.chesscom import Snapshot, parse_clock
from testing.night.config import RunSpec
from testing.night.recorder import Recorder
from testing.night.runner import ClockTracker, modal_result


def test_normalize_san_accepts_common_forms():
    assert normalize_san("e4") == "e4"
    assert normalize_san("Nf3!?") == "Nf3"
    assert normalize_san("0-0") == "O-O"
    assert normalize_san("...Nf6") == "Nf6"
    assert normalize_san("e7e8=Q") is None  # coordinates are not SAN
    assert normalize_san("e8Q") == "e8=Q"
    assert normalize_san("1.") is None


def test_board_from_san_replays_moves():
    board = board_from_san(chess.STARTING_FEN, ["e4", "d5", "Nf3"])
    assert board.fen().startswith(
        "rnbqkbnr/ppp1pppp/8/3p4/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq"
    )


def test_board_from_san_reports_bad_ply():
    with pytest.raises(BoardError, match="lance 3"):
        board_from_san(chess.STARTING_FEN, ["e4", "e5", "e4"])


def test_result_for_fools_mate():
    board = board_from_san(chess.STARTING_FEN, ["f3", "e5", "g4", "Qh4#"])
    assert result_for(board, chess.WHITE) == ("0-1", "checkmate")


def test_piece_classes_build_initial_position():
    classes = [
        "piece br square-18",
        "piece bn square-28",
        "piece bb square-38",
        "piece bq square-48",
        "piece bk square-58",
        "piece bb square-68",
        "piece bn square-78",
        "piece br square-88",
        "piece bp square-17",
        "piece bp square-27",
        "piece bp square-37",
        "piece bp square-47",
        "piece bp square-57",
        "piece bp square-67",
        "piece bp square-77",
        "piece bp square-87",
        "piece wr square-11",
        "piece wn square-21",
        "piece wb square-31",
        "piece wq square-41",
        "piece wk square-51",
        "piece wb square-61",
        "piece wn square-71",
        "piece wr square-81",
        "piece wp square-12",
        "piece wp square-22",
        "piece wp square-32",
        "piece wp square-42",
        "piece wp square-52",
        "piece wp square-62",
        "piece wp square-72",
        "piece wp square-82",
    ]
    board = board_from_pieces(classes, turn=chess.WHITE)
    assert board.board_fen() == chess.Board().board_fen()
    assert cross_check(chess.Board(), classes)


def test_piece_classes_reject_bad_square():
    with pytest.raises(BoardError):
        pieces_from_classes(["piece wp square-99"])


def test_parse_clock_variants():
    assert parse_clock("3:01") == 181_000
    assert parse_clock("0:05.3") == 5_300
    assert parse_clock("Maximum\n(3200)\n3:01") == 181_000
    assert parse_clock("") is None


def test_snapshot_maps_clocks_to_colors():
    snap = Snapshot(
        url="",
        title="",
        board=True,
        board_rect=None,
        orientation="white",
        sans=[],
        stamps=[],
        rows=[
            {"top": True, "username": "Maximum", "clock": "3:00", "text": ""},
            {"top": False, "username": "vito", "clock": "2:58", "text": ""},
        ],
        pieces=[],
        modal_text="",
        body="",
        member=None,
        buttons=[],
        promotion=False,
    )
    assert snap.clock_ms(chess.BLACK) == 180_000
    assert snap.clock_ms(chess.WHITE) == 178_000
    assert snap.our_username == "vito"


def test_modal_result():
    assert modal_result("You won by checkmate", "vito", chess.WHITE) == ("1-0", "win")
    assert modal_result("You lost", "vito", chess.BLACK) == ("1-0", "loss")
    assert modal_result("Draw by agreement", "vito", chess.WHITE) == ("1/2-1/2", "draw")
    assert modal_result("Maximum won by resignation", "vito", chess.WHITE) == (
        "0-1",
        "loss",
    )


def test_clock_tracker_uses_increment():
    now = [100.0]
    clock = ClockTracker(180_000, 2_000, now=lambda: now[0])
    now[0] += 1.0
    clock.press(chess.WHITE)
    assert clock.remaining(chess.WHITE) == pytest.approx(181_000, abs=2)
    assert clock.remaining(chess.BLACK) == pytest.approx(180_000, abs=2)


def test_recorder_writes_standard_pgn(tmp_path: Path):
    spec = RunSpec(max_games=1, max_hours=1, out_dir=tmp_path)
    recorder = Recorder(spec)
    path = recorder.write_pgn(
        1,
        start_fen=chess.STARTING_FEN,
        moves_uci=["e2e4", "e7e5"],
        headers={"White": "A", "Black": "B", "Result": "*"},
    )
    text = path.read_text(encoding="utf-8")
    assert "1. e4 e5" in text
    recorder.finish(result="test")


def test_run_spec_allows_unlimited(tmp_path: Path):
    spec = RunSpec(max_games=0, max_hours=0, out_dir=tmp_path)
    assert spec.max_hours == 0


def test_run_spec_rejects_negative_hours(tmp_path: Path):
    with pytest.raises(ValueError):
        RunSpec(max_games=0, max_hours=-1, out_dir=tmp_path)

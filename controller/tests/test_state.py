import json
import os

import chess
import pytest

from controller.state import (
    GameState, StateError, latest_unfinished, load_state, save_state, state_path_for,
)


def sample(**kw) -> GameState:
    base = dict(color="white", opponent="x", game=1, base_ms=900_000, inc_ms=10_000,
                moves=["e2e4", "e7e5"], white_ms=880_000, black_ms=870_000, log_path="l.log")
    base.update(kw)
    return GameState(**base)


def test_roundtrip(tmp_path):
    path = tmp_path / "g.state.json"
    save_state(sample(), path)
    assert load_state(path) == sample()
    assert not list(tmp_path.glob("*.tmp"))


def test_board_replays_moves():
    board = sample().board()
    assert board.fullmove_number == 2 and board.turn == chess.WHITE
    assert sample().us() == chess.WHITE and sample(color="black").us() == chess.BLACK


def test_finished():
    assert not sample().finished
    assert sample(result="1-0", reason="checkmate").finished


def test_state_path_for(tmp_path):
    assert state_path_for(tmp_path / "2026-10-28_x_g1.log") == tmp_path / "2026-10-28_x_g1.state.json"


@pytest.mark.parametrize("content, match", [
    ("{meio escrito", "corrompido"),
    (json.dumps({"version": 99}), "versão"),
    (json.dumps({"version": 1, "color": "white"}), "campos"),
])
def test_bad_files_raise_state_error(tmp_path, content, match):
    path = tmp_path / "g.state.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(StateError, match=match):
        load_state(path)


def test_illegal_moves_raise_state_error(tmp_path):
    path = tmp_path / "g.state.json"
    save_state(sample(moves=["e2e5"]), path)
    with pytest.raises(StateError, match="lances"):
        load_state(path)


def test_missing_raises_state_error(tmp_path):
    with pytest.raises(StateError, match="não encontrado"):
        load_state(tmp_path / "nada.state.json")


def test_latest_unfinished(tmp_path):
    old, done, new = (tmp_path / f"{n}.state.json" for n in ("old", "done", "new"))
    save_state(sample(game=1), old)
    save_state(sample(game=2, result="1-0", reason="resign_opponent"), done)
    save_state(sample(game=3), new)
    (tmp_path / "bad.state.json").write_text("{", encoding="utf-8")
    os.utime(old, (1000, 1000))
    os.utime(new, (2000, 2000))
    os.utime(done, (3000, 3000))
    assert latest_unfinished(tmp_path) == new
    assert latest_unfinished(tmp_path / "vazio") is None

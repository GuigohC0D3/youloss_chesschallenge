import json
import os

import chess
import pytest

from controller.state import (
    GameState,
    StateError,
    latest_unfinished,
    load_state,
    save_state,
    state_path_for,
)


def sample(**kw) -> GameState:
    base = dict(
        color="white",
        opponent="x",
        game=1,
        base_ms=900_000,
        inc_ms=10_000,
        moves=["e2e4", "e7e5"],
        white_ms=880_000,
        black_ms=870_000,
        log_path="l.log",
    )
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
    assert (
        state_path_for(tmp_path / "2026-10-28_x_g1.log")
        == tmp_path / "2026-10-28_x_g1.state.json"
    )


@pytest.mark.parametrize(
    "content, match",
    [
        ("{meio escrito", "corrompido"),
        (json.dumps({"version": 99}), "versão"),
        (json.dumps({"version": 1, "color": "white"}), "campos"),
    ],
)
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


@pytest.mark.parametrize(
    "patch",
    [
        {"moves": None},
        {"moves": [1, 2]},
        {"color": "red"},
        {"white_ms": "abc"},
        {"game": True},
        {"result": 1},
    ],
)
def test_wrong_field_types_raise_state_error(tmp_path, patch):
    path = tmp_path / "g.state.json"
    save_state(sample(), path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(patch)
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(StateError):
        load_state(path)


def test_undecodable_file_raises_state_error_and_is_skipped(tmp_path):
    bad = tmp_path / "bad.state.json"
    bad.write_bytes(b"\xff\xfe\x00lixo")
    with pytest.raises(StateError, match="corrompido"):
        load_state(bad)
    assert latest_unfinished(tmp_path) is None


def test_save_retries_when_file_is_locked(tmp_path, monkeypatch):
    import controller.state as state_mod

    real_replace = os.replace
    calls = []

    def flaky_replace(src, dst):
        calls.append(dst)
        if len(calls) == 1:
            raise PermissionError("arquivo em uso (antivírus)")
        real_replace(src, dst)

    monkeypatch.setattr(state_mod.os, "replace", flaky_replace)
    save_state(sample(), tmp_path / "g.state.json")
    assert len(calls) == 2 and load_state(tmp_path / "g.state.json") == sample()


def test_pending_proposal_roundtrip(tmp_path):
    path = tmp_path / "g.state.json"
    s = sample(
        pending_uci="e2e4",
        pending_source="engine",
        pending_depth=12,
        pending_seldepth=20,
        pending_nodes=999,
        pending_score_cp=35,
        pending_score_mate=None,
        pending_pv=["e2e4", "e7e5"],
    )
    save_state(s, path)
    assert load_state(path) == s


def test_v1_state_still_loads(tmp_path):
    import json as _json

    from controller.state import STATE_VERSION

    assert STATE_VERSION == 2
    path = tmp_path / "g.state.json"
    save_state(sample(), path)
    data = _json.loads(path.read_text(encoding="utf-8"))
    for key in [k for k in data if k.startswith("pending_")]:
        del data[key]
    data["version"] = 1
    path.write_text(_json.dumps(data), encoding="utf-8")
    loaded = load_state(path)
    assert loaded.pending_uci is None and loaded.pending_source is None
    assert loaded.moves == ["e2e4", "e7e5"]


def test_bad_pending_rejected(tmp_path):
    import json as _json

    path = tmp_path / "g.state.json"
    save_state(sample(), path)
    data = _json.loads(path.read_text(encoding="utf-8"))
    data["pending_uci"] = "e2e4"
    data["pending_source"] = None
    path.write_text(_json.dumps(data), encoding="utf-8")
    with pytest.raises(StateError):
        load_state(path)


@pytest.mark.parametrize("bad_pv", ["e2e4", 123, {"a": 1}, ["e2e4", 42], None])
def test_malformed_pending_pv_raises_state_error_not_type_error(tmp_path, bad_pv):
    import json as _json

    path = tmp_path / "g.state.json"
    save_state(sample(), path)
    data = _json.loads(path.read_text(encoding="utf-8"))
    data["pending_pv"] = bad_pv
    path.write_text(_json.dumps(data), encoding="utf-8")
    with pytest.raises(StateError):
        load_state(path)

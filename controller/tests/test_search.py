import sys
import time
from pathlib import Path

import pytest

from controller.engine_client import (
    EngineClient, EngineCrashed, EngineTimeout, SearchInfo, parse_info,
)

FAKE = Path(__file__).with_name("fake_engine.py")
GO = "go wtime 60000 btime 60000 winc 0 binc 0"


def fake(mode: str) -> EngineClient:
    return EngineClient(sys.executable, args=[str(FAKE), mode])


def test_search_returns_bestmove_and_last_info():
    with fake("ok") as eng:
        eng.handshake(timeout=5)
        info = eng.search("position startpos", GO, timeout=5)
    assert info.bestmove == "a2a3"
    assert (info.depth, info.seldepth, info.nodes) == (5, 7, 1234)
    assert (info.score_cp, info.score_mate) == (12, None)
    assert info.pv == ["a2a3"]
    assert info.stopped is False


def test_search_applies_fen_and_moves():
    fen = "8/8/8/8/8/k7/p7/7K w - - 0 1"
    with fake("ok") as eng:
        eng.handshake(timeout=5)
        info = eng.search(f"position fen {fen} moves h1g1 a2a1q", GO, timeout=5)
    assert info.bestmove in {"g1f2", "g1g2", "g1h2"}


def test_slow_engine_gets_stop_and_answers():
    with fake("slow") as eng:
        eng.handshake(timeout=5)
        t0 = time.monotonic()
        info = eng.search("position startpos", GO, timeout=0.3)
    assert info.stopped is True
    assert info.bestmove == "a2a3"
    assert time.monotonic() - t0 < 2.0


def test_deaf_engine_times_out_after_stop_grace():
    with fake("deaf") as eng:
        eng.handshake(timeout=5)
        t0 = time.monotonic()
        with pytest.raises(EngineTimeout, match="stop"):
            eng.search("position startpos", GO, timeout=0.2, stop_grace=0.3)
    assert time.monotonic() - t0 < 2.0


def test_engine_dying_on_go_raises_crashed():
    with fake("dieongo") as eng:
        eng.handshake(timeout=5)
        with pytest.raises(EngineCrashed):
            eng.search("position startpos", GO, timeout=5)


def parsed(*lines: str) -> SearchInfo:
    info = SearchInfo(bestmove="")
    for line in lines:
        parse_info(line, info)
    return info


def test_parse_info_mate_and_pv():
    info = parsed("info depth 20 seldepth 30 multipv 1 score mate -3 nodes 99 nps 1 pv e2e4 e7e5")
    assert (info.score_cp, info.score_mate, info.pv) == (None, -3, ["e2e4", "e7e5"])


def test_parse_info_ignores_bounds_multipv_and_garbage():
    base = "info depth 10 seldepth 12 multipv 1 score cp 30 nodes 500 pv d2d4"
    info = parsed(
        base,
        "info depth 11 seldepth 13 multipv 1 score cp 90 lowerbound nodes 600 pv e2e4",
        "info depth 11 seldepth 13 multipv 2 score cp 10 nodes 600 pv c2c4",
        "info depth x score cp y pv",
        "info string NNUE evaluation using nn.nnue",
    )
    assert (info.depth, info.score_cp, info.pv) == (10, 30, ["d2d4"])

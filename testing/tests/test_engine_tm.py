import re
import subprocess
import time
from pathlib import Path

import pytest

from controller.engine_client import EngineClient, SearchInfo
from controller.main import DEFAULT_ENGINE

ROOT = Path(__file__).resolve().parents[2]
REAL = DEFAULT_ENGINE
BENCH_NODES = 2497913
pytestmark = pytest.mark.skipif(not REAL.exists(), reason="engine não compilado")


def engine(**options) -> EngineClient:
    eng = EngineClient(REAL)
    eng.start()
    eng.handshake(timeout=10)
    for name, value in {"Threads": 1, "Hash": 16, **options}.items():
        eng.set_option(name, value)
    eng.is_ready(timeout=30)
    return eng


def timed(eng: EngineClient, position: str, go: str) -> tuple[SearchInfo, float]:
    t0 = time.perf_counter()
    info = eng.search(position, go, timeout=60)
    return info, (time.perf_counter() - t0) * 1000


def test_option_listed_with_default_true():
    with EngineClient(REAL) as eng:
        eng.send("uci")
        lines = eng.read_until("uciok", timeout=10)
    assert "option name YoulossTM type check default true" in lines


def test_forced_move_is_immediate():
    eng = engine()
    try:
        info, ms = timed(eng, "position fen k7/8/8/8/8/8/1r6/K7 w - - 0 1",
                         "go wtime 60000 btime 60000 winc 1000 binc 1000")
    finally:
        eng.quit()
    assert info.bestmove == "a1b2"
    assert ms < 300


@pytest.mark.parametrize("threads", [1, 4])
def test_think_time_within_maximum(threads):
    # 8 s, sem incremento, material completo: maximum = min(5*177, 2000) = 888 ms
    eng = engine(Threads=threads)
    try:
        info, ms = timed(eng, "position startpos", "go wtime 8000 btime 8000 winc 0 binc 0")
    finally:
        eng.quit()
    assert info.depth >= 1
    assert ms <= 888 + 150


def test_below_reserve_answers_fast():
    eng = engine(**{"Move Overhead": 1500})
    try:
        info, ms = timed(eng, "position startpos", "go wtime 2500 btime 2500 winc 0 binc 0")
    finally:
        eng.quit()
    assert info.bestmove
    assert ms < 250


def test_movetime_and_depth_ignore_youloss_tm():
    eng = engine()
    try:
        _, ms = timed(eng, "position startpos", "go movetime 400")
        info, _ = timed(eng, "position startpos", "go depth 6")
    finally:
        eng.quit()
    assert 350 <= ms <= 700
    assert info.depth == 6


def test_movestogo_uses_original_and_still_moves():
    eng = engine()
    try:
        info, ms = timed(eng, "position startpos", "go wtime 8000 btime 8000 movestogo 20")
    finally:
        eng.quit()
    assert info.bestmove and ms < 8000


def test_ponderhit_returns_within_limit():
    eng = engine(Ponder=True)
    try:
        eng.send("position startpos moves e2e4")
        eng.send("go ponder wtime 8000 btime 8000 winc 0 binc 0")
        time.sleep(0.2)
        t0 = time.perf_counter()
        eng.send("ponderhit")
        lines = eng.read_until("bestmove", timeout=10)
        ms = (time.perf_counter() - t0) * 1000
    finally:
        eng.quit()
    assert lines[-1].startswith("bestmove")
    assert ms <= 888 + 150


def test_original_tm_still_selectable():
    eng = engine(YoulossTM=False)
    try:
        info, ms = timed(eng, "position startpos", "go wtime 8000 btime 8000 winc 0 binc 0")
    finally:
        eng.quit()
    assert info.bestmove and ms < 8000 * 0.81


def test_bench_unchanged():
    out = subprocess.run([str(REAL), "bench"], capture_output=True, text=True, timeout=300)
    m = re.search(r"Nodes searched\s*:\s*(\d+)", out.stdout + out.stderr)
    assert m and int(m[1]) == BENCH_NODES

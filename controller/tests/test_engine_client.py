import sys
from pathlib import Path

import pytest

from controller.engine_client import (
    EngineClient, EngineCrashed, EngineError, EngineNotFound, EngineTimeout,
)
from controller.main import DEFAULT_ENGINE

FAKE = Path(__file__).with_name("fake_engine.py")
REAL = DEFAULT_ENGINE


def fake(mode: str) -> EngineClient:
    return EngineClient(sys.executable, args=[str(FAKE), mode])


def test_handshake_returns_id():
    with fake("ok") as eng:
        info = eng.handshake(timeout=5)
        eng.is_ready(timeout=5)
    assert info == {"name": "FakeFish 1.0", "author": "Youloss"}


def test_missing_binary_raises_not_found():
    eng = EngineClient("C:/nao/existe/engine.exe")
    with pytest.raises(EngineNotFound, match="nao/existe"):
        eng.start()


def test_hanging_engine_times_out():
    with fake("hang") as eng:
        with pytest.raises(EngineTimeout):
            eng.handshake(timeout=0.5)


def test_crashing_engine_raises_crashed():
    with fake("crash") as eng:
        with pytest.raises(EngineCrashed):
            eng.handshake(timeout=5)


@pytest.mark.skipif(not REAL.exists(), reason="engine não compilado")
def test_real_engine_handshake():
    with EngineClient(REAL) as eng:
        info = eng.handshake(timeout=10)
        eng.set_option("Threads", 1)
        eng.is_ready(timeout=10)
    assert "Stockfish" in info["name"]


def test_restart_same_instance():
    eng = fake("ok")
    eng.start()
    eng.handshake(timeout=5)
    eng.quit()
    eng.start()
    info = eng.handshake(timeout=5)
    eng.quit()
    assert info["name"] == "FakeFish 1.0"


def test_read_until_timeout_is_total_not_per_line():
    import time
    with fake("spam") as eng:
        eng.send("go infinite")
        t0 = time.monotonic()
        with pytest.raises(EngineTimeout):
            eng.read_until("bestmove", timeout=0.5)
        assert time.monotonic() - t0 < 2.0


def test_non_executable_raises_engine_error():
    eng = EngineClient(FAKE)  # .py não é executável no Windows (WinError 193)
    with pytest.raises(EngineError, match="fake_engine.py"):
        eng.start()


def test_stderr_flood_does_not_block_search_and_stays_bounded():
    eng = fake("stderr_flood")
    eng.stderr_max_lines = 50
    eng.stderr_max_bytes = 4096
    with eng:
        eng.handshake(timeout=5)
        eng.is_ready(timeout=5)
        info = eng.search("position startpos", "go wtime 10000 btime 10000", timeout=5)
        assert info.bestmove != ""
        tail = eng.stderr_tail()
        assert len(tail) <= 50
        assert sum(len(line.encode("utf-8")) for line in tail) <= 4096
        assert any("flood line" in line for line in tail)


def test_giant_stderr_line_without_newline_does_not_block_search():
    eng = fake("stderr_giant_no_newline")
    eng.stderr_max_lines = 8
    eng.stderr_max_bytes = 4096
    with eng:
        eng.handshake(timeout=5)
        info = eng.search("position startpos", "go wtime 10000 btime 10000", timeout=5)
        assert info.bestmove
        tail = eng.stderr_tail()
        assert tail
        assert len(tail) <= 8
        assert sum(len(line.encode("utf-8")) for line in tail) <= 4096


def test_stderr_sanitizes_control_chars_and_newlines():
    with fake("control_chars") as eng:
        eng.handshake(timeout=5)
        import time
        time.sleep(0.1)
        tail = eng.stderr_tail()
        assert any("error with ansi" in line for line in tail)
        for line in tail:
            assert "\x1b" not in line
            assert "\r" not in line
            assert "\n" not in line
            assert "\x07" not in line
            assert "\x00" not in line


def test_crash_and_restart_isolation():
    eng = fake("crash_with_stderr")
    with pytest.raises(EngineCrashed):
        with eng:
            eng.handshake(timeout=5)
    assert eng.exit_code == 5
    crash_tail = eng.stderr_tail()
    assert any("corrupted hash table" in line for line in crash_tail)

    # Restart with 'ok' mode on same client
    eng.args = [str(FAKE), "ok"]
    eng.start()
    try:
        assert eng.stderr_tail() == []
        info = eng.handshake(timeout=5)
        assert info["name"] == "FakeFish 1.0"
        assert eng.stderr_tail() == []
    finally:
        eng.quit()

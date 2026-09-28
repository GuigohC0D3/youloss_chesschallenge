import sys
from pathlib import Path

import pytest

from controller.engine_client import (
    EngineClient, EngineCrashed, EngineNotFound, EngineTimeout,
)

FAKE = Path(__file__).with_name("fake_engine.py")
REAL = Path(__file__).resolve().parents[2] / "bin" / "youloss.exe"


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

from pathlib import Path

import pytest

from controller.engine_client import EngineClient
from controller.runtime import free_memory_mb, has_syzygy, runtime_options
from controller.main import DEFAULT_ENGINE

ROOT = Path(__file__).resolve().parents[2]
REAL = DEFAULT_ENGINE
SYZYGY = ROOT / "assets" / "syzygy"


def test_defaults_from_machine(tmp_path):
    opts = runtime_options(tmp_path, cpus=8, free_mb=10_000)
    assert opts == {"Threads": 7, "Hash": 5_000, "Move Overhead": 1500, "SyzygyProbeLimit": 5}


def test_limits(tmp_path):
    assert runtime_options(tmp_path, cpus=1, free_mb=10)["Threads"] == 1
    assert runtime_options(tmp_path, cpus=1, free_mb=10)["Hash"] == 16
    assert runtime_options(tmp_path, cpus=4, free_mb=64_000)["Hash"] == 16_384


def test_overrides(tmp_path):
    opts = runtime_options(tmp_path, threads=1, hash_mb=16, cpus=8, free_mb=10_000)
    assert (opts["Threads"], opts["Hash"]) == (1, 16)


def test_syzygy_path_only_when_tables_exist(tmp_path):
    assert "SyzygyPath" not in runtime_options(tmp_path / "nao_existe", cpus=2, free_mb=64)
    (tmp_path / "KQvK.rtbw").touch()
    assert has_syzygy(tmp_path)
    assert runtime_options(tmp_path, cpus=2, free_mb=64)["SyzygyPath"] == str(tmp_path.resolve())


def test_free_memory_is_positive():
    assert free_memory_mb() > 0


@pytest.mark.skipif(not REAL.exists(), reason="engine não compilado")
def test_real_engine_accepts_every_option(tmp_path):
    with EngineClient(REAL) as eng:
        eng.handshake(timeout=10)
        for name, value in runtime_options(tmp_path, cpus=2, free_mb=64).items():
            eng.set_option(name, value)
        eng.send("isready")
        lines = eng.read_until("readyok", timeout=10)
    assert not [line for line in lines if "No such option" in line]


@pytest.mark.skipif(not (REAL.exists() and has_syzygy(SYZYGY)), reason="sem engine ou Syzygy")
def test_real_engine_probes_syzygy():
    with EngineClient(REAL) as eng:
        eng.handshake(timeout=10)
        for name, value in runtime_options(SYZYGY, threads=1, hash_mb=16).items():
            eng.set_option(name, value)
        eng.is_ready(timeout=30)
        eng.send("position fen 8/8/8/8/8/2k5/8/KQ6 w - - 0 1")
        eng.send("go depth 10")
        lines = eng.read_until("bestmove", timeout=30)
    hits = [int(t[t.index("tbhits") + 1]) for t in (l.split() for l in lines) if "tbhits" in t]
    assert hits and max(hits) > 0


def test_profile_for_m4_and_m5_ten_core_16gb():
    from controller.runtime import profile_for

    assert profile_for(perf=4, eff=6, total_mb=16384, free_mb=9000) == (6, 2048)


def test_profile_for_respects_free_memory_and_larger_chips():
    from controller.runtime import profile_for

    assert profile_for(perf=4, eff=6, total_mb=16384, free_mb=1000) == (6, 500)
    assert profile_for(perf=10, eff=4, total_mb=24576, free_mb=20000) == (11, 3072)

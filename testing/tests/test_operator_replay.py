"""Tests for operator replay qualification harness."""
import re

import pytest
from pathlib import Path

from testing.operator_replay import ReplayDelays, run_simulated_replay


def test_operator_replay_normal_evidence(tmp_path: Path):
    delays = ReplayDelays(
        clock_read_s=0.5,
        uci_entry_s=0.5,
        piece_move_s=0.5,
        clock_press_s=0.5,
        opp_think_s=1.0,
    )
    evidence = run_simulated_replay(tmp_path, scenario="normal", delays=delays)
    assert evidence["data_type"] == "simulated"
    assert "simulated values, not measured operator data" in evidence["disclaimer"]
    assert evidence["final_state"]["result"] is None
    assert len(evidence["final_state"]["moves"]) == 3
    for obs in evidence["search_observations"]:
        assert obs["budget_fits"] is True


def test_operator_replay_debits_reading_and_piece_handling(tmp_path: Path):
    quick = ReplayDelays(clock_read_s=0.25, piece_move_s=0.25)
    slow = ReplayDelays(clock_read_s=1.25, piece_move_s=1.25)
    first = run_simulated_replay(tmp_path / "quick", delays=quick)
    second = run_simulated_replay(tmp_path / "slow", delays=slow)
    # The physical clock reading replaces the first estimated remaining time.
    # The first move log still records the extra second spent moving the piece.
    def first_move_time(name: str) -> int:
        log = (tmp_path / name / "replay.log").read_text()
        match = re.search(r"^move=1 color=white .* time_ms=(\d+) source=engine$", log, re.MULTILINE)
        assert match is not None
        return int(match.group(1))

    assert first_move_time("slow") - first_move_time("quick") == 1000
    # After the clock reading, the extra read and second piece handling each
    # debit another second from our final remaining time.
    assert first["final_state"]["white_ms"] - second["final_state"]["white_ms"] == 2000


def test_operator_replay_positive_recovery_evidence(tmp_path: Path):
    evidence = run_simulated_replay(tmp_path, scenario="positive_recovery")
    assert evidence["data_type"] == "simulated"
    assert evidence["final_state"]["result"] is None
    assert len(evidence["final_state"]["moves"]) == 3


def test_operator_replay_physical_zero_evidence(tmp_path: Path):
    evidence = run_simulated_replay(tmp_path, scenario="physical_zero")
    assert evidence["data_type"] == "simulated"
    assert evidence["final_state"]["result"] == "0-1"
    assert evidence["final_state"]["reason"] == "flag"

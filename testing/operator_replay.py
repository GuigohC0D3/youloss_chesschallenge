"""Deterministic operator replay simulator with virtual monotonic clock and fake engine.

Produces simulated timing evidence for physical clock reading, opponent UCI entry,
piece movement, and clock press/played. All timing values are simulated.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import chess

from controller.book import OpeningBook
from controller.clock import GameClock
from controller.game import Game, STOP_GRACE_S
from controller.game_log import GameLog
from controller.state import GameState
from controller.tests.scripted import Script, fake_engine


class VirtualClock:
    """Deterministic monotonic clock for simulation."""

    def __init__(self, start_t: float = 1000.0) -> None:
        self.t = start_t

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


@dataclass
class ReplayDelays:
    """Simulated operator and opponent delay profile (seconds)."""
    clock_read_s: float = 1.0     # Time after the physical press, charged to us
    uci_entry_s: float = 1.2      # Time typing opponent UCI after press
    engine_search_s: float = 0.2  # Simulated search time charged to us
    piece_move_s: float = 1.5     # Time moving our physical piece after proposal
    clock_press_s: float = 0.8    # Time pressing physical clock and typing played
    opp_think_s: float = 3.0      # Opponent thinking time on board

    def __post_init__(self) -> None:
        if any(not math.isfinite(value) or value < 0 for value in asdict(self).values()):
            raise ValueError("replay delays must be finite and non-negative")


def run_simulated_replay(
    tmp_path: Path,
    scenario: str = "normal",
    delays: ReplayDelays | None = None,
    base_ms: int = 60_000,
    safety_margin_s: float = 2.0,
    clock_latency_s: float = 2.0,
) -> dict[str, Any]:
    """Execute a deterministic replay scenario and return simulated timing evidence."""
    delays = delays or ReplayDelays()
    vclock = VirtualClock()

    if scenario == "normal":
        script_commands = ["begin", "played", "press 00:58", "e7e5", "played"]
    elif scenario == "positive_recovery":
        script_commands = ["begin", "played", "press 00:02", "e7e5", "clock 00:05 00:56 nos", "played"]
    elif scenario == "physical_zero":
        script_commands = ["begin", "played", "press 00:02", "e7e5", "clock 00:00 00:56 nos"]
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    state = GameState(
        color="white",
        opponent="simulated_opponent",
        game=1,
        base_ms=base_ms,
        inc_ms=0,
        start_fen=chess.STARTING_FEN,
        white_ms=base_ms,
        black_ms=base_ms,
        log_path=str(tmp_path / "replay.log"),
    )
    engine = fake_engine("ok")
    engine.start()
    engine.handshake(timeout=5)
    log = GameLog(tmp_path / "replay.log")

    search_observations: list[dict[str, Any]] = []
    real_search = engine.search

    def spy_search(position: str, go: str, timeout: float, stop_grace: float = 1.0):
        fresh_ours = game.clock.remaining(game.us)
        search_observations.append({
            "timeout_ms": round(timeout * 1000),
            "stop_grace_ms": round(stop_grace * 1000),
            "reserve_ms": round(game.safety_margin_s * 1000),
            "reported_remaining_ms": fresh_ours,
            "budget_fits": (timeout + stop_grace + game.safety_margin_s) * 1000 <= fresh_ours + 1.0,
        })
        result = real_search(position, go, timeout, stop_grace=stop_grace)
        vclock.advance(delays.engine_search_s)
        return result

    engine.search = spy_search

    script = Script(script_commands)

    def advancing_input(prompt: str) -> str:
        cmd = script(prompt)
        if cmd == "begin":
            pass
        elif cmd == "played":
            vclock.advance(delays.piece_move_s)
            vclock.advance(delays.clock_press_s)
        elif cmd.startswith("press"):
            vclock.advance(delays.opp_think_s)
        elif cmd == "e7e5":
            # The opponent has pressed the physical clock; debit our side
            # for reading it and entering their move before requesting search.
            vclock.advance(delays.clock_read_s)
            vclock.advance(delays.uci_entry_s)
        return cmd

    game = Game(
        state=state,
        state_path=tmp_path / "replay.state.json",
        engine=engine,
        book=OpeningBook(None),
        log=log,
        clock=GameClock(base_ms, 0),
        input_fn=advancing_input,
        output_fn=lambda _: None,
        safety_margin_s=safety_margin_s,
        clock_latency_s=clock_latency_s,
    )
    game.clock._now = vclock  # type: ignore[attr-defined]

    try:
        outcome = game.run()
    finally:
        engine.quit()
        log.close()

    evidence: dict[str, Any] = {
        "data_type": "simulated",
        "disclaimer": "simulated values, not measured operator data",
        "scenario": scenario,
        "parameters": {
            "base_ms": base_ms,
            "safety_margin_s": safety_margin_s,
            "clock_latency_s": clock_latency_s,
            "delays_s": asdict(delays),
        },
        "search_observations": search_observations,
        "final_state": {
            "result": game.state.result,
            "reason": game.state.reason,
            "moves": list(game.state.moves),
            "white_ms": game.clock.remaining(chess.WHITE),
            "black_ms": game.clock.remaining(chess.BLACK),
        },
    }
    return evidence


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as tdir:
        res = run_simulated_replay(Path(tdir), scenario="normal")
        print(json.dumps(res, indent=2))

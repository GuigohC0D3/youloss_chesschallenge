#!/usr/bin/env python3
"""Automated Physical Board Operator Rehearsal Script.

Simulates a live tournament game through controller.main, exercising:
- Game initialization and engine handshake
- Opening book instantaneous lookup
- Physical clock press entry (`press <mm:ss>`)
- Move proposal (`go`) and confirmation (`played`)
- Physical clock resynchronization (`clock <ours> <adv>`)
- Game termination (`resign adv`)
- Game log and state persistence verification
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from controller.main import main
SCRIPTED_INPUTS = [
    "begin",            # Round starts, our clock starts, book proposes 1. g1f3
    "played",           # Confirm move played on physical board
    "press 24:55",      # Opponent pressed physical clock
    "e7e5",             # Opponent played 1... e5, engine proposes 2. f3e5
    "played",           # Confirm move played on physical board
    "clock 24:50 24:40",# Operator resyncs clocks with referee
    "resign adv",       # Opponent resigns on board
    "s",                # Confirm opponent resignation -> 1-0 WIN!
]

def input_mock(prompt: str = "") -> str:
    if SCRIPTED_INPUTS:
        cmd = SCRIPTED_INPUTS.pop(0)
        print(f"[REHEARSAL INPUT] {prompt}{cmd}")
        return cmd
    print(f"[REHEARSAL INPUT] {prompt}quit")
    return "quit"

def output_mock(msg: str):
    print(f"[REHEARSAL OUT] {msg}")

def run_rehearsal():
    print("=" * 80)
    print("STARTING PHYSICAL BOARD OPERATOR CLI SIMULATION REHEARSAL")
    print("=" * 80)
    
    argv = [
        "start",
        "--color", "white",
        "--opponent", "TournamentRehearsalOpponent",
        "--game", "2",
        "--tc", "1500+0",
        "--threads", "7",
        "--hash", "2048",
    ]
    
    rc = main(argv=argv, input_fn=input_mock, output_fn=output_mock)
    print("=" * 80)
    print(f"REHEARSAL COMPLETED WITH RETURN CODE: {rc}")
    print("=" * 80)
    return rc

if __name__ == "__main__":
    sys.exit(run_rehearsal())

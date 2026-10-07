# Youloss vs official Stockfish 19 loss-position reanalysis (2026-10-05)

**Status:** Completed forensic reanalysis note.

## Explicit caution

`go nodes` does not activate YoulossTM, this is one already-lost position, and it cannot justify a general strength claim or tuning change.

## Binary provenance and worktree note

- Candidate binary `bin/youloss`:
  - SHA-256: `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301` (matches tested SHA from the forensic report)
  - Modification time (mtime): October 3, 2026 (`2026-10-03 15:03`)
- Worktree state:
  - Current worktree time-manager parameters differ from HEAD (uncommitted modifications in `engine/src/youloss_tm.cpp`).
  - The provenance of `bin/youloss` relative to those uncommitted source edits is unverified.
  - A fresh build is required before evaluating those source edits.
  - Do not say or assume that the binary definitely contains any specific parameter values.
- Baseline binary `/tmp/youloss-benchmark/stockfish/stockfish-macos-universal`:
  - SHA-256: `8eed61129d1493c5d1f2fd9323f0c54c47ac49319911fbde18c6b9c87e8b13c5`
  - Verified official `official-stockfish/Stockfish` release artifact (`sf_19`, commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d`).

## Source PGN and FEN provenance

- Source PGN: `logs/sprt/tm_10+0.1_r5_s1791073990_20261003-213311.rEvMiR/match.pgn`
- Game: 10
- Result: `1-0` (White `sf` won; Black `tm` lost)
- Historical move: At ply 72 (fullmove 44, Black to move), Youloss played `Qe8` (UCI `e7e8`).
- Asserted FEN immediately prior to ply 72:
  `1Rb3k1/4qrp1/2r5/3p1P1Q/p2Bp1P1/2P4P/5RK1/8 b - - 2 44`
- Provenance recorded in both engine runs:
  `pgn_provenance: {uci: "e7e8", white: "sf", black: "tm", result: "1-0"}`

## Settings and execution harness

- Fixed search limit: `go nodes 20000000` (equal 20,000,000 nodes, no clock time supplied)
- UCI configuration:
  - `Threads=1`
  - `Hash=128` (128 MiB)
  - `MultiPV=3`
  - Fresh `ucinewgame` before position setup
  - Position: `position fen 1Rb3k1/4qrp1/2r5/3p1P1Q/p2Bp1P1/2P4P/5RK1/8 b - - 2 44`
- Engine-specific options:
  - Youloss: `YoulossTM=true` configured (inactive under `go nodes`)
  - Stockfish 19: `YoulossTM` option absent; standard UCI options only
- Runner: `/tmp/scratchpad/eng_run_safe.py`
  - Raw UCI subprocess communication with nonblocking `selectors` reads
  - Wall-clock budget: 75.0s search timeout + 5.0s `bestmove` grace
  - Clean child process handling via PID termination/kill
  - System telemetry polling at ~1s intervals (capped at 2s per probe, fail-closed on missing/malformed metrics)

## Hardware and safety telemetry

Both engine runs completed without timeout, engine errors, or resource aborts (`completed: true`, `timed_out: false`, `resource_abort: false`, `shutdown: quit`, `error: null`).

- Youloss run (`/tmp/scratchpad/youloss_result.json`):
  - Wall search time: 29.18s (total wall time: 30.00s)
  - Pre/in/post battery: 26.0% (stable across 28 samples)
  - Pre/in/post swap: 893.5 MiB (stable across 28 samples)
- Stockfish 19 run (`/tmp/scratchpad/stockfish_result.json`):
  - Wall search time: 23.34s (total wall time: 23.91s)
  - Pre/in/post battery: 26.0% (stable across 23 samples)
  - Pre/in/post swap: 893.5 MiB (stable across 23 samples)

## Engine comparison: Youloss vs Stockfish 19

### Bestmove and MultiPV comparison

| Engine | Bestmove | Historical Move | Nodes | Depth / Seldepth | Search Wall Time | NPS |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Youloss** | `e7d7` (`Qd7`) | `e7e8` (`Qe8`) | 20,000,583 | 24 / 38 | 29.18s (29,179 ms) | 685,444 |
| **Stockfish 19** | `e7d7` (`Qd7`) | `e7e8` (`Qe8`) | 20,000,583 | 24 / 38 | 23.34s (23,336 ms) | 857,069 |

Both engines agreed on `bestmove: e7d7` (`Qd7`). The game move `e7e8` was not preferred by either engine at fixed nodes.

### Principal variations and scores

#### Youloss (MultiPV=3)
- **PV1:** `score cp -390` | depth 24 | seldepth 38 | 20,000,583 nodes
  `e7d7 f5f6 g7f6 f2f5 f7h7 f5d5 d7e7 h5g6 h7g7 g6f5 e7f8 f5e4 g7e7 e4g6 e7g7 g6d3 g7f7 d5a5 f8d6 d3g6 g8f8 g6h6 f8e8 h6h8 f7f8 h8h5 e8d8 b8c8`
- **PV2:** `score cp -447` | depth 24 | seldepth 40 | 20,000,583 nodes
  `e4e3 f2e2 e7d8 f5f6 c6f6 d4f6 g7f6 h5g6 f7g7 g6d3 g7c7 d3e3 g8g7 b8b4 a4a3 b4a4 c8b7 g2g1 b7c6 a4a3 d5d4 e3d4`
- **PV3:** `score cp -507` | depth 24 | seldepth 28 | 20,000,583 nodes
  `e7d6 b8c8`

#### Stockfish 19 (MultiPV=3)
- **PV1:** `score cp -390` | depth 24 | seldepth 38 | 20,000,583 nodes
  `e7d7 f5f6 g7f6 f2f5 f7h7 f5d5 d7e7 h5g6 h7g7 g6f5 e7f8 f5e4 g7e7 e4g6 e7g7 g6d3 g7f7 d5a5 f8d6 d3g6 g8f8 g6h6 f8e8 h6h8 f7f8 h8h5 e8d8 b8c8`
- **PV2:** `score cp -447` | depth 24 | seldepth 40 | 20,000,583 nodes
  `e4e3 f2e2 e7d8 f5f6 c6f6 d4f6 g7f6 h5g6 f7g7 g6d3 g7c7 d3e3 g8g7 b8b4 a4a3 b4a4 c8b7 g2g1 b7c6 a4a3 d5d4 e3d4`
- **PV3:** `score cp -507` | depth 24 | seldepth 28 | 20,000,583 nodes
  `e7d6 b8c8`

### Score and search analysis

- **Score perspective:** Scores are UCI `score cp` from Black's perspective (Black to move). Negative values indicate that Black is at a disadvantage (`cp -390` corresponds to approximately White +3.90 pawns). No mate scores were reported.
- **Search tree agreement:** Both engines found identical PV lines, identical depths (24) and seldepths (38, 40, 28), and identical evaluation scores across all three MultiPV slots at 20,000,000 nodes.
- **Speed disparity:** At identical node counts, Youloss searched at 685,444 NPS (29.18s search wall time) versus Stockfish 19 at 857,069 NPS (23.34s search wall time).

## Limitations

- **No time-manager activation:** `go nodes` does not supply clock times (`wtime`, `btime`, `winc`, `binc`). In `engine/src/search.cpp`, YoulossTM is gated on clock time being provided. While `YoulossTM=true` was configured, it remained unactivated during this fixed-node search. This run constitutes a forensic move-search comparison at fixed nodes, not a test of time management behavior. Do not infer TM behavior from scores, PVs, or bestmove.
- **Single-position sample:** This forensic inspection addresses a single position from a single logged loss. It cannot justify any general claim regarding engine strength, rating differential, or parameter tuning.
- **Read-only forensic methodology:** The run was executed using external safe-harness tooling without altering repository files, rebuilding binaries, running competitive matches, staging, or committing.

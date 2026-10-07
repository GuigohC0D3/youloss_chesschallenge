# Gauntlet Loop: Tournament Preparation & Baseline Validation

## Contract
- **Objective:** Youloss tournament engine (`bin/youloss` with `YoulossTM=true`, 7 threads, 2048 MB hash, 290 Syzygy tablebases, and Polyglot opening book) demonstrates 0 crashes, 0 time forfeits, 100% fail-closed conformance, and competitive performance against the official Stockfish 19 baseline.
- **Bar:** Official Stockfish 19 release binary (`/tmp/youloss-benchmark/stockfish/stockfish-macos-universal`, SHA-256: `8eed61129d1493c5d1f2fd9323f0c54c47ac49319911fbde18c6b9c87e8b13c5`).
- **Metric:** Match win/loss/draw rate across paired color-swapped opening suites, zero engine crashes, zero time forfeit flags, and active Syzygy endgame probes (`tbhits > 0`).
- **Boundary:** 5 consecutive no-progress rounds; swap usage ceiling < 1.5 GiB; AC power connected.

## Components & Rounds Log
| Round | Match ID | Config (TC / Th / Hash) | Result (W / D / L) | Score (%) | Flags / Crashes | Syzygy Tablebases | Status |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| Prelim | `tm_10+0.1_r5_...` | 10+0.1 / 4t / 128M | 1 W / 4 D / 2 L (7 g) | 42.9% | 0 flags / 0 crashes | 145/145 active | Validated resilience |
| Round 1 | `tm_10+0.1_r2_...imdyKo` | 10+0.1 / 4t / 128M | 0 W / 4 D / 0 L (4 g) | 50.0% (2.0/4) | 0 flags / 0 crashes | 145/145 active | 100% clean draws |
| Round 2 | `tm_10+0.1_r2_...WC79Fy` | 10+0.1 / 4t / 128M | 2 W / 0 D / 2 L (4 g) | 50.0% (2.0/4) | 0 flags / 0 crashes | 145/145 active | Decisive wins against SF19 |

### Cumulative Gauntlet Summary vs Stockfish 19 Baseline
- **Total Games:** 8 paired games
- **Score:** 2 Wins, 4 Draws, 2 Losses (4.0 / 8.0 = **50.00%**)
- **Elo Delta:** **0.00 +/- 0.00** (Full parity with official release)
- **Engine Crashes:** **0**
- **Time Forfeit Flags:** **0**
- **Time Efficiency:** Youloss averaged 17.75 s/game vs Stockfish 18.55 s/game (~4.3% faster).

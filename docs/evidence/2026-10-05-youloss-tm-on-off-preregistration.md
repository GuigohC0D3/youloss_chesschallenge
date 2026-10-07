# Youloss time manager on versus off — 100-game screen

**Status:** Preregistered after the separate FallMax screen closed. No games in this study have started.

## Question

At `10+0.1`, does the custom Youloss time manager (`YoulossTM=true`) perform better than Stockfish's built-in time manager (`YoulossTM=false`) when both modes use the exact same current binary, NNUE, search code, options, openings, and host? This is an engine-only development screen. It is not full tournament-control evidence, a strength claim against official Stockfish, or neural-network training.

## Fixed design

- 50 paired rounds / 100 games; seed `2026100503`; same opening in both games of each pair, with colors swapped.
- Same binary on both sides: `bin/youloss`, SHA-256 `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301`; current source SHA-256 `b93c2f4557454c2b61ffbfee8decebc48d7ddae061df440567284c70d4600f1c`.
- Side A: `YoulossTM=true`. Side B: `YoulossTM=false` (Stockfish stock time manager). No `SF_ENGINE` override; the harness must verify matching binary hashes and apply only the time-manager option difference.
- `10+0.1`, Threads 1, Hash 128 MiB, Move Overhead 10 ms, concurrency 1, Syzygy off. Runner SHA-256 `38a7b822c711afd9435d8be91482e555c5b8e2d5414fd2c91de7e6db93baa6ab`; UHO book SHA-256 `7a7f6470615a69c6cf23d565417701d38732876f480af90d67b42abade35644a`.
- Integration smoke: one paired round, seed `2026100504`, excluded from the scored sample. Scored sample: 50 rounds, seed `2026100503`; wall-clock cap 7,200 seconds, watchdog hard cap 7,500 seconds. No rerun with these seeds or extension after seeing results.
- Exact scored command: `SF_ENGINE= SF_ENGINE_LABEL= SRAND=2026100503 THREADS=1 CONC=1 HASH_MB=128 MOVE_OVERHEAD_MS=10 TIME_CAP_S=7200 SYZYGY_PATH= bash testing/tm_match.sh 10+0.1 50`. Exact smoke command uses the same settings with seed `2026100504`, `TIME_CAP_S=600`, and one round.
- Run on AC only. Poll power, battery, and swap every 2 seconds; abort on loss of AC, battery at/below 20%, telemetry failure, or swap at/above 1,536 MiB (host swap is 2,048 MiB total). Preserve all match, PGN, metadata, profile, and watchdog logs.

## Analysis and decision rule

Report W/D/L, score by color, paired opening-cluster mean and 95% paired-*t* interval, elapsed time, time-use profile, and all incidents. Advance the custom manager to an independently preregistered validation only if its paired interval is wholly above 50% and the fail-closed checks pass. Prefer the stock manager for this binary if the interval is wholly below 50%. Otherwise the result is inconclusive; do not claim a strength gain or tune from this screen. No result-driven extension.

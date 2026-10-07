# YoulossTM strength experiment protocol — preregistration draft

**Status:** No new strength experiment has started under this protocol. The 240-game `60+0` overnight run with 1500 ms overhead is invalid for strength; the corrected four-game result was 2–2 and inconclusive. Archive every future failed, incomplete, and inconclusive trial.

## Fixed comparison

- **Same-binary A/B screening:** Compare the same committed engine binary with `YoulossTM=true` versus `YoulossTM=false`. Both sides use identical Threads, Hash, net, openings, and runner. The 8-thread/512-MiB setting is an unqualified hardware candidate; choose and record one profile before each study.
- **Official Stockfish 19 profile comparison:** When measuring against the official reference rather than an internal A/B disable, provide `SF_ENGINE` pointing to the official Stockfish 19 binary (built from pinned commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d` under matching compiler toolchain and NNUE net).
  - The external Stockfish baseline must never receive the unsupported `YoulossTM` option; shared standard UCI options (`Threads`, `Hash`, `Move Overhead`) are applied to both sides.
  - The harness records the immutable SHA-256 for both Youloss and baseline binaries, runner SHA-256, baseline label/options, book SHA, and seed in `meta.json`.
  - The screening analyzer strictly partitions results by both Youloss and baseline binary SHA-256, ensuring same-binary A/B trials and official Stockfish 19 comparisons are never pooled or conflated.
- Syzygy is **off by default** in `testing/tm_match.sh`. For a separately declared local study, set `SYZYGY_PATH` to a complete table directory; fastchess then sends the same `SyzygyPath` and `SyzygyProbeLimit=5` through `-each` to both engines. The run metadata records the path, WDL/DTZ file counts, probe limit, and table-set fingerprint. Set `SYZYGY_PATH=` to force it off. Do not use tablebases in the tournament profile until the organizer confirms they are allowed.
- Before a tablebase-enabled study, run `bash scripts/verify_assets.sh` and retain its result with the study artifacts. The fingerprint in each match's metadata identifies the table set declared by the asset manifest.
- Existing screening logs produced before this harness option was added are tablebase-free; do not mix them with tablebase-enabled comparisons.
- Use the pinned fastchess runner and manifest-verified UHO openings. Pair colors on the same opening. Save binary, runner, opening SHA-256, seed, exact command, PGN, raw log, timing profile, and exit status.
- Run one performance experiment at a time on an otherwise idle Mac. Avoid changing engine or settings mid-study. Keep development tests and builds outside the measurement window.
- The engine-only `Move Overhead` represents UCI and scheduling costs. It does not represent physical handling. Use preflight-approved values: 10 ms at `10+0`, 60 ms at `60+0`, and 150 ms at `180+0`, subject to a local latency measurement before a scored comparison. Apply the same value to both engines.
- Set an explicit `TIME_CAP_S` for fixed runs. For zero increment, the harness requires at least `rounds × 4 × base_seconds + 30` seconds. Keep `CONC=1` for full-thread comparisons. Declare rounds and wall cap before starting; do not extend a poor result after seeing the score.

## Study stages

1. **Integration smoke:** two paired-color games at `10+0`; require runner, checker, and timing profile to pass with no incidents. This verifies wiring only.
2. **Development screen:** up to two specific YoulossTM rule changes. Record the exact code diff and the mechanism expected to help. Use paired `10+0`, then `60+0`, then `180+0` only when prior wiring and time-use checks pass. Fix each stage's rounds, seed, and wall cap before running it.
3. **Independent validation:** choose a distinct opening segment/seed and do not use it for tuning. Report W/D/L, paired-score estimate, uncertainty, clock losses, time usage, and all stopped trials. A noninferiority result supports only its declared bound; it does not prove a gain.
4. **Tournament operation:** use confirmed event control with the controller and physical board. Those games qualify reliability and workflow, not Elo. The provisional interpretation is `1500+0` until the organizer answers.

Do not start an SPRT or claim an Elo improvement until its hypotheses, confidence bounds, game cap, and compute budget are written into a dated run specification. A checker pass confirms evidence integrity, not playing strength.

## Bounded screening sessions

- `testing/continuous_screening.sh` accepts an optional positive `MAX_BATCHES` (`0` means unlimited). A fixed-size experiment declares `MAX_BATCHES` and `ROUNDS_PER_BATCH` before starting; for example, `MAX_BATCHES=10` with `ROUNDS_PER_BATCH=5` is ten fully validated batches (100 games).
- At startup the supervisor logs all effective match settings and safety thresholds to the session log: TC, rounds, threads/concurrency/hash/overhead, per-batch cap, total deadline, pause, AC requirement, battery floor, swap used cap, and minimum free swap/memory/disk. Secrets are never logged.
- Bounded sessions fail closed: an invalid or failed batch aborts the supposedly fixed-size experiment instead of silently continuing. The completion/stop reason is logged.

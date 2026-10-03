# YoulossTM strength experiment protocol — preregistration draft

**Status:** No new strength experiment has started under this protocol. The 240-game `60+0` overnight run with 1500 ms overhead is invalid for strength; the corrected four-game result was 2–2 and inconclusive. Archive every future failed, incomplete, and inconclusive trial.

## Fixed comparison

- Compare the same committed engine binary with `YoulossTM=true` versus `YoulossTM=false`. Both sides use identical Threads, Hash, net, openings, and runner. The 8-thread/512-MiB setting is an unqualified hardware candidate; choose and record one profile before each study.
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

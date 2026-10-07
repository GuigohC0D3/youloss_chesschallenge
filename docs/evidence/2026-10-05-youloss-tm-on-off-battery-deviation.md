# YoulossTM on/off screen — battery-power deviation

## Amendment recorded before the first game

At 2026-10-05 19:30 UTC, the user explicitly authorized running the queued YoulossTM on/off study without AC power and asked to stop when battery becomes critical. This amends only the preregistration's power-source requirement; it does not rewrite the original preregistration or change the scored seed, openings, engine artifacts, settings, sample size, statistical rule, or stopping rules.

The original preregistration remains at `2026-10-05-youloss-tm-on-off-preregistration.md` (SHA-256 `f3340954e0df7b8b09e3b9ae08672ea1ae19396fed3b927cdfebd3012fa0cb2c`). Its AC-only condition is not met, so any result under this amendment is exploratory battery-power evidence and cannot qualify the engine for AC tournament operation.

## Fixed run and safety conditions

- Keep the original design: one excluded integration smoke (`2026100504`), then 50 paired rounds / 100 scored games (`2026100503`), `10+0.1`, Threads 1, Hash 128 MiB, Move Overhead 10 ms, concurrency 1, Syzygy off.
- Candidate binary SHA-256: `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301`; source SHA-256: `b93c2f4557454c2b61ffbfee8decebc48d7ddae061df440567284c70d4600f1c`.
- At authorization, the host reported Battery Power, 69% battery, and 869.5 MiB used swap (2,048 MiB total).
- Poll battery and swap every 2 seconds. Abort immediately at battery `<=20%`, swap `>=1536 MiB`, telemetry failure, invalid power-source telemetry, or the preregistered time cap. Do not restart or extend the sample after an abort.
- Preserve all smoke, match, PGN, metadata, timing-profile, process-watchdog, and resource JSONL logs. Record the exact termination reason if safety limits stop the sample.
- Because battery mode can affect sustained CPU performance and thermal behavior, report the power-source deviation prominently and do not pool this run with AC results or claim AC/tournament qualification.

## Execution log

- `2026-10-05T19:32:45Z`: battery/swap gate passed (`Battery Power`, 69%, 869.5 MiB swap). Sequence supervisor PID `30540` started the excluded two-game smoke.
- `2026-10-05T19:33:59Z`: smoke passed: Fastchess, match checker, timing profiler, and timeout checks all returned success; 2/2 games recorded. Run directory: `logs/sprt/tm_10+0.1_r1_s2026100504_20261005-163247.t8F7zk/`.
- `2026-10-05T19:33:59Z`: the 50-pair / 100-game scored sample started automatically after the smoke. Initial gate passed at Battery Power, 69%, 869.5 MiB swap. Fastchess PID `31248`; run directory: `logs/sprt/tm_10+0.1_r50_s2026100503_20261005-163401.7oNKSM/`; resource JSONL: `/tmp/scratchpad/youloss-tm_on_off-20261005T193359Z.jsonl`.
- Sequence log: `/tmp/scratchpad/youloss-tm-onoff-battery-sequence.log`. Watchdog polls every 2 seconds and aborts at the recorded battery, swap, telemetry, or time limits. No scored result is available yet.

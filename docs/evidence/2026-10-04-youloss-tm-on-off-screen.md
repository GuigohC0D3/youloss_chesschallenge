# Pre-registration: 100-game Youloss TM on vs off screening (2026-10-04)

**Status:** Aborted / Incomplete (2026-10-04).
This is exploratory match screening, not NNUE training, not tuning, and not proof of strength.

## Hypothesis & Purpose

- **Hypothesis:** Under the `10+0.1` time control, Youloss with its custom time manager enabled (`YoulossTM=true`, candidate FallMax=2.25) maintains stability, avoids time losses, and performs with search allocation parity relative to the same engine binary running Stockfish's stock time management (`YoulossTM=false`).
- **Scope:** Exploratory, bounded same-binary A/B screen isolating Youloss's custom time manager.
- **Rule:** 100 games (50 paired rounds) are screening only. Inconclusive results do not justify a tuning claim or unregistered extension. A poor intermediate score or inconclusive result is not a reason to tune parameters or extend the sample.

## Comparison

- Same binary on both sides: `bin/youloss` (candidate FallMax=2.25).
- Side A (Youloss): `YoulossTM=true` (default).
- Side B (Baseline): `YoulossTM=false` (restores Stockfish's stock time manager).
- No external `SF_ENGINE` is set (`SF_ENGINE=` empty), ensuring identical engine binary and build flags on both sides.

## Fixed design (do not extend after seeing results)

- Total: **100 paired games = 50 paired rounds** (2 games per round, colors paired on the same opening).
- Batching: **10 batches × 5 paired rounds per batch** (`ROUNDS_PER_BATCH=5`, `MAX_BATCHES=10`).
- Time control: `10+0.1`; Threads=1; Hash=128 MiB; Move Overhead=10 ms; concurrency=1.
- Per-batch wall cap: `TIME_CAP_S=600`. Pause between batches: `PAUSE_S=45`.
- Total deadline: `DEADLINE_HOURS=12` (`DEADLINE_S=43200`), in addition to the per-batch cap.
- Seeds: `SRAND` left unset so each batch draws a fresh `date +%s` seed; every seed is recorded in that batch's `meta.json`. No opening segment/seed is reused for tuning.
- Runner: pinned fastchess `v1.8.2-alpha` commit `f618e34540f94f4719ad3817950618dabe441318`, verified against `tools/fastchess.build.json` sidecar before each batch.
- Book: `assets/openings/UHO_Lichess_4852_v1.epd`, manifest-verified, random order, colors paired (no `-noswap`).
- Screening directory: `logs/screening/tm-on-off-fallmax225-20261004`. Match artifacts under `logs/sprt`.
- Preregistered launch command:
  ```bash
  MAX_BATCHES=10 ROUNDS_PER_BATCH=5 TC=10+0.1 THREADS=1 CONC=1 HASH_MB=128 MOVE_OVERHEAD_MS=10 TIME_CAP_S=600 PAUSE_S=45 REQUIRE_AC=0 BATTERY_MIN=20 MAX_SWAP_USED_MB=1536 MIN_FREE_SWAP_MB=512 MIN_FREE_MEM_PCT=10 SCREENING_DIR=logs/screening/tm-on-off-fallmax225-20261004 SF_ENGINE= bash testing/continuous_screening.sh start
  ```
- The supervisor stops after ten fully validated batches and fails closed on any invalid/failed batch.

## Hashes recorded from current checkout (2026-10-04)

- `bin/youloss`: `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301` (tested FallMax=2.25 candidate)
- `tools/fastchess`: `38a7b822c711afd9435d8be91482e555c5b8e2d5414fd2c91de7e6db93baa6ab` (tag `v1.8.2-alpha`, commit `f618e34540f94f4719ad3817950618dabe441318`, matches `tools/fastchess.build.json`)
- `assets/openings/UHO_Lichess_4852_v1.epd`: `7a7f6470615a69c6cf23d565417701d38732876f480af90d67b42abade35644a`
- Repo HEAD: `05f03f6e9c0aa26ad5b521e09f11a97cb585bbdd`

## Host limits and safety adaptation

- User authorized battery operation with a stop at 20% battery or 20 GB swap used.
- Host swap total is 2,048 MiB, so a 20 GB threshold could never trigger.
- Stricter safe cap applied: `MAX_SWAP_USED_MB=1536` and `MIN_FREE_SWAP_MB=512`.
- Battery minimum: `BATTERY_MIN=20`, `REQUIRE_AC=0`.
- System memory & disk: `MIN_FREE_MEM_PCT=10`, `MIN_DISK_MB=500`.
- Concurrency and threads: `THREADS=1`, `CONC=1`, `HASH_MB=128`.
- Safety telemetry is polled before and during matches; any failure aborts cleanly and fails closed.

## Outcome Measure

- Paired game score (+/=/-), win percentage, and paired score estimate with 95% confidence interval.
- Zero clock losses / time forfeits.
- Validation that all 10 batches complete with `exit_fastchess=0`, `exit_checker=0`, `exit_time_profile=0`, `exit_tee=0`.

## Verified Outcome

- **Execution summary:** Bounded supervisor session in `logs/screening/tm-on-off-fallmax225-20261004` aborted at 9/10 validated batches (90 games) after batch 10 failed validation and was rejected.
- **Nine-batch validated score (`scoreboard.json`):** 90 games; 22 YoulossTM (`tm`) wins, 25 TM-off (`sf`) wins, 43 draws, 0 incidents. Descriptive paired score: (22 + 43/2) / 90 = 48.33%. The sample is incomplete and exploratory; this does not warrant any strength or tuning conclusion. In accordance with the pre-registration protocol, no unregistered extension was made. The scoreboard excludes the rejected tenth batch.
- **Batch 10 rejection & failure cause:**
  - Artifacts: `logs/sprt/tm_10+0.1_r5_s1791153659_20261004-194101.dT8u02/match.log`, `match.pgn`, `meta.json`.
  - In batch 10 game 1, the TM-off `sf` side returned `Kh8` after 388.477s, losing on time by 382441ms. The run checker rejected batch 10 and the supervisor aborted cleanly. The run and PGN are preserved, but excluded from valid scoring.
  - Causal diagnosis: Independent OS log from `pmset -g log` confirms host clamshell sleep: `2026-10-04 19:41:13 -0300 Sleep Entering Sleep state due to 'Clamshell Sleep' ... Using Batt (Charge:59%) 388 secs`, waking at `19:47:41` upon lid-open/user activity. The 388-second sleep duration matches the 388.477s move delay. Although the supervisor ran under `caffeinate -s`, it was configured with `REQUIRE_AC=0` for user-authorized battery screening, allowing the Mac to sleep when the lid closed. This is an OS clamshell sleep event, not an engine search bug.
- **Host telemetry at abort:** Battery 58%, swap used 909.5 MiB / 2048 MiB total (1138.5 MiB free swap). No engine, match, or supervisor process remained running. As noted under host limits, the requested 20 GB swap threshold was impossible on a 2 GiB host; the 1536 MiB cap / 512 MiB free floor was used instead.
- **Next attempt gate:** Any future execution requires AC power (`REQUIRE_AC=1` or connected charger) and keeping the Mac lid open. Do not disable or bypass the safety gate.

# Pre-registration: 100-game Youloss vs official Stockfish development release screening (2026-10-05)

**Status:** ABORTED / INCOMPLETE (2026-10-05). Supervisor stopped after batch 5 safety event because free swap reached 504.5 MiB (<512 MiB floor; used swap then 1543.5 MiB >1536 cap). Verified no engine/screening processes remain.
This was exploratory match screening, not NNUE training, not tuning, and not proof of state-of-the-art strength. Preregistered 100-game study did not finish and supports no strength decision. No restart or extension, no code changes, no commit.

## Question and Exploratory Scope

At `10+0.1`, how does the current candidate Youloss engine (`YoulossTM=true`) perform against the official staged Stockfish development release (`stockfish-dev-20260930-49ea5ded`)?
This follows up on the 23W/54D/23L YoulossTM on/off ablation. That ablation compared the time manager on the same binary; this screen compares complete release engines and does not isolate the time manager or neural net.
This is an exploratory research screen on a local host. It is not full tournament-control evidence, an official strength claim against Stockfish, or an NNUE training run. Do not claim state-of-the-art from one screen.

## Pre-run Artifact Identities and Hashes

- **Repository:** `/Users/seunome/Code/youloss_chesschallenge`, branch `victor`, HEAD commit `05f03f6e9c0aa26ad5b521e09f11a97cb585bbdd`. Shared dirty worktree preserved; no commit or push.
- **Candidate binary:** `bin/youloss`
  - SHA-256: `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301`
  - UCI options: `YoulossTM=true`
- **Comparator baseline binary:** `/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/stockfish-macos-universal`
  - Official release tag: `stockfish-dev-20260930-49ea5ded`
  - Source commit: `49ea5ded38315cff8e67f4a677a9e7811612fbf6`
  - SHA-256: `adef0f3e2c97ef51e596a6a590d83b201221ad03a283d54fe79eb7edc0a80fd0`
  - UCI label: `stockfish-dev-20260930`
  - Provenance: official Stockfish development release archive fetched and verified, universal binary (x86_64 + arm64). Re-verified immediately before launch; fail closed on mismatch.
- **Pinned fastchess runner:** `tools/fastchess`
  - Sidecar: `tools/fastchess.build.json`
  - Tag: `v1.8.2-alpha`
  - Commit: `f618e34540f94f4719ad3817950618dabe441318`
  - SHA-256: `38a7b822c711afd9435d8be91482e555c5b8e2d5414fd2c91de7e6db93baa6ab` (matches sidecar and binary exactly)
- **Opening book:** `assets/openings/UHO_Lichess_4852_v1.epd`
  - SHA-256: `7a7f6470615a69c6cf23d565417701d38732876f480af90d67b42abade35644a` (verified in `assets/MANIFEST`)
  - Order: random order, paired openings without `-noswap`.
- **Runner scripts:**
  - `testing/tm_match.sh` SHA-256: `cef617162197810f6f6bbd254a5bc45823fe0071392c159f17e14e8b3b771f73`
  - `testing/continuous_screening.sh` SHA-256: `42ece277da918cd35f830dc99141449daf8453624314a0e63517c9601bca2b1c`
- **Competing processes:** None. Verified before launch that no competing `fastchess`, `stockfish`, or `youloss` instances are running.

## Fixed Experimental Design (No Extension)

- **Pairing:** 100 scored games = 50 paired rounds (2 games per round, same opening with colors reversed).
- **Batching:** 10 batches × 5 paired rounds per batch (`ROUNDS_PER_BATCH=5`, `MAX_BATCHES=10`).
- **Integration smoke:** One separate, excluded two-game smoke round (1 batch × 1 paired round = 2 games) in an isolated directory (`smoke-sfdev-*`) before starting scored games.
- **Time control:** `10+0.1` (10 seconds base + 0.1 second increment).
- **Engine settings:** Threads = 1, Hash = 128 MiB, Move Overhead = 10 ms, concurrency = 1 (one game at a time).
- **Syzygy:** Disabled (`SYZYGY_PATH=""`).
- **Seeds:** Fresh time-derived seeds (`SRAND` left unset); every batch records its exact seed in `meta.json`.
- **Protocol:** No stopping early based on score, no same-seed replacement, no extending after completion or abort.
- **Directories:** Unique directories under `logs/screening/` (`smoke-sfdev-*` and `sfdev-100game-*`). Match outputs remain isolated in `logs/sprt/`.

## Host Safeguards and Telemetry Thresholds

- **Power policy:** Authorized battery-powered execution (`REQUIRE_AC=0`).
- **Battery floor:** Stop fail-closed if battery drops to or below 20% (`BATTERY_MIN=20`).
- **Swap ceiling:** Total host swap is 2,048 MiB. Strict safety ceiling enforced: maximum 1,536 MiB used (`MAX_SWAP_USED_MB=1536`) and minimum 512 MiB free (`MIN_FREE_SWAP_MB=512`).
- **Memory floor:** Minimum 10% free system memory (`MIN_FREE_MEM_PCT=10`).
- **Disk floor:** Minimum 500 MB free disk space (`MIN_DISK_MB=500`).
- **Polling:** Continuous screening supervisor polls telemetry every 2 seconds and fails closed on unreadable or violating metrics.
- **Process buffer:** Hard wall-clock run deadline `DEADLINE_S=7200` (2 hours), per-batch wall timeout `TIME_CAP_S=600` (10 minutes), inter-batch pause `PAUSE_S=45`.
- **System load:** No concurrent benchmarks, builds, or training.

## Exact Commands

### 1. Integration Smoke Command (Excluded 2-game smoke)
```bash
SCREENING_DIR=/Users/seunome/Code/youloss_chesschallenge/logs/screening/smoke-sfdev-$(date +%Y%m%d%H%M%S) \
MAX_BATCHES=1 \
ROUNDS_PER_BATCH=1 \
TC=10+0.1 \
THREADS=1 \
CONC=1 \
HASH_MB=128 \
MOVE_OVERHEAD_MS=10 \
TIME_CAP_S=600 \
PAUSE_S=45 \
REQUIRE_AC=0 \
BATTERY_MIN=20 \
MAX_SWAP_USED_MB=1536 \
MIN_FREE_SWAP_MB=512 \
MIN_FREE_MEM_PCT=10 \
MIN_DISK_MB=500 \
SYZYGY_PATH= \
SF_ENGINE=/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/stockfish-macos-universal \
SF_ENGINE_LABEL=stockfish-dev-20260930 \
bash testing/continuous_screening.sh start
```

### 2. Scored 100-Game Command (Detached supervisor)
```bash
SCREENING_DIR=/Users/seunome/Code/youloss_chesschallenge/logs/screening/sfdev-100game-$(date +%Y%m%d%H%M%S) \
MAX_BATCHES=10 \
ROUNDS_PER_BATCH=5 \
TC=10+0.1 \
THREADS=1 \
CONC=1 \
HASH_MB=128 \
MOVE_OVERHEAD_MS=10 \
TIME_CAP_S=600 \
DEADLINE_S=7200 \
PAUSE_S=45 \
REQUIRE_AC=0 \
BATTERY_MIN=20 \
MAX_SWAP_USED_MB=1536 \
MIN_FREE_SWAP_MB=512 \
MIN_FREE_MEM_PCT=10 \
MIN_DISK_MB=500 \
SYZYGY_PATH= \
SF_ENGINE=/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/stockfish-macos-universal \
SF_ENGINE_LABEL=stockfish-dev-20260930 \
nohup bash testing/continuous_screening.sh start </dev/null >>"$SCREENING_DIR/continuous.log" 2>&1 &
```

## Statistical Decision Rule

- Evaluation is based on paired-opening clusters (50 pairs of color-swapped games on identical openings).
- Report Wins / Draws / Losses, total points, and score percentage.
- Calculate paired-cluster mean and Student-t 95% confidence interval on paired opening scores.
- **Inconclusive:** If the 95% confidence interval contains 50.0%, the screen is inconclusive and demonstrates neither superiority nor inferiority.
- **Superiority:** Candidate Youloss is considered superior only if the 95% confidence interval is strictly above 50.0% and all harness fail-closed checks pass.
- **Inferiority:** Candidate Youloss is considered inferior if the 95% confidence interval is strictly below 50.0%.
- **No tuning or extension:** Do not tune parameters, modify source, or extend the game count based on results.

## Excluded Integration Smoke Run (2026-10-05)

- **Execution:** 1 batch × 1 paired round (2 games) via `testing/continuous_screening.sh`.
- **Smoke directory:** `/Users/seunome/Code/youloss_chesschallenge/logs/screening/smoke-sfdev-20261005_200426`
- **Match rundir:** `/Users/seunome/Code/youloss_chesschallenge/logs/sprt/tm_10+0.1_r1_s1791241467_20261005-200428.VfWbTF`
- **Seed:** `1791241467`
- **Validation:** All exit codes clean (`exit_fastchess=0`, `exit_checker=0`, `exit_time_profile=0`, `exit_tee=0`, `timeout=0`).
- **Telemetry at start:** Battery 46%, memory free 47%, swap used 853.5 MiB / free 1194.5 MiB, disk free 29826 MB, thermal nominal.
- **Result:** 1 win (Youloss), 0 losses, 1 draw (1.5 / 2.0). Excluded from scored sample per protocol.

## Scored 100-Game Session (ABORTED / INCOMPLETE)

- **Launch time:** 2026-10-05 20:06:24 (-03:00)
- **Supervisor PID:** `6426` (detached with `nohup`)
- **Screening directory:** `/Users/seunome/Code/youloss_chesschallenge/logs/screening/sfdev-100game-20261005_200624`
- **Supervisor log:** `/Users/seunome/Code/youloss_chesschallenge/logs/screening/sfdev-100game-20261005_200624/continuous.log`
- **Scoreboard:** `/Users/seunome/Code/youloss_chesschallenge/logs/screening/sfdev-100game-20261005_200624/scoreboard.json`
- **Initial telemetry:** Battery 46% (discharging), memory free 50%, swap used 853.5 MiB, swap free 1194.5 MiB, disk free 29833 MB, thermal nominal.
- **Safety event & abort cause:** Supervisor stopped after batch 5 safety event because free swap reached 504.5 MiB (<512 MiB floor; used swap then 1543.5 MiB >1536 cap).
- **Process verification:** Verified no engine or screening processes remain.
- **Closeout telemetry:** Battery 36%, swap 1487.5 MiB used / 560.5 MiB free.
- **Supervisor-validated scoreboard:** 4 batches completed (40 games: 10W / 23D / 7L, 53.75%).
- **Batch 5 unpooled raw match:**
  - Raw match rundir: `logs/sprt/tm_10+0.1_r5_s1791243246_20261005-203408.FGO5hB`
  - Completed 10 games with fastchess/checker/time-profile/tee checks all exiting 0.
  - Outer supervisor marked the batch aborted due to the host swap safety event.
  - Result: 2W / 5D / 3L. Reported separately, not pooled as completion.
- **Raw games total:** 50 raw games exist across batches 1–5.
- **Study conclusion:** The preregistered 100-game study did not finish and supports no strength decision.
- **Protocol constraints:** No restart, no extension, no code changes, no commit.


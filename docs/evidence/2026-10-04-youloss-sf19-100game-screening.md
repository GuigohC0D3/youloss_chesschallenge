# Pre-registration: 100-game Youloss vs official Stockfish 19 screening (2026-10-04)

**Status:** Completed and closed (2026-10-04). All 10 batches (100 games) completed and validated.
This is exploratory match screening, not NNUE training and not proof of strength.

## Comparison

- Youloss (`bin/youloss`, `YoulossTM=true`) versus the local Stockfish 19
  baseline via `SF_ENGINE` (`YoulossTM` is never sent to the
  external baseline; only standard UCI options are applied to both sides).
- Baseline binary: `/tmp/youloss-benchmark/stockfish/stockfish-macos-universal`,
  SHA-256 `8eed61129d1493c5d1f2fd9323f0c54c47ac49319911fbde18c6b9c87e8b13c5`,
  UCI identity `id name Stockfish 19` (Stockfish developers), metadata label
  `stockfish-19` (as in existing `10+0.1` batch metadata). The exact binary
  hash pins this exploratory session.
- Provenance (verified): this binary is the binary extracted from the verified
  official `official-stockfish/Stockfish` release tag `sf_19` asset
  `stockfish-macos-universal.tar.gz` (archive SHA-256
  `a1f0e3bcc5a6927a11fe6fc8e54a779754645f3c2bae2cf13420fd1957adaa77`).
  GitHub resolves `sf_19` to source commit
  `edb0d9db6731067ec50ce619ff372b463bc4dd5d`. The extracted binary SHA-256
  matches this `SF_ENGINE` path exactly. This verifies release-artifact
  identity/provenance; it was not locally rebuilt from source. The
  `edb0d9db6731067ec50ce619ff372b463bc4dd5d` (`sf_19`) reference in
  `engine/ORIGIN.md` describes the Youloss fork base only.
- Same-binary A/B trials and official Stockfish 19 comparisons must never be
  pooled or conflated; results are partitioned by both binary SHA-256 values.

## Fixed design (do not extend after seeing results)

- Total: **100 paired games = 50 paired rounds** (2 games per round, colors
  paired on the same opening).
- Batching: **10 batches × 5 paired rounds per batch** (`ROUNDS_PER_BATCH=5`,
  `MAX_BATCHES=10`).
- Time control: `10+0.1`; Threads=1; Hash=128 MiB; Move Overhead=10 ms;
  concurrency 1.
- Per-batch wall cap: `TIME_CAP_S=600`. Pause between batches: `PAUSE_S=45`.
- Total deadline: `DEADLINE_HOURS=12` (`DEADLINE_S=43200`), in addition to the
  per-batch cap.
- Seeds: `SRAND` left unset so each batch draws a fresh `date +%s` seed;
  every seed is recorded in that batch's `meta.json`. No opening
  segment/seed is reused for tuning under this spec.
- Runner: pinned fastchess `v1.8.2-alpha` commit
  `f618e34540f94f4719ad3817950618dabe441318`, verified against
  `tools/fastchess.build.json` sidecar before each batch.
- Book: `assets/openings/UHO_Lichess_4852_v1.epd`, manifest-verified, random
  order, colors paired (no `-noswap`).
- Preregistered launch command:
  `MAX_BATCHES=10 ROUNDS_PER_BATCH=5 TC=10+0.1 THREADS=1 CONC=1 HASH_MB=128
  MOVE_OVERHEAD_MS=10 TIME_CAP_S=600 PAUSE_S=45 REQUIRE_AC=0 BATTERY_MIN=20
  MAX_SWAP_USED_MB=1536 MIN_FREE_SWAP_MB=512 MIN_FREE_MEM_PCT=10
  MIN_DISK_MB=500 SF_ENGINE=/tmp/youloss-benchmark/stockfish/stockfish-macos-universal
  SF_ENGINE_LABEL=stockfish-19
  bash testing/continuous_screening.sh start`
- The supervisor stops after ten fully validated batches and fails closed on
  any invalid/failed batch; the completion/stop reason is logged. A poor
  intermediate score is not a reason to tune parameters or extend the sample.
  This screens search allocation only.

## Hashes recorded from the current checkout (2026-10-04)

- `bin/youloss`: `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301`
- `tools/fastchess`: `38a7b822c711afd9435d8be91482e555c5b8e2d5414fd2c91de7e6db93baa6ab`
  (tag `v1.8.2-alpha`, commit `f618e34540f94f4719ad3817950618dabe441318`,
  matches `tools/fastchess.build.json`)
- `assets/openings/UHO_Lichess_4852_v1.epd`: `7a7f6470615a69c6cf23d565417701d38732876f480af90d67b42abade35644a`
- Local Stockfish 19 baseline binary (`SF_ENGINE`):
  `/tmp/youloss-benchmark/stockfish/stockfish-macos-universal`,
  SHA-256 `8eed61129d1493c5d1f2fd9323f0c54c47ac49319911fbde18c6b9c87e8b13c5`,
  label `stockfish-19`. Release-artifact provenance is verified: official
  `official-stockfish/Stockfish` tag `sf_19` asset
  `stockfish-macos-universal.tar.gz` (archive SHA-256
  `a1f0e3bcc5a6927a11fe6fc8e54a779754645f3c2bae2cf13420fd1957adaa77`,
  tag resolves to source commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d`);
  extracted binary hash matches exactly; it was not locally rebuilt from
  source. The file lives outside the
  repository and may be temporary: re-verify presence and SHA-256 immediately
  before the run and fail closed on any mismatch; each batch `meta.json`
  records the baseline path, hash, and label at run time.
- Repo HEAD at specification time: `05f03f6e9c0aa26ad5b521e09f11a97cb585bbdd`.

## Host limits and safety adaptation

- Host observed now: battery-powered, 100%; total swap 2,048 MiB, used
  989.5 MiB, free 1,058.5 MiB.
- The user authorized stopping at 20% battery or 20 GB swap used.
- Adaptation: 20 GB swap used is impossible on this 2-GiB swap configuration
  (it could never trigger), so this run uses a strictly more protective
  envelope: maximum 1,536 MiB swap used (`MAX_SWAP_USED_MB=1536`) and minimum
  512 MiB free (`MIN_FREE_SWAP_MB=512`). This fails earlier, not later, than
  the authorized limit and preserves headroom on this host.
- Battery floor: `BATTERY_MIN=20`. Telemetry must be readable; any unreadable
  power/thermal/memory/swap/disk telemetry stops the session fail-closed.
- `REQUIRE_AC=0` applies only to this user-authorized, low-load run
  (`10+0.1`, Threads=1, concurrency 1). All thermal, memory, disk, battery,
  and swap checks remain enforced.

## Acceptance for this screening session

- Ten fully validated batches with `exit_fastchess=0`, `exit_checker=0`,
  `exit_time_profile=0`, `exit_tee=0`, no timeout, and `match.log` totals
  matching `meta.json` (`completed_games == expected_games == 10` per batch).
- Any rejected batch aborts the fixed-size experiment; it is archived as an
  incident and the session stops instead of continuing silently.
- Report W/D/L, paired-score estimate with uncertainty, clock losses, time
  usage, and every stopped trial. An inconclusive or noninferiority result
  supports only its declared bound.

## Results and session closeout (2026-10-04)

- **Execution:** Session `sf19-100game-20261004T180342Z` completed 10 bounded batches (100 games total, 50 opening/color pairs). All 10 batches fully validated (`exit_fastchess=0`, `exit_checker=0`, `exit_time_profile=0`, `exit_tee=0`, `timeout=0`).
- **Score:** 18 wins, 26 losses, 56 draws; points: 46.0 / 100 (**46.0%** score).
- **Paired-cluster analysis:** Across the 50 same-opening color-swapped pairs:
  - Pair-cluster mean: **46.00%**
  - Paired *t* 95% confidence interval: **40.95% – 51.05%**
- **Operational telemetry & incidents:** Zero incidents recorded (`incidents: []`), zero time flags, zero crashes.
- **Match parameters:** TC `10+0.1`, Threads=1, Hash=128 MiB, Move Overhead=10 ms, concurrency=1 (one match at a time).
- **Host telemetry:** Host remained battery-powered; battery was 97% at launch and 87% at completion. Swap usage was 973.5 MiB used / 2,048 MiB total at both launch and completion checks. No macOS thermal or performance warning was recorded.
- **Session artifacts:** Run logs are preserved in ignored `logs/sprt/tm_10+0.1_*`. Session outputs and regenerated partitioned diagnostics are recorded in `logs/screening/sf19-100game-20261004T180342Z/` (`scoreboard.json`, `diagnostics.json`, `tuning_insights.md`, `continuous.log`, `analyzer_last.log`).
- **Conclusions:**
  - This is a `10+0.1` exploratory screen against the verified official Stockfish 19 release-artifact binary (`sf_19`; extracted binary SHA-256 `8eed61129d1493c5d1f2fd9323f0c54c47ac49319911fbde18c6b9c87e8b13c5`); it was not locally rebuilt from source.
  - The score interval includes 50% (paired *t* 95% interval 40.95%–51.05%), so it establishes neither superiority nor inferiority.
  - This experiment does not isolate the effect of `FallMax=2.25`.
  - Next steps: Freeze the tested engine for now. The next useful experiment is a preregistered paired A/B comparing otherwise identical `FallMax 2.0` and `FallMax 2.25` builds on this host with fixed options/openings and disjoint seeds. Do not start another match or change engine parameters in this task.

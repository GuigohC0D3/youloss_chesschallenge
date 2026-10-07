# Project Handoff — Youloss Chess Challenge → M5 machine (2026-10-07)

Status at handoff: **nothing is running** (user cancelled the battery screen to protect the
dev Mac), branch `sprint1-sfdev-adopt` ready to push, all gates green. This document is the
single entry point: what exists, what was happening, and exactly what to do next.

## 1. TL;DR

- The Stockfish-dev brain port is **done, built, and gated**: `bin/youloss_devport` =
  Stockfish `dev-20260930-49ea5ded` sources + all 6 YoulossTM hooks; bench **1,714,434**
  (byte-for-byte equal to the official dev prebuilt). Frozen tournament candidate
  `bin/youloss` is untouched (bench 2,497,913).
- The preregistered strength batteries (S2 → S1 → S3, 400 games each) are **written and
  locked** in `docs/evidence/2026-10-06-devbrain-preregistration.md`, but **0 games are
  counted yet** — every attempted batch was rejected by environment safeguards (fail-closed
  worked as designed).
- Next concrete action on the M5: build/verify (Section 5), then launch S2 on AC power
  (Section 6) and let it run in 12-hour sessions.

## 2. What was built (chronological)

### Pre-port work (branch `victor`, already pushed)
- **Controller / physical tournament**: incident sidecars, stderr tails, emergency-fallback
  move reuse with FEN+legality validation, clock-replay simulator
  (`testing/operator_replay.py`).
- **Fail-closed match harness**: `testing/tm_match.sh` (numeric base+inc parsing, 10%
  budget-overhead policy, wall-cap checks, pinned fastchess sidecar, Syzygy wiring,
  meta.json with binary/book/runner SHA-256) + 366 lines of fail-closed tests.
- **Continuous screening subsystem**: `testing/continuous_screening.sh` (AC/battery/swap/
  disk/thermal telemetry gates, bounded `MAX_BATCHES` sessions, validated PID/lock ownership,
  per-batch acceptance rules) + `testing/analyze_screening.py` (paired-opening scoring,
  SHA-partitioned analysis) + 1,386-line test suite.
- **YoulossTM tuning**: `HorizonOpening` 45→32, `StabilityMin` 0.55→0.70, `FallMax`
  1.75→2.0 with unit + pytest updates.
- **Offline release tooling**: `build_offline_release.py` / `verify_offline_release.py`,
  launcher preflight, asset manifest (290 Syzygy files verified).
- **Study evidence**: sf19 screening partitions (50.00% parity over 470 games), TM on/off
  screens, FallMax 2.25-vs-2.0 (inconclusive, keep 2.25 experimental), loss-position
  audits, M4 thermal/thread profile, 10M-word research gauntlet corpus.

### This sprint (`sprint1-sfdev-adopt`, base `05f03f6`)
- **Spec + plan + preregistration written before any counted game**
  (`docs/superpowers/specs/2026-10-06-state-of-the-art-design.md`,
  `docs/superpowers/plans/2026-10-06-state-of-the-art-devbrain-port.md`).
- **39-file brain port**: all Stockfish-dev-20260930 sources copied into `engine/src/`
  (`diff -rq` clean vs upstream tree), with the 6 YoulossTM hooks re-wired:
  1. `engine.cpp` — `YoulossTM` UCI option (default true),
  2. `search.h` — `youlossTM` flag on the search manager,
  3. `timeman.h` — `set_bounds()` for the custom budget,
  4. `search.cpp` — budget block after `tm.init()` (per-position `Youloss::budget`),
  5. `search.cpp` — per-iteration target via `Youloss::iteration_time`,
  6. `Makefile` — `youloss_tm.{h,cpp}` back in SRCS/HEADERS.
- **Build**: `scripts/build_engine.sh` gained `ENGINE_OUT`; `ENGINE_OUT=youloss_devport`
  produces `bin/youloss_devport` (SHA-256
  `5de10e10a18d03f0ef788473b1b89b5fba7928ce7670b77245b3bd4e96d4d518`, bench 1714434,
  id `Stockfish dev-20261003-m-05f03f6e`).
- **Harness ENGINE override**: `testing/tm_match.sh` line ~177 honors `ENGINE=` so
  screening can run `youloss_devport` vs frozen `youloss` without touching either binary.
- **Kill-path bug fixed** (root-caused with an isolated repro): bash `exec`-optimizes the
  final command of `bash -c`, dropping `token=` from the child argv, so
  `terminate_child_tree` refused to signal and SAFETY_STOP left an orphan fastchess
  running. Fix: ancestry fallback (`is_descendant_of` + `is_verified_owned_child`) —
  PID-reuse-safe because an unrelated `tm_match.sh` can never be a descendant of the
  supervisor. Regression test:
  `test_terminate_kills_child_when_exec_drops_token_from_argv`; the wrong-token refusal
  and unrelated-PID security pins still pass.
- **Gates at handoff**: `.venv/bin/python -m pytest -q` → **335 passed**;
  `bash scripts/test_engine_tm.sh` → `OK: youloss_tm`; `sha256sum -c` frozen binary → OK.

## 3. What was being run when cancelled

S2 (devport vs frozen, `TC=1500+0`, 7 threads / 2048 MiB / 1500 ms overhead, balanced GM
book, Syzygy on) under `testing/continuous_screening.sh`, battery mode (Amendment #1 of the
preregistration), launched 2026-10-07 12:20. User cancelled ~14:00 to spare the Mac
(battery was at 60%). `stop` completed cleanly through the fixed kill path.

**Screening history — every batch rejected, zero counted games:**
| batch | window | outcome |
|---|---|---|
| AC-loss attempt | 10-06 19:43–20:24 | environment-rejected: AC lost, clean SAFETY_STOP |
| overnight battery | 10-06 23:14–10-07 02:04 | environment-rejected: lid closed 00:03 → `Clamshell Sleep` → 3 fake time-forfeits (`tm_match` correctly exited 1) |
| midday battery | 10-07 12:20–~14:00 | manually cancelled by user |

Scoreboard `logs/screening/devbrain-s2-20261006/scoreboard.json`: 0 validated batches,
2 failed, 0 counted games. The AC auto-relaunch watcher was killed at handoff.

**Engine was exonerated**: at `5+0.1` the same pair went 4/4 `Termination=normal`, and UCI
clock probes are sane/symmetric (devport TM-on 0.62 s vs frozen 0.57 s at a 30 s clock).
Note: with `Move Overhead=1500` on a `1500+0` clock both engines legitimately move near
instantly (budget = clock − overhead) — symmetric by design, so a flag during an awake
window is never legitimate.

## 4. Gotchas (read before operating)

1. **Lid = everything on battery.** `caffeinate -i` does NOT block clamshell sleep; closing
   the lid during a match creates fake time-forfeits. Keep the lid open, or run on AC.
   Sleep events are auditable: `pmset -g log | grep 'Entering Sleep'`.
2. **Always pass `SCREENING_DIR`** to `status`/`stop`, otherwise the script silently uses
   the default directory and reports the wrong state:
   `env SCREENING_DIR=logs/screening/devbrain-s2-20261006 bash testing/continuous_screening.sh status`
3. **`tm_match.sh` exit 1 = game validation failed** (timeout/crash/short game) → the
   supervisor rejects the whole batch (fixed-size experiments abort). That is correct
   behavior; do not "fix" it by counting partial batches.
4. **Never overwrite `bin/youloss`.** SHA-256 must stay
   `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301` (bench 2,497,913) —
   it is the S2 opponent and the rollback anchor.
5. **Rebuilds of the candidate** are `ENGINE_OUT=youloss_devport bash scripts/build_engine.sh`
   — the default output name is the frozen `youloss`.
6. Environment floors are fail-closed: AC required (`REQUIRE_AC=1`) for protocol runs,
   battery ≥ 20-25%, free swap ≥ 256 MiB, free mem ≥ 10%, disk ≥ 500 MB, thermal nominal.

## 5. M5 setup & verification (do this first)

```bash
git clone https://github.com/GuigohC0D3/youloss_chesschallenge.git
cd youloss_chesschallenge
git checkout sprint1-sfdev-adopt

# toolchain
xcode-select -p                     # install Xcode CLT if missing
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# pinned NNUE nets (engine/src/*.nnue is gitignored — download, then verify)
make -C engine/src net              # or: (cd engine/src && make net)
shasum -a 256 engine/src/nn-252f33942263.nnue | cut -c1-12   # must print 252f33942263

# pinned fastchess runner (tools/ is gitignored)
bash scripts/build_fastchess.sh

# Syzygy tablebases (~941 MiB; assets/ gitignored except MANIFEST)
bash scripts/fetch_syzygy.sh && bash scripts/verify_assets.sh

# build the devport candidate (frozen bin/youloss comes from the release flow — see note*)
ENGINE_OUT=youloss_devport bash scripts/build_engine.sh
# bench must print: Nodes searched : 1714434

# gates
.venv/bin/python -m pytest -q                   # expect 335 passed
bash scripts/test_engine_tm.sh                  # expect OK: youloss_tm
```

\* `bin/` is gitignored, and a default build from **this** branch would produce the *dev*
brain named `youloss` (bench 1,714,434) — wrong opponent. Recover the frozen binary by
building the **port base commit** in a worktree:

```bash
git worktree add /tmp/youloss-frozen 05f03f6
(cd /tmp/youloss-frozen && bash scripts/build_engine.sh)   # bench must be 2,497,913
cp /tmp/youloss-frozen/bin/youloss bin/youloss
```

Verify bench 2,497,913. The original SHA-256 was
`c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301`; a PGO rebuild can
differ at byte level while matching bench. If it differs, record the new SHA in the S2
session log — the analyzer partitions by binary SHA, so scoring stays coherent (no counted
games exist under the old SHA anyway).

## 6. Run the batteries (needs AC, lid rule from §4)

Launch S2 exactly as preregistered (Amendment #1 is battery-only; on AC use `REQUIRE_AC=1`):

```bash
nohup env REQUIRE_AC=1 BATTERY_MIN=20 TC=1500+0 ROUNDS_PER_BATCH=2 MAX_BATCHES=50 PAUSE_S=30 \
  THREADS=7 CONC=1 HASH_MB=2048 MOVE_OVERHEAD_MS=1500 TIME_CAP_S=13000 \
  SYZYGY_PATH="$PWD/assets/syzygy" BOOK="$PWD/testing/openings/balanced_gm_v1.epd" \
  ENGINE="$PWD/bin/youloss_devport" SF_ENGINE="$PWD/bin/youloss" SF_ENGINE_LABEL=frozen-19 \
  MIN_FREE_SWAP_MB=256 MIN_FREE_MEM_PCT=10 MIN_DISK_MB=500 \
  SCREENING_DIR=logs/screening/devbrain-s2-20261006 \
  caffeinate -i bash testing/continuous_screening.sh start >> /tmp/youloss_s2.log 2>&1
```

- Monitor: `tail -f /tmp/youloss_s2.log` and
  `env SCREENING_DIR=... bash testing/continuous_screening.sh status`.
- Stop: same command with `stop` (verified working through the fixed kill path).
- Progress scoring: `testing/analyze_screening.py --sprt-dir logs/sprt`
  (paired openings, SHA-partitioned).
- Bars (write-locked before any game): **S2** devport vs frozen, n=400, ≥55% & CI-LB>50%;
  **S1** vs official dev prebuilt, n=400, ≥55% & CI-LB>50%; **S3** vs official sf19
  binary, n=400, ≥50% & zero time/crash/flag losses. CI = paired bootstrap 10,000
  resamples; only `Termination=normal` games count. Full protocol:
  `docs/evidence/2026-10-06-devbrain-preregistration.md`.
- Throughput estimate: ~35-45 min/game at 1500+0, CONC=1 → ≈8-10 days per 400-game series
  on M4; expect meaningfully faster on M5. Budget ≈1 month for all three series; start S2,
  then S1/S3 sizing updates.

## 7. After the batteries (stage 3, already specced)

`docs/evidence/2026-10-06-stage2-m5-handoff.md` covers, in order:
1. **NNUE retraining** on the M5's 400 GB free disk (data pipeline + schedules),
2. **SPSA tuning slot** for YoulossTM constants with a held-out validation set,
3. **Release rebuild** of the final artifact + archive verification,
4. **Tournament-day invariant** (settings freeze, board/clock rehearsal — still open with
   the organizer: written acceptance, physical latency, six qualification games).

## 8. Evidence index

| doc | contents |
|---|---|
| `docs/evidence/2026-10-06-devbrain-preregistration.md` | locked bars, stats plan, Amendment #1 (battery) |
| `docs/evidence/2026-10-06-devbrain-port-progress.md` | per-task RED→GREEN log, fingerprints, S2 campaign log |
| `docs/evidence/2026-10-06-stage2-m5-handoff.md` | retraining / SPSA / release playbook |
| `docs/superpowers/specs/2026-10-06-state-of-the-art-design.md` | approved architecture |
| `docs/superpowers/plans/2026-10-06-state-of-the-art-devbrain-port.md` | 10-task plan (1-7 done, 8-9 blocked on games, 10 partial) |
| `handoff.md` | dated project log (controller, harness, studies) |
| `docs/strength-experiment-protocol.md` | study hygiene rules |

Key fingerprints: frozen `bin/youloss` `c5ae7908…` bench 2,497,913 ·
`bin/youloss_devport` `5de10e10…` bench 1,714,434 · dev prebuilt
`stockfish dev-20260930-49ea5ded` `adef0f3e…80fd0` bench 1,714,434 · net
`nn-252f33942263.nnue`.

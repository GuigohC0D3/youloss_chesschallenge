# State-of-the-Art Engine Design: Adopt the SF-Dev Brain, Keep YoulossTM

**Date:** 2026-10-06
**Status:** Approved by user (Sections 1-5 approved; "do everything and start working")
**Repo:** youloss_chesschallenge, branch `victor` @ 05f03f6
**Classification:** Architectural

## Intent

Youloss is currently stock Stockfish 19 plus the YoulossTM time manager. The
intelligence barrier is not reached: search and evaluation are byte-identical
to sf_19 (`engine/ORIGIN.md`: base commit edb0d9db6731067ec50ce619ff372b463bc4dd5d,
bench 2497913, stock net `nn-1a298aa575a0.nnue`, "Busca e avaliação não foram
alteradas"). The goal is to make the engine as strong as possible while keeping
YoulossTM as the original claim.

**Acceptance yardsticks (user, layered):**

1. **Elo ladder** — track strength over time.
2. **Dev head-to-head hard bar** — ≥55% over 400 games, paired-CI lower bound >50%.
3. **Tournament metric** — ≥90% score, zero losses vs ICEV-tier (2200-2800)
   opponents; draws acceptable, losses unacceptable.

**Strategy (user):** adopt the brain, keep YoulossTM as the claim, phased —
adopt then own.

**Machine split (user):**

- **M4 dev laptop (16 GB, ~19 GiB free disk) — now:** everything that fits
  here: source port, builds, tests, benchmark verification, match batteries.
- **Friend's M5 tournament machine (Apple M5, 16 GB RAM, 512 GB disk, ≥400 GB
  free for the engine) — later:** the heavy adjustments — NNUE retraining on
  the 400 GB budget, SPSA tuning, final polish and tournament release build.

## Constraints

- **handoff.md:120** — ICEV official rules contain a "significant algorithm
  modification" rule whose satisfaction by YoulossTM remains unconfirmed.
  Event Nov 6 2026; team-change cutoff Nov 3; Git submission by email to
  icev@somosicev.com Nov 4; 25 min/player; physical board with
  player-operated clocks; no online software or external API; loss on flag
  or software failure; increment unspecified → 1500+0 provisional.
- No commits without explicit user go-ahead (repo rule: return diffs +
  evidence).
- Fail-closed testing harness must not be weakened: any time-forfeit,
  crash, disconnect, illegal move or stall rejects the batch
  (`testing/check_fastchess_log.sh`, `tests/test_failclosed_harness.py`).
- Screening must run on AC power with lid open: `caffeinate -i` does not
  block clamshell sleep, and system sleep during a move creates fake
  time-forfeit results (root-caused 2026-10-06: 587 s sleep → false
  "loses on time").

## Approach

**Approach A (approved):** full port of the Stockfish-dev source onto a
branch, re-apply the 6 YoulossTM hooks, fetch the dev net, build, verify,
then prove strength with preregistered screens. Current binary and dist
stay frozen as rollback. Stage 2 (own NNUE, SPSA) is spec'd for the M5.

## Section 1 — Phasing & Branch Strategy

**Branch:** `sprint1-sfdev-adopt` off `victor` (05f03f6).

**Stage 1 — M4, now:**

1. Port the 39 differing Stockfish-dev files into `engine/src/`, re-apply
   the 6 YoulossTM hooks.
2. Fetch dev net `nn-252f33942263.nnue` (missing from the extracted
   archive).
3. Build with the existing macOS clang PGO path; update the bench pin in
   tests to the dev official bench value.
4. Gate: unit test → 334 pytest suite → official bench cross-check.
5. Prove: preregistered screens (Section 4).
6. Rollback: current `bin/youloss` + `dist/youloss-candidate.tar.gz`
   untouched as the frozen fallback.

**Stage 2 — M5, friend's work (spec'd, not executed here):** full-size
NNUE training on 400 GB, SPSA tuning, final release rebuild.

**Out of Stage 1:** any training, any change to tournament day-of
procedure, any commit without user go-ahead.

## Section 2 — Port Mechanics & Hook Re-application

**Source of truth:** `/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/src`
(dev tree, no `.git`) vs `engine/src` (sf_19 + YoulossTM).

**Port = wholesale copy, not diff-merge.** The tree is byte-identical sf_19
except YoulossTM, so:

1. Copy all 39 differing `.cpp/.h` files dev → `engine/src/` (expected to
   wipe sf_19-era code and hooks wherever they overlap; hooks are re-added).
2. Do NOT copy `youloss_tm.{h,cpp}` (absent in dev) or
   `nn-1a298aa575a0.nnue`.
3. Re-apply the 6 hooks in dependency order:
   - `engine.cpp` — register the `YoulossTM` UCI option
   - `search.h` — TM-active flag
   - `timeman.h` / `timeman.cpp` — `set_bounds` interception. Dev
     `timeman.cpp` is 168 lines vs our 144 → the hook must be re-derived
     against the new function body, not pasted.
   - `search.cpp` — consult YoulossTM in the time-check path
   - `Makefile` — add `youloss_tm.o`
4. Collision check: diff the 6 hook sites before/after; anything ambiguous
   in dev's new code is flagged for manual review rather than guessed.

**Error handling:** fail-closed. If the ported tree does not compile, or
the hooks do not reproduce the UCI option surface exactly, the branch stays
broken and `victor` + frozen `bin/youloss` remain the working state.

**Verification:** `bash scripts/build_engine.sh` succeeds, `youloss_tm`
unit test OK, `uci` still exposes `YoulossTM`.

## Section 3 — Build, Test & Bench Gates

**Build:** `bash scripts/build_engine.sh` (macOS clang PGO path:
`platform.sh`, `LLVM_PROFDATA=$(xcrun -f llvm-profdata)`). Output →
`bin/youloss_devport` (never overwrite `bin/youloss` during Stage 1).

**Gates in order, each must pass before the next:**

1. Compile + link clean.
2. C++ unit tests — `youloss_tm_test` must pass against the ported tree.
3. Bench pin — the dev official bench value replaces the `2497913` pin;
   record our build's bench and cross-check against the prebuilt dev binary
   (`/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/stockfish-macos-universal`).
   Mismatch → stop and investigate; do not tune pins to match.
4. Pytest suite (334) — bench-pin and engine-identity assertions updated in
   the same diff; `.venv/bin/python -m pytest -q`.
5. Fingerprint — SHA-256 plus `id name` output of `bin/youloss_devport`
   recorded in the evidence doc.

**Stop condition:** any gate fails → fix on the branch, never weaken the
test. Three consecutive failures → stop and raise the architecture question.

**Disk hygiene:** reclaim stale `/tmp/youloss-*` dirs (≈1 GB, with user OK)
before building so PGO profile + artifacts fit in 19 GiB.

## Section 4 — Proving Ground (Preregistered Screens)

One protocol, three match series, all preregistered in an evidence doc
before the first game.

- **Runner:** `testing/continuous_screening.sh` → `tm_match.sh` → fastchess,
  fail-closed checker untouched.
- **Environment:** `REQUIRE_AC=1`, lid open, `caffeinate -i`, balanced book
  `testing/openings/balanced_gm_v1.epd` via the `BOOK` override,
  `TC=1500+0`, `THREADS=7 HASH_MB=2048 MOVE_OVERHEAD_MS=1500`, Syzygy on,
  swap/mem/disk floors as validated 2026-10-06.

| Series | Match | n | Hard bar |
|---|---|---|---|
| S2 (first) | `youloss_devport` vs current `bin/youloss` | 400 | ≥55%, CI lower bound >50% (regression guard) |
| S1 | `youloss_devport` vs official dev binary | 400 | ≥55%, CI lower bound >50% |
| S3 | `youloss_devport` vs sf19-official | 400 | score ≥50%, zero losses on time / crashes / flags |

**Analysis:** paired-Bootstrap CI on game scores; W/D/L totals; color
split; termination audit — every counted game must be `Termination=normal`.
Any time-forfeit is an environment failure: batch rejected, not counted.

**Result handling:** all bars pass → Stage 1 done. Any bar fails → hold at
the current binary (frozen rollback) and the user decides: iterate or ship
the stock-SF19 brain. No silent "close enough".

## Section 5 — Stage 2 Handoff (M5) & Evidence Trail

**Handoff package for the M5 (400 GB, 16 GB RAM):**

1. **NNUE retraining playbook** — full Stockfish-style pipeline: data
   generation with the ported brain, train/holdout split, compact→full net
   progression, target = beat `nn-252f33942263` head-to-head with a
   preregistered screen using Section-4 bars.
2. **SPSA tuning slot** — YoulossTM constants (`HorizonOpening 32`,
   `StabilityMin 0.70`, `FallMax 2.0`) listed as tuning candidates; the
   incumbent is the documented baseline; any promotion needs a
   preregistered screen whose CI excludes 50% in favor (FallMax-2.25
   precedent).
3. **Release rebuild** — `scripts/build_offline_release.py` + `dist/`
   regeneration on the M5, then Section-4 bars re-run on tournament
   hardware as final acceptance.
4. **Tournament-day invariant:** ship only `bin/youloss` + `assets/book.bin`
   + `assets/syzygy/` + `launch_youloss.sh`. Training corpora and PGO
   artifacts never leave the dev machines.

**Evidence trail (`docs/evidence/`):**

- This spec (written at design time).
- One preregistration doc per series (S1/S2/S3 written before games).
- Post-run results doc: W/D/L, CIs, color split, terminations, SHA-256 of
  every binary tested.

**Stop rules:** disk headroom short → clean first; battery/AC/sleep
violation → batch rejected (checker unchanged); 3 failed gates →
architecture question to the user; never commit without explicit
go-ahead.

## Non-Goals (Stage 1)

- NNUE training, SPSA tuning (Stage 2, M5).
- Any modification to the fail-closed checker thresholds.
- Any change to tournament day-of launch procedure.
- Any commit or push without explicit user approval.

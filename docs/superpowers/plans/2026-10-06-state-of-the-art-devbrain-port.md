# SF-Dev Brain Port (Stage 1 — M4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the Stockfish-dev-20260930 brain (39 source files + net) into `engine/src/`, re-apply the 6 YoulossTM hooks, build `bin/youloss_devport`, prove it through gates, then run the preregistered S2/S1/S3 match batteries.

**Architecture:** Wholesale copy of the 39 differing files from the extracted dev tree (our tree is byte-identical sf_19 except YoulossTM, so a copy is safer than a merge), then re-insert 6 known hooks verbatim, then build with the existing macOS clang PGO script into a NEW binary name so `bin/youloss` stays frozen as rollback. All quality claims are then re-earned through the existing fail-closed gates and three preregistered 400-game screens.

**Tech Stack:** C++17/Stockfish build system (make, clang, PGO), bash harnesses (`scripts/build_engine.sh`, `testing/tm_match.sh`, `testing/continuous_screening.sh`), fastchess, pytest (`.venv`, chess 1.11.2).

**Spec:** `docs/superpowers/specs/2026-10-06-state-of-the-art-design.md`

## Global Constraints

- **NO COMMITS, NO PUSH, NO STAGING.** Repo rule (AGENTS.md): return diffs + verification evidence only. Every task ends with a verification, never `git commit`.
- `bin/youloss` (SHA-256 recorded in Task 1) must remain byte-identical at the end of every task. Never overwrite it.
- Fail-closed checker (`testing/check_fastchess_log.sh`, `tests/test_failclosed_harness.py`) must not be modified.
- Screen environment: `REQUIRE_AC=1`, lid open, `caffeinate -i`, `TC=1500+0`, `THREADS=7 HASH_MB=2048 MOVE_OVERHEAD_MS=1500`, `SYZYGY_PATH=$PWD/assets/syzygy`, balanced book `BOOK=$PWD/testing/openings/balanced_gm_v1.epd`.
- 334-test pytest suite must be green before and after (` .venv/bin/python -m pytest -q`).
- Exact expected bench values: frozen `bin/youloss` = **2497913**, dev official prebuilt (`/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/stockfish-macos-universal`) = **1714434** (measured 2026-10-06).
- Dev binary id: `Stockfish dev-20260930-49ea5ded`. Dev net (from `evaluate.h`): `nn-252f33942263.nnue`, auto-fetched by `make net` from `https://tests.stockfishchess.org/api/nn/` (fallback `https://github.com/official-stockfish/networks/raw/master/`), sha256-validated by filename.

## Review Focus

1. **Hook silently lost during copy** — a 39-file copy wipes all 6 hooks; the engine would still compile and run, just with TM never engaging (or the option missing). Test: `test_option_listed_with_default_true` (pytest, Task 5) + `grep` inventory after Task 3 + a live `set_bounds` smoke (Task 5 Step 4) assert the option exists and TM actually alters budgeting.
2. **Bench mismatch hiding a wrong net or codegen** — build succeeds but bench ≠ 1714434 means wrong/missing net or a stray non-dev file. Test: Task 5 Step 2 pins `Nodes searched : 1714434` exactly; mismatch is a STOP (never adjust the pin to match).
3. **`bin/youloss` clobbered by the build** — build_engine.sh's default output name is `youloss`. Test: Task 1 records SHA-256; Task 4 Step 4 re-checks it equals the recorded value.
4. **Frozen binary drifting during promotion** — later tests import `DEFAULT_ENGINE = bin/youloss`. Test: `test_engine_tm.py::test_bench_unchanged` must keep asserting 2497913 against `bin/youloss` (Task 5 Step 3); it must NOT be edited in Stage 1.
5. **Screen rejected as environment artifact (sleep/AC)** — clamshell sleep during a move produces a fake "loses on time". Test: every screen batch uses `REQUIRE_AC=1` + `caffeinate -i` (Task 7/9 launch blocks) and any `SAFETY_STOP`/`incidente` in the batch log is classified as environment, never as a game result (Task 8/10 audit step).

---

### Task 1: Baseline snapshot and working branch

**Files:**
- Create: `docs/evidence/2026-10-06-devbrain-port-progress.md`
- No source changes.

**Interfaces:**
- Produces: recorded SHA-256 of `bin/youloss` (later tasks re-verify it) and the branch `sprint1-sfdev-adopt` that all later tasks use.

- [ ] **Step 1: Record baseline fingerprints**

```bash
cd /Users/seunome/Code/youloss_chesschallenge
sha256sum bin/youloss | tee /tmp/youloss_frozen.sha256
git switch -c sprint1-sfdev-adopt
git status --short | head -30
```

Expected: branch created at `05f03f6` (or current `victor` HEAD); dirty files carried over as-is (they are pre-existing, untouched).

- [ ] **Step 2: Confirm the suite is green before any change**

```bash
.venv/bin/python -m pytest -q 2>&1 | tail -3
bash scripts/test_engine_tm.sh 2>&1 | tail -3
```

Expected: `334 passed` (or the current known count) and `OK` (rc=0) for `youloss_tm`. If red here, STOP — fix the baseline first, do not proceed.

- [ ] **Step 3: Create the progress evidence file**

Write `docs/evidence/2026-10-06-devbrain-port-progress.md` containing: date, branch name, frozen `bin/youloss` SHA-256, dev prebuilt SHA-256 (`sha256sum /tmp/youloss-upstream-stockfish-dev/extracted/stockfish/stockfish-macos-universal`), dev id line, dev bench 1714434, frozen bench 2497913.

---

### Task 2: Copy the 39 differing source files from the dev tree

**Files:**
- Modify: 39 files under `engine/src/` (list below) — replaced wholesale by their dev versions.
- Not touched: `engine/src/youloss_tm.h`, `engine/src/youloss_tm.cpp`, `engine/src/nn-1a298aa575a0.nnue`, all `*.o`, `.depend`, `.build_*.txt`.

**Interfaces:**
- Consumes: dev tree at `/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/src`.
- Produces: a working tree whose 39 files are byte-identical to dev, still on branch `sprint1-sfdev-adopt`. Hooks are absent after this task (re-added in Task 3).

The exact 39 files:

```
attacks.h benchmark.cpp benchmark.h bitboard.h engine.cpp evaluate.cpp evaluate.h
Makefile memory.cpp memory.h misc.cpp misc.h movegen.cpp movepick.cpp
nnue/features/half_ka_v2_hm.cpp nnue/network.cpp nnue/network.h
nnue/nnue_accumulator.cpp nnue/nnue_accumulator.h nnue/nnue_architecture.h
nnue/nnue_common.h nnue/nnue_feature_transformer.h nnue/nnue_misc.cpp
nnue/nnue_misc.h nnue/simd.h numa.h position.cpp position.h search.cpp search.h
shm.h shm_unix.h thread.cpp thread.h timeman.cpp timeman.h tt.cpp tt.h uci.cpp
```

- [ ] **Step 1: Copy the 39 files**

```bash
cd /Users/seunome/Code/youloss_chesschallenge
DEV=/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/src
while read -r f; do cp "$DEV/$f" "engine/src/$f"; done < <(diff -rq engine/src "$DEV" | grep '^Files' | sed 's|Files engine/src/||; s| and .* differ||')
```

- [ ] **Step 2: Verify the copy and the invariants**

```bash
diff -rq engine/src "$DEV" | grep '^Files' | wc -l        # expect 0
diff -rq engine/src "$DEV" | grep 'Only in /tmp' | wc -l  # expect 0
ls engine/src/youloss_tm.h engine/src/youloss_tm.cpp engine/src/nn-1a298aa575a0.nnue  # all exist
git status --short engine/src | head -50
```

Expected: 0 differing files, no dev-only files, youloss files intact. `git status` shows the 39 files modified.

---

### Task 3: Re-apply the 6 YoulossTM hooks

**Files:**
- Modify: `engine/src/engine.cpp`, `engine/src/search.h`, `engine/src/timeman.h`, `engine/src/search.cpp` (3 insertions), `engine/src/Makefile` (2 insertions).

**Interfaces:**
- Consumes: dev files as copied in Task 2 (exact anchor text below is dev's current content).
- Produces: UCI option `YoulossTM` (default `true`), `SearchManager::youlossTM` flag, `TimeManagement::set_bounds()`, the budget/iteration-time call sites, `youloss_tm.o` linked. These are what Task 5's tests assert.

- [ ] **Step 1: Hook A — `engine.cpp` UCI option**

In `engine/src/engine.cpp`, replace:

```cpp
    options.add("nodestime", Option(0, 0, 10000));

    options.add("UCI_Chess960", Option(false));
```

with:

```cpp
    options.add("nodestime", Option(0, 0, 10000));

    // Youloss: gestão de tempo autoral (youloss_tm). false restaura a original.
    options.add("YoulossTM", Option(true));

    options.add("UCI_Chess960", Option(false));
```

- [ ] **Step 2: Hook B — `search.h` flag**

In `engine/src/search.h`, replace:

```cpp
    Value                bestPreviousAverageScore;
    bool                 stopOnPonderhit;
```

with:

```cpp
    Value                bestPreviousAverageScore;
    bool                 stopOnPonderhit;
    bool                 youlossTM = false;  // Youloss: youloss_tm ativo nesta busca
```

- [ ] **Step 3: Hook C — `timeman.h` set_bounds**

In `engine/src/timeman.h`, replace:

```cpp
    TimePoint elapsed_time() const { return now() - startTime; }

    void clear();
```

with:

```cpp
    TimePoint elapsed_time() const { return now() - startTime; }

    // Youloss: substitui optimum/maximum calculados por init() (youloss_tm).
    void set_bounds(TimePoint optimum, TimePoint maximum) {
        optimumTime = optimum;
        maximumTime = maximum;
    }

    void clear();
```

- [ ] **Step 4: Hook D — `search.cpp` include**

In `engine/src/search.cpp`, replace:

```cpp
#include "thread.h"
#include "timeman.h"
#include "tt.h"
#include "types.h"
```

with:

```cpp
#include "thread.h"
#include "timeman.h"
#include "tt.h"
#include "youloss_tm.h"
#include "types.h"
```

- [ ] **Step 5: Hook E — `search.cpp` budget call (after `tm.init`, before `tt.new_search`)**

In `engine/src/search.cpp`, replace:

```cpp
    main_manager()->tm.init(limits, rootPos.side_to_move(), rootPos.game_ply(), options,
                            main_manager()->originalTimeAdjust);
    tt.new_search();
```

with:

```cpp
    main_manager()->tm.init(limits, rootPos.side_to_move(), rootPos.game_ply(), options,
                            main_manager()->originalTimeAdjust);

    // Youloss: gestão de tempo autoral só em "base + incremento"; movestogo e
    // nodestime continuam com o gerenciador original.
    {
        const Color us = rootPos.side_to_move();
        auto*       mm = main_manager();
        mm->youlossTM  = int(options["YoulossTM"]) != 0 && limits.time[us] > 0
                     && limits.movestogo == 0 && int(options["nodestime"]) == 0;
        if (mm->youlossTM)
        {
            constexpr Value FullNonPawn =
              2 * (2 * KnightValue + 2 * BishopValue + 2 * RookValue + QueenValue);
            const Youloss::Budget b = Youloss::budget(
              {limits.time[us], limits.inc[us], TimePoint(options["Move Overhead"]),
               double(rootPos.non_pawn_material()) / FullNonPawn});
            mm->tm.set_bounds(b.optimum, b.maximum);
        }
    }
    tt.new_search();
```

- [ ] **Step 6: Hook F — `search.cpp` iteration_time call (after the totalTime cap, before `elapsedTime`)**

In `engine/src/search.cpp`, replace:

```cpp
            if (rootMoves.size() == 1)
                // Cap used time to 0.5s for a better viewer experience
                totalTime = std::min(500.0, totalTime);

            auto elapsedTime = elapsed();
```

with:

```cpp
            if (rootMoves.size() == 1)
                // Cap used time to 0.5s for a better viewer experience
                totalTime = std::min(500.0, totalTime);

            // Youloss: tempo-alvo autoral; as variáveis originais acima continuam
            // sendo calculadas porque alimentam previousTimeReduction.
            if (mainThread->youlossTM)
            {
                const Value prevAvg = std::abs(mainThread->bestPreviousAverageScore) >= VALUE_INFINITE
                                      ? bestValue
                                      : mainThread->bestPreviousAverageScore;
                totalTime           = Youloss::iteration_time(
                  {double(mainThread->tm.optimum()), rootDepth - lastBestMoveDepth,
                             totBestMoveChanges / double(threads.size()), bestValue, prevAvg,
                             mainThread->iterValue[iterIdx], is_decisive(bestValue),
                             int(rootMoves.size()), double(nodesEffort) / 100000.0});
            }

            auto elapsedTime = elapsed();
```

- [ ] **Step 7: Hook G/H — `Makefile`**

In `engine/src/Makefile`, replace:

```make
	engine.cpp score.cpp memory.cpp
```

with:

```make
	engine.cpp score.cpp memory.cpp youloss_tm.cpp
```

and replace the line ending `... numa.h memory.h shm.h shm_unix.h` with the same text plus ` youloss_tm.h` appended.

- [ ] **Step 8: Verify the hook inventory**

```bash
grep -c 'YoulossTM' engine/src/engine.cpp        # expect 2 (comment + option)
grep -c 'youlossTM' engine/src/search.h           # expect 1
grep -c 'set_bounds' engine/src/timeman.h         # expect 1
grep -c 'youloss_tm.h' engine/src/search.cpp      # expect 1
grep -c 'Youloss::budget' engine/src/search.cpp   # expect 1
grep -c 'Youloss::iteration_time' engine/src/search.cpp  # expect 1
grep -c 'youloss_tm.cpp' engine/src/Makefile      # expect 1
grep -c 'youloss_tm.h' engine/src/Makefile        # expect 1
bash -n scripts/build_engine.sh && echo OK
```

Expected: all counts as shown; `OK`.

---

### Task 4: Build `bin/youloss_devport` (PGO) without touching `bin/youloss`

**Files:**
- Modify: `scripts/build_engine.sh` (2 lines — parameterize the output name).

**Interfaces:**
- Consumes: Task 3 tree; `ENGINE_OUT` env var (default preserves today's behavior).
- Produces: `bin/youloss_devport`, re-cloned with default output still `youloss` (so CI/scripts are unaffected).

- [ ] **Step 1: Parameterize the output name**

In `scripts/build_engine.sh`, replace:

```bash
if is_mac; then
  build apple-silicon youloss
else
  build native youloss
  build x86-64-avx2 youloss-avx2
fi
"$ROOT/bin/youloss$EXE" bench 2>&1 | tail -4
```

with:

```bash
OUT="${ENGINE_OUT:-youloss}"
if is_mac; then
  build apple-silicon "$OUT"
else
  build native "$OUT"
  build x86-64-avx2 "$OUT-avx2"
fi
"$ROOT/bin/$OUT$EXE" bench 2>&1 | tail -4
```

- [ ] **Step 2: Sanity-check the script**

```bash
bash -n scripts/build_engine.sh && echo OK
grep -n 'ENGINE_OUT' scripts/build_engine.sh
```

Expected: `OK`, three hits (OUT=, build lines, bench line).

- [ ] **Step 3: Build with PGO**

```bash
ENGINE_OUT=youloss_devport bash scripts/build_engine.sh
```

Expected: completes with `Nodes searched : 1714434` in the final bench tail. Build takes several minutes (PGO: profile-make → bench → profile-use). If `make net` fails to download, retry once; if still failing, run `curl -skL -o engine/src/nn-252f33942263.nnue https://tests.stockfishchess.org/api/nn/nn-252f33942263.nnue` and verify `shasum -a 256 engine/src/nn-252f33942263.nnue | cut -c1-12` == `252f33942263`, then rebuild.

- [ ] **Step 4: Prove `bin/youloss` is untouched**

```bash
sha256sum -c /tmp/youloss_frozen.sha256
ls -la bin/youloss bin/youloss_devport
```

Expected: `OK`; both binaries present.

---

### Task 5: Gate battery (unit test → bench pin → pytest → UCI surface → fingerprint)

**Files:**
- Modify: `docs/evidence/2026-10-06-devbrain-port-progress.md` (append gate results).
- Test only: `scripts/test_engine_tm.sh`, `testing/tests/test_engine_tm.py`, `bin/youloss_devport`.

**Interfaces:**
- Consumes: `bin/youloss_devport` (Task 4).
- Produces: recorded gate evidence — this is the "unit test → 334 tests → official bench cross-check" gate from spec Section 3. Nothing here edits test files (the bench pin for `bin/youloss` must keep passing unchanged).

- [ ] **Step 1: C++ unit tests (TM model unchanged by the port)**

```bash
bash scripts/test_engine_tm.sh 2>&1 | tail -3
```

Expected: `OK` / rc=0. Failure = hooks or youloss files were damaged → fix in Task 3 scope, do not proceed.

- [ ] **Step 2: Bench cross-check against the official dev binary**

```bash
bin/youloss_devport bench 2>&1 | grep 'Nodes searched'
/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/stockfish-macos-universal bench 2>&1 | grep 'Nodes searched'
```

Expected: both print `Nodes searched  : 1714434`. A mismatch in our build is a STOP condition: re-check net file (`shasum -a 256 engine/src/nn-252f33942263.nnue`), re-check `diff -rq` count is 0, re-check hooks; do NOT edit any pin.

- [ ] **Step 3: Full pytest suite (must pass with zero edits to the frozen-binary assertions)**

```bash
.venv/bin/python -m pytest -q 2>&1 | tail -3
git diff --stat testing/tests/ | tail -3
```

Expected: `334 passed`; `git diff` shows NO test-file changes from this plan so far. `test_bench_unchanged` still asserts 2497913 against `bin/youloss`.

- [ ] **Step 4: UCI surface + TM smoke on the devport binary**

```bash
printf 'uci\nsetoption name YoulossTM value false\nquit\n' | bin/youloss_devport | grep -E 'id name|YoulossTM'
```

Expected: `id name Stockfish dev-20260930-49ea5ded` and `option name YoulossTM type check default true`. Then a live budget smoke: `bash testing/tm_match.sh 60+0.6 1` with `ENGINE_OUT`-independent defaults but `ENGINE` pointing at devport is NOT available yet (Task 7 adds it) — so instead assert `set_bounds` presence at runtime via the same output above plus the grep inventory of Task 3 Step 8. Record both.

- [ ] **Step 5: Fingerprint the devport binary**

```bash
sha256sum bin/youloss_devport | tee -a docs/evidence/2026-10-06-devbrain-port-progress.md
printf 'uci\nquit\n' | bin/youloss_devport | grep 'id name' | tee -a docs/evidence/2026-10-06-devbrain-port-progress.md
```

Expected: both lines appended to the evidence file.

---

### Task 6: Preregistration document for S2 / S1 / S3

**Files:**
- Create: `docs/evidence/2026-10-06-devbrain-preregistration.md`

**Interfaces:**
- Consumes: gates green (Task 5), spec Section 4 bars.
- Produces: the written-before-first-game hypotheses, bars, stop rules that Tasks 7/9/10 reference.

- [ ] **Step 1: Write the preregistration doc**

Contents (exact, in the doc):

```markdown
# Preregistration: devport screens S2 / S1 / S3 (2026-10-06)

Written BEFORE the first game. Changes require an amendment section, never silent edits.

## Candidate
bin/youloss_devport (sha256 <from Task 5>), id "Stockfish dev-20260930-49ea5ded" + YoulossTM option.

## Protocol (all series)
- Runner: testing/continuous_screening.sh -> tm_match.sh -> fastchess, fail-closed checker unmodified.
- Env: REQUIRE_AC=1, caffeinate -i, TC=1500+0, THREADS=7, CONC=1, HASH_MB=2048,
  MOVE_OVERHEAD_MS=1500, TIME_CAP_S=6100, SYZYGY_PATH=$PWD/assets/syzygy,
  BOOK=$PWD/testing/openings/balanced_gm_v1.epd, MIN_FREE_SWAP_MB=256,
  MIN_FREE_MEM_PCT=10, MIN_DISK_MB=500.
- Counted games: Termination=normal only. Any time-forfeit/crash/illegal/stall rejects the
  batch (environment) and is NOT counted as a result.
- CI: paired bootstrap on game scores, 10000 resamples, 95%.

## Series
| # | opponent | n | bar |
|---|----------|---|-----|
| S2 first | bin/youloss (frozen, YoulossTM default) | 400 | >=55% AND CI lower bound >50% |
| S1 | official dev prebuilt (SF_ENGINE=/tmp/youloss-upstream-stockfish-dev/.../stockfish-macos-universal, label dev-official) | 400 | >=55% AND CI lower bound >50% |
| S3 | sf19-official (SF_ENGINE=/tmp/youloss-benchmark/stockfish/stockfish-macos-universal) | 400 | >=50% score AND zero losses on time/crash/flag |

## Stop rules
- Any series' bar fails -> hold at frozen bin/youloss (rollback), report to user: iterate or ship.
- Environment rejection -> rerun after fixing power/sleep; never reclassify as a result.
- Sleep/AC violation -> batch invalid (pmset -g log audit after every batch).
```

- [ ] **Step 2: Self-check the doc exists before any match starts**

```bash
test -s docs/evidence/2026-10-06-devbrain-preregistration.md && echo PREREG-OK
```

Expected: `PREREG-OK`.

---

### Task 7: `ENGINE` override in `tm_match.sh` + launch S2 (devport vs frozen `bin/youloss`)

**Files:**
- Modify: `testing/tm_match.sh:177` (one line, same pattern as the existing `BOOK` override).

**Interfaces:**
- Consumes: `bin/youloss_devport`, preregistration (Task 6).
- Produces: S2 rundir + scoreboard under `logs/screening/devbrain-s2-20261006/`; `SF_OPTIONS` stays default (different SHA ⇒ opponent plays with its own defaults, recorded as `external:frozen-19`).

- [ ] **Step 1: Add the ENGINE override**

In `testing/tm_match.sh`, replace:

```bash
ENGINE="$ROOT/bin/youloss$EXE"
```

with:

```bash
ENGINE="${ENGINE:-$ROOT/bin/youloss$EXE}"
```

- [ ] **Step 2: Syntax + harness tests still green**

```bash
bash -n testing/tm_match.sh && echo OK
.venv/bin/python -m pytest -q testing/tests/ 2>&1 | tail -2
```

Expected: `OK`, suite unchanged (334 passed).

- [ ] **Step 3: Verify the two-binary match wiring (1 round smoke, not scored)**

```bash
ENGINE="$PWD/bin/youloss_devport" SF_ENGINE="$PWD/bin/youloss" SF_ENGINE_LABEL=frozen-19 \
  THREADS=2 HASH_MB=64 MOVE_OVERHEAD_MS=10 TIME_CAP_S=300 \
  bash testing/tm_match.sh 10+0.1 1 2>&1 | tail -15
```

Expected: fastchess runs with `cmd=bin/youloss_devport` vs `cmd=bin/youloss`, both SHAs recorded in meta.json, exit 0, checker 0. This smoke game is discarded (different TC from preregistration) — note that in the progress file.

- [ ] **Step 4: Launch S2 in the background**

```bash
cd /Users/seunome/Code/youloss_chesschallenge
nohup env REQUIRE_AC=1 BATTERY_MIN=20 TC=1500+0 ROUNDS_PER_BATCH=2 MAX_BATCHES=50 PAUSE_S=30 \
  THREADS=7 CONC=1 HASH_MB=2048 MOVE_OVERHEAD_MS=1500 TIME_CAP_S=13000 \
  SYZYGY_PATH="$PWD/assets/syzygy" BOOK="$PWD/testing/openings/balanced_gm_v1.epd" \
  ENGINE="$PWD/bin/youloss_devport" SF_ENGINE="$PWD/bin/youloss" SF_ENGINE_LABEL=frozen-19 \
  MIN_FREE_SWAP_MB=256 MIN_FREE_MEM_PCT=10 MIN_DISK_MB=500 \
  SCREENING_DIR=logs/screening/devbrain-s2-20261006 \
  caffeinate -i bash testing/continuous_screening.sh start > /tmp/youloss_s2.log 2>&1 &
echo "S2 pid=$!"
```

Expected: supervisor starts, `Pre-batch check #1` passes (AC required), child starts `tm_match.sh`, rundir parsed, batch accepted or rejected visibly in `/tmp/youloss_s2.log`. Note: `TIME_CAP_S=13000` covers 2 rounds × 4 × 1500 s + 30 s (pre-flight formula from the earlier root-cause: `rounds*4*base + 30`).

- [ ] **Step 5: Verify the first batch is running clean (after ~10 min)**

```bash
tail -30 /tmp/youloss_s2.log
pmset -g log | grep -i 'sleep' | tail -3
```

Expected: batch accepted, no `SAFETY_STOP`, no sleep event while the lid is open. If a batch is rejected for environment reasons, fix the environment and relaunch; never edit the checker.

---

### Task 8: S2 monitoring, scoring and evidence

**Files:**
- Create: `docs/evidence/2026-10-06-devbrain-s2-results.md`

**Interfaces:**
- Consumes: S2 scoreboard at `logs/screening/devbrain-s2-20261006/scoreboard.json` + `meta.json`/`match.log` per rundir.
- Produces: W/D/L, score %, paired-bootstrap CI, color split, termination audit, bar verdict.

- [ ] **Step 1: Poll until the bounded session ends (batch cap or deadline)**

```bash
bash testing/continuous_screening.sh status; tail -5 /tmp/youloss_s2.log
```

Repeat on a schedule; if the session stops early (SAFETY_STOP/incidente), classify cause from the log + `pmset -g log` before relaunching.

- [ ] **Step 2: Aggregate results**

Parse all `meta.json` under `logs/sprt/` created since launch (only `exit_checker=0` entries): sum `Games/Wins/Losses/Draws` from `match.log`, split by side, verify every counted game's PGN `Termination` is normal.

- [ ] **Step 3: Compute the CI and write the results doc**

Use `.venv/bin/python` with a 10000-resample paired bootstrap over game scores (win=1, draw=0.5, loss=0); record W/D/L, %, CI, color split, and the bar verdict (≥55% AND CI-LB>50%) in `docs/evidence/2026-10-06-devbrain-s2-results.md`, plus SHA-256 of both binaries.

- [ ] **Step 4: Verdict branch**

If the bar fails → STOP the campaign, restore nothing (frozen binary was never touched), report to the user: iterate on the port or ship the sf_19 brain. If it passes → Task 9.

---

### Task 9: S1 (vs official dev binary) and S3 (vs sf19-official)

**Files:**
- Create: `docs/evidence/2026-10-06-devbrain-s1-results.md`, `docs/evidence/2026-10-06-devbrain-s3-results.md`

**Interfaces:**
- Consumes: `ENGINE` override (Task 7), preregistration bars.
- Produces: two more results docs; final Stage-1 verdict (all three bars).

- [ ] **Step 1: Launch S1**

Same launch block as Task 7 Step 4, changing only:

```bash
  SF_ENGINE=/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/stockfish-macos-universal \
  SF_ENGINE_LABEL=dev-official \
  SCREENING_DIR=logs/screening/devbrain-s1-20261006 \
```

Expected: meta.json records the dev prebuilt SHA; `SF_OPTIONS_DESCRIPTION=external:dev-official`.

- [ ] **Step 2: S1 scoring** — same aggregation/CI/audit as Task 8 Steps 2-3 into the S1 results doc.

- [ ] **Step 3: Launch S3**

Same block, changing only:

```bash
  SF_ENGINE=/tmp/youloss-benchmark/stockfish/stockfish-macos-universal \
  SF_ENGINE_LABEL=sf19-official \
  SCREENING_DIR=logs/screening/devbrain-s3-20261006 \
```

S3 bar: score ≥50% **and** zero losses on time / crashes / flags across counted games.

- [ ] **Step 4: S3 scoring** — as Task 8 Steps 2-3, with the termination audit elevated: a single counted game with a non-normal termination fails the bar (checker normally prevents this; the audit double-checks).

- [ ] **Step 5: Final Stage-1 verdict**

Append to `docs/evidence/2026-10-06-devbrain-port-progress.md`: the three bar verdicts and the decision (all pass → devport becomes the candidate pending user-approved promotion; any fail → rollback hold).

---

### Task 10: Stage-2 M5 handoff playbook + final report

**Files:**
- Create: `docs/evidence/2026-10-06-stage2-m5-handoff.md`

**Interfaces:**
- Consumes: spec Section 5; all Stage-1 evidence.
- Produces: the executable checklist the friend runs on the M5 (≥400 GB); the final diff + evidence report to the user (no commits).

- [ ] **Step 1: Write the handoff playbook**

Sections, each with concrete commands (not vibes):
1. **NNUE retraining** — disk layout for 400 GB/16 GB RAM; data generation command from the ported brain (`bin/youloss_devport` data-gen if present in dev toolchain, else the Stockfish `make net` + `nnue-py` workflow); train/holdout split; target net name format `nn-[sha256-12].nnue`; acceptance = head-to-head screen vs `nn-252f33942263` using the Section-4 bars (same runner, `BOOK`, `REQUIRE_AC=1`).
2. **SPSA slot** — candidates `HorizonOpening=32.0`, `StabilityMin=0.70`, `FallMax=2.0` in `engine/src/youloss_tm.cpp`; incumbent = baseline; promotion only with a preregistered screen whose CI excludes 50% (FallMax-2.25 precedent, `docs/evidence/2026-10-05-fallmax-2.0-vs-2.25-results.md`).
3. **Release rebuild** — `scripts/build_offline_release.py`, `scripts/verify_offline_release.py` (7/7), then re-run S3-style acceptance on the M5 hardware.
4. **Tournament-day invariant** — ship only `bin/youloss` + `assets/book.bin` + `assets/syzygy/` + `release/launch_youloss.sh`; never ship corpora/PGO artifacts.

- [ ] **Step 2: Final evidence bundle**

```bash
git status --short > /tmp/final_diff_status.txt
git diff --stat | tail -5
sha256sum bin/youloss bin/youloss_devport
.venv/bin/python -m pytest -q 2>&1 | tail -2
bash scripts/test_engine_tm.sh 2>&1 | tail -1
```

- [ ] **Step 3: Report to the user (no commits)**

Deliver: branch + full `git status`/`git diff` summary, gate evidence (bench 1714434 match, 334 passed, unit OK), S2/S1/S3 verdicts with CIs, file list of new evidence docs, and the explicit question of whether to promote `youloss_devport` over `bin/youloss` (promotion = a separate, user-approved change that also updates `BENCH_NODES` in `testing/tests/test_engine_tm.py` to 1714434).

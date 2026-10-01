# Youloss Chess Challenge — Handoff

**Prepared:** 2026-10-01
**For:** Next project reviewer/agent
**Repository:** Youloss Chess Challenge repository root (local path omitted)
**Branch:** victor
**Initial snapshot HEAD:** 207a0734fd5f135703eff176f41f652c6a680397
**State:** This handoff preserves earlier snapshots and adds the 2026-10-01 closeout. The starting point for the closeout was a clean `victor` branch at `f143ffbe11f065e83638c8a6f79b92aad5a88b10`, synchronized with `origin/victor`; subsequent handoff edits are recorded below.

## Project objective

Prepare a Stockfish 19-derived chess engine with an original time manager and Python controller for the local-only III Chess Challenge. The operator uses a physical board and manual clock. The project aims to be tournament-compliant, reliable under clock pressure, and supported by honest strength evidence. Bench parity and short screens are integrity checks; they do not establish playing strength.

The official [event rules PDF](https://www.somosicev.com/wp-content/uploads/2026/09/Chess-Challenge-III-1.pdf) and [event announcement](https://www.somosicev.com/icev-abre-inscricoes-para-o-iii-chess-challenge-torneio-que-une-programacao-e-xadrez/) were reviewed on 2026-10-01. The rules confirm the event date (Nov 6, 2026), team-change cutoff (Nov 3), Git submission by email to `icev@somosicev.com` on Nov 4, 25 minutes per player, player-operated clocks, a physical board, player responsibility for moving pieces, no online software or external API communication, and losses for a flag or software failure. They do not specify an increment; `1500+0` remains the controller's provisional interpretation. Exact clock operation, local books/tablebases/ponder, illegal-move and draw procedure, and whether the current YoulossTM satisfies the significant-algorithm-modification rule remain to be confirmed.

The official PDF also contradicts itself about the number of qualifying rounds and knockout bracket: it contains “5 quatro rodadas,” says the top eight advance to semifinals/final, and separately schedules a round of 16 and quarterfinals. The announcement and PDF also give different venue names in different locations. Ask the organizers to clarify these items before relying on the schedule or venue details.

## Current repository state

- At the handoff snapshot, branch victor tracked origin/victor at the same commit. A fresh `git fetch origin` during the 2026-10-01 closeout confirmed no divergence before the closeout commits. The local sprint0-fundacao branch was four commits behind its cached upstream.
- The shared worktree was dirty at the handoff snapshot. Its controller, harness, plan/spec, README, and handoff changes were reviewed and included in the closeout; macOS `.DS_Store` artifacts were excluded. Five closeout commits were pushed to `origin/victor`; the checkout was clean and synchronized after a fresh post-push fetch.
- Current local assets include bin/youloss, tools/fastchess, .venv, and assets/openings/UHO_Lichess_4852_v1.epd. The later 2026-09-30 review addendum records the EPD matching assets/MANIFEST and scripts/verify_assets.sh passing. No Polyglot book or Syzygy tablebases are present.
- Runner pin: fastchess v1.8.2-alpha, commit f618e34540f94f4719ad3817950618dabe441318. Recorded fastchess SHA256 38a7b822c711afd9435d8be91482e555c5b8e2d5414fd2c91de7e6db93baa6ab matched tools/fastchess.build.json. Recorded UHO EPD SHA256 7a7f6470615a69c6cf23d565417701d38732876f480af90d67b42abade35644a. Alpha-versus-stable policy is unresolved.
- `scripts/fetch_openings.sh` was an unexplained modification in the pre-closeout snapshot; it was reviewed and included in the pushed closeout.
- Vault pull failed with `fatal: Not possible to fast-forward, aborting`; no vault files were changed, so this handoff is based on the checkout, existing project docs, and available session context.

## Work completed in this conversation

1. Project branch/context was reviewed after switching to victor and pulling the shared project work. The local tournament-excellence plan was used to identify remaining risks.
2. A fuller project review package was created in the local agent scratchpad and is not included in this repository. Its first/current-state addendum is newest; older dossier sections intentionally preserve historical snapshots and may be stale.
3. Four defects from review were tracked:
   - Premature clock loss with positive physical time: the fix was already in the dirty checkout before the harness phase. Estimated-clock expiry now requires a fresh physical reading; only confirmed physical zero records a flag.
   - Rounded/inconclusive SPRT acceptance: parser/checker require displayed LLR to clear the displayed bound by at least 0.01.
   - Timeout left a descendant holding the tee pipe: harness uses a dedicated process group, waits for descendant exit, and escalates TERM to KILL after grace.
   - Malformed evidence passed: parser/checker validate the full LLR row, reconcile Wins + Losses + Draws with Games, and reconcile the five paired Ptnml(0-2) buckets with Games. Current runner output uses Ptnml(0-2), not Penta; valid nan WL/DD ratio is supported.
4. The harness keeps unique run directories and records seed/config/runner/engine metadata, captures stdout and stderr, omits -recover, runs the checker even after runner failure, and checks fastchess/tee/checker outcomes. THREADS and HASH_MB are validated and recorded.
5. The 2026-10-01 closeout also moved low-margin fallback behind estimated-clock expiry handling, rejected `played` after estimate expiry until a fresh physical reading, allowed `undo` to clear an unplayed first-move proposal, and rejected SPRT invocations with only one Elo bound.

## Verification already recorded

**2026-10-01 closeout verification:**

- `./.venv/bin/python -m pytest controller/tests testing/tests -q` — 213 passed, 1 skipped in 37.41s.
- Targeted partial-SPRT-argument regression cases — 2 passed in 0.12s.
- `git diff --check` — exit 0.
- `almostGlobal` quality run — 91/100, passed, no secret findings. Two Semgrep warnings point to unchanged `engine/src/shm_unix.h`; the resilience check skipped because `DATABASE_URL` was unset.
- Fresh official-rule review — confirms the event date, deadlines, 25-minute allocation, physical-board/manual-clock operation, offline/API restriction, and flag/software-failure losses. See the source links above; remaining interpretations are listed below.
- `bash scripts/check_toolchain.sh` — passed on this Apple M4/macOS host.
- `bash scripts/verify_assets.sh` — the one tracked manifest asset verified successfully. The engine, fastchess, virtual environment, and UHO test file are local ignored artifacts, not included in a clean Git clone.

**Focused tests from the defect repair:**

- ./.venv/bin/python3 -m pytest testing/tests/test_failclosed_harness.py -q — 39 passed in 8.21s.
- ./.venv/bin/python3 -m pytest controller/tests/test_clock_protocol.py -q — 20 passed in 6.38s. Clock fix/test pre-existed this harness phase; this was a rerun.
- git diff --check — no output, exit 0.

**Bounded checks from the follow-up:**

- ./.venv/bin/python3 -m pytest testing/tests/test_engine_tm.py::test_bench_unchanged -q — 1 passed in 7.12s; expected 2,497,913 nodes. This confirms bench parity, not strength.
- Offline UCI startup was rechecked on 2026-10-01 using the existing local `bin/youloss`: `uci`, `isready`, and `quit` returned 0 with `uciok` and `readyok` under 10 seconds; local only, no network. A clean-clone source build is still outstanding.
- Real fastchess direct smoke used a temporary legal start-position EPD, real engine in both YoulossTM modes, one round/two games, and a 20-second process-group cap. It completed in 17.3 seconds, runner exit 0, two draws, PGN showed both color orientations. No -recover; config/PGN stayed under /tmp. At that point the UHO asset was absent; it was fetched and verified in later recorded work.
- Raw output was saved in the local agent scratchpad and is not included in this repository.

**Later results documented in the current-state addendum (not rerun while writing this file):**

- Full controller/testing suite: 205 passed, 1 skipped in 42.58s. Shell syntax, Python compilation, git diff --check, and scripts/verify_assets.sh also reportedly passed.
- 40 paired games at 10+0, 1 thread / 16 MiB, seed 2026093001: tm 10W/12L/18D, Elo -17.39 +/- 68.73, score 47.50%. Inconclusive scaled screen, not strength evidence. Averaged 9.02s/game (tm) vs 9.31 (sf); passed runner/checker/time profile with no incidents in 12m24s. Log: logs/sprt/tm_10+0_r20_s2026093001_20260930-220620.Wdw0EC.
- 40 paired games at 10+0, 4 threads / 512 MiB, seed 2026093003: tm 9W/7L/24D, Elo +17.39 +/- 53.86, score 52.50%. Inconclusive scaled screen, not sustained thermal evidence. Averaged 8.69 vs 8.96; passed all checks with no incidents in 11m59s. Log: logs/sprt/tm_10+0_r20_s2026093003_20260930-222758.hJKp75.
- Four paired games at 25+0, 4 threads / 512 MiB, seed 2026093004: tm 2W/0L/2D, score 75 percent, no incidents. Four-game engine-only smoke; it did not test the controller or physical clock. Averaged 23.70 vs 24.76; passed all checks in 3m18s; provisional config. Log: logs/sprt/tm_25+0_r2_s2026093004_20260930-224146.xZggHp.
- Fail-closed SPRT rule: fastchess v1.8.2-alpha may print `SPRT completed - H1 was accepted` at max games while LLR is still inside [-2.94, 2.94]; acceptance must require the checker's evidence, not that status string alone.
- Post-parser-fix two-game end-to-end smoke (tm 0W/1L/1D) was the successful rerun after the Penta vs Ptnml(0-2) fix. An earlier four-game wrapper run failed because the checker expected Penta instead of Ptnml(0-2); retain it as a failed validation, not a pass.
- Separate four-thread 512 MiB option-propagation smoke passed option propagation; it is distinct from the post-parser-fix two-game end-to-end smoke above.
- Detailed ignored logs and experiment summaries are in local-only review materials. Preserve successful, failed, and inconclusive runs.

## Remaining work, in priority order

1. Request organizer clarification of: clock increment and exact hands-on protocol; local book/tablebase/ponder policy; illegal-move and draw handling; qualifying-round count, knockout bracket, and venue; whether the documented YoulossTM algorithm meets the significant-modification criterion; and the exact Git submission/validation procedure. The PDF already confirms Nov 4 email submission to `icev@somosicev.com`, 25 minutes per player, and losses on flag or software failure. No message has been sent.
2. Measure the provisional 2.0-second operator latency and rehearse physical-board operation with the actual clock: low-time recovery, corrections, promotion, draw handling, resume reconciliation, clock corrections, and fault injection.
3. Select the M4 thread/hash profile from sustained, AC-powered thermals, throughput, latency, memory pressure, and swap measurements. Existing 1-thread/16-MiB and 4-thread/512-MiB runs are short screens, not sustained profile evidence.
4. Before a strength study, freeze the binary, options, and opening holdout, then preregister paired-color sample size, stopping/acceptance rules, and compute budget. Keep failed and inconclusive outcomes. No accepted SPRT or strength conclusion exists.
5. Complete release readiness: clean-clone build, offline startup from the release artifact, runtime asset/checksum audit, rollback artifact, and license/provenance review. The GPLv3 text, Stockfish origin commit, and current YoulossTM algorithm summary are present; verify the exact submitted source and binary together. The pinned runner remains `v1.8.2-alpha`, still marked Latest on the [upstream release list](https://github.com/Disservin/fastchess/releases) when checked on 2026-10-01; all listed versions are alpha. Do not use it for a strength conclusion without explicitly accepting that limitation.
6. Keep physical-clock rehearsal and tournament readiness separate from engine-to-engine fastchess results.

## Dates and caveats

The project plan's P0–P5 date windows are roadmap proposals, not all confirmed commitments. Event facts above come from the official rules and announcement linked above; both contain wording inconsistencies that need organizer clarification. The plan assumes engine, controller/operator, and testing/release roles, but names are unassigned.

The 2026-09-30 bounded note originally said the UHO asset was missing and only a synthetic two-game smoke had been run. Later same-day review evidence supersedes that snapshot: UHO is present, asset verification reportedly passed, and paired screening runs were recorded. Fuller historical evidence remains in local-only review materials and is not part of this repository.

No long SPRT, sustained thermal run, organizer clarification, or physical-operator rehearsal is recorded as complete. No outbound message has been sent. Five closeout commits were authorized, reviewed, and pushed on 2026-10-01; `victor` was clean and synchronized with `origin/victor` after fetch. No future owner assignment is known.

## Reviewer checklist

Return prioritized findings with file/evidence references. Separate verified facts, reported historical results, inference, and recommendations. Identify contradictions or stale claims. Recommend the single highest-value next action and give a concrete completion/verification condition. Check current branch/worktree state and session authorization before further mutations.

## Source manifest

- README.md — setup and operator workflow.
- docs/superpowers/plans/2026-09-28-local-tournament-excellence.md — roadmap and current progress.
- docs/superpowers/specs/2026-09-28-youloss-chess-engine-design.md — architecture; superseded assumptions must be checked against PDF.
- engine/ORIGIN.md and engine/src/youloss_tm.* — upstream baseline and custom allocator.
- controller/game.py, controller/clock.py, controller/runtime.py and controller/tests — controller/clock reliability.
- testing/sprt_result.py, testing/check_fastchess_log.sh, testing/tm_match.sh, testing/tests/test_failclosed_harness.py — SPRT acceptance and match runner.
- scripts/build_fastchess.sh, tools/fastchess.build.json, assets/MANIFEST, scripts/verify_assets.sh — runner pin and asset integrity.
- Ignored experiment logs: logs/sprt/tm_10+0_r20_s2026093001_20260930-220620.Wdw0EC; logs/sprt/tm_10+0_r20_s2026093003_20260930-222758.hJKp75; logs/sprt/tm_25+0_r2_s2026093004_20260930-224146.xZggHp.

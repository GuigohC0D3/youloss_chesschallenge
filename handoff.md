# Youloss Chess Challenge — Handoff

## 2026-10-03 implementation and qualification update (newest)

The starting point for this update was clean `victor` at `e9cf37a`, synchronized with `origin/victor`. Earlier sections below preserve their historical snapshots and results. This update adds a stricter engine-match preflight, bounded engine stderr incident diagnostics, exact-position emergency move reuse, simulated operator-delay replay, and an offline candidate package. It does not change the Stockfish-derived C++ search or time manager.

- **Controller:** engine stderr is drained into a 100-line/16-KiB tail; engine incidents record failure class, exit code, FEN, clocks, and that tail beside the game log. An incident write failure cannot suppress the tournament terminal software-loss path. Emergency fallback reuses an engine candidate only for the exact current FEN and a still-legal move; otherwise it uses the existing tactical ordering. Tests cover stalls, crashes, large stderr without a newline, low-time recovery, corrections, and candidate invalidation.
- **Clock replay:** `testing/operator_replay.py` uses a virtual clock and fake engine to debit simulated clock reading, UCI entry, piece movement, and clock pressing. It checks search budget against the reported clock and marks output explicitly as simulated. Normal and positive-recovery replays finished with three moves; the confirmed physical-zero replay recorded a flag. Logs, states, and summary are under `docs/evidence/operator-replay-20261003/`. These values are not measurements of the physical board or operators.
- **Experiment preflight:** `testing/tm_match.sh` supports numeric `base+increment` controls, applies a 10% initial-budget overhead policy, and rejects a fixed zero-increment run whose wall cap cannot cover its maximum clock time plus a process buffer. The 10% limit is a conservative experiment policy, not a fairness or strength guarantee. The two-game `10+0` smoke at 4 threads/512 MiB, 10 ms overhead and seed `2026100301` completed in 42 seconds: YoulossTM 0W/1L/1D; runner, checker, and timing profile passed without flags. This is wiring evidence only, not an Elo estimate. Preserved ignored log: `logs/sprt/tm_10+0_r1_s2026100301_20261003-000551.qzWXeJ/`.
- **Offline candidate:** `scripts/build_offline_release.py` creates `dist/youloss-candidate.tar.gz` with the native engine, full corresponding engine source and NNUE build input, bundled macOS arm64 Python 3.12 and `chess==1.11.2`, controller, GPL/provenance, launcher, and a per-file SHA-256 manifest. `scripts/verify_offline_release.py` checks archive paths, all 1,764 file hashes, bundled imports, UCI readiness, legal controller searches in both engine modes, launcher preflight, and source presence. The first verified archive was built from the dirty implementation checkout at `e9cf37a` and is **an unqualified candidate**, not the final submission artifact. At this precommit snapshot, a clean-commit rebuild and exact-archive verification were still required.
- **Verification:** full `controller/tests testing/tests` suite **262 passed, 1 skipped in 44.77s**; the skip remains the optional Syzygy integration because no tablebases are installed. `bash scripts/check_toolchain.sh`, `bash scripts/verify_assets.sh`, shell syntax, release syntax, and `git diff --check` passed. The engine binary in the package has SHA-256 `07114ae47f7a9e6139425b01086b89a0b9203998ff4f9f76024c43f95346a301`, matching the earlier clean-clone PGO build; C++ source did not change in this update.
- **Open external/physical gates:** organizer acceptance and increment, actual clock latency, six physical-board qualification games, a sustained AC-only hardware profile, and a statistically meaningful strength study remain open. The Mac was on battery at 66% during this update; no sustained thermal qualification was attempted. See `docs/organizer-clarification-draft.md` (unsent) and `docs/strength-experiment-protocol.md` (no scored experiment begun under it). `1500+0` and 8 threads/512 MiB/2.0s remain provisional candidates.

**Prepared:** 2026-10-02
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
- Four paired games at fastchess `25+0` (25 seconds per side, zero increment), 4 threads / 512 MiB, seed 2026093004: tm 2W/0L/2D, score 75 percent, no incidents. The PGN records `TimeControl "25"` and games lasted 46–50 seconds. This was a short engine-only smoke; it did not test the tournament's provisional `1500+0` time control, controller, physical clock, or strength. Averaged 23.70 vs 24.76; passed all checks in 3m18s. The rules say 25 minutes per player but do not specify increment, so `1500+0` remains provisional pending organizer clarification. Log: logs/sprt/tm_25+0_r2_s2026093004_20260930-224146.xZggHp.
- Fail-closed SPRT rule: fastchess v1.8.2-alpha may print `SPRT completed - H1 was accepted` at max games while LLR is still inside [-2.94, 2.94]; acceptance must require the checker's evidence, not that status string alone.
- Post-parser-fix two-game end-to-end smoke (tm 0W/1L/1D) was the successful rerun after the Penta vs Ptnml(0-2) fix. An earlier four-game wrapper run failed because the checker expected Penta instead of Ptnml(0-2); retain it as a failed validation, not a pass.
- Separate four-thread 512 MiB option-propagation smoke passed option propagation; it is distinct from the post-parser-fix two-game end-to-end smoke above.
- Detailed ignored logs and experiment summaries are in local-only review materials. Preserve successful, failed, and inconclusive runs.

## 2026-10-01 follow-up

- The local branch was fast-forwarded to include upstream `4aafff4` (`docs: add contributors section to README`) before this follow-up. The match runner now applies `Move Overhead=1500` to both engines by default, matching the controller, and records the value in the run log and `meta.json`. This remains an engine-only comparison and does not simulate human clock-operation latency. A single paired `1500+0` runner example uses `TIME_CAP_S=7200`; the event control and zero increment remain provisional pending organizer confirmation.
- All previously recorded `10+0` and `25+0` fastchess results predate that runner change and used the engine's default `Move Overhead=10` ms. Keep them as historical short screens only; do not compare them as if they used the controller's 1500 ms setting. No new strength run was started in this follow-up.
- The `25+0` record is a 25-second-per-side test, as shown by PGN `TimeControl "25"` and 46–50-second game durations. It did not exercise the tournament control, physical controller/clock, or establish strength.
- A real-runner smoke at `10+0` (`1` thread, `16` MiB, seed `2026100101`) completed 2 games without flags, and `meta.json` confirms `Move Overhead=1500` was sent to both engines. The later source-based budget calculation shows this overhead exhausts Stockfish's initial search horizon at `10+0`; retain the run only as evidence that the option was propagated, not as normal-search, reliability, or strength evidence. Ignored log: `logs/sprt/tm_10+0_r1_s2026100101_20261001-224843.wxv4hP/`.
- Controller failures during a started game now record the rules-defined local forfeit on engine/I/O errors, Ctrl+C, normal `quit`, or restart after a durable `begin` marker; `--resume` refuses that game. A pre-game state is not treated as started until board and clock reconciliation finishes. The low-time move picker now scores one-ply checks, mate, promotions/captures, and moving attacked pieces; these emergency choices are not strength-qualified.
- Final `.venv/bin/python -m pytest controller/tests testing/tests -q -rs` passed **219 tests, 1 skipped in 37.23s**; `bash -n testing/tm_match.sh`, `python3 -m compileall -q controller`, `git diff --check`, and `bash scripts/verify_assets.sh` passed (the single manifest entry matched). The skip is the optional runtime Syzygy integration (`controller/tests/test_runtime.py:52`); the engine binary exists, but no Syzygy set is installed. `almostGlobal run -- ./.venv/bin/python -m pytest controller/tests testing/tests -q` passed at **91/100** (threshold 80): Semgrep reported 0 errors and 2 warnings because `bodyclose` and `sqlclosecheck` are unavailable; resilience was skipped because `DATABASE_URL` is unset.
- The first isolated clean-clone check exposed that the 167 MB UHO testing EPD is ignored by Git and must be prepared separately. `scripts/fetch_openings.sh` restored it in the clone and verified the pinned SHA-256 `7a7f6470615a69c6cf23d565417701d38732876f480af90d67b42abade35644a`; `scripts/verify_assets.sh` then passed. The EPD is test/match data, not needed to start the tournament engine.
- A fresh clone at `c522854` passed `scripts/check_toolchain.sh` and the native Apple Silicon PGO `scripts/build_engine.sh`. The rebuilt engine passed offline `uci`/`isready` (`uciok`, `readyok`) and the deterministic bench (`2,497,913` nodes). Binary SHA-256: `befaea7fa522ac45cdad1827eb81220e19e46731c04d992096b0603f137882ab`.
- The full suite from that clone passed **219 tests, 1 skipped in 40.96s**. It used the existing Python 3.12 virtualenv while running tests from the clone; the skip is the optional Syzygy integration because no tablebases are installed. The clone and build evidence remain under `/tmp/youloss-qual.kW9Ygn` on this machine.
- The clean-clone build ran on battery (46% at build completion); no sustained thermal/profile run was performed. Physical-clock rehearsal and organizer response remain open, and no message was sent.

## 2026-10-02 full-control simulation follow-up

- A paired-color engine-only `1500+0` simulation completed from the clean-clone PGO binary built at `c522854` (SHA-256 `befaea7fa522ac45cdad1827eb81220e19e46731c04d992096b0603f137882ab`). Settings: one game pair, 4 threads, 512 MiB hash, 1500 ms move overhead for both engines, seed `2026100199`; fastchess v1.8.2-alpha commit `f618e34540f94f4719ad3817950618dabe441318`; UHO opening SHA-256 `7a7f6470615a69c6cf23d565417701d38732876f480af90d67b42abade35644a`.
- Both games completed in 1:26:24: YoulossTM scored 0 wins, 1 loss, 1 draw (25%). The first game ended by mate; the reverse-color game ended by threefold repetition. There were zero flags and timeouts; fastchess, result checker, and timing-profile checks all exited 0.
- This two-game sample is not strength evidence. The run started on battery and continued on AC after the user plugged in; it is not sustained AC thermal/profile qualification. It did not exercise the controller, physical board, or clock. `1500+0` remains provisional until the organizer confirms the increment.
- Preserved run artifacts: [config.json](docs/evidence/full-control-1500-0-20261001-235457/config.json), [match.log](docs/evidence/full-control-1500-0-20261001-235457/match.log), [match.pgn](docs/evidence/full-control-1500-0-20261001-235457/match.pgn), and [meta.json](docs/evidence/full-control-1500-0-20261001-235457/meta.json).

## 2026-10-02 8-thread profile follow-up

- A two-pass depth-12 benchmark screen covered Threads 4/6/8 and Hash 512/1024/2048 MiB on the same clean-clone PGO binary. At 512 MiB, mean throughput was 2.39M, 3.46M, and 3.92M nodes/s respectively; peak benchmark RSS was about 889, 1025, and 1034 MiB. The 8-thread/512-MiB combination led this shallow screen, narrowly ahead of 8/1024. This is a throughput screen, not strength evidence or a frozen tournament profile.
- A paired-color full-control simulation at `1500+0`, 8 threads / 512 MiB, 1500 ms move overhead, seed `2026100208`, completed in 1:25:41: 2 draws (threefold repetition; insufficient mating material), zero flags/timeouts. fastchess, log checker, and timing-profile exits were all 0. The runner’s sample Elo output is meaningless for two all-draw games; no strength conclusion follows.
- Continuous system samples covered 85:44. The run began on AC at 85%, then the adapter disconnected around minute 24; it continued on battery and finished at 86%. macOS recorded no thermal, performance, or CPU-power warning. Memory-pressure free percentage was 36% at start and 45% at finish; matched runner/engine RSS peaked around 1.6 GiB. Swap allocation rose from 21 GiB to a maximum of 23 GiB; usage peaked at 22.3 GiB and ended at 21.6 GiB. `powermetrics` could not run without superuser access, so direct temperature and CPU-package power were not measured. This is mixed-power operational evidence, not AC-only thermal qualification.
- This run did not exercise the controller, physical board, or clock, and `1500+0` remains provisional pending organizer confirmation. Keep 8/512 as a measured candidate; do not freeze the profile or claim strength from these results.
- Preserved evidence: [config.json](docs/evidence/full-control-1500-0-20261002-8t512/config.json), [match.log](docs/evidence/full-control-1500-0-20261002-8t512/match.log), [match.pgn](docs/evidence/full-control-1500-0-20261002-8t512/match.pgn), [meta.json](docs/evidence/full-control-1500-0-20261002-8t512/meta.json), [profile-screen.json](docs/evidence/full-control-1500-0-20261002-8t512/profile-screen.json), and [hardware-samples.jsonl](docs/evidence/full-control-1500-0-20261002-8t512/hardware-samples.jsonl).

## 2026-10-02 exact pushed-source build verification

- Verified a fresh clone at `d62d0402e8560d9ea0df3e60f499fdb4a65fecde`, matching both local `HEAD` and `origin/victor`. `bash scripts/check_toolchain.sh` and the Apple Silicon PGO `bash scripts/build_engine.sh` passed.
- The rebuilt `bin/youloss` is 100,006,392 bytes with SHA-256 `07114ae47f7a9e6139425b01086b89a0b9203998ff4f9f76024c43f95346a301`. Offline `uci`/`isready` returned `uciok`/`readyok`; two captured bench runs each searched `2,497,913` nodes.
- On this exact source state, `.venv/bin/python -m pytest controller/tests testing/tests -q` passed **219 tests, 1 skipped in 38.18s**. The optional Syzygy integration is the skip because no tablebases are installed. `bash scripts/test_engine_tm.sh` passed; `bash scripts/verify_assets.sh` verified the one local manifest entry; shell syntax and controller `compileall` checks passed.
- The verification ran on battery (84% before, 83% after the checks). No direct temperature or CPU-package power data was collected. Build correctness is verified; this does not qualify thermals, physical-clock operation, strength, or the packaged release/rollback artifact.
- Build and command logs are retained locally under `/tmp/youloss-clean-verify.Ed07T9`; the clean clone and binary are not committed.

## 2026-10-02 scaled-control timing and harness follow-up

- The overnight screen ran 24 paired-color batches (240 games total) at `60+0`, 8 threads, Hash 512 MiB, and `Move Overhead=1500` ms for both engines. The aggregate was 227 wins, 0 losses, 13 draws for YoulossTM. Every batch runner, checker, and timing-profile command exited 0, but this is **invalid strength evidence**: Stockfish's initial time-manager budget is `base + increment * (mtg - 1) - overhead * (2 + mtg)`. With no moves-to-go, `mtg=50`, so 1500 ms overhead reserves 78 seconds from a 60-second control and reduces the baseline search budget to 1 ms. The first batch profile confirms the distortion: baseline averaged 0.003 seconds per move in moves 1–10, versus 1.354 seconds for YoulossTM. Exclude all 240 games from strength comparisons. Local artifacts: `logs/sprt/tm_60+0_r5_s2026100209_*` through `tm_60+0_r5_s2026100232_*`.
- A corrected 20-game diagnostic at `60+0`, 8 threads / 512 MiB, 60 ms overhead, seed `2026100244`, reached 15 games before its configured 1800-second wall cap. The harness timed it out, rejected the incomplete result summary, and preserved the partial PGN. Its timing profile showed ordinary search on both engines (moves 1–10: `sf` 2.437 s/move, `tm` 1.569 s/move), with no flags among completed games. It is incomplete diagnostic data, not a result or strength claim. Local run: `logs/sprt/tm_60+0_r10_s2026100244_20261002-162127.92C3vm/`.
- A bounded corrected smoke then completed 4 paired-color games with the same 8-thread / 512-MiB profile and 60 ms overhead, seed `2026100245`, in 7:32. Result: 2 wins, 2 losses, 0 draws for YoulossTM; checker and timing profile passed, with no flags. First-10-move timing was 1.065 s/move (`tm`) and 1.597 s/move (`sf`). This verifies normal matched search and harness completion only; four games are not strength evidence. Local run: `logs/sprt/tm_60+0_r2_s2026100245_20261002-165218.pOKrFa/`.
- `testing/tm_match.sh` now preflights simple numeric `base+increment` controls against Stockfish's initial time-management horizon and rejects overhead that consumes that budget. Regression tests cover rejection of `60+0` / 1500 ms and `10+0.1` / 1500 ms, plus acceptance of calibrated `60+0` / 60 ms and provisional `1500+0` / 1500 ms. Other fastchess time-control syntaxes are outside this specific static check.
- Post-change verification: focused harness tests passed **46/46**; the full `controller/tests testing/tests` suite passed **223 tests, 1 skipped in 39.73s**. The skip is the optional Syzygy integration because no tablebases are installed. `bash -n testing/tm_match.sh` and `git diff --check` passed.

## Remaining work, in priority order

1. Request organizer clarification of: clock increment and exact hands-on protocol; local book/tablebase/ponder policy; illegal-move and draw handling; qualifying-round count, knockout bracket, and venue; whether the documented YoulossTM algorithm meets the significant-modification criterion; and the exact Git submission/validation procedure. The PDF already confirms Nov 4 email submission to `icev@somosicev.com`, 25 minutes per player, and losses on flag or software failure. No message has been sent.
2. Measure the provisional 2.0-second operator latency and rehearse physical-board operation with the actual clock: low-time recovery, corrections, promotion, draw handling, resume reconciliation, clock corrections, and fault injection.
3. Select the M4 thread/hash profile from sustained, AC-powered thermals, throughput, latency, memory pressure, and swap measurements. Existing 1-thread/16-MiB and 4-thread/512-MiB runs are short screens, not sustained profile evidence.
4. Before a strength study, freeze the binary, options, and opening holdout, then preregister paired-color sample size, stopping/acceptance rules, and compute budget. Keep failed and inconclusive outcomes. No accepted SPRT or strength conclusion exists.
5. Complete release readiness: package the controller, Python dependencies, engine, and permitted runtime assets; verify offline startup from that exact archive; prepare and test a rollback artifact; and finish the license/provenance review. The clean-clone PGO build, engine smoke, deterministic bench, and full test suite now match the exact pushed source at `d62d040` (verification above). The GPLv3 text, Stockfish origin commit, and current YoulossTM algorithm summary are present. The pinned runner remains `v1.8.2-alpha`, still marked Latest on the [upstream release list](https://github.com/Disservin/fastchess/releases) when checked on 2026-10-01; all listed versions are alpha. Do not use it for a strength conclusion without explicitly accepting that limitation.
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

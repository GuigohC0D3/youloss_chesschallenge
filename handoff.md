# Youloss Chess Challenge — Handoff

## 2026-11-04 — YoulossTM de volta, livro de aberturas (mais recente)

- A pedido do dono, o engine voltou a ser modificado: `sf_19` + YoulossTM. Ver `engine/ORIGIN.md`.
- `assets/book.bin` entra no pacote, checado por `scripts/vet_opening_book.py`.
- `testing/tournament_soak.py` simula um dia de torneio.

## 2026-11-03 — projeto migrado para Stockfish 19 puro

- `engine/` agora é o `sf_19` oficial sem modificações (bench 2497913). O YoulossTM saiu;
  a bancada foi para `archive/youloss-tm/`. O SPRT S2 e o restante do plano abaixo foram
  abandonados, e tudo que vem depois desta seção é histórico.
- Interface nova: `controller/web.py` + `web_ui.html`. Operação no `README.md`.
- Pendente: confirmar com a organização se Stockfish sem modificações é aceito, rodar
  `--dry-run` no M4 e ensaiar com relógio físico.

## 2026-10-07 update — devbrain port complete, M5 handoff (newest)

- **Read `docs/evidence/2026-10-07-m5-project-handoff.md` first** — it is the complete
  status/runbook for the next operator (M5 machine): setup, verification, battery launch
  commands, gotchas, and evidence index.
- Branch `sprint1-sfdev-adopt` (base `05f03f6` from `victor`): Stockfish `dev-20260930`
  brain ported into `engine/src` (39 files) with all six YoulossTM hooks re-wired;
  `bin/youloss_devport` builds with bench **1,714,434** = official dev prebuilt; frozen
  `bin/youloss` untouched (bench 2,497,913, SHA-256 `c5ae7908…`).
- Gates at handoff: full suite **335 passed**, `OK: youloss_tm`, frozen SHA verified.
- Preregistration locked before any counted game
  (`docs/evidence/2026-10-06-devbrain-preregistration.md`): S2 ≥55% vs frozen, S1 ≥55% vs
  official dev, S3 ≥50% vs official sf19, n=400 each, paired bootstrap CIs,
  `Termination=normal` only. **Zero games counted so far** — all batches were rejected by
  environment safeguards (AC loss ×1, clamshell sleep ×2, manual cancel ×1); fail-closed
  behaved correctly each time.
- Harness kill-path bug fixed (bash `exec` dropped the verification token from argv,
  orphaning matches past SAFETY_STOP): ancestry-based verification + regression test;
  wrong-token/unrelated-PID refusal pins still green. `stop` was then proven live.
- User cancelled the final battery screen to protect the dev Mac; the AC auto-relaunch
  watcher was removed. Next action is on the M5 under AC: Section 5 (setup) → Section 6
  (launch S2) of the M5 handoff doc.

## 2026-10-05 update — FallMax screen and next study

- The preregistered FallMax 2.25 versus 2.0 screen completed **100 games / 50 color-swapped opening pairs** at `10+0.1`, Threads=1, Hash=128 MiB, Move Overhead=10 ms, concurrency=1, Syzygy off. Candidate result: **29W/47D/24L, 52.5%**. Paired-opening *t* 95% CI: **47.69%–57.31%**, so the result is inconclusive and does not support a tuning or strength claim. Keep 2.25 experimental. Evidence: `docs/evidence/2026-10-05-fallmax-2.0-vs-2.25-results.md`; full preregistration and run hash in `docs/evidence/2026-10-05-fallmax-2.0-vs-2.25-preregistration.md`.
- Fastchess, fail-closed checker, and time profiler passed; all 100 PGNs parsed and the 50 color pairs shared starting FENs. Candidate/control timing and depth were nearly equal. Score-drop counts are unverified telemetry proxies, not adjudicated blunders.
- Resource log `/tmp/scratchpad/youloss-fallmax-study-screen-20261005T045711Z.jsonl`: AC throughout that run; battery 72%–99% charging; maximum swap 885.5 MiB / 2,048 MiB. The run finished in 54m32s.
- A separate same-binary YoulossTM on/off study is preregistered with fresh seeds (`2026100504` wiring smoke, excluded; `2026100503` scored 100 games). It tests the custom manager against Stockfish's stock time manager and cannot be pooled with the FallMax comparison. No games in this study have started.
- The machine currently reports Battery Power at 99%, with swap at 885.5 MiB. An AC-gated supervisor is active as PID 98412, logging to `/tmp/scratchpad/youloss-tm-onoff-ac-supervisor.jsonl`; it waits for AC, then runs the smoke and fixed screen. Battery floor is 20%, swap ceiling 1,536 MiB, and each active match aborts on AC loss or telemetry failure. It checks the wait state every 20 seconds and records 20-minute progress events.
- The current checkout remains dirty on branch `victor`; no commit or push was made. Existing code verification before these documentation updates: full suite **333 passed**, both isolated PGO binaries returned 2,497,913 bench nodes and passed UCI readiness. The new on/off screen will record its own checks when it starts.
- Next: keep monitoring the AC-gated supervisor; review the fixed on/off sample only after completion; advance or reject the time-manager change according to its preregistered interval. Do not interpret this as neural-network training or proof of maximum possible strength.

## 2026-10-04 audit correction and current screening evidence (newest)

- Reprocessed the available match directories with the hardened analyzer: **200 runs inspected, 8 valid configuration partitions, 33 excluded runs**. Paired scoring matches only color-swapped games with the same round and starting FEN. The approximate normal interval is withheld below 30 pairs or when observed pair variance is zero.
- Current candidate (`c5ae79086977`) versus the logged Stockfish 19 baseline (`8eed61129d14`): **470 games**, 111W/248D/111L, 235 paired openings, **50.00%**, approximate paired 95% interval **47.77–52.23%**. This shows parity within this sample; it does not establish superiority. Baseline is the verified official `official-stockfish/Stockfish` `sf_19` release-artifact binary (archive SHA-256 `a1f0e3bcc5a6927a11fe6fc8e54a779754645f3c2bae2cf13420fd1957adaa77`, tag resolves to source commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d`; extracted binary matches exactly); it was not locally rebuilt from source.
- Current candidate YoulossTM on/off: **90 games**, 22W/43D/25L, 45 pairs, **48.33%**, interval **43.08–53.59%**; inconclusive. Historical FallMax 2.25 vs 2.0: **140 games**, 34W/70D/36L, 70 pairs, **49.29%**, interval **45.98–52.59%**; no demonstrated gain. Keep 2.25 experimental.
- Older same-binary TM on/off build (`73346ba86938`): **1,010 games**, 230W/511D/269L, 505 unique paired openings, **48.07%**, interval **46.55–49.59%** under `10+0.1`, Threads=1, Hash=128. This suggests a small disadvantage for that older build/profile; it is not the current candidate and should not be projected onto it.
- The archived scoreboard records **105 completed batches / 1,050 games** from Oct 2 23:55 to Oct 3 14:55 local time. W/D/L totals are 236/532/282 = 502 points, or **47.81%**. Earlier session claims of 1,405 games and 56.47% are not supported by these repository artifacts. Legacy `points`/`score_pct` fields were stale (16.5/41.25%) and have been reconciled; `testing/continuous_screening.sh` now recalculates them after successful or failed batches.
- Game review found that mate scores had been converted to ±10,000 cp and counted as centipawn drops. Mate values are now excluded and break the comparison chain. Score-drop proxies remain descriptive and no longer trigger tuning recommendations.
- Verification after these changes: analyzer tests **21 passed**; final full suite **322 passed, 0 skipped** after the small-sample interval guard. Ruff, shell syntax, and diff checks passed.
- Brief local throughput screen: two fixed-node sweeps at Hash=512 MiB, 100,000 nodes per default benchmark position, with thread counts in ascending and descending order. Mean observed NPS: Threads 1=0.922M, 2=2.203M, 4=3.164M, 6=4.212M, 8=4.631M, 10=5.080M. Ten threads was about 9.7% faster than eight in this short run. This is throughput evidence only, not a strength or sustained-thermal result. `pmset -g therm` recorded no thermal/performance warning; no match is running.
- Host last checked at 44% battery, discharging, swap 901.5/2,048 MiB. Defer long engine runs until AC power and lid-open operation. Next: use AC for a preregistered hardware-profile screen and independent validation. Do not claim a strength gain or “peak” from the current screens. No commit or push was requested.
- 2026-10-04 upstream dev smoke: official `stockfish-dev-20260930-49ea5ded` macOS universal binary staged only in `/tmp/youloss-upstream-stockfish-dev/` passed UCI/bench smoke alongside `bin/youloss`; no match started, no source/build changes. See `docs/evidence/2026-10-04-upstream-dev-smoke.md`.

## 2026-10-04 post-review correction: match tablebase configuration (newest)

- **Game-log review:** The 100-game Stockfish 19 screen scored 18W/56D/26L (46.0%); its paired 95% interval includes 50%. The nine accepted YoulossTM on/off batches scored 22W/43D/25L (48.33%); the tenth batch was rejected after macOS clamshell sleep. The 140-game FallMax 2.25 vs 2.0 partition scored 34W/70D/36L (49.29%). These are exploratory and inconclusive; do not infer a strength gain or tune from the earlier score-drop proxy alone.
- **Tablebase finding:** The 290 local Syzygy files were not sent to either engine in the historical screening runs (`meta.json` predates tablebase fields). Retrospective Syzygy probes at the first candidate-to-move position with five or fewer pieces found WDL loss in every probed candidate loss: Stockfish 19 screen 18/18, YoulossTM on/off 16/16, and FallMax screen 29/29 (63 positions total). This shows none of those losses reached a probeable five-piece position where the candidate could still draw or win. It does not identify the earlier cause or prove the exchanges were forced.
- **Move review:** A bounded fixed-node follow-up examined 22 candidate moves that entered tablebase-lost positions. Large PGN evaluation jumps in some examples were mate scores in positions already evaluated at -11.49 pawns or mate in 20 before the move; they are not verified blunders. The review did not establish an alternate line that saves a game, so it does not support another parameter change.
- **Harness correction:** `testing/tm_match.sh` now supports an explicit `SYZYGY_PATH` opt-in and passes the same path plus `SyzygyProbeLimit=5` to both engines. It records table counts and a fingerprint in `meta.json`, rejects unpaired WDL/DTZ files, and leaves tablebases off by default while event permission is unresolved. Previous tablebase-free scores must remain a separate configuration from future tablebase-enabled runs. See `docs/strength-experiment-protocol.md`.
- **Verification:** `pytest controller/tests testing/tests -q -rs`: **317 passed, 0 skipped**; `bash scripts/test_engine_tm.sh`: passed; `bash scripts/verify_assets.sh`: all **291 manifest entries** verified. The real-engine Syzygy integration test completed with `tbhits > 0`; a direct UCI path/probe-limit handshake returned `readyok`. New harness regressions cover symmetric tablebase options, metadata, explicit disable, incomplete pairs, and external table directories.
- **Current boundary:** No new match was started. At the latest check the host was on battery at 51%, swap used 909.5 MiB / 2,048 MiB, so defer long comparisons until AC power with the lid open. Keep `FallMax=2.25` experimental; the 140-game screen does not separate it from the 2.0 baseline. Next work is a preregistered 2.0-vs-2.25 paired study with a fixed profile and independent validation, followed by fixed-depth review of the losses that were already decided before the tablebase range.

## 2026-10-04 YoulossTM on/off same-binary screening abort record and diagnosis

- **Session closeout & outcome:** Bounded same-binary YoulossTM on/off screening session (`logs/screening/tm-on-off-fallmax225-20261004`, preregistered in `docs/evidence/2026-10-04-youloss-tm-on-off-screen.md`) aborted at 9/10 validated batches (90 games) after batch 10 failed validation and was rejected.
- **Nine-batch descriptive score:** 90 validated games (`scoreboard.json`): 22 YoulossTM (`tm`) wins, 25 TM-off (`sf`) wins, 43 draws, 0 incidents. Descriptive paired score: (22 + 43/2) / 90 = **48.33%**. This sample is incomplete and exploratory; it warrants no strength or tuning conclusion, and no unregistered extension was made. The scoreboard excludes the rejected tenth batch.
- **Batch 10 rejection & causal diagnosis:**
  - Artifacts: `logs/sprt/tm_10+0.1_r5_s1791153659_20261004-194101.dT8u02/` (`match.log`, `match.pgn`, `meta.json`).
  - Failure: In batch 10 game 1, the TM-off `sf` side returned `Kh8` after 388.477s, losing on time by 382441ms. The run checker rejected batch 10 and the supervisor aborted cleanly.
  - Diagnosis: Independent OS evidence from `pmset -g log` confirms host clamshell sleep: `2026-10-04 19:41:13 -0300 Sleep Entering Sleep state due to 'Clamshell Sleep' ... Using Batt (Charge:59%) 388 secs`, waking at `19:47:41` on lid-open/user activity. The 388-second duration aligns exactly with the 388.477s move delay. Although the supervisor ran under `caffeinate -s`, it was configured with `REQUIRE_AC=0` for user-authorized battery screening, allowing the Mac to sleep when the lid closed. This is host clamshell sleep, not an engine search bug. Run artifacts and PGN are preserved, but not counted as a valid score.
- **Host telemetry & process status at stop:** Battery 58%, swap used 909.5 MiB / 2,048 MiB total (1,138.5 MiB free swap). No engine, match, or supervisor process remains active. The requested 20 GB swap threshold was impossible on the 2 GiB host; the 1,536 MiB used cap and 512 MiB free floor safely governed swap.
- **Next attempt gate:** AC power required (`REQUIRE_AC=1` or connected charger) and the Mac lid must remain open. Do not disable or bypass the safety gate.

## 2026-10-04 Youloss vs Stockfish 19 100-game screening closeout and diagnostic scope correction

- **Session closeout & outcome:** Completed the preregistered 100-game exploratory screening session (`logs/screening/sf19-100game-20261004T180342Z`) of Youloss vs the local Stockfish 19 baseline binary (`/tmp/youloss-benchmark/stockfish/stockfish-macos-universal`, SHA-256 `8eed61129d1493c5d1f2fd9323f0c54c47ac49319911fbde18c6b9c87e8b13c5`). Fixed 100 games across 50 opening/color pairs in 10 batches. All 10 batches fully validated.
- **Match score & paired analysis:**
  - Games: 100 (18 wins, 26 losses, 56 draws; 46.0 points, **46.0%** score).
  - Pair-cluster mean: **46.00%**.
  - Paired *t* 95% confidence interval: **40.95% – 51.05%** (computed from the 50 same-opening color-swapped pairs).
  - No incidents or time flags (`incidents: []`).
- **Match parameters:** TC `10+0.1`, Threads=1, Hash=128 MiB, Move Overhead=10 ms, concurrency=1 (one match at a time).
- **Host environment & telemetry:** Battery was 97% at launch and 87% at completion; swap was 973.5 MiB used / 2,048 MiB total at both launch and completion checks; no macOS thermal or performance warning. Run logs are in ignored `logs/sprt/tm_10+0.1_*` and session outputs in `logs/screening/sf19-100game-20261004T180342Z`.
- **Diagnostic scope fix:** Updated `testing/analyze_screening.py` and `testing/continuous_screening.sh` so a session's automatic diagnostics analyzes exactly the completed run directories listed in that session's scoreboard (via `--scoreboard`), preserving the general explicit `--sprt-dir` behavior for standalone/global analysis. Regenerated session diagnostics at `logs/screening/sf19-100game-20261004T180342Z`: exactly 10 run dirs inspected, one valid configuration partition, zero excluded (superseding the earlier incorrect global scan of 190 inspected / 32 excluded). Focused unit tests verify exclusion of unrelated historical runs and fail-closed handling for missing or invalid listed runs.
- **Conclusions:**
  - This is a `10+0.1` exploratory screen against the verified official Stockfish 19 release-artifact binary (`sf_19`; extracted binary SHA-256 `8eed61129d1493c5d1f2fd9323f0c54c47ac49319911fbde18c6b9c87e8b13c5`); it was not locally rebuilt from source.
  - The score interval includes 50% (paired *t* 95% interval 40.95%–51.05%), establishing neither superiority nor inferiority.
  - This experiment does not isolate the effect of `FallMax=2.25`.
  - The tested engine is frozen for now; the next useful experiment is a preregistered paired A/B comparing otherwise identical `FallMax 2.0` and `FallMax 2.25` builds on this host with fixed options/openings and disjoint seeds. No new match is started and no engine parameters are changed.
- **Worktree state:** No commit or push performed.

## 2026-10-04 current status and screening addendum

- **Branch and worktree state:** Branch `victor`, HEAD `05f03f6` (equal to `origin/victor` at last check). Substantial staged, unstaged, and untracked changes remain in the checkout; nothing is committed or pushed in this update.
- **Verification status:** Full test suite passed with **302 passed in 49.70s** (0 skips); `bash scripts/test_engine_tm.sh` passed (`OK: youloss_tm`). Shell syntax and staged/unstaged diff checks pass cleanly. Ruff check and format pass across the codebase (including two newly formatted analyzer/screening test files). Focused analyzer and continuous-screening tests: 45 passed in 38.02s.
- **Syzygy tablebase integrity:** 290 `.rtbw`/`.rtbz` tablebase files (~941 MiB) are present in `assets/syzygy`; `bash scripts/verify_assets.sh` exited 0 (`OK: 291 arquivos conferem com assets/MANIFEST`). The earlier claim that tablebase files were missing locally is superseded and corrected.
- **Engine binary verification:** The current on-disk `bin/youloss` has SHA-256 `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301`, matching the exact candidate engine SHA in the 140-game run metadata. This confirms the identity of the tested binary; do not infer full clean-source reproducibility from filesystem modification times alone.
- **140-game FallMax screening partition:** In a 140-game screen at `60+0`, 1 thread, Hash 128 MiB, Move Overhead 60 ms, FallMax 2.25 scored 34W-70D-36L (49.29% score) against the project's FallMax 2.0 baseline binary. This is inconclusive screening evidence, not proof of strength or Elo improvement.
- **Official Stockfish 19 partition:** 370 games at `10+0.1`, 1 thread, Hash 128 MiB, Move Overhead 10 ms; Youloss scored 93W-192D-85L (51.08%), engine SHA `c5ae79086977`, external baseline SHA `8eed61129d14` (`/tmp/youloss-benchmark/stockfish/stockfish-macos-universal`). This was preliminary screening outside the preregistered protocol and does not constitute an accepted strength conclusion. Match screening evaluates time management and search allocation, not NNUE network training.
- **Tuning split preserved:** Current repository source/index maintains a staged FallMax 2.0 version and an unstaged FallMax 2.25 version (`engine/src/youloss_tm.cpp` and `engine/tests/youloss_tm_test.cpp`). This experimental split is intentionally preserved and not staged or resolved here.
- **Host telemetry & safety gate:** No engine or match process is active. The host Mac is running on battery at 100% (discharging), with swap usage at ~989.5 MiB used / ~1058.5 MiB free. Because the screening safety gate requires sustained AC power and at least 2,048 MiB of free swap, neither a hardware profile run nor long match execution is complete or safe to launch at this time.
- **External & physical gates:** The organizer clarification draft remains unsent, and physical-board operation/rehearsal remains outstanding. The existing release candidate package must be rebuilt from a reconciled, clean Git source state before tournament submission.

**Next actions in priority order:**
1. Connect AC power and ensure >= 2 GiB free swap before resuming any match processes.
2. Reconcile and freeze the exact candidate parameters (`FallMax` 2.0 vs 2.25) and engine binary.
3. Predeclare and execute an independent, paired strength study using fresh opening sequences against the pinned Stockfish 19 reference binary.
4. Run sustained AC-powered thread/hash thermal profiling (fanless M4).
5. Conduct physical-board and clock rehearsal, and obtain written organizer clarification rulings.
6. Rebuild from clean source and execute full offline release archive verification.

## 2026-10-03 screening evidence correction

This corrects the previous overnight headline, which combined screening counts and telemetry that do not reconcile with the raw `logs/sprt` run metadata. Do not use its 1,415-game, 56.47% result or its hardware/incident claims as qualification evidence.

- **Reanalyzed runs:** `testing/analyze_screening.py` inspected 139 run directories and accepted 4 separate configuration partitions totaling 1,056 games; it excluded 32 runs (25 violate the move-overhead budget policy, 1 timed out, and 6 failed validation or lacked required metadata). The report is `logs/screening/tuning_insights.md`; diagnostics are `logs/screening/diagnostics.json`.
- **Largest comparable partition:** `10+0.1`, Threads=1, Hash=128 MiB, Move Overhead=10 ms: 1,010 games, 230 wins, 511 draws, 269 losses, 48.07% score. This is screening evidence only; it does not establish an Elo change. Other valid partitions used different time controls or settings and must remain separate.
- **Overhead correction:** Historical `60+0`/1,500 ms runs reserved 78,000 ms against a 60,000 ms initial budget, starving Stockfish's search. They are excluded. The analyzer now applies the same conservative 10% initial-budget rule as `testing/tm_match.sh`, with regression coverage for scaled and full tournament controls.
- **Engine tuning:** `FallMax=2.25` is an experimental candidate. The score-change drop count is a proxy, not a verified blunder count, and these mixed historical runs cannot establish that the parameter improves strength. A controlled paired comparison remains necessary.
- **Verification:** `.venv/bin/python -m pytest controller/tests testing/tests -q -rs` passed **291 tests**; `scripts/test_engine_tm.sh` reported `OK: youloss_tm`. The analyzer and test changes are not committed.
- **Screening state and safety:** The continuous supervisor is stopped. At the latest check the Mac was on battery with 1,174.5 MiB free swap, below the configured 2,048 MiB minimum. No new engine match was started; resume only after AC power and the memory preflight both pass.

Syzygy assets, PGO build, and offline-candidate status are recorded in the earlier implementation update below; verify the current manifest and exact release artifact before treating them as a submission build.

## 2026-10-03 implementation and qualification update

The starting point for this update was clean `victor` at `e9cf37a`, synchronized with `origin/victor`. Earlier sections below preserve their historical snapshots and results. This update adds a stricter engine-match preflight, bounded engine stderr incident diagnostics, exact-position emergency move reuse, simulated operator-delay replay, and an offline candidate package. It does not change the Stockfish-derived C++ search or time manager.

- **Controller:** engine stderr is drained into a 100-line/16-KiB tail; engine incidents record failure class, exit code, FEN, clocks, and that tail beside the game log. An incident write failure cannot suppress the tournament terminal software-loss path. Emergency fallback reuses an engine candidate only for the exact current FEN and a still-legal move; otherwise it uses the existing tactical ordering. Tests cover stalls, crashes, large stderr without a newline, low-time recovery, corrections, and candidate invalidation.
- **Clock replay:** `testing/operator_replay.py` uses a virtual clock and fake engine to debit simulated clock reading, UCI entry, piece movement, and clock pressing. It checks search budget against the reported clock and marks output explicitly as simulated. Normal and positive-recovery replays finished with three moves; the confirmed physical-zero replay recorded a flag. Logs, states, and summary are under `docs/evidence/operator-replay-20261003/`. These values are not measurements of the physical board or operators.
- **Experiment preflight & tournament-control simulation:** `testing/tm_match.sh` supports numeric `base+increment` controls, applies a 10% initial-budget overhead policy, and rejects a fixed zero-increment run whose wall cap cannot cover its maximum clock time plus a process buffer. The 10% limit is a conservative experiment policy, not a fairness or strength guarantee. The two-game `10+0` smoke at 4 threads/512 MiB, 10 ms overhead and seed `2026100301` completed in 42 seconds: YoulossTM 0W/1L/1D (wiring evidence only). A separate two-game simulation at provisional `1500+0` (25m+0, 4 threads, 512 MiB Hash, 1500 ms Move Overhead, seed `2026100199`) completed in 01:26:24 without flags, crashes, or timeouts (`exit_fastchess: 0`, `exit_checker: 0`). Game 1: `tm` lost as White (0-1, checkmate at move 80, 45m28s). Game 2: `tm` drew as Black (1/2-1/2, 3-fold repetition at move 77, 40m51s). Score: 0.5/2 (25.0%). This is a small operational smoke only; it cannot establish reliability or strength. Its logs are in a temporary directory and are not part of the reproducible screening dataset. Preserved repo log for the `10+0` smoke: `logs/sprt/tm_10+0_r1_s2026100301_20261003-000551.qzWXeJ/`.
- **Time manager tuning (`youloss_tm`):** In response to the depth deficit observed in the `1500+0` match, parameters were tuned: `HorizonOpening` 45.0 -> 32.0 (increasing early-game allocation from ~33s to ~47s base), `StabilityMin` 0.55 -> 0.70 (preventing premature time reduction on stable root moves), and `FallMax` 1.75 -> 2.0 (deeper defensive search on evaluation decline). C++ unit tests were updated and verified green. Engine recompiled with native Apple Silicon PGO (`bash scripts/build_engine.sh`), preserving exact Stockfish bench search parity at 2,497,913 nodes. Full test suite: **262 passed, 1 skipped**.
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

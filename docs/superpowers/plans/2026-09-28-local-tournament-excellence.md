# Local Tournament Excellence Plan — 2026-09-28

> Status: **in-progress local implementation roadmap**. Implementation, builds, and test verification authorized per closeout brief. It consolidates reviewed evidence into an actionable plan for a local-only tournament on the inspected MacBook.
> Authority: a local copy of the 3-page event PDF, SHA256 `edcec7139d2e6ed48f6b5c43d4dee7990279c21a9e3a38cd475f8e08dc893bcf` (the PDF is not included in this repository). Interpretations are labeled as such. Prior spec/FAQ claims not established by this PDF are superseded design choices, not rules.
> Snapshot: branch `victor`, HEAD `207a0734fd5f135703eff176f41f652c6a680397`, initially clean on 2026-09-28. Three team members assumed (engine, controller/operator, testing/release); identities unassigned. Assumptions: single offline operator station, local logs, no match network, soft compute budget chosen by evidence, role owners unassigned.

> **Snapshot scope:** Sections 1–2 below preserve the initial 2026-09-28 review. Their checkout and blocker descriptions are historical. The verified progress update immediately below is the current status as of 2026-09-30 and supersedes dated claims where they differ.

## 1A. Verified progress update — 2026-09-30

- **Controller:** the tournament default is now documented and implemented as provisional `1500+0`. Physical clock readings are required to recover from an exhausted internal estimate; a physical `00:00` is logged as a confirmed flag. `controller/tests/test_clock_protocol.py` covers delayed input and clock-resync cases. The 2.0-second latency deduction remains provisional and has not been calibrated in operator rehearsals.
- **SPRT parser and match checker:** Python now requires a complete LLR row, a valid nonzero Games summary with reconciled outcomes, and one displayed hundredth beyond the rounded LLR boundary. The shell checker now understands fastchess v1.8.2-alpha's real `Ptnml(0-2)` row, accepts a defined `nan` ratio, and reconciles paired buckets with Games. The actual runner log exposed the old `Penta:` fixture mismatch before the correction.
- **Opening data:** the UHO opening file was fetched before the event and matched the pre-existing manifest SHA-256 `7a7f6470615a69c6cf23d565417701d38732876f480af90d67b42abade35644a`. `scripts/fetch_openings.sh` now verifies that recorded digest and does not rewrite the manifest. `scripts/verify_assets.sh` passed for the one manifest entry. Syzygy and Polyglot books are not present locally; related rule limits remain unconfirmed assumptions.
- **Runner release:** the [upstream release list](https://github.com/Disservin/fastchess/releases), checked 2026-09-30 through GitHub CLI, marks `v1.8.2-alpha` as Latest; the listed releases are alpha builds. The existing commit pin is current, but alpha status remains a reliability limitation.
- **A/B screening run:** fastchess `v1.8.2-alpha`, commit `f618e34540f94f4719ad3817950618dabe441318`, completed 40 paired-color games at `10+0`, one thread, Hash 16 MiB, seed `2026093001`, using the manifest-verified UHO suite. Summary: 10 wins, 12 losses, 18 draws for `tm`; Elo `-17.39 +/- 68.73`; score `47.50%`. No flags or engine incidents; runner, checker and PGN time profile all exited 0 in 12m24s. Time profile averaged 9.02s/game (`tm`) vs 9.31s/game (`sf`). This is a small screen, not an acceptance result: the uncertainty is wide, the time control is scaled, and the options are not a measured tournament profile. Evidence files are under ignored `logs/sprt/tm_10+0_r20_s2026093001_20260930-220620.Wdw0EC/` (`match.log`, `match.pgn`, `meta.json`).
- **Four-thread A/B screen:** 40 paired-color games at `10+0`, four threads, Hash 512 MiB, seed `2026093003`, same engine, runner and UHO opening hash. Result for `tm`: 9 wins, 7 losses, 24 draws; Elo `+17.39 +/- 53.86`; score `52.50%`. Engine time averaged 8.69s/game (`tm`) vs 8.96s/game (`sf`). Runner, checker, and profile all passed in 11m59s; no flags or engine incidents. This remains an inconclusive scaled-control screen, not a tournament profile or evidence of a strength gain. Evidence is under ignored `logs/sprt/tm_10+0_r20_s2026093003_20260930-222758.hJKp75/` (`match.log`, `match.pgn`, `meta.json`).
- **25-second engine smoke (correction):** four paired-color games at fastchess `25+0` means 25 seconds per side and zero increment. The PGN records `TimeControl "25"`; games lasted 46–50 seconds. At four threads, Hash 512 MiB, seed `2026093004`, `tm` scored 2 wins, 0 losses, 2 draws; engine time averaged 23.70s/game vs 24.76s/game (`sf`). Runner, checker, and profile passed in 3m18s, with no flags or engine incidents. This validates only a short engine-to-engine smoke. It did not test the provisional tournament control `1500+0`, manual clock/controller, or strength. `1500+0` interprets the rules' 25 minutes per player; the unspecified increment still needs organizer confirmation. Evidence is under ignored `logs/sprt/tm_25+0_r2_s2026093004_20260930-224146.xZggHp/` (`match.log`, `match.pgn`, `meta.json`).
- **Multi-thread harness path:** `testing/tm_match.sh` now accepts validated `THREADS` and `HASH_MB` environment values and records them in `meta.json`; defaults remain 1 thread and 16 MiB. A two-game paired-color integration run at `10+0`, 4 threads, Hash 512 MiB, seed `2026093002` passed in 42 seconds without incidents. Two games do not qualify the M4 tournament profile.
- **Earlier integration findings:** the first four-game smoke completed without incidents but initially returned wrapper failure because the checker expected `Penta:` rather than pinned fastchess's `Ptnml(0-2)`; it scored 0W/2L/2D for `tm`. After correction, the two-game paired rerun passed end to end (one loss, one draw). Keep both outcomes as validation history; neither establishes strength.
- **Strength / hardware:** no SPRT acceptance or tournament-strength conclusion exists. The 1-thread bench test establishes deterministic node-count parity only. The two 40-game screens are inconclusive, and the four-game 25-second engine smoke does not validate the tournament control or manual-clock operation. The four-thread runs are not sustained thermal tests. No final thread/hash profile or full manual-board rehearsal is recorded.
- **Verification:** `.venv/bin/python -m pytest controller/tests testing/tests -q` passed **205 tests, 1 skipped in 42.58s** after the latest harness change. `bash -n` for changed shell scripts, Python compilation, `git diff --check`, and `bash scripts/verify_assets.sh` all passed.
- **Worktree:** changes are uncommitted on branch `victor`; no commit was requested. `.DS_Store` files are untracked workspace artifacts.

## 1B. Closeout update — 2026-10-01

- **Controller:** estimated-clock expiry is checked before the low-margin fallback; `played` requires a fresh physical reading after estimate expiry; `undo` clears and persists an unplayed first-move proposal.
- **Harness:** `tm_match.sh` rejects a partial SPRT bound pair before creating a run directory or starting fastchess.
- **Verification:** `.venv/bin/python -m pytest controller/tests testing/tests -q` passed **213 tests, 1 skipped in 37.41s**. The two partial-bound regression cases passed in 0.12s, and `git diff --check` passed.
- **Git closeout:** a fresh fetch confirmed `origin/victor` matched the pre-closeout HEAD. The user subsequently authorized organized commits and a push; `.DS_Store` artifacts are excluded from the commits.

## 1C. Clean-clone validation — 2026-10-01

- A detached, clean clone at `c522854` passed the native Apple Silicon PGO build and toolchain check. The rebuilt engine returned `uciok`/`readyok`; its deterministic bench count was `2,497,913` nodes. The binary SHA-256 was `befaea7fa522ac45cdad1827eb81220e19e46731c04d992096b0603f137882ab`.
- The clean clone initially lacked the ignored UHO test EPD. `scripts/fetch_openings.sh` restored it from the pinned source and verified the existing manifest digest; `scripts/verify_assets.sh` then passed. This is test/match data, not required for engine startup.
- The full suite from the clone passed **219 tests, 1 skipped in 40.96s**, using the existing Python 3.12 environment. The skip is the optional Syzygy integration; no tablebase set is installed. The build ran on battery and does not count as sustained thermal qualification.
- **Still open:** AC-powered sustained profile, physical-clock/operator rehearsal, organizer clarification/eligibility acceptance, and a statistically meaningful strength study. Detailed evidence and release gates are in `handoff.md`.

## 1D. Exact pushed-source validation — 2026-10-02

- A fresh clone at `d62d0402e8560d9ea0df3e60f499fdb4a65fecde` matched both local `HEAD` and `origin/victor`. The Apple Silicon toolchain check and PGO source build passed.
- The rebuilt 100,006,392-byte engine has SHA-256 `07114ae47f7a9e6139425b01086b89a0b9203998ff4f9f76024c43f95346a301`; offline UCI returned `uciok`/`readyok`, and two bench runs each searched `2,497,913` nodes.
- The full suite passed **219 tests, 1 skipped in 38.18s**; the optional Syzygy integration is skipped because no tablebases are installed. `scripts/test_engine_tm.sh`, the one-entry local asset manifest check, shell syntax, and controller compile checks also passed.
- Verification ran on battery (84% before, 83% afterward) and did not collect direct temperature or CPU-package power. It verifies a reproducible build, not sustained thermal qualification, playing strength, physical operation, or the final packaged release.
- **Still open:** final offline release/rollback archive, AC-powered sustained profile, physical-clock/operator rehearsal, organizer clarification and eligibility acceptance, and a statistically meaningful strength study.

## 1E. Scaled-control overhead correction — 2026-10-02

- An overnight 240-game screen at `60+0`, 8 threads / 512 MiB, and 1500 ms `Move Overhead` produced 227 wins, 0 losses, and 13 draws for YoulossTM, but is invalid strength evidence. Stockfish reserves `Move Overhead * (2 + mtg)` against its time budget; with `mtg=50`, 1500 ms reserves 78 seconds from a 60-second clock. The first-batch profile showed baseline search at 0.003 seconds per move in moves 1–10 versus 1.354 seconds for YoulossTM. Exclude these results.
- The same calculation invalidates the 2026-10-01 `10+0` / 1500 ms smoke as normal-search evidence; its record is useful only to show option propagation. Older `10+0` and `25+0` screens with the engine's 10 ms default are separate historical runs and remain scaled, non-strength evidence.
- A corrected `60+0` / 60 ms overhead run reached 15 of 20 games before its 1800-second cap. The fail-closed harness rejected the incomplete summary; completed-game timing showed normal search on both engines and no flags. A subsequent four-game paired-color smoke with the same calibrated settings passed the runner, checker, and time profile, with no flags. Both are diagnostic only, not strength results.
- `testing/tm_match.sh` now rejects supported numeric `base+increment` controls when the configured overhead consumes Stockfish's initial time-management horizon. Focused harness tests passed 46/46; the full suite passed **223 tests, 1 skipped in 39.73s**. Tests cover rejection of `60+0` / 1500 ms and `10+0.1` / 1500 ms, and acceptance of `60+0` / 60 ms and provisional `1500+0` / 1500 ms. See the exact runs, timings, and local artifact paths in `handoff.md`.
- **Still open:** a preregistered, correctly budgeted strength study, sustained AC profile qualification, physical-clock rehearsal, and organizer approval.

## 1. Verified baseline

- **Hardware (inspected):** MacBook Air Mac16,12, Apple M4, 10 cores (4 performance + 6 efficiency), 16 GB unified RAM, ~47 GiB SSD free at inspection. Fanless design per [Apple](https://www.apple.com/newsroom/2025/03/apple-introduces-the-new-macbook-air-with-the-m4-chip-and-a-sky-blue-color/). Thread counts do not pin tasks to P cores.
- **Tournament shape (user-confirmed):** local-only on this MacBook, one engine process, physical board, manual clock. No network/API during games; pre-event downloads allowed as preparation; all runtime assets local at the venue.
- **PDF essentials (pages 1–2):** event NOVEMBER 6 2026; team exactly 3 with at least one ICEV student; changes/registration cutoff November 3; scoring 3 points per win and 1 per draw (confirmed page 1 rule); existing AI permitted only with significant algorithm modifications, copies without relevant changes disqualified; Git inspection at any time; Git submission November 4 with validation required; no online software/external APIs during games; teams decide own moves and replicate the opponent's; 25 minutes EACH with no increment stated; physical board and manually managed clock; software failure/crash loses the game. Page 3 includes schedule and organizer questions.
- **Interpreted control:** plan `1500+0` as an explicit interpretation of "25 minutes EACH", pending organizer confirmation. Do not quote `+0` as PDF wording.
- **Engine base:** Stockfish `sf_19` pinned at `edb0d9db6731067ec50ce619ff372b463bc4dd5d` (see `engine/ORIGIN.md`). Current official release per the [Stockfish 19 blog](https://stockfishchess.org/blog/2026/stockfish-19/), not an obsolete base. Existing foundation: UCI-separated Python controller, legal input validation, atomic state saving, logs, Polyglot support, optional Syzygy, pure custom C++ time functions, A/B option, macOS PGO build, fastchess harness.
- **Checkout state:** no `bin/`, `.venv/`, `tools/`, `logs/`, or local asset payloads observed. `assets/MANIFEST` holds only one testing-opening checksum. No tracked accepted SPRT ledger or hardware benchmark. Tests were inspected, NOT executed; claim no results. Some engine tests skip without a binary. File existence is not runtime readiness.
- **Prior-spec caution:** the old spec cites an unavailable FAQ for 15+10, ≤10 book plies, ≤5-piece tablebases, mandatory move-log format, ponder allowed, and an ~October 28 date. None are established by this PDF. Retain conservative 10-ply/5-piece configuration until clarified; do not infer unlimited permission.

## 2. Findings and priorities

Ordered by tournament risk. Relative links resolve from this document to the repo root. Statuses in §1A supersede the original findings below; unresolved gates remain open until their evidence is added.

### BLOCKER 1 — Time control requires organizer confirmation [partially resolved]

- The old `900+10` default is superseded. The controller now defaults to `1500+0`, an interpretation of the PDF's 25 minutes per side, and the A/B harness screen used zero increment.
- Risk: the PDF does not define an increment or fully specify the manual clock procedure.
- Remaining action: obtain written confirmation, then freeze the exact event time control and verify the operator invocation/UCI values against it.
- Gate: confirmed time control; tests show no per-move bonus unless organizers explicitly specify one.

### BLOCKER 2 — Physical-clock accounting and manual latency [partially resolved]

- The controller now separates proposed from physically confirmed moves, requires physical readings during `press`/recovery, and logs confirmed physical flags. Regression tests cover delayed UCI entry and resynchronization.
- Remaining risk: the conservative 2.0-second latency deduction and manual operating procedure are not calibrated with a trained operator on the real clock.
- Remaining action: measure press/input/execute delays and rehearse corrections, promotions, resume reconciliation, and late-clock handling; preserve physical readings and confirmed-vs-proposed state in logs.
- Gate: replayed handling delays do not credit time optimistically; rehearsal logs show consistent state and clock corrections.

### BLOCKER 3 — Search/stop budget and physical-flag handling [partially resolved]

- A zero internal estimate now stops the search and requests a fresh physical reading; a positive reading has the provisional latency deduction, while confirmed physical zero records a flag. A low useful-search margin uses an immediate legal move. Search stop grace is bounded to one second.
- Remaining risk: the timing path is unit/replay tested, not validated against measured operator latency during a 25-minute game. Do not treat the fallback as a guarantee against a physical flag.
- Remaining action: replay injected delays and conduct late-clock drills; keep any physically confirmed expiration as a loss, never clamp it away.
- Gate: search + stop + response stays inside available physical time after measured operator/uncertainty reserve, or the system surfaces expiration.

### HIGH 4 — Fault path and crash behavior [open]

- Current policy follows the PDF: a crash during play loses; `--resume` is diagnostic reconciliation and does not revive that game. The controller records a proposal separately from a physically played move.
- Remaining risk: full fault drills for engine I/O failure, disk failure, interrupted search, and between-game rollback are not recorded.
- Gate: fault drills show no phantom confirmed move and an unambiguous incident record; never auto-restart into an active game.

### HIGH 5 — Empirical strength unknown; custom TM unproven

- Anchors: [engine/src/engine.cpp](../../../engine/src/engine.cpp):112 enables `YoulossTM` by default; [engine/src/youloss_tm.cpp](../../../engine/src/youloss_tm.cpp):16-40,44-87 use horizons 45/25 and heuristics with no recorded tuning evidence in this review.
- Risk: custom TM can weaken Stockfish; bench stability is integrity only, not Elo proof. This review found no recorded validation evidence for no-increment long games, low material with many moves, and conversions.
- Action: test current TM vs proposed allocator vs original Stockfish TM under identical options/build, with paired color-balanced games, ablations, and holdout openings.
- Gate: preregistered comparative evidence under no increment; failed/inconclusive reported as such, never as gains.

### HIGH 6 — Harness acceptance integrity [partially resolved]

- `tm_match.sh` now captures both output streams, verifies the runner sidecar and engine/book hashes, uses unique run directories and seeds, calls the fail-closed checker, and stores run metadata. A real smoke exposed that the checker expected `Penta:` while the pinned runner prints `Ptnml(0-2)`; the parser and fixture now match the pinned source/output.
- Remaining risk: `v1.8.2-alpha` is still an alpha pin; the checked run uses 1 thread and Hash 16 MiB, not a validated tournament profile. No statistical acceptance run exists.
- Gate: all incidents/incomplete output fail; use a reviewed runner version and publish full run records before accepting any strength result.

### HIGH 7 — Default threads/memory unvalidated on fanless M4

- Anchor: [controller/runtime.py](../../../controller/runtime.py):65-69 defaults to nine threads and half estimated free RAM; telemetry/parsing sits outside the main runtime exception handler.
- Risk: sustained throttling differs from brief peaks; telemetry failure can break preflight.
- Action: stage sustained measurements, freeze one tournament profile, preflight telemetry defensively. Play plugged in, lid open, cool stable placement, sleep prevented, background sync/workers stopped; log battery/AC settings.
- Gate: frozen threads/hash justified by 30–60 min and multi-game evidence; no impairing swap growth; thermal, latency, and pressure deltas logged.

### MEDIUM 8 — Ponder, knobs, Syzygy, offline readiness

- Anchors: [controller/engine_client.py](../../../controller/engine_client.py) reads ponder hints but `Game` has no `go ponder`/`ponderhit` path; `has_syzygy` checks a single `.rtbw`; manifests do not establish complete assets; startup/build must not need venue network.
- Risk: dead optional-gain paths, incomplete tablebase sets mistaken for complete, late discovery of network dependence.
- Action: keep ponder off until permission plus a qualified state machine (hit/miss/stale-bestmove/stop/undo/clock-correction) and thermal-inclusive A/B. Vet a small local book vs no book on held-out openings; keep complete local 3–5 piece WDL+DTZ with checksums and 50-move handling. Defer six-piece subsets until permission, disk budget, and proven benefit align. Verify offline startup from clean clone with local dependencies.
- Gate: offline startup proven; asset manifest complete with checksums; ponder off unless qualified and permitted.

## 3. Route comparison

- **A (recommended): keep pinned SF19 search+NNUE; evolve tested physical-clock-aware custom allocator/controller.** Lowest regression exposure, fixes the blockers directly, preserves a credible original contribution. Fits hardware and calendar with disciplined evidence.
- **B: broader TM/search rewrites.** Research upside but far more compute/regression exposure on one shared fanless machine; risks weakening a strong base without games to prove gain. Bounded follow-ups only if A regresses.
- **C: alternative engine, GPU inference, or NNUE training.** Needs a separate benchmark track; poor near-term return here. SF19 CPU gains nothing automatically from Apple GPU/ANE. UI/packaging alone is not algorithm originality.
- Objective (no victory promise): highest demonstrated local strength among compliant candidates with incident-free operation and credible original contribution.

## 4. Time and interaction design

Physical clock is authoritative. Required states: setup, ready, our-search, move-proposed, physical-move-confirmed, opponent-turn, input-correction, game-over, fault. Handle promotion, castling, en passant, repetition/50-move claim eligibility vs automatic endings, corrections, and history loss after FEN edits. Minimal terminal UI with large move (UCI+SAN), board, and clock suffices; add a visual board only if it measurably cuts errors. Support safe correction/stop during search with no unbounded blocking, no arbitrary fallback, and transparent incident reporting. Record physical readings, timestamps, suggested vs confirmed moves, and latency.

## 5. Original algorithm proposal

Build an empirically calibrated remaining-move horizon for sudden death, reserving time for future physical execution (measured conservative latency), manual-clock sync uncertainty, and bounded complexity/stability/search-iteration evidence. Inputs observable during play only. Separate search reserve, operator time, and clock estimation; internal eval units are not literal pawns. Compare current TM, proposed allocator, and original Stockfish TM under identical options/build with a small bounded parameter set, ablations, and holdout openings. An optional constrained adjustment around the original allocation is the fallback experiment if the full replacement regresses — but any fallback still needs organizer-accepted significant modifications; plain Stockfish with originality off is not automatically legal. Package pseudocode, exact diff vs pinned upstream, measured behavior, positive and negative experiments, contributor explanations, and GPL/source/dependency/asset provenance. Claim no acceptance without validation.

## 6. Hardware experiment

PGO native ARM64; preserve the validated original binary. Stage threads 1 (baseline), then 4/6/8/9/10; then Hash 512/1024/2048 MiB, with 4096 only if pressure/swap data and benefit justify it. No full Cartesian product: threads first, then hash, then finalists under sustained 30–60 min and multi-game sessions. Log sustained throughput/search quality, move latency, memory pressure/swap deltas, thermal behavior, and accessible energy counters; capture battery/AC settings. Four threads does not guarantee P-core-only execution. Use MultiPV1/full strength per the [Stockfish FAQ](https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html) (CPU evaluation). Select sustained reliability, not brief NPS peaks.

## 7. Assets and ponder

Qualify a small local vetted book vs no book on held-out openings; do not confuse UHO testing EPDs with playable Polyglot books. Start from complete local 3–5 piece WDL+DTZ with checksums and verified 50-move handling. Six-piece subsets only after permission, measured disk budget on ~47 GiB free, and proven benefit — never blanket 7-piece downloads. Ponder stays default-off until clarification, a reliable state machine, hit/miss/stale/stop/undo/clock-correction tests, and thermal-inclusive A/B.

## 8. Evidence strategy

Start from a reproducible native build and focused test inventory; infer no global result from skipped binary tests. Cover pinned bench `2497913`, UCI integration, fake-engine delays/stalls/invalid output, and actual engine clock behavior, plus synthetic 100+ move games and low-clock/adversarial input timing with no accidental increment — injection must surface loss, not hide it. Require paired openings alternating colors, equal hash/threads/options, fresh unique metadata with hashes/seeds, and full stdout+stderr. Progress `10+0` screening → `60+0` → `180+0` → `1500+0` rehearsals ([sudden-death TM testing with staged testing](https://official-stockfish.github.io/docs/fishtest-wiki/Creating-my-first-test.html)); do NOT claim increment tests scale to no increment, since fixed overhead/operator latency breaks scaling — scale protocol overhead in engine-only tests and cover physical latency via controller replay at full control. Preregister statistical targets and compute budgets; SPRT only with enough games ([selection bias and uncertainty](https://official-stockfish.github.io/docs/fishtest-wiki/Fishtest-FAQ.html)). Existing `-5/0` and `0/5` bounds are candidates, not guarantees; verify Elo model/version. Report W/D/L plus `(3*W+D)/games` vs representative opponents as a secondary tournament metric reflecting the confirmed 3/1/0 scoring; never use it as an excuse for untested aggression or as a replacement for paired Elo comparison. Pin the runner version and verify `-srand`, openings, and metadata locally ([fastchess](https://github.com/Disservin/fastchess)). Set max games AND wall time, report inconclusive honestly, never restart until passing, stop on genuine incidents, retain all failed trials, and compare full systems (book/ponder/config, representative opponent styles). Several real games demonstrate operation in those samples, not prove operations or Elo. Scale warning: ~1000 full games at up to 50 min each ≈ 833 match-hours (≈278 h even with three concurrent streams, which distort full-strength comparisons on shared hardware) — calibrate durations, budget modest compute, use concurrency 1 for full-thread comparisons.

## 9. Calendar with owners, dependencies, gates (2026)

Each phase requires the prior gate. Roles: engine, controller/operator, testing/release.

- **P0 Sep 28–Oct 2 — Rules, register, baseline.** Owners: controller + release. Register PDF facts, mark superseded assumptions, draft written prevalidation request (user sends), finish baseline build+manifest+test inventory, correct `1500+0` config. The clean-clone PGO build and 219/1 suite were first verified at `c522854` (section 1C), then repeated against exact pushed source `d62d040` on Oct 2 (section 1D); organizer prevalidation and final release packaging remain open. The earlier fastchess `25+0` result was a 25-second-per-side smoke, not an event-control run. Use 1500 ms `Move Overhead` only for the provisional `1500+0` full-control comparison; scaled controls require calibrated overhead, and the harness now rejects a setting that exhausts Stockfish's initial time-management budget. This does not simulate manual-clock latency. A single paired full-control run requires an explicit generous wall cap, for example `MOVE_OVERHEAD_MS=1500 TIME_CAP_S=7200 CONC=1 THREADS=4 HASH_MB=512 bash testing/tm_match.sh 1500+0 1`; it remains provisional pending organizer confirmation. Output: compliance matrix + reproducible baseline. No assumed approval.
- **P1 Oct 3–9 — Clock, watchdog, move handling.** Owner: controller (+ engine deadlines). Build clock/state model, bounded watchdog, reliable handling + regression cases. Gate: no optimistic time, no artificial increment, total search+stop+response <= remaining minus operator/clock-uncertainty reserve (else immediate legal-move path or surfaced expiry, no guarantee), faults surface cleanly.
- **P2 Oct 10–16 — Allocator + fair harness.** Owners: engine + validation. Candidates, telemetry/tuning controls, fail-closed harness; small screened hypothesis set with ablations. Gate: behavior/clock tests + preregistered comparative evidence; failures not reported as gains.
- **P3 Oct 17–23 — M4 tuning + asset qualification.** Owners: validation + engine. Staged sustained tuning, book/tablebase qualification, conditional ponder only after P1; freeze finalists in tournament profile; start full-control rehearsals. Gate: frozen measured threads/hash, assets verified offline, zero incidents, no impairing swap.
- **P4 Oct 24–30 — Operator rehearsal.** The two active contributors run 6 full physical-board games at the confirmed control (3 each color), including a long game and a clock scramble, plus one continuous mock-event session; include the third registered teammate where available. Until confirmed, use provisional `1500+0` as an interpretation of the 25-minute rule. Six games are workload evidence, not Elo evidence. Keep fault/correction drills separate from incident-free games. Candidates must meet originality and evidence gates; do not silently substitute an unqualified engine.
- **P5 Oct 31–Nov 3 — Freeze + release.** Freeze Oct 31; reproducible release from clean clone/local deps; GPL/attribution/provenance + algorithm dossier; offline startup verified; between-game rollback to validated artifact; eligibility locked Nov 3; no worker changes during play. No commit/tag/publish without explicit user request.
- **Nov 4 — Submission.** User sends Git to `icev@somosicev.com` per PDF, captures validation acceptance, clarifies cutoff/post-submission changes. We do not send email.
- **Nov 5 — Final rehearsal** without unapproved changes. **Nov 6 — Tournament** with preflight checklist (power, sleep, placement, background processes, offline assets, clock procedure, rollback artifact).

## 10. Final acceptance

Documented organizer validation/significant-change acceptance; correct clocks/rules (`1500+0` confirmed or amended); native pinned build with offline-complete assets; sustained-evidence profile; zero crashes/illegal moves/forfeits in the finite qualification set (evidence, not guarantee); per-game audit records; honest strength report with uncertainty; trained operators; preserved compliant release artifact. Out of scope: new engine, large NNUE training, remote inference, unrelated GUI/containers/cloud.

## 11. External sources

- Release: [Stockfish 19 blog](https://stockfishchess.org/blog/2026/stockfish-19/) — Sep 5 2026; current SF19; strict FEN/UCI validation can terminate the process.
- Settings/GPU: [Stockfish FAQ](https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html) — MultiPV1, appropriate hash, CPU evaluation.
- Methodology: [Creating my first test](https://official-stockfish.github.io/docs/fishtest-wiki/Creating-my-first-test.html) — sudden-death TM testing with staged testing.
- Statistics: [Fishtest FAQ](https://official-stockfish.github.io/docs/fishtest-wiki/Fishtest-FAQ.html) — selection bias, uncertainty; report inconclusive honestly.
- Runner: [fastchess](https://github.com/Disservin/fastchess) — pin version; verify `-srand`, openings, metadata locally.
- Hardware: [Apple MacBook Air with M4](https://www.apple.com/newsroom/2025/03/apple-introduces-the-new-macbook-air-with-the-m4-chip-and-a-sky-blue-color/) — confirms fanless design.

## 12. Decision log

- PDF is sole authority; FAQ-derived numbers (15+10, book/tablebase caps, ponder, log mandates, October date) are superseded assumptions kept only as conservative config.
- `1500+0` is an interpretation of "25 minutes EACH", not a quotation.
- Route A adopted; B/C deferred for stated reasons. No victory/ranking promise; success is compliant demonstrated strength with incident-free operation.
- Plain Stockfish with originality off is not an accepted silent fallback.

## 13. Unresolved organizer questions

One written prevalidation request; the user sends it. No assumed answers.

1. Confirm 25 min each = `1500+0` and manual-press clock procedure.
2. Reconcile 5 vs four initial rounds; top eight vs round of 16 incl. semifinals; 35-min slots vs 50-min games; best-of-three placement meaning.
3. Define "significant modification" and crash semantics (failure, restart, loss).
4. Permit/forbid books, tablebases (piece/size limits), ponder, with limits.
5. State draw, illegal-move, and clock-handling procedures.
6. State exact Nov 4 submission time, channel beyond listed email, validation criteria, post-submission change policy.

## 14. First three independently assignable tasks

1. **Compliance matrix + baseline (controller/release):** register PDF facts vs superseded claims, correct `1500+0` profile with zero-increment assertion, record reproducible build/manifest/test inventory.
2. **Clock-state slice (controller):** proposal-vs-confirmation states + authoritative resync with per-move latency logging, without changing search budgets; mandatory physical reading on `press <nós mm:ss> [adv mm:ss]`; conservative latency allowance (`DEFAULT_CLOCK_LATENCY_S = 2.0`, `--clock-latency`, validated finite in `[0.0, 60.0]`) deducted on transition; positive physical reading with low margin (below stop grace + operator reserve + minimum useful search) bypasses internal flag inference and forces immediate legal fallback; when latency allowance consumes the reading, clock estimate is floored at 1 second (not 1 ms); exact latency allowance remains a provisional 2.0s open rehearsal-measurement gate.
3. **Fail-closed harness slice (testing):** pin fastchess version/seeds, capture both streams, enforce incident-free evidence, store unique run metadata; injected crash/flag fails the trial.

## 15. Review limitations

Static review only at `207a0734fd5f135703eff176f41f652c6a680397`; no runtime tests performed; no outcomes claimed. Vault pull recorded without blocking assessment: `fatal: Not possible to fast-forward, aborting.`

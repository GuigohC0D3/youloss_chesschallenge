# Stage-2 Handoff Playbook — M5 Machine (friend's box)

**When:** after Stage 1 (devbrain port + S2/S1/S3 screens) is complete and the
candidate is promoted. **Where:** Apple M5, 16 GB RAM, 512 GB disk, ≥400 GB free
for engine work. **Event:** ICEV, Nov 6 2026 (submission by email Nov 4).

Candidate at handoff: `bin/youloss_devport` (Stockfish dev-20260930 brain +
YoulossTM, bench 1714434) — unless the screens failed, in which case handoff
starts from frozen `bin/youloss` (sf_19 brain) and this playbook still applies.

## 0. Ground rules (inherited from spec)

- Bars: any strength claim needs a preregistered screen (write the doc BEFORE
  the first game) with the fail-closed runner, `REQUIRE_AC=1`, lid open,
  `caffeinate -i`, balanced book `testing/openings/balanced_gm_v1.epd`.
- Never commit without the owner's go-ahead; evidence goes in `docs/evidence/`.
- Tournament day ships ONLY: `bin/youloss` + `assets/book.bin` +
  `assets/syzygy/` + `release/launch_youloss.sh`. Corpora, PGO profiles and
  training data never leave the dev machine.

## 1. NNUE retraining (400 GB budget)

Target: a net that beats `nn-252f33942263` head-to-head.

1. **Layout** (16 GB RAM, ~400 GB free):
   - `/data/fens/` — generated training positions (target ≤300 GB)
   - `/data/nets/` — checkpoints (`nn-<sha12>.nnue` naming, verify with
     `shasum -a 256 | cut -c1-12`)
   - `/data/logs/` — loss curves
2. **Data generation**: use the Stockfish dev toolchain in
   `engine/src` (`make net` brings in `nn-252f33942263.nnue`), generate self-play
   FEN data with the candidate binary at ≥16-24 games/parallel, varied openings
   (reuse `testing/openings/balanced_gm_v1.epd` + UHO book), skip first 8 plies,
   filter by eval margin (target: positions with |eval| ≥ 20cp and ≤ 300cp).
3. **Train/holdout split**: 95/5 by position hash (no leakage), holdout never
   seen during training.
4. **Training**: stockfish-nnue (`nnue-py`) workflow; start from a compact net,
   scale width/layers as RAM allows; early-stop on holdout loss; cap wall time
   at 72h per run, keep the best checkpoint.
5. **Acceptance (hard bar)**: preregistered 400-game screen vs the stock
   `nn-252f33942263` build using Section-4 protocol; promote only with
   ≥55% and CI lower bound >50%. A net that only "looks better on loss" is
   NOT promoted.

## 2. SPSA tuning slot (YoulossTM constants)

- Candidates (in `engine/src/youloss_tm.cpp`): `HorizonOpening = 32.0`,
  `StabilityMin = 0.70`, `FallMax = 2.0`. Incumbent = current values = baseline.
- Procedure: standard SPSA (e.g., 200+ iterations, A/c tuning aligned with
  ±0.05..0.5 ranges), each candidate validated by a SHORT screen (40 games,
  10+0.1) before a FULL preregistered screen at 1500+0.
- Promotion precedent: `docs/evidence/2026-10-05-fallmax-2.0-vs-2.25-results.md`
  (52.5%, CI [47.69,57.31] → NOT promoted). A candidate must land with a CI
  that excludes 50% in its favor.

## 3. Release rebuild + final acceptance

1. `scripts/build_offline_release.py` → `dist/youloss-candidate.tar.gz`
2. `scripts/verify_offline_release.py` → 7/7 checks must pass
3. `pytest -q` → full suite green; `scripts/test_engine_tm.sh` → OK
4. Re-run an S3-style acceptance ON THE M5 (same binary, same book/Syzygy/TC)
   as final pre-tournament evidence: score ≥50% vs sf19-official, zero
   losses on time/crash/flag.
5. Operator rehearsal: `scripts/rehearse_operator_game.py` (rc=0, resign path).

## 4. Tournament-day invariant

- Launch: `./launch_youloss.sh --color white --opponent <NAME>` (defaults:
  7 threads / 2048 MiB / 1500+0 / clock-latency 2.0 s — matches the checklist).
- Assets required in working dir: `assets/syzygy/` (290 files), `assets/book.bin`.
- No network, no external APIs (ICEV rules); physical board + operator clocks.
- Rollback: the previous known-good binary keeps its SHA-256 recorded in
  `docs/evidence/`; if the machine misbehaves, swap back before round 1.

## 5. Evidence checklist for the M5 phase

- [ ] Preregistration doc (before first game) + results doc per series
- [ ] SHA-256 of every binary tested, bench values, id lines
- [ ] W/D/L, CI, color split, termination audit (all `normal`)
- [ ] Promotion/rejection decision written down with rationale

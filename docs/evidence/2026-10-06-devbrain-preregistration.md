# Preregistration: devport screens S2 / S1 / S3 (2026-10-06)

Written BEFORE the first game. Changes require an amendment section, never silent edits.

## Candidate
`bin/youloss_devport` (sha256 `5de10e10a18d03f0ef788473b1b89b5fba7928ce7670b77245b3bd4e96d4d518`), id `Stockfish dev-20261003-m-05f03f6e` + YoulossTM option (default true), bench `1714434` (byte-equal search behavior to official dev prebuilt, which also benches 1714434).

## Protocol (all series)
- Runner: `testing/continuous_screening.sh` -> `tm_match.sh` -> fastchess, fail-closed checker unmodified.
- Env: `REQUIRE_AC=1`, `caffeinate -i`, `TC=1500+0`, `THREADS=7`, `CONC=1`, `HASH_MB=2048`,
  `MOVE_OVERHEAD_MS=1500`, `TIME_CAP_S` per preflight (`rounds*4*base+30`), `SYZYGY_PATH=$PWD/assets/syzygy`,
  `BOOK=$PWD/testing/openings/balanced_gm_v1.epd`, `MIN_FREE_SWAP_MB=256`,
  `MIN_FREE_MEM_PCT=10`, `MIN_DISK_MB=500`.
- Counted games: `Termination=normal` only. Any time-forfeit/crash/illegal/stall rejects the
  batch (environment) and is NOT counted as a result.
- CI: paired bootstrap on game scores (win=1, draw=0.5, loss=0), 10000 resamples, 95%.
- One discarded wiring smoke at 10+0.1/Threads2/Hash64/overhead10ms (Task 7 Step 3) is
  explicitly NOT part of any series — different TC, run before S2 launch.

## Series

| # | opponent | n | bar |
|---|----------|---|-----|
| S2 first | `bin/youloss` (frozen sf_19 + YoulossTM, sha c5ae7908..38301) | 400 | >=55% AND CI lower bound >50% |
| S1 | official dev prebuilt (`SF_ENGINE=/tmp/youloss-upstream-stockfish-dev/extracted/stockfish/stockfish-macos-universal`, label `dev-official`) | 400 | >=55% AND CI lower bound >50% |
| S3 | sf19-official (`SF_ENGINE=/tmp/youloss-benchmark/stockfish/stockfish-macos-universal`, label `sf19-official`) | 400 | >=50% score AND zero losses on time/crash/flag |

## Stop rules
- Any series' bar fails -> hold at frozen `bin/youloss` (rollback), report to user: iterate or ship.
- Environment rejection -> rerun after fixing power/sleep; never reclassify as a result.
- Sleep/AC violation -> batch invalid (`pmset -g log` audit after every batch).
- Development staging: S2 is both the first scored series AND the regression guard; games are
  counted only from the first validated batch after this document was written.

## Amendment #1 (2026-10-06 ~21:00, user authorization)
User directive: "do not plug the ac now" then "do it without ac" — battery run authorized.
Changes vs protocol above:
- `REQUIRE_AC=0` (was 1). All other env unchanged.
- `BATTERY_MIN=25` — supervisor aborts cleanly when battery hits 25% (floor stop is an
  environment rejection; batches never counted past it).
- **Lid MUST stay open** — `caffeinate -i` does not block clamshell sleep; closing the lid
  during a move creates fake time-forfeits and invalidates the batch (2026-10-06 evidence).
- Kill-path fix (ancestry verification) is live, so any safety stop now actually stops the
  match — no orphans.

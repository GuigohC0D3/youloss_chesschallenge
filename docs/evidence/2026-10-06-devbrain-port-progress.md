# Devbrain Port — Progress & Gate Evidence (Stage 1, M4)

Date: 2026-10-06
Branch: `sprint1-sfdev-adopt` (from `victor` @ 05f03f6)
Plan: `docs/superpowers/plans/2026-10-06-state-of-the-art-devbrain-port.md`
Spec: `docs/superpowers/specs/2026-10-06-state-of-the-art-design.md`

## Baseline fingerprints (before any change)

- Frozen `bin/youloss` SHA-256: `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301`
- Frozen `bin/youloss` bench: `2497913`
- Dev official prebuilt SHA-256: `adef0f3e2c97ef51e596a6a590d83b201221ad03a283d54fe79eb7edc0a80fd0`
- Dev prebuilt id: `Stockfish dev-20260930-49ea5ded`
- Dev prebuilt bench: `1714434`
- Dev net: `nn-252f33942263.nnue` (from `engine/src/evaluate.h` after port; auto-fetch via `make net`)
- Baseline gates: pytest `334 passed in 82.46s`; `scripts/test_engine_tm.sh` → `OK: youloss_tm` (rc=0)

## Gate results (Task 5)

- `scripts/test_engine_tm.sh` → `OK: youloss_tm` (rc=0)
- `bin/youloss_devport bench` → `Nodes searched : 1714434` == official dev prebuilt `1714434`
- `.venv/bin/python -m pytest -q` → `334 passed` (port complete; later `335 passed` after the
  harness kill-path fix added `test_terminate_kills_child_when_exec_drops_token_from_argv`)
- UCI surface: `option name YoulossTM type check default true`, `readyok`
- Frozen `bin/youloss` SHA re-verified after build: OK

## S2 campaign log (Task 7-8)

- Launched 19:43:29 on AC, batch #1 rundir `tm_1500+0_r2_s1791326610_20261006-194331.FkVPYZ`
  (cmd=youloss_devport vs youloss, 7t/2048/1500ms, balanced book, Syzygy on).
- 20:24:15 AC lost → SAFETY_STOP fired; kill-path bug left match running (root cause: bash
  execs the final `-c` command, dropping `token=` from argv → verification refused).
  Orphan killed manually; batch #1 environment-rejected per prereg (1/4 games finished:
  ½-½ Termination=normal — NOT counted).
- Harness fixed (ancestry fallback, security pins intact, suite 335).
- Auto-relaunch watcher armed (pid 88785, `/tmp/youloss_ac_watcher.sh`): starts S2 with
  REQUIRE_AC=1 within 60s of AC returning.
5de10e10a18d03f0ef788473b1b89b5fba7928ce7670b77245b3bd4e96d4d518  bin/youloss_devport
id name Stockfish dev-20261003-m-05f03f6e

### 2026-10-15 — S2 relaunched on the M5 (owner's machine, AC, lid open)

- Machine: Apple M5 (4P+6E, 16 GB), `/bin/bash` 3.2. Setup via `scripts/m5_setup.sh`.
- Fingerprints: frozen `bin/youloss` sha `24e00a638029b5e61a14e302555ffed7b655bd87a77af526e80628916cb00145`
  bench 2,497,913 (PGO rebuild; differs from `c5ae7908…`, no counted games under the old SHA) ·
  `bin/youloss_devport` sha `3b42145b92d9a2621719243a4e9ef63691bf765df09ffde30fdeb86a451bd4d8` bench 1,714,434 ·
  net `nn-252f33942263` · fastchess v1.8.2-alpha `f618e34`, sha `5b15b3b8…349fe3`.
- Fixes before the first counted game (no protocol change): empty-array expansions in
  `testing/tm_match.sh` guarded for bash 3.2 (`set -u` aborted 13 harness tests); `m5_setup.sh`
  now rebuilds fastchess when the pinned sidecar is missing.
- Batch #1 11:03 rejected at preflight (sidecar missing, child exit 2, 0 games). Relaunched 11:04
  with identical preregistered parameters plus `LIVE_LOG=1` (observation-only UCI log for
  `testing/live_view.py`). Gates: pytest 335 passed, `OK: youloss_tm`.
- 2026-10-15 ~12:00: stopped by owner (moving machine). Batch in progress (games 1-2 draws, game 3 started)
  discarded by design; still 0 counted games. Clean stop, no orphan processes.

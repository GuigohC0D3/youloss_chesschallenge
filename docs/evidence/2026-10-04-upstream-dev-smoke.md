# Upstream Stockfish dev smoke (2026-10-04)

**Status:** Completed smoke only (2026-10-04). No game/match started. Not strength evidence.

## Provenance

- Official release tag: `stockfish-dev-20260930-49ea5ded`.
- Source commit `49ea5ded38315cff8e67f4a677a9e7811612fbf6`.
- Project base `sf_19` commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d`.

## Artifact

- Official macOS universal archive fetched from the tag release.
- Archive SHA-256 `63d15a29153e0a42500628ed4bf68bc8f0b8c76fbcc34710f5bf3121d711d525`.
- Extracted binary SHA-256 `adef0f3e2c97ef51e596a6a590d83b201221ad03a283d54fe79eb7edc0a80fd0`.
- `file` confirmed x86_64 + arm64.
- It is only staged in `/tmp/youloss-upstream-stockfish-dev/`, not bundled in the checkout; re-fetch and verify if removed.

## Smoke checks

- Upstream dev and current `bin/youloss` both returned UCI `uciok` and `readyok` and completed default `bench` with exit 0.
- Upstream: 1,714,434 nodes, 984,175 nodes/s, 1,742ms.
- Youloss: 2,497,913 nodes, 1,054,861 nodes/s, 2,368ms.
- Benchmark node totals are version/position-set dependent; neither nodes nor NPS establish relative playing strength.

## State

- No game/match started, no source/build changes made.
- The existing pre-work dirty state was preserved.
- Current machine after these short checks: battery power at 37%, swap 901.5MiB / 2,048MiB.
- No match/screening process active.

## Next

- Next valuable strength test: one preregistered paired match between Youloss and this official dev binary with identical Threads=1, Hash=128, equal overhead and paired colors/openings, after AC power and lid-open readiness.
- Re-fetch/check hashes if the `/tmp` artifact has been removed.
- Treat the dev binary as a research comparator, not a tournament-eligibility decision.

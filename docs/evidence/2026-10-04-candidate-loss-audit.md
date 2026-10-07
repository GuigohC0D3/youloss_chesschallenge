# Current candidate loss audit — 2026-10-04

## Comparison context

The largest current comparable partition used candidate binary SHA-256
`c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301` and
external baseline SHA-256
`8eed61129d1493c5d1f2fd9323f0c54c47ac49319911fbde18c6b9c87e8b13c5` (labelled
Stockfish 19). It used fastchess `v1.8.2-alpha`, `10+0.1`, one thread, Hash
128 MiB, Move Overhead 10 ms, and the manifest-identified UHO opening book.
The external binary is the binary extracted from the verified official
`official-stockfish/Stockfish` release tag `sf_19` asset
`stockfish-macos-universal.tar.gz` (archive SHA-256
`a1f0e3bcc5a6927a11fe6fc8e54a779754645f3c2bae2cf13420fd1957adaa77`, tag
resolves to source commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d`); its
SHA-256 matches the 100-game and 470-game logs/reports exactly. This verifies
release-artifact identity/provenance; it was not locally rebuilt from source.

Across 470 games and 235 color-paired openings, the result was 111 wins,
248 draws, and 111 losses for Youloss: 50.0% score. The approximate paired
95% confidence interval was 47.77%–52.23%. This is consistent with parity; it
does not establish superiority or describe performance at the tournament's
25-minute control.

## Review of the 111 candidate losses

For each loss, the audit located the first candidate-to-move PGN score that
crossed from better than -200 cp to -200 cp or worse, ignoring mate scores and
numeric scores outside ±1000 cp. A one-thread, 50,000-node replay compared the
historical move and the immediately preceding opponent move with the replay
engine's preferred move at each position. This is a screening measure, not a
verified blunder adjudication.

- Opponent move regret: median 0 cp, 90th percentile 19 cp, none above 100 cp.
- Candidate response regret: median 9 cp, 90th percentile 43 cp, one above
  100 cp (190 cp), none above 250 cp.

The single larger response gap was in
`logs/sprt/tm_10+0.1_r5_s1791073990_20261003-213311.rEvMiR/match.pgn`, game 10,
ply 72. Youloss played `Qe8` after 0.490 seconds. At 5 million nodes, the
candidate's MultiPV search preferred `Qd7` at -320 cp; a search restricted to
the played move returned -539 cp. At 1 million nodes the leading move was
`e3`, showing search instability as depth increased. All sampled lines were
already unfavorable, and the analysis does not show that another move saves
the game. Treat this as one position for deeper study, not evidence for a
global time-manager change.

Retrospective Syzygy probes found that 74 of the 111 losses reached a
candidate-to-move position with five or fewer pieces; all 74 were already WDL
losses at their first such position. The remaining 37 games ended before a
candidate-to-move position in that tablebase range. This rules out an
endgame-only rescue for the probeable positions, but does not establish that
the preceding exchanges were forced.

## Telemetry caveat and decision

Some PGN comments contain numeric scores around ±80–90 pawns near promotions
and mate. Those values are not useful for the analyzer's exploratory
centipawn-change proxy. The analyzer now excludes mate values and numeric
values outside ±1000 cp, counts excluded numeric outliers per engine, and
resets the comparison baseline across excluded values. Reprocessing inspected
200 run directories (8 valid partitions, 33 excluded runs); in the 470-game
partition above, it excluded 532 candidate and 553 baseline numeric outliers.
Proxy drops remain unverified and must not be reported as blunder counts.

No engine parameter change is supported by this audit. Keep `FallMax=2.25`
experimental. The next strength experiment should be a preregistered,
paired `FallMax=2.0` versus `2.25` comparison using identical binary settings,
fixed seeds/opening holdout, a verified reference build, and independent
validation. Run extended strength/profile tests only on AC power; no match was
started as part of this audit. Verification: analyzer tests **32 passed**;
full controller and testing suites **333 passed**; Ruff check and format passed.

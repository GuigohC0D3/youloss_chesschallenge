# Youloss vs chess.com Maximum (3200) — overnight report

- **Run:** 2026-11-06T02:01:52.899535+00:00 → 2026-11-06T09:04:04.539563+00:00 (UTC)
- **Elapsed:** 422.2 min (25331 s)
- **Opponent:** chess.com Maximum (3200), Komodo25
- **Control:** 3+2; engine cap 800 ms; 6 threads; 512 MiB hash; overhead 40 ms
- **Games:** 131 finished; **13970 moves**; **0 failures**

## Score

**125 wins / 6 draws / 0 losses — 97.7%**

| Color | Games | W | D | L | Score |
|---|---:|---:|---:|---:|---:|
| White | 66 | 65 | 1 | 0 | 99.2% |
| Black | 65 | 60 | 5 | 0 | 96.2% |

## Terminations

- `checkmate`: 125
- `draw`: 4
- `stalemate`: 2

## Pace

- Average game: **183.1 s**; median **187.6 s**; min **75.7 s**; max **287.7 s**
- Average length: **106.7 plies**; max **166**
- Throughput: **18.6 games/hour**
- Longest: game 82 (black, 0-1, 166 plies, 287.7 s)
- Shortest: game 88 (black, 1/2-1/2, 45 plies, 75.7 s)

## Engine telemetry

- Our moves: **7018**; source: `engine` 6702, `book` 316
- Depth: median **17**, p95 **120**, max **245** (245 is Stockfish's forced-mate convention, not a normal search depth); mate scores found: **1107**
- Nodes: avg **1,378,112**, total **9,236,106,081**
- Engine time: avg **723 ms**; board time: avg **2031 ms** (engine + click/UI latency)
- Eval (cp): avg **+653**, min **-37**, max **+9880**; mate scores: **1107**
- Lowest clock before one of our moves: **163.0 s**; moves under 10 s: **0**; under 3 s: **0**; time forfeits: **0**

## Anomalies

- Failures: **0**
- Board mismatches: **0**
- Underpromotion substitutions: **7**
  - game 4: engine `g1=B+` → board `g1=Q+`
  - game 28: engine `a1=R` → board `a1=Q`
  - game 53: engine `a8=R` → board `a8=Q`
  - game 61: engine `f8=R` → board `f8=Q`
  - game 90: engine `f1=R` → board `f1=Q`
  - game 120: engine `f1=N#` → board `f1=Q`
  - game 128: engine `dxc1=R+` → board `dxc1=Q+`

## Data

- PGNs: **131**
- Run size: **84.3 MiB**
- Files: `logs/night/night-20261105-230150`

## Handoff and stop

- The finite run hit its 7-hour cutoff at 06:04 local after game 131.
- The unlimited watchdog started at 06:04 but did not detect AC during its 4-hour window; it exited at 10:04 without starting a new series.
- No games were played after 06:04. Everything above is the complete dataset.
- The operator stopped the harness at 11:30 local. No harness, watchdog, or `caffeinate` process remained.
- Chrome stays open with the throwaway session; `controller.web` was not touched.

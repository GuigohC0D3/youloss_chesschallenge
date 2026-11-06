# Chess.com night harness

Unattended series of Youloss (`bin/stockfish`, YoulossTM) against chess.com's
**Maximum (3200)** bot. It drives a real Chrome window over CDP, reads the live
board and move list, plays with real mouse clicks, and records every move.

## One-time setup

```bash
.venv/bin/pip install -r testing/night/requirements.txt
.venv/bin/python -m testing.night login
```

A dedicated Chrome profile lives in `~/.local/share/youloss-night/chrome`.
Log in to the throwaway chess.com account there once; the session persists.

## Smoke test

```bash
.venv/bin/python -m testing.night diag
```

Saves a screenshot, DOM snapshot, and parsed state under `logs/night/.../diag`.
It does not start or click a game.

## Run

```bash
.venv/bin/python -m testing.night run \
  --games 0 --hours 7 \
  --color alternate \
  --tc 3+2 \
  --max-move-ms 800 --overhead 40 \
  --threads 6 --hash 512
```

- `--games 0` runs until `--hours`.
- `--color alternate` = White, Black, White, Black...
- chess.com offers **3+2**, not 3+0. Three minutes plus two seconds is the
  closest control and keeps the clock healthy with the 800 ms cap.
- `--attach` takes over the game already open instead of starting one.
- `--dry-run` reads the board and chooses a move without clicking.

### Overnight, AC-gated

```bash
nohup bash testing/night/launch_overnight.sh \
  > logs/night/supervisor-$(date +%Y%m%d-%H%M%S).log 2>&1 &
```

The launcher waits for AC, then runs under `caffeinate -dimsu`.
Keep the lid open: `caffeinate` cannot defeat clamshell sleep.
By default it runs **without a time limit** (`--hours 0`) until stopped.

To hand over from a finite run to an unlimited one:

```bash
nohup bash testing/night/watch_indefinite.sh \
  > logs/night/unlimited-$(date +%Y%m%d-%H%M%S).log 2>&1 &
```

Stop order matters: kill `logs/night/unlimited.pid` first, then the active
run, otherwise the watchdog starts another series.

## Output

One folder per run: `logs/night/night-YYYYMMDD-HHMMSS/`

| File | Contents |
|---|---|
| `run.json` | spec, host, start time |
| `events.jsonl` | lifecycle, failures, board mismatches, engine options |
| `moves.jsonl` | one row per ply: FEN, UCI/SAN, source, depth, seldepth, nodes, eval, PV, engine time, clock before/after, chess.com per-move time |
| `games/NNNN.pgn` | full game with result and termination |
| `summary.json` | games, moves, failures, per-game result and wall time |
| `failures/` | screenshot on a rejected move or timeout |
| `diag/` | browser snapshots and promotion samples |

## Operational notes

- Close `controller.web` and other heavy apps before the night; the harness
  prints a warning if port 8765 is active. The engine and Chrome compete for CPU.
- A 512 MiB hash is deliberate while swap is high. Increase it only with free RAM.
- The bot is chess.com's `Komodo25` engine at the 3200 slider. It is not
  deterministic across nights, so results are training telemetry, not a
  paired-opening Elo experiment.
- If chess.com changes its DOM, run `diag` and update the selectors in
  `testing/night/chesscom.py`; `SNAPSHOT_JS` is the single source of truth.
- On a failure the runner abandons the game, retries the next one, and stops
  after `--max-failures` consecutive failures (8 in the overnight launcher).

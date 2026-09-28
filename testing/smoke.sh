#!/usr/bin/env bash
# Smoke test: 4 partidas rápidas do engine contra ele mesmo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$ROOT/logs/smoke.log"
mkdir -p "$ROOT/logs"
# fastchess grava config.json (autosave) no cwd; mantém isso fora do root do repo.
cd "$ROOT/logs"
"$ROOT/tools/fastchess.exe" \
  -engine cmd="$ROOT/bin/youloss.exe" name=A \
  -engine cmd="$ROOT/bin/youloss.exe" name=B \
  -each tc=5+0.05 option.Threads=1 option.Hash=16 \
  -rounds 2 -games 2 -concurrency 2 -recover | tee "$LOG"
bash "$ROOT/testing/check_fastchess_log.sh" "$LOG"

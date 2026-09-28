#!/usr/bin/env bash
# Smoke test: 4 partidas rápidas do engine contra ele mesmo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"
LOG="$ROOT/logs/smoke.log"
mkdir -p "$ROOT/logs"
# fastchess grava config.json (autosave) no cwd; mantém isso fora do root do repo.
cd "$ROOT/logs"
"$ROOT/tools/fastchess$EXE" \
  -engine cmd="$ROOT/bin/youloss$EXE" name=A \
  -engine cmd="$ROOT/bin/youloss$EXE" name=B \
  -each tc=5+0.05 option.Threads=1 option.Hash=16 \
  -rounds 2 -games 2 -concurrency 2 -recover | tee "$LOG"
bash "$ROOT/testing/check_fastchess_log.sh" "$LOG"

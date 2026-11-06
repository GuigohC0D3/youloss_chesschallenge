#!/usr/bin/env bash
# Wait for AC, keep the Mac awake, then run the chess.com night series.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p logs/night

MAX_WAIT="${AC_WAIT_SECONDS:-14400}"
started="$(date +%s)"
while ! pmset -g batt | grep -q "AC Power"; do
    now="$(date +%s)"
    if (( now - started > MAX_WAIT )); then
        echo "ERRO: sem AC após ${MAX_WAIT}s; série não iniciada" >&2
        exit 2
    fi
    echo "[$(date '+%H:%M:%S')] aguardando AC..."
    sleep 20
done

RUN_DIR="logs/night/night-$(date +%Y%m%d-%H%M%S)"
if (( $# > 0 )); then
    echo "[$(date '+%H:%M:%S')] AC ok; argumentos do operador"
    exec caffeinate -dimsu .venv/bin/python -m testing.night run "$@"
fi

echo "[$(date '+%H:%M:%S')] AC ok; run=$RUN_DIR"
exec caffeinate -dimsu .venv/bin/python -m testing.night run \
    --games 0 \
    --hours 0 \
    --color alternate \
    --tc 3+2 \
    --max-move-ms 800 \
    --overhead 40 \
    --hash 512 \
    --threads 6 \
    --max-failures 8 \
    --out "$RUN_DIR"

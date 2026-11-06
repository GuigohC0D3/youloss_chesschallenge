#!/usr/bin/env bash
# Wait for the finite run to exit, then start an unlimited series.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p logs/night

echo $$ > logs/night/unlimited.pid
FINITE_PID_FILE="logs/night/supervisor.pid"
if [[ -f "$FINITE_PID_FILE" ]]; then
    FINITE_PID="$(cat "$FINITE_PID_FILE")"
    echo "[$(date '+%H:%M:%S')] aguardando o run finito PID=$FINITE_PID"
    while kill -0 "$FINITE_PID" 2>/dev/null; do
        sleep 15
    done
fi

echo "[$(date '+%H:%M:%S')] run finito encerrado; iniciando série sem limite"
exec bash testing/night/launch_overnight.sh \
    --games 0 \
    --hours 0 \
    --color alternate \
    --tc 3+2 \
    --max-move-ms 800 \
    --overhead 40 \
    --hash 512 \
    --threads 6 \
    --max-failures 8

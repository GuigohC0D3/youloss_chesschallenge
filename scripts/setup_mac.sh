#!/usr/bin/env bash
# Prepara um clone do repositório em Mac Apple Silicon (M4, M5): compila e testa.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

bash scripts/check_toolchain.sh
ENGINE_OUT=stockfish bash scripts/build_engine.sh
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -m pytest controller/tests testing/tests -q

nodes="$(bin/stockfish bench 2>&1 | awk '/Nodes searched/ {print $NF}')"
if [ "$nodes" != "2497913" ]; then
  echo "ERRO: bench $nodes, esperado 2497913 (Stockfish 19)" >&2
  exit 1
fi
echo "OK: bench $nodes. Para jogar: .venv/bin/python -m controller.web"

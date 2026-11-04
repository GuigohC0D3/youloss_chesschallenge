#!/usr/bin/env bash
# Compila e roda os testes unitários do youloss_tm. Rodar do root do repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"
msys_reexec scripts/test_engine_tm.sh

mkdir -p "$ROOT/bin"
c++ -std=c++17 -O1 -Wall -Wextra -Werror -I "$ROOT/engine/src" \
  "$ROOT/engine/tests/youloss_tm_test.cpp" "$ROOT/engine/src/youloss_tm.cpp" \
  -o "$ROOT/bin/youloss_tm_test$EXE"
"$ROOT/bin/youloss_tm_test$EXE"

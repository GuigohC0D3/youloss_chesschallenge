#!/usr/bin/env bash
# Compila e roda os testes unitários do youloss_tm. Rodar do root do repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Mesmo motivo do build_engine.sh: o gcc do MSYS2 precisa do TMP do próprio MSYS2.
if [ "${MSYSTEM:-}" != "UCRT64" ]; then
  exec env MSYSTEM=UCRT64 CHERE_INVOKING=1 /c/msys64/usr/bin/bash -lc \
    "cd '$(cygpath -u "$ROOT")' && bash scripts/test_engine_tm.sh"
fi

mkdir -p "$ROOT/bin"
g++ -std=c++17 -O1 -Wall -Wextra -Werror -I "$ROOT/engine/src" \
  "$ROOT/engine/tests/youloss_tm_test.cpp" "$ROOT/engine/src/youloss_tm.cpp" \
  -o "$ROOT/bin/youloss_tm_test.exe"
"$ROOT/bin/youloss_tm_test.exe"

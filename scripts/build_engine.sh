#!/usr/bin/env bash
# Compila o engine com PGO e copia para bin/. Rodar do root do repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# O make do MSYS2 perde TMP/TEMP quando chamado pelo Git Bash (runtimes msys
# diferentes) e o gcc falha com "Cannot create temporary file in C:\WINDOWS".
# Reexecuta este script dentro do bash do próprio MSYS2 (UCRT64).
if [ "${MSYSTEM:-}" != "UCRT64" ]; then
  exec env MSYSTEM=UCRT64 CHERE_INVOKING=1 /c/msys64/usr/bin/bash -lc \
    "cd '$(cygpath -u "$ROOT")' && bash scripts/build_engine.sh"
fi

SRC="$ROOT/engine/src"
JOBS="$(nproc)"
mkdir -p "$ROOT/bin"

# O Windows (antivírus) segura o .exe recém-executado por alguns segundos;
# o objclean do profile-build do Stockfish falha com "Device or resource busy".
wait_unlock() {
  for _ in $(seq 1 30); do
    rm -f "$SRC/stockfish.exe" 2>/dev/null && return 0
    sleep 1
  done
  echo "stockfish.exe continua bloqueado" >&2
  return 1
}

# Equivalente ao target profile-build do Makefile, com espera entre os passos.
build() {  # $1=ARCH  $2=nome do binário
  local mk=(make -C "$SRC" ARCH="$1" COMP=mingw)
  "${mk[@]}" clean >/dev/null
  "${mk[@]}" net config-sanity >/dev/null
  "${mk[@]}" -j"$JOBS" gcc-profile-make
  (cd "$SRC" && ./stockfish.exe bench > PGOBENCH.out 2>&1)
  wait_unlock
  "${mk[@]}" objclean
  "${mk[@]}" -j"$JOBS" gcc-profile-use
  "${mk[@]}" profileclean
  cp "$SRC/stockfish.exe" "$ROOT/bin/$2"
}

build native youloss.exe
build x86-64-avx2 youloss-avx2.exe
"$ROOT/bin/youloss.exe" bench 2>&1 | tail -4

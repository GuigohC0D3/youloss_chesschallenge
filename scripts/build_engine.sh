#!/usr/bin/env bash
# Compila o engine com PGO e copia para bin/. Rodar do root do repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"
msys_reexec scripts/build_engine.sh

SRC="$ROOT/engine/src"
mkdir -p "$ROOT/bin"

# O Windows (antivírus) segura o .exe recém-executado por alguns segundos;
# o objclean do profile-build do Stockfish falha com "Device or resource busy".
wait_unlock() {
  for _ in $(seq 1 30); do
    rm -f "$SRC/stockfish$EXE" 2>/dev/null && return 0
    sleep 1
  done
  echo "stockfish$EXE continua bloqueado" >&2
  return 1
}

# Equivalente ao target profile-build do Makefile, com espera entre os passos.
build() {  # $1=ARCH  $2=nome do binário
  local mk profile
  if is_mac; then
    # O Makefile procura llvm-profdata ao lado do clang++ e não acha o do Xcode.
    mk=(make -C "$SRC" ARCH="$1" COMP=clang LLVM_PROFDATA="$(xcrun -f llvm-profdata)")
    profile=clang
  else
    mk=(make -C "$SRC" ARCH="$1" COMP=mingw)
    profile=gcc
  fi
  "${mk[@]}" clean >/dev/null
  "${mk[@]}" net config-sanity >/dev/null
  "${mk[@]}" -j"$JOBS" "$profile-profile-make"
  (cd "$SRC" && "./stockfish$EXE" bench > PGOBENCH.out 2>&1)
  wait_unlock
  "${mk[@]}" objclean
  "${mk[@]}" -j"$JOBS" "$profile-profile-use"
  "${mk[@]}" profileclean
  cp "$SRC/stockfish$EXE" "$ROOT/bin/$2$EXE"
}

OUT="${ENGINE_OUT:-youloss}"
if is_mac; then
  build apple-silicon "$OUT"
else
  build native "$OUT"
  build x86-64-avx2 "$OUT-avx2"
fi
"$ROOT/bin/$OUT$EXE" bench 2>&1 | tail -4

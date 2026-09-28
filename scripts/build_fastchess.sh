#!/usr/bin/env bash
# Baixa e compila a última release do fastchess em tools/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"
msys_reexec scripts/build_fastchess.sh

TAG="$(git ls-remote --tags --refs https://github.com/Disservin/fastchess 'v*' | awk -F/ '{print $3}' | sort -V | tail -1)"
rm -rf "$ROOT/tools/fastchess-src"
git clone -q --depth 1 --branch "$TAG" https://github.com/Disservin/fastchess "$ROOT/tools/fastchess-src"
# build=release linka estático no Windows (sem depender das DLLs do gcc no PATH);
# o macOS não suporta binário estático, então lá é o build padrão.
if is_mac; then
  make -C "$ROOT/tools/fastchess-src" -j"$JOBS"
else
  make -C "$ROOT/tools/fastchess-src" -j"$JOBS" build=release
fi
cp "$ROOT/tools/fastchess-src/fastchess$EXE" "$ROOT/tools/fastchess$EXE"
echo "fastchess $TAG"

#!/usr/bin/env bash
# Baixa e compila a última release do fastchess em tools/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Mesmo motivo de build_engine.sh: make do MSYS2 precisa rodar no bash do MSYS2.
if [ "${MSYSTEM:-}" != "UCRT64" ]; then
  exec env MSYSTEM=UCRT64 CHERE_INVOKING=1 /c/msys64/usr/bin/bash -lc \
    "cd '$(cygpath -u "$ROOT")' && bash scripts/build_fastchess.sh"
fi

TAG="$(git ls-remote --tags --refs https://github.com/Disservin/fastchess 'v*' | awk -F/ '{print $3}' | sort -V | tail -1)"
rm -rf "$ROOT/tools/fastchess-src"
git clone -q --depth 1 --branch "$TAG" https://github.com/Disservin/fastchess "$ROOT/tools/fastchess-src"
# build=release linka estático (sem depender das DLLs do gcc no PATH)
make -C "$ROOT/tools/fastchess-src" -j"$(nproc)" build=release
cp "$ROOT/tools/fastchess-src/fastchess.exe" "$ROOT/tools/fastchess.exe"
echo "fastchess $TAG"

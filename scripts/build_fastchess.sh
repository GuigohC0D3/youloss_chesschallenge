#!/usr/bin/env bash
# Baixa e compila o fastchess pinado em tools/.
#
# Pin verificado: tag v1.8.2-alpha == commit
# f618e34540f94f4719ad3817950618dabe441318. A tag remota e a HEAD clonada
# sao ambas verificadas antes/depois do build; qualquer divergencia aborta.
# O sidecar tools/fastchess.build.json registra tag/commit/SHA-256 exatos
# do binario construido; testing/tm_match.sh exige e valida esse sidecar
# antes de rodar (fail-closed contra binario trocado/reconstruido).
#
# CAVEAT de politica de versao: este pin e ALPHA; se a intencao era
# stable-only, esta e a decisao restante a tomar.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"
msys_reexec scripts/build_fastchess.sh

TAG="v1.8.2-alpha"
PINNED_COMMIT="f618e34540f94f4719ad3817950618dabe441318"
UPSTREAM="https://github.com/Disservin/fastchess"

REMOTE_SHA="$(git ls-remote --tags --refs "$UPSTREAM" "refs/tags/$TAG" | awk '{print $1}')"
[ -n "$REMOTE_SHA" ] || { echo "FAIL: tag $TAG nao encontrada em $UPSTREAM" >&2; exit 1; }
[ "$REMOTE_SHA" = "$PINNED_COMMIT" ] || {
  echo "FAIL: tag $TAG resolve para $REMOTE_SHA, esperado $PINNED_COMMIT" >&2
  exit 1
}

mkdir -p "$ROOT/tools"
rm -rf "$ROOT/tools/fastchess-src"
git clone -q --depth 1 --branch "$TAG" "$UPSTREAM" "$ROOT/tools/fastchess-src"
LOCAL_SHA="$(git -C "$ROOT/tools/fastchess-src" rev-parse HEAD)"
[ "$LOCAL_SHA" = "$PINNED_COMMIT" ] || {
  echo "FAIL: HEAD clonada $LOCAL_SHA != $PINNED_COMMIT" >&2
  exit 1
}
# build=release linka estático no Windows (sem depender das DLLs do gcc no PATH);
# o macOS não suporta binário estático, então lá é o build padrão.
if is_mac; then
  make -C "$ROOT/tools/fastchess-src" -j"$JOBS"
else
  make -C "$ROOT/tools/fastchess-src" -j"$JOBS" build=release
fi
cp "$ROOT/tools/fastchess-src/fastchess$EXE" "$ROOT/tools/fastchess$EXE"
BIN_SHA="$($SHA256 "$ROOT/tools/fastchess$EXE")"
BIN_SHA="${BIN_SHA%% *}"
SIDECAR="$ROOT/tools/fastchess.build.json"
{
  printf '{\n'
  printf '  "tag": "%s",\n' "$TAG"
  printf '  "commit": "%s",\n' "$PINNED_COMMIT"
  printf '  "sha256": "%s"\n' "$BIN_SHA"
  printf '}\n'
} >"$SIDECAR"
echo "fastchess $TAG $LOCAL_SHA"
echo "sidecar $SIDECAR $BIN_SHA"

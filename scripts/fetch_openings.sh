#!/usr/bin/env bash
# Baixa as aberturas do SPRT (UHO_Lichess_4852_v1, as mesmas dos testes oficiais
# do Stockfish) para assets/openings e registra sha256 em assets/MANIFEST.
# Rodar do root do repo, com rede, ANTES do evento.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"
URL="https://github.com/official-stockfish/books/raw/master/UHO_Lichess_4852_v1.epd.zip"
DEST="assets/openings"
mkdir -p "$DEST"
curl -fsSL --retry 3 -o "$DEST/uho.zip" "$URL"
"$PY" -m zipfile -e "$DEST/uho.zip" "$DEST"
rm "$DEST/uho.zip"
[ -s "$DEST/UHO_Lichess_4852_v1.epd" ] || { echo "EPD não encontrado após extrair" >&2; exit 1; }
touch assets/MANIFEST
grep -vE ' [*]?openings/' assets/MANIFEST > assets/MANIFEST.tmp || true
(cd assets && $SHA256 openings/*.epd) >> assets/MANIFEST.tmp
mv assets/MANIFEST.tmp assets/MANIFEST
echo "OK: $(wc -l < "$DEST/UHO_Lichess_4852_v1.epd") posições em $DEST"

#!/usr/bin/env bash
# Baixa as Syzygy 3-4-5 (WDL+DTZ) para assets/syzygy e registra sha256 em assets/MANIFEST.
# Opcional, somente se a organização confirmar o uso e o limite de peças. ~1 GB.
# Rodar do root do repo, com rede, antes do evento; não requer rede durante a partida.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"
BASE="https://tablebase.lichess.ovh/tables/standard/3-4-5"
DEST="assets/syzygy"
mkdir -p "$DEST"
files=$(curl -fsSL "$BASE/" | grep -oE 'href="[KQRBNP]+v[KQRBNP]+\.rtb[wz]"' \
  | sed -e 's/^href="//' -e 's/"$//' | sort -u)
[ -n "$files" ] || { echo "nenhuma tabela listada em $BASE/" >&2; exit 1; }
for f in $files; do
  if [ ! -s "$DEST/$f" ]; then
    curl -fsSL --retry 3 -o "$DEST/$f.part" "$BASE/$f"
    mv "$DEST/$f.part" "$DEST/$f"
  fi
done
wdl=$(ls "$DEST"/*.rtbw | wc -l)
dtz=$(ls "$DEST"/*.rtbz | wc -l)
[ "$wdl" -eq "$dtz" ] || { echo "WDL ($wdl) e DTZ ($dtz) não batem" >&2; exit 1; }
touch assets/MANIFEST
grep -vE ' [*]?syzygy/' assets/MANIFEST > assets/MANIFEST.tmp || true
(cd assets && $SHA256 syzygy/*.rtbw syzygy/*.rtbz) >> assets/MANIFEST.tmp
mv assets/MANIFEST.tmp assets/MANIFEST
echo "OK: $wdl WDL + $dtz DTZ em $DEST"

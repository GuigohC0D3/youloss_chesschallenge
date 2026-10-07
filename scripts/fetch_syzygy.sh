#!/usr/bin/env bash
# Baixa as Syzygy 3-4-5 (WDL+DTZ) para assets/syzygy e registra sha256 em assets/MANIFEST.
# Opcional, somente se a organização confirmar o uso e o limite de peças. ~1 GB.
# Rodar do root do repo, com rede, antes do evento; não requer rede durante a partida.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"
BASE_WDL="https://tablebase.lichess.ovh/tables/standard/3-4-5-wdl"
BASE_DTZ="https://tablebase.lichess.ovh/tables/standard/3-4-5-dtz"
DEST="assets/syzygy"
mkdir -p "$DEST"

echo "Listing 3-4-5 WDL and DTZ tables from Lichess..."
wdl_files=$(curl -fsSL "$BASE_WDL/" | grep -oE 'href="[KQRBNP]+v[KQRBNP]+\.rtbw"' | sed -e 's/^href="//' -e 's/"$//' | sort -u)
dtz_files=$(curl -fsSL "$BASE_DTZ/" | grep -oE 'href="[KQRBNP]+v[KQRBNP]+\.rtbz"' | sed -e 's/^href="//' -e 's/"$//' | sort -u)

[ -n "$wdl_files" ] || { echo "nenhuma tabela WDL listada em $BASE_WDL/" >&2; exit 1; }
[ -n "$dtz_files" ] || { echo "nenhuma tabela DTZ listada em $BASE_DTZ/" >&2; exit 1; }

total_wdl=$(echo "$wdl_files" | wc -l | tr -d ' ')
count=0
for f in $wdl_files; do
  count=$((count + 1))
  if [ ! -s "$DEST/$f" ]; then
    echo "[$count/$total_wdl] Fetching WDL: $f"
    curl -fsSL --retry 3 -o "$DEST/$f.part" "$BASE_WDL/$f"
    mv "$DEST/$f.part" "$DEST/$f"
  fi
done

total_dtz=$(echo "$dtz_files" | wc -l | tr -d ' ')
count=0
for f in $dtz_files; do
  count=$((count + 1))
  if [ ! -s "$DEST/$f" ]; then
    echo "[$count/$total_dtz] Fetching DTZ: $f"
    curl -fsSL --retry 3 -o "$DEST/$f.part" "$BASE_DTZ/$f"
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

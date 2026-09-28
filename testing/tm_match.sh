#!/usr/bin/env bash
# Match do youloss_tm: mesmo binário, YoulossTM=true ("tm") x false ("sf").
# Uso: bash testing/tm_match.sh <tc> <rounds> [elo0 elo1]
#   partidas fixas:  bash testing/tm_match.sh 10+0.1 100
#   SPRT:            bash testing/tm_match.sh 60+0.6 50000 -5 0
# Concorrência: CONC (padrão: núcleos físicos - 1; no macOS, só os de performance). Deixe a máquina ociosa.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TC="${1:?uso: tm_match.sh <tc> <rounds> [elo0 elo1]}"
ROUNDS="${2:?rounds}"
ELO0="${3:-}"
ELO1="${4:-}"
source "$ROOT/scripts/platform.sh"
if [ -z "${CONC:-}" ]; then
  CONC=$(( PHYS_CORES > 1 ? PHYS_CORES - 1 : 1 ))
fi
BOOK="$ROOT/assets/openings/UHO_Lichess_4852_v1.epd"
[ -s "$BOOK" ] || { echo "sem aberturas: rode scripts/fetch_openings.sh" >&2; exit 2; }

OUT="$ROOT/logs/sprt"
mkdir -p "$OUT"
NAME="tm_${TC}_r${ROUNDS}${ELO0:+_sprt${ELO0}_${ELO1}}_$(date +%Y%m%d-%H%M%S)"
SPRT=()
[ -n "$ELO0" ] && SPRT=(-sprt elo0="$ELO0" elo1="$ELO1" alpha=0.05 beta=0.05)

cd "$OUT"  # fastchess grava config.json no cwd
"$ROOT/tools/fastchess$EXE" \
  -engine cmd="$ROOT/bin/youloss$EXE" name=tm option.YoulossTM=true \
  -engine cmd="$ROOT/bin/youloss$EXE" name=sf option.YoulossTM=false \
  -each tc="$TC" option.Threads=1 option.Hash=16 \
  -openings file="$BOOK" format=epd order=random \
  -rounds "$ROUNDS" -games 2 -concurrency "$CONC" -recover \
  "${SPRT[@]}" \
  -pgnout file="$OUT/$NAME.pgn" \
  | tee "$OUT/$NAME.log"

cd "$ROOT"
echo "== perfil de tempo ($NAME.pgn)"
"$PY" -m testing.time_profile "$OUT/$NAME.pgn"
if [ -n "$ELO0" ]; then
  "$PY" -m testing.sprt_result "$OUT/$NAME.log"
fi

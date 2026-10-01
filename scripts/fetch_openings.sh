#!/usr/bin/env bash
# Baixa o conjunto UHO fixado pelo checksum já registrado em assets/MANIFEST.
# Preparar com rede, antes do evento; partidas continuam totalmente offline.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"

URL="https://github.com/official-stockfish/books/raw/master/UHO_Lichess_4852_v1.epd.zip"
FILENAME="UHO_Lichess_4852_v1.epd"
MANIFEST_PATH="*openings/$FILENAME"
MANIFEST="$ROOT/assets/MANIFEST"
DEST="$ROOT/assets/openings/$FILENAME"

[ -s "$MANIFEST" ] || { echo "FAIL: assets/MANIFEST ausente ou vazio" >&2; exit 1; }
MATCH_COUNT="$(awk -v p="$MANIFEST_PATH" '$2 == p { n++ } END { print n+0 }' "$MANIFEST")"
[ "$MATCH_COUNT" = 1 ] || {
  echo "FAIL: assets/MANIFEST deve conter exatamente um checksum para $MANIFEST_PATH" >&2
  exit 1
}
EXPECTED_SHA="$(awk -v p="$MANIFEST_PATH" '$2 == p { print $1 }' "$MANIFEST")"
case "$EXPECTED_SHA" in ''|*[!0-9a-f]*) echo "FAIL: checksum inválido em $MANIFEST" >&2; exit 1 ;; esac
[ "${#EXPECTED_SHA}" -eq 64 ] || { echo "FAIL: checksum SHA-256 inválido em $MANIFEST" >&2; exit 1; }

hash_file() {
  local result
  # shellcheck disable=SC2086 # SHA256 is a trusted command plus fixed flags.
  result="$($SHA256 "$1")"
  printf '%s\n' "${result%% *}"
}

if [ -e "$DEST" ]; then
  ACTUAL_SHA="$(hash_file "$DEST")"
  [ "$ACTUAL_SHA" = "$EXPECTED_SHA" ] || {
    echo "FAIL: asset existente $DEST tem SHA-256 $ACTUAL_SHA; esperado $EXPECTED_SHA" >&2
    exit 1
  }
  echo "OK: $DEST já confere com assets/MANIFEST ($EXPECTED_SHA)"
  exit 0
fi

TMP="$(mktemp -d "$ROOT/assets/.openings-download.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
mkdir "$TMP/extracted"
curl -fsSL --connect-timeout 10 --max-time 60 --retry 2 \
  -o "$TMP/uho.zip" "$URL"
"$PY" -m zipfile -e "$TMP/uho.zip" "$TMP/extracted"
SOURCE="$TMP/extracted/$FILENAME"
[ -s "$SOURCE" ] || { echo "FAIL: $FILENAME não encontrado no arquivo baixado" >&2; exit 1; }
ACTUAL_SHA="$(hash_file "$SOURCE")"
[ "$ACTUAL_SHA" = "$EXPECTED_SHA" ] || {
  echo "FAIL: checksum do download $ACTUAL_SHA != assets/MANIFEST $EXPECTED_SHA" >&2
  exit 1
}

mkdir -p "$(dirname "$DEST")"
mv "$SOURCE" "$DEST"
echo "OK: $DEST verificado ($ACTUAL_SHA); assets/MANIFEST preservado"

#!/usr/bin/env bash
# Falha (exit 1) se o log do fastchess tiver perda por tempo, desconexão,
# lance ilegal ou crash — o fastchess sai com 0 mesmo nesses casos.
set -u
LOG="$1"
if grep -iE "loses on time|disconnect|illegal|crash|stalls" "$LOG"; then
  echo "FAIL: problemas no log $LOG" >&2
  exit 1
fi
grep -qE "^Games: [1-9]" "$LOG" || { echo "FAIL: nenhuma partida concluída" >&2; exit 1; }

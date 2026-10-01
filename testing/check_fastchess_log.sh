#!/usr/bin/env bash
# Fail-closed checker for fastchess match logs.
#
# Fails (exit 1) on any incident class (crash, time loss, disconnect,
# illegal move, stall), on a missing/incomplete/malformed game summary,
# and — in SPRT mode — on an inconclusive result. fastchess itself exits
# 0 even when incidents occur, so this checker must always run, including
# when the runner exits nonzero.
#
# The textual "H0/H1 was accepted" marker is NEVER trusted on its own:
# the final numeric LLR must actually cross the logged SPRT bounds.
# Pinned fastchess v1.8.2-alpha prints "H1 was accepted" on max-round
# exhaustion even when the SPRT verdict is still CONTINUE, so an
# in-bounds final LLR is rejected as inconclusive even if that phrase
# is present.
#
# Uso:
#   bash testing/check_fastchess_log.sh <log> [--expect-games N]
#                                       [--sprt <elo0> <elo1>]
# Exit: 0 = PASS, 1 = FAIL, 2 = usage error.
set -u

usage() {
  echo "uso: check_fastchess_log.sh <log> [--expect-games N] [--sprt <elo0> <elo1>]" >&2
}

[ $# -ge 1 ] || { usage; exit 2; }
LOG="$1"; shift
EXPECT_GAMES=""
SPRT=0
SPRT_ELO0=""
SPRT_ELO1=""
while [ $# -gt 0 ]; do
  case "$1" in
    --expect-games) [ $# -ge 2 ] || { usage; exit 2; }; EXPECT_GAMES="$2"; shift 2 ;;
    --sprt) [ $# -ge 3 ] || { usage; exit 2; }; SPRT=1; SPRT_ELO0="$2"; SPRT_ELO1="$3"; shift 3 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "argumento desconhecido: $1" >&2; usage; exit 2 ;;
  esac
done

FAIL=0
fail() { echo "FAIL: $*" >&2; FAIL=1; }

[ -f "$LOG" ] || { echo "FAIL: log nao encontrado: $LOG" >&2; exit 1; }

# 1. Incident classes. O fastchess sai com 0 mesmo nesses casos.
if grep -qiE 'loses on time|disconnect|illegal|crash|stall' "$LOG"; then
  grep -niE 'loses on time|disconnect|illegal|crash|stall' "$LOG" | head -n 20 >&2
  fail "incidente detectado no log (crash/time-loss/disconnect/illegal/stall)"
fi

# 2. Completed-game summary must exist and be well-formed as a complete
#    structured row (pinned fastchess format). A numeric count followed by
#    junk (e.g. 'Games: 200oops') or missing/malformed fields must fail.
GAMES_LINE="$(grep -E '^Games: ' "$LOG" | tail -n 1)"
[ -n "$GAMES_LINE" ] || fail "resumo ausente: nenhuma linha 'Games:' no log"
if [ -n "$GAMES_LINE" ]; then
  if ! printf '%s\n' "$GAMES_LINE" | grep -Eq '^Games: *[0-9]+, *Wins: *[0-9]+, *Losses: *[0-9]+, *Draws: *[0-9]+, *Points: *[0-9]+(\.[0-9]+)? *\([0-9]+(\.[0-9]+)? *%\) *$'; then
    fail "resumo malformado: '$GAMES_LINE'"
    GAMES=""
  else
    SUMMARY_FIELDS="$(printf '%s\n' "$GAMES_LINE" | sed -E -n 's/^Games: *([0-9]+), *Wins: *([0-9]+), *Losses: *([0-9]+), *Draws: *([0-9]+),.*/\1 \2 \3 \4/p')"
    # shellcheck disable=SC2086
    set -- $SUMMARY_FIELDS
    GAMES="${1:-}"; WINS="${2:-}"; LOSSES="${3:-}"; DRAWS="${4:-}"
    case "$GAMES" in
      ''|*[!0-9]*) fail "resumo malformado: '$GAMES_LINE'" ;;
      0) fail "nenhuma partida concluida: '$GAMES_LINE'" ;;
    esac
    if [ -n "$GAMES" ] && [ -n "$WINS" ] && [ -n "$LOSSES" ] && [ -n "$DRAWS" ]; then
      OUTCOME_GAMES=$((WINS + LOSSES + DRAWS))
      [ "$OUTCOME_GAMES" -eq "$GAMES" ] \
        || fail "Wins + Losses + Draws ($OUTCOME_GAMES) != Games ($GAMES)"
    fi
  fi
else
  GAMES=""
fi
if [ -n "$EXPECT_GAMES" ] && [ -n "$GAMES" ]; then
  [ "$GAMES" = "$EXPECT_GAMES" ] || fail "partidas concluidas $GAMES != esperado $EXPECT_GAMES"
fi

# 3. Fixed runs require the pinned fastchess pentanomial summary row.
#    Its v1.8.2-alpha label is "Ptnml(0-2)", not "Penta". Reconcile
#    its 2-game pairs against Games for every run type.
PENTA_LINE="$(grep -E '^Ptnml\(0-2\): ' "$LOG" | tail -n 1)"
if [ "$SPRT" = 0 ]; then
  [ -n "$PENTA_LINE" ] || fail "resumo incompleto: nenhuma linha 'Ptnml(0-2):' no log (relatorio final truncado)"
fi
if [ -n "$PENTA_LINE" ]; then
  if ! printf '%s\n' "$PENTA_LINE" | grep -Eq '^Ptnml\(0-2\): *\[[0-9]+, *[0-9]+, *[0-9]+, *[0-9]+, *[0-9]+\], *WL/DD Ratio: *(nan|-?inf|-?[0-9]+(\.[0-9]+)?) *$'; then
    fail "linha 'Ptnml(0-2):' malformada: '$PENTA_LINE'"
  elif [ -n "$GAMES" ]; then
    PENTA_BUCKETS="$(printf '%s\n' "$PENTA_LINE" | sed -E -n 's/^Ptnml\(0-2\): *\[([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+)\], *WL\/DD Ratio: *(nan|-?inf|-?[0-9]+(\.[0-9]+)?) *$/\1 \2 \3 \4 \5/p')"
    # shellcheck disable=SC2086
    set -- $PENTA_BUCKETS
    PENTA_SUM=$((${1:-0} + ${2:-0} + ${3:-0} + ${4:-0} + ${5:-0}))
    PENTA_GAMES=$((2 * PENTA_SUM))
    [ "$PENTA_SUM" -gt 0 ] || fail "resumo 'Ptnml(0-2):' sem pares de partidas concluidos"
    [ "$PENTA_GAMES" -eq "$GAMES" ] \
      || fail "2 * sum(Ptnml buckets) ($PENTA_GAMES) != Games ($GAMES)"
  fi
fi

# 4. SPRT verdict: the final numeric LLR must cross the logged bounds.
#    Never trust only the textual H0/H1 marker.
if [ "$SPRT" = 1 ]; then
  LLR_LINE="$(grep -E '^LLR: ' "$LOG" | tail -n 1)"
  [ -n "$LLR_LINE" ] || fail "modo SPRT sem linha 'LLR:' no log (resumo incompleto)"
  if printf '%s\n' "$LLR_LINE" | grep -Eq '^LLR: *-?[0-9]+([.][0-9]+)? *\(-?[0-9]+([.][0-9]+)?%\) *\( *-?[0-9]+([.][0-9]+)?, *-?[0-9]+([.][0-9]+)? *\) *\[ *-?[0-9]+([.][0-9]+)?, *-?[0-9]+([.][0-9]+)? *\] *$'; then
    LLR_FIELDS="$(printf '%s\n' "$LLR_LINE" | tr -d '()[]%' | tr ',:' '  ')"
  else
    LLR_FIELDS=""
  fi
  # shellcheck disable=SC2086
  set -- $LLR_FIELDS
  LLR_V="${2:-}"; LLR_LO="${4:-}"; LLR_HI="${5:-}"; LLR_E0="${6:-}"; LLR_E1="${7:-}"
  if [ -z "$LLR_V" ] || [ -z "$LLR_LO" ] || [ -z "$LLR_HI" ] || [ -z "$LLR_E0" ] || [ -z "$LLR_E1" ]; then
    fail "linha 'LLR:' malformada: '$LLR_LINE'"
  else
    # The logged Elo bounds must equal the configured ones.
    awk -v a="$LLR_E0" -v b="$SPRT_ELO0" -v c="$LLR_E1" -v d="$SPRT_ELO1" \
      'BEGIN{ if (a != b || c != d) exit 1 }' \
      || fail "bounds do log [$LLR_E0, $LLR_E1] != configurado [$SPRT_ELO0, $SPRT_ELO1]"
    MARKER="$(grep -Eo 'H[01] was accepted' "$LOG" | tail -n 1)"
    # LLR and bounds are printed to two decimals. Require one full displayed
    # step beyond the rounded bound so equality (for example 2.94 vs 2.94)
    # cannot turn an ambiguous CONTINUE into an accepted hypothesis.
    if awk -v v="$LLR_V" -v hi="$LLR_HI" 'BEGIN{ exit !(v >= hi + 0.01) }'; then
      [ "$MARKER" = "H1 was accepted" ] \
        || fail "LLR final $LLR_V cruza o bound superior $LLR_HI mas o marcador e '$MARKER' (malformado)"
    elif awk -v v="$LLR_V" -v lo="$LLR_LO" 'BEGIN{ exit !(v <= lo - 0.01) }'; then
      [ "$MARKER" = "H0 was accepted" ] \
        || fail "LLR final $LLR_V cruza o bound inferior $LLR_LO mas o marcador e '$MARKER' (malformado)"
    else
      fail "SPRT inconclusivo: LLR final $LLR_V dentro dos bounds ($LLR_LO, $LLR_HI); marcador textual '${MARKER:-ausente}' ignorado (fastchess imprime H1 no esgotamento de rounds mesmo com CONTINUE)"
    fi
  fi
fi

if [ "$FAIL" = 0 ]; then
  echo "PASS: $LOG (games=${GAMES:-?}${SPRT_ELO0:+, sprt=[$SPRT_ELO0, $SPRT_ELO1]})"
fi
exit "$FAIL"

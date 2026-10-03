#!/usr/bin/env bash
# Fail-closed tournament-match harness: fixed runs and SPRT runs of
# youloss_tm ("tm", YoulossTM=true) vs baseline ("sf", YoulossTM=false).
#
# Uso: bash testing/tm_match.sh <tc> <rounds> [elo0 elo1]
#   partidas fixas:  MOVE_OVERHEAD_MS=10 bash testing/tm_match.sh 10+0 100
#   SPRT:            MOVE_OVERHEAD_MS=60 bash testing/tm_match.sh 60+0 50000 -5 0
#
# Env: CONC (padrao: 1 no fanless M4 para nao sobrecarregar; sobrescrevivel),
#      THREADS (padrao: 1), HASH_MB (padrao: 16),
#      MOVE_OVERHEAD_MS (padrao: 1500, igual ao controlador),
#      TIME_CAP_S (teto wall-clock em segundos; padrao 1800 / 30 min),
#      KILL_GRACE_S (graca entre TERM e KILL em segundos; padrao 30),
#      SRAND (seed reproduzivel das aberturas; padrao: epoch atual, gravado).
# Para controles escalados, calibre MOVE_OVERHEAD_MS; o preflight rejeita valores
# que esgotam o horizonte inicial do time manager.
# Deixe a maquina ociosa. Smoke runs devem ser curtos e registrados; confrontos
# longos/SPRT exigem orçamento de tempo deliberado e não devem rodar em paralelo
# com outras cargas que afetem a medição.
#
# Fail-closed: a run falha (exit 1) em crash, time loss, disconnect,
# lance ilegal, stall, resumo incompleto/malformado, exit nonzero do
# fastchess, timeout do teto wall-clock, SPRT inconclusivo, sidecar de
# build ausente/divergente e hash do binario divergente do sidecar.
# O verificador
# testing/check_fastchess_log.sh SEMPRE roda, mesmo se o fastchess sair
# com nonzero, e o marcador textual H0/H1 nunca e confiado sozinho.
#
# Diretorio da run a prova de colisao: mktemp -d com sufixo aleatorio,
# entao NAME e derivado do diretorio criado (sem overwrite mesmo com
# mesmos parametros no mesmo segundo); NAME/rundir gravados no meta.json.
#
# Sem -recover: partidas com incidente nunca sao reiniciadas/ocultadas.
# Fixed runs exigem exatamente rounds*2 partidas concluidas. SPRT permite
# parada antecipada somente quando o LLR final cruza um bound configurado.
#
# Pareamento intencional (sem -noswap): com dois engines e
# "-rounds N -games 2", o round-robin cria dois jogos por pairing, reusa
# a mesma abertura nos dois jogos e troca as cores nos IDs pares. O
# embaralhamento do livro usa o RNG compartilhado; -srand o fixa.
# Nao adicione -noswap: o pareamento por cor e o comportamento desejado.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TC="${1:?uso: tm_match.sh <tc> <rounds> [elo0 elo1]}"
ROUNDS="${2:?uso: tm_match.sh <tc> <rounds> [elo0 elo1]}"
ELO0="${3:-}"
ELO1="${4:-}"
if { [ -n "$ELO0" ] && [ -z "$ELO1" ]; } || { [ -z "$ELO0" ] && [ -n "$ELO1" ]; }; then
  echo "FAIL: elo0 e elo1 devem ser fornecidos juntos" >&2
  exit 2
fi
source "$ROOT/scripts/platform.sh"
# Padrao CONC=1 e TIME_CAP_S=1800 (30 min) para nao sobrecarregar o M4 (fanless)
# em comparacoes de forca total e limitar screening.
CONC="${CONC:-1}"
THREADS="${THREADS:-1}"
HASH_MB="${HASH_MB:-16}"
MOVE_OVERHEAD_MS="${MOVE_OVERHEAD_MS:-1500}"
TIME_CAP_S="${TIME_CAP_S:-1800}"
KILL_GRACE_S="${KILL_GRACE_S:-30}"
SRAND="${SRAND:-}"
[ -n "$SRAND" ] || SRAND="$(date +%s)"
case "$ROUNDS" in ''|*[!0-9]*|0) echo "FAIL: rounds deve ser inteiro positivo" >&2; exit 2 ;; esac
case "$CONC" in ''|*[!0-9]*|0) echo "FAIL: CONC deve ser inteiro positivo" >&2; exit 2 ;; esac
case "$THREADS" in ''|*[!0-9]*|0) echo "FAIL: THREADS deve ser inteiro positivo" >&2; exit 2 ;; esac
case "$HASH_MB" in ''|*[!0-9]*|0) echo "FAIL: HASH_MB deve ser inteiro positivo" >&2; exit 2 ;; esac
case "$MOVE_OVERHEAD_MS" in ''|*[!0-9]*) echo "FAIL: MOVE_OVERHEAD_MS deve ser inteiro entre 0 e 5000" >&2; exit 2 ;; esac
[ "${#MOVE_OVERHEAD_MS}" -le 4 ] && [ "$MOVE_OVERHEAD_MS" -le 5000 ] || {
  echo "FAIL: MOVE_OVERHEAD_MS deve estar entre 0 e 5000" >&2; exit 2;
}
case "$TIME_CAP_S" in ''|*[!0-9]*|0) echo "FAIL: TIME_CAP_S deve ser inteiro positivo" >&2; exit 2 ;; esac
case "$KILL_GRACE_S" in ''|*[!0-9]*|0) echo "FAIL: KILL_GRACE_S deve ser inteiro positivo" >&2; exit 2 ;; esac

# Time-control and overhead preflight (fail-closed):
# 1. Rejects unsupported or malformed time controls (requires base+increment format).
# 2. Rejects Move Overhead * (2+mtg) exceeding 10% of Stockfish's initial budget.
#    (10% is a conservative experiment policy, not a fairness proof).
# 3. For zero-increment fixed runs, verifies TIME_CAP_S covers maximum clock time
#    (rounds * 2 games * 2 sides * base seconds) plus modest process buffer (30s).
#    SPRT and incremented controls are not rejected without a justified bound.
# Overhead calibration note:
# In engine-only tests (fastchess), MOVE_OVERHEAD_MS models OS scheduling and UCI pipe
# latency only. Unlike physical tournament operation with human operators reading clocks,
# typing moves, and pressing physical buttons (where latency is on the order of seconds),
# engine-only tests require calibrated overhead (e.g. 10-60 ms) to avoid artificial search
# horizon starvation. No physical simulation is performed here.
if ! "$PY" - "$TC" "$MOVE_OVERHEAD_MS" "$TIME_CAP_S" "$ROUNDS" "$ELO0" <<'PY'
from decimal import Decimal
import math
import re
import sys

control, overhead_text, time_cap_text, rounds_text, elo0_text = sys.argv[1:6]
match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\+([0-9]+(?:\.[0-9]+)?)", control)
if match is None:
    print(
        f"FAIL: unsupported or malformed time control '{control}' (expected base+inc, e.g. 60+0 or 10+0.1)",
        file=sys.stderr,
    )
    raise SystemExit(1)

base_sec = Decimal(match.group(1))
inc_sec = Decimal(match.group(2))
base_ms = int(base_sec * 1000)
increment_ms = int(inc_sec * 1000)
move_overhead_ms = int(overhead_text)

mtg = 50 if base_ms >= 1000 else (base_ms * 5) // 100
initial_budget_ms = base_ms + increment_ms * (mtg - 1)

if initial_budget_ms <= 0:
    print(
        f"FAIL: time control '{control}' provides non-positive initial budget ({initial_budget_ms}ms)",
        file=sys.stderr,
    )
    raise SystemExit(1)

overhead_reserve_ms = move_overhead_ms * (2 + mtg)
if overhead_reserve_ms * 10 > initial_budget_ms:
    max_overhead_ms = initial_budget_ms // (10 * (2 + mtg))
    print(
        "FAIL: Move Overhead exceeds the 10% initial-budget policy "
        f"for {control}: {overhead_reserve_ms}ms reserved vs "
        f"{initial_budget_ms}ms available (mtg={mtg}). "
        f"Move Overhead * (2+mtg) exceeds 10% of initial budget (limit={initial_budget_ms // 10}ms). "
        "State note: 10% is a conservative experiment policy, not a fairness proof. "
        f"Calibrate overhead for scaled controls (<= {max_overhead_ms}ms); "
        "1500ms is intended for the provisional 1500+0 control.",
        file=sys.stderr,
    )
    raise SystemExit(1)

is_sprt = bool(elo0_text.strip())
if increment_ms == 0 and not is_sprt:
    rounds = int(rounds_text)
    time_cap_s = int(time_cap_text)
    # rounds * 2 games * 2 sides * base seconds
    max_clock_s = int(math.ceil(Decimal(rounds) * 4 * base_sec))
    process_buffer_s = 30
    required_cap_s = max_clock_s + process_buffer_s
    if time_cap_s < required_cap_s:
        print(
            f"FAIL: TIME_CAP_S={time_cap_s}s cannot cover maximum clock time for {rounds} round(s) "
            f"of {control}: max clock time is {max_clock_s}s ({rounds} rounds * 2 games * 2 sides * {base_sec}s) "
            f"+ {process_buffer_s}s process buffer = {required_cap_s}s required. "
            f"Increase TIME_CAP_S to at least {required_cap_s}.",
            file=sys.stderr,
        )
        raise SystemExit(1)
PY
then
  exit 2
fi

# Runner pin: deve ser identico ao scripts/build_fastchess.sh.
# CAVEAT de politica de versao: este pin e ALPHA (v1.8.2-alpha); se a
# intencao era stable-only, esta e a decisao restante a tomar.
FASTCHESS_TAG="v1.8.2-alpha"
FASTCHESS_COMMIT="f618e34540f94f4719ad3817950618dabe441318"

BOOK="$ROOT/assets/openings/UHO_Lichess_4852_v1.epd"
[ -s "$BOOK" ] || { echo "FAIL: sem aberturas: rode scripts/fetch_openings.sh" >&2; exit 2; }
FASTCHESS="$ROOT/tools/fastchess$EXE"
[ -x "$FASTCHESS" ] || { echo "FAIL: fastchess ausente: rode scripts/build_fastchess.sh" >&2; exit 2; }
SIDECAR="$ROOT/tools/fastchess.build.json"
[ -s "$SIDECAR" ] || { echo "FAIL: sidecar ausente em $SIDECAR: rode scripts/build_fastchess.sh" >&2; exit 2; }
SIDECAR_TAG="$(sed -E -n 's/.*"tag": *"([^"]+)".*/\1/p' "$SIDECAR" | head -n 1)"
SIDECAR_COMMIT="$(sed -E -n 's/.*"commit": *"([^"]+)".*/\1/p' "$SIDECAR" | head -n 1)"
SIDECAR_SHA="$(sed -E -n 's/.*"sha256": *"([^"]+)".*/\1/p' "$SIDECAR" | head -n 1)"
[ -n "$SIDECAR_TAG" ] || { echo "FAIL: sidecar sem tag: $SIDECAR" >&2; exit 2; }
[ -n "$SIDECAR_COMMIT" ] || { echo "FAIL: sidecar sem commit: $SIDECAR" >&2; exit 2; }
[ -n "$SIDECAR_SHA" ] || { echo "FAIL: sidecar sem sha256: $SIDECAR" >&2; exit 2; }
[ "$SIDECAR_TAG" = "$FASTCHESS_TAG" ] || { echo "FAIL: sidecar tag $SIDECAR_TAG != pin $FASTCHESS_TAG" >&2; exit 2; }
[ "$SIDECAR_COMMIT" = "$FASTCHESS_COMMIT" ] || { echo "FAIL: sidecar commit $SIDECAR_COMMIT != pin $FASTCHESS_COMMIT" >&2; exit 2; }
ENGINE="$ROOT/bin/youloss$EXE"
[ -x "$ENGINE" ] || { echo "FAIL: engine ausente em $ENGINE" >&2; exit 2; }
BOOK_SHA="$($SHA256 "$BOOK")"
BOOK_SHA="${BOOK_SHA%% *}"
FASTCHESS_SHA="$($SHA256 "$FASTCHESS")"
FASTCHESS_SHA="${FASTCHESS_SHA%% *}"
[ "$FASTCHESS_SHA" = "$SIDECAR_SHA" ] || { echo "FAIL: hash do binario $FASTCHESS_SHA != sidecar $SIDECAR_SHA: rode scripts/build_fastchess.sh" >&2; exit 2; }
ENGINE_SHA="$($SHA256 "$ENGINE")"
ENGINE_SHA="${ENGINE_SHA%% *}"

GAMES_PER_ROUND=2
EXPECTED_GAMES=$(( ROUNDS * GAMES_PER_ROUND ))
SPRT=0
[ -z "$ELO0" ] || SPRT=1

OUT="$ROOT/logs/sprt"
mkdir -p "$OUT"
BASE="tm_${TC}_r${ROUNDS}${ELO0:+_sprt${ELO0}_${ELO1}}_s${SRAND}_$(date +%Y%m%d-%H%M%S)"
RUNDIR="$(mktemp -d "$OUT/${BASE}.XXXXXX")"
NAME="$(basename "$RUNDIR")"
LOG="$RUNDIR/match.log"
PGN="$RUNDIR/match.pgn"
META="$RUNDIR/meta.json"
STATUS_F="$RUNDIR/.fastchess.status"
TIMEOUT_F="$RUNDIR/.timeout"

FC_ARGS=(
  -engine "cmd=$ENGINE" name=tm option.YoulossTM=true
  -engine "cmd=$ENGINE" name=sf option.YoulossTM=false
  -each "tc=$TC" "option.Threads=$THREADS" "option.Hash=$HASH_MB" "option.Move Overhead=$MOVE_OVERHEAD_MS"
  -openings "file=$BOOK" format=epd order=random
  -srand "$SRAND"
  -rounds "$ROUNDS" -games "$GAMES_PER_ROUND" -concurrency "$CONC"
  -pgnout "file=$PGN"
)
SPRT_ARGS=()
[ "$SPRT" = 0 ] || SPRT_ARGS=(-sprt "elo0=$ELO0" "elo1=$ELO1" alpha=0.05 beta=0.05)

echo "== match $NAME"
echo "tc=$TC rounds=$ROUNDS games_per_round=$GAMES_PER_ROUND conc=$CONC threads=$THREADS hash_mb=$HASH_MB move_overhead_ms=$MOVE_OVERHEAD_MS"
echo "seed=$SRAND book_sha256=$BOOK_SHA"
echo "runner=$FASTCHESS_TAG commit=$FASTCHESS_COMMIT sha256=$FASTCHESS_SHA time_cap_s=$TIME_CAP_S (sidecar verificado: $SIDECAR)"
[ "$SPRT" = 0 ] || echo "sprt=[$ELO0, $ELO1] alpha=0.05 beta=0.05"
echo "rundir=$RUNDIR"

# O fastchess grava config.json (autosave) no cwd: rodar dentro do RUNDIR
# preserva config/logs/PGNs/metadata distintos por run, sem overwrite.
cd "$RUNDIR"
rm -f "$STATUS_F" "$TIMEOUT_F" "$RUNDIR/.watchdog.sleep.pid"

# Create a fresh POSIX session for fastchess so all ordinary descendants share
# its process group; Python's os.setsid/os.killpg are available on macOS and
# avoid relying on GNU timeout or nonportable setsid/pgrep utilities.
signal_runner_tree() {
  "$PY" -c 'import os, signal, sys; os.killpg(int(sys.argv[1]), getattr(signal, sys.argv[2]))' \
    "$FC_PID" "$1" >/dev/null 2>&1 || true
}
runner_tree_alive() {
  "$PY" -c 'import os, sys
try:
    os.killpg(int(sys.argv[1]), 0)
except ProcessLookupError:
    sys.exit(1)
except PermissionError:
    pass
sys.exit(0)' "$FC_PID" >/dev/null 2>&1
}

# Teto wall-clock portatil (sem depender de GNU timeout): watchdog em
# background toca o sentinela e encerra o runner ao estourar o teto.
# O watchdog e seus sleeps sao destacados do pipe do tee (</dev/null
# >/dev/null 2>&1) para que nenhum filho segure a saida do tee; o pid do
# sleep vigente e publicado para cancelamento/reap na conclusao normal.
set +e
{
  "$PY" -c 'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
    "$FASTCHESS" "${FC_ARGS[@]}" ${SPRT_ARGS[@]+"${SPRT_ARGS[@]}"} 2>&1 &
  FC_PID=$!
  (
    sleep "$TIME_CAP_S" &
    echo "$!" >"$RUNDIR/.watchdog.sleep.pid"
    wait "$!" 2>/dev/null
    RC=$?
    rm -f "$RUNDIR/.watchdog.sleep.pid"
    if [ "$RC" -eq 0 ]; then
      if runner_tree_alive; then
        touch "$TIMEOUT_F"
        signal_runner_tree SIGTERM
        sleep "$KILL_GRACE_S" &
        echo "$!" >"$RUNDIR/.watchdog.sleep.pid"
        wait "$!" 2>/dev/null || true
        rm -f "$RUNDIR/.watchdog.sleep.pid"
        if runner_tree_alive; then
          signal_runner_tree SIGKILL
        fi
      fi
    fi
  ) </dev/null >/dev/null 2>&1 &
  WD_PID=$!
  wait "$FC_PID"
  echo "$?" >"$STATUS_F"
  # The runner may exit while a child still holds tee's pipe. Keep the
  # watchdog alive until the whole runner process group is gone.
  while runner_tree_alive; do sleep 0.05; done
  if [ -f "$RUNDIR/.watchdog.sleep.pid" ]; then WD_SLEEP_PID="$(cat "$RUNDIR/.watchdog.sleep.pid" 2>/dev/null || true)"; if [ -n "${WD_SLEEP_PID:-}" ]; then kill "$WD_SLEEP_PID" 2>/dev/null || true; fi; fi
  kill "$WD_PID" 2>/dev/null || true
  wait "$WD_PID" 2>/dev/null || true
  if [ -f "$RUNDIR/.watchdog.sleep.pid" ]; then WD_SLEEP_PID="$(cat "$RUNDIR/.watchdog.sleep.pid" 2>/dev/null || true)"; if [ -n "${WD_SLEEP_PID:-}" ]; then kill "$WD_SLEEP_PID" 2>/dev/null || true; fi; rm -f "$RUNDIR/.watchdog.sleep.pid"; fi
} | tee "$LOG"
TEE_STATUS="${PIPESTATUS[1]:-1}"
FC_STATUS="$(cat "$STATUS_F" 2>/dev/null || echo missing)"
set -e
cd "$ROOT"

TIMEOUT=0
[ ! -f "$TIMEOUT_F" ] || TIMEOUT=1
[ "$TIMEOUT" = 0 ] || FC_STATUS="timeout ($FC_STATUS)"

# O verificador sempre roda, mesmo com fastchess nonzero/timeout.
CHECK_STATUS=0
if [ "$SPRT" = 1 ]; then
  bash "$ROOT/testing/check_fastchess_log.sh" "$LOG" --sprt "$ELO0" "$ELO1" || CHECK_STATUS=$?
else
  bash "$ROOT/testing/check_fastchess_log.sh" "$LOG" --expect-games "$EXPECTED_GAMES" || CHECK_STATUS=$?
fi

PROFILE_STATUS=0
if [ -f "$PGN" ]; then
  echo "== perfil de tempo ($PGN)"
  "$PY" -m testing.time_profile "$PGN" || PROFILE_STATUS=$?
else
  echo "FAIL: PGN ausente: $PGN" >&2
  PROFILE_STATUS=1
fi

# Display-only: tanto o parser (testing/sprt_result.py) quanto o checker
# validam numericamente os bounds do LLR; seu exit nunca decide pass/fail
# do trial (apenas fastchess/tee/checker/profile decidem).
INFO_SPRT_RESULT="n/a"
if [ "$SPRT" = 1 ]; then
  INFO_SPRT_RESULT=0
  "$PY" -m testing.sprt_result "$LOG" || INFO_SPRT_RESULT=$?
fi

COMPLETED="$(grep -E '^Games: ' "$LOG" 2>/dev/null | tail -n 1 | sed -E -n 's/^Games: *([0-9]+).*/\1/p' || true)"
COMPLETED_JSON="${COMPLETED:-null}"

{
  printf '{\n'
  printf '  "name": "%s",\n' "$NAME"
  printf '  "rundir": "%s",\n' "$RUNDIR"
  printf '  "tc": "%s",\n' "$TC"
  printf '  "rounds": %s,\n' "$ROUNDS"
  printf '  "games_per_round": %s,\n' "$GAMES_PER_ROUND"
  printf '  "expected_games": %s,\n' "$EXPECTED_GAMES"
  printf '  "completed_games": %s,\n' "$COMPLETED_JSON"
  printf '  "concurrency": %s,\n' "$CONC"
  printf '  "threads": %s,\n' "$THREADS"
  printf '  "hash_mb": %s,\n' "$HASH_MB"
  printf '  "move_overhead_ms": %s,\n' "$MOVE_OVERHEAD_MS"
  printf '  "time_cap_s": %s,\n' "$TIME_CAP_S"
  printf '  "kill_grace_s": %s,\n' "$KILL_GRACE_S"
  printf '  "timeout": %s,\n' "$TIMEOUT"
  printf '  "seed": "%s",\n' "$SRAND"
  printf '  "book": "%s",\n' "$BOOK"
  printf '  "book_sha256": "%s",\n' "$BOOK_SHA"
  printf '  "runner_tag": "%s",\n' "$FASTCHESS_TAG"
  printf '  "runner_commit": "%s",\n' "$FASTCHESS_COMMIT"
  printf '  "runner_sha256": "%s",\n' "$FASTCHESS_SHA"
  printf '  "runner_sidecar": "%s",\n' "$SIDECAR"
  printf '  "runner_tag_verified": "%s",\n' "$SIDECAR_TAG"
  printf '  "runner_commit_verified": "%s",\n' "$SIDECAR_COMMIT"
  printf '  "runner_sha256_verified": "%s",\n' "$SIDECAR_SHA"
  printf '  "engine": "%s",\n' "$ENGINE"
  printf '  "engine_sha256": "%s",\n' "$ENGINE_SHA"
  printf '  "engine_options": "tm: YoulossTM=true; sf: YoulossTM=false; each: Threads=%s Hash=%s Move Overhead=%sms",\n' "$THREADS" "$HASH_MB" "$MOVE_OVERHEAD_MS"
  printf '  "sprt": %s,\n' "$SPRT"
  printf '  "sprt_elo0": "%s",\n' "$ELO0"
  printf '  "sprt_elo1": "%s",\n' "$ELO1"
  printf '  "exit_fastchess": "%s",\n' "$FC_STATUS"
  printf '  "exit_tee": "%s",\n' "$TEE_STATUS"
  printf '  "exit_checker": "%s",\n' "$CHECK_STATUS"
  printf '  "exit_time_profile": "%s",\n' "$PROFILE_STATUS"
  printf '  "exit_sprt_result_info": "%s"\n' "$INFO_SPRT_RESULT"
  printf '}\n'
} >"$META"
echo "metadata: $META"

FINAL=0
[ "$FC_STATUS" = "0" ] || { echo "FAIL: runner status: $FC_STATUS" >&2; FINAL=1; }
[ "$TEE_STATUS" = "0" ] || { echo "FAIL: tee status: $TEE_STATUS" >&2; FINAL=1; }
[ "$TIMEOUT" = "0" ] || { echo "FAIL: teto wall-clock excedido: ${TIME_CAP_S}s" >&2; FINAL=1; }
[ "$CHECK_STATUS" = "0" ] || { echo "FAIL: checker reprovou o log" >&2; FINAL=1; }
[ "$PROFILE_STATUS" = "0" ] || { echo "FAIL: perfil de tempo falhou / PGN ausente" >&2; FINAL=1; }
[ "$FINAL" = "0" ] && echo "PASS: $NAME"
exit "$FINAL"

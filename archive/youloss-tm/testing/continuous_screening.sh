#!/usr/bin/env bash
# Continuous unattended screening harness for Youloss vs baseline Stockfish.
#
# This supervisor performs bounded engine screening, telemetry collection,
# and diagnostic reporting only. It does NOT train NNUE weights or auto-tune source.
#
# Usage:
#   bash testing/continuous_screening.sh [start|status|stop]
#
# Environment variables (with sensible defaults):
#   TC                Time control (default: 10+0.1)
#   ROUNDS_PER_BATCH  Paired rounds per batch (default: 5 = 10 games)
#   MAX_BATCHES       Fully validated batches to complete before stopping
#                     (default: 0 = unlimited; positive integer = bounded session).
#                     A bounded session stops after MAX_BATCHES validated batches
#                     and fails closed on any invalid/failed batch.
#   THREADS           Search threads per engine (default: 1)
#   CONC              Concurrent matches (default: 1)
#   HASH_MB           Hash size in MB (default: 128)
#   MOVE_OVERHEAD_MS  Calibrated overhead (default: 10 for 10+0.1, 60 for 60+0)
#   TIME_CAP_S        Wall timeout per batch (default: 600)
#   DEADLINE_HOURS    Hard wall-clock run deadline in hours (default: 12)
#   DEADLINE_S        Hard wall-clock run deadline in seconds (default: DEADLINE_HOURS * 3600)
#   BATTERY_MIN       Halt if battery drops below % (default: 15)
#   MIN_DISK_MB       Minimum free disk space in MB required (default: 500)
#   MIN_FREE_SWAP_MB  Minimum free swap in MiB required (default: 2048)
#   MAX_SWAP_USED_MB  Maximum swap used in MiB allowed (default: 20480)
#   MIN_FREE_MEM_PCT  Minimum system-wide free memory % (default: 10)
#   REQUIRE_AC        Require positive confirmation of AC power (default: 1)
#   PAUSE_S           Pause in seconds between batches (default: 45)
#   SCREENING_DIR     Directory for status and logs (default: logs/screening)
#   TM_MATCH_SCRIPT   Batch runner script (default: $ROOT/testing/tm_match.sh).
#                     Override only for hermetic tests with a stub whose command
#                     line still contains 'tm_match.sh' for child verification.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/platform.sh"

SCREENING_DIR="${SCREENING_DIR:-$ROOT/logs/screening}"
PID_FILE="$SCREENING_DIR/screening.pid"
LOCK_DIR="$SCREENING_DIR/supervisor.lock"
LOCK_OWNER_FILE="$LOCK_DIR/owner.json"
SCOREBOARD_FILE="$SCREENING_DIR/scoreboard.json"
RUN_LOG="$SCREENING_DIR/continuous.log"

TC="${TC:-10+0.1}"
ROUNDS_PER_BATCH="${ROUNDS_PER_BATCH:-5}"
MAX_BATCHES="${MAX_BATCHES:-0}"
THREADS="${THREADS:-1}"
CONC="${CONC:-1}"
HASH_MB="${HASH_MB:-128}"
MOVE_OVERHEAD_MS="${MOVE_OVERHEAD_MS:-10}"
TIME_CAP_S="${TIME_CAP_S:-600}"
DEADLINE_HOURS="${DEADLINE_HOURS:-12}"
DEADLINE_S="${DEADLINE_S:-$((DEADLINE_HOURS * 3600))}"
BATTERY_MIN="${BATTERY_MIN:-15}"
MIN_DISK_MB="${MIN_DISK_MB:-500}"
MIN_FREE_SWAP_MB="${MIN_FREE_SWAP_MB:-2048}"
MAX_SWAP_USED_MB="${MAX_SWAP_USED_MB:-20480}"
export MAX_SWAP_USED_MB
MIN_FREE_MEM_PCT="${MIN_FREE_MEM_PCT:-10}"
REQUIRE_AC="${REQUIRE_AC:-1}"
PAUSE_S="${PAUSE_S:-45}"
TM_MATCH_SCRIPT="${TM_MATCH_SCRIPT:-$ROOT/testing/tm_match.sh}"

validate_bounded_config() {
  case "$MAX_BATCHES" in
    ''|*[!0-9]*)
      echo "FAIL: MAX_BATCHES must be a non-negative integer (0 = unlimited), got '${MAX_BATCHES:-}'" >&2
      return 2
      ;;
  esac
  case "$ROUNDS_PER_BATCH" in
    ''|*[!0-9]*|0)
      echo "FAIL: ROUNDS_PER_BATCH must be a positive integer, got '${ROUNDS_PER_BATCH:-}'" >&2
      return 2
      ;;
  esac
  if [ ! -f "$TM_MATCH_SCRIPT" ] || [ ! -r "$TM_MATCH_SCRIPT" ]; then
    echo "FAIL: TM_MATCH_SCRIPT is not readable: $TM_MATCH_SCRIPT" >&2
    return 2
  fi
  return 0
}

log_effective_config() {
  # Audit all effective match settings and safety thresholds to the session
  # log. Whitelisted variables only; never log secrets or full environment.
  {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Effective screening configuration:"
    echo "  TC=$TC"
    echo "  ROUNDS_PER_BATCH=$ROUNDS_PER_BATCH"
    echo "  MAX_BATCHES=$MAX_BATCHES (0=unlimited)"
    echo "  THREADS=$THREADS | CONC=$CONC | HASH_MB=${HASH_MB}MB | MOVE_OVERHEAD_MS=${MOVE_OVERHEAD_MS}ms"
    echo "  TIME_CAP_S=${TIME_CAP_S}s (per-batch cap)"
    echo "  DEADLINE_S=${DEADLINE_S}s (DEADLINE_HOURS=${DEADLINE_HOURS}h)"
    echo "  PAUSE_S=${PAUSE_S}s"
    echo "  REQUIRE_AC=$REQUIRE_AC | BATTERY_MIN=${BATTERY_MIN}%"
    echo "  MAX_SWAP_USED_MB=${MAX_SWAP_USED_MB}MiB | MIN_FREE_SWAP_MB=${MIN_FREE_SWAP_MB}MiB"
    echo "  MIN_FREE_MEM_PCT=${MIN_FREE_MEM_PCT}% | MIN_DISK_MB=${MIN_DISK_MB}MB"
  } | tee -a "$RUN_LOG"
}

mkdir -p "$SCREENING_DIR"

SUPERVISOR_START="$(date +%s)"
CHILD_PID=""
CHILD_TOKEN=""
CAFFEINATE_PID=""

is_pid_alive() {
  local pid="$1"
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null || return 1
  local state
  state="$(ps -p "$pid" -o stat= 2>/dev/null || true)"
  [ -n "$state" ] && [[ "$state" != Z* ]]
}

write_pid_record() {
  local record_file="${1:-$PID_FILE}"
  local script_argument="${BASH_SOURCE[0]}"
  local launch_cwd="$PWD"
  local lstart
  lstart="$(ps -p $$ -o lstart= 2>/dev/null || true)"
  local tmp_record="$record_file.$$.tmp"
  "$PY" - "$tmp_record" "$$" "$lstart" "$script_argument" "$launch_cwd" <<'PY'
import json, os, sys

script_argument = sys.argv[4]
launch_cwd = sys.argv[5]
data = {
    "pid": int(sys.argv[2]),
    "lstart": sys.argv[3].strip(),
    "canonical_path": os.path.realpath(os.path.join(launch_cwd, script_argument)),
    "script_argument": script_argument,
    "working_directory": launch_cwd,
}
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
PY
  mv -f "$tmp_record" "$record_file"
}

is_validated_supervisor() {
  local record_file="$1"
  if [ ! -f "$record_file" ]; then return 1; fi
  "$PY" - "$record_file" <<'PY'
import json, os, shlex, subprocess, sys

try:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
    pid = int(data["pid"])
    rec_lstart = data.get("lstart", "").strip()
    rec_path = data.get("canonical_path", "").strip()
    script_argument = data.get("script_argument", "").strip()
    launch_cwd = data.get("working_directory", "").strip()
except Exception:
    sys.exit(1)

if pid <= 1 or not rec_lstart or not rec_path or not script_argument or not launch_cwd:
    sys.exit(1)

expected_path = os.path.realpath(os.path.join(launch_cwd, script_argument))
if expected_path != os.path.realpath(rec_path) or not os.path.isfile(expected_path):
    sys.exit(1)

try:
    os.kill(pid, 0)
except OSError:
    sys.exit(1)

res_lstart = subprocess.run(["ps", "-p", str(pid), "-o", "lstart="], capture_output=True, text=True)
if res_lstart.returncode != 0:
    sys.exit(1)
curr_lstart = res_lstart.stdout.strip()
if rec_lstart and curr_lstart != rec_lstart:
    sys.exit(1)

res_cmd = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True)
if res_cmd.returncode != 0:
    sys.exit(1)
cmd = res_cmd.stdout.strip()

try:
    argv = shlex.split(cmd)
except ValueError:
    sys.exit(1)
if len(argv) < 2 or os.path.basename(argv[0]).lstrip("-") != "bash":
    sys.exit(1)
if argv[1] != script_argument or argv[1].startswith("-"):
    sys.exit(1)

sys.exit(0)
PY
}

is_descendant_of() {
  local pid="$1"
  local ancestor="$2"
  local guard=0
  while [ -n "$pid" ] && [ "$pid" != "0" ] && [ "$pid" != "1" ] && [ "$guard" -lt 64 ]; do
    if [ "$pid" = "$ancestor" ]; then
      return 0
    fi
    pid="$(ps -p "$pid" -o ppid= 2>/dev/null | tr -d '[:space:]' || true)"
    guard=$((guard + 1))
  done
  return 1
}

is_verified_owned_child() {
  local pid="$1"
  local token="$2"
  if [ -z "$pid" ] || ! is_pid_alive "$pid"; then
    return 1
  fi
  local cmd
  cmd="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  if ! [[ "$cmd" =~ tm_match\.sh ]]; then
    return 1
  fi
  if [[ "$cmd" =~ "$token" ]]; then
    return 0
  fi
  # Bash execs the final command of its -c list, which drops token= from the
  # child's argv (observed 2026-10-06: SAFETY_STOP orphan). Fall back to fork
  # ancestry from this supervisor: an unrelated tm_match.sh can never be a
  # descendant of this process, so PID reuse stays refused.
  is_descendant_of "$pid" "$$"
}

get_all_descendants() {
  local parent="$1"
  local children
  children="$(pgrep -P "$parent" 2>/dev/null || true)"
  for c in $children; do
    echo "$c"
    get_all_descendants "$c"
  done
}

terminate_child_tree() {
  local root_pid="$1"
  local token="${2:-$CHILD_TOKEN}"

  if [ -z "$root_pid" ]; then return 0; fi

  if ! is_verified_owned_child "$root_pid" "$token"; then
    echo "WARNING: PID $root_pid does not match verified owned screening child (token: $token). Refusing to signal." >&2
    return 1
  fi

  local descendants
  descendants="$(get_all_descendants "$root_pid" | sort -u || true)"

  for cpid in $descendants; do
    if is_pid_alive "$cpid"; then
      kill -TERM "$cpid" 2>/dev/null || true
    fi
  done

  kill -TERM "$root_pid" 2>/dev/null || true

  for _ in {1..20}; do
    local still_alive=0
    if is_pid_alive "$root_pid"; then
      still_alive=1
    else
      for cpid in $descendants; do
        if is_pid_alive "$cpid"; then
          still_alive=1
          break
        fi
      done
    fi
    if [ "$still_alive" -eq 0 ]; then
      break
    fi
    sleep 0.1
  done

  for cpid in $descendants; do
    if is_pid_alive "$cpid"; then
      kill -KILL "$cpid" 2>/dev/null || true
    fi
  done
  if is_pid_alive "$root_pid"; then
    kill -KILL "$root_pid" 2>/dev/null || true
  fi
}

check_safety_telemetry() {
  local check_dir="$1"
  "$PY" - "$check_dir" <<'PY'
import os, re, shutil, subprocess, sys

screening_dir = sys.argv[1] if len(sys.argv) > 1 else "."

# 1. Power telemetry probe
mock_pwr_fail = os.getenv("MOCK_POWER_FAIL")
if mock_pwr_fail:
    print(f"ERROR: Power telemetry unreadable: mock failure ({mock_pwr_fail})", file=sys.stderr)
    sys.exit(10)

mock_batt = os.getenv("MOCK_POWER_OUTPUT")
if mock_batt is not None:
    batt_out = mock_batt
else:
    if not shutil.which("pmset"):
        print("ERROR: Power telemetry unavailable (pmset not found)", file=sys.stderr)
        sys.exit(10)
    try:
        res = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, timeout=5)
        if res.returncode != 0:
            print("ERROR: Power telemetry unavailable (pmset failed)", file=sys.stderr)
            sys.exit(10)
        batt_out = res.stdout
    except Exception as e:
        print(f"ERROR: Power telemetry probe failed: {e}", file=sys.stderr)
        sys.exit(10)

is_ac = "AC Power" in batt_out
is_batt = "Battery Power" in batt_out

if not is_ac and not is_batt:
    print("ERROR: Power telemetry unreadable: unrecognized power state", file=sys.stderr)
    sys.exit(10)

m_batt = re.search(r"(\d+)%", batt_out)
if not m_batt:
    print("ERROR: Power telemetry unreadable: missing battery percentage", file=sys.stderr)
    sys.exit(10)
batt_pct = int(m_batt.group(1))

require_ac = os.getenv("REQUIRE_AC", "1") == "1"
if require_ac and not is_ac:
    print(f"SAFETY_STOP: Not on AC Power (Status: {'Battery' if is_batt else 'Unknown'}, Battery: {batt_pct}%)", file=sys.stderr)
    sys.exit(11)

batt_min = int(os.getenv("BATTERY_MIN", "15"))
if "discharging" in batt_out.lower() and batt_pct <= batt_min:
    print(f"SAFETY_STOP: Battery level ({batt_pct}%) <= min threshold ({batt_min}%)", file=sys.stderr)
    sys.exit(12)

# 2. System thermal / performance warning telemetry probe
mock_therm_fail = os.getenv("MOCK_THERM_FAIL")
if mock_therm_fail:
    print(f"SAFETY_STOP: System thermal/performance warning: {mock_therm_fail}", file=sys.stderr)
    sys.exit(15)

mock_therm = os.getenv("MOCK_THERM_OUTPUT")
if mock_therm is not None:
    therm_out = mock_therm
else:
    if not shutil.which("pmset"):
        print("ERROR: System thermal telemetry unavailable (pmset not found)", file=sys.stderr)
        sys.exit(15)

    try:
        t_res = subprocess.run(["pmset", "-g", "therm"], capture_output=True, text=True, timeout=5)
        if t_res.returncode != 0:
            print(f"ERROR: Thermal telemetry query failed with exit code {t_res.returncode}", file=sys.stderr)
            sys.exit(15)
        therm_out = t_res.stdout
    except Exception as e:
        print(f"ERROR: Thermal telemetry query exception: {e}", file=sys.stderr)
        sys.exit(15)

therm_warning = "nominal"
thermal_seen = False
performance_seen = False
if not therm_out.strip():
    print("ERROR: Thermal telemetry returned no data", file=sys.stderr)
    sys.exit(15)

for line in therm_out.splitlines():
    normalized = line.strip().lower().replace("_", " ")
    if "no thermal warning level has been recorded" in normalized:
        thermal_seen = True
        continue
    if "no performance warning level has been recorded" in normalized:
        performance_seen = True
        continue

    warning = re.search(r"\b(thermal|performance)\s+warning(?:\s+level)?(?:\s*[:=]\s*|\s+)(-?\d+)\b", normalized)
    if warning:
        level = int(warning.group(2))
        if warning.group(1) == "thermal":
            thermal_seen = True
        else:
            performance_seen = True
        if level != 0:
            therm_warning = line.strip()
            print(f"SAFETY_STOP: System thermal/performance warning: {therm_warning}", file=sys.stderr)
            sys.exit(15)
        continue

    if "thermal warning" in normalized or "performance warning" in normalized:
        print(f"ERROR: Unrecognized thermal warning telemetry: {line.strip()}", file=sys.stderr)
        sys.exit(15)

    limit = re.search(r"\b(cpu speed|scheduler) limit\s*=\s*(\d+)\b", normalized)
    if limit:
        performance_seen = True
        percent = int(limit.group(2))
        if percent != 100:
            therm_warning = f"{limit.group(1)} limit is {percent}%"
            print(f"SAFETY_STOP: System thermal/performance warning: {therm_warning}", file=sys.stderr)
            sys.exit(15)
    elif "cpu speed limit" in normalized or "scheduler limit" in normalized:
        print(f"ERROR: Unrecognized thermal performance limit: {line.strip()}", file=sys.stderr)
        sys.exit(15)

if not thermal_seen or not performance_seen:
    print("ERROR: Thermal telemetry format was unrecognized or incomplete", file=sys.stderr)
    sys.exit(15)

# 3. Memory pressure & swap telemetry probe
mock_mem_fail = os.getenv("MOCK_MEM_FAIL")
if mock_mem_fail:
    print(f"ERROR: Memory telemetry failure: {mock_mem_fail}", file=sys.stderr)
    sys.exit(16)

mock_mem_pct = os.getenv("MOCK_MEM_FREE_PCT")
if mock_mem_pct is not None:
    mem_free_pct = int(mock_mem_pct)
else:
    if not shutil.which("memory_pressure"):
        print("ERROR: Memory telemetry unavailable (memory_pressure not found)", file=sys.stderr)
        sys.exit(16)
    try:
        mp_res = subprocess.run(["memory_pressure", "-Q"], capture_output=True, text=True, timeout=5)
        if mp_res.returncode != 0:
            print(f"ERROR: memory_pressure failed with code {mp_res.returncode}", file=sys.stderr)
            sys.exit(16)
        m_mp = re.search(r"System-wide memory free percentage:\s*(\d+)%", mp_res.stdout)
        if not m_mp:
            print("ERROR: Unable to parse free memory percentage from memory_pressure", file=sys.stderr)
            sys.exit(16)
        mem_free_pct = int(m_mp.group(1))
    except Exception as e:
        print(f"ERROR: Memory pressure probe failed: {e}", file=sys.stderr)
        sys.exit(16)

min_mem_pct = int(os.getenv("MIN_FREE_MEM_PCT", "10"))
if mem_free_pct < min_mem_pct:
    print(f"SAFETY_STOP: Free memory ({mem_free_pct}%) < minimum threshold ({min_mem_pct}%)", file=sys.stderr)
    sys.exit(17)

mock_swap_free = os.getenv("MOCK_SWAP_FREE_MB")
mock_swap_used = os.getenv("MOCK_SWAP_USED_MB")
if mock_swap_free is not None or mock_swap_used is not None:
    swap_free_mb = float(mock_swap_free) if mock_swap_free is not None else 4096.0
    swap_used_mb = float(mock_swap_used) if mock_swap_used is not None else 0.0
else:
    if not shutil.which("sysctl"):
        print("ERROR: Swap telemetry unavailable (sysctl not found)", file=sys.stderr)
        sys.exit(18)
    try:
        su_res = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True, timeout=5)
        if su_res.returncode != 0:
            print(f"ERROR: sysctl vm.swapusage failed with code {su_res.returncode}", file=sys.stderr)
            sys.exit(18)
        m_su = re.search(r"total\s*=\s*([\d\.]+)M\s+used\s*=\s*([\d\.]+)M\s+free\s*=\s*([\d\.]+)M", su_res.stdout)
        if not m_su:
            print("ERROR: Unable to parse swap usage from sysctl", file=sys.stderr)
            sys.exit(18)
        swap_used_mb = float(m_su.group(2))
        swap_free_mb = float(m_su.group(3))
    except Exception as e:
        print(f"ERROR: Swap usage probe failed: {e}", file=sys.stderr)
        sys.exit(18)

min_swap_mb = float(os.getenv("MIN_FREE_SWAP_MB", "2048"))
if swap_free_mb < min_swap_mb:
    print(f"SAFETY_STOP: Free swap ({swap_free_mb:.2f} MiB) < minimum threshold ({min_swap_mb:.2f} MiB)", file=sys.stderr)
    sys.exit(19)

max_swap_used_mb = float(os.getenv("MAX_SWAP_USED_MB", "20480"))
if swap_used_mb >= max_swap_used_mb:
    print(f"SAFETY_STOP: Swap used ({swap_used_mb:.2f} MiB) >= maximum threshold ({max_swap_used_mb:.2f} MiB)", file=sys.stderr)
    sys.exit(20)

# 4. Disk telemetry probe
try:
    usage = shutil.disk_usage(screening_dir)
    free_disk_mb = usage.free // (1024 * 1024)
except Exception as e:
    print(f"ERROR: Disk telemetry unreadable: {e}", file=sys.stderr)
    sys.exit(13)

min_disk_mb = int(os.getenv("MIN_DISK_MB", "500"))
if free_disk_mb < min_disk_mb:
    print(f"SAFETY_STOP: Free disk space ({free_disk_mb} MB) < minimum ({min_disk_mb} MB)", file=sys.stderr)
    sys.exit(14)

p_src = "AC" if is_ac else "Battery"
print(f"power={p_src} ({batt_pct}%), memory_free={mem_free_pct}%, swap_used={swap_used_mb:.1f}MiB, swap_free={swap_free_mb:.1f}MiB, disk_free={free_disk_mb}MB, thermal_warning={therm_warning}")
sys.exit(0)
PY
}

do_status() {
  echo "=== Continuous Screening Status ==="
  if [ -f "$PID_FILE" ]; then
    if is_validated_supervisor "$PID_FILE"; then
      local pid
      pid="$("$PY" -c 'import json, sys; print(json.load(open(sys.argv[1]))["pid"])' "$PID_FILE" 2>/dev/null || true)"
      echo "State: RUNNING (PID $pid)"
    else
      echo "State: STOPPED (stale or unverified PID record)"
    fi
  else
    echo "State: STOPPED"
  fi

  if [ -f "$SCOREBOARD_FILE" ]; then
    echo ""
    echo "=== Cumulative Scoreboard ==="
    "$PY" - "$SCOREBOARD_FILE" <<'PY'
import json, sys
try:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Total Games Played : {data.get('total_games', 0)}")
    print(f"Batches Completed  : {data.get('batches_completed', 0)}")
    print(f"Batches Failed     : {data.get('batches_failed', 0)}")
    w = data.get('youloss_wins', 0)
    l = data.get('baseline_wins', 0)
    d = data.get('draws', 0)
    print(f"Score Record (W/D/L): {w}W - {d}D - {l}L")
    tot = data.get('total_games', 0)
    if tot > 0:
        pts = w + 0.5 * d
        pct = (pts / tot) * 100.0
        print(f"Score Percentage   : {pct:.2f}% ({pts}/{tot})")
    print(f"Last Updated       : {data.get('last_updated_at', 'never')}")
except Exception as e:
    print(f"Error parsing scoreboard: {e}")
PY
  fi
}

do_stop() {
  local record_file=""
  if [ -f "$LOCK_OWNER_FILE" ] && is_validated_supervisor "$LOCK_OWNER_FILE"; then
    record_file="$LOCK_OWNER_FILE"
  elif [ -f "$PID_FILE" ] && is_validated_supervisor "$PID_FILE"; then
    record_file="$PID_FILE"
  fi

  if [ -z "$record_file" ]; then
    if [ -e "$LOCK_DIR" ]; then
      echo "Screening lock owner cannot be verified. Leaving PID and lock records untouched."
    elif [ -f "$PID_FILE" ]; then
      echo "PID record does not match an active screening supervisor. Leaving unharmed; process and lock are untouched."
    else
      echo "No screening process running."
    fi
    return 0
  fi

  local pid
  pid="$("$PY" -c 'import json, sys; print(json.load(open(sys.argv[1]))["pid"])' "$record_file" 2>/dev/null || true)"
  if [ -z "$pid" ] || ! is_pid_alive "$pid"; then
    echo "Validated screening record is stale. Leaving lock in place for manual recovery."
    return 0
  fi

  echo "Stopping validated screening supervisor PID $pid..."
  kill -TERM "$pid" 2>/dev/null || true
  for _ in {1..30}; do
    if ! is_pid_alive "$pid"; then
      echo "Stopped successfully; supervisor cleanup owns its PID and lock records."
      return 0
    fi
    sleep 0.5
  done

  if is_validated_supervisor "$record_file"; then
    echo "Process $pid did not exit cleanly, sending KILL..."
    kill -KILL "$pid" 2>/dev/null || true
    for _ in {1..10}; do
      if ! is_pid_alive "$pid"; then
        echo "Stopped; stale lock is preserved because the supervisor could not clean up."
        return 0
      fi
      sleep 0.2
    done
  else
    echo "PID $pid identity changed before KILL. Leaving it unharmed."
  fi
  echo "Supervisor remains active or unverified; leaving lock records untouched." >&2
  return 1
}

record_incident() {
  local batch_rundir="$1"
  local reason="$2"
  "$PY" - "$SCOREBOARD_FILE" "$batch_rundir" "$reason" <<'PY'
import json, os, sys
from datetime import datetime, timezone

sb_path = sys.argv[1]
rundir = sys.argv[2]
reason = sys.argv[3]

sb = {
    "started_at": datetime.now(timezone.utc).isoformat(),
    "last_updated_at": datetime.now(timezone.utc).isoformat(),
    "batches_completed": 0,
    "batches_failed": 0,
    "total_games": 0,
    "youloss_wins": 0,
    "baseline_wins": 0,
    "draws": 0,
    "recent_batches": [],
    "incidents": []
}

if os.path.isfile(sb_path):
    with open(sb_path, "r", encoding="utf-8") as f:
        sb = json.load(f)
    if not isinstance(sb, dict):
        raise SystemExit("scoreboard.json must contain a JSON object")

sb["last_updated_at"] = datetime.now(timezone.utc).isoformat()
sb["batches_failed"] = sb.get("batches_failed", 0) + 1
games = int(sb.get("total_games", 0))
points = int(sb.get("youloss_wins", 0)) + 0.5 * int(sb.get("draws", 0))
sb["points"] = points
sb["score_pct"] = round(points * 100.0 / games, 2) if games else 0.0
sb.setdefault("incidents", []).append({
    "rundir": rundir,
    "reason": reason,
    "time": datetime.now(timezone.utc).isoformat()
})
sb["incidents"] = sb["incidents"][-50:]

tmp_file = f"{sb_path}.{os.getpid()}.tmp"
with open(tmp_file, "w", encoding="utf-8") as f:
    json.dump(sb, f, indent=2)
os.replace(tmp_file, sb_path)
PY
}

update_scoreboard() {
  local batch_rundir="$1"
  local child_exit="${2:-0}"
  "$PY" - "$SCOREBOARD_FILE" "$batch_rundir" "$child_exit" <<'PY'
import json, os, re, sys
from datetime import datetime, timezone

sb_path = sys.argv[1]
rundir = sys.argv[2]
meta_path = os.path.join(rundir, "meta.json")
log_path = os.path.join(rundir, "match.log")

sb = {
    "started_at": datetime.now(timezone.utc).isoformat(),
    "last_updated_at": datetime.now(timezone.utc).isoformat(),
    "batches_completed": 0,
    "batches_failed": 0,
    "total_games": 0,
    "youloss_wins": 0,
    "baseline_wins": 0,
    "draws": 0,
    "recent_batches": [],
    "incidents": []
}

if os.path.isfile(sb_path):
    with open(sb_path, "r", encoding="utf-8") as f:
        sb = json.load(f)
    if not isinstance(sb, dict):
        raise SystemExit("scoreboard.json must contain a JSON object")

sb["last_updated_at"] = datetime.now(timezone.utc).isoformat()

def refresh_score_summary():
    games = int(sb.get("total_games", 0))
    points = int(sb.get("youloss_wins", 0)) + 0.5 * int(sb.get("draws", 0))
    sb["points"] = points
    sb["score_pct"] = round(points * 100.0 / games, 2) if games else 0.0

def fail_batch(reason: str):
    sb["batches_failed"] = sb.get("batches_failed", 0) + 1
    refresh_score_summary()
    sb.setdefault("incidents", []).append({
        "rundir": rundir,
        "reason": reason,
        "time": datetime.now(timezone.utc).isoformat()
    })
    sb["incidents"] = sb["incidents"][-50:]
    tmp_path = f"{sb_path}.{os.getpid()}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(sb, f, indent=2)
    os.replace(tmp_path, sb_path)
    print("failed")
    sys.exit(0)

child_exit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
if child_exit != 0:
    fail_batch(f"Match child exited with non-zero status ({child_exit})")

if not os.path.isfile(meta_path):
    fail_batch("Missing meta.json")
if not os.path.isfile(log_path):
    fail_batch("Missing match.log")

try:
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
except Exception as e:
    fail_batch(f"Malformed meta.json: {e}")

# Strict validation of all harness exit codes
for field, name in [
    ("exit_fastchess", "Fastchess"),
    ("exit_checker", "Checker"),
    ("exit_time_profile", "Time profile"),
    ("exit_tee", "Tee output"),
]:
    val = str(meta.get(field, "missing"))
    if val != "0":
        fail_batch(f"{name} exited with non-zero status ({val})")

if meta.get("timeout") in (1, True, "1"):
    fail_batch("Batch timed out")

# Extract the last complete cumulative fastchess summary. Fastchess emits
# intermediate summaries during a match, so the first one may undercount games.
summary = None
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        m = re.search(
            r"Games\s*:\s*(\d+)\s*,\s*Wins\s*:\s*(\d+)\s*,\s*"
            r"Losses\s*:\s*(\d+)\s*,\s*Draws\s*:\s*(\d+)",
            line,
            re.I,
        )
        if m:
            summary = tuple(int(value) for value in m.groups())

if summary is None:
    fail_batch("Unable to parse complete Games/Wins/Losses/Draws summary from match.log")

summary_games, wins, losses, draws = summary
log_total = wins + losses + draws
if log_total != summary_games:
    fail_batch(
        f"Inconsistent final match.log summary: Games is {summary_games}, "
        f"but Wins/Losses/Draws total {log_total}"
    )

expected = meta.get("expected_games")
completed = meta.get("completed_games")
is_sprt = bool(meta.get("sprt"))

if completed is None:
    fail_batch("Missing meta.completed_games")
if log_total != int(completed):
    fail_batch(f"Game count mismatch: match.log has {log_total}, meta.completed_games is {completed}")

if not is_sprt and expected is None:
    fail_batch("Missing meta.expected_games for fixed run")
if not is_sprt and log_total != int(expected):
    fail_batch(f"Incomplete fixed run: match.log has {log_total}, meta.expected_games is {expected}")

# Valid completed batch
sb["batches_completed"] = sb.get("batches_completed", 0) + 1
sb["total_games"] = sb.get("total_games", 0) + log_total
sb["youloss_wins"] = sb.get("youloss_wins", 0) + wins
sb["baseline_wins"] = sb.get("baseline_wins", 0) + losses
sb["draws"] = sb.get("draws", 0) + draws
refresh_score_summary()

sb.setdefault("recent_batches", []).append({
    "rundir": rundir,
    "time": datetime.now(timezone.utc).isoformat(),
    "wins": wins,
    "losses": losses,
    "draws": draws,
    "exit_fastchess": meta.get("exit_fastchess"),
    "exit_checker": meta.get("exit_checker")
})
sb["recent_batches"] = sb["recent_batches"][-50:]

tmp_path = f"{sb_path}.{os.getpid()}.tmp"
with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(sb, f, indent=2)
os.replace(tmp_path, sb_path)
print("completed")
PY
}

cleanup() {
  echo "Screening received termination signal. Cleaning up..."
  if [ -n "$CHILD_PID" ] && is_pid_alive "$CHILD_PID"; then
    echo "Terminating child process tree for PID $CHILD_PID..."
    terminate_child_tree "$CHILD_PID" "${CHILD_TOKEN:-}"
  fi
  if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
    kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
    wait "$CAFFEINATE_PID" 2>/dev/null || true
  fi
  rm -rf "$PID_FILE" "$LOCK_DIR"
  echo "Screening harness cleanly stopped."
  exit 0
}

acquire_startup_lock() {
  if [ -f "$PID_FILE" ]; then
    if is_validated_supervisor "$PID_FILE"; then
      echo "FAIL: Screening supervisor already running with validated PID record" >&2
      exit 1
    fi
    rm -f "$PID_FILE"
  fi

  if mkdir "$LOCK_DIR" 2>/dev/null; then
    write_pid_record "$LOCK_OWNER_FILE"
    return 0
  fi

  if { [ -f "$PID_FILE" ] && is_validated_supervisor "$PID_FILE"; } || \
     { [ -f "$LOCK_OWNER_FILE" ] && is_validated_supervisor "$LOCK_OWNER_FILE"; }; then
    echo "FAIL: Screening supervisor already running with validated PID/lock record" >&2
  else
    echo "FAIL: Screening lock exists but its owner cannot be verified; preserving it" >&2
  fi
  exit 1
}

do_start() {
  if ! validate_bounded_config; then
    exit 2
  fi
  acquire_startup_lock

  if [ -f "$PID_FILE" ]; then
    if is_validated_supervisor "$PID_FILE"; then
      echo "FAIL: Screening supervisor already running with validated PID record" >&2
      exit 1
    fi
    rm -f "$PID_FILE"
  fi

  write_pid_record "$PID_FILE"
  trap cleanup SIGINT SIGTERM SIGHUP

  echo "=== Starting Continuous Screening Loop ==="
  echo "PID: $$"
  echo "Time Control: $TC"
  echo "Rounds per batch: $ROUNDS_PER_BATCH"
  echo "Max batches: $MAX_BATCHES (0=unlimited)"
  echo "Threads: $THREADS | Concurrency: $CONC | Hash: ${HASH_MB}MB | Overhead: ${MOVE_OVERHEAD_MS}ms"
  echo "Max batch wall-clock: ${TIME_CAP_S}s | Overall run deadline: ${DEADLINE_S}s (${DEADLINE_HOURS}h)"
  echo "Logs and scoreboard at: $SCREENING_DIR"

  log_effective_config

  local batch_num=0
  local completed_batches=0
  SUPERVISOR_START="$(date +%s)"

  while true; do
    local now_s
    now_s="$(date +%s)"
    local elapsed=$((now_s - SUPERVISOR_START))
    if [ "$elapsed" -ge "$DEADLINE_S" ]; then
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] Hard deadline reached (${DEADLINE_S}s). Stopping screening loop cleanly."
      if [ "$MAX_BATCHES" -gt 0 ] && [ "$completed_batches" -lt "$MAX_BATCHES" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bounded session aborted: deadline reached before completing all batches. Stopping fixed-size experiment at $completed_batches/$MAX_BATCHES validated batches." | tee -a "$RUN_LOG" >&2
        if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
          kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
        fi
        rm -rf "$PID_FILE" "$LOCK_DIR"
        exit 1
      fi
      if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
        kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
      fi
      rm -rf "$PID_FILE" "$LOCK_DIR"
      exit 0
    fi

    batch_num=$((batch_num + 1))
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pre-batch check #$batch_num..."

    # Pre-batch fail-closed telemetry check
    local telemetry_info
    set +e
    telemetry_info="$(check_safety_telemetry "$SCREENING_DIR" 2>&1)"
    local tele_rc=$?
    set -e

    if [ "$tele_rc" -ne 0 ]; then
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] SAFETY STOP before batch #$batch_num: $telemetry_info" | tee -a "$RUN_LOG" >&2
      if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
        kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
      fi
      rm -rf "$PID_FILE" "$LOCK_DIR"
      exit 1
    fi

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Telemetry nominal: $telemetry_info" | tee -a "$RUN_LOG"

    # Start caffeinate assertion process only after AC and safety preflight succeeds
    if [ -z "$CAFFEINATE_PID" ] || ! is_pid_alive "$CAFFEINATE_PID"; then
      caffeinate -s -w "$$" &
      CAFFEINATE_PID=$!
      sleep 0.1
      if ! is_pid_alive "$CAFFEINATE_PID"; then
        echo "ERROR: Failed to start macOS caffeinate assertion process" | tee -a "$RUN_LOG" >&2
        rm -rf "$PID_FILE" "$LOCK_DIR"
        exit 1
      fi
    fi

    # Launch batch via tm_match.sh with unique run token
    CHILD_TOKEN="token_${batch_num}_$$_$(date +%s)_$RANDOM"
    local tmp_batch_log
    tmp_batch_log="$(mktemp)"
    set +e
    THREADS="$THREADS" CONC="$CONC" HASH_MB="$HASH_MB" MOVE_OVERHEAD_MS="$MOVE_OVERHEAD_MS" TIME_CAP_S="$TIME_CAP_S" \
      bash -c ": 'tm_match.sh' 'token=$CHILD_TOKEN'; bash '$TM_MATCH_SCRIPT' '$TC' '$ROUNDS_PER_BATCH'" >"$tmp_batch_log" 2>&1 &
    CHILD_PID=$!

    local abort_reason=""
    while is_pid_alive "$CHILD_PID"; do
      local check_now
      check_now="$(date +%s)"
      if [ $((check_now - SUPERVISOR_START)) -ge "$DEADLINE_S" ]; then
        abort_reason="DEADLINE_EXCEEDED"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Supervisor deadline reached (${DEADLINE_S}s). Stopping active match..." | tee -a "$RUN_LOG"
        terminate_child_tree "$CHILD_PID" "$CHILD_TOKEN"
        break
      fi

      local mid_telemetry
      if ! mid_telemetry="$(check_safety_telemetry "$SCREENING_DIR" 2>&1)"; then
        abort_reason="SAFETY_VIOLATION: $mid_telemetry"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] SAFETY ALERT during batch #$batch_num: $mid_telemetry. Cleanly stopping match..." | tee -a "$RUN_LOG"
        terminate_child_tree "$CHILD_PID" "$CHILD_TOKEN"
        break
      fi

      sleep 2
    done

    set +e
    wait "$CHILD_PID"
    local rc=$?
    set -e
    CHILD_PID=""
    CHILD_TOKEN=""

    cat "$tmp_batch_log" >>"$RUN_LOG"

    local batch_rundir
    batch_rundir="$(grep -E '^rundir=' "$tmp_batch_log" 2>/dev/null | tail -n 1 | sed -E 's/^rundir=//g' || true)"
    rm -f "$tmp_batch_log"

    if [ -n "$abort_reason" ]; then
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] Batch #$batch_num aborted: $abort_reason (child exit code: $rc)." | tee -a "$RUN_LOG"
      if [ -n "$batch_rundir" ]; then
        record_incident "$batch_rundir" "$abort_reason"
      elif [ "$abort_reason" = "DEADLINE_EXCEEDED" ]; then
        record_incident "(batch #$batch_num, no rundir)" "$abort_reason"
      fi
      if [ "$abort_reason" = "DEADLINE_EXCEEDED" ]; then
        if [ "$MAX_BATCHES" -gt 0 ] && [ "$completed_batches" -lt "$MAX_BATCHES" ]; then
          echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bounded session aborted: batch #$batch_num aborted (DEADLINE_EXCEEDED). Stopping fixed-size experiment at $completed_batches/$MAX_BATCHES validated batches." | tee -a "$RUN_LOG" >&2
          if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
            kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
          fi
          rm -rf "$PID_FILE" "$LOCK_DIR"
          exit 1
        fi
        if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
          kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
        fi
        rm -rf "$PID_FILE" "$LOCK_DIR"
        exit 0
      fi
      if [ "$MAX_BATCHES" -gt 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bounded session aborted: batch #$batch_num aborted ($abort_reason). Stopping fixed-size experiment at $completed_batches/$MAX_BATCHES validated batches." | tee -a "$RUN_LOG" >&2
        if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
          kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
        fi
        rm -rf "$PID_FILE" "$LOCK_DIR"
        exit 1
      fi
      echo "Waiting 30s after safety alert before retrying..."
      sleep 30
      continue
    fi

    if [ -n "$batch_rundir" ] && [ -d "$batch_rundir" ]; then
      set +e
      local score_result
      score_result="$(update_scoreboard "$batch_rundir" "$rc" 2>&1)"
      local score_rc=$?
      set -e

      if [ "$score_rc" -ne 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: scoreboard update failed (exit $score_rc): $score_result" | tee -a "$RUN_LOG" >&2
        if [ "$MAX_BATCHES" -gt 0 ]; then
          echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bounded session aborted: batch #$batch_num invalid (scoreboard update failed). Stopping fixed-size experiment at $completed_batches/$MAX_BATCHES validated batches." | tee -a "$RUN_LOG" >&2
          if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
            kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
          fi
          rm -rf "$PID_FILE" "$LOCK_DIR"
          exit 1
        fi
      elif [ "$score_result" = "completed" ] && [ "$rc" -eq 0 ]; then
        completed_batches=$((completed_batches + 1))
        if [ "$MAX_BATCHES" -gt 0 ]; then
          echo "[$(date '+%Y-%m-%d %H:%M:%S')] Batch #$batch_num complete (child exit code: 0). Rundir: $batch_rundir (validated $completed_batches/$MAX_BATCHES)" | tee -a "$RUN_LOG"
        else
          echo "[$(date '+%Y-%m-%d %H:%M:%S')] Batch #$batch_num complete (child exit code: 0). Rundir: $batch_rundir" | tee -a "$RUN_LOG"
        fi

        # Run diagnostic analyzer only for a verified completed batch.
        if [ -f "$ROOT/testing/analyze_screening.py" ]; then
          set +e
          local analyzer_log="$SCREENING_DIR/analyzer_last.log"
          "$PY" "$ROOT/testing/analyze_screening.py" --scoreboard "$SCOREBOARD_FILE" --output-dir "$SCREENING_DIR" >"$analyzer_log" 2>&1
          local analyzer_rc=$?
          set -e
          cat "$analyzer_log" >>"$RUN_LOG"
          if [ "$analyzer_rc" -ne 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: analyze_screening.py failed with exit code $analyzer_rc" | tee -a "$RUN_LOG" >&2
          fi
        fi

        if [ "$MAX_BATCHES" -gt 0 ] && [ "$completed_batches" -ge "$MAX_BATCHES" ]; then
          echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bounded session complete: $completed_batches/$MAX_BATCHES validated batches." | tee -a "$RUN_LOG"
          if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
            kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
          fi
          rm -rf "$PID_FILE" "$LOCK_DIR"
          exit 0
        fi
      else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Batch #$batch_num rejected from completed results: $score_result (child exit code: $rc). Rundir: $batch_rundir" | tee -a "$RUN_LOG"
        if [ "$MAX_BATCHES" -gt 0 ]; then
          echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bounded session aborted: batch #$batch_num failed validation ($score_result, child exit $rc). Stopping fixed-size experiment at $completed_batches/$MAX_BATCHES validated batches." | tee -a "$RUN_LOG" >&2
          if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
            kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
          fi
          rm -rf "$PID_FILE" "$LOCK_DIR"
          exit 1
        fi
      fi
    else
      record_incident "$batch_rundir" "Missing or invalid run directory (child exit code: $rc)"
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] Batch #$batch_num rejected: rundir could not be parsed (child exit code: $rc)." | tee -a "$RUN_LOG"
      if [ "$MAX_BATCHES" -gt 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bounded session aborted: batch #$batch_num invalid (missing rundir). Stopping fixed-size experiment at $completed_batches/$MAX_BATCHES validated batches." | tee -a "$RUN_LOG" >&2
        if [ -n "$CAFFEINATE_PID" ] && is_pid_alive "$CAFFEINATE_PID"; then
          kill -TERM "$CAFFEINATE_PID" 2>/dev/null || true
        fi
        rm -rf "$PID_FILE" "$LOCK_DIR"
        exit 1
      fi
    fi

    sleep "$PAUSE_S"
  done
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  ACTION="${1:-start}"
  case "$ACTION" in
    start)
      do_start
      ;;
    status)
      do_status
      ;;
    stop)
      do_stop
      ;;
    *)
      echo "Usage: $0 [start|status|stop]" >&2
      exit 2
      ;;
  esac
fi

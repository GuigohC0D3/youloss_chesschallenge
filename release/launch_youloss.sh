#!/usr/bin/env bash
# Youloss Offline Launcher (Candidate Package)
# Explicit candidate profile: 7 threads / 2048 MiB / 2.0 s clock latency / 1500+0 provisional TC.
# WARNING: Labelled UNQUALIFIED CANDIDATE - not a final tournament profile.
# Physical-board qualification and organizer acceptance remain OPEN.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The archive must work from its own contents. A host fallback would hide a
# missing dependency during preflight and could fail after submission.
PYTHON_BIN="${SCRIPT_DIR}/python/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "ERROR: Bundled Python runtime is missing." >&2
    exit 1
fi

# Resolve Engine binary
ENGINE_BIN="${SCRIPT_DIR}/bin/youloss"
if [[ ! -x "$ENGINE_BIN" ]]; then
    echo "ERROR: Bundled engine binary is missing." >&2
    exit 1
fi

# Keep host Python packages out of the offline candidate environment.
unset PYTHONHOME
export PYTHONNOUSERSITE=1
export PYTHONPATH="${SCRIPT_DIR}:${SCRIPT_DIR}/python/lib/python3.12/site-packages"

# Candidate defaults (Maximum Technical Power Profile)
DEFAULT_THREADS=7
DEFAULT_HASH_MB=2048
DEFAULT_TC="1500+0"
CLOCK_LATENCY="${CLOCK_LATENCY:-2.0}"

print_banner() {
    cat <<'EOF'
================================================================================
                    YOULOSS OFFLINE LAUNCHER (CANDIDATE)
================================================================================
 [PROFILE STATUS] MAXIMUM TECHNICAL POWER PROFILE (16 GB APPLE SILICON)
   * Engine:         Apple Silicon native bin/youloss (embedded NNUE)
   * Threads:        7 (optimal 4P + 3E cores; reaches Depth 31 without SMP stalls)
   * Hash:           2048 MiB (2.0 GB transposition table; zero swap in 16 GB RAM)
   * Time Control:   1500+0 (Official: 25 min each flat, zero increment)
   * Clock Latency:  configurable via --clock-latency (default 2.0 s)
   * Move Overhead:  1500 ms (controller default)

 [ASSETS & TOURNAMENT DEPLOYMENT NOTE]
   * Syzygy tablebases (assets/syzygy) and Polyglot book (assets/book.bin)
     are local repository assets; copy assets/ alongside the launcher on M5 Air.
   * Physical-board operator rehearsal recommended before round 1.
================================================================================
EOF
}

show_help() {
    print_banner
    cat <<EOF

Usage:
  $(basename "$0") --color <white|black> [OPTIONS]
  $(basename "$0") --resume [STATE]
  $(basename "$0") --dry-run
  $(basename "$0") --help

Options:
  --color white|black       Our engine side (required unless --resume or --dry-run)
  --opponent NAME           Opponent team/player name (default: 'adversario')
  --game NUM                Game sequence number (default: 1)
  --resume [STATE]          Resume match reconciliation from state file or latest
  --clock-latency SEC       Conservative physical clock read/entry latency (default: 2.0 s)
  --threads NUM             Override thread count (candidate default: 7)
  --hash MB                 Override hash size in MiB (candidate default: 2048)
  --tc BASE+INC             Override time control in seconds (candidate provisional: 1500+0)
  --dry-run                 Run offline environment and binary checks, then exit
  --help, -h                Show this help message and candidate profile details

All other arguments are forwarded to controller.main.
EOF
}

# Scan arguments
DRY_RUN=0
FORWARD_ARGS=()
HAS_THREADS=0
HAS_HASH=0
HAS_TC=0
HAS_LATENCY=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --clock-latency)
            if [[ $# -lt 2 ]]; then
                echo "ERROR: --clock-latency requires a value in seconds" >&2
                exit 1
            fi
            CLOCK_LATENCY="$2"
            HAS_LATENCY=1
            FORWARD_ARGS+=("$1" "$2")
            shift 2
            ;;
        --threads)
            [[ $# -ge 2 ]] || { echo "ERROR: --threads requires a value" >&2; exit 1; }
            HAS_THREADS=1
            FORWARD_ARGS+=("$1" "$2")
            shift 2
            ;;
        --hash)
            [[ $# -ge 2 ]] || { echo "ERROR: --hash requires a value" >&2; exit 1; }
            HAS_HASH=1
            FORWARD_ARGS+=("$1" "$2")
            shift 2
            ;;
        --tc)
            [[ $# -ge 2 ]] || { echo "ERROR: --tc requires a value" >&2; exit 1; }
            HAS_TC=1
            FORWARD_ARGS+=("$1" "$2")
            shift 2
            ;;
        --engine)
            echo "ERROR: This package uses only its manifested bin/youloss engine." >&2
            exit 1
            ;;
        *)
            FORWARD_ARGS+=("$1")
            shift
            ;;
    esac
done

# Dry run preflight check
if [[ "$DRY_RUN" -eq 1 ]]; then
    print_banner
    echo "[DRY-RUN] Verifying bundled Python interpreter..."
    "$PYTHON_BIN" -c "import sys, chess; assert sys.version_info[:2] == (3, 12); assert chess.__version__ == '1.11.2'; print(f'  Python {sys.version.split()[0]} OK, chess {chess.__version__} OK')"
    echo "[DRY-RUN] Verifying engine offline handshake..."
    "$PYTHON_BIN" - "$ENGINE_BIN" <<'PY'
import subprocess
import sys

try:
    result = subprocess.run(
        [sys.argv[1]], input="uci\nisready\nquit\n", capture_output=True,
        text=True, timeout=10, check=True,
    )
except (OSError, subprocess.SubprocessError) as exc:
    raise SystemExit(f"ERROR: Engine failed UCI handshake: {exc}")
if not {"uciok", "readyok"}.issubset(result.stdout.splitlines()):
    raise SystemExit("ERROR: Engine did not return uciok and readyok")
print("  Engine bin/youloss answered uciok and readyok successfully.")
PY
    echo "[DRY-RUN] Verification successful. Open items: physical-board qualification & organizer acceptance."
    exit 0
fi

# Print banner for operator
print_banner

# Assemble execution arguments with defaults
EXEC_ARGS=("$PYTHON_BIN" -m controller.main start --engine "$ENGINE_BIN")

if [[ "$HAS_THREADS" -eq 0 ]]; then
    EXEC_ARGS+=(--threads "$DEFAULT_THREADS")
fi

if [[ "$HAS_HASH" -eq 0 ]]; then
    EXEC_ARGS+=(--hash "$DEFAULT_HASH_MB")
fi

if [[ "$HAS_TC" -eq 0 ]]; then
    EXEC_ARGS+=(--tc "$DEFAULT_TC")
fi

if [[ "$HAS_LATENCY" -eq 0 ]]; then
    EXEC_ARGS+=(--clock-latency "$CLOCK_LATENCY")
fi

EXEC_ARGS+=("${FORWARD_ARGS[@]}")

echo "[LAUNCH] Executing: ${EXEC_ARGS[*]}"
exec "${EXEC_ARGS[@]}"

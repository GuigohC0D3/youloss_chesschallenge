#!/usr/bin/env bash
# Valida toolchain necessário para build do engine e do controller.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/platform.sh"
fail=0
check() { if "$@" >/dev/null 2>&1; then echo "OK   $*"; else echo "FAIL $*"; fail=1; fi; }

if is_mac; then
  check clang++ --version
  check xcrun -f llvm-profdata
  PY="$(command -v python3)"
else
  UCRT=/c/msys64/ucrt64/bin
  export PATH="$UCRT:/c/msys64/usr/bin:$PATH"
  check "$UCRT/g++" --version
  PY="$(command -v py >/dev/null && py -3.12 -c 'import sys;print(sys.executable)' 2>/dev/null)"
fi
check make --version
check git --version

if [ -z "$PY" ] || [[ "$PY" == *WindowsApps* ]] \
  || ! "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 12))' 2>/dev/null; then
  echo "FAIL python >= 3.12 real não encontrado (stub WindowsApps?)"; fail=1
else
  echo "OK   python $PY"
fi
exit $fail

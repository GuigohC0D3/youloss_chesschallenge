#!/usr/bin/env bash
# Valida toolchain necessário para build do engine e do controller.
set -u
fail=0
check() { if "$@" >/dev/null 2>&1; then echo "OK   $*"; else echo "FAIL $*"; fail=1; fi; }

UCRT=/c/msys64/ucrt64/bin
export PATH="$UCRT:/c/msys64/usr/bin:$PATH"

check "$UCRT/g++" --version
check make --version
check git --version

PY="$(command -v py >/dev/null && py -3.12 -c 'import sys;print(sys.executable)' 2>/dev/null)"
if [ -z "$PY" ] || [[ "$PY" == *WindowsApps* ]]; then
  echo "FAIL python 3.12 real não encontrado (stub WindowsApps?)"; fail=1
else
  echo "OK   python $PY"
fi
exit $fail

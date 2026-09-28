# Detecção de plataforma compartilhada pelos scripts. Uso: source depois de definir ROOT.
# Suporta macOS (Apple Silicon, máquina do torneio) e Windows (MSYS2 UCRT64).
# Define: EXE (sufixo de binário), PY (python do .venv), JOBS, PHYS_CORES,
# SHA256 (comando compatível com sha256sum) e as funções is_mac / msys_reexec.

is_mac() { [ "$(uname -s)" = "Darwin" ]; }

if is_mac; then
  EXE=""
  PY="$ROOT/.venv/bin/python"
  JOBS="$(sysctl -n hw.ncpu)"
  # Só núcleos de performance: partidas em núcleos E distorcem a gestão de tempo.
  PHYS_CORES="$(sysctl -n hw.perflevel0.physicalcpu 2>/dev/null || sysctl -n hw.physicalcpu)"
  SHA256="shasum -a 256"
else
  EXE=".exe"
  PY="$ROOT/.venv/Scripts/python"
  JOBS="$(nproc)"
  PHYS_CORES="$(powershell -NoProfile -Command \
    "(Get-CimInstance Win32_Processor | Measure-Object NumberOfCores -Sum).Sum" | tr -d '\r')"
  SHA256="sha256sum"
fi

# No Windows, o make/gcc do MSYS2 perde TMP/TEMP quando chamado pelo Git Bash
# (runtimes msys diferentes) e falha com "Cannot create temporary file in C:\WINDOWS".
# Reexecuta o script chamador dentro do bash do próprio MSYS2 (UCRT64). No-op no macOS.
msys_reexec() {  # $1 = caminho do script relativo ao ROOT
  is_mac && return 0
  [ "${MSYSTEM:-}" = "UCRT64" ] && return 0
  exec env MSYSTEM=UCRT64 CHERE_INVOKING=1 /c/msys64/usr/bin/bash -lc \
    "cd '$(cygpath -u "$ROOT")' && bash $1"
}

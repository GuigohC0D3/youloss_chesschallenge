#!/usr/bin/env bash
# Inicia a interface da partida: Stockfish 19 + YoulossTM, com tabuleiro no navegador, sem rede.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE="$DIR/bin/stockfish"
EXPECTED_BENCH=2497913

show_help() {
    cat <<HELP
Uso:
  ./launch_stockfish.sh              abre a interface no navegador
  ./launch_stockfish.sh --dry-run    confere este Mac (rode antes da partida)
  ./launch_stockfish.sh --help

Opções repassadas à interface:
  --threads N          padrão automático: núcleos P + 1/3 dos E (6 em M4/M5 de 10 núcleos)
  --hash MB            padrão automático: 1/8 da RAM (2048 em 16 GB)
  --clock-latency SEG  desconto por transição do relógio interno (padrão 2.0)
  --port N             padrão 8765
  --no-ponder          não pensa no tempo do adversário
HELP
}

# Arquivo baixado pelo navegador vem em quarentena e o macOS bloquearia o engine.
xattr -dr com.apple.quarantine "$DIR" 2>/dev/null || true

find_python() {
    local candidate
    for candidate in python3 /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
        if command -v "$candidate" >/dev/null 2>&1 &&
            "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 9))' >/dev/null 2>&1; then
            command -v "$candidate"
            return 0
        fi
    done
    return 1
}

PYTHON="$(find_python)" || {
    echo "ERRO: python3 (3.9 ou mais novo) não encontrado." >&2
    echo "Instale com: xcode-select --install" >&2
    exit 1
}
if [[ ! -x "$ENGINE" ]]; then
    echo "ERRO: engine não encontrado em $ENGINE" >&2
    exit 1
fi

unset PYTHONHOME
export PYTHONNOUSERSITE=1
export PYTHONPATH="$DIR:$DIR/vendor"

dry_run() {
    echo "Mac:    $(sysctl -n machdep.cpu.brand_string), macOS $(sw_vers -productVersion)"
    echo "Python: $("$PYTHON" --version) ($PYTHON)"
    "$PYTHON" -c 'import chess, chess.svg, controller.web; print("chess:  " + chess.__version__)'
    "$PYTHON" -c 'from controller.runtime import auto_profile as a; t, h = a(); print(f"Perfil: {t} threads, {h} MiB")'
    local nodes
    nodes="$("$ENGINE" bench 2>&1 | awk '/Nodes searched/ {print $NF}')"
    if [[ "$nodes" != "$EXPECTED_BENCH" ]]; then
        echo "ERRO: bench $nodes, esperado $EXPECTED_BENCH" >&2
        exit 1
    fi
    echo "Engine: Stockfish 19 + YoulossTM, bench $nodes correto"
    echo "Verificação concluída: este Mac pode rodar a partida."
}

for arg in "$@"; do
    case "$arg" in
        --help|-h) show_help; exit 0 ;;
        --dry-run) dry_run; exit 0 ;;
        --engine)
            echo "ERRO: este pacote só usa o bin/stockfish do manifesto." >&2
            exit 1
            ;;
    esac
done

# caffeinate: o Mac não pode dormir no meio da partida. Tampa fechada ainda dorme.
cd "$DIR"
exec caffeinate -dims "$PYTHON" -m controller.web --engine "$ENGINE" "$@"

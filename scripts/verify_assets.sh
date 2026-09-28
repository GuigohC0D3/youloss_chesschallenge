#!/usr/bin/env bash
# Confere os assets contra assets/MANIFEST (offline). Rodar do root do repo.
set -euo pipefail
[ -s assets/MANIFEST ] || { echo "assets/MANIFEST ausente ou vazio" >&2; exit 1; }
(cd assets && sha256sum --check --quiet MANIFEST)
echo "OK: $(wc -l < assets/MANIFEST) arquivos conferem com assets/MANIFEST"

#!/usr/bin/env bash
# Prepara o M5 para as baterias S2/S1/S3 (seção 5 de
# docs/evidence/2026-10-07-m5-project-handoff.md). Fail-closed e idempotente:
# para no primeiro bench/SHA divergente. Rodar do root do repo, no macOS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/platform.sh"

FROZEN_COMMIT=05f03f6
FROZEN_BENCH=2497913
FROZEN_SHA=c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301
DEVPORT_BENCH=1714434
DEV_NET=nn-252f33942263.nnue
LOG="$ROOT/logs/m5_setup.log"

die() { echo "FALHA: $*" >&2; exit 1; }
step() { echo; echo "== $*"; }
bench_of() { "$1" bench 2>&1 | awk '/Nodes searched/ {print $NF}'; }
sha_of() { $SHA256 "$1" | cut -d' ' -f1; }

is_mac || die "este script é só para o M5 (macOS)"
mkdir -p "$ROOT/logs"

step "toolchain"
xcode-select -p >/dev/null || die "Xcode CLT ausente: xcode-select --install"
command -v git >/dev/null || die "git ausente"
bash scripts/check_toolchain.sh

step "python .venv"
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt

step "fastchess"
[ -x tools/fastchess ] || bash scripts/build_fastchess.sh

step "syzygy"
if ! bash scripts/verify_assets.sh 2>/dev/null; then
  bash scripts/fetch_syzygy.sh
  bash scripts/verify_assets.sh
fi

step "candidato bin/youloss_devport"
ENGINE_OUT=youloss_devport bash scripts/build_engine.sh
[ "$(sha_of "engine/src/$DEV_NET" | cut -c1-12)" = "${DEV_NET:3:12}" ] \
  || die "rede $DEV_NET com SHA divergente"
got="$(bench_of bin/youloss_devport)"
[ "$got" = "$DEVPORT_BENCH" ] || die "bench devport $got != $DEVPORT_BENCH"

step "frozen bin/youloss (commit $FROZEN_COMMIT)"
if [ -x bin/youloss ] && [ "$(bench_of bin/youloss)" = "$FROZEN_BENCH" ]; then
  echo "bin/youloss já presente com bench $FROZEN_BENCH; mantido"
else
  wt="$(mktemp -d)/youloss-frozen"
  git worktree add --detach "$wt" "$FROZEN_COMMIT"
  trap 'git -C "$ROOT" worktree remove --force "$wt" 2>/dev/null || true' EXIT
  (cd "$wt" && bash scripts/build_engine.sh)
  got="$(bench_of "$wt/bin/youloss")"
  [ "$got" = "$FROZEN_BENCH" ] || die "bench frozen $got != $FROZEN_BENCH"
  cp "$wt/bin/youloss" bin/youloss
fi
frozen_sha="$(sha_of bin/youloss)"
[ "$frozen_sha" = "$FROZEN_SHA" ] \
  || echo "AVISO: SHA do frozen difere do original (rebuild PGO); registre no log da S2"

step "gates"
.venv/bin/python -m pytest -q
bash scripts/test_engine_tm.sh

{
  echo "$(date -u +%FT%TZ) m5_setup OK commit=$(git rev-parse --short HEAD)"
  echo "  bin/youloss          sha=$frozen_sha bench=$FROZEN_BENCH"
  echo "  bin/youloss_devport  sha=$(sha_of bin/youloss_devport) bench=$DEVPORT_BENCH"
  echo "  net                  $DEV_NET"
} | tee -a "$LOG"
echo
echo "Pronto. Próximo: seção 6 do handoff (lançar S2 na tomada, tampa aberta)."

# Sprint 2 — `youloss_tm` v1 + harness SPRT Implementation Plan

> **Status note (2026-09-30):** This is the original implementation plan, not a
> record that every task or acceptance gate completed. No accepted SPRT result
> is present in tracked project records. The actual event profile is
> provisionally `1500+0`, not the incremented controls used in this draft; see
> `README.md` and the current local-tournament roadmap. The pinned fastchess
> `v1.8.2-alpha` summary uses `Ptnml(0-2): [...]`, not the `Penta:` row assumed
> by the initial checker fixtures. The current checker and tests use the real
> pinned format. Treat code excerpts below as historical plan material unless
> independently checked against the current source.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Avaliar a gestão de tempo autoral (`youloss_tm`) contra o gerenciador original com um harness de SPRT; a não-regressão (`elo0=-5`, `elo1=0`) é um critério proposto, não um resultado assumido.

**Architecture:** O modelo da seção 4 do spec vive em `engine/src/youloss_tm.{h,cpp}` como **funções puras** (`budget`, `iteration_time`), sem dependências do resto do engine. Um executável de teste C++ próprio cobre essas funções. O Stockfish chama essas funções em dois pontos só: no início da busca, para fixar `optimum`/`maximum`, e no fim de cada iteração, para decidir se para. Ambos ficam protegidos por uma flag. Com `YoulossTM=false`, em `movestogo` ou em `nodestime`, o caminho original fica intacto. O harness roda o mesmo binário contra ele mesmo (`YoulossTM=true` × `false`) com aberturas UHO, e dois scripts Python leem o resultado: o do SPRT e o perfil de uso de tempo.

**Tech Stack:** C++17 (g++ MSYS2 UCRT64, Makefile do Stockfish), Stockfish `sf_19`, fastchess 1.8.2-alpha, Python 3.12 + pytest, bash.

**Spec:** `docs/superpowers/specs/2026-09-28-youloss-chess-engine-design.md` (seções 1, 4, 7 e 8/S2)

## Global Constraints

- Commits **sem** linhas `Co-Authored-By` de IA ou qualquer atribuição de IA.
- Opção UCI `YoulossTM`, **padrão `true`**; `false` restaura a gestão de tempo original (spec seção 4).
- Modelo (spec 4): `base = remaining / H(fase) + 0.8 * inc`; `maximum = min(5 * base, 0.25 * remaining)`; reserva de segurança `MoveOverhead` + 1 s abaixo de 10 s; ajustes por iteração: estabilidade da PV, queda de avaliação, lance forçado, lance único claramente melhor, posição decidida.
- `bench` inalterado: `bin/youloss.exe bench` → `Nodes searched : 2497913`. O bench é limitado por profundidade e não usa gestão de tempo, então qualquer mudança nesse número indica que a busca foi alterada.
- Aceite proposto: SPRT `YoulossTM=true` × `false`, **elo0=-5, elo1=0**, alpha=beta=0.05, 1 thread. Os controles precisam ser sem incremento e representativos; `60+0` é screening escalado, não o controle do evento.
- Nenhuma mudança na avaliação/NNUE nem na busca do Stockfish (spec 9). Só a decisão de tempo muda.
- Build sempre por `bash scripts/build_engine.sh` (profile-build, MSYS2 UCRT64).
- Ponder e tuning SPSA ficam para a S3. Os parâmetros nesta sprint são `constexpr` nomeados, prontos para virar opção UCI.
- Downloads (aberturas) só por script, com sha256 em `assets/MANIFEST`.

## Review Focus

1. **Buscas que não são "base + incremento"** (`go movetime`, `go depth`, `go infinite`, `movestogo`, `nodestime`): continuam com o comportamento original, sem que o `youloss_tm` interfira. Teste na Task 2.
2. **Relógio menor que a reserva** (`wtime` < `Move Overhead` + 1 s): o orçamento cai para 1 ms e o engine responde quase na hora, sem perder por tempo. Teste na Task 2.
3. **Lance forçado**: com 1 lance legal, resposta imediata. O original gastava até 500 ms. Teste na Task 2.
4. **Várias threads** (`Threads=4`, como no evento): `bestMoveChanges` é tirado a média por thread, e o tempo gasto continua dentro de `maximum`. Teste na Task 2.
5. **`go ponder` seguido de `ponderhit`** com `YoulossTM=true`: continua devolvendo `bestmove` dentro do limite. O ponder em si é assunto da S3, mas não pode quebrar agora. Teste na Task 2.

## Decisões desta sprint (justificadas)

- **"Lance único claramente melhor"**: a v1 usa como indicador o esforço de nós no melhor lance (`rootMoves[0].effort / nodes`), que o Stockfish já mede, em vez de rodar uma busca de verificação extra na raiz. Custa zero nós; a busca de verificação fica como candidata para a S3.
- **Fallback**: o `youloss_tm` só atua com `wtime/btime` > 0, `movestogo == 0` e `nodestime == 0`. O evento está planejado provisoriamente como 25 minutos por lado sem incremento; nos outros formatos o original continua valendo.
- **`Ponder=true`**: o bônus de +25% do original não se aplica ao nosso orçamento na S2. O ponder é da S3.
- **Gate rápido proposto**: um screening a 10+0 pode preceder um SPRT mais longo a 60+0. O resultado do screening serve para descartar incidentes/regressões óbvias, não para alegar aceitação estatística.
- **Duração**: as estimativas abaixo neste plano eram projeções para controles incrementados e concorrência alta. Não são medições desta máquina nem orçamento aprovado; recalcular após medir jogos a `10+0`/`25+0` com concorrência 1 no M4.

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `engine/src/youloss_tm.h`, `engine/src/youloss_tm.cpp` | Modelo puro: `budget`, `iteration_time`, parâmetros `constexpr` |
| `engine/tests/youloss_tm_test.cpp` | Testes unitários C++ do modelo (sem framework) |
| `scripts/test_engine_tm.sh` | Compila e roda o teste C++ no MSYS2 UCRT64 |
| `engine/src/timeman.h` | + `set_bounds(optimum, maximum)` |
| `engine/src/search.h` | + flag `SearchManager::youlossTM` |
| `engine/src/search.cpp` | Ganchos: início da busca (orçamento) e fim da iteração (parada) |
| `engine/src/engine.cpp` | + opção UCI `YoulossTM` |
| `engine/src/Makefile` | + `youloss_tm.cpp` / `youloss_tm.h` |
| `engine/ORIGIN.md` | Lista das modificações autorais |
| `testing/__init__.py`, `testing/tests/__init__.py` | Pacotes Python dos testes de `testing/` |
| `testing/tests/test_engine_tm.py` | Integração: engine real com `YoulossTM` |
| `scripts/fetch_openings.sh` | Baixa UHO_Lichess_4852_v1.epd + MANIFEST |
| `testing/tm_match.sh` | Match `tm` × `sf` (partidas fixas ou SPRT) |
| `testing/sprt_result.py` | Lê o log do fastchess → H0/H1/inconclusivo |
| `testing/time_profile.py` | Perfil de tempo por engine a partir do PGN |
| `testing/tests/test_sprt_tools.py` | Testes dos dois leitores |
| `docs/sprt/2026-s2-youloss-tm.md` | Registro de calibração e dos SPRTs |

Comandos a partir do root do repo, no Git Bash: `PY=.venv/Scripts/python`.

---

### Task 1: Modelo puro `youloss_tm` + teste C++

**Files:**
- Create: `engine/src/youloss_tm.h`, `engine/src/youloss_tm.cpp`, `engine/tests/youloss_tm_test.cpp`, `scripts/test_engine_tm.sh`

**Interfaces:**
- Consumes: nada (só `<cstdint>`, `<algorithm>`, `<cmath>`).
- Produces (namespace `Stockfish::Youloss`):
  - `struct Budget { int64_t optimum; int64_t maximum; };`
  - `struct BudgetInput { int64_t remaining; int64_t increment; int64_t moveOverhead; double phase; };`
  - `struct IterationInput { double optimum; int stableIterations; double bestMoveChanges; int eval; int previousAverage; int previousIteration; bool decisive; int legalMoves; double bestMoveEffort; };`
  - `constexpr int PawnUnits = 208;`
  - `Budget budget(const BudgetInput&)`, `double iteration_time(const IterationInput&)`

- [ ] **Step 1: Escrever `scripts/test_engine_tm.sh`**

```bash
#!/usr/bin/env bash
# Compila e roda os testes unitários do youloss_tm. Rodar do root do repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Mesmo motivo do build_engine.sh: o gcc do MSYS2 precisa do TMP do próprio MSYS2.
if [ "${MSYSTEM:-}" != "UCRT64" ]; then
  exec env MSYSTEM=UCRT64 CHERE_INVOKING=1 /c/msys64/usr/bin/bash -lc \
    "cd '$(cygpath -u "$ROOT")' && bash scripts/test_engine_tm.sh"
fi

mkdir -p "$ROOT/bin"
g++ -std=c++17 -O1 -Wall -Wextra -Werror -I "$ROOT/engine/src" \
  "$ROOT/engine/tests/youloss_tm_test.cpp" "$ROOT/engine/src/youloss_tm.cpp" \
  -o "$ROOT/bin/youloss_tm_test.exe"
"$ROOT/bin/youloss_tm_test.exe"
```

- [ ] **Step 2: Escrever o teste que falha (`engine/tests/youloss_tm_test.cpp`)**

```cpp
// Testes unitários do youloss_tm (gestão de tempo autoral). Sem framework:
// cada CHECK que falha imprime a linha; o processo sai com 1 se houver falha.
#include "youloss_tm.h"

#include <algorithm>
#include <cmath>
#include <cstdio>

using namespace Stockfish::Youloss;

static int failures = 0;

#define CHECK(cond) \
    do \
    { \
        if (!(cond)) \
        { \
            std::printf("FALHOU %s:%d: %s\n", __FILE__, __LINE__, #cond); \
            ++failures; \
        } \
    } while (0)

static bool near(double a, double b) { return std::abs(a - b) <= 1e-6 * std::max(1.0, std::abs(b)); }

static IterationInput neutral() { return {1000.0, 0, 0.0, 0, 0, 0, false, 20, 0.5}; }

static void test_budget_opening() {
    Budget b = budget({900000, 10000, 10, 1.0});  // 15+10, material completo
    CHECK(b.optimum == 28000);                     // 900000/45 + 0.8*10000
    CHECK(b.maximum == 140000);                    // min(5*base, 0.25*remaining)
}

static void test_budget_endgame() {
    Budget b = budget({60000, 10000, 10, 0.0});  // só reis e peões
    CHECK(b.optimum == 10400);                    // 60000/25 + 8000
    CHECK(b.maximum == 15000);                    // 0.25 * 60000
}

static void test_budget_low_time_keeps_reserve() {
    Budget b = budget({5000, 10000, 1500, 1.0});
    CHECK(b.maximum == 1250);  // 0.25 * 5000 (reserva: 5000-1500-1000 = 2500)
    CHECK(b.optimum == 1250);  // optimum nunca passa do maximum
}

static void test_budget_below_reserve_is_one_ms() {
    Budget b = budget({800, 0, 1500, 0.5});
    CHECK(b.optimum == 1);
    CHECK(b.maximum == 1);
    Budget negative = budget({-300, 0, 10, 0.5});
    CHECK(negative.optimum == 1 && negative.maximum == 1);
}

static void test_budget_phase_is_clamped() {
    CHECK(budget({900000, 0, 10, 7.0}).optimum == budget({900000, 0, 10, 1.0}).optimum);
    CHECK(budget({900000, 0, 10, -1.0}).optimum == budget({900000, 0, 10, 0.0}).optimum);
}

static void test_iteration_forced_move_is_zero() {
    IterationInput in = neutral();
    in.legalMoves = 1;
    CHECK(iteration_time(in) == 0.0);
}

static void test_iteration_neutral_and_stability() {
    CHECK(near(iteration_time(neutral()), 1350.0));  // estabilidade inicial 1.35
    IterationInput stable = neutral();
    stable.stableIterations = 20;
    CHECK(near(iteration_time(stable), 550.0));  // piso 0.55
}

static void test_iteration_instability_is_capped() {
    IterationInput in = neutral();
    in.bestMoveChanges = 0.5;
    CHECK(near(iteration_time(in), 1350.0 * 1.9));
    in.bestMoveChanges = 5.0;
    CHECK(near(iteration_time(in), 1350.0 * 2.5));
}

static void test_iteration_falling_eval_extends() {
    IterationInput in = neutral();
    in.previousAverage = PawnUnits;  // caiu 1 peão em relação à média
    CHECK(near(iteration_time(in), 1350.0 * 1.5));
    in.previousAverage = 10 * PawnUnits;
    CHECK(near(iteration_time(in), 1350.0 * 1.75));  // teto
    in.previousAverage = -10 * PawnUnits;             // melhorou muito
    CHECK(near(iteration_time(in), 1350.0 * 0.75));  // piso
}

static void test_iteration_decided_position_cuts() {
    IterationInput in = neutral();
    in.eval = in.previousAverage = in.previousIteration = 6 * PawnUnits;
    CHECK(near(iteration_time(in), 1350.0 * 0.6));
    in.decisive = true;
    CHECK(near(iteration_time(in), 1350.0 * 0.25));
}

static void test_iteration_clear_best_move_cuts() {
    IterationInput in = neutral();
    in.bestMoveEffort = 0.95;
    CHECK(near(iteration_time(in), 1350.0 * 0.7));
    in.bestMoveEffort = 0.855;
    CHECK(near(iteration_time(in), 1350.0 * 0.85));
}

int main() {
    test_budget_opening();
    test_budget_endgame();
    test_budget_low_time_keeps_reserve();
    test_budget_below_reserve_is_one_ms();
    test_budget_phase_is_clamped();
    test_iteration_forced_move_is_zero();
    test_iteration_neutral_and_stability();
    test_iteration_instability_is_capped();
    test_iteration_falling_eval_extends();
    test_iteration_decided_position_cuts();
    test_iteration_clear_best_move_cuts();
    if (failures)
    {
        std::printf("%d falha(s)\n", failures);
        return 1;
    }
    std::printf("OK: youloss_tm\n");
    return 0;
}
```

- [ ] **Step 3: Rodar e confirmar que falha**

Run: `bash scripts/test_engine_tm.sh`
Expected: erro de compilação `youloss_tm.h: No such file or directory`.

- [ ] **Step 4: Implementar `engine/src/youloss_tm.h`**

```cpp
/*
  Youloss — gestão de tempo autoral (spec seção 4). Funções puras, sem
  dependência do resto do engine, para serem testadas isoladamente
  (engine/tests/youloss_tm_test.cpp). Licença: GPLv3, como o Stockfish.
*/

#ifndef YOULOSS_TM_H_INCLUDED
#define YOULOSS_TM_H_INCLUDED

#include <cstdint>

namespace Stockfish::Youloss {

// Unidades internas de avaliação por peão (igual a PawnValue do Stockfish).
constexpr int PawnUnits = 208;

struct Budget {
    int64_t optimum;  // ms
    int64_t maximum;  // ms
};

struct BudgetInput {
    int64_t remaining;     // ms no nosso relógio
    int64_t increment;     // ms por lance
    int64_t moveOverhead;  // ms (opção UCI "Move Overhead")
    double  phase;         // 1 = material completo, 0 = só reis e peões
};

struct IterationInput {
    double optimum;            // ms, vindo de budget()
    int    stableIterations;   // iterações sem trocar o melhor lance
    double bestMoveChanges;    // trocas recentes do melhor lance, média por thread
    int    eval;               // valor desta iteração (unidades internas)
    int    previousAverage;    // média do lance anterior (unidades internas)
    int    previousIteration;  // valor de algumas iterações atrás
    bool   decisive;           // mate ou vitória de tablebase encontrada
    int    legalMoves;
    double bestMoveEffort;     // fração dos nós gastos no melhor lance (0..1)
};

// Orçamento do lance: optimum (alvo) e maximum (teto duro).
Budget budget(const BudgetInput& in);

// Tempo-alvo (ms) após uma iteração; a busca para quando o tempo gasto passa
// de min(iteration_time, maximum).
double iteration_time(const IterationInput& in);

}  // namespace Stockfish::Youloss

#endif  // #ifndef YOULOSS_TM_H_INCLUDED
```

- [ ] **Step 5: Implementar `engine/src/youloss_tm.cpp`**

```cpp
/*
  Youloss — gestão de tempo autoral (spec seção 4). Licença: GPLv3.
  Parâmetros nomeados abaixo viram opções UCI para tuning na Sprint 3.
*/

#include "youloss_tm.h"

#include <algorithm>
#include <cmath>

namespace Stockfish::Youloss {

namespace {

// Orçamento base: remaining / H(fase) + IncrementShare * inc
constexpr double HorizonOpening    = 45.0;  // lances restantes estimados, material completo
constexpr double HorizonEndgame    = 25.0;  // idem, só reis e peões
constexpr double IncrementShare    = 0.8;
constexpr double MaxBaseMultiple   = 5.0;   // maximum <= 5 * base
constexpr double MaxRemainingShare = 0.25;  // maximum <= 0.25 * remaining
constexpr int64_t LowTimeThreshold = 10000; // abaixo disso, reserva extra
constexpr int64_t LowTimeReserve   = 1000;

// Ajustes por iteração
constexpr double StabilityStart      = 1.35;
constexpr double StabilityStep       = 0.08;
constexpr double StabilityMin        = 0.55;
constexpr double InstabilityWeight   = 1.8;
constexpr double InstabilityMax      = 2.5;
constexpr double FallAverageWeight   = 0.5;
constexpr double FallIterationWeight = 0.25;
constexpr double FallMin             = 0.75;
constexpr double FallMax             = 1.75;
constexpr double DecidedEvalPawns    = 5.0;
constexpr double DecidedFactor       = 0.6;
constexpr double DecisiveFactor      = 0.25;
constexpr double EffortLow           = 0.76;
constexpr double EffortHigh          = 0.95;
constexpr double EffortMinFactor     = 0.7;

}  // namespace

Budget budget(const BudgetInput& in) {
    const double phase     = std::clamp(in.phase, 0.0, 1.0);
    const double horizon   = HorizonEndgame + (HorizonOpening - HorizonEndgame) * phase;
    const double remaining = double(std::max<int64_t>(in.remaining, 0));
    const double base      = remaining / horizon + IncrementShare * double(in.increment);

    const int64_t reserve =
      in.moveOverhead + (in.remaining < LowTimeThreshold ? LowTimeReserve : 0);
    const double available = std::max(1.0, remaining - double(reserve));

    const double maximum =
      std::clamp(std::min(MaxBaseMultiple * base, MaxRemainingShare * remaining), 1.0, available);
    const double optimum = std::clamp(base, 1.0, maximum);
    return {int64_t(optimum), int64_t(maximum)};
}

double iteration_time(const IterationInput& in) {
    if (in.legalMoves <= 1)
        return 0.0;

    const double stability =
      std::max(StabilityMin, StabilityStart - StabilityStep * in.stableIterations);
    const double instability =
      std::min(InstabilityMax, 1.0 + InstabilityWeight * in.bestMoveChanges);

    const double dropAverage   = double(in.previousAverage - in.eval) / PawnUnits;
    const double dropIteration = double(in.previousIteration - in.eval) / PawnUnits;
    const double fall = std::clamp(
      1.0 + FallAverageWeight * dropAverage + FallIterationWeight * dropIteration, FallMin, FallMax);

    double decided = 1.0;
    if (in.decisive)
        decided = DecisiveFactor;
    else if (std::abs(in.eval) >= DecidedEvalPawns * PawnUnits)
        decided = DecidedFactor;

    const double t = std::clamp((in.bestMoveEffort - EffortLow) / (EffortHigh - EffortLow), 0.0, 1.0);
    const double effort = 1.0 - (1.0 - EffortMinFactor) * t;

    return in.optimum * stability * instability * fall * decided * effort;
}

}  // namespace Stockfish::Youloss
```

- [ ] **Step 6: Rodar e confirmar que passa**

Run: `bash scripts/test_engine_tm.sh`
Expected: `OK: youloss_tm`, exit 0.

- [ ] **Step 7: Commit**

```bash
git add engine/src/youloss_tm.h engine/src/youloss_tm.cpp engine/tests/youloss_tm_test.cpp scripts/test_engine_tm.sh
git commit -m "feat(engine): modelo youloss_tm (orçamento e ajuste por iteração) com testes"
```

---

### Task 2: Integração no engine + testes com o binário real

**Files:**
- Modify: `engine/src/Makefile` (listas `SRCS`/`HEADERS`), `engine/src/engine.cpp` (após `Move Overhead`), `engine/src/timeman.h` (público), `engine/src/search.h` (`SearchManager`), `engine/src/search.cpp` (include; após `tm.init`; bloco de parada por iteração), `engine/ORIGIN.md`
- Create: `testing/__init__.py`, `testing/tests/__init__.py`, `testing/tests/test_engine_tm.py`

**Interfaces:**
- Consumes: `Youloss::budget`, `Youloss::iteration_time` (Task 1); `EngineClient`, `SearchInfo` (controller, Sprint 1).
- Produces: opção UCI `YoulossTM` (check, default true); `TimeManagement::set_bounds(TimePoint, TimePoint)`; `SearchManager::youlossTM` (bool); binário `bin/youloss.exe` reconstruído.

- [ ] **Step 1: Criar os pacotes e os testes de integração que falham**

`testing/__init__.py` e `testing/tests/__init__.py`: arquivos vazios.

`testing/tests/test_engine_tm.py`:

```python
import re
import subprocess
import time
from pathlib import Path

import pytest

from controller.engine_client import EngineClient, SearchInfo

ROOT = Path(__file__).resolve().parents[2]
REAL = ROOT / "bin" / "youloss.exe"
BENCH_NODES = 2497913
pytestmark = pytest.mark.skipif(not REAL.exists(), reason="engine não compilado")


def engine(**options) -> EngineClient:
    eng = EngineClient(REAL)
    eng.start()
    eng.handshake(timeout=10)
    for name, value in {"Threads": 1, "Hash": 16, **options}.items():
        eng.set_option(name, value)
    eng.is_ready(timeout=30)
    return eng


def timed(eng: EngineClient, position: str, go: str) -> tuple[SearchInfo, float]:
    t0 = time.perf_counter()
    info = eng.search(position, go, timeout=60)
    return info, (time.perf_counter() - t0) * 1000


def test_option_listed_with_default_true():
    with EngineClient(REAL) as eng:
        eng.send("uci")
        lines = eng.read_until("uciok", timeout=10)
    assert "option name YoulossTM type check default true" in lines


def test_forced_move_is_immediate():
    eng = engine()
    try:
        info, ms = timed(eng, "position fen k7/8/8/8/8/8/1r6/K7 w - - 0 1",
                         "go wtime 60000 btime 60000 winc 1000 binc 1000")
    finally:
        eng.quit()
    assert info.bestmove == "a1b2"
    assert ms < 300


@pytest.mark.parametrize("threads", [1, 4])
def test_think_time_within_maximum(threads):
    # 8 s, sem incremento, material completo: maximum = min(5*177, 2000) = 888 ms
    eng = engine(Threads=threads)
    try:
        info, ms = timed(eng, "position startpos", "go wtime 8000 btime 8000 winc 0 binc 0")
    finally:
        eng.quit()
    assert info.depth >= 1
    assert ms <= 888 + 150


def test_below_reserve_answers_fast():
    eng = engine(**{"Move Overhead": 1500})
    try:
        info, ms = timed(eng, "position startpos", "go wtime 2500 btime 2500 winc 0 binc 0")
    finally:
        eng.quit()
    assert info.bestmove
    assert ms < 250


def test_movetime_and_depth_ignore_youloss_tm():
    eng = engine()
    try:
        _, ms = timed(eng, "position startpos", "go movetime 400")
        info, _ = timed(eng, "position startpos", "go depth 6")
    finally:
        eng.quit()
    assert 350 <= ms <= 700
    assert info.depth == 6


def test_movestogo_uses_original_and_still_moves():
    eng = engine()
    try:
        info, ms = timed(eng, "position startpos", "go wtime 8000 btime 8000 movestogo 20")
    finally:
        eng.quit()
    assert info.bestmove and ms < 8000


def test_ponderhit_returns_within_limit():
    eng = engine(Ponder=True)
    try:
        eng.send("position startpos moves e2e4")
        eng.send("go ponder wtime 8000 btime 8000 winc 0 binc 0")
        time.sleep(0.2)
        t0 = time.perf_counter()
        eng.send("ponderhit")
        lines = eng.read_until("bestmove", timeout=10)
        ms = (time.perf_counter() - t0) * 1000
    finally:
        eng.quit()
    assert lines[-1].startswith("bestmove")
    assert ms <= 888 + 150


def test_original_tm_still_selectable():
    eng = engine(YoulossTM=False)
    try:
        info, ms = timed(eng, "position startpos", "go wtime 8000 btime 8000 winc 0 binc 0")
    finally:
        eng.quit()
    assert info.bestmove and ms < 8000 * 0.81


def test_bench_unchanged():
    out = subprocess.run([str(REAL), "bench"], capture_output=True, text=True, timeout=300)
    m = re.search(r"Nodes searched\s*:\s*(\d+)", out.stdout + out.stderr)
    assert m and int(m[1]) == BENCH_NODES
```

- [ ] **Step 2: Rodar e confirmar que falha (binário atual, sem `YoulossTM`)**

Run: `$PY -m pytest testing/tests/test_engine_tm.py -q`
Expected: FAIL em `test_option_listed_with_default_true` (opção ausente) e em `test_forced_move_is_immediate` (o original gasta ~500 ms). `test_bench_unchanged` passa.

- [ ] **Step 3: Makefile — incluir o módulo**

Em `engine/src/Makefile`, na linha de `SRCS` que termina com `engine.cpp score.cpp memory.cpp`, trocar por:

```make
	engine.cpp score.cpp memory.cpp youloss_tm.cpp
```

E, na última linha de `HEADERS` (a que termina em `shm.h shm_unix.h`), trocar por:

```make
		tt.h tune.h types.h uci.h ucioption.h perft.h nnue/network.h engine.h score.h numa.h memory.h shm.h shm_unix.h youloss_tm.h
```

- [ ] **Step 4: Opção UCI em `engine/src/engine.cpp`**

Logo após a linha `options.add("Move Overhead", Option(10, 0, 5000));`:

```cpp
    // Youloss: gestão de tempo autoral (youloss_tm). false restaura a original.
    options.add("YoulossTM", Option(true));
```

- [ ] **Step 5: `engine/src/timeman.h` — permitir fixar os limites**

Na seção `public:` da classe `TimeManagement`, após `void advance_nodes_time(i64 nodes);`:

```cpp
    // Youloss: substitui optimum/maximum calculados por init() (youloss_tm).
    void set_bounds(TimePoint optimum, TimePoint maximum) {
        optimumTime = optimum;
        maximumTime = maximum;
    }
```

- [ ] **Step 6: `engine/src/search.h` — flag no `SearchManager`**

Logo após a linha `bool                 stopOnPonderhit;`:

```cpp
    bool                 youlossTM = false;  // Youloss: youloss_tm ativo nesta busca
```

- [ ] **Step 7: `engine/src/search.cpp` — ganchos**

Nos includes do topo, junto aos outros `#include "..."` do projeto:

```cpp
#include "youloss_tm.h"
```

Logo após a chamada `main_manager()->tm.init(limits, rootPos.side_to_move(), rootPos.game_ply(), options, main_manager()->originalTimeAdjust);`:

```cpp
    // Youloss: gestão de tempo autoral só em "base + incremento"; movestogo e
    // nodestime continuam com o gerenciador original.
    {
        const Color us = rootPos.side_to_move();
        auto*       mm = main_manager();
        mm->youlossTM  = int(options["YoulossTM"]) != 0 && limits.time[us] > 0
                     && limits.movestogo == 0 && int(options["nodestime"]) == 0;
        if (mm->youlossTM)
        {
            constexpr Value FullNonPawn =
              2 * (2 * KnightValue + 2 * BishopValue + 2 * RookValue + QueenValue);
            const Youloss::Budget b = Youloss::budget(
              {limits.time[us], limits.inc[us], TimePoint(options["Move Overhead"]),
               double(rootPos.non_pawn_material()) / FullNonPawn});
            mm->tm.set_bounds(b.optimum, b.maximum);
        }
    }
```

No bloco de parada por iteração, **logo após** o `if (rootMoves.size() == 1) totalTime = std::min(500.0, totalTime);` (e antes de `auto elapsedTime = elapsed();`):

```cpp
            // Youloss: tempo-alvo autoral; as variáveis originais acima continuam
            // sendo calculadas porque alimentam previousTimeReduction.
            if (mainThread->youlossTM)
            {
                const Value prevAvg = std::abs(mainThread->bestPreviousAverageScore) >= VALUE_INFINITE
                                      ? bestValue
                                      : mainThread->bestPreviousAverageScore;
                totalTime           = Youloss::iteration_time(
                  {double(mainThread->tm.optimum()), rootDepth - lastBestMoveDepth,
                             totBestMoveChanges / double(threads.size()), bestValue, prevAvg,
                             mainThread->iterValue[iterIdx], is_decisive(bestValue),
                             int(rootMoves.size()), double(nodesEffort) / 100000.0});
            }
```

- [ ] **Step 8: Rebuild e testes**

Run:
```bash
bash scripts/test_engine_tm.sh
bash scripts/build_engine.sh
$PY -m pytest testing/tests/test_engine_tm.py -q
$PY -m pytest controller/tests -q
```
Expected: `OK: youloss_tm`. O build termina com o binário em `bin/`. Os testes de integração passam, inclusive `test_bench_unchanged` (2497913). A suíte do controller continua verde. Se `test_think_time_within_maximum[4]` estourar por ~50 ms por causa da criação de threads, investigar antes de afrouxar a margem (`superpowers:systematic-debugging`).

- [ ] **Step 9: `engine/ORIGIN.md` — declarar as modificações**

Trocar a seção `## Modificações autorais da equipe Youloss` inteira por:

```markdown
## Modificações autorais da equipe Youloss
- Gestão de tempo (`src/youloss_tm.{h,cpp}`, testes em `tests/youloss_tm_test.cpp`),
  ativa pela opção UCI `YoulossTM` (padrão `true`; `false` restaura a original).
- Ganchos mínimos: `search.cpp` (orçamento após `tm.init` e tempo-alvo por iteração),
  `timeman.h` (`set_bounds`), `search.h` (flag `youlossTM`), `engine.cpp` (opção),
  `Makefile` (novo fonte). Busca e avaliação não foram alteradas: o `bench`
  continua em 2497913 nós.
```

- [ ] **Step 10: Commit**

```bash
git add engine/src/Makefile engine/src/engine.cpp engine/src/timeman.h engine/src/search.h engine/src/search.cpp engine/ORIGIN.md testing/__init__.py testing/tests/__init__.py testing/tests/test_engine_tm.py
git commit -m "feat(engine): opção YoulossTM liga o youloss_tm na busca (bench inalterado)"
```

---

### Task 3: Leitores de resultado (SPRT e perfil de tempo)

**Files:**
- Create: `testing/sprt_result.py`, `testing/time_profile.py`
- Test: `testing/tests/test_sprt_tools.py`

**Interfaces:**
- Consumes: texto do log e PGN do fastchess.
- Produces:
  - `sprt_result.summarize(text: str) -> tuple[int, str]`: código (0 = H1 aceita, 1 = H0 aceita, 2 = inconclusivo) e um resumo em uma linha. CLI: `python -m testing.sprt_result <log>` sai com esse código.
  - `time_profile.profile(pgn_text: str) -> dict[str, EngineProfile]` com `EngineProfile(games: int, total_s: float, buckets: dict[str, list[float]], forfeits: int)`; `mean_total(p) -> float`; CLI `python -m testing.time_profile <pgn>` imprime a tabela.

- [ ] **Step 1: Escrever os testes que falham (`testing/tests/test_sprt_tools.py`)**

```python
from testing.sprt_result import summarize
from testing.time_profile import mean_total, profile

LOG_H1 = """
Results of tm vs sf (10+0, 1t, 16MB, UHO_Lichess_4852_v1.epd):
Elo: 1.25 +/- 3.40, nElo: 2.10 +/- 5.70
Games: 4000, Wins: 900, Losses: 886, Draws: 2214, Points: 2007.0 (50.18 %)
LLR: 2.96 (100.5%) (-2.94, 2.94) [-5.00, 0.00]
SPRT ([-5.00, 0.00]) completed - H1 was accepted
"""


def test_h1_accepted():
    code, line = summarize(LOG_H1)
    assert code == 0
    assert "H1" in line and "4000" in line and "2.96" in line


def test_h0_accepted():
    code, _ = summarize(LOG_H1.replace("H1 was accepted", "H0 was accepted"))
    assert code == 1


def test_inconclusive_uses_last_block():
    text = LOG_H1.replace("SPRT ([-5.00, 0.00]) completed - H1 was accepted", "")
    text += "Games: 5000, Wins: 1\nLLR: 1.10 (37.4%) (-2.94, 2.94) [-5.00, 0.00]\n"
    code, line = summarize(text)
    assert code == 2 and "5000" in line and "1.10" in line


PGN = """[Event "Fastchess Tournament"]
[White "tm"]
[Black "sf"]
[Result "0-1"]
[FEN "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"]
[Termination "time forfeit"]

1... e5 {+0.10/10 0.500s} 2. Nf3 {+0.20/11 1.000s} Nc6 {-0.10/9 0.250s}
3. Bb5 {+0.30/12 2.000s, White loses on time} 0-1

[Event "Fastchess Tournament"]
[White "sf"]
[Black "tm"]
[Result "1/2-1/2"]
[FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]
[Termination "adjudication"]

1. d4 {+0.10/10 1.500s} d5 {-0.05/10 0.500s} 1/2-1/2
"""


def test_profile_assigns_moves_to_engines_and_buckets():
    prof = profile(PGN)
    assert prof["tm"].games == 2 and prof["sf"].games == 2
    assert abs(prof["tm"].total_s - (1.0 + 2.0 + 0.5)) < 1e-9
    assert abs(prof["sf"].total_s - (0.5 + 0.25 + 1.5)) < 1e-9
    assert prof["tm"].buckets["1-10"] == [1.0, 2.0, 0.5]
    assert prof["tm"].forfeits == 1 and prof["sf"].forfeits == 0
    assert abs(mean_total(prof["tm"]) - 1.75) < 1e-9
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `$PY -m pytest testing/tests/test_sprt_tools.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'testing.sprt_result'`

- [ ] **Step 3: Implementar `testing/sprt_result.py`**

```python
"""Resume o SPRT a partir do log do fastchess.

Exit (CLI): 0 = H1 aceita, 1 = H0 aceita, 2 = inconclusivo."""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ACCEPTED = re.compile(r"H([01]) was accepted")
_GAMES = re.compile(r"^Games:\s*(\d+)", re.M)
_LLR = re.compile(r"^LLR:\s*(-?\d+(?:\.\d+)?)", re.M)
_ELO = re.compile(r"^Elo:\s*(-?\d+(?:\.\d+)?)\s*\+/-\s*(\d+(?:\.\d+)?)", re.M)


def _last(pattern: re.Pattern[str], text: str) -> re.Match[str] | None:
    matches = list(pattern.finditer(text))
    return matches[-1] if matches else None


def summarize(text: str) -> tuple[int, str]:
    accepted = _last(_ACCEPTED, text)
    games, llr, elo = _last(_GAMES, text), _last(_LLR, text), _last(_ELO, text)
    parts = [
        f"games={games[1] if games else '?'}",
        f"llr={llr[1] if llr else '?'}",
        f"elo={elo[1]}±{elo[2]}" if elo else "elo=?",
    ]
    if accepted is None:
        return 2, "SPRT inconclusivo: " + " ".join(parts)
    hypothesis = accepted[1]
    return (0 if hypothesis == "1" else 1), f"SPRT H{hypothesis} aceita: " + " ".join(parts)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    code, line = summarize(Path(args[0]).read_text(encoding="utf-8", errors="replace"))
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Implementar `testing/time_profile.py`**

```python
"""Perfil de uso de tempo por engine a partir do PGN do fastchess.

Cada lance traz um comentário com o tempo gasto, ex.: {+0.25/12 0.345s}."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

BUCKETS = [("1-10", 1, 10), ("11-20", 11, 20), ("21-40", 21, 40), ("41+", 41, 10_000)]
_TAG = re.compile(r'^\[(\w+) "([^"]*)"\]', re.M)
_MOVE_TIME = re.compile(r"\{[^}]*?\s(\d+(?:\.\d+)?)s\b[^}]*\}")


@dataclass
class EngineProfile:
    games: int = 0
    total_s: float = 0.0
    buckets: dict[str, list[float]] = field(
        default_factory=lambda: {name: [] for name, _, _ in BUCKETS})
    forfeits: int = 0


def _bucket(fullmove: int) -> str:
    return next(name for name, lo, hi in BUCKETS if lo <= fullmove <= hi)


def _split_games(text: str) -> list[str]:
    return [g for g in re.split(r"(?=^\[Event )", text, flags=re.M) if g.strip()]


def profile(pgn_text: str) -> dict[str, EngineProfile]:
    result: dict[str, EngineProfile] = {}
    for game in _split_games(pgn_text):
        tags = dict(_TAG.findall(game))
        white, black = tags.get("White", "?"), tags.get("Black", "?")
        fen = tags.get("FEN", "").split()
        white_to_move = len(fen) < 2 or fen[1] == "w"
        fullmove = int(fen[5]) if len(fen) >= 6 else 1
        for name in (white, black):
            result.setdefault(name, EngineProfile()).games += 1
        side_white = white_to_move
        for m in _MOVE_TIME.finditer(game):
            seconds = float(m[1])
            prof = result[white if side_white else black]
            prof.total_s += seconds
            prof.buckets[_bucket(fullmove)].append(seconds)
            if not side_white:
                fullmove += 1
            side_white = not side_white
        if tags.get("Termination") == "time forfeit":
            loser = white if tags.get("Result") == "0-1" else black
            result[loser].forfeits += 1
    return result


def mean_total(prof: EngineProfile) -> float:
    return prof.total_s / prof.games if prof.games else 0.0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    prof = profile(Path(args[0]).read_text(encoding="utf-8", errors="replace"))
    header = f"{'engine':<8}{'jogos':>7}{'s/jogo':>9}" + "".join(
        f"{'s/lance ' + name:>18}" for name, _, _ in BUCKETS) + f"{'flag':>6}"
    print(header)
    for name, p in sorted(prof.items()):
        means = "".join(
            f"{(sum(v) / len(v) if v else 0.0):>18.3f}" for v in p.buckets.values())
        print(f"{name:<8}{p.games:>7}{mean_total(p):>9.2f}{means}{p.forfeits:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Rodar e confirmar que passa**

Run: `$PY -m pytest testing/tests/test_sprt_tools.py -q`
Expected: todos passam.

- [ ] **Step 6: Commit**

```bash
git add testing/sprt_result.py testing/time_profile.py testing/tests/test_sprt_tools.py
git commit -m "test: leitores do SPRT e do perfil de tempo do fastchess"
```

---

### Task 4: Aberturas + script de match/SPRT

**Files:**
- Create: `scripts/fetch_openings.sh`, `testing/tm_match.sh`
- Modify: `assets/MANIFEST` (gerado pelo script)

**Interfaces:**
- Consumes: `bin/youloss.exe` com `YoulossTM` (Task 2); `testing.sprt_result`, `testing.time_profile` (Task 3).
- Produces: `assets/openings/UHO_Lichess_4852_v1.epd`; `bash testing/tm_match.sh <tc> <rounds> [elo0 elo1]`, que grava `logs/sprt/<nome>.{log,pgn}` e, com SPRT, sai com o código de `sprt_result`.

- [ ] **Step 1: Escrever `scripts/fetch_openings.sh`**

```bash
#!/usr/bin/env bash
# Baixa as aberturas do SPRT (UHO_Lichess_4852_v1, as mesmas dos testes oficiais
# do Stockfish) para assets/openings e registra sha256 em assets/MANIFEST.
# Rodar do root do repo, com rede, ANTES do evento.
set -euo pipefail
URL="https://github.com/official-stockfish/books/raw/master/UHO_Lichess_4852_v1.epd.zip"
DEST="assets/openings"
PY=".venv/Scripts/python"
mkdir -p "$DEST"
curl -fsSL --retry 3 -o "$DEST/uho.zip" "$URL"
"$PY" -m zipfile -e "$DEST/uho.zip" "$DEST"
rm "$DEST/uho.zip"
[ -s "$DEST/UHO_Lichess_4852_v1.epd" ] || { echo "EPD não encontrado após extrair" >&2; exit 1; }
touch assets/MANIFEST
grep -v ' openings/' assets/MANIFEST > assets/MANIFEST.tmp || true
(cd assets && sha256sum openings/*.epd) >> assets/MANIFEST.tmp
mv assets/MANIFEST.tmp assets/MANIFEST
echo "OK: $(wc -l < "$DEST/UHO_Lichess_4852_v1.epd") posições em $DEST"
```

- [ ] **Step 2: Rodar**

Run: `bash scripts/fetch_openings.sh && bash scripts/verify_assets.sh`
Expected: `OK: <N> posições`, com N na casa de dezenas de milhares, e `verify_assets` sai com 0. Se o GitHub for bloqueado pelo firewall (TLS), parar e registrar no ledger. **Não** desligar a verificação de certificado.

- [ ] **Step 3: Escrever `testing/tm_match.sh`**

```bash
#!/usr/bin/env bash
# Match do youloss_tm: mesmo binário, YoulossTM=true ("tm") x false ("sf").
# Uso: bash testing/tm_match.sh <tc> <rounds> [elo0 elo1]
#   partidas fixas:  bash testing/tm_match.sh 10+0 100
#   SPRT:            bash testing/tm_match.sh 60+0 50000 -5 0
# Concorrência: CONC (padrão: núcleos físicos - 1). Deixe a máquina ociosa.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TC="${1:?uso: tm_match.sh <tc> <rounds> [elo0 elo1]}"
ROUNDS="${2:?rounds}"
ELO0="${3:-}"
ELO1="${4:-}"
if [ -z "${CONC:-}" ]; then
  CORES=$(powershell -NoProfile -Command \
    "(Get-CimInstance Win32_Processor | Measure-Object NumberOfCores -Sum).Sum" | tr -d '\r')
  CONC=$(( CORES > 1 ? CORES - 1 : 1 ))
fi
BOOK="$ROOT/assets/openings/UHO_Lichess_4852_v1.epd"
[ -s "$BOOK" ] || { echo "sem aberturas: rode scripts/fetch_openings.sh" >&2; exit 2; }

OUT="$ROOT/logs/sprt"
mkdir -p "$OUT"
NAME="tm_${TC}_r${ROUNDS}${ELO0:+_sprt${ELO0}_${ELO1}}_$(date +%Y%m%d-%H%M%S)"
SPRT=()
[ -n "$ELO0" ] && SPRT=(-sprt elo0="$ELO0" elo1="$ELO1" alpha=0.05 beta=0.05)

cd "$OUT"  # fastchess grava config.json no cwd
"$ROOT/tools/fastchess.exe" \
  -engine cmd="$ROOT/bin/youloss.exe" name=tm option.YoulossTM=true \
  -engine cmd="$ROOT/bin/youloss.exe" name=sf option.YoulossTM=false \
  -each tc="$TC" option.Threads=1 option.Hash=16 \
  -openings file="$BOOK" format=epd order=random \
  -rounds "$ROUNDS" -games 2 -concurrency "$CONC" -recover \
  "${SPRT[@]}" \
  -pgnout file="$OUT/$NAME.pgn" \
  | tee "$OUT/$NAME.log"

cd "$ROOT"
echo "== perfil de tempo ($NAME.pgn)"
.venv/Scripts/python -m testing.time_profile "$OUT/$NAME.pgn"
if [ -n "$ELO0" ]; then
  .venv/Scripts/python -m testing.sprt_result "$OUT/$NAME.log"
fi
```

- [ ] **Step 4: Smoke do harness com saída real (valida os leitores)**

Run:
```bash
CONC=4 bash testing/tm_match.sh 2+0.02 4
CONC=4 bash testing/tm_match.sh 2+0.02 400 -300 300; echo "exit=$?"
```
Expected: o primeiro termina com 8 jogos e a tabela de perfil mostra `tm` e `sf`, com `jogos` = 8 e tempos > 0. O segundo conclui cedo, porque os limites [-300, 300] são largos, e imprime `SPRT H0 aceita`, `SPRT H1 aceita` ou `inconclusivo`, com `games=` e `llr=` preenchidos. **Se** a tabela vier zerada ou o resumo vier com `?`, o formato real do fastchess é diferente do que os testes assumem. Nesse caso, copiar um trecho real do `.log`/`.pgn` para os testes da Task 3, ajustar as regex (primeiro RED, depois GREEN) e registrar um `Ruling:`.

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_openings.sh testing/tm_match.sh assets/MANIFEST
git commit -m "test: aberturas UHO e harness de match/SPRT do youloss_tm"
```

---

### Task 5: Calibração do perfil de tempo

**Files:**
- Create: `docs/sprt/2026-s2-youloss-tm.md`
- Modify (só se a regra de decisão pedir): `engine/src/youloss_tm.cpp` (`HorizonOpening`, `HorizonEndgame`), `engine/tests/youloss_tm_test.cpp` (valores esperados de `budget`)

**Interfaces:**
- Consumes: `testing/tm_match.sh`, `testing.time_profile` (Tasks 3–4).
- Produces: constantes de horizonte calibradas e o registro em `docs/sprt/2026-s2-youloss-tm.md`.

- [ ] **Step 1: Rodar os matches de calibração**

Run (com a máquina ociosa):
```bash
bash testing/tm_match.sh 10+0 100
bash testing/tm_match.sh 60+0 20
```
Expected: 200 e 40 jogos, cada um com a tabela de perfil no final.

- [ ] **Step 2: Aplicar a regra de decisão**

Para cada TC, seja `r = s/jogo(tm) / s/jogo(sf)`:
- **Aceita** se `0.90 ≤ r ≤ 1.10`, `flag(tm) == 0` e `s/lance 1-10` do `tm` ≤ 1,5 × o do `sf`.
- **Senão**, dividir `HorizonOpening` e `HorizonEndgame` por `r`, arredondando para 0,5 e com mínimo de 15. Atualizar os valores esperados em `test_budget_opening`/`test_budget_endgame` (RED primeiro: rodar `bash scripts/test_engine_tm.sh` e ver falhar antes de mudar o `.cpp`). Depois rebuild (`bash scripts/build_engine.sh`), `$PY -m pytest testing/tests/test_engine_tm.py -q` e repetir o Step 1.
- **No máximo 2 rodadas de ajuste.** Se continuar fora da faixa, registrar no ledger e seguir para a Task 6 mesmo assim. O SPRT decide, e a equipe é avisada.

- [ ] **Step 3: Registrar em `docs/sprt/2026-s2-youloss-tm.md`**

```markdown
# SPRT — youloss_tm (Sprint 2)

## Calibração
| rodada | TC | jogos | s/jogo tm | s/jogo sf | r | flag tm | HorizonOpening/Endgame |
|---|---|---|---|---|---|---|---|
| 1 | 10+0 | 200 | … | … | … | … | 45 / 25 |
| 1 | 60+0 | 40 | … | … | … | … | 45 / 25 |

## SPRTs
| TC | limites | jogos | LLR | Elo | resultado | log |
|---|---|---|---|---|---|---|
```

Preencher as linhas com os números reais das tabelas. Cada `…` vira um número.

- [ ] **Step 4: Commit**

```bash
git add docs/sprt/2026-s2-youloss-tm.md engine/src/youloss_tm.cpp engine/tests/youloss_tm_test.cpp
git commit -m "test: calibração do perfil de tempo do youloss_tm"
```

---

### Task 6: SPRT de não-regressão

**Files:**
- Modify: `docs/sprt/2026-s2-youloss-tm.md` (tabela "SPRTs")

**Interfaces:**
- Consumes: `testing/tm_match.sh` (Task 4), binário calibrado (Task 5).
- Produces: resultado registrado; `H1 aceita` a 60+0 é o critério proposto de não-regressão, não um resultado assumido.

- [ ] **Step 1: Gate rápido a 10+0**

Run: `bash testing/tm_match.sh 10+0 50000 -5 0; echo "exit=$?"`
Expected: `SPRT H1 aceita` (exit 0). Estimativa: 1 a 4 h. Se der **H0** (exit 1), não rodar o Step 2. Registrar na tabela, voltar à Task 5 para mais uma rodada de ajuste (conta no limite de 2) e, se ainda falhar, parar e escalar para a equipe com o perfil de tempo em mãos.

- [ ] **Step 2: Aceite a 60+0 (longo, em segundo plano)**

Run: `bash testing/tm_match.sh 60+0 50000 -5 0; echo "exit=$?"` (em segundo plano somente com orçamento deliberado)
Expected: `SPRT H1 aceita` (exit 0). Estimativa: 18 a 90 h. Se passar de 48 h, registrar o LLR parcial e pedir decisão à equipe.

- [ ] **Step 3: Registrar e commitar**

Preencher uma linha por SPRT na tabela, com TC, limites, jogos, LLR, Elo±, resultado e o nome do `.log`.

```bash
git add docs/sprt/2026-s2-youloss-tm.md
git commit -m "test: SPRT de não-regressão do youloss_tm"
```

---

## Definição de pronto da Sprint 2

- `bash scripts/test_engine_tm.sh` → `OK: youloss_tm`.
- `$PY -m pytest testing/tests controller/tests -q` verde, com `test_bench_unchanged` confirmando 2497913 nós.
- `bin/youloss.exe` com `YoulossTM` padrão `true`; `ORIGIN.md` lista as modificações.
- Não há resultado de SPRT registrado. O smoke real de 2026-09-30 a `10+0` teve somente 2 jogos e serve apenas para validar o caminho integrado; não permite concluir não-regressão nem ganho.
- `bash testing/smoke.sh` continua passando.
- Nenhum commit com atribuição de IA.
- **Pendências herdadas da S1** (não bloqueiam a S2): Syzygy 3-4-5 (rede sem inspeção TLS) e a escolha do book.

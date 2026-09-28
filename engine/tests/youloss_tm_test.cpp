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

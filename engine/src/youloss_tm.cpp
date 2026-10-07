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
constexpr double  HorizonOpening    = 32.0;   // lances restantes estimados, material completo
constexpr double  HorizonEndgame    = 25.0;   // idem, só reis e peões
constexpr double  IncrementShare    = 0.8;
constexpr double  MaxBaseMultiple   = 5.0;    // maximum <= 5 * base
constexpr double  MaxRemainingShare = 0.25;   // maximum <= 0.25 * remaining
constexpr int64_t LowTimeThreshold  = 10000;  // abaixo disso, reserva extra
constexpr int64_t LowTimeReserve    = 1000;   // teto da reserva extra
constexpr double  LowTimeShare      = 0.1;    // reserva extra <= 10% do restante

// Ajustes por iteração
constexpr double StabilityStart      = 1.35;
constexpr double StabilityStep       = 0.08;
constexpr double StabilityMin        = 0.70;
constexpr double InstabilityWeight   = 1.8;
constexpr double InstabilityMax      = 2.5;
constexpr double FallAverageWeight   = 0.5;
constexpr double FallIterationWeight = 0.25;
constexpr double FallMin             = 0.75;
constexpr double FallMax             = 2.0;
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

    // Abaixo de 10 s guarda até 1 s extra, proporcional ao relógio: uma reserva
    // fixa zeraria o orçamento quando restar pouco mais de 1 s.
    const double lowTimeReserve =
      in.remaining < LowTimeThreshold ? std::min(double(LowTimeReserve), LowTimeShare * remaining)
                                      : 0.0;
    const double available =
      std::max(1.0, remaining - double(in.moveOverhead) - lowTimeReserve);

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

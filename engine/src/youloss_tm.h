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

# YoulossTM: corte de tempo em empate morto (2026-11-04)

Registrado antes de medir a correção.

## Problema observado

Na simulação em 1500+0 (`logs/soak-20261104/`), partida 1, a posição estava em +0,00 e o motor
repetia lances, mas pensou 58 s e 88 s. Os 88 s batem com o teto de `5 × base`. A hipótese é
que lances equivalentes troquem de lugar, levantando a instabilidade sem significado real.

## Correção

Quando a avaliação atual, a média do lance anterior e a iteração anterior estão todas em
±2 unidades internas (cerca de 0,01 peão), o tempo-alvo passa a ser
`optimum × estabilidade × 0,5`, ignorando instabilidade, queda e esforço.

## Medições, nesta ordem, depois que a simulação terminar

1. Triagem: esta branch contra a `main` (`9df551c`), `60+0`, 1 thread, Hash 128 MiB, Move
   Overhead 60 ms, concorrência 4, 30 rodadas pareadas, 60 partidas.
2. Uma partida 1500+0 pelo `testing/tournament_soak.py`, com as mesmas condições da simulação.

## Regra de decisão

Propor a correção ao dono somente se:

- a triagem não tiver perda no tempo nem crash e der **pelo menos 45%**;
- a partida 1500+0 não tiver lance acima de 30 s com a avaliação em +0,00 depois de o
  critério valer por pelo menos 3 lances seguidos.

A triagem não prova ganho de força. Se a regra falhar, a correção não entra.

## Resultado

Pendente.

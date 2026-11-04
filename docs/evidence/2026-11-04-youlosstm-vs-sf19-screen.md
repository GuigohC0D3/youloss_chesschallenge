# Triagem: Stockfish 19 + YoulossTM contra Stockfish 19 puro (2026-11-04)

Registrado antes da primeira partida.

## Pergunta

A versão modificada perde força ou perde no tempo contra o `sf_19` puro?
A triagem não prova ganho de força: 60 partidas têm margem de cerca de ±7 pontos percentuais.

## Plano fixo

- `bin/stockfish` (modificado) contra `bin/stockfish_sf19` (puro), mesmo fonte-base e rede.
- `60+0`, 1 thread, Hash 128 MiB, Move Overhead 60 ms, concorrência 4.
- 30 rodadas pareadas, 60 partidas, cores trocadas na mesma abertura
  (`testing/openings/balanced_gm_v1.epd`), checagem com `testing/check_fastchess_log.sh`.

## Regra de decisão

Manter `YoulossTM=true` se **não houver perda no tempo nem crash** e o placar for **pelo
menos 45%**. Caso contrário, a modificação não vai para a entrega sem nova decisão do dono.

## Resultado

Do ponto de vista de `youlosstm`: **1 vitória, 59 empates, 0 derrotas, 50,83%** em 60 partidas.
fastchess: Elo +5,79 ± 11,17. Nenhuma perda no tempo nem crash; `check_fastchess_log.sh`
aprovou. Duração: 21min31s.

**Decisão: manter `YoulossTM=true`**, pela regra acima.

Com 59 empates em 60, o resultado não mostra ganho de força: é compatível com efeito nenhum.
O controle é `60+0` com 1 thread, não o de torneio. Log e PGN ficam em `logs/screen-20261104/`,
fora do git.

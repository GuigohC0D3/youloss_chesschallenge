# Origem do engine

`engine/` é o **Stockfish 19 com uma modificação da equipe Youloss**: o gerenciador de
tempo YoulossTM. Busca, avaliação e rede neural são as do Stockfish.

- Projeto-base: Stockfish, https://github.com/official-stockfish/Stockfish
- Tag: `sf_19`, commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d`
- Rede NNUE: `nn-1a298aa575a0.nnue`, embutida no binário
- Bench: 2497913 nós, igual ao oficial, porque o `bench` não usa gestão de tempo
- Licença: GPLv3 (ver `Copying.txt`)

## Modificações em relação ao `sf_19`

- `src/youloss_tm.{h,cpp}` e `tests/youloss_tm_test.cpp`: gerenciador de tempo autoral.
- `src/search.cpp`, `src/search.h`, `src/timeman.h`: ganchos do orçamento por lance e do
  tempo-alvo por iteração.
- `src/engine.cpp`: opção UCI `YoulossTM` (padrão `true`; `false` restaura a original).
- `src/misc.cpp`: o nome UCI passa a ser `Stockfish 19 YoulossTM`.
- `src/Makefile`: compila o novo arquivo.

## O que o YoulossTM muda

Orçamento por lance: `restante / H(fase) + 0,8 × incremento`, com H entre 32 (material
completo) e 25 (só reis e peões) e teto de 25% do relógio. A cada iteração o alvo se ajusta
pela estabilidade do melhor lance, pela queda de avaliação e pela concentração de nós.

O Stockfish original reserva `Move Overhead × (lances restantes + 2)`. O YoulossTM desconta
o overhead uma vez, então não zera o orçamento com pouco tempo no relógio.

Os testes de força não mostram ganho estatístico: ver `docs/evidence/`.

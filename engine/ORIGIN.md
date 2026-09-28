# Origem do engine

- Projeto-base: Stockfish — https://github.com/official-stockfish/Stockfish
- Tag: sf_19
- Commit: edb0d9db6731067ec50ce619ff372b463bc4dd5d
- Licença: GPLv3 (ver `Copying.txt`). Este fork herda a licença; o código-fonte
  completo será disponibilizado à banca e publicado ao final do evento.
- Bench de referência (sem modificações, 1 thread, `bench` padrão): 2497913 nós (Nodes searched) — igual ao `Bench:` oficial do commit

## Modificações autorais da equipe Youloss
- Gestão de tempo (`src/youloss_tm.{h,cpp}`, testes em `tests/youloss_tm_test.cpp`),
  ativa pela opção UCI `YoulossTM` (padrão `true`; `false` restaura a original).
- Ganchos mínimos: `search.cpp` (orçamento após `tm.init` e tempo-alvo por iteração),
  `timeman.h` (`set_bounds`), `search.h` (flag `youlossTM`), `engine.cpp` (opção),
  `Makefile` (novo fonte). Busca e avaliação não foram alteradas: o `bench`
  continua em 2497913 nós.

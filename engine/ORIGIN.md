# Origem do engine

`engine/` é o **Stockfish 19 oficial, sem nenhuma modificação**.

- Projeto: Stockfish, https://github.com/official-stockfish/Stockfish
- Tag: `sf_19`, commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d`
- Fonte: `https://github.com/official-stockfish/Stockfish/archive/refs/tags/sf_19.tar.gz`
  (SHA-256 `519b653d0d1ffb96531d982ccbe5c6a19425e8388e0e3c2f70f34b424ab32d76`)
- Rede NNUE: `nn-1a298aa575a0.nnue`, embutida no binário
- Bench de referência: 2497913 nós (`bin/stockfish bench`)
- Licença: GPLv3 (ver `Copying.txt`)

Autoria da equipe, fora deste diretório: `controller/` (interface, relógio, log).
O antigo gerenciador de tempo foi retirado; ver `archive/youloss-tm/README.md`.

Para conferir: extraia o arquivo acima e compare com `diff -r`; só este `ORIGIN.md`
é diferente. A rede é baixada pelo `make net` ou extraída do binário pelo comando
UCI `export_net`.

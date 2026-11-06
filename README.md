# Youloss — III Chess Challenge

Stockfish 19 com o gerenciador de tempo autoral YoulossTM (`engine/`, ver
`engine/ORIGIN.md`), um livro de aberturas e uma interface local escrita pela equipe:
tabuleiro no navegador e um campo para digitar o lance do adversário. Roda offline em
Mac Apple Silicon.

## Jogar

Com o pacote (`dist/stockfish-chess-challenge.tar.gz`), dentro da pasta extraída:

```bash
./launch_stockfish.sh --dry-run   # confere o Mac; rode antes da partida
./launch_stockfish.sh             # abre o tabuleiro no navegador
```

No M4 (plano B), siga o passo a passo em `docs/rodar-no-m4.md`.

A partir de um clone do repositório:

```bash
bash scripts/setup_mac.sh         # compila, instala e testa
.venv/bin/python -m controller.web
```

1. Escolha cor e adversário e clique em **Iniciar** junto com o relógio físico.
   De brancas, nosso primeiro lance já é calculado.
2. Digite o lance do adversário e tecle Enter: `e2e4`, `e7e8q`, `Nf3`, `Cf3`, `exd5`, `O-O`.
   Aceita a notação em português (R, D, T, B, C). Se a mesma letra servir para dois
   lances diferentes (`Rd2`: torre ou rei), o programa pede casa de origem e destino.
3. Nosso lance aparece em destaque e no tabuleiro. Jogue-o e aperte o relógio.

**Desfazer** volta para antes do último lance do adversário, inclusive durante o
cálculo. **Corrigir relógio** aplica a leitura do físico. **Encerrar partida** registra
o resultado; mate e empate automático são detectados sozinhos.

O relógio da tela é estimativa; o físico é a referência. Cada transição desconta
2 s (`--clock-latency`): o tempo de digitar o lance dele e o de executar o nosso.
Com o relógio interno no limite, o programa mostra um lance imediato sem busca e um
aviso. Se o engine cair, ele é reiniciado e a busca repetida; se não voltar, sai um
lance de emergência com aviso.

Depois do nosso lance, o motor continua pensando no lance que prevê para o adversário
(ponder). Se ele acertar, a resposta sai mais rápida e mais profunda; a tela mostra
**Stockfish (previsto)**. Isso mantém a CPU ocupada o tempo todo. Para desligar, use
`--no-ponder`.

Fechar o programa (Ctrl-C) não perde a partida: ao abrir de novo aparece **Retomar**.
Logs por lance ficam em `logs/`. O lançador impede o Mac de dormir, mas não com a
tampa fechada: mantenha aberto e na tomada.

## M4 e M5

O binário é único: ARMv8.2 genérico, macOS 11 ou mais novo, sem instruções exclusivas
de nenhum chip. Threads e Hash são escolhidos ao iniciar:

- Threads: todos os núcleos menos um, que fica para o sistema e a interface. Dá 9 em
  M4/M5 de 10 núcleos (partida de 600+0 com 9 threads testada no M5 em 2026-11-06).
- Hash: 1/8 da RAM (2048 MiB em 16 GB), limitado à metade da memória livre.

`--threads` e `--hash` substituem os valores. O pacote usa o `python3` da máquina
(3.9 ou mais novo); `xcode-select --install` instala, com internet, se faltar.

## Gerar o pacote

```bash
.venv/bin/python scripts/build_offline_release.py            # exige checkout limpo
.venv/bin/python scripts/build_offline_release.py --candidate  # aceita alterações locais
.venv/bin/python scripts/verify_offline_release.py dist/stockfish-chess-challenge.tar.gz
```

## Testes

```bash
.venv/bin/python -m pytest controller/tests testing/tests -q
```

## Modo terminal

`python -m controller.main start --color white --opponent "Equipe X" --game 1` mantém
a CLI anterior, com protocolo explícito do relógio físico (`begin`, `press`, `go`,
`played`). Comandos em `help`.

## Livro de aberturas e tablebases

O Stockfish não lê texto, então livros de regras ou de estratégia não têm como entrar nele:
as regras já estão no gerador de lances e o conhecimento posicional, na rede neural. O que
ele usa de fato são estes dois formatos:

- **Livro de aberturas** (`assets/book.bin`, no pacote): repertório da equipe em
  `scripts/build_opening_book.py`, até 16 meios-lances, sorteando entre os lances aprovados para variar a abertura. `scripts/vet_opening_book.py` testa
  cada lance com o próprio engine e descarta os ruins. Fora do livro, o engine calcula.
- **Tablebases de finais** (`assets/syzygy/`, até 5 peças, 939 MB, fora do pacote):
  usadas automaticamente se a pasta existir junto do programa. Com o pacote, copie
  `assets/syzygy/` para dentro da pasta extraída ou use `--syzygy <caminho>`. Confira a tela
  inicial: ela precisa mostrar "com tablebases".

O dono informou em 2026-11-04 que a organização aceita o motor, o livro e as tablebases. Para
desligar o livro, use `--book` apontando outro arquivo ou remova `assets/book.bin`.

## Simular um dia de torneio

`python testing/tournament_soak.py --out logs/soak/run.jsonl` joga partidas seguidas em tempo
real e grava NPS, profundidade e relógio de cada lance.

## Histórico

A bancada antiga de A/B do gerenciador está em `archive/youloss-tm/` e os resultados, em
`docs/evidence/`.

## Contribuidores

- [@GuigohC0D3](https://github.com/GuigohC0D3)
- [@victorportelada](https://github.com/victorportelada)
- [@yurihzz](https://github.com/yurihzz)

## Licença

GPLv3, herdada do Stockfish. Ver `engine/Copying.txt`.

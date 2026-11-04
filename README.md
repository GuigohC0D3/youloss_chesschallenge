# Youloss — III Chess Challenge

Stockfish 19 oficial, sem modificações (`engine/`, ver `engine/ORIGIN.md`), com uma
interface local escrita pela equipe: tabuleiro no navegador e um campo para digitar
o lance do adversário. Roda offline em Mac Apple Silicon.

## Jogar

Com o pacote (`dist/stockfish-chess-challenge.tar.gz`), dentro da pasta extraída:

```bash
./launch_stockfish.sh --dry-run   # confere o Mac; rode antes da partida
./launch_stockfish.sh             # abre o tabuleiro no navegador
```

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

Fechar o programa (Ctrl-C) não perde a partida: ao abrir de novo aparece **Retomar**.
Logs por lance ficam em `logs/`. O lançador impede o Mac de dormir, mas não com a
tampa fechada: mantenha aberto e na tomada.

## M4 e M5

O binário é único: ARMv8.2 genérico, macOS 11 ou mais novo, sem instruções exclusivas
de nenhum chip. Threads e Hash são escolhidos ao iniciar:

- Threads: núcleos P + 1/3 dos E. Dá 6 em M4/M5 de 10 núcleos, o perfil medido em
  `docs/evidence/2026-10-06-m4-thermal-thread-profile.md`.
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

## Tablebases e livro

Opcionais e fora do pacote. Se existirem `assets/syzygy/` (até 5 peças) ou
`assets/book.bin` junto do programa, são usados. O uso depende de confirmação da
organização: ver `docs/organizer-clarification-draft.md`.

## Histórico

O gerenciador de tempo autoral (YoulossTM) foi retirado. A bancada está em
`archive/youloss-tm/`, o código no git até o commit `39b0913` e os resultados em
`docs/evidence/`.

## Contribuidores

- [@GuigohC0D3](https://github.com/GuigohC0D3)
- [@victorportelada](https://github.com/victorportelada)
- [@yurihzz](https://github.com/yurihzz)

## Licença

GPLv3, herdada do Stockfish. Ver `engine/Copying.txt`.

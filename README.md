# Youloss — III Chess Challenge

Motor de xadrez baseado em fork do Stockfish (ver `engine/ORIGIN.md`), com
gestão de tempo autoral e CLI de operador em Python.

## Setup (macOS — máquina do torneio)
1. `scripts/check_toolchain.sh` — valida Xcode CLT (clang++/llvm-profdata)/make/Python.
2. `scripts/build_engine.sh` — compila o engine (`apple-silicon`, PGO) em `bin/youloss`.
3. `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
4. `.venv/bin/python -m pytest controller/tests testing/tests -v`
5. `scripts/build_fastchess.sh` e `scripts/fetch_openings.sh` (com rede) para smoke/SPRT.

## Setup (Windows)
Mesmos passos, com MSYS2/g++ e `py -3.12 -m venv .venv`; o python fica em
`.venv/Scripts/python` e os binários em `bin/*.exe`. Os scripts detectam a
plataforma via `scripts/platform.sh`.

## Operação (controller)

```bash
.venv/bin/python -m controller.main start --color white --opponent "Equipe X" --game 1
.venv/bin/python -m controller.main start --resume        # após crash ou quit
.venv/bin/python -m controller.game_log logs/<arquivo>.log  # valida o log
```

No prompt: lance do adversário em UCI (`e2e4`, `e7e8q`) ou um comando
(`undo`, `fen <FEN>`, `clock <nós mm:ss> <adv mm:ss>`, `board`, `go`,
`resign nos|adv`, `draw`, `quit`, `help`). Antes do evento:
`bash scripts/fetch_syzygy.sh` (com rede) e `bash scripts/verify_assets.sh` (offline).

## Licença
GPLv3 (herdada do Stockfish). Ver `engine/Copying.txt`.

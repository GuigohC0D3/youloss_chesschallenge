# Youloss — III Chess Challenge

Motor de xadrez baseado em fork do Stockfish (ver `engine/ORIGIN.md`), com
gestão de tempo autoral e CLI de operador em Python.

## Setup (Windows)
1. `scripts/check_toolchain.sh` — valida MSYS2/g++/make/Python.
2. `scripts/build_engine.sh` — compila o engine em `bin/`.
3. `py -3.12 -m venv .venv && .venv/Scripts/pip install -r requirements.txt`
4. `.venv/Scripts/python -m pytest controller/tests -v`

## Operação (controller)

```bash
.venv/Scripts/python -m controller.main start --color white --opponent "Equipe X" --game 1
.venv/Scripts/python -m controller.main start --resume        # após crash ou quit
.venv/Scripts/python -m controller.game_log logs/<arquivo>.log  # valida o log
```

No prompt: lance do adversário em UCI (`e2e4`, `e7e8q`) ou um comando
(`undo`, `fen <FEN>`, `clock <nós mm:ss> <adv mm:ss>`, `board`, `go`,
`resign nos|adv`, `draw`, `quit`, `help`). Antes do evento:
`bash scripts/fetch_syzygy.sh` (com rede) e `bash scripts/verify_assets.sh` (offline).

## Licença
GPLv3 (herdada do Stockfish). Ver `engine/Copying.txt`.

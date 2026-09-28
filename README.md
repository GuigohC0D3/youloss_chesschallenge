# Youloss — III Chess Challenge

Motor de xadrez baseado em fork do Stockfish (ver `engine/ORIGIN.md`), com
gestão de tempo autoral e CLI de operador em Python.

## Setup (Windows)
1. `scripts/check_toolchain.sh` — valida MSYS2/g++/make/Python.
2. `scripts/build_engine.sh` — compila o engine em `bin/`.
3. `py -3.12 -m venv .venv && .venv/Scripts/pip install -r requirements.txt`
4. `.venv/Scripts/python -m pytest controller/tests -v`

## Licença
GPLv3 (herdada do Stockfish). Ver `engine/Copying.txt`.

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
.venv/bin/python -m controller.main start --resume        # diagnóstico/reconciliação do operador
.venv/bin/python -m controller.game_log logs/<arquivo>.log  # valida o log
```

No prompt, protocolo do relógio físico (autoritativo; o interno é estimativa):
`begin` (inicia o relógio), `press <nós mm:ss> [adv mm:ss]` (adversário apertou o dele; leitura física obrigatória, deduz latência conservadora provisória de 2.0s `--clock-latency`, configurável) + lance UCI
dele (`e2e4`, `e7e8q`), `go` (propõe nosso lance, só com nosso relógio
correndo) + `played` (confirma após jogar no físico). Proposta ≠ lance
confirmado: nada avança nem loga `move=` antes de `played`. Outros comandos:
`undo`, `fen <FEN>` (ambos param o relógio e exigem `clock` novo),
`clock <nós mm:ss> <adv mm:ss> [nos|adv|stop]` (omitido preserva
parado/correndo), `board`, `resign nos|adv`, `draw`, `quit`, `help`. Padrão de tempo `1500+0` PROVISÓRIO (interpretação de
"25 min cada"; o PDF não define incremento). Sob o regulamento oficial (PDF), crash durante a partida acarreta derrota; `--resume` é ferramenta de diagnóstico e reconciliação do operador (exige `fen` + `clock` e nunca auto-confirma proposta), não resgatando elegibilidade nem permitindo continuar partida dada como perdida. Antes do evento:
`bash scripts/fetch_syzygy.sh` (com rede) e `bash scripts/verify_assets.sh` (offline).

Se a estimativa interna chegar a zero, o controlador para e pede uma leitura
fresca do relógio físico; isso, sozinho, não declara derrota. Leia o relógio e
sincronize com `clock <nosso mm:ss> <adv mm:ss> nos`. `00:00` físico confirmado
registra flag; tempo positivo desconta `--clock-latency` conservador antes de
buscar. Se a margem não comportar busca útil, o controlador propõe um lance
legal imediato de fallback.

Livro Polyglot e Syzygy são opcionais e não fazem parte do conjunto local atual.
Os limites de 10 meios-lances e cinco peças são premissas conservadoras, não
regras confirmadas pelo PDF; só prepare/use esses assets após confirmação da
organização. O engine e o controlador devem iniciar com os assets locais e sem
rede no local do evento.

## Licença
GPLv3 (herdada do Stockfish). Ver `engine/Copying.txt`.

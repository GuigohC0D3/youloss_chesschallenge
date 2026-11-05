# Livro até o 16º meio-lance, com sorteio entre lances (2026-11-05)

Registrado antes de checar o livro novo.

## Mudança

- `controller/book.py`: o livro é consultado até o 16º meio-lance, antes 10.
- Em vez de jogar sempre o lance de maior peso, o livro sorteia entre os lances aprovados da
  posição, proporcional ao peso (`100 − perda em cp`, mínimo 1). Isso varia a abertura de uma
  partida para outra. A perda máxima aceita continua 35 cp, então o sorteio pode escolher um
  lance até 35 cp pior que o melhor da checagem.
- O repertório (`scripts/build_opening_book.py`) não mudou: 110 linhas, que no horizonte de
  16 meios-lances dão 761 posições e 841 lances.

## Checagem, igual à de 2026-11-04

`scripts/vet_opening_book.py` com `bin/stockfish` da `main` `58dbf9f`, profundidade 20,
6 threads, Hash 1024 MiB. Um lance sai se perder mais de 35 cp para o melhor ou deixar o lado
que joga abaixo de −50 cp; o que vem depois dele fica inalcançável e sai junto.

## Regra de decisão

Propor ao dono somente se:

- a checagem terminar sem erro e a releitura do arquivo bater;
- todos os testes passarem;
- duas partidas curtas pela interface (`testing/tournament_soak.py --tc 300+0`) terminarem
  sem erro, sem lance de emergência e com lances de livro registrados.

Isso confere que o livro funciona, não que ele melhora o resultado. Nenhuma partida aqui mede
força.

## Desvio registrado antes do resultado

A primeira checagem, de 19h16 a 19h26, parou na releitura do arquivo: duas transposições chegam
à mesma posição com contadores de lance diferentes. O script separava posições pelo FEN
completo, mas o Polyglot as junta numa chave só. O script passou a separar por EPD, que ignora
os contadores, e ganhou testes em `testing/tests/test_vet_opening_book.py`. Os critérios de
checagem não mudaram, e a checagem foi refeita do zero.

## Resultado

**A regra falhou na terceira condição.** O livro funcionou; a falha veio do desenho do teste.

Checagem: 698 lances em 628 posições, 52 recusados de 840, releitura do arquivo correta
(`docs/evidence/2026-11-05-book-vetting.md`). Testes: 255 passaram. Em 2.000 aberturas
simuladas com os dois lados no livro, o primeiro lance de brancas se dividiu entre `d4`, `Nf3`,
`e4` e `c4`, e saíram 72 linhas diferentes.

Partidas `300+0` contra `stockfish_sf19` (`logs/book-20261105/`):

| Partida | Cor | Resultado | Lances de livro | Relógio final | Lances de emergência |
|---|---|---|---:|---:|---:|
| 1 | brancas | empate (repetição), 76 meios-lances | 3 | 87 s | 0 |
| 2 | pretas | derrota (mate), 143 meios-lances | 7 | −42 s | **11** |

Na partida 2, o motor pensou só 57 s no total. O custo simulado de 4 s por lance (2 s em cada
transição do relógio) somou 284 s em 71 lances, quase os 300 s da partida inteira. Com esse
custo, `300+0` não comporta uma partida longa, com ou sem livro. O teste foi mal escolhido para
esse custo por lance.

O livro jogou de 3 a 7 lances por partida, sem erro. Por esta regra, o livro não entra.


## Segunda rodada, registrada antes de jogar

O dono autorizou repetir as partidas no tempo do torneio. A reprovação acima continua valendo;
esta é uma regra nova, escrita antes das partidas.

Duas partidas `1500+0` pelo `testing/tournament_soak.py`, uma de cada cor, contra
`stockfish_sf19`, com o mesmo binário e o mesmo livro. Propor ao dono somente se as duas
terminarem sem erro, sem lance de emergência, sem relógio zerado e com lances de livro
registrados. Duas partidas não medem força.

### Resultado da segunda rodada

**A regra da segunda rodada passou.** Registros em `logs/book-20261105-1500/`.

| Partida | Cor | Resultado | Meios-lances | Lances de livro | Último no livro | Relógio final | Maior lance | Emergência |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | brancas | empate (afogamento) | 140 | 8 | 15 | 418 s | 46,0 s | 0 |
| 2 | pretas | empate (repetição) | 101 | 7 | 14 | 658 s | 69,2 s | 0 |

As duas abriram por linhas diferentes (Inglesa e Francesa). O adversário era `stockfish_sf19`
com 1 thread e 2 s por lance; isto confere o funcionamento, não força.

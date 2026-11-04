# YoulossTM: estouro de tempo em partidas longas (2026-11-04)

Registrado antes de medir a correção.

## Problema observado

Na simulação em 1500+0 (`logs/soak-20261104/`), partida 1, a posição estava em +0,00 e o motor
repetia lances, mas pensou 58 s e 88 s. Os 88 s batem com o teto de `5 × base`. A hipótese é
que lances equivalentes troquem de lugar, levantando a instabilidade sem significado real.

## Correção

Quando a avaliação atual, a média do lance anterior e a iteração anterior estão todas em
±2 unidades internas (cerca de 0,01 peão), o tempo-alvo passa a ser
`optimum × estabilidade × 0,5`, ignorando instabilidade, queda e esforço.

## Segundo problema, visto na mesma partida antes de qualquer medição desta correção

A partida 1 da simulação perdeu: o relógio interno zerou no lance 72 com a posição em +0,00,
e os lances de emergência levaram a mate. Foram 1213 s pensando e 352 s de descontos do
operador (4 s por lance). O orçamento do YoulossTM desconta `Move Overhead` uma vez só, e o
do Stockfish original multiplica pelos lances restantes.

## Segunda correção

- O orçamento reserva `Move Overhead × horizonte`, com piso de 1/4 do relógio para o lance não
  sair sem busca nenhuma.
- `MOVE_OVERHEAD_MS` passa de 1500 para 4000, o custo por lance que o controlador já desconta.

## Medições, nesta ordem, depois que a simulação terminar

1. Triagem: esta branch contra a `main` (`9df551c`), `60+0`, 1 thread, Hash 128 MiB, Move
   Overhead 60 ms, concorrência 4, 30 rodadas pareadas, 60 partidas.
2. Duas partidas 1500+0 pelo `testing/tournament_soak.py`, uma de cada cor, com esta branch.
3. Controle: as mesmas duas partidas com `--stock-tm` (gerenciador original), na mesma branch.

## Regra de decisão

Propor a correção ao dono somente se:

- a triagem não tiver perda no tempo nem crash e der **pelo menos 45%**;
- nas partidas 1500+0 não houver lance de emergência nem relógio zerado;
- nenhum lance em +0,00 passar de 30 s depois de 3 lances seguidos nessa avaliação.

O controle indica se o gerenciador original é mais seguro nessas condições. Duas partidas
de cada lado não medem força.

A triagem não prova ganho de força. Se a regra falhar, a correção não entra.

## Resultado

**A regra falhou: a correção não entra pela regra.** Falta a decisão do dono.

Triagem contra a `main`, `60+0`: 1V 59E 0D em 60 partidas (50,83%), sem perda no tempo nem
crash, `check_fastchess_log.sh` PASS. Critério atendido. Isso mostra que não houve regressão,
não ganho de força.

Partidas `1500+0`, todas com Move Overhead 4000 ms:

| Gerenciador | Cor | Resultado | Meios-lances | Relógio final | Maior lance | Emergência | +0,00 acima de 30 s |
|---|---|---|---:|---:|---:|---:|---|
| Correção | brancas | empate | 123 | 246 s | 94,4 s | 0 | **`Kd3`, meio-lance 105, 39,3 s** |
| Correção | pretas | empate | 183 | 262 s | 34,9 s | 0 | nenhum |
| Original | brancas | empate | 131 | 158 s | 112,5 s | 0 | `Nf3`, meio-lance 65, 112,5 s |
| Original | pretas | empate | 134 | 280 s | 94,8 s | 0 | nenhum |

Critério de lances de emergência e relógio zerado: atendido. Critério de +0,00 acima de 30 s:
**não atendido**, por causa de `Kd3`. Ele veio depois de pelo menos 3 lances seguidos em +0,00,
com cerca de 337 s no relógio antes de pensar.

O controle mostra o gerenciador original sem queda de bandeira nessas duas partidas, e também
com um lance longo em +0,00. A regra não se aplica a ele; a comparação é apenas informativa.
Duas partidas de cada lado não separam o efeito da reserva de 4000 ms do efeito da redução em
posições empatadas.

A causa de `Kd3` não foi determinada. O log guarda só a avaliação final de cada lance, não a
de cada iteração.

## Decisão do dono

Em 2026-11-04, depois de ver estes resultados, o dono escolheu usar a correção como está. É uma
**exceção à regra acima, não uma aprovação por ela**: o critério de +0,00 continua reprovado e o
limite de 30 s não foi alterado.

A recomendação apresentada ao dono foi manter ativa a modificação autoral, por causa da exigência
de "modificações algorítmicas significativas" do regulamento, já que o critério reprovado mede
desperdício de tempo, não segurança. A organização ainda não confirmou se aceita o motor. A causa
de `Kd3` continua desconhecida e nada aqui mostra ganho de força.

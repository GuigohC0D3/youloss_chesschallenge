# Youloss Chess Engine — Design Spec

Data: 2026-09-28 · Evento: III Chess Challenge (2026-11-06) · Equipe: 3 pessoas

> **Status (2026-09-30):** Este é o documento de design original, não o registro
> autoritativo do estado atual. Use `README.md` para operação e
> `docs/superpowers/plans/2026-09-28-local-tournament-excellence.md` para os
> riscos, gates e próximos passos revistos. A agenda S0–S4 abaixo é histórica;
> não representa confirmação de conclusão nem de resultado de força.

## 1. Objetivo

Motor de xadrez que dispute o III Chess Challenge, com resposta rápida e
uso ótimo do relógio (25 min por lado; o PDF não especifica incremento, então 1500+0 é provisório até confirmação da organização), atendendo
às premissas de projeto e regras oficiais.

**Critérios de sucesso**
- Joga partidas completas offline no notebook da equipe, sem incidentes operacionais.
- Componente decisório de autoria própria (gestão de tempo) funcional e com ganho
  de Elo medido estatisticamente (SPRT) sobre o gerenciador original.
- Log por lance detalhado (premissa de projeto para auditoria).
- Repositório pronto para entrega à banca, com origem declarada e licença GPLv3.

## 2. Premissas de Projeto e Restrições

> **Nota de conformidade com o regulamento:** O regulamento oficial está consolidado no PDF do evento. As diretrizes abaixo derivadas de FAQ/discussões informais (teto de 10 meios-lances no book, tablebases até 5 peças, autorização de ponder, formato/exigência de log .log por lance) são **premissas de projeto (design assumptions) pendentes de confirmação formal com a organização**, e **não regras expressas no PDF**. Configurações conservadoras são rigorosamente mantidas sem inferir permissão tácita da organização.

| Item | Tópico | Status / Classificação | Como atendemos (postura conservadora) |
|---|---|---|---|
| 1 | Fork e licença | Regra geral / GPLv3 | `engine/` = fork do Stockfish, commit fixado em `ORIGIN.md`; repo público ao final |
| 2 | Componente autoral | Requisito do evento | Gestão de tempo própria (`youloss_tm`) |
| 3 | Book ≤ 10 plies | Premissa de projeto (FAQ, pendente de confirmação) | Controller consulta book Polyglot só enquanto `ply < 10` |
| 4 | Tablebases ≤ 5 peças | Premissa de projeto (FAQ, pendente de confirmação) | Apenas Syzygy 3-4-5 em `assets/syzygy`; `SyzygyProbeLimit=5` |
| 7 | Relógio 25 min por lado | Regra do PDF (incremento não definido; 1500+0 provisório) | Controller mantém relógio e envia `wtime/btime/winc/binc` |
| 9 | Log .log por lance | Premissa de projeto (FAQ, pendente de confirmação) | Logger do controller (durabilidade e auditoria por lance) |
| 10 | Tabuleiro físico | Regra do evento (tabuleiro físico é a verdade) | Entrada UCI validada; comandos de desfazer e ressincronizar por FEN |
| 13 | Ponder | Premissa de projeto (FAQ, pendente de confirmação) | Não usado pelo controller; manter desativado até permissão e fluxo qualificado |
| 14 | Sem rede no evento | Regra do PDF (ambiente offline) | `requirements.txt`; verificação offline de dependências e assets |

## 3. Arquitetura

```
youloss_chesschallenge/
├── engine/                 Fork do Stockfish (commit fixado)
│   ├── ORIGIN.md           Projeto-base, commit/tag, licença
│   └── src/youloss_tm.{h,cpp}   Gestão de tempo autoral
├── controller/             CLI do operador (Python 3.12 + python-chess)
│   ├── main.py             Loop de partida / comandos
│   ├── engine_client.py    Wrapper UCI (processo do engine, ponder)
│   ├── clock.py            Relógio da partida
│   ├── book.py             Consulta Polyglot com corte de ply
│   └── game_log.py         Logger .log
├── assets/                 book .bin, syzygy/ (não versionados; checksums em assets/MANIFEST)
├── testing/                Scripts de SPRT (fastchess), posições de abertura
├── docs/                   Specs, planos, material da arguição
└── requirements.txt
```

**Fronteiras**
- **Engine** — busca e avaliação do Stockfish; decide *quanto tempo pensar*
  através do `youloss_tm`. Único canal: UCI via stdin/stdout.
- **Controller** — dono do estado da partida, relógio, book, ponder e log.
  Não decide lances (exceto lance de book). Nunca depende de detalhes internos do engine.
- **Testing** — só consome o binário do engine via UCI.

## 4. Engine: gestão de tempo autoral (`youloss_tm`)

Substitui a gestão de tempo original quando a opção UCI `YoulossTM=true`
(padrão `true`; `false` restaura o original, para A/B e demonstração).

**Entradas:** tempo restante, incremento, número do lance, material/fase,
histórico de iterações do aprofundamento iterativo (melhor lance, avaliação),
número de lances legais, estado de ponder.

**Modelo**
1. **Orçamento base** — `base = remaining / H(fase) + 0.8 * inc`, onde `H` é o
   horizonte estimado de lances restantes (maior na abertura/meio-jogo, menor no final).
2. **Limites** — `optimum = base * f_ajustes`; `maximum = min(5 * base, 0.25 * remaining)`;
   nunca menos que uma reserva de segurança (`MoveOverhead` + reserva de 1 s abaixo de 10 s).
3. **Ajustes dinâmicos a cada iteração**
   - *Estabilidade da PV:* melhor lance inalterado em N iterações → reduz o orçamento.
   - *Queda de avaliação:* avaliação caindo em relação à iteração anterior ou à média
     dos lances anteriores → estende até `maximum`.
   - *Lance forçado:* 1 lance legal → joga imediatamente; lance único claramente
     melhor (margem grande na busca de verificação) → corta o tempo.
   - *Posição decidida:* |avaliação| muito alta ou mate encontrado → reduz o tempo.
4. **Ponder** — em `ponderhit` o tempo já pensado conta como investimento e o
   orçamento restante é recalculado.
5. **Parâmetros** — expostos como opções UCI para tuning (fastchess/SPSA) na Sprint 3.

**Métrica de aceite proposta:** comparar `YoulossTM=true` × `false` em pares de
cores, com o mesmo binário, opções, book e hardware. Os limites SPRT `[-5, 0]`
(não-regressão) e `[0, 5]` (ganho) são alvos de estudo, não resultados obtidos.
Usar controles sem incremento para refletir a interpretação provisória do evento
(`10+0` apenas para screening e `25+0` para validação final, se a organização
confirmar 25 minutos sem incremento). A smoke atual de dois jogos a `10+0` só
verifica a integração; não sustenta inferência de Elo.

## 5. Controller (CLI do operador)

### 5.1 Fluxo
```
start --color white|black [--tc 1500+0 (provisório)]
loop (relógio físico autoritativo; interno é estimativa; nada anda antes de `begin`):
  partida nova: operador dá `begin` (liga o relógio no lado a mover)
  se é nossa vez (nosso relógio correndo): `go` propõe (book ply<10 ou engine
                  go wtime.. btime.. winc.. binc.. com teto 25% + stop + reserva)
                  → anuncia a PROPOSTA (UCI, destacada) → persiste + loga `# proposal`
                  → operador joga no físico e dá `played` (avanço único: loga `move=`, troca o relógio)
  se é a vez do adversário: adversário joga e aperta o físico → operador dá `press`
                  (liquida o tempo dele, liga o nosso, uma vez) → digita o lance UCI
                  → valida legalidade (sem trocar o relógio de novo)
   resume: exige `fen` + `clock`; proposta pendente nunca é auto-confirmada
                   (`undo`/`fen` param o relógio interno e exigem `clock` novo;
                   busca só com nosso relógio correndo e teto busca+stop+reserva <= restante,
                   com fallback imediato abaixo de 100 ms úteis)
```

### 5.2 Comandos do operador
| Comando | Ação |
|---|---|
| `begin` | Inicia o relógio no lado a mover (partida nova; sem ele não há busca) |
| `press <nosso_mm:ss> [adv_mm:ss]` | O adversário apertou o físico; informa a leitura autoritativa, ressincroniza com margem de latência e liga nosso relógio |
| `<uci>` (ex. `e2e4`, `e7e8q`) | Lance do adversário após `press`; rejeitado se ilegal/sem `press` (repete o prompt; não troca o relógio) |
| `go` | Propõe nosso lance (só na nossa vez E com nosso relógio correndo; parado/vez alheia é recusado, sem busca) |
| `played` | Confirma a proposta após jogar no físico (avanço único; sem proposta é recusado) |
| `undo` | Desfaz o último meio-lance (descarta proposta; para o relógio e exige `clock` novo) |
| `fen <FEN>` | Ressincroniza com o tabuleiro físico (descarta proposta; para o relógio e exige `clock` novo) |
| `clock <nosso_mm:ss> <adv_mm:ss> [nos\|adv\|stop]` | Sincroniza com o relógio físico (omitido preserva parado/correndo; `nos`/`adv` liga um lado, `stop` para) |
| `board` | Mostra o tabuleiro ASCII + FEN |
| `resign` / `draw` / `quit` | Encerra; fecha o log |

### 5.3 Relógio
O relógio físico manual é autoritativo; o relógio monotônico interno é uma
estimativa. O perfil provisório é `1500+0`, de acordo com a interpretação de
25 minutos por lado, sem incremento concedido automaticamente. `press` exige
uma leitura física e desconta a margem configurada de latência (padrão
provisório 2.0 s); uma estimativa interna esgotada pede nova leitura em vez de
declarar flag. Uma leitura física confirmada em `00:00` registra a flag. Se a
margem positiva não comportar busca útil, usa-se o fallback legal imediato.
`Move Overhead` (1500 ms) afeta o orçamento do engine e não substitui a leitura
física nem confirma o valor do relógio.

### 5.4 Log (`logs/<data>_<adversario>_g<n>.log`)
Uma linha por lance nosso (e linha sem busca para os lances do adversário):
```
move=12 color=white uci=g1f3 depth=31 seldepth=44 nodes=182334112 eval=+0.42 pv="g1f3 d7d5 ..." time_ms=21873 source=engine
```
`source` ∈ `engine | book | ponderhit | forced`. Para lances de book:
`depth=0 nodes=0 eval=book`. O log é gravado com flush a cada linha.

### 5.5 Robustez
- Estado salvo em `logs/<partida>.state.json` (FEN, histórico, relógios) a cada lance.
- `start --resume` é uma ferramenta de diagnóstico e reconciliação: exige FEN e
  relógio físico atualizado, e nunca confirma uma proposta pendente. Pelo
  regulamento do evento, um crash durante a partida acarreta derrota; resume ou
  reinício do processo não recupera uma partida perdida.
- Busca e resposta têm limite de parada; a expiração estimada pede leitura
  física, enquanto falha real de resposta do engine deve ser registrada como
  incidente. Isso não garante ausência de flags na operação manual.

## 6. Configuração de runtime
- O código atualmente parte de `Threads = núcleos lógicos − 1` e
  `Hash = 50% da memória disponível`, limitado a 16 GB. Esses defaults ainda
  precisam de medição sustentada no M4 fanless; não são um perfil de torneio
  validado. Os confrontos atuais usam 1 thread e Hash 16 para comparação
  controlada do alocador.
- `SyzygyPath=assets/syzygy`, `SyzygyProbeLimit=5`.
- Build `-march=native` (profile-build), com binário de fallback `x86-64-v3`.
- Windows: plano de energia de alto desempenho, na tomada, Wi-Fi desligado.

## 7. Testes
- **Engine:** `bench` com contagem de nós determinística (1 thread) após cada mudança;
  SPRT do TM (seção 4).
- **Controller:** pytest para validação de lance, corte de book, relógio, formato
  do log, resume a partir do estado e ponderhit/ponder-miss com engine real.
- **Ensaio (S4):** 3 partidas completas com protocolo verbal entre duas máquinas.

## 8. Sprints

Estas datas e gates foram escritos antes da revisão do regulamento e são
mantidos como histórico. O roadmap revisto para 6 de novembro está em
`docs/superpowers/plans/2026-09-28-local-tournament-excellence.md`.

| Sprint | Datas | Entrega | Pronto quando |
|---|---|---|---|
| S0 | 28/09–30/09 | Toolchain (MSYS2 g++, Python, fastchess), fork fixado, build, bench, `ORIGIN.md` | `bench` roda; controller troca `uci`/`isready` com o engine |
| S1 | 01/10–07/10 | Controller MVP: loop, comandos, relógio, book, syzygy, log, estado/resume | Partida completa pela CLI com log válido |
| S2 | 08/10–14/10 | `youloss_tm` v1 + harness SPRT | SPRT de não-regressão aprovado |
| S3 | 15/10–21/10 | Ponder, tuning do TM, tuning de threads/hash, auto-restart | SPRT com ganho positivo; ponder estável |
| S4 | 22/10–28/10 | Freeze em 25/10, ensaios, checklist offline, material da arguição | 3 ensaios sem incidentes; tag `v1.0` |

**Responsáveis:** P1 — engine/TM (C++). P2 — controller (Python). P3 — infra, testes/SPRT,
assets, documentação da arguição e operador principal.

## 9. Fora de escopo
Mudanças na avaliação/NNUE ou na busca do Stockfish; interface gráfica;
leitura automática do tabuleiro físico; uso de GPU.

## 10. Política do repositório
Commits sem linhas de coautoria de IA. Dependências declaradas em
`requirements.txt`; assets grandes fora do git, com checksums em `assets/MANIFEST`.

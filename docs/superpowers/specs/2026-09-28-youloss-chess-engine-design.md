# Youloss Chess Engine — Design Spec

Data: 2026-09-28 · Evento: III Chess Challenge (~2026-10-28) · Equipe: 3 pessoas

## 1. Objetivo

Motor de xadrez que vença os motores das outras equipes no III Chess Challenge,
com resposta rápida e uso ótimo do relógio (15 min + 10 s/lance), atendendo
todas as regras do FAQ do evento.

**Critérios de sucesso**
- Joga partidas completas offline no notebook da equipe, sem incidentes operacionais.
- Componente decisório de autoria própria (gestão de tempo) funcional e com ganho
  de Elo medido estatisticamente (SPRT) sobre o gerenciador original.
- Log por lance em conformidade com o FAQ item 9.
- Repositório pronto para entrega à banca, com origem declarada e licença GPLv3.

## 2. Restrições (do FAQ)

| Item | Restrição | Como atendemos |
|---|---|---|
| 1 | Fork permitido; declarar projeto-base e commit; GPLv3 | `engine/` = fork do Stockfish, commit fixado em `ORIGIN.md`; repo público ao final |
| 2 | ≥1 componente decisório autoral | Gestão de tempo própria (`youloss_tm`) |
| 3 | Book ≤ 10 meios-lances, baixado antes | Controller consulta book Polyglot só enquanto `ply < 10` |
| 4 | Tablebases ≤ 5 peças | Apenas Syzygy 3-4-5 em `assets/syzygy`; `SyzygyProbeLimit=5` |
| 7 | Relógio 15+10 | Controller mantém relógio e envia `wtime/btime/winc/binc` |
| 9 | Log .log por lance | Logger do controller (formato na seção 5.4) |
| 10 | Lances em UCI, tabuleiro físico é a verdade | Entrada UCI validada; comandos de desfazer e ressincronizar por FEN |
| 13 | Ponder permitido | `go ponder` / `ponderhit` no controller |
| 14 | Sem rede; dependências declaradas | `requirements.txt`; checklist offline |

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

**Métrica de aceite:** SPRT `YoulossTM=true` × `false`. Na S2 exige-se não-regressão
(elo0=-5, elo1=0). Na S3 exige-se ganho positivo (elo0=0, elo1=5). O teste usa
15+10 escalado (ex.: 60+0.6 e 180+2), 1 thread, e confirmação final em 15+10 real com poucas partidas.

## 5. Controller (CLI do operador)

### 5.1 Fluxo
```
start --color white|black [--tc 900+10]
loop:
  se é nossa vez: book (ply<10) ou engine (go wtime.. btime.. winc.. binc..)
                  → anuncia o lance (UCI, destacado) → loga → inicia ponder
  se é a vez do adversário: operador digita o lance UCI
                  → valida legalidade → ponderhit ou stop+nova busca
```

### 5.2 Comandos do operador
| Comando | Ação |
|---|---|
| `<uci>` (ex. `e2e4`, `e7e8q`) | Lance do adversário; rejeitado se ilegal (repete o prompt) |
| `undo` | Desfaz o último meio-lance |
| `fen <FEN>` | Ressincroniza com o tabuleiro físico |
| `clock <nosso_mm:ss> <adv_mm:ss>` | Sincroniza com o relógio físico |
| `board` | Mostra o tabuleiro ASCII + FEN |
| `resign` / `draw` / `quit` | Encerra; fecha o log |

### 5.3 Relógio
Relógio interno por lado (monotonic), com incremento após cada lance. Por
padrão, o tempo do adversário corre do nosso anúncio até a confirmação do lance dele.
Divergências são corrigidas pelo comando `clock`. O `MoveOverhead` do engine
cobre a latência de anúncio e acionamento do relógio (ajuste inicial: 1500 ms).

### 5.4 Log (`logs/<data>_<adversario>_g<n>.log`)
Uma linha por lance nosso (e linha sem busca para os lances do adversário):
```
move=12 color=white uci=g1f3 depth=31 seldepth=44 nodes=182334112 eval=+0.42 pv="g1f3 d7d5 ..." time_ms=21873 source=engine
```
`source` ∈ `engine | book | ponderhit | forced`. Para lances de book:
`depth=0 nodes=0 eval=book`. O log é gravado com flush a cada linha.

### 5.5 Robustez
- Estado salvo em `logs/<partida>.state.json` (FEN, histórico, relógios) a cada lance.
- `start --resume` retoma após crash; o engine é relançado automaticamente se o processo cair.
- Timeout de segurança: se o engine não responder em `optimum + 2 s`, envia `stop`.

## 6. Configuração de runtime
- `Threads` = núcleos lógicos − 1 (validar por bench na S3); `Hash` = 50% da RAM livre, limitado a 16 GB.
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

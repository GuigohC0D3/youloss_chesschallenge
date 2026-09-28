# Sprint 1 — Controller MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CLI do operador que joga uma partida completa contra um adversário externo: relógio, book, Syzygy, log por lance, comandos do operador e retomada após crash.

**Architecture:** O controller é dividido em módulos pequenos e testáveis isoladamente (`clock`, `book`, `game_log`, `state`, `runtime`), com o loop da partida em `game.py`. `game.py` recebe todas as dependências injetadas (engine, book, log, relógio, funções de entrada e saída), então os testes rodam o loop com um engine falso e respostas roteirizadas. `main.py` só monta as peças a partir dos argumentos. O engine continua sendo acessado apenas via UCI pelo `EngineClient`, que ganha o método `search`.

**Tech Stack:** Python 3.12, python-chess 1.11.2 (validação de lances, Polyglot), pytest 8.3.3, Stockfish `sf_19` em `bin/youloss.exe`, MSYS2 bash para scripts.

**Spec:** `docs/superpowers/specs/2026-09-28-youloss-chess-engine-design.md` (seções 2, 5, 6, 7 e 8/S1)

## Global Constraints

- Commits **sem** linhas `Co-Authored-By` de IA ou qualquer atribuição de IA.
- Nenhuma dependência de rede em runtime. Downloads (Syzygy, book) só por script, antes do evento.
- Book consultado só enquanto `ply < 10` (FAQ item 3).
- Tablebases: apenas Syzygy 3-4-5 em `assets/syzygy`; `SyzygyProbeLimit=5` (FAQ item 4).
- Relógio 15+10: o controller envia `wtime/btime/winc/binc` (FAQ item 7).
- Log `.log` por lance, com flush a cada linha, em `logs/<data>_<adversario>_g<n>.log` (FAQ item 9, spec 5.4).
- Lances do operador em UCI; tabuleiro físico é a verdade (`undo`, `fen`) (FAQ item 10).
- Dependências Python declaradas em `requirements.txt` com versões fixadas. Esta sprint não adiciona nenhuma.
- `assets/`, `logs/`, `bin/` fora do git; checksums dos assets em `assets/MANIFEST`.
- `MoveOverhead` inicial: 1500 ms. `Threads` = núcleos lógicos − 1. `Hash` = 50% da RAM livre, limitado a 16 GB.
- Fora desta sprint (S3): ponder/`ponderhit` e auto-restart do engine. Na S1, se o engine cair, o controller salva o estado e sai com código 2 para `start --resume`.

## Review Focus

1. **Erro de digitação no lance do adversário** (maiúsculas, espaços, promoção sem peça, texto qualquer, linha vazia): o controller repete o prompt sem avançar a partida nem cair. Testes na Task 7.
2. **Engine que morre ou trava no meio da partida**: mensagem clara, estado salvo, saída com código 2, e `--resume` continua dali. Testes nas Tasks 3, 7 e 9.
3. **`start` repetido com o mesmo adversário, partida e dia**: recusa com mensagem e nunca sobrescreve um log existente. Teste na Task 9.
4. **Relógio zerado ou negativo** (operador sincronizou com o físico em apuros): o `go` nunca manda tempo ≤ 0 e o timeout de segurança continua positivo. Teste na Task 7.
5. **Arquivo de estado corrompido ou meio escrito**: a gravação é atômica, e o `--resume` falha com `StateError` legível, sem traceback. Testes na Task 5.

## Decisões desta sprint (desvios pequenos do spec, justificados)

- **`go`**: novo comando. Depois de `undo` ou `fen`, se for a nossa vez, o controller **pausa** em vez de mandar o engine jogar na hora. Assim o operador pode desfazer mais de um meio-lance antes de retomar. A pausa também sai sozinha quando um lance do adversário é aceito.
- **`resign nos|adv`**: o spec lista `resign` sem dizer quem abandonou; o argumento remove a ambiguidade no log.
- **`help`**: lista os comandos.
- **Lance forçado** (1 lance legal): o controller joga na hora, sem chamar o engine (`source=forced`).
- **Linhas de comentário no log** começam com `# ` (cabeçalho, `undo`, `fen`, `clock`, resultado). As linhas de lance seguem exatamente o formato 5.4. Os lances do adversário usam `source=opponent`.
- **Book**: o controller aceita qualquer `.bin` Polyglot (`--book`, padrão `assets/book.bin` se existir). A escolha do arquivo de book é uma decisão da equipe e fica em aberto (ver "Definição de pronto").

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `controller/clock.py` | `parse_tc`, `parse_mmss`, `format_mmss`, `GameClock` |
| `controller/book.py` | `OpeningBook` (Polyglot com corte de ply), `game_ply` |
| `controller/engine_client.py` | + `SearchInfo`, `parse_info`, `EngineClient.search` |
| `controller/game_log.py` | `GameLog`, `LINE_RE`, `log_path`, `format_eval`, `check_log` (CLI validador) |
| `controller/state.py` | `GameState`, `save_state` (atômico), `load_state`, `latest_unfinished` |
| `controller/runtime.py` | `runtime_options` (Threads/Hash/MoveOverhead/Syzygy), `free_memory_mb` |
| `controller/game.py` | `Game`: loop, nosso lance, lance do adversário, comandos |
| `controller/main.py` | CLI `start` / `--resume`, montagem das dependências |
| `scripts/fetch_syzygy.sh`, `scripts/verify_assets.sh` | Download das Syzygy 3-4-5 + MANIFEST; verificação offline |
| `controller/tests/fake_engine.py` | + modos com `position`/`go`: `ok`, `slow`, `deaf`, `dieongo` |
| `controller/tests/polyglot.py` | `write_book` (gera book Polyglot mínimo para testes) |
| `controller/tests/scripted.py` | `Script` (input roteirizado), `fake_engine`, `FAKE`, `REAL` |
| `controller/tests/conftest.py` | fixture `games` (monta `Game` com engine falso) |

Todos os comandos abaixo rodam do root do repo, no bash do MSYS2 (ou Git Bash), com o venv:
`PY=.venv/Scripts/python`.

---

### Task 1: Relógio da partida

**Files:**
- Create: `controller/clock.py`
- Test: `controller/tests/test_clock.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `class ClockFormatError(ValueError)`
  - `parse_tc(text: str) -> tuple[int, int]` → `(base_ms, inc_ms)`
  - `parse_mmss(text: str) -> int` (ms)
  - `format_mmss(ms: int) -> str`
  - `GameClock(base_ms: int, inc_ms: int, now: Callable[[], float] = time.monotonic)` com `inc_ms`, `running: chess.Color | None`, `remaining(color) -> int`, `start(color) -> None`, `press() -> int` (ms gastos pelo lado que jogou), `set(color, ms) -> None`

- [ ] **Step 1: Escrever os testes que falham**

```python
import chess
import pytest

from controller.clock import (
    ClockFormatError, GameClock, format_mmss, parse_mmss, parse_tc,
)


class FakeTime:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


def test_parse_tc():
    assert parse_tc("900+10") == (900_000, 10_000)
    assert parse_tc(" 60+0.6 ") == (60_000, 600)


@pytest.mark.parametrize("bad", ["900", "abc", "0+1", "900+", "+10", "-5+1"])
def test_parse_tc_rejects(bad):
    with pytest.raises(ClockFormatError):
        parse_tc(bad)


def test_parse_mmss():
    assert parse_mmss("14:59") == 899_000
    assert parse_mmss("0:05") == 5_000
    assert parse_mmss("100:00") == 6_000_000


@pytest.mark.parametrize("bad", ["1:60", "abc", "-1:00", "10", "1:5"])
def test_parse_mmss_rejects(bad):
    with pytest.raises(ClockFormatError):
        parse_mmss(bad)


def test_format_mmss():
    assert format_mmss(899_000) == "14:59"
    assert format_mmss(500) == "0:00"
    assert format_mmss(-3_000) == "-0:03"


def test_press_charges_mover_adds_increment_and_switches():
    t = FakeTime()
    clock = GameClock(60_000, 1_000, now=t)
    clock.start(chess.WHITE)
    t.t += 3
    assert clock.remaining(chess.WHITE) == 57_000
    assert clock.press() == 3_000
    assert clock.remaining(chess.WHITE) == 58_000
    assert clock.running == chess.BLACK
    t.t += 2
    assert clock.remaining(chess.BLACK) == 58_000


def test_set_overrides_running_side():
    t = FakeTime()
    clock = GameClock(60_000, 1_000, now=t)
    clock.start(chess.BLACK)
    t.t += 10
    clock.set(chess.BLACK, 5_000)
    assert clock.remaining(chess.BLACK) == 5_000
    t.t += 1
    assert clock.remaining(chess.BLACK) == 4_000


def test_start_switches_without_increment():
    t = FakeTime()
    clock = GameClock(60_000, 1_000, now=t)
    clock.start(chess.WHITE)
    t.t += 2
    clock.start(chess.BLACK)
    assert clock.remaining(chess.WHITE) == 58_000
    assert clock.running == chess.BLACK


def test_press_when_stopped_raises():
    with pytest.raises(RuntimeError):
        GameClock(60_000, 0).press()
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `$PY -m pytest controller/tests/test_clock.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'controller.clock'`

- [ ] **Step 3: Implementar `controller/clock.py`**

```python
"""Relógio da partida: um contador por lado, com incremento a cada lance."""
from __future__ import annotations

import re
import time
from typing import Callable

import chess

_TC_RE = re.compile(r"^(\d+(?:\.\d+)?)\+(\d+(?:\.\d+)?)$")
_MMSS_RE = re.compile(r"^(\d{1,3}):([0-5]\d)$")


class ClockFormatError(ValueError):
    pass


def parse_tc(text: str) -> tuple[int, int]:
    """'900+10' (segundos) -> (base_ms, inc_ms)."""
    m = _TC_RE.match(text.strip())
    if not m:
        raise ClockFormatError(
            f"controle de tempo inválido: {text!r} (use base+inc em segundos, ex. 900+10)"
        )
    base_ms, inc_ms = round(float(m[1]) * 1000), round(float(m[2]) * 1000)
    if base_ms <= 0:
        raise ClockFormatError(f"tempo base precisa ser positivo: {text!r}")
    return base_ms, inc_ms


def parse_mmss(text: str) -> int:
    m = _MMSS_RE.match(text.strip())
    if not m:
        raise ClockFormatError(f"tempo inválido: {text!r} (use mm:ss, ex. 14:59)")
    return (int(m[1]) * 60 + int(m[2])) * 1000


def format_mmss(ms: int) -> str:
    sign = "-" if ms < 0 else ""
    s = abs(ms) // 1000
    return f"{sign}{s // 60}:{s % 60:02d}"


class GameClock:
    def __init__(
        self, base_ms: int, inc_ms: int, now: Callable[[], float] = time.monotonic
    ):
        self.inc_ms = inc_ms
        self._now = now
        self._ms = {chess.WHITE: base_ms, chess.BLACK: base_ms}
        self.running: chess.Color | None = None
        self._since = 0.0

    def _settle(self, t: float) -> None:
        # Desconta do lado que está correndo o tempo desde o último acerto.
        if self.running is not None:
            self._ms[self.running] -= round((t - self._since) * 1000)
            self._since = t

    def remaining(self, color: chess.Color) -> int:
        ms = self._ms[color]
        if color == self.running:
            ms -= round((self._now() - self._since) * 1000)
        return ms

    def start(self, color: chess.Color) -> None:
        """Liga o relógio de `color` (sem incremento para quem parou)."""
        t = self._now()
        self._settle(t)
        self.running = color
        self._since = t

    def press(self) -> int:
        """O lado que está correndo jogou: desconta, soma incremento e liga o outro."""
        if self.running is None:
            raise RuntimeError("relógio parado")
        t = self._now()
        side = self.running
        spent = round((t - self._since) * 1000)
        self._ms[side] += self.inc_ms - spent
        self.running = not side
        self._since = t
        return spent

    def set(self, color: chess.Color, ms: int) -> None:
        t = self._now()
        self._settle(t)
        self._ms[color] = ms
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `$PY -m pytest controller/tests/test_clock.py -q`
Expected: todos passam.

- [ ] **Step 5: Commit**

```bash
git add controller/clock.py controller/tests/test_clock.py
git commit -m "feat(controller): relógio da partida com incremento e sincronização"
```

---

### Task 2: Book Polyglot com corte de ply

**Files:**
- Create: `controller/book.py`, `controller/tests/polyglot.py`
- Test: `controller/tests/test_book.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `MAX_BOOK_PLY = 10`
  - `class BookError(Exception)`
  - `game_ply(board: chess.Board) -> int`
  - `OpeningBook(path: str | Path | None, max_ply: int = MAX_BOOK_PLY)` com `path: Path | None`, `pick(board) -> chess.Move | None`, `close() -> None`
  - Teste: `controller.tests.polyglot.write_book(path: Path, entries: list[tuple[chess.Board, str, int]]) -> None`

- [ ] **Step 1: Criar o gerador de book para testes (`controller/tests/polyglot.py`)**

```python
"""Gera um book Polyglot mínimo para testes (sem promoção nem roque)."""
from __future__ import annotations

import struct
from pathlib import Path

import chess
import chess.polyglot


def write_book(path: Path, entries: list[tuple[chess.Board, str, int]]) -> None:
    rows = []
    for board, uci, weight in entries:
        move = chess.Move.from_uci(uci)
        raw = move.to_square | (move.from_square << 6)
        rows.append((chess.polyglot.zobrist_hash(board), raw, weight))
    rows.sort()
    with open(path, "wb") as f:
        for key, raw, weight in rows:
            f.write(struct.pack(">QHHI", key, raw, weight, 0))
```

- [ ] **Step 2: Escrever os testes que falham**

```python
import chess
import pytest

from controller.book import BookError, OpeningBook, game_ply
from controller.tests.polyglot import write_book

# Giuoco Piano: 10 meios-lances.
LINE = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "c2c3", "g8f6", "d2d4", "e5d4"]


def board_after(n: int) -> chess.Board:
    board = chess.Board()
    for uci in LINE[:n]:
        board.push_uci(uci)
    return board


def test_game_ply():
    assert game_ply(chess.Board()) == 0
    assert game_ply(board_after(1)) == 1
    assert game_ply(board_after(10)) == 10


def test_picks_highest_weight(tmp_path):
    path = tmp_path / "b.bin"
    write_book(path, [(chess.Board(), "d2d4", 5), (chess.Board(), "e2e4", 9)])
    book = OpeningBook(path)
    assert book.pick(chess.Board()) == chess.Move.from_uci("e2e4")
    book.close()


def test_cut_at_ply_10(tmp_path):
    path = tmp_path / "b.bin"
    write_book(path, [(board_after(9), "e5d4", 1), (board_after(10), "c3d4", 1)])
    book = OpeningBook(path)
    assert book.pick(board_after(9)) == chess.Move.from_uci("e5d4")
    assert book.pick(board_after(10)) is None
    book.close()


def test_unknown_position_returns_none(tmp_path):
    path = tmp_path / "b.bin"
    write_book(path, [(chess.Board(), "e2e4", 1)])
    book = OpeningBook(path)
    assert book.pick(board_after(1)) is None
    book.close()


def test_no_book():
    assert OpeningBook(None).pick(chess.Board()) is None


def test_empty_book_file(tmp_path):
    path = tmp_path / "vazio.bin"
    path.write_bytes(b"")
    assert OpeningBook(path).pick(chess.Board()) is None


def test_missing_book_raises(tmp_path):
    with pytest.raises(BookError, match="nao_existe.bin"):
        OpeningBook(tmp_path / "nao_existe.bin")
```

- [ ] **Step 3: Rodar e confirmar que falha**

Run: `$PY -m pytest controller/tests/test_book.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'controller.book'`

- [ ] **Step 4: Implementar `controller/book.py`**

```python
"""Book Polyglot consultado só nos primeiros meios-lances (FAQ item 3)."""
from __future__ import annotations

from pathlib import Path

import chess
import chess.polyglot

MAX_BOOK_PLY = 10


class BookError(Exception):
    pass


def game_ply(board: chess.Board) -> int:
    """Meios-lances jogados desde o início (vale também após `fen`)."""
    return (board.fullmove_number - 1) * 2 + (board.turn == chess.BLACK)


class OpeningBook:
    def __init__(self, path: str | Path | None, max_ply: int = MAX_BOOK_PLY):
        self.path = Path(path) if path else None
        self.max_ply = max_ply
        self._reader: chess.polyglot.MemoryMappedReader | None = None
        if self.path:
            try:
                self._reader = chess.polyglot.open_reader(self.path)
            except OSError as exc:
                raise BookError(f"book não pôde ser aberto: {self.path}: {exc}") from exc

    def pick(self, board: chess.Board) -> chess.Move | None:
        if self._reader is None or game_ply(board) >= self.max_ply:
            return None
        try:
            return self._reader.find(board).move
        except IndexError:
            return None

    def close(self) -> None:
        if self._reader is not None:
            self._reader.close()
            self._reader = None
```

- [ ] **Step 5: Rodar e confirmar que passa**

Run: `$PY -m pytest controller/tests/test_book.py -q`
Expected: todos passam.

- [ ] **Step 6: Commit**

```bash
git add controller/book.py controller/tests/polyglot.py controller/tests/test_book.py
git commit -m "feat(controller): book Polyglot com corte em 10 meios-lances"
```

---

### Task 3: `EngineClient.search` com parse de `info` e stop de segurança

**Files:**
- Modify: `controller/engine_client.py` (imports no topo; novo código após `EngineCrashed` e novo método após `set_option`)
- Modify: `controller/tests/fake_engine.py` (reescrito, mantendo os modos existentes)
- Test: `controller/tests/test_search.py`

**Interfaces:**
- Consumes: `EngineClient.send`, `EngineClient.read_line`, `EngineTimeout`, `EngineCrashed`, `EngineError` (Sprint 0).
- Produces:
  - `@dataclass SearchInfo(bestmove: str, ponder: str | None = None, depth: int = 0, seldepth: int = 0, nodes: int = 0, score_cp: int | None = None, score_mate: int | None = None, pv: list[str] = [], stopped: bool = False)`
  - `parse_info(line: str, into: SearchInfo) -> None`
  - `EngineClient.search(position: str, go: str, timeout: float, stop_grace: float = 2.0) -> SearchInfo`. Manda `stop` quando `timeout` estoura. Levanta `EngineTimeout` se nem o `stop` gerar `bestmove`, e `EngineError` se vier `bestmove (none)`.
  - Engine falso: modos `ok` (responde `go` com o menor lance legal em ordem UCI, `info depth 5 seldepth 7 score cp 12 nodes 1234`), `slow` (só responde no `stop`), `deaf` (ignora `go` e `stop`), `dieongo` (sai com código 4 no `go`), além de `hang`, `crash` e `spam` da Sprint 0.

- [ ] **Step 1: Reescrever `controller/tests/fake_engine.py`**

```python
"""Engine UCI falso para testes. Modo via argv[1]:
ok | hang | crash | spam | slow (só responde ao stop) | deaf (ignora go/stop) | dieongo."""
import sys
import time

import chess

mode = sys.argv[1] if len(sys.argv) > 1 else "ok"
board = chess.Board()


def set_position(tokens: list[str]) -> None:
    global board
    if tokens[1] == "startpos":
        board, rest = chess.Board(), tokens[2:]
    else:  # position fen <6 campos> [moves ...]
        board, rest = chess.Board(" ".join(tokens[2:8])), tokens[8:]
    if rest and rest[0] == "moves":
        for uci in rest[1:]:
            board.push_uci(uci)


def answer_bestmove() -> None:
    moves = sorted(m.uci() for m in board.legal_moves)
    if not moves:
        print("bestmove (none)")
        return
    print(f"info depth 5 seldepth 7 multipv 1 score cp 12 nodes 1234 nps 1000 time 1 pv {moves[0]}")
    print(f"bestmove {moves[0]}")


for line in sys.stdin:
    cmd = line.strip()
    if mode == "crash":
        sys.exit(3)
    if mode == "spam" and cmd.startswith("go"):
        while True:
            print("info depth 1 score cp 0 pv e2e4", flush=True)
            time.sleep(0.05)
    if mode == "hang":
        continue
    if cmd == "uci":
        print("id name FakeFish 1.0")
        print("id author Youloss")
        print("option name Hash type spin default 16 min 1 max 1024")
        print("uciok")
    elif cmd == "isready":
        print("readyok")
    elif cmd.startswith("position"):
        set_position(cmd.split())
    elif cmd.startswith("go"):
        if mode == "dieongo":
            sys.exit(4)
        if mode not in ("slow", "deaf"):
            answer_bestmove()
    elif cmd == "stop" and mode == "slow":
        answer_bestmove()
    elif cmd == "quit":
        break
    sys.stdout.flush()
```

- [ ] **Step 2: Escrever os testes que falham (`controller/tests/test_search.py`)**

```python
import sys
import time
from pathlib import Path

import pytest

from controller.engine_client import (
    EngineClient, EngineCrashed, EngineTimeout, SearchInfo, parse_info,
)

FAKE = Path(__file__).with_name("fake_engine.py")
GO = "go wtime 60000 btime 60000 winc 0 binc 0"


def fake(mode: str) -> EngineClient:
    return EngineClient(sys.executable, args=[str(FAKE), mode])


def test_search_returns_bestmove_and_last_info():
    with fake("ok") as eng:
        eng.handshake(timeout=5)
        info = eng.search("position startpos", GO, timeout=5)
    assert info.bestmove == "a2a3"
    assert (info.depth, info.seldepth, info.nodes) == (5, 7, 1234)
    assert (info.score_cp, info.score_mate) == (12, None)
    assert info.pv == ["a2a3"]
    assert info.stopped is False


def test_search_applies_fen_and_moves():
    fen = "8/8/8/8/8/k7/p7/7K w - - 0 1"
    with fake("ok") as eng:
        eng.handshake(timeout=5)
        info = eng.search(f"position fen {fen} moves h1g1 a2a1q", GO, timeout=5)
    assert info.bestmove in {"g1f2", "g1g2", "g1h2"}


def test_slow_engine_gets_stop_and_answers():
    with fake("slow") as eng:
        eng.handshake(timeout=5)
        t0 = time.monotonic()
        info = eng.search("position startpos", GO, timeout=0.3)
    assert info.stopped is True
    assert info.bestmove == "a2a3"
    assert time.monotonic() - t0 < 2.0


def test_deaf_engine_times_out_after_stop_grace():
    with fake("deaf") as eng:
        eng.handshake(timeout=5)
        t0 = time.monotonic()
        with pytest.raises(EngineTimeout, match="stop"):
            eng.search("position startpos", GO, timeout=0.2, stop_grace=0.3)
    assert time.monotonic() - t0 < 2.0


def test_engine_dying_on_go_raises_crashed():
    with fake("dieongo") as eng:
        eng.handshake(timeout=5)
        with pytest.raises(EngineCrashed):
            eng.search("position startpos", GO, timeout=5)


def parsed(*lines: str) -> SearchInfo:
    info = SearchInfo(bestmove="")
    for line in lines:
        parse_info(line, info)
    return info


def test_parse_info_mate_and_pv():
    info = parsed("info depth 20 seldepth 30 multipv 1 score mate -3 nodes 99 nps 1 pv e2e4 e7e5")
    assert (info.score_cp, info.score_mate, info.pv) == (None, -3, ["e2e4", "e7e5"])


def test_parse_info_ignores_bounds_multipv_and_garbage():
    base = "info depth 10 seldepth 12 multipv 1 score cp 30 nodes 500 pv d2d4"
    info = parsed(
        base,
        "info depth 11 seldepth 13 multipv 1 score cp 90 lowerbound nodes 600 pv e2e4",
        "info depth 11 seldepth 13 multipv 2 score cp 10 nodes 600 pv c2c4",
        "info depth x score cp y pv",
        "info string NNUE evaluation using nn.nnue",
    )
    assert (info.depth, info.score_cp, info.pv) == (10, 30, ["d2d4"])
```

- [ ] **Step 3: Rodar e confirmar que falha**

Run: `$PY -m pytest controller/tests/test_search.py -q`
Expected: FAIL com `ImportError: cannot import name 'SearchInfo'`

- [ ] **Step 4: Implementar em `controller/engine_client.py`**

Nos imports do topo, trocar o bloco por:

```python
import queue
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
```

Logo após `class EngineCrashed(EngineError): pass`, adicionar:

```python
@dataclass
class SearchInfo:
    bestmove: str
    ponder: str | None = None
    depth: int = 0
    seldepth: int = 0
    nodes: int = 0
    score_cp: int | None = None
    score_mate: int | None = None
    pv: list[str] = field(default_factory=list)
    stopped: bool = False


def parse_info(line: str, into: SearchInfo) -> None:
    """Atualiza `into` com uma linha `info` completa (com score e pv).

    Ignora bounds (score provisório), multipv > 1 e linhas malformadas."""
    tok = line.split()
    if tok[:1] != ["info"] or "pv" not in tok or "score" not in tok:
        return
    if "lowerbound" in tok or "upperbound" in tok:
        return
    try:
        if "multipv" in tok and tok[tok.index("multipv") + 1] != "1":
            return
        i = tok.index("score")
        kind, value = tok[i + 1], int(tok[i + 2])
        depth = int(tok[tok.index("depth") + 1])
        seldepth = int(tok[tok.index("seldepth") + 1]) if "seldepth" in tok else 0
        nodes = int(tok[tok.index("nodes") + 1]) if "nodes" in tok else 0
    except (ValueError, IndexError):
        return
    if kind not in ("cp", "mate"):
        return
    into.depth, into.seldepth, into.nodes = depth, seldepth, nodes
    into.score_cp = value if kind == "cp" else None
    into.score_mate = value if kind == "mate" else None
    into.pv = tok[tok.index("pv") + 1:]
```

Logo após o método `set_option`, adicionar:

```python
    def search(
        self, position: str, go: str, timeout: float, stop_grace: float = 2.0
    ) -> SearchInfo:
        """Busca até `bestmove`. Estourado `timeout`, manda `stop` e espera `stop_grace`."""
        self.send(position)
        self.send(go)
        info = SearchInfo(bestmove="")
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                if info.stopped:
                    raise EngineTimeout(f"bestmove não recebido {stop_grace}s após stop")
                self.send("stop")
                info.stopped = True
                deadline = time.monotonic() + stop_grace
                continue
            try:
                line = self.read_line(remaining)
            except EngineTimeout:
                continue
            if line.startswith("info "):
                parse_info(line, info)
            elif line.startswith("bestmove"):
                parts = line.split()
                info.bestmove = parts[1] if len(parts) > 1 else "(none)"
                if len(parts) >= 4 and parts[2] == "ponder":
                    info.ponder = parts[3]
                if info.bestmove == "(none)":
                    raise EngineError("engine sem lance: bestmove (none)")
                return info
```

- [ ] **Step 5: Rodar a suíte do controller**

Run: `$PY -m pytest controller/tests -q`
Expected: todos passam (os 8 da Sprint 0 + os novos).

- [ ] **Step 6: Commit**

```bash
git add controller/engine_client.py controller/tests/fake_engine.py controller/tests/test_search.py
git commit -m "feat(controller): busca UCI com parse de info e stop de segurança"
```

---

### Task 4: Log por lance

**Files:**
- Create: `controller/game_log.py`
- Test: `controller/tests/test_game_log.py`

**Interfaces:**
- Consumes: `SearchInfo` (Task 3).
- Produces:
  - `LINE_RE: re.Pattern` (linha de lance válida)
  - `slug(text: str) -> str`, `log_path(logs_dir: Path, opponent: str, game: int, day: date) -> Path`
  - `format_eval(score_cp: int | None, score_mate: int | None) -> str`
  - `GameLog(path)` com `header(**fields)`, `note(text)`, `our_move(move_no: int, color: str, uci: str, source: str, time_ms: int, info: SearchInfo | None = None)`, `opponent_move(move_no: int, color: str, uci: str, time_ms: int)`, `result(result: str, reason: str)`, `close()`
  - `check_log(path) -> list[str]` e CLI `python -m controller.game_log <arquivo.log>...` (exit 1 se houver linha inválida)

- [ ] **Step 1: Escrever os testes que falham**

```python
from datetime import date

from controller.engine_client import SearchInfo
from controller.game_log import (
    LINE_RE, GameLog, _main, check_log, format_eval, log_path, slug,
)


def test_format_eval():
    assert format_eval(42, None) == "+0.42"
    assert format_eval(-130, None) == "-1.30"
    assert format_eval(0, None) == "+0.00"
    assert format_eval(None, 5) == "M5"
    assert format_eval(None, -3) == "-M3"
    assert format_eval(None, None) == "none"


def test_slug_and_log_path(tmp_path):
    assert slug("Équipe Xadrez 2!") == "equipe-xadrez-2"
    assert slug("***") == "adversario"
    p = log_path(tmp_path, "Time X", 3, date(2026, 10, 28))
    assert p == tmp_path / "2026-10-28_time-x_g3.log"


def test_engine_line_matches_spec(tmp_path):
    log = GameLog(tmp_path / "g.log")
    info = SearchInfo(bestmove="g1f3", depth=31, seldepth=44, nodes=182334112,
                      score_cp=42, pv=["g1f3", "d7d5"])
    log.our_move(12, "white", "g1f3", "engine", 21873, info)
    line = (tmp_path / "g.log").read_text(encoding="utf-8").splitlines()[0]
    assert line == ('move=12 color=white uci=g1f3 depth=31 seldepth=44 nodes=182334112 '
                    'eval=+0.42 pv="g1f3 d7d5" time_ms=21873 source=engine')
    assert LINE_RE.match(line)
    log.close()


def test_book_forced_and_opponent_lines(tmp_path):
    log = GameLog(tmp_path / "g.log")
    log.our_move(1, "white", "e2e4", "book", 3)
    log.our_move(2, "white", "e1f1", "forced", 1)
    log.opponent_move(1, "black", "e7e5", 5000)
    lines = (tmp_path / "g.log").read_text(encoding="utf-8").splitlines()
    assert lines[0] == 'move=1 color=white uci=e2e4 depth=0 seldepth=0 nodes=0 eval=book pv="e2e4" time_ms=3 source=book'
    assert lines[2] == "move=1 color=black uci=e7e5 time_ms=5000 source=opponent"
    assert all(LINE_RE.match(line) for line in lines)
    log.close()


def test_header_note_result_and_append(tmp_path):
    path = tmp_path / "g.log"
    log = GameLog(path)
    log.header(color="white", start_fen="rnbqkbnr/8 w - - 0 1")
    log.close()
    log = GameLog(path)  # reabrir (resume) não apaga o que já existe
    log.note("resume")
    log.result("1-0", "checkmate")
    log.close()
    assert path.read_text(encoding="utf-8").splitlines() == [
        '# color=white start_fen="rnbqkbnr/8 w - - 0 1"',
        "# resume",
        "# result=1-0 reason=checkmate",
    ]


def test_lines_visible_before_close(tmp_path):
    log = GameLog(tmp_path / "g.log")
    log.opponent_move(1, "black", "e7e5", 10)
    assert "e7e5" in (tmp_path / "g.log").read_text(encoding="utf-8")
    log.close()


def test_check_log_flags_bad_lines(tmp_path):
    path = tmp_path / "g.log"
    path.write_text("# ok\nmove=1 color=white uci=e2e4 time_ms=1 source=opponent\nlixo\n",
                    encoding="utf-8")
    assert check_log(path) == ["3: lixo"]
    assert _main([str(path)]) == 1
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `$PY -m pytest controller/tests/test_game_log.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'controller.game_log'`

- [ ] **Step 3: Implementar `controller/game_log.py`**

```python
"""Log .log por lance (FAQ item 9), com flush e fsync a cada linha."""
from __future__ import annotations

import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from controller.engine_client import SearchInfo

_UCI = r"[a-h][1-8][a-h][1-8][qrbn]?"
LINE_RE = re.compile(
    rf"^move=\d+ color=(?:white|black) uci={_UCI} (?:"
    rf"depth=\d+ seldepth=\d+ nodes=\d+ "
    rf"eval=(?:[+-]\d+\.\d{{2}}|-?M\d+|book|forced|none) "
    rf'pv="(?:{_UCI}(?: {_UCI})*)?" time_ms=\d+ source=(?:engine|book|forced|ponderhit)'
    rf"|time_ms=\d+ source=opponent)$"
)


def slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-") or "adversario"


def log_path(logs_dir: Path, opponent: str, game: int, day: date) -> Path:
    return Path(logs_dir) / f"{day.isoformat()}_{slug(opponent)}_g{game}.log"


def format_eval(score_cp: int | None, score_mate: int | None) -> str:
    if score_mate is not None:
        return f"M{score_mate}" if score_mate > 0 else f"-M{-score_mate}"
    if score_cp is None:
        return "none"
    return f"{score_cp / 100:+.2f}"


class GameLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._f = open(self.path, "a", encoding="utf-8", newline="\n")

    def _write(self, line: str) -> None:
        self._f.write(line + "\n")
        self._f.flush()
        os.fsync(self._f.fileno())

    def header(self, **fields: object) -> None:
        parts = [f'{k}="{v}"' if " " in str(v) else f"{k}={v}" for k, v in fields.items()]
        self._write("# " + " ".join(parts))

    def note(self, text: str) -> None:
        self._write(f"# {text}")

    def our_move(
        self, move_no: int, color: str, uci: str, source: str, time_ms: int,
        info: SearchInfo | None = None,
    ) -> None:
        if info is not None:
            search = (
                f"depth={info.depth} seldepth={info.seldepth} nodes={info.nodes} "
                f"eval={format_eval(info.score_cp, info.score_mate)} "
                f'pv="{" ".join(info.pv)}"'
            )
        else:
            search = f'depth=0 seldepth=0 nodes=0 eval={source} pv="{uci}"'
        self._write(
            f"move={move_no} color={color} uci={uci} {search} time_ms={time_ms} source={source}"
        )

    def opponent_move(self, move_no: int, color: str, uci: str, time_ms: int) -> None:
        self._write(f"move={move_no} color={color} uci={uci} time_ms={time_ms} source=opponent")

    def result(self, result: str, reason: str) -> None:
        self._write(f"# result={result} reason={reason}")

    def close(self) -> None:
        if not self._f.closed:
            self._f.close()


def check_log(path: str | Path) -> list[str]:
    """Linhas fora do formato (comentários `# ` são aceitos)."""
    bad = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not (line.startswith("# ") or LINE_RE.match(line)):
            bad.append(f"{n}: {line}")
    return bad


def _main(argv: list[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else argv
    failed = False
    for path in paths:
        for bad in check_log(path):
            print(f"{path}:{bad}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_main())
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `$PY -m pytest controller/tests/test_game_log.py -q`
Expected: todos passam.

- [ ] **Step 5: Commit**

```bash
git add controller/game_log.py controller/tests/test_game_log.py
git commit -m "feat(controller): log por lance no formato do spec e validador"
```

---

### Task 5: Estado da partida (save atômico, load, resume)

**Files:**
- Create: `controller/state.py`
- Test: `controller/tests/test_state.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `class StateError(Exception)`, `STATE_VERSION = 1`
  - `@dataclass GameState(color: str, opponent: str, game: int, base_ms: int, inc_ms: int, start_fen: str = chess.STARTING_FEN, moves: list[str] = [], white_ms: int = 0, black_ms: int = 0, log_path: str = "", result: str | None = None, reason: str | None = None)` com `finished` (property), `us() -> chess.Color`, `board() -> chess.Board`
  - `save_state(state, path) -> None`, `load_state(path) -> GameState`, `state_path_for(log_path) -> Path`, `latest_unfinished(logs_dir) -> Path | None`

- [ ] **Step 1: Escrever os testes que falham**

```python
import json
import os

import chess
import pytest

from controller.state import (
    GameState, StateError, latest_unfinished, load_state, save_state, state_path_for,
)


def sample(**kw) -> GameState:
    base = dict(color="white", opponent="x", game=1, base_ms=900_000, inc_ms=10_000,
                moves=["e2e4", "e7e5"], white_ms=880_000, black_ms=870_000, log_path="l.log")
    base.update(kw)
    return GameState(**base)


def test_roundtrip(tmp_path):
    path = tmp_path / "g.state.json"
    save_state(sample(), path)
    assert load_state(path) == sample()
    assert not list(tmp_path.glob("*.tmp"))


def test_board_replays_moves():
    board = sample().board()
    assert board.fullmove_number == 2 and board.turn == chess.WHITE
    assert sample().us() == chess.WHITE and sample(color="black").us() == chess.BLACK


def test_finished():
    assert not sample().finished
    assert sample(result="1-0", reason="checkmate").finished


def test_state_path_for(tmp_path):
    assert state_path_for(tmp_path / "2026-10-28_x_g1.log") == tmp_path / "2026-10-28_x_g1.state.json"


@pytest.mark.parametrize("content, match", [
    ("{meio escrito", "corrompido"),
    (json.dumps({"version": 99}), "versão"),
    (json.dumps({"version": 1, "color": "white"}), "campos"),
])
def test_bad_files_raise_state_error(tmp_path, content, match):
    path = tmp_path / "g.state.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(StateError, match=match):
        load_state(path)


def test_illegal_moves_raise_state_error(tmp_path):
    path = tmp_path / "g.state.json"
    save_state(sample(moves=["e2e5"]), path)
    with pytest.raises(StateError, match="lances"):
        load_state(path)


def test_missing_raises_state_error(tmp_path):
    with pytest.raises(StateError, match="não encontrado"):
        load_state(tmp_path / "nada.state.json")


def test_latest_unfinished(tmp_path):
    old, done, new = (tmp_path / f"{n}.state.json" for n in ("old", "done", "new"))
    save_state(sample(game=1), old)
    save_state(sample(game=2, result="1-0", reason="resign_opponent"), done)
    save_state(sample(game=3), new)
    (tmp_path / "bad.state.json").write_text("{", encoding="utf-8")
    os.utime(old, (1000, 1000))
    os.utime(new, (2000, 2000))
    os.utime(done, (3000, 3000))
    assert latest_unfinished(tmp_path) == new
    assert latest_unfinished(tmp_path / "vazio") is None
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `$PY -m pytest controller/tests/test_state.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'controller.state'`

- [ ] **Step 3: Implementar `controller/state.py`**

```python
"""Estado da partida em JSON, gravado a cada lance para `start --resume`."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

import chess

STATE_VERSION = 1


class StateError(Exception):
    pass


@dataclass
class GameState:
    color: str  # nosso lado: "white" | "black"
    opponent: str
    game: int
    base_ms: int
    inc_ms: int
    start_fen: str = chess.STARTING_FEN
    moves: list[str] = field(default_factory=list)
    white_ms: int = 0
    black_ms: int = 0
    log_path: str = ""
    result: str | None = None  # "1-0" | "0-1" | "1/2-1/2"
    reason: str | None = None

    @property
    def finished(self) -> bool:
        return self.result is not None

    def us(self) -> chess.Color:
        return self.color == "white"

    def board(self) -> chess.Board:
        board = chess.Board(self.start_fen)
        for uci in self.moves:
            board.push_uci(uci)
        return board


def save_state(state: GameState, path: str | Path) -> None:
    # Grava em .tmp e troca com os.replace: um crash nunca deixa o JSON pela metade.
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"version": STATE_VERSION, **asdict(state)}, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_state(path: str | Path) -> GameState:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StateError(f"estado não encontrado: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"estado corrompido: {path}: {exc}") from exc
    if not isinstance(data, dict) or data.pop("version", None) != STATE_VERSION:
        raise StateError(f"versão de estado não suportada: {path}")
    try:
        state = GameState(**data)
    except TypeError as exc:
        raise StateError(f"estado com campos inválidos: {path}: {exc}") from exc
    try:
        state.board()
    except ValueError as exc:
        raise StateError(f"estado com lances ou FEN inválidos: {path}: {exc}") from exc
    return state


def state_path_for(log_path: str | Path) -> Path:
    return Path(log_path).with_suffix(".state.json")


def latest_unfinished(logs_dir: str | Path) -> Path | None:
    paths = sorted(
        Path(logs_dir).glob("*.state.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    for path in paths:
        try:
            if not load_state(path).finished:
                return path
        except StateError:
            continue
    return None
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `$PY -m pytest controller/tests/test_state.py -q`
Expected: todos passam.

- [ ] **Step 5: Commit**

```bash
git add controller/state.py controller/tests/test_state.py
git commit -m "feat(controller): estado da partida com gravação atômica e resume"
```

---

### Task 6: Opções de runtime + Syzygy 3-4-5

**Files:**
- Create: `controller/runtime.py`, `scripts/fetch_syzygy.sh`, `scripts/verify_assets.sh`
- Test: `controller/tests/test_runtime.py`

**Interfaces:**
- Consumes: `EngineClient` (Sprint 0) nos testes com engine real.
- Produces:
  - `MOVE_OVERHEAD_MS = 1500`, `HASH_CAP_MB = 16384`, `SYZYGY_PROBE_LIMIT = 5`
  - `free_memory_mb() -> int`, `has_syzygy(path: Path) -> bool`
  - `runtime_options(syzygy_dir: Path, threads: int | None = None, hash_mb: int | None = None, cpus: int | None = None, free_mb: int | None = None) -> dict[str, int | str]`. Chaves: `Threads`, `Hash`, `Move Overhead` e `SyzygyProbeLimit`, mais `SyzygyPath` só se houver `*.rtbw` no diretório.

- [ ] **Step 1: Escrever os testes que falham**

```python
from pathlib import Path

import pytest

from controller.engine_client import EngineClient
from controller.runtime import free_memory_mb, has_syzygy, runtime_options

ROOT = Path(__file__).resolve().parents[2]
REAL = ROOT / "bin" / "youloss.exe"
SYZYGY = ROOT / "assets" / "syzygy"


def test_defaults_from_machine(tmp_path):
    opts = runtime_options(tmp_path, cpus=8, free_mb=10_000)
    assert opts == {"Threads": 7, "Hash": 5_000, "Move Overhead": 1500, "SyzygyProbeLimit": 5}


def test_limits(tmp_path):
    assert runtime_options(tmp_path, cpus=1, free_mb=10)["Threads"] == 1
    assert runtime_options(tmp_path, cpus=1, free_mb=10)["Hash"] == 16
    assert runtime_options(tmp_path, cpus=4, free_mb=64_000)["Hash"] == 16_384


def test_overrides(tmp_path):
    opts = runtime_options(tmp_path, threads=1, hash_mb=16, cpus=8, free_mb=10_000)
    assert (opts["Threads"], opts["Hash"]) == (1, 16)


def test_syzygy_path_only_when_tables_exist(tmp_path):
    assert "SyzygyPath" not in runtime_options(tmp_path / "nao_existe", cpus=2, free_mb=64)
    (tmp_path / "KQvK.rtbw").touch()
    assert has_syzygy(tmp_path)
    assert runtime_options(tmp_path, cpus=2, free_mb=64)["SyzygyPath"] == str(tmp_path.resolve())


def test_free_memory_is_positive():
    assert free_memory_mb() > 0


@pytest.mark.skipif(not REAL.exists(), reason="engine não compilado")
def test_real_engine_accepts_every_option(tmp_path):
    with EngineClient(REAL) as eng:
        eng.handshake(timeout=10)
        for name, value in runtime_options(tmp_path, cpus=2, free_mb=64).items():
            eng.set_option(name, value)
        eng.send("isready")
        lines = eng.read_until("readyok", timeout=10)
    assert not [line for line in lines if "No such option" in line]


@pytest.mark.skipif(not (REAL.exists() and has_syzygy(SYZYGY)), reason="sem engine ou Syzygy")
def test_real_engine_probes_syzygy():
    with EngineClient(REAL) as eng:
        eng.handshake(timeout=10)
        for name, value in runtime_options(SYZYGY, threads=1, hash_mb=16).items():
            eng.set_option(name, value)
        eng.is_ready(timeout=30)
        eng.send("position fen 8/8/8/8/8/2k5/8/KQ6 w - - 0 1")
        eng.send("go depth 10")
        lines = eng.read_until("bestmove", timeout=30)
    hits = [int(t[t.index("tbhits") + 1]) for t in (l.split() for l in lines) if "tbhits" in t]
    assert hits and max(hits) > 0
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `$PY -m pytest controller/tests/test_runtime.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'controller.runtime'`

- [ ] **Step 3: Implementar `controller/runtime.py`**

```python
"""Opções UCI de runtime do engine (spec seção 6)."""
from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

MOVE_OVERHEAD_MS = 1500
HASH_CAP_MB = 16 * 1024
SYZYGY_PROBE_LIMIT = 5  # FAQ item 4: no máximo 5 peças


def free_memory_mb() -> int:
    if sys.platform != "win32":
        return os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") // 2**20

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx falhou")
    return status.ullAvailPhys // 2**20


def has_syzygy(path: Path) -> bool:
    return path.is_dir() and any(path.glob("*.rtbw"))


def runtime_options(
    syzygy_dir: Path,
    threads: int | None = None,
    hash_mb: int | None = None,
    cpus: int | None = None,
    free_mb: int | None = None,
) -> dict[str, int | str]:
    if threads is None:
        threads = max(1, (cpus if cpus is not None else os.cpu_count() or 2) - 1)
    if hash_mb is None:
        free = free_mb if free_mb is not None else free_memory_mb()
        hash_mb = max(16, min(HASH_CAP_MB, free // 2))
    opts: dict[str, int | str] = {
        "Threads": threads,
        "Hash": hash_mb,
        "Move Overhead": MOVE_OVERHEAD_MS,
        "SyzygyProbeLimit": SYZYGY_PROBE_LIMIT,
    }
    if has_syzygy(Path(syzygy_dir)):
        opts["SyzygyPath"] = str(Path(syzygy_dir).resolve())
    return opts
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `$PY -m pytest controller/tests/test_runtime.py -q`
Expected: todos passam; `test_real_engine_probes_syzygy` aparece como `skipped` (as Syzygy ainda não foram baixadas).

- [ ] **Step 5: Escrever `scripts/fetch_syzygy.sh`**

```bash
#!/usr/bin/env bash
# Baixa as Syzygy 3-4-5 (WDL+DTZ) para assets/syzygy e registra sha256 em assets/MANIFEST.
# Rodar do root do repo, com rede, ANTES do evento (FAQ itens 4 e 14). ~1 GB.
set -euo pipefail
BASE="https://tablebase.lichess.ovh/tables/standard/3-4-5"
DEST="assets/syzygy"
mkdir -p "$DEST"
files=$(curl -fsSL "$BASE/" | grep -oE 'href="[KQRBNP]+v[KQRBNP]+\.rtb[wz]"' \
  | sed -e 's/^href="//' -e 's/"$//' | sort -u)
[ -n "$files" ] || { echo "nenhuma tabela listada em $BASE/" >&2; exit 1; }
for f in $files; do
  if [ ! -s "$DEST/$f" ]; then
    curl -fsSL --retry 3 -o "$DEST/$f.part" "$BASE/$f"
    mv "$DEST/$f.part" "$DEST/$f"
  fi
done
wdl=$(ls "$DEST"/*.rtbw | wc -l)
dtz=$(ls "$DEST"/*.rtbz | wc -l)
[ "$wdl" -eq "$dtz" ] || { echo "WDL ($wdl) e DTZ ($dtz) não batem" >&2; exit 1; }
touch assets/MANIFEST
grep -v ' syzygy/' assets/MANIFEST > assets/MANIFEST.tmp || true
(cd assets && sha256sum syzygy/*.rtbw syzygy/*.rtbz) >> assets/MANIFEST.tmp
mv assets/MANIFEST.tmp assets/MANIFEST
echo "OK: $wdl WDL + $dtz DTZ em $DEST"
```

- [ ] **Step 6: Escrever `scripts/verify_assets.sh`**

```bash
#!/usr/bin/env bash
# Confere os assets contra assets/MANIFEST (offline). Rodar do root do repo.
set -euo pipefail
[ -s assets/MANIFEST ] || { echo "assets/MANIFEST ausente ou vazio" >&2; exit 1; }
(cd assets && sha256sum --check --quiet MANIFEST)
echo "OK: $(wc -l < assets/MANIFEST) arquivos conferem com assets/MANIFEST"
```

- [ ] **Step 7: Baixar, verificar e rodar o teste real de Syzygy**

Run:
```bash
bash scripts/fetch_syzygy.sh
bash scripts/verify_assets.sh
$PY -m pytest controller/tests/test_runtime.py -q
```
Expected: `OK: N WDL + N DTZ` com o mesmo N nos dois; `verify_assets` sai com 0; o teste `test_real_engine_probes_syzygy` passa, sem `skipped`. Se o `curl` da listagem não achar arquivos, abrir `$BASE/` no navegador e ajustar o padrão do `grep`.

- [ ] **Step 8: Commit** (os assets ficam fora do git; só entram o MANIFEST e os scripts)

```bash
git add controller/runtime.py controller/tests/test_runtime.py scripts/fetch_syzygy.sh scripts/verify_assets.sh assets/MANIFEST
git commit -m "feat(controller): opções de runtime e Syzygy 3-4-5 com MANIFEST"
```

---

### Task 7: Loop da partida (nosso lance, lance do adversário, fim)

**Files:**
- Create: `controller/game.py`, `controller/tests/scripted.py`, `controller/tests/conftest.py`
- Test: `controller/tests/test_game.py`

**Interfaces:**
- Consumes: `GameClock` (T1), `OpeningBook` (T2), `EngineClient.search`/`SearchInfo`/`EngineError` (T3), `GameLog` (T4), `GameState`/`save_state` (T5).
- Produces:
  - `Game(state: GameState, state_path: Path, engine: EngineClient, book: OpeningBook, log: GameLog, clock: GameClock, input_fn=input, output_fn=print, paused: bool = False, safety_margin_s: float = 2.0)` com `run() -> str | None` (resultado, ou `None` se interrompida por `quit`/EOF), `board: chess.Board`, `paused: bool` e o dicionário `_commands: dict[str, Callable[[str], None]]`, que a Task 8 estende.
  - `Game._finish(result: str, reason: str) -> None`, `Game._save() -> None` (usados na Task 8)
  - `color_name(color) -> str`
  - Teste: `scripted.Script(answers)`, `scripted.fake_engine(mode) -> EngineClient`, `scripted.FAKE`, `scripted.REAL`; fixture `games(tmp_path, answers, color="white", fen=..., mode="ok", book=None, base_ms=60_000, paused=False, safety=2.0) -> (Game, list[str])`

- [ ] **Step 1: Criar `controller/tests/scripted.py`**

```python
"""Helpers de teste: entrada roteirizada do operador e engine falso."""
from __future__ import annotations

import sys
from pathlib import Path

from controller.engine_client import EngineClient

FAKE = Path(__file__).with_name("fake_engine.py")
REAL = Path(__file__).resolve().parents[2] / "bin" / "youloss.exe"


def fake_engine(mode: str = "ok") -> EngineClient:
    return EngineClient(sys.executable, args=[str(FAKE), mode])


class Script:
    """input_fn roteirizado: devolve as respostas em ordem; esgotadas → EOFError (quit)."""

    def __init__(self, answers: list[str]):
        self.answers = list(answers)
        self.prompts: list[str] = []

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self.answers:
            raise EOFError
        return self.answers.pop(0)
```

- [ ] **Step 2: Criar `controller/tests/conftest.py`**

```python
import chess
import pytest

from controller.book import OpeningBook
from controller.clock import GameClock
from controller.game import Game
from controller.game_log import GameLog
from controller.state import GameState
from controller.tests.scripted import Script, fake_engine


@pytest.fixture
def games():
    made = []

    def factory(tmp_path, answers, color="white", fen=chess.STARTING_FEN, mode="ok",
                book=None, base_ms=60_000, paused=False, safety=2.0):
        state = GameState(color=color, opponent="teste", game=1, base_ms=base_ms,
                          inc_ms=100, start_fen=fen, white_ms=base_ms, black_ms=base_ms,
                          log_path=str(tmp_path / "g.log"))
        engine = fake_engine(mode)
        engine.start()
        engine.handshake(timeout=5)
        log = GameLog(tmp_path / "g.log")
        out: list[str] = []
        game = Game(state, tmp_path / "g.state.json", engine, OpeningBook(book), log,
                    GameClock(base_ms, 100), input_fn=Script(answers),
                    output_fn=out.append, paused=paused, safety_margin_s=safety)
        made.append((engine, log))
        return game, out

    yield factory
    for engine, log in made:
        engine.quit()
        log.close()
```

- [ ] **Step 3: Escrever os testes que falham (`controller/tests/test_game.py`)**

```python
import chess
import pytest

from controller.engine_client import EngineCrashed
from controller.game_log import LINE_RE
from controller.state import load_state
from controller.tests.polyglot import write_book


def log_lines(tmp_path) -> list[str]:
    return (tmp_path / "g.log").read_text(encoding="utf-8").splitlines()


def moves_in_log(tmp_path) -> list[str]:
    return [l for l in log_lines(tmp_path) if l.startswith("move=")]


def test_engine_and_opponent_moves_logged_and_saved(tmp_path, games):
    game, out = games(tmp_path, ["e7e5"])
    assert game.run() is None  # EOF depois do e7e5 → quit
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]
    lines = moves_in_log(tmp_path)
    assert len(lines) == 3 and all(LINE_RE.match(l) for l in lines)
    assert "source=engine" in lines[0] and "eval=+0.12" in lines[0]
    assert lines[1].startswith("move=1 color=black uci=e7e5 ")
    assert load_state(tmp_path / "g.state.json").moves == game.state.moves
    assert any("NOSSO LANCE: a2a3" in o for o in out)


def test_bad_input_reprompts_without_advancing(tmp_path, games):
    game, out = games(tmp_path, ["e2e4", "xyz", "", "  E7E5  "])
    game.run()
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]
    text = "\n".join(out)
    assert "lance ilegal: e2e4" in text
    assert "entrada inválida" in text


def test_promotion_without_piece_gets_hint(tmp_path, games):
    game, out = games(tmp_path, ["a2a1", "a2a1q"], fen="8/8/8/8/8/k7/p7/7K w - - 0 1")
    game.run()
    assert game.state.moves[:2] == ["h1g1", "a2a1q"]
    assert any("promoção" in o for o in out)


def test_forced_move_skips_engine(tmp_path, games):
    # Só Kxb2 é legal; o engine "deaf" estouraria o teste se fosse chamado.
    game, _ = games(tmp_path, [], fen="k7/8/8/8/8/8/1r6/K7 w - - 0 1", mode="deaf")
    assert game.run() == "1/2-1/2"  # K x K: material insuficiente
    lines = log_lines(tmp_path)
    assert "source=forced" in lines[0] and "eval=forced" in lines[0]
    assert lines[-1] == "# result=1/2-1/2 reason=insufficient_material"


def test_book_move_used(tmp_path, games):
    path = tmp_path / "b.bin"
    write_book(path, [(chess.Board(), "e2e4", 1)])
    game, _ = games(tmp_path, [], book=path, mode="deaf")
    game.run()
    assert game.state.moves == ["e2e4"]
    assert "source=book" in moves_in_log(tmp_path)[0]


def test_opponent_checkmate_ends_game(tmp_path, games):
    game, out = games(tmp_path, ["a1a8"], color="black",
                      fen="6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1")
    assert game.run() == "1-0"
    state = load_state(tmp_path / "g.state.json")
    assert (state.result, state.reason) == ("1-0", "checkmate")
    assert log_lines(tmp_path)[-1] == "# result=1-0 reason=checkmate"


def test_slow_engine_is_stopped(tmp_path, games):
    game, out = games(tmp_path, [], mode="slow", base_ms=400, safety=0.2)
    game.run()
    assert game.state.moves == ["a2a3"]
    assert any("stop enviado" in o for o in out)


def test_go_never_sends_non_positive_time(tmp_path, games):
    game, _ = games(tmp_path, [])
    game.clock.start(chess.WHITE)
    game.clock.set(chess.WHITE, -500)
    sent = []
    real_search = game.engine.search

    def spy(position, go, timeout):
        sent.append((go, timeout))
        return real_search(position, go, timeout)

    game.engine.search = spy
    game.run()
    go, timeout = sent[0]
    assert go.startswith("go wtime 1 btime 60000 winc 100 binc 100")
    assert timeout > 0


def test_engine_crash_propagates(tmp_path, games):
    game, _ = games(tmp_path, [], mode="dieongo")
    with pytest.raises(EngineCrashed):
        game.run()
```

- [ ] **Step 4: Rodar e confirmar que falha**

Run: `$PY -m pytest controller/tests/test_game.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'controller.game'`

- [ ] **Step 5: Implementar `controller/game.py`**

```python
"""Loop da partida: nosso lance (forçado/book/engine), lance do adversário e comandos."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import chess

from controller.book import OpeningBook
from controller.clock import GameClock
from controller.engine_client import EngineClient, EngineError, SearchInfo
from controller.game_log import GameLog
from controller.state import GameState, save_state

# Teto de pensamento do spec (maximum <= 0.25 * restante); além disso o controller manda stop.
MAX_THINK_FRACTION = 0.25


def color_name(color: chess.Color) -> str:
    return "white" if color == chess.WHITE else "black"


class Game:
    def __init__(
        self,
        state: GameState,
        state_path: Path,
        engine: EngineClient,
        book: OpeningBook,
        log: GameLog,
        clock: GameClock,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
        paused: bool = False,
        safety_margin_s: float = 2.0,
    ):
        self.state = state
        self.state_path = Path(state_path)
        self.engine = engine
        self.book = book
        self.log = log
        self.clock = clock
        self.input_fn = input_fn
        self.out = output_fn
        self.paused = paused
        self.safety_margin_s = safety_margin_s
        self.board = state.board()
        self.us = state.us()
        self.running = True
        self._commands: dict[str, Callable[[str], None]] = {"quit": self._cmd_quit}

    def run(self) -> str | None:
        """Joga até o fim da partida ou `quit`. Retorna o resultado, ou None se interrompida."""
        if self.clock.running is None:
            self.clock.start(self.board.turn)
        while self.running:
            outcome = self.board.outcome()
            if outcome is not None:
                self._finish(outcome.result(), outcome.termination.name.lower())
                break
            if self.board.turn == self.us and not self.paused:
                self._play_our_move()
            else:
                self._prompt()
        return self.state.result

    # --- nosso lance -------------------------------------------------------

    def _play_our_move(self) -> None:
        legal = list(self.board.legal_moves)
        info: SearchInfo | None = None
        book_move = self.book.pick(self.board)
        if len(legal) == 1:
            move, source = legal[0], "forced"
        elif book_move is not None and book_move in legal:
            move, source = book_move, "book"
        else:
            info = self._search()
            try:
                move = chess.Move.from_uci(info.bestmove)
            except ValueError as exc:
                raise EngineError(f"bestmove malformado: {info.bestmove!r}") from exc
            if move not in legal:
                raise EngineError(f"engine devolveu lance ilegal: {info.bestmove}")
            source = "engine"
        move_no, color = self.board.fullmove_number, self.board.turn
        spent = self.clock.press()
        self._push(move)
        self.out(f"\n>>> NOSSO LANCE: {move.uci()}   ({source}, {spent / 1000:.1f}s)\n")
        self.log.our_move(move_no, color_name(color), move.uci(), source, spent, info)

    def _search(self) -> SearchInfo:
        white = self.clock.remaining(chess.WHITE)
        black = self.clock.remaining(chess.BLACK)
        inc = self.clock.inc_ms
        ours = white if self.us == chess.WHITE else black
        timeout = max(ours, 0) * MAX_THINK_FRACTION / 1000 + self.safety_margin_s
        position = f"position fen {self.state.start_fen}"
        if self.state.moves:
            position += " moves " + " ".join(self.state.moves)
        go = f"go wtime {max(white, 1)} btime {max(black, 1)} winc {inc} binc {inc}"
        info = self.engine.search(position, go, timeout)
        if info.stopped:
            self.out(f"AVISO: engine passou de {timeout:.1f}s; stop enviado")
        return info

    # --- vez do adversário / comandos -------------------------------------

    def _prompt(self) -> None:
        if self.board.turn == self.us:
            who = "NÓS (pausado: 'go' para jogar)"
        else:
            who = "adversário"
        dots = "." if self.board.turn == chess.WHITE else "..."
        try:
            line = self.input_fn(f"[{self.board.fullmove_number}{dots}] vez: {who} > ")
        except EOFError:
            line = "quit"
        text = line.strip()
        if not text:
            return
        cmd, _, arg = text.partition(" ")
        handler = self._commands.get(cmd.lower())
        if handler is not None:
            handler(arg.strip())
        else:
            self._opponent_move(text)

    def _opponent_move(self, text: str) -> None:
        if self.board.turn == self.us:
            self.out("é a nossa vez: use 'go' para o engine jogar")
            return
        uci = text.lower()
        try:
            move = chess.Move.from_uci(uci)
        except ValueError:
            self.out(f"entrada inválida: {text!r} (lance UCI como e2e4 ou e7e8q, ou 'help')")
            return
        if move not in self.board.legal_moves:
            promo = chess.Move(move.from_square, move.to_square, chess.QUEEN)
            hint = ""
            if move.promotion is None and promo in self.board.legal_moves:
                hint = " (promoção? informe a peça, ex. e7e8q)"
            self.out(f"lance ilegal: {uci}{hint}")
            return
        move_no, color = self.board.fullmove_number, self.board.turn
        spent = self.clock.press()
        self._push(move)
        self.paused = False
        self.log.opponent_move(move_no, color_name(color), move.uci(), spent)

    def _cmd_quit(self, arg: str) -> None:
        self._save()
        self.out(f"partida interrompida; estado em {self.state_path}. "
                 "Retome com: python -m controller.main start --resume")
        self.running = False

    # --- estado ------------------------------------------------------------

    def _push(self, move: chess.Move) -> None:
        self.board.push(move)
        self.state.moves.append(move.uci())
        self._save()

    def _save(self) -> None:
        self.state.white_ms = self.clock.remaining(chess.WHITE)
        self.state.black_ms = self.clock.remaining(chess.BLACK)
        save_state(self.state, self.state_path)

    def _finish(self, result: str, reason: str) -> None:
        self.state.result, self.state.reason = result, reason
        self._save()
        self.log.result(result, reason)
        self.out(f"FIM DE PARTIDA: {result} ({reason})")
        self.running = False
```

- [ ] **Step 6: Rodar e confirmar que passa**

Run: `$PY -m pytest controller/tests -q`
Expected: todos passam.

- [ ] **Step 7: Commit**

```bash
git add controller/game.py controller/tests/scripted.py controller/tests/conftest.py controller/tests/test_game.py
git commit -m "feat(controller): loop da partida com book, lance forçado e engine"
```

---

### Task 8: Comandos do operador

**Files:**
- Modify: `controller/game.py` (imports; registro em `_commands` no `__init__`; novos métodos após `_cmd_quit`)
- Test: `controller/tests/test_commands.py`

**Interfaces:**
- Consumes: `Game`, `_commands`, `_finish`, `_save`, `paused`, `board` (T7); `parse_mmss`, `format_mmss`, `ClockFormatError` (T1).
- Produces: comandos `undo`, `fen <FEN>`, `clock <nosso mm:ss> <adv mm:ss>`, `board`, `go`, `resign nos|adv`, `draw`, `help`, além de `quit`. Método público `Game.show_board(arg: str = "") -> None` (usado na Task 9 ao retomar).

- [ ] **Step 1: Escrever os testes que falham**

```python
import chess

from controller.state import load_state

BLACK_TO_MOVE = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"


def test_undo_twice_then_new_opponent_move(tmp_path, games):
    # a2a3 (nós), e7e5, a1a2 (nós) → undo, undo → d7d5 → engine joga de novo
    game, out = games(tmp_path, ["e7e5", "undo", "undo", "d7d5"])
    game.run()
    assert game.state.moves[:2] == ["a2a3", "d7d5"] and len(game.state.moves) == 3
    assert any(l.startswith("# undo") for l in
               (tmp_path / "g.log").read_text(encoding="utf-8").splitlines())


def test_undo_pauses_on_our_turn_and_rejects_moves(tmp_path, games):
    game, out = games(tmp_path, ["e7e5", "undo", "h2h3", "go"])
    game.run()
    assert any("nossa vez" in o for o in out)
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]


def test_undo_with_nothing(tmp_path, games):
    game, out = games(tmp_path, ["undo"], color="black")
    game.run()
    assert any("nada a desfazer" in o for o in out)


def test_fen_resync_pauses_then_go(tmp_path, games):
    game, _ = games(tmp_path, [f"fen {BLACK_TO_MOVE}", "go"], color="black")
    game.run()
    state = load_state(tmp_path / "g.state.json")
    assert state.start_fen == BLACK_TO_MOVE and len(state.moves) == 1


def test_invalid_fen_rejected(tmp_path, games):
    game, out = games(tmp_path, ["fen lixo", "fen 8/8/8/8/8/8/8/8 w - - 0 1"], color="black")
    game.run()
    assert sum("FEN inválida" in o for o in out) == 2
    assert game.state.start_fen == chess.STARTING_FEN


def test_clock_sync(tmp_path, games):
    game, out = games(tmp_path, ["clock 10:00 12:30", "clock 10 12"], color="black")
    game.run()
    assert abs(game.clock.remaining(chess.BLACK) - 600_000) < 500
    assert abs(game.clock.remaining(chess.WHITE) - 750_000) < 500
    assert any("mm:ss" in o for o in out)


def test_board_shows_fen(tmp_path, games):
    game, out = games(tmp_path, ["board"], color="black")
    game.run()
    assert any(chess.STARTING_FEN in o for o in out)


def test_go_on_opponent_turn_is_rejected(tmp_path, games):
    game, out = games(tmp_path, ["go"], color="black")
    game.run()
    assert any("vez do adversário" in o for o in out)


def test_resign_and_draw(tmp_path, games):
    for answers, color, expected in [
        (["resign nos"], "black", ("1-0", "resign_us")),
        (["resign adv"], "black", ("0-1", "resign_opponent")),
        (["resign"], "black", (None, None)),
        (["draw"], "black", ("1/2-1/2", "draw_agreed")),
    ]:
        sub = tmp_path / f"{answers[0].replace(' ', '_')}"
        sub.mkdir()
        game, _ = games(sub, answers, color=color)
        game.run()
        assert (game.state.result, game.state.reason) == expected


def test_help_lists_commands(tmp_path, games):
    game, out = games(tmp_path, ["help"], color="black")
    game.run()
    assert any("undo" in o and "clock" in o for o in out)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `$PY -m pytest controller/tests/test_commands.py -q`
Expected: FAIL (`nada a desfazer` não encontrado; `resign`/`draw` não tratados).

- [ ] **Step 3: Implementar em `controller/game.py`**

Trocar o import do relógio por:

```python
from controller.clock import ClockFormatError, GameClock, format_mmss, parse_mmss
```

Adicionar após as imports:

```python
HELP = """comandos:
  <uci>                     lance do adversário (ex. e2e4, e7e8q)
  undo                      desfaz o último meio-lance (pausa se virar nossa vez)
  fen <FEN>                 ressincroniza com o tabuleiro físico (pausa se for nossa vez)
  clock <nós mm:ss> <adv mm:ss>   sincroniza com o relógio físico
  board                     tabuleiro, FEN e relógios
  go                        retoma: engine joga (quando pausado na nossa vez)
  resign nos|adv            registra abandono (nosso ou do adversário)
  draw                      registra empate acordado
  quit                      sai sem resultado (retomar com start --resume)"""
```

No `__init__`, trocar a linha de `self._commands` por:

```python
        self._commands: dict[str, Callable[[str], None]] = {
            "quit": self._cmd_quit,
            "undo": self._cmd_undo,
            "fen": self._cmd_fen,
            "clock": self._cmd_clock,
            "board": self.show_board,
            "go": self._cmd_go,
            "resign": self._cmd_resign,
            "draw": self._cmd_draw,
            "help": lambda arg: self.out(HELP),
        }
```

Após `_cmd_quit`, adicionar:

```python
    def _cmd_undo(self, arg: str) -> None:
        if not self.state.moves:
            self.out("nada a desfazer")
            return
        undone = self.state.moves.pop()
        self.board = self.state.board()
        self.clock.start(self.board.turn)
        self.paused = True
        self._save()
        self.log.note(f"undo {undone}")
        self.show_board()

    def _cmd_fen(self, arg: str) -> None:
        try:
            board = chess.Board(arg)
        except ValueError as exc:
            self.out(f"FEN inválida: {exc}")
            return
        if not board.is_valid():
            self.out(f"FEN inválida: {board.status()!r}")
            return
        self.board = board
        self.state.start_fen, self.state.moves = board.fen(), []
        self.clock.start(board.turn)
        self.paused = True
        self._save()
        self.log.note(f'fen "{board.fen()}"')
        self.show_board()

    def _cmd_clock(self, arg: str) -> None:
        parts = arg.split()
        if len(parts) != 2:
            self.out("uso: clock <nosso mm:ss> <adv mm:ss>")
            return
        try:
            ours, theirs = parse_mmss(parts[0]), parse_mmss(parts[1])
        except ClockFormatError as exc:
            self.out(str(exc))
            return
        self.clock.set(self.us, ours)
        self.clock.set(not self.us, theirs)
        self._save()
        self.log.note(f"clock nos={parts[0]} adv={parts[1]}")
        self.out(self._clock_line())

    def _cmd_go(self, arg: str) -> None:
        if self.board.turn != self.us:
            self.out("vez do adversário: digite o lance dele")
            return
        self.paused = False

    def _cmd_resign(self, arg: str) -> None:
        who = arg.lower().replace("ó", "o")
        if who not in ("nos", "adv"):
            self.out("uso: resign nos|adv")
            return
        loser = self.us if who == "nos" else (not self.us)
        result = "0-1" if loser == chess.WHITE else "1-0"
        self._finish(result, "resign_us" if who == "nos" else "resign_opponent")

    def _cmd_draw(self, arg: str) -> None:
        self._finish("1/2-1/2", "draw_agreed")

    def show_board(self, arg: str = "") -> None:
        self.out(f"{self.board}\nFEN: {self.board.fen()}\n{self._clock_line()}")

    def _clock_line(self) -> str:
        ours = format_mmss(self.clock.remaining(self.us))
        theirs = format_mmss(self.clock.remaining(not self.us))
        return f"relógio: nós {ours} | adv {theirs}"
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `$PY -m pytest controller/tests -q`
Expected: todos passam.

- [ ] **Step 5: Commit**

```bash
git add controller/game.py controller/tests/test_commands.py
git commit -m "feat(controller): comandos do operador (undo, fen, clock, board, go, resign, draw)"
```

---

### Task 9: CLI `start` / `--resume` e partida completa com o engine real

**Files:**
- Create: `controller/main.py`
- Modify: `README.md` (nova seção "Operação" antes de "Licença")
- Test: `controller/tests/test_main.py`

**Interfaces:**
- Consumes: tudo das Tasks 1–8 (`parse_tc`, `GameClock`, `OpeningBook`/`BookError`, `EngineClient`/`EngineError`, `GameLog`/`log_path`/`check_log`, `GameState`/`save_state`/`load_state`/`state_path_for`/`latest_unfinished`/`StateError`, `runtime_options`, `Game`/`show_board`).
- Produces:
  - `main(argv: list[str] | None = None, input_fn=input, output_fn=print, engine_factory: Callable[[Path], EngineClient] = EngineClient) -> int`. Retorna 0 (ok), 2 (erro de uso/estado/book/engine) ou 130 (Ctrl+C).
  - `open_engine(engine: EngineClient, options: dict) -> str` (nome do engine)
  - CLI: `python -m controller.main start --color white|black [--tc 900+10] [--opponent NOME] [--game N] [--engine PATH] [--book PATH | --no-book] [--syzygy DIR] [--logs DIR] [--threads N] [--hash MB]` e `start --resume [STATE]`

- [ ] **Step 1: Escrever os testes que falham**

```python
import pytest

from controller.game_log import check_log
from controller.main import main
from controller.state import latest_unfinished, load_state
from controller.tests.scripted import REAL, Script, fake_engine


def base_args(tmp_path) -> list[str]:
    return ["--logs", str(tmp_path / "logs"), "--no-book",
            "--syzygy", str(tmp_path / "sem_syzygy"), "--threads", "1", "--hash", "16"]


def run(argv, answers=(), mode="ok"):
    out: list[str] = []
    code = main(argv, input_fn=Script(list(answers)), output_fn=out.append,
                engine_factory=lambda path: fake_engine(mode))
    return code, "\n".join(out)


def test_color_required_without_resume(tmp_path):
    code, text = run(["start", *base_args(tmp_path)])
    assert code == 2 and "--color" in text


def test_bad_tc(tmp_path):
    code, text = run(["start", "--color", "white", "--tc", "15min", *base_args(tmp_path)])
    assert code == 2 and "controle de tempo" in text


def test_refuses_to_overwrite_existing_log(tmp_path):
    argv = ["start", "--color", "black", "--opponent", "X", *base_args(tmp_path)]
    assert run(argv)[0] == 0
    code, text = run(argv)
    assert code == 2 and "já existe" in text


def test_missing_book_is_an_error(tmp_path):
    args = [a for a in base_args(tmp_path) if a != "--no-book"]
    code, text = run(["start", "--color", "white", "--book", str(tmp_path / "x.bin"), *args])
    assert code == 2 and "x.bin" in text


def test_warns_without_book_and_syzygy(tmp_path):
    code, text = run(["start", "--color", "black", *base_args(tmp_path)])
    assert code == 0 and "sem book" in text and "sem tablebases" in text


def test_engine_crash_exits_2_then_resume_continues(tmp_path):
    code, text = run(["start", "--color", "white", *base_args(tmp_path)], mode="dieongo")
    assert code == 2 and "--resume" in text
    code, text = run(["start", "--resume", *base_args(tmp_path)], answers=["go"])
    assert code == 0
    assert "FEN:" in text  # tabuleiro mostrado ao retomar
    state = load_state(latest_unfinished(tmp_path / "logs"))
    assert state.moves == ["a2a3"]


def test_resume_without_games(tmp_path):
    code, text = run(["start", "--resume", *base_args(tmp_path)])
    assert code == 2 and "nenhuma partida" in text


def test_resume_finished_game_refused(tmp_path):
    assert run(["start", "--color", "black", *base_args(tmp_path)], answers=["draw"])[0] == 0
    state_file = next((tmp_path / "logs").glob("*.state.json"))
    code, text = run(["start", "--resume", str(state_file), *base_args(tmp_path)])
    assert code == 2 and "encerrada" in text


@pytest.mark.skipif(not REAL.exists(), reason="engine não compilado")
def test_full_game_against_weak_opponent_real_engine(tmp_path):
    logs = tmp_path / "logs"

    def opponent(prompt: str) -> str:
        # Adversário fraco: sempre o menor lance legal em ordem UCI.
        board = load_state(next(logs.glob("*.state.json"))).board()
        return min(m.uci() for m in board.legal_moves)

    out: list[str] = []
    code = main(["start", "--color", "white", "--tc", "20+0.2", "--opponent", "bot",
                 "--engine", str(REAL), *base_args(tmp_path)],
                input_fn=opponent, output_fn=out.append)
    assert code == 0
    state = load_state(next(logs.glob("*.state.json")))
    assert (state.result, state.reason) == ("1-0", "checkmate")
    log_file = next(logs.glob("*.log"))
    assert check_log(log_file) == []
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert sum(l.startswith("move=") for l in lines) == len(state.moves)
    assert lines[-1] == "# result=1-0 reason=checkmate"
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `$PY -m pytest controller/tests/test_main.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'controller.main'`

- [ ] **Step 3: Implementar `controller/main.py`**

```python
"""CLI do operador: `python -m controller.main start ...`."""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Callable

import chess

from controller.book import BookError, OpeningBook
from controller.clock import ClockFormatError, GameClock, parse_tc
from controller.engine_client import EngineClient, EngineError
from controller.game import Game
from controller.game_log import GameLog, log_path
from controller.runtime import runtime_options
from controller.state import (
    GameState, StateError, latest_unfinished, load_state, save_state, state_path_for,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENGINE = ROOT / "bin" / "youloss.exe"
DEFAULT_BOOK = ROOT / "assets" / "book.bin"
DEFAULT_SYZYGY = ROOT / "assets" / "syzygy"
DEFAULT_LOGS = ROOT / "logs"


class UsageError(Exception):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m controller.main")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start", help="inicia ou retoma uma partida")
    s.add_argument("--color", choices=["white", "black"], help="nosso lado")
    s.add_argument("--tc", default="900+10", help="base+inc em segundos (padrão 900+10)")
    s.add_argument("--opponent", default="adversario")
    s.add_argument("--game", type=int, default=1)
    s.add_argument("--resume", nargs="?", const="latest", metavar="STATE",
                   help="retoma a última partida em andamento (ou o .state.json dado)")
    s.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    s.add_argument("--book", type=Path, help=f"book Polyglot (padrão {DEFAULT_BOOK} se existir)")
    s.add_argument("--no-book", action="store_true")
    s.add_argument("--syzygy", type=Path, default=DEFAULT_SYZYGY)
    s.add_argument("--logs", type=Path, default=DEFAULT_LOGS)
    s.add_argument("--threads", type=int)
    s.add_argument("--hash", type=int, dest="hash_mb", metavar="MB")
    return parser


def _new_state(args: argparse.Namespace) -> tuple[GameState, Path]:
    if not args.color:
        raise UsageError("informe --color white|black (ou use --resume)")
    base_ms, inc_ms = parse_tc(args.tc)
    path = log_path(args.logs, args.opponent, args.game, date.today())
    if path.exists():
        raise UsageError(f"log já existe: {path} (use --resume ou outro --game)")
    state = GameState(color=args.color, opponent=args.opponent, game=args.game,
                      base_ms=base_ms, inc_ms=inc_ms, white_ms=base_ms, black_ms=base_ms,
                      log_path=str(path))
    state_path = state_path_for(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    save_state(state, state_path)
    return state, state_path


def _resumed_state(args: argparse.Namespace) -> tuple[GameState, Path]:
    if args.resume == "latest":
        state_path = latest_unfinished(args.logs)
        if state_path is None:
            raise UsageError(f"nenhuma partida em andamento em {args.logs}")
    else:
        state_path = Path(args.resume)
    state = load_state(state_path)
    if state.finished:
        raise UsageError(f"partida já encerrada ({state.result}): {state_path}")
    return state, state_path


def _book_path(args: argparse.Namespace) -> Path | None:
    if args.no_book:
        return None
    if args.book is not None:
        return args.book
    return DEFAULT_BOOK if DEFAULT_BOOK.exists() else None


def open_engine(engine: EngineClient, options: dict[str, int | str]) -> str:
    engine.start()
    info = engine.handshake(timeout=10)
    for name, value in options.items():
        engine.set_option(name, value)
    engine.is_ready(timeout=30)  # alocar Hash grande leva alguns segundos
    engine.send("ucinewgame")
    engine.is_ready(timeout=30)
    return info.get("name", "?")


def main(
    argv: list[str] | None = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    engine_factory: Callable[[Path], EngineClient] = EngineClient,
) -> int:
    args = build_parser().parse_args(argv)
    resumed = args.resume is not None
    book_path = _book_path(args)
    try:
        book = OpeningBook(book_path)
        state, state_path = _resumed_state(args) if resumed else _new_state(args)
    except (UsageError, StateError, ClockFormatError, BookError) as exc:
        output_fn(f"ERRO: {exc}")
        return 2

    options = runtime_options(args.syzygy, threads=args.threads, hash_mb=args.hash_mb)
    if book_path is None:
        output_fn("AVISO: sem book (--book ou assets/book.bin)")
    if "SyzygyPath" not in options:
        output_fn(f"AVISO: sem tablebases em {args.syzygy}")

    clock = GameClock(state.base_ms, state.inc_ms)
    clock.set(chess.WHITE, state.white_ms)
    clock.set(chess.BLACK, state.black_ms)
    log = GameLog(state.log_path)
    engine = engine_factory(args.engine)
    try:
        name = open_engine(engine, options)
        if resumed:
            log.note("resume")
        else:
            log.header(engine=name, color=state.color, opponent=state.opponent,
                       game=state.game, tc=args.tc, start_fen=state.start_fen)
        game = Game(state, state_path, engine, book, log, clock,
                    input_fn=input_fn, output_fn=output_fn, paused=resumed)
        output_fn(f"{name} | nós: {state.color} | adversário: {state.opponent} | log: {log.path}")
        if resumed:
            game.show_board()
        game.run()
    except EngineError as exc:
        output_fn(f"ERRO DO ENGINE: {exc}\nestado salvo em {state_path}; "
                  "retome com: python -m controller.main start --resume")
        return 2
    except KeyboardInterrupt:
        output_fn(f"\ninterrompido; estado em {state_path} (start --resume)")
        return 130
    finally:
        engine.quit()
        log.close()
        book.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `$PY -m pytest controller/tests -q`
Expected: todos passam, incluindo `test_full_game_against_weak_opponent_real_engine`, que leva cerca de 10 a 40 s.

- [ ] **Step 5: Adicionar a seção "Operação" no `README.md` (antes de `## Licença`)**

````markdown
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
````

- [ ] **Step 6: Ensaio manual pela CLI**

Run (no terminal, interativo):
```bash
.venv/Scripts/python -m controller.main start --color white --tc 60+1 --opponent ensaio --no-book
```
Jogar uns 5 lances do adversário e depois testar, nesta ordem: `board`, um lance ilegal, `undo`, `go`, `clock 0:50 0:55`, Ctrl+C, `start --resume`, `go`, `resign adv`. Depois:
```bash
.venv/Scripts/python -m controller.game_log logs/*_ensaio_g1.log
```
Expected: todas as ações se comportam como descrito no `help`; o validador sai com 0 e sem saída. Apagar os arquivos do ensaio em `logs/`, que ficam fora do git de qualquer forma.

- [ ] **Step 7: Commit**

```bash
git add controller/main.py controller/tests/test_main.py README.md
git commit -m "feat(controller): CLI start/--resume e partida completa com engine real"
```

---

## Definição de pronto da Sprint 1

- `pytest controller/tests` passa por inteiro, incluindo a partida completa com o engine real e `test_real_engine_probes_syzygy` (sem `skipped` com engine e Syzygy presentes).
- Partida completa pela CLI com log válido: `python -m controller.game_log <log>` sai com 0.
- `bash scripts/verify_assets.sh` sai com 0 (Syzygy 3-4-5 no MANIFEST).
- `bash testing/smoke.sh` continua passando (sem regressão da Sprint 0).
- Nenhum commit com atribuição de IA: `git log --format=%B main..HEAD | grep -ci co-authored` retorna 0.
- **Em aberto (decisão da equipe):** qual book Polyglot usar em `assets/book.bin`. Quando escolhido: baixar, adicionar o sha256 ao `assets/MANIFEST` e rodar `verify_assets.sh`. O controller já funciona com ou sem book.

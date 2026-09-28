# Sprint 0 — Fundação (toolchain, fork, build, handshake) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deixar o repositório pronto para as sprints seguintes. Isso inclui o toolchain instalado, o fork do Stockfish fixado e compilando com `bench` registrado, um controller Python que faz o handshake UCI com o engine e o fastchess rodando um smoke test.

**Architecture:** O Stockfish entra em `engine/` via `git subtree --squash`, fixado em uma tag de release, com a origem declarada em `engine/ORIGIN.md`. O build roda no shell MSYS2 UCRT64 por scripts em `scripts/`, e o binário sai em `bin/`. O controller (`controller/`) fala UCI com o processo do engine por um wrapper próprio de subprocess (`EngineClient`), escrito à mão porque as sprints seguintes precisam de `ponderhit`.

**Tech Stack:** MSYS2 UCRT64 (g++, make), Python 3.12, pytest, python-chess, Stockfish (tag de release), fastchess.

**Spec:** `docs/superpowers/specs/2026-09-28-youloss-chess-engine-design.md`

## Global Constraints

- Commits **sem** linhas `Co-Authored-By` de IA ou qualquer atribuição de IA.
- Nenhuma dependência de rede em runtime. Downloads (código, rede NNUE, ferramentas) só agora, antes do evento.
- `engine/` fixado em tag de release; projeto-base, tag, commit e licença (GPLv3) declarados em `engine/ORIGIN.md`.
- Dependências Python declaradas em `requirements.txt` com versões fixadas.
- Assets grandes e binários (`bin/`, `tools/`, `assets/`, `logs/`) fora do git.
- Python 3.12; build do engine com `COMP=mingw` no MSYS2 UCRT64.

## Review Focus

1. **Fontes C++ convertidos para CRLF pelo git no Windows (`core.autocrlf`)**: o build e o `bench` têm que continuar funcionando. O `.gitattributes` força LF em `engine/`, e a Task 1 inclui a verificação.
2. **Binário do engine ausente ou caminho errado**: o `EngineClient.start()` deve dar erro claro (`EngineNotFound` com o caminho), não um traceback genérico. O teste fica na Task 4.
3. **Engine que trava ou nunca responde `uciok`/`readyok`**: o handshake deve falhar por timeout em segundos (`EngineTimeout`), sem pendurar a CLI. O teste fica na Task 4.
4. **Engine que morre no meio (EOF no stdout)**: a leitura deve levantar `EngineCrashed`, não retornar string vazia em loop. O teste fica na Task 4.
5. **`python` resolvendo para o stub da Microsoft Store (WindowsApps)**: `scripts/check_toolchain.sh` deve detectar isso e falhar com mensagem. A verificação fica na Task 2.

---

### Task 1: Esqueleto do repositório

**Files:**
- Create: `.gitignore`, `.gitattributes`, `README.md`, `requirements.txt`

**Interfaces:**
- Produces: a estrutura de diretórios da spec (seção 3) e as regras de ignore e EOL usadas pelas tasks seguintes.

- [ ] **Step 1: Criar `.gitattributes`**

```
* text=auto
engine/** text eol=lf
*.sh text eol=lf
*.bin binary
*.rtbw binary
*.rtbz binary
*.nnue binary
```

- [ ] **Step 2: Criar `.gitignore`**

```
bin/
tools/
assets/*
!assets/MANIFEST
logs/
.venv/
__pycache__/
*.pyc
.pytest_cache/
engine/src/*.o
engine/src/stockfish
engine/src/stockfish.exe
engine/src/*.nnue
```

- [ ] **Step 3: Criar `requirements.txt`**

```
chess==1.11.2
pytest==8.3.3
```

- [ ] **Step 4: Criar `README.md`**

```markdown
# Youloss — III Chess Challenge

Motor de xadrez baseado em fork do Stockfish (ver `engine/ORIGIN.md`), com
gestão de tempo autoral e CLI de operador em Python.

## Setup (Windows)
1. `scripts/check_toolchain.sh` — valida MSYS2/g++/make/Python.
2. `scripts/build_engine.sh` — compila o engine em `bin/`.
3. `python -m venv .venv && .venv/Scripts/pip install -r requirements.txt`
4. `.venv/Scripts/python -m pytest controller/tests -v`

## Licença
GPLv3 (herdada do Stockfish). Ver `engine/Copying.txt`.
```

- [ ] **Step 5: Commit**

```bash
git add .gitattributes .gitignore requirements.txt README.md
git commit -m "chore: esqueleto do repositório"
```

---

### Task 2: Toolchain (MSYS2 + Python) com verificação

**Files:**
- Create: `scripts/check_toolchain.sh`

**Interfaces:**
- Produces: `scripts/check_toolchain.sh`, que termina com exit 0 quando o toolchain está OK. As Tasks 3, 5 e 6 dependem disso.

- [ ] **Step 1: Escrever o script de verificação (é o "teste" desta task)**

```bash
#!/usr/bin/env bash
# Valida toolchain necessário para build do engine e do controller.
set -u
fail=0
check() { if "$@" >/dev/null 2>&1; then echo "OK   $*"; else echo "FAIL $*"; fail=1; fi; }

UCRT=/c/msys64/ucrt64/bin
export PATH="$UCRT:/c/msys64/usr/bin:$PATH"

check "$UCRT/g++" --version
check make --version
check git --version

PY="$(command -v py >/dev/null && py -3.12 -c 'import sys;print(sys.executable)' 2>/dev/null)"
if [ -z "$PY" ] || [[ "$PY" == *WindowsApps* ]]; then
  echo "FAIL python 3.12 real não encontrado (stub WindowsApps?)"; fail=1
else
  echo "OK   python $PY"
fi
exit $fail
```

- [ ] **Step 2: Rodar e confirmar que falha (toolchain ausente)**

Run: `bash scripts/check_toolchain.sh`
Expected: linhas `FAIL` para g++ e python, exit 1.

- [ ] **Step 3: Instalar o toolchain**

```powershell
winget install --id MSYS2.MSYS2 -e --accept-package-agreements --accept-source-agreements
winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
C:\msys64\usr\bin\bash.exe -lc "pacman -Syu --noconfirm; pacman -S --noconfirm --needed mingw-w64-ucrt-x86_64-gcc make git"
```

Desativar os aliases do Python da Microsoft Store: Configurações > Aplicativos > Configurações avançadas > Aliases de execução > desligar `python.exe` e `python3.exe`.

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `bash scripts/check_toolchain.sh`
Expected: todas as linhas `OK`, exit 0.

- [ ] **Step 5: Commit**

```bash
git add scripts/check_toolchain.sh
git commit -m "chore: script de verificação do toolchain"
```

---

### Task 3: Fork do Stockfish fixado + ORIGIN.md

**Files:**
- Create: `engine/` (via subtree), `engine/ORIGIN.md`

**Interfaces:**
- Produces: `engine/src/Makefile` e as fontes do Stockfish. `engine/ORIGIN.md` guarda a tag, o commit e o bench de referência (preenchido na Task 5).

- [ ] **Step 1: Descobrir a tag de release estável mais recente**

Run: `git ls-remote --tags --refs https://github.com/official-stockfish/Stockfish "sf_*" | sort -t_ -k2 -V | tail -1`
Expected: uma linha `<sha> refs/tags/sf_<N>`. Anotar `<N>` e `<sha>`.

- [ ] **Step 2: Adicionar como subtree**

```bash
git subtree add --prefix engine https://github.com/official-stockfish/Stockfish sf_<N> --squash
```

Expected: commit de merge "Squashed 'engine/' content from commit <sha>".

- [ ] **Step 3: Verificar que as fontes estão com LF**

Run: `git ls-files --eol engine/src/Makefile engine/src/search.cpp`
Expected: `i/lf w/lf` nas duas linhas.

- [ ] **Step 4: Criar `engine/ORIGIN.md`**

```markdown
# Origem do engine

- Projeto-base: Stockfish — https://github.com/official-stockfish/Stockfish
- Tag: sf_<N>
- Commit: <sha>
- Licença: GPLv3 (ver `Copying.txt`). Este fork herda a licença; o código-fonte
  completo será disponibilizado à banca e publicado ao final do evento.
- Bench de referência (sem modificações, 1 thread, `bench` padrão): <preenchido na Task 5>

## Modificações autorais da equipe Youloss
- Gestão de tempo (`src/youloss_tm.{h,cpp}`) — a partir da Sprint 2.
```

- [ ] **Step 5: Commit**

```bash
git add engine/ORIGIN.md
git commit -m "docs: declara origem do fork do Stockfish"
```

---

### Task 4: `EngineClient` — handshake UCI com erros explícitos

**Files:**
- Create: `controller/__init__.py`, `controller/engine_client.py`
- Create: `controller/tests/__init__.py`, `controller/tests/fake_engine.py`, `controller/tests/test_engine_client.py`

**Interfaces:**
- Produces (usado pela Sprint 1):
  - `class EngineError(Exception)`; as subclasses são `EngineNotFound`, `EngineTimeout` e `EngineCrashed`.
  - `EngineClient(path: str | Path, args: list[str] | None = None)`
  - `.start() -> None`, `.send(cmd: str) -> None`, `.read_line(timeout: float) -> str`
  - `.read_until(prefix: str, timeout: float) -> list[str]`: devolve todas as linhas lidas, incluindo a que começa com `prefix`.
  - `.handshake(timeout: float = 5.0) -> dict[str, str]`: devolve `{"name": ..., "author": ...}` depois de `uciok`.
  - `.is_ready(timeout: float = 5.0) -> None`, `.set_option(name: str, value: str | int | bool) -> None`, `.quit(timeout: float = 2.0) -> None`
  - O contexto (`with EngineClient(...) as e:`) chama `start()` na entrada e `quit()` na saída.

- [ ] **Step 1: Criar o engine falso para os testes**

`controller/tests/fake_engine.py`:
```python
"""Engine UCI falso para testes. Modo via argv[1]: ok | hang | crash."""
import sys

mode = sys.argv[1] if len(sys.argv) > 1 else "ok"
for line in sys.stdin:
    cmd = line.strip()
    if mode == "crash":
        sys.exit(3)
    if mode == "hang":
        continue
    if cmd == "uci":
        print("id name FakeFish 1.0")
        print("id author Youloss")
        print("option name Hash type spin default 16 min 1 max 1024")
        print("uciok")
    elif cmd == "isready":
        print("readyok")
    elif cmd == "quit":
        break
    sys.stdout.flush()
```

- [ ] **Step 2: Escrever os testes que falham**

`controller/tests/test_engine_client.py`:
```python
import sys
from pathlib import Path

import pytest

from controller.engine_client import (
    EngineClient, EngineCrashed, EngineNotFound, EngineTimeout,
)

FAKE = Path(__file__).with_name("fake_engine.py")
REAL = Path(__file__).resolve().parents[2] / "bin" / "youloss.exe"


def fake(mode: str) -> EngineClient:
    return EngineClient(sys.executable, args=[str(FAKE), mode])


def test_handshake_returns_id():
    with fake("ok") as eng:
        info = eng.handshake(timeout=5)
        eng.is_ready(timeout=5)
    assert info == {"name": "FakeFish 1.0", "author": "Youloss"}


def test_missing_binary_raises_not_found():
    eng = EngineClient("C:/nao/existe/engine.exe")
    with pytest.raises(EngineNotFound, match="nao/existe"):
        eng.start()


def test_hanging_engine_times_out():
    with fake("hang") as eng:
        with pytest.raises(EngineTimeout):
            eng.handshake(timeout=0.5)


def test_crashing_engine_raises_crashed():
    with fake("crash") as eng:
        with pytest.raises(EngineCrashed):
            eng.handshake(timeout=5)


@pytest.mark.skipif(not REAL.exists(), reason="engine não compilado")
def test_real_engine_handshake():
    with EngineClient(REAL) as eng:
        info = eng.handshake(timeout=10)
        eng.set_option("Threads", 1)
        eng.is_ready(timeout=10)
    assert "Stockfish" in info["name"]
```

- [ ] **Step 3: Rodar e confirmar que falha**

Run: `.venv/Scripts/python -m pytest controller/tests/test_engine_client.py -v`
Expected: `ModuleNotFoundError: No module named 'controller.engine_client'`.

- [ ] **Step 4: Implementar `controller/engine_client.py`**

```python
"""Cliente UCI mínimo sobre subprocess, com leitura em thread e timeouts."""
from __future__ import annotations

import queue
import subprocess
import threading
from pathlib import Path

_EOF = object()


class EngineError(Exception):
    pass


class EngineNotFound(EngineError):
    pass


class EngineTimeout(EngineError):
    pass


class EngineCrashed(EngineError):
    pass


class EngineClient:
    def __init__(self, path: str | Path, args: list[str] | None = None):
        self.path = str(path)
        self.args = args or []
        self._proc: subprocess.Popen[str] | None = None
        self._lines: queue.Queue[object] = queue.Queue()

    def start(self) -> None:
        try:
            self._proc = subprocess.Popen(
                [self.path, *self.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except FileNotFoundError as exc:
            raise EngineNotFound(f"engine não encontrado: {self.path}") from exc
        threading.Thread(target=self._pump, daemon=True).start()

    def _pump(self) -> None:
        assert self._proc and self._proc.stdout
        for line in self._proc.stdout:
            self._lines.put(line.rstrip("\r\n"))
        self._lines.put(_EOF)

    def send(self, cmd: str) -> None:
        if not self._proc or not self._proc.stdin:
            raise EngineCrashed("engine não iniciado")
        try:
            self._proc.stdin.write(cmd + "\n")
            self._proc.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise EngineCrashed(f"falha ao enviar '{cmd}'") from exc

    def read_line(self, timeout: float) -> str:
        try:
            item = self._lines.get(timeout=timeout)
        except queue.Empty as exc:
            raise EngineTimeout(f"sem resposta em {timeout}s") from exc
        if item is _EOF:
            self._lines.put(_EOF)
            code = self._proc.poll() if self._proc else None
            raise EngineCrashed(f"engine encerrou (exit={code})")
        return item  # type: ignore[return-value]

    def read_until(self, prefix: str, timeout: float) -> list[str]:
        out: list[str] = []
        while True:
            line = self.read_line(timeout)
            out.append(line)
            if line.startswith(prefix):
                return out

    def handshake(self, timeout: float = 5.0) -> dict[str, str]:
        self.send("uci")
        info: dict[str, str] = {}
        for line in self.read_until("uciok", timeout):
            if line.startswith("id name "):
                info["name"] = line[len("id name "):]
            elif line.startswith("id author "):
                info["author"] = line[len("id author "):]
        return info

    def is_ready(self, timeout: float = 5.0) -> None:
        self.send("isready")
        self.read_until("readyok", timeout)

    def set_option(self, name: str, value: str | int | bool) -> None:
        if isinstance(value, bool):
            value = "true" if value else "false"
        self.send(f"setoption name {name} value {value}")

    def quit(self, timeout: float = 2.0) -> None:
        if not self._proc:
            return
        try:
            self.send("quit")
        except EngineCrashed:
            pass
        try:
            self._proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._proc.kill()
            self._proc.wait()

    def __enter__(self) -> EngineClient:
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.quit()
```

Criar `controller/__init__.py` e `controller/tests/__init__.py` vazios.

- [ ] **Step 5: Criar o venv e rodar os testes**

```bash
py -3.12 -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python -m pytest controller/tests/test_engine_client.py -v
```

Expected: 4 passed, 1 skipped (engine real ainda não compilado).

- [ ] **Step 6: Commit**

```bash
git add controller
git commit -m "feat(controller): cliente UCI com handshake e erros explícitos"
```

---

### Task 5: Build do engine + bench de referência

**Files:**
- Create: `scripts/build_engine.sh`
- Modify: `engine/ORIGIN.md` (linha "Bench de referência")

**Interfaces:**
- Consumes: `engine/src/Makefile` (Task 3), toolchain (Task 2).
- Produces: `bin/youloss.exe` (build `native`) e `bin/youloss-avx2.exe` (fallback).

- [ ] **Step 1: Escrever `scripts/build_engine.sh`**

```bash
#!/usr/bin/env bash
# Compila o engine (profile-build) e copia para bin/. Rodar do root do repo.
set -euo pipefail
export PATH="/c/msys64/ucrt64/bin:/c/msys64/usr/bin:$PATH"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JOBS="$(nproc)"
mkdir -p "$ROOT/bin"

build() {  # $1=ARCH  $2=nome do binário
  make -C "$ROOT/engine/src" clean >/dev/null
  make -C "$ROOT/engine/src" -j"$JOBS" profile-build ARCH="$1" COMP=mingw
  cp "$ROOT/engine/src/stockfish.exe" "$ROOT/bin/$2"
}

build native youloss.exe
build x86-64-avx2 youloss-avx2.exe
"$ROOT/bin/youloss.exe" bench 2>&1 | tail -4
```

O `make` baixa a rede NNUE padrão na primeira execução. Isso é permitido agora, antes do evento. A rede fica embutida no binário.

- [ ] **Step 2: Rodar o build**

Run: `bash scripts/build_engine.sh`
Expected: as últimas linhas mostram `Total time (ms)`, `Nodes searched  : <N>` e `Nodes/second`.

- [ ] **Step 3: Validar o bench contra o upstream**

Abrir `https://github.com/official-stockfish/Stockfish/commit/<sha>` (sha anotado na Task 3) e comparar `<N>` com a linha `Bench: ...` da mensagem do commit.
Expected: `Nodes searched` igual ao `Bench:` oficial. Se for diferente, os fontes foram alterados (verificar o EOL da Task 3).

- [ ] **Step 4: Registrar em `engine/ORIGIN.md`**

Substituir `<preenchido na Task 5>` por `<N> nós (Nodes searched)`.

- [ ] **Step 5: Rodar o teste de integração do handshake real**

Run: `.venv/Scripts/python -m pytest controller/tests -v`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add scripts/build_engine.sh engine/ORIGIN.md
git commit -m "build: script de build do engine e bench de referência"
```

---

### Task 6: fastchess + smoke test

**Files:**
- Create: `scripts/build_fastchess.sh`, `testing/smoke.sh`

**Interfaces:**
- Consumes: `bin/youloss.exe` (Task 5).
- Produces: `tools/fastchess.exe` e `testing/smoke.sh`. A Sprint 2 usa os dois como base do SPRT.

- [ ] **Step 1: Escrever `scripts/build_fastchess.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
export PATH="/c/msys64/ucrt64/bin:/c/msys64/usr/bin:$PATH"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAG="$(git ls-remote --tags --refs https://github.com/Disservin/fastchess 'v*' | awk -F/ '{print $3}' | sort -V | tail -1)"
rm -rf "$ROOT/tools/fastchess-src"
git clone --depth 1 --branch "$TAG" https://github.com/Disservin/fastchess "$ROOT/tools/fastchess-src"
make -C "$ROOT/tools/fastchess-src" -j"$(nproc)"
cp "$ROOT/tools/fastchess-src/fastchess.exe" "$ROOT/tools/fastchess.exe"
echo "fastchess $TAG"
```

- [ ] **Step 2: Escrever `testing/smoke.sh`**

```bash
#!/usr/bin/env bash
# Smoke test: 4 partidas rápidas do engine contra ele mesmo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/tools/fastchess.exe" \
  -engine cmd="$ROOT/bin/youloss.exe" name=A \
  -engine cmd="$ROOT/bin/youloss.exe" name=B \
  -each tc=5+0.05 option.Threads=1 option.Hash=16 \
  -rounds 2 -games 2 -concurrency 2 -recover
```

- [ ] **Step 3: Rodar**

```bash
bash scripts/build_fastchess.sh
bash testing/smoke.sh
```

Expected: 4 partidas terminadas, resumo com `Games: 4`, nenhum `timeout`/`disconnect`.

- [ ] **Step 4: Commit**

```bash
git add scripts/build_fastchess.sh testing/smoke.sh
git commit -m "test: fastchess e smoke test do engine"
```

---

## Definição de pronto da Sprint 0
- `scripts/check_toolchain.sh` sai com 0.
- `bin/youloss.exe bench` bate com o `Bench:` oficial da tag, registrado em `engine/ORIGIN.md`.
- `pytest controller/tests` passa com 5 testes (incluindo o handshake real).
- `testing/smoke.sh` completa 4 partidas sem erros.
- Nenhum commit com atribuição de IA: `git log --format=%B | grep -ci co-authored` retorna 0.

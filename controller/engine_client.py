"""Cliente UCI mínimo sobre subprocess, com leitura em thread e timeouts."""
from __future__ import annotations

import queue
import subprocess
import threading
import time
from dataclasses import dataclass, field
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


class EngineClient:
    def __init__(self, path: str | Path, args: list[str] | None = None):
        self.path = str(path)
        self.args = args or []
        self._proc: subprocess.Popen[str] | None = None
        self._lines: queue.Queue[object] = queue.Queue()

    def start(self) -> None:
        if self._proc and self._proc.poll() is None:
            self.quit()
        # Fila nova por processo: o EOF/linhas do processo anterior não vazam.
        self._lines = queue.Queue()
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
        except OSError as exc:
            raise EngineError(f"falha ao iniciar {self.path}: {exc}") from exc
        threading.Thread(
            target=self._pump, args=(self._proc, self._lines), daemon=True
        ).start()

    @staticmethod
    def _pump(proc: subprocess.Popen[str], lines: queue.Queue[object]) -> None:
        # Recebe proc/fila como argumentos: após um restart, a thread antiga
        # continua presa à fila antiga e não contamina a do processo novo.
        assert proc.stdout
        for line in proc.stdout:
            lines.put(line.rstrip("\r\n"))
        lines.put(_EOF)

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
        """Lê até a linha com `prefix`; `timeout` vale para a chamada inteira."""
        deadline = time.monotonic() + timeout
        out: list[str] = []
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise EngineTimeout(f"'{prefix}' não recebido em {timeout}s")
            line = self.read_line(remaining)
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

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

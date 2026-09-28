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

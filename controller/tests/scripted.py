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

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

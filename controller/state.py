"""Estado da partida em JSON, gravado a cada lance para `start --resume`."""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import chess

STATE_VERSION = 2
SUPPORTED_VERSIONS = (1, 2)
REPLACE_ATTEMPTS = 5
_FIELD_TYPES = {
    "color": str,
    "opponent": str,
    "game": int,
    "base_ms": int,
    "inc_ms": int,
    "start_fen": str,
    "moves": list,
    "white_ms": int,
    "black_ms": int,
    "log_path": str,
    "pending_depth": int,
    "pending_seldepth": int,
    "pending_nodes": int,
}


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
    # Proposta pendente (v2): lance sugerido pelo engine/book ainda NÃO jogado
    # no tabuleiro físico. Só vira lance após `played` (confirmação única).
    # Ausente (None) em arquivos v1.
    pending_uci: str | None = None
    pending_source: str | None = None  # "engine" | "book" | "forced" | "fallback"
    pending_depth: int = 0
    pending_seldepth: int = 0
    pending_nodes: int = 0
    pending_score_cp: int | None = None
    pending_score_mate: int | None = None
    pending_pv: list[str] = field(default_factory=list)

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
    # No Windows, antivírus/indexador pode segurar o destino por instantes.
    for attempt in range(REPLACE_ATTEMPTS):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == REPLACE_ATTEMPTS - 1:
                raise
            time.sleep(0.05)


def _check_types(state: GameState, path: str | Path) -> None:
    for name, kind in _FIELD_TYPES.items():
        value = getattr(state, name)
        if not isinstance(value, kind) or (kind is int and isinstance(value, bool)):
            raise StateError(f"estado com campo inválido: {path}: {name}={value!r}")
    if state.color not in ("white", "black"):
        raise StateError(f"estado com cor inválida: {path}: {state.color!r}")
    if not all(isinstance(uci, str) for uci in state.moves):
        raise StateError(f"estado com lances inválidos: {path}: {state.moves!r}")
    for name in ("result", "reason", "pending_uci", "pending_source"):
        if getattr(state, name) is not None and not isinstance(
            getattr(state, name), str
        ):
            raise StateError(f"estado com campo inválido: {path}: {name}")
    for name in ("pending_score_cp", "pending_score_mate"):
        value = getattr(state, name)
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool)
        ):
            raise StateError(f"estado com campo inválido: {path}: {name}={value!r}")
    if not isinstance(state.pending_pv, list) or not all(
        isinstance(uci, str) for uci in state.pending_pv
    ):
        raise StateError(
            f"estado com PV pendente inválida: {path}: {state.pending_pv!r}"
        )
    if state.pending_source is not None and state.pending_source not in (
        "engine",
        "book",
        "forced",
        "fallback",
    ):
        raise StateError(
            f"estado com proposta inválida: {path}: {state.pending_source!r}"
        )
    if (state.pending_uci is None) != (state.pending_source is None):
        raise StateError(f"estado com proposta incompleta: {path}")
    if state.pending_uci is not None:
        try:
            chess.Move.from_uci(state.pending_uci)
        except ValueError as exc:
            raise StateError(f"estado com proposta inválida: {path}: {exc}") from exc


def load_state(path: str | Path) -> GameState:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StateError(f"estado não encontrado: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StateError(f"estado corrompido ou ilegível: {path}: {exc}") from exc
    if (
        not isinstance(data, dict)
        or data.pop("version", None) not in SUPPORTED_VERSIONS
    ):
        raise StateError(f"versão de estado não suportada: {path}")
    # v1 não tem os campos pending_*: os defaults do dataclass cobrem a leitura.
    try:
        state = GameState(**data)
    except TypeError as exc:
        raise StateError(f"estado com campos inválidos: {path}: {exc}") from exc
    _check_types(state, path)
    try:
        state.board()
    except ValueError as exc:
        raise StateError(f"estado com lances ou FEN inválidos: {path}: {exc}") from exc
    return state


def state_path_for(log_path: str | Path) -> Path:
    return Path(log_path).with_suffix(".state.json")


def latest_unfinished(logs_dir: str | Path) -> Path | None:
    paths = sorted(
        Path(logs_dir).glob("*.state.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for path in paths:
        try:
            if not load_state(path).finished:
                return path
        except StateError:
            continue
    return None

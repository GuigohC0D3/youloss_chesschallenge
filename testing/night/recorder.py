"""Durable per-run recording: events, per-move telemetry, PGN, summary."""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import chess
import chess.pgn

from testing.night.config import RunSpec


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, chess.Move):
        return value.uci()
    return value


class Recorder:
    def __init__(self, spec: RunSpec):
        self.spec = spec
        self.run_dir = spec.out_dir
        self.games_dir = self.run_dir / "games"
        self.failures_dir = self.run_dir / "failures"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.games_dir.mkdir(parents=True, exist_ok=True)
        self.failures_dir.mkdir(parents=True, exist_ok=True)
        self._events = open(self.run_dir / "events.jsonl", "a", encoding="utf-8")
        self._moves = open(self.run_dir / "moves.jsonl", "a", encoding="utf-8")
        self.started_at = _utc_now()
        self._started_mono = time.monotonic()
        self.games: list[dict[str, Any]] = []
        self.moves = 0
        self.failures = 0
        (self.run_dir / "run.json").write_text(
            json.dumps(
                {
                    "spec": spec.to_dict(),
                    "started_at": self.started_at,
                    "host": os.uname().nodename,
                    "python": os.sys.version.split()[0],
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def event(self, name: str, **fields: Any) -> None:
        row = {"ts": _utc_now(), "event": name, **fields}
        self._events.write(
            json.dumps(row, ensure_ascii=False, default=_jsonable) + "\n"
        )
        self._events.flush()

    def move(self, **fields: Any) -> None:
        row = {"ts": _utc_now(), **fields}
        self._moves.write(json.dumps(row, ensure_ascii=False, default=_jsonable) + "\n")
        self._moves.flush()
        self.moves += 1

    def game_start(self, number: int, **fields: Any) -> None:
        self.event("game_start", number=number, **fields)

    def game_end(self, number: int, **fields: Any) -> None:
        row = {"number": number, **fields}
        self.games.append(row)
        self.event("game_end", **row)

    def failure(
        self, label: str, screenshot: Path | None = None, **fields: Any
    ) -> Path:
        self.failures += 1
        row = {"label": label, **fields}
        if screenshot is not None:
            row["screenshot"] = str(screenshot)
        self.event("failure", **row)
        return screenshot or self.failures_dir

    def write_pgn(
        self,
        number: int,
        *,
        start_fen: str,
        moves_uci: list[str],
        headers: dict[str, str],
    ) -> Path:
        game = chess.pgn.Game()
        game.headers.update(headers)
        if start_fen != chess.STARTING_FEN:
            game.headers["SetUp"] = "1"
            game.headers["FEN"] = start_fen
            game.setup(start_fen)
        node = game
        replay = chess.Board(start_fen)
        for uci in moves_uci:
            move = chess.Move.from_uci(uci)
            node = node.add_variation(move)
            replay.push(move)
        path = self.games_dir / f"{number:04d}.pgn"
        path.write_text(str(game) + "\n", encoding="utf-8")
        return path

    def finish(self, *, result: str) -> Path:
        elapsed = time.monotonic() - self._started_mono
        summary = {
            "result": result,
            "started_at": self.started_at,
            "finished_at": _utc_now(),
            "elapsed_s": round(elapsed, 1),
            "games": len(self.games),
            "moves": self.moves,
            "failures": self.failures,
            "game_rows": self.games,
        }
        path = self.run_dir / "summary.json"
        path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        self.event("run_end", result=result, elapsed_s=round(elapsed, 1))
        self.close()
        return path

    def close(self) -> None:
        for handle in (self._events, self._moves):
            if not handle.closed:
                handle.flush()
                os.fsync(handle.fileno())
                handle.close()

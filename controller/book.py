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

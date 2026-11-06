"""Board reconstruction and SAN handling for chess.com move lists."""

from __future__ import annotations

import re
from dataclasses import dataclass

import chess

_CASTLE = {"0-0-0": "O-O-O", "0-0": "O-O", "o-o-o": "O-O-O", "o-o": "O-O"}
_ANNOTATION = re.compile(r"[!?]+$")
_SAN = re.compile(
    r"^(?:[KQRBN][a-h]?[1-8]?x?[a-h][1-8]"
    r"|[a-h]x?[a-h][1-8](?:=[QRBN])?"
    r"|[a-h][1-8](?:=[QRBN])?"
    r"|O-O(?:-O)?)"
    r"[+#]?$"
)


class BoardError(ValueError):
    pass


def normalize_san(raw: str) -> str | None:
    """Return a python-chess-friendly SAN token, or None for noise."""
    text = (raw or "").strip().replace("\u00a0", " ")
    text = text.replace("e.p.", "").replace("ep", "").strip()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", "", text)
    text = text.lstrip(".")
    text = _ANNOTATION.sub("", text)
    if not text:
        return None
    lower = text.lower()
    if lower in _CASTLE:
        text = _CASTLE[lower]
    # chess.com occasionally renders promotion without '='.
    text = re.sub(r"^([a-h][1-8])([QRBN])$", r"\1=\2", text)
    if not _SAN.match(text):
        return None
    return text


def san_list(raw_tokens: list[str]) -> list[str]:
    out: list[str] = []
    for raw in raw_tokens:
        san = normalize_san(raw)
        if san is not None:
            out.append(san)
    return out


def board_from_san(start_fen: str, sans: list[str]) -> chess.Board:
    board = chess.Board(start_fen)
    for index, san in enumerate(sans):
        try:
            board.push_san(san)
        except ValueError as exc:
            raise BoardError(
                f"lance {index + 1} inválido ({san!r}) a partir de {board.fen()}: {exc}"
            ) from exc
    return board


def uci_from_san(board: chess.Board, san: str) -> str:
    return board.parse_san(san).uci()


def result_for(board: chess.Board, our_color: chess.Color) -> tuple[str, str] | None:
    """Map a finished board to a PGN result and a stable reason string."""
    outcome = board.outcome()
    if outcome is None:
        return None
    termination = outcome.termination.name.lower()
    if outcome.winner is None:
        return "1/2-1/2", termination
    white_won = outcome.winner == chess.WHITE
    return ("1-0" if white_won else "0-1"), termination


@dataclass(frozen=True)
class PiecePlacement:
    square: chess.Square
    piece: chess.Piece


_PIECE_LETTERS = {
    "p": chess.PAWN,
    "n": chess.KNIGHT,
    "b": chess.BISHOP,
    "r": chess.ROOK,
    "q": chess.QUEEN,
    "k": chess.KING,
}


def pieces_from_classes(classes: list[str]) -> list[PiecePlacement]:
    """Parse chess.com piece classes such as ``piece wp square-52``.

    Extra classes and unknown tokens are ignored; a malformed square is an
    error because silently dropping a piece would corrupt the position.
    """
    placements: list[PiecePlacement] = []
    for raw in classes:
        tokens = raw.split()
        color = piece_type = None
        file_no = rank_no = None
        for token in tokens:
            if token in ("wp", "wn", "wb", "wr", "wq", "wk"):
                color, piece_type = chess.WHITE, _PIECE_LETTERS[token[1]]
            elif token in ("bp", "bn", "bb", "br", "bq", "bk"):
                color, piece_type = chess.BLACK, _PIECE_LETTERS[token[1]]
            elif token.startswith("square-") and len(token) == 9:
                try:
                    file_no = int(token[7])
                    rank_no = int(token[8])
                except ValueError as exc:
                    raise BoardError(f"casa inválida: {token!r}") from exc
        if color is None or piece_type is None or file_no is None or rank_no is None:
            continue
        if not (1 <= file_no <= 8 and 1 <= rank_no <= 8):
            raise BoardError(f"casa fora do tabuleiro: {raw!r}")
        square = chess.square(file_no - 1, rank_no - 1)
        placements.append(PiecePlacement(square, chess.Piece(piece_type, color)))
    return placements


def board_from_pieces(
    classes: list[str],
    *,
    turn: chess.Color,
    castling: str = "KQkq",
    ep_square: int | None = None,
    halfmove_clock: int = 0,
    fullmove_number: int = 1,
) -> chess.Board:
    board = chess.Board(None)
    seen: dict[chess.Square, chess.Piece] = {}
    for placement in pieces_from_classes(classes):
        if placement.square in seen:
            raise BoardError(
                f"duas peças na casa {chess.square_name(placement.square)}"
            )
        seen[placement.square] = placement.piece
        board.set_piece_at(placement.square, placement.piece)
    if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
        raise BoardError("posição sem os dois reis")
    board.turn = turn
    board.castling_rights = board.clean_castling_rights()
    if castling:
        board.set_castling_fen(castling)
    board.ep_square = ep_square
    board.halfmove_clock = halfmove_clock
    board.fullmove_number = fullmove_number
    if not board.is_valid():
        raise BoardError(f"posição inválida: {board.status()!r}")
    return board


def cross_check(san_board: chess.Board, piece_classes: list[str]) -> bool:
    """True when the rendered pieces match the SAN-reconstructed board."""
    try:
        rendered = board_from_pieces(
            piece_classes,
            turn=san_board.turn,
            castling=san_board.castling_xfen().split()[0].replace("-", ""),
            ep_square=san_board.ep_square,
            halfmove_clock=san_board.halfmove_clock,
            fullmove_number=san_board.fullmove_number,
        )
    except (BoardError, ValueError):
        return False
    return rendered.board_fen() == san_board.board_fen()

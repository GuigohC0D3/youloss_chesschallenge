"""Perfil de uso de tempo por engine a partir do PGN do fastchess.

Cada lance traz um comentário com o tempo gasto, ex.: {+0.25/12 0.345s}."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

BUCKETS = [("1-10", 1, 10), ("11-20", 11, 20), ("21-40", 21, 40), ("41+", 41, 10_000)]
_TAG = re.compile(r'^\[(\w+) "([^"]*)"\]', re.M)
_MOVE_TIME = re.compile(r"\{[^}]*?\s(\d+(?:\.\d+)?)s\b[^}]*\}")


@dataclass
class EngineProfile:
    games: int = 0
    total_s: float = 0.0
    buckets: dict[str, list[float]] = field(
        default_factory=lambda: {name: [] for name, _, _ in BUCKETS})
    forfeits: int = 0


def _bucket(fullmove: int) -> str:
    return next(name for name, lo, hi in BUCKETS if lo <= fullmove <= hi)


def _split_games(text: str) -> list[str]:
    return [g for g in re.split(r"(?=^\[Event )", text, flags=re.M) if g.strip()]


def profile(pgn_text: str) -> dict[str, EngineProfile]:
    result: dict[str, EngineProfile] = {}
    for game in _split_games(pgn_text):
        tags = dict(_TAG.findall(game))
        white, black = tags.get("White", "?"), tags.get("Black", "?")
        fen = tags.get("FEN", "").split()
        white_to_move = len(fen) < 2 or fen[1] == "w"
        fullmove = int(fen[5]) if len(fen) >= 6 else 1
        for name in (white, black):
            result.setdefault(name, EngineProfile()).games += 1
        side_white = white_to_move
        for m in _MOVE_TIME.finditer(game):
            seconds = float(m[1])
            prof = result[white if side_white else black]
            prof.total_s += seconds
            prof.buckets[_bucket(fullmove)].append(seconds)
            if not side_white:
                fullmove += 1
            side_white = not side_white
        if tags.get("Termination") == "time forfeit":
            loser = white if tags.get("Result") == "0-1" else black
            result[loser].forfeits += 1
    return result


def mean_total(prof: EngineProfile) -> float:
    return prof.total_s / prof.games if prof.games else 0.0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    prof = profile(Path(args[0]).read_text(encoding="utf-8", errors="replace"))
    header = f"{'engine':<8}{'jogos':>7}{'s/jogo':>9}" + "".join(
        f"{'s/lance ' + name:>18}" for name, _, _ in BUCKETS) + f"{'flag':>6}"
    print(header)
    for name, p in sorted(prof.items()):
        means = "".join(
            f"{(sum(v) / len(v) if v else 0.0):>18.3f}" for v in p.buckets.values())
        print(f"{name:<8}{p.games:>7}{mean_total(p):>9.2f}{means}{p.forfeits:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

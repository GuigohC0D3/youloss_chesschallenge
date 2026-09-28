"""Resume o SPRT a partir do log do fastchess.

Exit (CLI): 0 = H1 aceita, 1 = H0 aceita, 2 = inconclusivo."""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ACCEPTED = re.compile(r"H([01]) was accepted")
_GAMES = re.compile(r"^Games:\s*(\d+)", re.M)
_LLR = re.compile(r"^LLR:\s*(-?\d+(?:\.\d+)?)", re.M)
_ELO = re.compile(r"^Elo:\s*(-?\d+(?:\.\d+)?)\s*\+/-\s*(\d+(?:\.\d+)?)", re.M)


def _last(pattern: re.Pattern[str], text: str) -> re.Match[str] | None:
    matches = list(pattern.finditer(text))
    return matches[-1] if matches else None


def summarize(text: str) -> tuple[int, str]:
    accepted = _last(_ACCEPTED, text)
    games, llr, elo = _last(_GAMES, text), _last(_LLR, text), _last(_ELO, text)
    parts = [
        f"games={games[1] if games else '?'}",
        f"llr={llr[1] if llr else '?'}",
        f"elo={elo[1]}±{elo[2]}" if elo else "elo=?",
    ]
    if accepted is None:
        return 2, "SPRT inconclusivo: " + " ".join(parts)
    hypothesis = accepted[1]
    return (0 if hypothesis == "1" else 1), f"SPRT H{hypothesis} aceita: " + " ".join(parts)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    code, line = summarize(Path(args[0]).read_text(encoding="utf-8", errors="replace"))
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())

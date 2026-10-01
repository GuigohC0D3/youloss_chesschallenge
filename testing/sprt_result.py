"""Resume o SPRT a partir do log do fastchess.

Exit (CLI): 0 = H1 aceita, 1 = H0 aceita, 2 = inconclusivo."""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

_ACCEPTED = re.compile(r"H([01]) was accepted")
_GAMES_ROW = re.compile(r"^Games:.*$", re.M)
_ELO = re.compile(r"^Elo:\s*(-?\d+(?:\.\d+)?)\s*\+/-\s*(\d+(?:\.\d+)?)", re.M)
_LLR_LINE = re.compile(r"^LLR:\s*(.*)$", re.M)
_NUMBER = r"-?\d+(?:\.\d+)?"
_GAMES_SUMMARY = re.compile(
    rf"^Games:\s*(\d+),\s*Wins:\s*(\d+),\s*Losses:\s*(\d+),\s*"
    rf"Draws:\s*(\d+),\s*Points:\s*({_NUMBER})\s*"
    rf"\(\s*{_NUMBER}\s*%\s*\)$"
)
_LLR_SUMMARY = re.compile(
    rf"^({_NUMBER})\s*\(\s*({_NUMBER})%\s*\)\s*"
    rf"\(\s*({_NUMBER})\s*,\s*({_NUMBER})\s*\)\s*"
    rf"\[\s*({_NUMBER})\s*,\s*({_NUMBER})\s*\]$"
)
_LLR_FALLBACK = re.compile(r"^\s*(-?\d+(?:\.\d+)?)")


def _last(pattern: re.Pattern[str], text: str) -> re.Match[str] | None:
    matches = list(pattern.finditer(text))
    return matches[-1] if matches else None


def _final_block(text: str) -> str:
    headers = list(re.finditer(r"^Results of .+$", text, re.M))
    return text[headers[-1].start() :] if headers else text


def _parse_games(text: str) -> tuple[str | None, bool]:
    row_match = _last(_GAMES_ROW, text)
    if row_match is None:
        return None, False

    row = row_match.group(0).strip()
    count_match = re.match(r"^Games:\s*(\d+)", row)
    games_str = count_match.group(1) if count_match else None
    summary_match = _GAMES_SUMMARY.fullmatch(row)
    if summary_match is None:
        return games_str, False

    games, wins, losses, draws = map(int, summary_match.group(1, 2, 3, 4))
    return str(games), games > 0 and wins + losses + draws == games


def _parse_llr(
    text: str,
) -> tuple[str | None, float | None, float | None, float | None]:
    llr_matches = list(_LLR_LINE.finditer(text))
    if not llr_matches:
        return None, None, None, None
    raw = llr_matches[-1].group(1).strip()
    summary_match = _LLR_SUMMARY.fullmatch(raw)
    if summary_match:
        llr_str, pct_str, lower_str, upper_str, elo0_str, elo1_str = summary_match.groups()
        try:
            llr_val, pct_val, lower_val, upper_val, elo0_val, elo1_val = map(
                float, (llr_str, pct_str, lower_str, upper_str, elo0_str, elo1_str)
            )
            if (
                all(
                    math.isfinite(value)
                    for value in (
                        llr_val,
                        pct_val,
                        lower_val,
                        upper_val,
                        elo0_val,
                        elo1_val,
                    )
                )
                and lower_val < upper_val
            ):
                return llr_str, llr_val, lower_val, upper_val
        except ValueError:
            pass
        return llr_str, None, None, None
    fallback_match = _LLR_FALLBACK.match(raw)
    llr_str = fallback_match.group(1) if fallback_match else None
    return llr_str, None, None, None


def summarize(text: str) -> tuple[int, str]:
    block = _final_block(text)
    accepted = _last(_ACCEPTED, block)
    games_str, valid_games = _parse_games(block)
    elo = _last(_ELO, block)
    llr_str, llr_val, lower_val, upper_val = _parse_llr(block)
    parts = [
        f"games={games_str if games_str is not None else '?'}",
        f"llr={llr_str if llr_str is not None else '?'}",
        f"elo={elo[1]}±{elo[2]}" if elo else "elo=?",
    ]
    if (
        accepted is not None
        and valid_games
        and llr_val is not None
        and lower_val is not None
        and upper_val is not None
    ):
        hypothesis = accepted[1]
        if hypothesis == "1" and llr_val >= upper_val + 0.01:
            return 0, "SPRT H1 aceita: " + " ".join(parts)
        if hypothesis == "0" and llr_val <= lower_val - 0.01:
            return 1, "SPRT H0 aceita: " + " ".join(parts)
    return 2, "SPRT inconclusivo: " + " ".join(parts)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    code, line = summarize(Path(args[0]).read_text(encoding="utf-8", errors="replace"))
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())

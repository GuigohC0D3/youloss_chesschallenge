"""Log .log por lance (FAQ item 9), com flush e fsync a cada linha."""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from controller.engine_client import SearchInfo

_UCI = r"[a-h][1-8][a-h][1-8][qrbn]?"
LINE_RE = re.compile(
    rf"^move=\d+ color=(?:white|black) uci={_UCI} (?:"
    rf"depth=\d+ seldepth=\d+ nodes=\d+ "
    rf"eval=(?:[+-]\d+\.\d{{2}}|-?M\d+|book|forced|fallback|none) "
    rf'pv="(?:{_UCI}(?: {_UCI})*)?" time_ms=\d+ source=(?:engine|book|forced|fallback|ponderhit)'
    rf"|time_ms=\d+ source=opponent)$"
)


def slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-") or "adversario"


def log_path(logs_dir: Path, opponent: str, game: int, day: date) -> Path:
    return Path(logs_dir) / f"{day.isoformat()}_{slug(opponent)}_g{game}.log"


def format_eval(score_cp: int | None, score_mate: int | None) -> str:
    if score_mate is not None:
        return f"M{score_mate}" if score_mate > 0 else f"-M{-score_mate}"
    if score_cp is None:
        return "none"
    return f"{score_cp / 100:+.2f}"


class GameLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._f = open(self.path, "a", encoding="utf-8", newline="\n")

    def _write(self, line: str) -> None:
        self._f.write(line + "\n")
        self._f.flush()
        os.fsync(self._f.fileno())

    def header(self, **fields: object) -> None:
        parts = [
            f'{k}="{v}"' if " " in str(v) else f"{k}={v}" for k, v in fields.items()
        ]
        self._write("# " + " ".join(parts))

    def note(self, text: str) -> None:
        self._write(f"# {text}")

    def our_move(
        self,
        move_no: int,
        color: str,
        uci: str,
        source: str,
        time_ms: int,
        info: SearchInfo | None = None,
    ) -> None:
        if info is not None:
            search = (
                f"depth={info.depth} seldepth={info.seldepth} nodes={info.nodes} "
                f"eval={format_eval(info.score_cp, info.score_mate)} "
                f'pv="{" ".join(info.pv)}"'
            )
        else:
            search = f'depth=0 seldepth=0 nodes=0 eval={source} pv="{uci}"'
        self._write(
            f"move={move_no} color={color} uci={uci} {search} time_ms={time_ms} source={source}"
        )

    def opponent_move(self, move_no: int, color: str, uci: str, time_ms: int) -> None:
        self._write(
            f"move={move_no} color={color} uci={uci} time_ms={time_ms} source=opponent"
        )

    def result(self, result: str, reason: str) -> None:
        self._write(f"# result={result} reason={reason}")

    def close(self) -> None:
        if not self._f.closed:
            self._f.close()


def check_log(path: str | Path) -> list[str]:
    """Linhas fora do formato (comentários `# ` são aceitos)."""
    bad = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not (line.startswith("# ") or LINE_RE.match(line)):
            bad.append(f"{n}: {line}")
    return bad


def _main(argv: list[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else argv
    failed = False
    for path in paths:
        for bad in check_log(path):
            print(f"{path}:{bad}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_main())

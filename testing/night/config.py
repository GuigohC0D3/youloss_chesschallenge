"""Run specification for the chess.com night harness."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE = Path.home() / ".local" / "share" / "youloss-night" / "chrome"


def default_run_dir(now: datetime | None = None) -> Path:
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    return ROOT / "logs" / "night" / stamp


@dataclass
class RunSpec:
    """Everything the runner needs to start a series.

    Values are deliberately plain: one JSON-serializable spec, one run folder,
    no hidden state outside the profile directory.
    """

    # Series shape
    bot: str = "Expert"
    tc: str = "3+0"
    color_mode: str = "alternate"  # alternate | white | black
    max_games: int = 0  # 0 = until max_hours or stop
    max_hours: float = 8.0
    attach: bool = False  # take over a game the operator started by hand
    dry_run: bool = False

    # Engine
    engine: Path = ROOT / "bin" / "stockfish"
    threads: int | None = None
    hash_mb: int | None = None
    move_overhead_ms: int = 80
    max_move_ms: int = 2500
    book: Path | None = ROOT / "assets" / "book.bin"
    syzygy: Path = ROOT / "assets" / "syzygy"

    # Browser
    profile_dir: Path = DEFAULT_PROFILE
    cdp_port: int = 9222
    chrome_path: Path = Path(
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )
    keep_browser: bool = True

    # Timing and recovery
    poll_ms: int = 100
    move_timeout_s: float = 45.0
    click_timeout_s: float = 8.0
    login_timeout_s: float = 900.0
    max_consecutive_failures: int = 3
    max_attempts_per_game: int = 3
    pause_between_games_s: float = 0.5

    # Output
    out_dir: Path = field(default_factory=default_run_dir)

    def __post_init__(self) -> None:
        self.engine = Path(self.engine).expanduser()
        self.book = Path(self.book).expanduser() if self.book else None
        self.syzygy = Path(self.syzygy).expanduser()
        self.profile_dir = Path(self.profile_dir).expanduser()
        self.chrome_path = Path(self.chrome_path).expanduser()
        self.out_dir = Path(self.out_dir).expanduser()
        if self.color_mode not in ("alternate", "white", "black"):
            raise ValueError(f"color_mode inválido: {self.color_mode!r}")
        if self.max_games < 0:
            raise ValueError("max_games não pode ser negativo")
        if self.max_hours < 0:
            raise ValueError("max_hours não pode ser negativo")
        # max_games=0 with max_hours=0 is explicit unlimited mode.
        if self.move_overhead_ms < 0:
            raise ValueError("move_overhead_ms não pode ser negativo")
        if self.max_move_ms < 0:
            raise ValueError("max_move_ms não pode ser negativo")

    def to_dict(self) -> dict[str, object]:
        return {
            "bot": self.bot,
            "tc": self.tc,
            "color_mode": self.color_mode,
            "max_games": self.max_games,
            "max_hours": self.max_hours,
            "attach": self.attach,
            "dry_run": self.dry_run,
            "engine": str(self.engine),
            "threads": self.threads,
            "hash_mb": self.hash_mb,
            "move_overhead_ms": self.move_overhead_ms,
            "max_move_ms": self.max_move_ms,
            "book": str(self.book) if self.book else None,
            "syzygy": str(self.syzygy),
            "profile_dir": str(self.profile_dir),
            "cdp_port": self.cdp_port,
            "poll_ms": self.poll_ms,
            "move_timeout_s": self.move_timeout_s,
            "click_timeout_s": self.click_timeout_s,
            "login_timeout_s": self.login_timeout_s,
            "max_consecutive_failures": self.max_consecutive_failures,
            "max_attempts_per_game": self.max_attempts_per_game,
            "pause_between_games_s": self.pause_between_games_s,
            "out_dir": str(self.out_dir),
        }

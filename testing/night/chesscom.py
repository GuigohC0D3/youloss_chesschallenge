"""Chess.com adapter over Chrome DevTools Protocol.

The only module that knows chess.com exists. It owns the browser connection,
the bot-selection flow, the live board snapshot, and real mouse clicks.
"""

from __future__ import annotations

import re
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chess
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Locator,
    Page,
    Playwright,
    sync_playwright,
)

from testing.night.board import board_from_pieces
from testing.night.config import RunSpec

BOT_URL = "https://www.chess.com/play/computer"


class ChessComError(RuntimeError):
    pass


class LoginRequired(ChessComError):
    pass


class MoveRejected(ChessComError):
    pass


SNAPSHOT_JS = r"""
() => {
  const txt = (e) => (e && (e.innerText || e.textContent) || "").trim();
  const board = document.querySelector('wc-chess-board#board-play-computer')
             || document.querySelector('wc-chess-board')
             || document.querySelector('chess-board')
             || document.querySelector('#board-single');
  const moveList = document.querySelector('wc-simple-move-list')
                || document.querySelector('wc-move-list')
                || document.querySelector('.move-list');
  const nodes = moveList ? [...moveList.querySelectorAll('.node')] : [];
  const sans = nodes.map(n => {
    const hit = n.querySelector('.node-highlight-content');
    const fig = n.querySelector('[data-figurine]');
    const icon = n.querySelector('.icon-font-chess');
    let figurine = fig ? (fig.getAttribute('data-figurine') || '') : '';
    if (!figurine && icon) {
      const cls = String(icon.className || '').toLowerCase();
      for (const [name, letter] of [
        ['knight', 'N'], ['bishop', 'B'], ['rook', 'R'],
        ['queen', 'Q'], ['king', 'K']
      ]) {
        if (cls.includes(name)) { figurine = letter; break; }
      }
    }
    let text = txt(hit || n).replace(/\s+/g, ' ').trim();
    if (figurine && !text.startsWith(figurine)) {
      text = figurine + text;
    }
    return text;
  }).filter(Boolean);
  const stamps = moveList
    ? [...moveList.querySelectorAll('[data-move-list-el="timestamp"]')].map(e => ({
        ply: parseInt(e.getAttribute('data-ply') || '0', 10),
        time: parseFloat(e.getAttribute('data-time') || '0'),
        text: txt(e)
      }))
    : [];
  const rows = [...document.querySelectorAll('.player-row-component')].map(r => ({
    top: r.classList.contains('player-row-top'),
    username: txt(r.querySelector('[data-test-element="user-tagline-username"]')),
    clock: txt(r.querySelector('.player-row-move-time, .move-time-time')),
    text: txt(r)
  }));
  let orientation = 'white';
  if (board) {
    const one = [...board.querySelectorAll('.coordinates text')].find(e => txt(e) === '1');
    const eight = [...board.querySelectorAll('.coordinates text')].find(e => txt(e) === '8');
    if (one && eight) {
      orientation = one.getBoundingClientRect().y > eight.getBoundingClientRect().y ? 'white' : 'black';
    } else if (board.classList.contains('flipped')) {
      orientation = 'black';
    }
  }
  let rect = null;
  if (board) {
    const r = board.getBoundingClientRect();
    rect = {x: r.x, y: r.y, w: r.width, h: r.height};
  }
  const modal = document.querySelector('.game-over-modal, [class*="game-over"], .modal-content');
  const modalVisible = modal && (modal.offsetParent !== null || modal.getClientRects().length > 0);
  const member = document.querySelector('a[href*="/member/"]');
  const buttons = [...document.querySelectorAll('button,[role=button],a')]
    .map(e => ({text: txt(e), cls: String(e.className || '')}))
    .filter(x => x.text);
  const promotionEl = [...document.querySelectorAll(
    '.promotion-window, [class*="promotion-window"]'
  )].find(e => e.offsetParent !== null || e.getClientRects().length > 0);
  const promotion = !!promotionEl;
  return {
    url: location.href,
    title: document.title,
    board: !!board,
    boardRect: rect,
    orientation,
    sans,
    stamps,
    rows,
    pieces: board ? [...board.querySelectorAll('.piece')].map(e => String(e.className)) : [],
    modalText: modalVisible ? txt(modal).slice(0, 1200) : '',
    body: (document.body.innerText || '').slice(0, 5000),
    member: member ? {text: txt(member), href: member.getAttribute('href') || ''} : null,
    buttons,
    promotion
  };
}
"""


@dataclass
class Snapshot:
    url: str
    title: str
    board: bool
    board_rect: dict[str, float] | None
    orientation: str
    sans: list[str]
    stamps: list[dict[str, Any]]
    rows: list[dict[str, Any]]
    pieces: list[str]
    modal_text: str
    body: str
    member: dict[str, str] | None
    buttons: list[dict[str, str]]
    promotion: bool

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> Snapshot:
        return cls(
            url=raw.get("url", ""),
            title=raw.get("title", ""),
            board=bool(raw.get("board")),
            board_rect=raw.get("boardRect"),
            orientation=raw.get("orientation", "white"),
            sans=list(raw.get("sans") or []),
            stamps=list(raw.get("stamps") or []),
            rows=list(raw.get("rows") or []),
            pieces=list(raw.get("pieces") or []),
            modal_text=raw.get("modalText", ""),
            body=raw.get("body", ""),
            member=raw.get("member"),
            buttons=list(raw.get("buttons") or []),
            promotion=bool(raw.get("promotion")),
        )

    @property
    def ply(self) -> int:
        return len(self.sans)

    @property
    def our_color(self) -> chess.Color:
        return chess.WHITE if self.orientation == "white" else chess.BLACK

    @property
    def our_username(self) -> str:
        for row in reversed(self.rows):
            if not row.get("top"):
                return str(row.get("username") or "")
        return ""

    def clock_ms(self, color: chess.Color) -> int | None:
        for row in self.rows:
            top = bool(row.get("top"))
            row_color = (
                chess.BLACK if (self.orientation == "white") == top else chess.WHITE
            )
            if row_color == color:
                return parse_clock(str(row.get("clock") or ""))
        return None

    def spent_ms(self, ply: int) -> int | None:
        """chess.com stores per-move time in tenths of a second."""
        for stamp in self.stamps:
            if int(stamp.get("ply") or 0) == ply:
                value = stamp.get("time")
                if isinstance(value, (int, float)):
                    return int(round(float(value) * 100))
        return None


def parse_clock(text: str) -> int | None:
    match = re.search(r"(\d+):(\d{2})(?:\.(\d+))?", text or "")
    if not match:
        return None
    minutes = int(match.group(1))
    seconds = int(match.group(2))
    fraction = match.group(3)
    ms = (minutes * 60 + seconds) * 1000
    if fraction:
        ms += int(float("0." + fraction) * 1000)
    return ms


def is_standard_start(snap: Snapshot) -> bool:
    if len(snap.pieces) != 32:
        return False
    try:
        rendered = board_from_pieces(snap.pieces, turn=chess.WHITE)
    except Exception:
        return False
    return rendered.board_fen() == chess.Board().board_fen()


def ensure_chrome(spec: RunSpec, log_path: Path | None = None) -> None:
    """Attach to CDP, launching a dedicated Chrome profile when absent."""
    endpoint = f"http://127.0.0.1:{spec.cdp_port}/json/version"
    try:
        with urllib.request.urlopen(endpoint, timeout=1.5) as response:
            if response.status == 200:
                return
    except (urllib.error.URLError, OSError, TimeoutError):
        pass

    spec.profile_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not spec.chrome_path.exists():
        raise ChessComError(f"Chrome não encontrado em {spec.chrome_path}")
    log_path = log_path or (spec.out_dir / "chrome.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = open(log_path, "a", encoding="utf-8")
    subprocess.Popen(
        [
            str(spec.chrome_path),
            f"--user-data-dir={spec.profile_dir}",
            f"--remote-debugging-port={spec.cdp_port}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--window-size=1440,1000",
            BOT_URL,
        ],
        stdout=log,
        stderr=log,
        start_new_session=True,
    )
    deadline = time.monotonic() + 30.0
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(endpoint, timeout=1.0) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, OSError, TimeoutError):
            time.sleep(0.25)
    raise ChessComError(f"Chrome não abriu CDP em {endpoint}")


class ChessComSession:
    def __init__(self, spec: RunSpec):
        self.spec = spec
        self._pw: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    # --- connection --------------------------------------------------------

    def connect(self) -> None:
        ensure_chrome(self.spec, self.spec.out_dir / "chrome.log")
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.connect_over_cdp(
            f"http://127.0.0.1:{self.spec.cdp_port}"
        )
        if not self.browser.contexts:
            raise ChessComError("Chrome sem contexto de navegador")
        self.context = self.browser.contexts[0]
        pages = list(self.context.pages)
        self.page = next(
            (p for p in pages if "chess.com" in p.url),
            pages[0] if pages else self.context.new_page(),
        )
        self.page.set_default_timeout(15_000)
        try:
            # Kill board animations so a click is accepted on the next poll.
            self.page.add_style_tag(
                content="wc-chess-board{--move-animation-duration:0ms !important;}"
            )
        except Exception:
            pass

    def close(self) -> None:
        # Deliberately do not close the browser: the profile stays logged in
        # and a crashed runner can reconnect without a new login.
        if self.browser is not None:
            try:
                self.browser.close()
            except Exception:
                pass
        if self._pw is not None:
            try:
                self._pw.stop()
            except Exception:
                pass
        self.browser = None
        self.context = None
        self.page = None
        self._pw = None

    # --- navigation and state ---------------------------------------------

    def goto(self, url: str) -> None:
        assert self.page is not None
        self.page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        self.page.wait_for_timeout(1500)

    def snapshot(self) -> Snapshot:
        assert self.page is not None
        return Snapshot.from_raw(self.page.evaluate(SNAPSHOT_JS))

    def screenshot(self, path: Path) -> Path:
        assert self.page is not None
        path.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def login_state(self) -> str:
        snap = self.snapshot()
        if any(part in snap.url for part in ("/register", "/login")):
            return "logged_out"
        if "Create Your Chess.com Account" in snap.body:
            return "logged_out"
        if snap.member is not None:
            return "logged_in"
        if "Log In" in snap.body and "Log Out" not in snap.body:
            return "logged_out"
        return "unknown"

    def wait_for_login(self, timeout_s: float | None = None, progress=None) -> None:
        timeout_s = self.spec.login_timeout_s if timeout_s is None else timeout_s
        self.goto(BOT_URL)
        deadline = time.monotonic() + timeout_s
        last = 0.0
        while time.monotonic() < deadline:
            state = self.login_state()
            if state == "logged_in":
                return
            if progress is not None and time.monotonic() - last > 5:
                progress(state)
                last = time.monotonic()
            time.sleep(2.0)
        raise LoginRequired(
            "login não detectado; entre na conta descartável na janela do Chrome e repita"
        )

    def ensure_logged_in(self, navigate: bool = True) -> None:
        if navigate:
            self.goto(BOT_URL)
        if self.login_state() != "logged_in":
            raise LoginRequired(
                "conta não autenticada; rode `python -m testing.night login` e entre na conta descartável"
            )
        assert self.page is not None
        if navigate:
            self.page.wait_for_selector(
                ".bot-group-accordion-component", timeout=20_000
            )

    # --- bot selection -----------------------------------------------------

    def _engine_accordion(self) -> Locator:
        assert self.page is not None
        return (
            self.page.locator(".bot-group-accordion-component")
            .filter(
                has=self.page.locator(
                    ".bot-group-accordion-sectionTitle", has_text="Engine"
                )
            )
            .first
        )

    def _open_engine_accordion(self) -> Locator:
        assert self.page is not None
        self.page.wait_for_selector(".bot-group-accordion-component", timeout=20_000)
        accordion = self._engine_accordion()
        toggle = accordion.locator(".bot-group-accordion-toggleClickArea").first
        for _ in range(2):
            if "Expanded" in (toggle.get_attribute("class") or ""):
                break
            toggle.scroll_into_view_if_needed()
            self.page.wait_for_timeout(200)
            box = toggle.bounding_box()
            if box is None:
                raise ChessComError("accordion Engine sem caixa clicável")
            self.page.mouse.click(
                box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            )
            try:
                self.page.wait_for_selector(
                    "input.slider-input", state="attached", timeout=5_000
                )
                break
            except Exception:
                continue
        return accordion

    def select_engine_3200(self) -> None:
        assert self.page is not None
        accordion = self._open_engine_accordion()
        slider = accordion.locator("input.slider-input").first
        if slider.count() == 0:
            raise ChessComError("slider do Engine não encontrado")
        value = slider.evaluate(
            """el => {
                el.value = el.max || '25';
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
                return el.value;
            }"""
        )
        if str(value) != "25":
            raise ChessComError(f"slider do Engine não chegou a 25 (valor={value!r})")
        self.page.wait_for_timeout(700)

    def select_time_control(self, tc: str) -> None:
        assert self.page is not None
        self.page.wait_for_selector(
            ".time-selector-button-button", state="attached", timeout=15_000
        )
        label = tc.replace("+", " + ").strip()
        clicked = self.page.evaluate(
            """label => {
                const b = [...document.querySelectorAll('button')]
                    .find(x => (x.innerText || '').trim() === label);
                if (!b) return false;
                b.click();
                return true;
            }""",
            label,
        )
        if not clicked:
            raise ChessComError(f"controle de tempo {label!r} não encontrado")
        self.page.wait_for_timeout(500)

    def _select_side_if_available(self, color_mode: str) -> str:
        assert self.page is not None
        if color_mode not in ("white", "black"):
            return "default"
        options = self.page.locator(".play-side-selector-option")
        wanted = f"{color_mode}--sm.svg"
        for index in range(options.count()):
            option = options.nth(index)
            style = option.get_attribute("style") or ""
            if wanted not in style:
                continue
            option.click()
            self.page.wait_for_timeout(350)
            if option.get_attribute("data-playing-as-selected") != "true":
                raise ChessComError(f"seletor de lado {color_mode} não ficou ativo")
            return color_mode
        raise ChessComError(f"seletor de lado {color_mode} não encontrado")

    def _tc_ready(self) -> bool:
        assert self.page is not None
        try:
            texts = self.page.locator(".time-selector-button-button").all_inner_texts()
        except Exception:
            return False
        return any(text.strip() for text in texts)

    def _prepare_selection(self) -> None:
        assert self.page is not None
        if self._tc_ready():
            return
        # An active game or a "Continue" preview hides usable time controls.
        for label in (r"^New Game$", r"^New Bot$", r"^Continue$"):
            if self.click_button_text(label):
                self.page.wait_for_timeout(1000)
                self.click_button_text(r"^(Resign|Abandon|Desistir|Yes|Sim|Confirm)$")
                self.page.wait_for_timeout(800)
                if self._tc_ready():
                    return
        raise ChessComError(
            "não foi possível abrir a seleção de tempo; feche a partida ativa manualmente"
        )

    def start_game(self, color_mode: str = "alternate") -> Snapshot:
        assert self.page is not None
        url = self.page.url
        if "/play/computer" in url:
            self.ensure_logged_in(navigate=False)
        else:
            self.ensure_logged_in(navigate=True)
        self._prepare_selection()
        self.select_engine_3200()
        self.select_time_control(self.spec.tc)
        side = self._select_side_if_available(color_mode)
        cta = self.page.locator(".bot-selection-cta-button-button").first
        if cta.count() == 0:
            raise ChessComError("botão Play do bot não encontrado")
        cta.click()
        snapshot = self.wait_for_board()
        deadline = time.monotonic() + 6.0
        while time.monotonic() < deadline:
            if is_standard_start(snapshot):
                break
            time.sleep(0.25)
            snapshot = self.snapshot()
        if not is_standard_start(snapshot):
            raise ChessComError(
                "a partida não começou da posição inicial padrão; selecione Standard e tente de novo"
            )
        if color_mode in ("white", "black"):
            expected = chess.WHITE if color_mode == "white" else chess.BLACK
            if snapshot.our_color != expected:
                raise ChessComError(
                    f"lado escolhido {color_mode}, mas o tabuleiro abriu em "
                    f"{snapshot.orientation}"
                )
        return snapshot

    def wait_for_board(self, timeout_s: float = 30.0) -> Snapshot:
        deadline = time.monotonic() + timeout_s
        last_error = ""
        while time.monotonic() < deadline:
            snap = self.snapshot()
            if snap.board and snap.board_rect and snap.sans is not None:
                if "/play/computer/" in snap.url or snap.rows:
                    return snap
            last_error = snap.url
            time.sleep(0.25)
        raise ChessComError(f"tabuleiro não apareceu (url={last_error})")

    # --- live game ---------------------------------------------------------

    def wait_for_ply(self, previous_ply: int, timeout_s: float) -> Snapshot:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            snap = self.snapshot()
            if snap.ply > previous_ply or snap.modal_text:
                # The figurine icon can land a frame after the SAN text.
                time.sleep(0.2)
                return self.snapshot()
            time.sleep(self.spec.poll_ms / 1000.0)
        raise TimeoutError(f"sem lance novo em {timeout_s:.1f}s (ply={previous_ply})")

    def _square_xy(
        self, rect: dict[str, float], orientation: str, square: chess.Square
    ) -> tuple[float, float]:
        file_no = chess.square_file(square)
        rank_no = chess.square_rank(square)
        size = rect["w"] / 8.0
        if orientation == "white":
            x = rect["x"] + (file_no + 0.5) * size
            y = rect["y"] + (7 - rank_no + 0.5) * size
        else:
            x = rect["x"] + (7 - file_no + 0.5) * size
            y = rect["y"] + (rank_no + 0.5) * size
        return x, y

    def _click_square(
        self, rect: dict[str, float], orientation: str, square: chess.Square
    ) -> None:
        assert self.page is not None
        x, y = self._square_xy(rect, orientation, square)
        self.page.mouse.click(x, y)
        self.page.wait_for_timeout(120)

    def _drag_square(
        self,
        rect: dict[str, float],
        orientation: str,
        source: chess.Square,
        target: chess.Square,
    ) -> None:
        assert self.page is not None
        x1, y1 = self._square_xy(rect, orientation, source)
        x2, y2 = self._square_xy(rect, orientation, target)
        self.page.mouse.move(x1, y1)
        self.page.mouse.down()
        self.page.mouse.move(x2, y2, steps=12)
        self.page.mouse.up()

    _PROMO_LETTER = {
        chess.QUEEN: "q",
        chess.ROOK: "r",
        chess.BISHOP: "b",
        chess.KNIGHT: "n",
    }

    def _handle_promotion(
        self,
        promotion: int | None,
        color_prefix: str,
        timeout_s: float = 2.0,
    ) -> None:
        assert self.page is not None
        if promotion is None:
            return
        letter = self._PROMO_LETTER.get(promotion, "q")
        token = f"{color_prefix}{letter}"
        deadline = time.monotonic() + timeout_s
        detected = False
        while time.monotonic() < deadline:
            if self.snapshot().promotion:
                detected = True
                break
            time.sleep(0.1)
        if not detected:
            return
        # Keep one diagnostic sample in case chess.com changes the picker.
        try:
            stamp = time.strftime("%Y%m%d-%H%M%S")
            diag = self.spec.out_dir / "diag"
            diag.mkdir(parents=True, exist_ok=True)
            (diag / f"promotion_{stamp}.html").write_text(
                self.page.content(), encoding="utf-8"
            )
            self.page.screenshot(path=str(diag / f"promotion_{stamp}.png"))
        except Exception:
            pass
        selectors = (
            f".promotion-window .promotion-piece.{token}",
            f".promotion-window .{token}",
            f".promotion-piece.{token}",
            f'.promotion-window [data-piece="{letter}"]',
            f'[class*="promotion"] [data-piece="{letter}"]',
        )
        for selector in selectors:
            locator = self.page.locator(selector)
            for index in range(min(locator.count(), 4)):
                item = locator.nth(index)
                try:
                    if item.is_visible():
                        item.click(timeout=1500)
                        return
                except Exception:
                    continue
        clicked = self.page.evaluate(
            """token => {
                const nodes = [...document.querySelectorAll('[data-piece], [class*="promotion"] *')];
                const hit = nodes.find(e => {
                    const c = String(e.className || '').toLowerCase();
                    return c.split(/\\s+/).includes(token) &&
                           (e.offsetParent || e.getClientRects().length);
                });
                if (!hit) return false;
                hit.click();
                return true;
            }""",
            token,
        )
        if not clicked:
            self.page.keyboard.press(letter)

    def play(self, move: chess.Move, timeout_s: float | None = None) -> Snapshot:
        assert self.page is not None
        timeout_s = self.spec.click_timeout_s if timeout_s is None else timeout_s
        before = self.snapshot()
        if not before.board_rect:
            raise MoveRejected("tabuleiro sem geometria para clique")
        orientation = before.orientation
        self._click_square(before.board_rect, orientation, move.from_square)
        self._click_square(before.board_rect, orientation, move.to_square)
        self._handle_promotion(
            move.promotion, "w" if before.our_color == chess.WHITE else "b"
        )
        try:
            return self.wait_for_ply(before.ply, timeout_s)
        except TimeoutError:
            # Some board states ignore the second click; retry as a drag.
            self._drag_square(
                before.board_rect, orientation, move.from_square, move.to_square
            )
            self._handle_promotion(
                move.promotion, "w" if before.our_color == chess.WHITE else "b"
            )
            try:
                return self.wait_for_ply(before.ply, timeout_s)
            except TimeoutError as exc:
                raise MoveRejected(
                    f"lance {move.uci()} não foi aceito pelo tabuleiro"
                ) from exc

    def click_button_text(self, pattern: str) -> bool:
        assert self.page is not None
        regex = re.compile(pattern, re.IGNORECASE)
        for button in self.page.locator("button, [role=button], a").all():
            try:
                text = (button.inner_text() or "").strip()
            except Exception:
                continue
            if text and regex.search(text):
                try:
                    button.click(timeout=3000)
                    return True
                except Exception:
                    continue
        return False

    def new_game(self, color_mode: str = "alternate") -> Snapshot:
        assert self.page is not None
        if self.click_button_text(
            r"^(Rematch|Play Again|New Game|Next Game|Jogar novamente)$"
        ):
            self.page.wait_for_timeout(1500)
            for _ in range(30):
                snap = self.snapshot()
                if (
                    snap.board
                    and snap.rows
                    and snap.our_username
                    and is_standard_start(snap)
                ):
                    return snap
                time.sleep(0.25)
        return self.start_game(color_mode)

    def resign(self) -> None:
        assert self.page is not None
        for selector in (
            'button[aria-label="Resign"]',
            'button[aria-label*="Resign" i]',
            'button[aria-label*="Abandon" i]',
            '[data-cy="resign"]',
        ):
            locator = self.page.locator(selector)
            if locator.count():
                try:
                    locator.first.click(timeout=3000)
                    self.page.wait_for_timeout(800)
                    break
                except Exception:
                    continue
        else:
            try:
                self.click_button_text(r"^(Resign|Abandonar|Desistir)$")
            except Exception:
                pass
        self.click_button_text(r"^(Resign|Yes|Sim|Confirm|Abandonar)$")

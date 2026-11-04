#!/usr/bin/env python3
"""Painel local da triagem: placar, tabuleiro ao vivo e partidas terminadas.

Somente leitura. Le o scoreboard.json do SCREENING_DIR, o run mais recente
em logs/sprt (match.pgn + uci.log gravado com LIVE_LOG=1) e serve HTML em
http://127.0.0.1:PORT. Uso:

    .venv/bin/python testing/live_view.py --screening-dir logs/screening/devbrain-s2-20261006
"""
from __future__ import annotations

import argparse
import html
import io
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import chess
import chess.pgn
import chess.svg

ROOT = Path(__file__).resolve().parents[1]
LABELS = {"tm": "devport (candidato)", "sf": "frozen-19"}
TAIL_BYTES = 256 * 1024

POSITION_RE = re.compile(r" (\w+) <--- position (startpos|fen (.+?))(?: moves (.*))?$")
GO_RE = re.compile(r" (\w+) <--- go wtime (\d+) btime (\d+)")
SCORE_RE = re.compile(r" (\w+) ---> info .*?depth (\d+) .*?score (cp|mate) (-?\d+)")


def tail_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    with path.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - TAIL_BYTES))
        return f.read().decode("utf-8", "replace").splitlines()


def latest_rundir(sprt_dir: Path) -> Path | None:
    runs = [p for p in sprt_dir.glob("tm_*") if p.is_dir()]
    return max(runs, key=lambda p: p.stat().st_mtime, default=None)


def live_state(rundir: Path) -> dict | None:
    """Ultima posicao enviada a um motor, relogios e avaliacoes recentes."""
    state: dict = {}
    scores: dict[str, str] = {}
    for line in tail_lines(rundir / "uci.log"):
        if m := POSITION_RE.search(line):
            state["to_move"], fen, moves = m.group(1), m.group(3), m.group(4)
            state["fen"], state["moves"] = fen, (moves or "").split()
        elif m := GO_RE.search(line):
            state["wtime"], state["btime"] = int(m.group(2)), int(m.group(3))
        elif m := SCORE_RE.search(line):
            kind, val = m.group(3), int(m.group(4))
            scores[m.group(1)] = f"{val / 100:+.2f} (d{m.group(2)})" if kind == "cp" else f"mate {val} (d{m.group(2)})"
    if "moves" not in state:
        return None
    board = chess.Board(state["fen"]) if state["fen"] else chess.Board()
    for uci in state["moves"]:
        board.push_uci(uci)
    state["board"], state["scores"] = board, scores
    return state


def finished_games(rundir: Path) -> list[chess.pgn.Game]:
    pgn = rundir / "match.pgn"
    if not pgn.is_file():
        return []
    games, stream = [], io.StringIO(pgn.read_text(encoding="utf-8", errors="replace"))
    while (game := chess.pgn.read_game(stream)) is not None:
        games.append(game)
    return games


def all_rundirs(sprt_dir: Path) -> list[Path]:
    return sorted((p for p in sprt_dir.glob("tm_*") if p.is_dir()), key=lambda p: p.stat().st_mtime)


def clock(ms: int | None) -> str:
    if ms is None:
        return "–"
    s = ms // 1000
    return f"{s // 60}:{s % 60:02d}"


def label(name: str) -> str:
    return LABELS.get(name, name)


def svg(board: chess.Board, size: int = 440) -> str:
    last = board.peek() if board.move_stack else None
    check = board.king(board.turn) if board.is_check() else None
    return chess.svg.board(board, lastmove=last, check=check, size=size)


STYLE = """
:root{--bg:#f6f5f2;--fg:#1d1d1f;--muted:#6b6b70;--card:#fff;--line:#e3e1dc;--acc:#2f6f4f}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#ececee;--muted:#9a9aa0;--card:#1e1e22;--line:#2e2e33;--acc:#6fc79a}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 -apple-system,system-ui,sans-serif}
main{max-width:1100px;margin:0 auto;padding:20px 16px}
h1{font-size:20px;margin:0 0 4px}h2{font-size:15px;margin:0 0 10px;color:var(--muted);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;margin-top:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.kpis{display:flex;gap:18px;flex-wrap:wrap}.kpi b{display:block;font-size:24px}.kpi span{color:var(--muted);font-size:12px}
table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:5px 4px;border-bottom:1px solid var(--line);text-align:left}
a{color:var(--acc)}.muted{color:var(--muted)}.mono{font-family:ui-monospace,Menlo,monospace;font-size:12px}
svg{max-width:100%;height:auto}.nav a{margin-right:10px}
"""


def page(title: str, body: str, refresh: bool) -> bytes:
    meta = '<meta http-equiv="refresh" content="3">' if refresh else ""
    return (f"<!doctype html><html lang=pt-br><head><meta charset=utf-8>"
            f"<meta name=viewport content='width=device-width,initial-scale=1'>{meta}"
            f"<title>{html.escape(title)}</title><style>{STYLE}</style></head>"
            f"<body><main>{body}</main></body></html>").encode()


class Viewer:
    def __init__(self, screening_dir: Path, sprt_dir: Path):
        self.screening_dir, self.sprt_dir = screening_dir, sprt_dir

    def scoreboard(self) -> dict:
        try:
            return json.loads((self.screening_dir / "scoreboard.json").read_text())
        except (OSError, ValueError):
            return {}

    def index(self) -> bytes:
        sb = self.scoreboard()
        rundir = latest_rundir(self.sprt_dir)
        batch_log = "\n".join(tail_lines(rundir / "match.log")) if rundir else ""
        planned = re.findall(r"Started game \d+ of (\d+)", batch_log)
        batch_done = len(re.findall(r"^Finished game", batch_log, re.M))
        wdl = [0, 0, 0]  # devport: vitorias, empates, derrotas no lote atual
        for g in finished_games(rundir) if rundir else []:
            res, tm_white = g.headers.get("Result"), g.headers.get("White") == "tm"
            if res == "1/2-1/2":
                wdl[1] += 1
            elif res in ("1-0", "0-1"):
                wdl[0 if (res == "1-0") == tm_white else 2] += 1
        kpis = "".join(
            f"<div class=kpi><b>{html.escape(str(v))}</b><span>{k}</span></div>"
            for k, v in [
                ("partidas contadas", f"{sb.get('total_games', 0)} / 400"),
                ("score devport", f"{sb.get('score_pct', 0.0)}%"),
                ("V / E / D contados", f"{sb.get('youloss_wins', 0)} / {sb.get('draws', 0)} / {sb.get('baseline_wins', 0)}"),
                ("lotes ok / rejeitados", f"{sb.get('batches_completed', 0)} / {sb.get('batches_failed', 0)}"),
                ("lote atual (conta ao fechar)", f"{batch_done} / {planned[-1] if planned else '–'}"),
                ("V / E / D parcial do lote", f"{wdl[0]} / {wdl[1]} / {wdl[2]}"),
            ])
        incidents = "".join(
            f"<li class=mono>{html.escape(i.get('time', '')[:19])} — {html.escape(i.get('reason', ''))}</li>"
            for i in sb.get("incidents", [])[-5:])
        body = (f"<h1>S2 — devport × frozen-19</h1><div class=muted>barra: ≥55% e IC inferior &gt; 50% em 400 partidas "
                f"· atualiza a cada 3 s</div><div class='card' style='margin-top:16px'><div class=kpis>{kpis}</div>"
                f"{'<h2 style=margin-top:12px>incidentes recentes</h2><ul>' + incidents + '</ul>' if incidents else ''}</div>")

        live = live_state(rundir) if rundir else None
        if live:
            b = live["board"]
            evals = "".join(f"<tr><td>{label(n)}</td><td class=mono>{html.escape(s)}</td></tr>" for n, s in live["scores"].items())
            live_html = (f"<div class=card><h2>ao vivo · lance {b.fullmove_number} · vez de {label(live['to_move'])}</h2>"
                         f"{svg(b)}<table><tr><td>relógio brancas</td><td class=mono>{clock(live.get('wtime'))}</td></tr>"
                         f"<tr><td>relógio pretas</td><td class=mono>{clock(live.get('btime'))}</td></tr>{evals}</table>"
                         f"<div class='muted mono'>{html.escape(rundir.name)}</div></div>")
        else:
            live_html = ("<div class=card><h2>ao vivo</h2><p class=muted>Nenhuma partida em andamento "
                         "(ou o lote não foi lançado com LIVE_LOG=1).</p></div>")

        rows = []
        for r in reversed(all_rundirs(self.sprt_dir)):
            for i, g in reversed(list(enumerate(finished_games(r)))):
                h = g.headers
                rows.append(f"<tr><td><a href='/game?run={quote(r.name)}&i={i}'>{label(h.get('White', '?'))} × "
                            f"{label(h.get('Black', '?'))}</a></td><td>{html.escape(h.get('Result', '*'))}</td>"
                            f"<td>{html.escape(h.get('Termination', ''))}</td><td>{html.escape(h.get('PlyCount', ''))}</td></tr>")
                if len(rows) >= 40:
                    break
            if len(rows) >= 40:
                break
        games_html = ("<div class=card><h2>partidas terminadas</h2><table><tr><th>brancas × pretas</th><th>res.</th>"
                      f"<th>término</th><th>plies</th></tr>{''.join(rows) or '<tr><td colspan=4 class=muted>nenhuma ainda</td></tr>'}"
                      "</table></div>")
        return page("S2 ao vivo", body + f"<div class=grid>{live_html}{games_html}</div>", refresh=True)

    def game(self, run: str, i: int, ply: int | None) -> bytes | None:
        rundir = self.sprt_dir / run
        if rundir.parent != self.sprt_dir or not rundir.is_dir():
            return None
        games = finished_games(rundir)
        if not 0 <= i < len(games):
            return None
        g = games[i]
        moves = list(g.mainline_moves())
        ply = len(moves) if ply is None else max(0, min(ply, len(moves)))
        board = g.board()
        for mv in moves[:ply]:
            board.push(mv)
        base = f"/game?run={quote(run)}&i={i}&ply="
        nav = (f"<div class=nav><a href='{base}0'>⏮</a><a href='{base}{max(ply - 1, 0)}'>◀</a>"
               f"<span class=mono>{ply}/{len(moves)}</span> <a href='{base}{ply + 1}'>▶</a><a href='{base}{len(moves)}'>⏭</a></div>")
        h = g.headers
        body = (f"<p><a href='/'>← painel</a></p><h1>{label(h.get('White', '?'))} × {label(h.get('Black', '?'))} · "
                f"{html.escape(h.get('Result', '*'))}</h1><div class=muted>{html.escape(h.get('Termination', ''))} · "
                f"abertura {html.escape(h.get('FEN', 'startpos'))}</div><div class=grid><div class=card>{svg(board)}{nav}</div>"
                f"<div class=card><h2>PGN</h2><div class=mono>{html.escape(str(g.mainline()))}</div></div></div>")
        return page("Partida", body, refresh=False)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--screening-dir", default="logs/screening/devbrain-s2-20261006")
    ap.add_argument("--sprt-dir", default="logs/sprt")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    viewer = Viewer((ROOT / args.screening_dir).resolve(), (ROOT / args.sprt_dir).resolve())

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlparse(self.path)
            q = parse_qs(url.query)
            try:
                if url.path == "/":
                    out = viewer.index()
                elif url.path == "/game":
                    ply = q.get("ply", [None])[0]
                    out = viewer.game(q.get("run", [""])[0], int(q.get("i", ["-1"])[0]), int(ply) if ply else None)
                else:
                    out = None
            except ValueError:
                out = None
            if out is None:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(out)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"painel em http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

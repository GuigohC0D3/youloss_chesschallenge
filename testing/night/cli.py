"""CLI for the chess.com night harness."""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

from testing.night.chesscom import (
    BOT_URL,
    ChessComError,
    ChessComSession,
    LoginRequired,
)
from testing.night.config import RunSpec, default_run_dir
from testing.night.recorder import Recorder
from testing.night.runner import NightRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m testing.night",
        description="Joga o engine Youloss contra o bot 3200 do chess.com, sem supervisão.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--profile", type=Path, default=RunSpec.profile_dir)
        p.add_argument("--cdp-port", type=int, default=RunSpec.cdp_port)

    login = sub.add_parser("login", help="abre o Chrome e espera o login manual")
    common(login)
    login.add_argument("--timeout", type=float, default=900.0)

    diag = sub.add_parser("diag", help="salva um retrato do DOM e da tela atuais")
    common(diag)
    diag.add_argument("--url", default=BOT_URL)
    diag.add_argument("--out", type=Path, default=None)

    run = sub.add_parser("run", help="inicia a série noturna")
    common(run)
    run.add_argument("--games", type=int, default=0, help="0 = até --hours")
    run.add_argument(
        "--hours", type=float, default=8.0, help="0 = sem limite, até parar"
    )
    run.add_argument(
        "--tc", default="3+2", help="padrão 3+2 (o chess.com não oferece 3+0)"
    )
    run.add_argument("--bot", default="Maximum")
    run.add_argument(
        "--color", choices=["alternate", "white", "black"], default="alternate"
    )
    run.add_argument("--engine", type=Path, default=RunSpec.engine)
    run.add_argument("--threads", type=int)
    run.add_argument("--hash", type=int, dest="hash_mb")
    run.add_argument("--overhead", type=int, default=80, dest="move_overhead_ms")
    run.add_argument("--max-move-ms", type=int, default=2500)
    run.add_argument("--no-book", action="store_true")
    run.add_argument("--syzygy", type=Path, default=RunSpec.syzygy)
    run.add_argument("--attach", action="store_true", help="assume a partida já aberta")
    run.add_argument(
        "--dry-run", action="store_true", help="lê e escolhe, mas não clica"
    )
    run.add_argument("--out", type=Path, default=None)
    run.add_argument("--max-failures", type=int, default=3)
    run.add_argument("--move-timeout", type=float, default=45.0)
    run.add_argument(
        "--allow-battery",
        action="store_true",
        help="permite iniciar sem AC (não recomendado para a noite)",
    )
    return parser


def _power_state() -> str:
    try:
        out = subprocess.run(
            ["pmset", "-g", "batt"], capture_output=True, text=True, timeout=5
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    if "AC Power" in out:
        return "ac"
    if "Battery Power" in out:
        return "battery"
    return "unknown"


def _swap_warning() -> str:
    try:
        out = subprocess.run(
            ["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    return out


def _port_busy(port: int = 8765) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _memory_warning() -> str:
    try:
        from controller.runtime import free_memory_mb

        free = free_memory_mb()
    except Exception:
        return ""
    if free < 1024:
        return (
            f"AVISO: apenas {free} MiB de RAM disponíveis; feche apps e o "
            "controller.web antes da série para evitar swap."
        )
    return ""


def _spec_from_run(args: argparse.Namespace) -> RunSpec:
    return RunSpec(
        bot=args.bot,
        tc=args.tc,
        color_mode=args.color,
        max_games=args.games,
        max_hours=args.hours,
        attach=args.attach,
        dry_run=args.dry_run,
        engine=args.engine,
        threads=args.threads,
        hash_mb=args.hash_mb,
        move_overhead_ms=args.move_overhead_ms,
        max_move_ms=args.max_move_ms,
        book=None if args.no_book else RunSpec.book,
        syzygy=args.syzygy,
        profile_dir=args.profile,
        cdp_port=args.cdp_port,
        max_consecutive_failures=args.max_failures,
        move_timeout_s=args.move_timeout,
        out_dir=args.out or default_run_dir(),
    )


def _login(args: argparse.Namespace) -> int:
    spec = RunSpec(
        profile_dir=args.profile, cdp_port=args.cdp_port, out_dir=default_run_dir()
    )
    session = ChessComSession(spec)
    try:
        session.connect()
        session.goto("https://www.chess.com/login")
        print("Faça login na janela do Chrome (conta descartável).", flush=True)
        print("A sessão fica no perfil dedicado; não feche a janela.", flush=True)
        session.wait_for_login(
            timeout_s=args.timeout,
            progress=lambda state: print(f"estado: {state}", flush=True),
        )
        print(f"login confirmado: {session.snapshot().member}", flush=True)
        return 0
    except LoginRequired as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    finally:
        session.close()


def _diag(args: argparse.Namespace) -> int:
    spec = RunSpec(
        profile_dir=args.profile, cdp_port=args.cdp_port, out_dir=default_run_dir()
    )
    session = ChessComSession(spec)
    out = args.out or (spec.out_dir / "diag")
    out.mkdir(parents=True, exist_ok=True)
    try:
        session.connect()
        session.goto(args.url)
        snap = session.snapshot()
        stamp = time.strftime("%Y%m%d-%H%M%S")
        (out / f"{stamp}.json").write_text(
            json.dumps(snap.__dict__, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (out / f"{stamp}.html").write_text(session.page.content(), encoding="utf-8")
        session.screenshot(out / f"{stamp}.png")
        print(
            json.dumps(
                {
                    "url": snap.url,
                    "board": snap.board,
                    "orientation": snap.orientation,
                    "ply": snap.ply,
                    "sans": snap.sans[-8:],
                    "rows": snap.rows,
                    "member": snap.member,
                    "modal": snap.modal_text[:200],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0
    except (ChessComError, OSError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    finally:
        session.close()


def _run(args: argparse.Namespace) -> int:
    power = _power_state()
    if power != "ac" and not args.allow_battery:
        print(
            "ERRO: o Mac está na bateria. Conecte o carregador antes da série "
            "noturna (ou use --allow-battery para um teste curto).",
            file=sys.stderr,
        )
        return 2
    swap = _swap_warning()
    if swap:
        print(f"swap: {swap}", flush=True)
    warning = _memory_warning()
    if warning:
        print(warning, file=sys.stderr, flush=True)
    if _port_busy(8765):
        print(
            "AVISO: controller.web está ativo na porta 8765; feche a partida "
            "de torneio para não disputar CPU com a série.",
            file=sys.stderr,
            flush=True,
        )
    spec = _spec_from_run(args)
    recorder = Recorder(spec)
    runner = NightRunner(spec, recorder)
    print(f"run: {spec.out_dir}", flush=True)
    print(
        f"bot={spec.bot} tc={spec.tc} jogos={spec.max_games or 'inf'} "
        f"horas={spec.max_hours} cor={spec.color_mode}",
        flush=True,
    )
    print(
        f"engine={spec.engine} overhead={spec.move_overhead_ms}ms cap={spec.max_move_ms}ms",
        flush=True,
    )
    result = "error"
    try:
        result = runner.run()
        return 0 if result not in ("consecutive_failures", "failed", "error") else 2
    except LoginRequired as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        result = "login_required"
        return 2
    except KeyboardInterrupt:
        result = "interrupted"
        print("\ninterrompido; estado e jogos já gravados", file=sys.stderr)
        return 130
    except (ChessComError, OSError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        result = f"error:{type(exc).__name__}"
        return 2
    finally:
        try:
            summary = recorder.finish(result=result)
            print(f"resumo: {summary}", flush=True)
        except Exception as exc:
            print(f"ERRO ao gravar resumo: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "login":
        return _login(args)
    if args.cmd == "diag":
        return _diag(args)
    return _run(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Verificação independente do pacote offline do Stockfish.

  1. Segurança do arquivo e extração isolada
  2. Manifesto: hash de cada arquivo, binário e configurações
  3. python3 da máquina + python-chess embutido
  4. Engine: uci/isready e bench do Stockfish 19
  5. Interface: partida real pela WebSession, com lance legal do engine
  6. Lançador: --help, --dry-run, recusa de engine fora do manifesto
  7. GPL e pendências em aberto
"""


from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import textwrap
from typing import Any


ENGINE_BENCH = 2497913


class VerificationError(Exception):
    """Raised when any release package verification step fails."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def check_archive_safety(tar: tarfile.TarFile) -> None:
    """Verifies that archive members cannot escape the extraction directory."""
    names: set[str] = set()
    for member in tar.getmembers():
        name = member.name
        if name in names:
            raise VerificationError(f"Duplicate archive member: {name!r}")
        names.add(name)
        # 1. Reject absolute member paths
        if os.path.isabs(name) or name.startswith("/"):
            raise VerificationError(f"Security violation: archive member has absolute path: {name!r}")

        # 2. Reject path traversal
        norm_parts = Path(name).parts
        if ".." in norm_parts:
            raise VerificationError(f"Security violation: path traversal '..' in member path: {name!r}")

        # 3. Reject unsafe symlinks or hardlinks
        if member.issym() or member.islnk():
            target = member.linkname
            if os.path.isabs(target) or target.startswith("/"):
                raise VerificationError(
                    f"Security violation: link {name!r} points to absolute target {target!r}"
                )
            parent_rel = Path(name).parent
            # Check normalized target relative to member parent
            combined = os.path.normpath(os.path.join(str(parent_rel), target))
            if combined.startswith("..") or combined.startswith("/"):
                raise VerificationError(
                    f"Security violation: link {name!r} escapes extraction root: {target!r}"
                )

        # 4. Reject special device files, FIFOs, etc.
        if member.isdev() or member.ischr() or member.isblk() or member.isfifo():
            raise VerificationError(f"Security violation: non-regular special device file: {name!r}")


def safe_extract(archive_path: Path, extract_dir: Path) -> None:
    print(f"[VERIFY 1/7] Inspecting archive safety: {archive_path.name}")
    with tarfile.open(archive_path, "r:*") as tar:
        check_archive_safety(tar)
        # Use Python 3.12 data filter if available
        if hasattr(tarfile, "data_filter"):
            tar.extractall(path=extract_dir, filter="data")
        else:
            tar.extractall(path=extract_dir)
    print("  -> Safe extraction verified. No path traversal or escaping links found.")


def verify_manifest(extract_root: Path) -> dict[str, Any]:
    print("[VERIFY 2/7] Verifying release manifest integrity and metadata...")
    manifest_path = extract_root / "RELEASE_MANIFEST.json"
    if not manifest_path.is_file():
        raise VerificationError(f"Missing RELEASE_MANIFEST.json at {manifest_path}")

    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        raise VerificationError(f"Failed to parse RELEASE_MANIFEST.json: {e}") from e

    # Required top-level fields
    required_keys = [
        "manifest_version",
        "package_name",
        "created_at",
        "architecture",
        "source_commit",
        "git_dirty",
        "candidate_mode",
        "binary_path",
        "binary_hash",
        "chess_version",
        "nnue_id",
        "engine_bench",
        "exact_run_settings",
        "absent_optional_assets",
        "open_items",
        "organizer_acceptance",
        "gpl_compliance",
        "files",
    ]
    for key in required_keys:
        if key not in manifest:
            raise VerificationError(f"Manifest missing required key: {key!r}")

    # Check exact run settings
    settings = manifest["exact_run_settings"]
    if settings.get("time_control") != "1500+0":
        raise VerificationError(f"Expected 1500+0 TC, got {settings.get('time_control')}")
    if settings.get("clock_latency_s") != 2.0:
        raise VerificationError(f"Expected 2.0s clock latency, got {settings.get('clock_latency_s')}")

    # Check open items
    open_items = manifest["open_items"]
    if "OPEN" not in open_items.get("physical_board_qualification", "").upper():
        raise VerificationError("Manifest must record physical_board_qualification as OPEN")
    if not manifest["organizer_acceptance"].upper().startswith("CONFIRMED"):
        raise VerificationError("Manifest must record organizer_acceptance as CONFIRMED")

    # Check absent optional assets
    absent = manifest["absent_optional_assets"]
    if not (extract_root / absent.get("polyglot_book", "missing")).is_file():
        raise VerificationError("Manifest must point polyglot_book at the packaged book")
    if "absent" not in absent.get("syzygy_tablebases", "").lower():
        raise VerificationError("Manifest must record syzygy_tablebases as absent")

    # Re-hash all bundled files
    files_dict = manifest["files"]
    if not isinstance(files_dict, dict) or not files_dict:
        raise VerificationError("Manifest files must be a nonempty mapping")
    print(f"  Verifying SHA-256 hashes of {len(files_dict)} bundled files...")
    verified_files: set[str] = set()
    root = extract_root.resolve()

    for rel_path_str, meta in files_dict.items():
        if Path(rel_path_str).is_absolute() or ".." in Path(rel_path_str).parts:
            raise VerificationError(f"Manifest file path escapes package: {rel_path_str!r}")
        file_path = extract_root / rel_path_str
        if not file_path.resolve().is_relative_to(root):
            raise VerificationError(f"Manifest file resolves outside package: {rel_path_str!r}")
        if not file_path.is_file():
            raise VerificationError(f"Manifested file missing on disk: {rel_path_str}")

        expected_hash = meta["sha256"]
        actual_hash = sha256_file(file_path)
        if actual_hash != expected_hash:
            raise VerificationError(
                f"Hash mismatch on {rel_path_str}: expected {expected_hash}, got {actual_hash}"
            )

        expected_size = meta["size"]
        actual_size = file_path.stat().st_size
        if actual_size != expected_size:
            raise VerificationError(
                f"Size mismatch on {rel_path_str}: expected {expected_size} bytes, got {actual_size}"
            )

        verified_files.add(rel_path_str)

    actual_files = {
        str((Path(folder) / name).relative_to(extract_root))
        for folder, _, names in os.walk(extract_root)
        for name in names
        if str((Path(folder) / name).relative_to(extract_root)) != "RELEASE_MANIFEST.json"
    }
    if actual_files != verified_files:
        raise VerificationError(
            f"Manifest file list differs from archive: missing={sorted(verified_files - actual_files)}, "
            f"unexpected={sorted(actual_files - verified_files)}"
        )

    # Verify engine binary hash
    bin_file = extract_root / manifest["binary_path"]
    if not bin_file.is_file():
        raise VerificationError(f"Binary path does not exist: {bin_file}")
    if sha256_file(bin_file) != manifest["binary_hash"]:
        raise VerificationError("Engine binary hash mismatch with manifest binary_hash")

    print(f"  -> Manifest validated. Commit {manifest['source_commit'][:10]}, "
          f"dirty={manifest['git_dirty']}, files={len(files_dict)} OK.")
    return manifest


def host_python() -> str:
    python = shutil.which("python3")
    if python is None:
        raise VerificationError("python3 not found on this machine")
    return python


def package_env(extract_root: Path) -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONPATH"] = f"{extract_root}:{extract_root}/vendor"
    return env


def verify_vendored_python(extract_root: Path) -> None:
    print("[VERIFY 3/7] Verifying host python3 with vendored chess...")
    code = (
        "import sys, chess, chess.svg, controller.web; "
        "assert sys.version_info >= (3, 9); "
        "assert 'vendor' in chess.__file__, chess.__file__; "
        "print('CHESS_OK:' + chess.__version__)"
    )
    try:
        res = subprocess.run(
            [host_python(), "-c", code], cwd=extract_root, env=package_env(extract_root),
            capture_output=True, text=True, timeout=20, check=True,
        )
    except (OSError, subprocess.SubprocessError) as e:
        raise VerificationError(f"Vendored chess import failed: {e}") from e
    if "CHESS_OK:1.11.2" not in res.stdout:
        raise VerificationError(f"Expected chess 1.11.2, output was:\n{res.stdout}")
    print("  -> python3 and vendored chess==1.11.2 OK.")


def verify_engine_uci(extract_root: Path) -> None:
    print("[VERIFY 4/7] Verifying offline engine UCI handshake (uciok/readyok)...")
    bin_file = extract_root / "bin" / "stockfish"
    if not bin_file.is_file():
        raise VerificationError(f"Engine binary missing: {bin_file}")

    if not os.access(bin_file, os.X_OK):
        os.chmod(bin_file, os.stat(bin_file).st_mode | stat.S_IXUSR)

    try:
        result = subprocess.run(
            [str(bin_file)], input="uci\nisready\nquit\n", capture_output=True,
            text=True, timeout=10, check=True,
        )
    except subprocess.TimeoutExpired as e:
        raise VerificationError("Engine timed out during UCI handshake") from e
    except Exception as e:
        raise VerificationError(f"Engine UCI communication failure: {e}") from e
    lines = result.stdout.splitlines()
    if "uciok" not in lines or "readyok" not in lines:
        raise VerificationError("Engine did not return both uciok and readyok")

    try:
        bench = subprocess.run(
            [str(bin_file), "bench"], capture_output=True, text=True, timeout=60, check=True,
        )
    except (OSError, subprocess.SubprocessError) as e:
        raise VerificationError(f"Engine bench failed: {e}") from e
    if f"Nodes searched  : {ENGINE_BENCH}" not in bench.stdout + bench.stderr:
        raise VerificationError(f"Engine bench differs from Stockfish 19 ({ENGINE_BENCH})")

    print(f"  -> Engine answered uciok/readyok; bench {ENGINE_BENCH} matches Stockfish 19.")


def verify_controller_search(extract_root: Path) -> None:
    """Plays one real exchange through the packaged web session and engine."""
    print("[VERIFY 5/7] Verifying packaged interface against the real engine...")
    script = textwrap.dedent("""
        import pathlib, sys, tempfile, time
        import chess
        from controller.engine_client import EngineClient
        from controller.web import WebSession

        options = {"Threads": 1, "Hash": 16, "Move Overhead": 100}
        with tempfile.TemporaryDirectory() as logs:
            session = WebSession(lambda: EngineClient(sys.argv[1]), options, pathlib.Path(logs))
            print(session.open())
            session.start_game("black", "verify", 1, "10+0")
            session.opponent_move("e4")
            deadline = time.monotonic() + 20
            while session.thinking and time.monotonic() < deadline:
                time.sleep(0.02)
            snap = session.snapshot()
            assert snap["our_move"]["source"] == "engine", snap["our_move"]
            assert snap["board_svg"].startswith("<svg")
            import chess.polyglot
            with chess.polyglot.open_reader("assets/book.bin") as reader:
                assert reader.find(chess.Board()).move in chess.Board().legal_moves
            board = chess.Board()
            board.push_san("e4")
            board.push_uci(snap["our_move"]["from"] + snap["our_move"]["to"])
            session.close()
        print("LEGAL_MOVE_OK")
    """)
    try:
        result = subprocess.run(
            [host_python(), "-c", script, str(extract_root / "bin" / "stockfish")],
            cwd=extract_root, env=package_env(extract_root),
            capture_output=True, text=True, timeout=40, check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        detail = getattr(exc, "stderr", "") or ""
        raise VerificationError(f"Packaged interface failed: {exc}\n{detail}") from exc
    if "LEGAL_MOVE_OK" not in result.stdout or "Stockfish 19 YoulossTM" not in result.stdout:
        raise VerificationError(f"Packaged interface did not confirm a legal move:\n{result.stdout}")
    print("  -> Interface sent the opponent move and received a legal Stockfish 19 reply.")


def verify_launcher(extract_root: Path) -> None:
    print("[VERIFY 6/7] Verifying offline launcher script (launch_stockfish.sh)...")
    launcher_file = extract_root / "launch_stockfish.sh"
    if not launcher_file.is_file():
        raise VerificationError(f"Launcher script missing: {launcher_file}")

    if not os.access(launcher_file, os.X_OK):
        os.chmod(launcher_file, os.stat(launcher_file).st_mode | stat.S_IXUSR)

    # 1. Test --help
    try:
        res_help = subprocess.run(
            ["bash", str(launcher_file), "--help"],
            cwd=extract_root,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except Exception as e:
        raise VerificationError(f"Launcher --help failed: {e}") from e

    help_out = res_help.stdout
    required_strings = ["--dry-run", "--threads", "--hash", "--clock-latency"]
    for s in required_strings:
        if s not in help_out:
            raise VerificationError(f"Launcher --help missing required string {s!r}")

    # 2. Test --dry-run
    try:
        res_dry = subprocess.run(
            ["bash", str(launcher_file), "--dry-run"],
            cwd=extract_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )
    except Exception as e:
        raise VerificationError(f"Launcher --dry-run failed: {e}") from e

    if "Verificação concluída" not in res_dry.stdout:
        raise VerificationError(f"Launcher --dry-run did not confirm success:\n{res_dry.stdout}")

    override = subprocess.run(
        ["bash", str(launcher_file), "--engine", "/tmp/unmanifested-engine"],
        cwd=extract_root, capture_output=True, text=True, timeout=10,
    )
    if override.returncode == 0 or "bin/stockfish" not in override.stderr:
        raise VerificationError("Launcher accepted an unmanifested engine override")

    print("  -> Launcher help and dry-run preflight passed offline.")


def verify_gpl_and_open_status(extract_root: Path, manifest: dict[str, Any]) -> None:
    print("[VERIFY 7/7] Verifying GPL source completeness and recording open items...")
    gpl_file = extract_root / "engine" / "Copying.txt"
    if not gpl_file.is_file():
        raise VerificationError("Missing engine/Copying.txt GPLv3 license text")

    origin_file = extract_root / "engine" / "ORIGIN.md"
    if not origin_file.is_file():
        raise VerificationError("Missing engine/ORIGIN.md Stockfish baseline documentation")

    print("=" * 72)
    print(f"  Manifest verified: {len(manifest['files'])} files. Engine: Stockfish 19 + YoulossTM.")
    print("  OPEN: physical-board rehearsal; run --dry-run on the M4 itself.")
    print("=" * 72)


def verify_archive(archive_path: Path, keep_extracted: bool = False) -> None:
    archive_path = archive_path.resolve()
    if not archive_path.is_file():
        raise VerificationError(f"Candidate archive file not found: {archive_path}")

    temp_dir = Path(tempfile.mkdtemp(prefix="stockfish_verify_"))
    try:
        safe_extract(archive_path, temp_dir)
        manifest = verify_manifest(temp_dir)
        verify_vendored_python(temp_dir)
        verify_engine_uci(temp_dir)
        verify_controller_search(temp_dir)
        verify_launcher(temp_dir)
        verify_gpl_and_open_status(temp_dir, manifest)
        print("\nALL VERIFICATION CHECKS PASSED.")
    finally:
        if keep_extracted:
            print(f"Preserved extracted bundle at: {temp_dir}")
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)


def parse_args() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Independently verify the offline Stockfish release package.")
    p.add_argument("archive", type=Path, help="Path to release archive (.tar.gz)")
    p.add_argument(
        "--keep-extracted",
        action="store_true",
        help="Keep temporary extracted folder after verification",
    )
    return p


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    try:
        verify_archive(args.archive, keep_extracted=args.keep_extracted)
    except VerificationError as e:
        print(f"\nVERIFICATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

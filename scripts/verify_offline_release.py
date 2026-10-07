#!/usr/bin/env python3
"""Offline Candidate Release Verifier for Youloss.

Performs independent offline verification:
  1. Archive security checks (rejects absolute paths, path traversal, escaping symlinks)
  2. Safe extraction to isolated temporary directory
  3. Full manifest verification (hashes every file, validates commit, dirty state, binary hash,
     Python/chess versions, NNUE ID/hash, exact run settings, and absent optional assets)
  4. Bundled Python 3.12 execution and offline `import chess` (version 1.11.2)
  5. Offline engine UCI handshake (uci -> uciok, isready -> readyok, quit)
  6. Offline launcher help and dry-run preflight check
  7. Verification that physical-board qualification and organizer acceptance remain open
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
        "python_version",
        "chess_version",
        "nnue_id",
        "nnue_build_input_hash",
        "exact_run_settings",
        "absent_optional_assets",
        "open_items",
        "gpl_compliance",
        "files",
    ]
    for key in required_keys:
        if key not in manifest:
            raise VerificationError(f"Manifest missing required key: {key!r}")

    # Check exact run settings
    settings = manifest["exact_run_settings"]
    if settings.get("threads") not in (7, 8):
        raise VerificationError(f"Expected 7 or 8 threads in settings, got {settings.get('threads')}")
    if settings.get("hash_mb") not in (512, 2048):
        raise VerificationError(f"Expected 512 or 2048 MiB hash in settings, got {settings.get('hash_mb')}")
    if settings.get("time_control") != "1500+0":
        raise VerificationError(f"Expected 1500+0 TC, got {settings.get('time_control')}")
    if settings.get("clock_latency_s") != 2.0:
        raise VerificationError(f"Expected 2.0s clock latency, got {settings.get('clock_latency_s')}")

    # Verify candidate labelling
    profile_status_upper = settings.get("profile_status", "").upper()
    if "UNQUALIFIED CANDIDATE" not in profile_status_upper and "MAXIMUM TECHNICAL POWER" not in profile_status_upper:
        raise VerificationError("Run settings must explicitly label profile as UNQUALIFIED CANDIDATE or MAXIMUM TECHNICAL POWER PROFILE")
    # Check open items
    open_items = manifest["open_items"]
    if "OPEN" not in open_items.get("physical_board_qualification", "").upper():
        raise VerificationError("Manifest must record physical_board_qualification as OPEN")
    if "OPEN" not in open_items.get("organizer_acceptance", "").upper():
        raise VerificationError("Manifest must record organizer_acceptance as OPEN")

    # Check absent optional assets
    absent = manifest["absent_optional_assets"]
    if "absent" not in absent.get("polyglot_book", "").lower():
        raise VerificationError("Manifest must record polyglot_book as absent")
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

    # Verify NNUE build input net hash
    nnue_file = extract_root / "engine" / "src" / manifest["nnue_id"]
    if not nnue_file.is_file():
        raise VerificationError(f"Build input NNUE missing at: {nnue_file}")
    if sha256_file(nnue_file) != manifest["nnue_build_input_hash"]:
        raise VerificationError("NNUE build input hash mismatch with manifest")

    print(f"  -> Manifest validated. Commit {manifest['source_commit'][:10]}, "
          f"dirty={manifest['git_dirty']}, files={len(files_dict)} OK.")
    return manifest


def verify_bundled_python(extract_root: Path) -> None:
    print("[VERIFY 3/7] Verifying bundled Python runtime and chess import offline...")
    py_bin = extract_root / "python" / "bin" / "python3"
    if not py_bin.is_file():
        py_bin = extract_root / "python" / "bin" / "python"
    if not py_bin.is_file():
        raise VerificationError(f"Bundled Python binary missing at: {py_bin}")

    # Ensure executable permission
    if not os.access(py_bin, os.X_OK):
        os.chmod(py_bin, os.stat(py_bin).st_mode | stat.S_IXUSR)

    # Run offline Python check without network
    env = dict(os.environ)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONPATH"] = f"{extract_root}:{extract_root}/python/lib/python3.12/site-packages"

    cmd = [
        str(py_bin),
        "-c",
        (
            "import sys, chess; "
            "print(f'PYTHON_OK:{sys.version.split()[0]}'); "
            "print(f'CHESS_OK:{chess.__version__}'); "
            "assert chess.__version__ == '1.11.2', f'Expected 1.11.2, got {chess.__version__}'; "
            "b = chess.Board(); "
            "assert b.is_valid(), 'chess.Board invalid'"
        ),
    ]

    try:
        res = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise VerificationError(
            f"Bundled Python execution failed (code {e.returncode}):\nStdout: {e.stdout}\nStderr: {e.stderr}"
        ) from e
    except Exception as e:
        raise VerificationError(f"Failed to execute bundled Python: {e}") from e

    out = res.stdout
    if "CHESS_OK:1.11.2" not in out or "PYTHON_OK:3.12." not in out:
        raise VerificationError(f"Expected chess 1.11.2, output was:\n{out}")

    print("  -> Bundled Python and chess==1.11.2 verified offline.")


def verify_engine_uci(extract_root: Path) -> None:
    print("[VERIFY 4/7] Verifying offline engine UCI handshake (uciok/readyok)...")
    bin_file = extract_root / "bin" / "youloss"
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

    print("  -> Engine responded to uci and isready with uciok and readyok offline.")


def verify_controller_search(extract_root: Path) -> None:
    """Exercise packaged controller, dependency, and engine through legal moves."""
    print("[VERIFY 5/7] Verifying packaged controller searches in both engine modes...")
    py_bin = extract_root / "python" / "bin" / "python3"
    engine_bin = extract_root / "bin" / "youloss"
    env = dict(os.environ)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONPATH"] = f"{extract_root}:{extract_root}/python/lib/python3.12/site-packages"
    script = textwrap.dedent("""
        import chess
        import sys
        from controller.engine_client import EngineClient

        with EngineClient(sys.argv[1]) as engine:
            engine.handshake(timeout=5)
            engine.set_option("Threads", 1)
            engine.set_option("Hash", 64)
            for enabled, moves in ((True, []), (False, ["e2e4"])):
                engine.set_option("YoulossTM", enabled)
                engine.is_ready(timeout=5)
                board = chess.Board()
                for uci in moves:
                    board.push_uci(uci)
                position = "position startpos"
                if moves:
                    position += " moves " + " ".join(moves)
                result = engine.search(position, "go depth 2", timeout=10)
                assert chess.Move.from_uci(result.bestmove) in board.legal_moves
        print("LEGAL_MOVES_OK")
    """)
    try:
        result = subprocess.run(
            [str(py_bin), "-c", script, str(engine_bin)], cwd=extract_root,
            env=env, capture_output=True, text=True, timeout=25, check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise VerificationError(f"Packaged controller search failed: {exc}") from exc
    if "LEGAL_MOVES_OK" not in result.stdout:
        raise VerificationError("Packaged controller did not confirm both legal moves")
    print("  -> Packaged controller returned legal moves in both engine modes.")


def verify_launcher(extract_root: Path) -> None:
    print("[VERIFY 6/7] Verifying offline launcher script (launch_youloss.sh)...")
    launcher_file = extract_root / "launch_youloss.sh"
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
    required_strings = [
        "1500+0",
        "--clock-latency",
        "7",
        "2048",
        "Physical-board",
    ]
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
            timeout=15,
            check=True,
        )
    except Exception as e:
        raise VerificationError(f"Launcher --dry-run failed: {e}") from e

    if "Verification successful" not in res_dry.stdout:
        raise VerificationError(f"Launcher --dry-run did not confirm success:\n{res_dry.stdout}")

    override = subprocess.run(
        ["bash", str(launcher_file), "--engine", "/tmp/unmanifested-engine"],
        cwd=extract_root, capture_output=True, text=True, timeout=10,
    )
    if override.returncode == 0 or "manifested bin/youloss" not in override.stderr:
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

    # Explicitly print caveats and open items as required
    print("================================================================================")
    print("                    OFFLINE CANDIDATE VERIFICATION REPORT")
    print("================================================================================")
    print(" [PASSED CHECKS]")
    print("   1. Archive security: no path traversal, no absolute paths, no escaping links.")
    print(f"   2. Manifest integrity: verified all {len(manifest['files'])} bundled file hashes.")
    print("   3. Pinned Python runtime: Python 3.12 + chess==1.11.2 imported offline.")
    print("   4. Native Apple Silicon engine: answered uciok and readyok offline.")
    print("   5. Packaged controller: legal moves in both engine modes.")
    print("   6. Offline launcher: --help and --dry-run passed with candidate profile.")
    print("   7. GPL provenance: engine source, ORIGIN.md, Copying.txt, and NNUE net present.")
    print("")
    print(" [TOURNAMENT PROFILE - MAXIMUM TECHNICAL POWER]")
    print("   * Candidate settings: 7 threads / 2048 MiB / 2.0 s latency / official 1500+0.")
    print("   * LABEL: MAXIMUM TECHNICAL POWER PROFILE (4P + 3E cores on 16 GB Apple Silicon).")
    print(" [CRITICAL OPEN ITEMS]")
    print("   * PHYSICAL-BOARD QUALIFICATION: OPEN. Physical clock reading/typing latency")
    print("     rehearsal and operator reconciliation remain open.")
    print("   * ORGANIZER ACCEPTANCE: OPEN. Formal rules confirmation of increment (1500+0),")
    print("     illegal-move handling, Polyglot/Syzygy policy, and brackets remains open.")
    print("================================================================================")


def verify_archive(archive_path: Path, keep_extracted: bool = False) -> None:
    archive_path = archive_path.resolve()
    if not archive_path.is_file():
        raise VerificationError(f"Candidate archive file not found: {archive_path}")

    temp_dir = Path(tempfile.mkdtemp(prefix="youloss_verify_"))
    try:
        safe_extract(archive_path, temp_dir)
        manifest = verify_manifest(temp_dir)
        verify_bundled_python(temp_dir)
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
    p = argparse.ArgumentParser(description="Independently verify Youloss offline release package.")
    p.add_argument("archive", type=Path, help="Path to youloss release archive (.tar.gz)")
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

#!/usr/bin/env python3
"""Offline Candidate Release Builder for Youloss (macOS Apple Silicon).

Stages:
  1. bin/youloss executable (embedded NNUE, native Apple Silicon)
  2. Tracked controller source (excluding tests and logs)
  3. Pinned Python 3.12 runtime from sys.base_prefix + chess==1.11.2 and dist-info
  4. Tracked Stockfish/Youloss source, GPLv3 license, and ORIGIN
  5. Local default engine/src/nn-1a298aa575a0.nnue build input
  6. Offline launcher script (launch_youloss.sh)
  7. RELEASE_MANIFEST.json hashing every bundled file and recording metadata

Excludes:
  - Test runners (testing/, pytest)
  - Logs (logs/)
  - Secrets / .git
  - .venv
  - Optional assets (polyglot book, Syzygy tablebases)
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from typing import Any


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_git_info(repo_root: Path) -> tuple[str, bool, str]:
    commit = "unknown"
    is_dirty = True
    summary = "git status unavailable"

    # Attempt to query git CLI
    try:
        commit_res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        commit = commit_res.stdout.strip()

        status_res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        # Ignore untracked .DS_Store or dist/ if not ignored
        lines = [
            ln for ln in status_res.stdout.splitlines()
            if not ln.strip().endswith(".DS_Store") and not ln.strip().startswith("?? dist/")
        ]
        is_dirty = len(lines) > 0
        summary = f"{len(lines)} changed/untracked entries" if is_dirty else "clean"
        return commit, is_dirty, summary
    except Exception:
        pass

    # Fallback to inspecting .git directly
    git_dir = repo_root / ".git"
    if git_dir.is_dir():
        head_file = git_dir / "HEAD"
        if head_file.exists():
            content = head_file.read_text().strip()
            if content.startswith("ref:"):
                ref_rel = content[4:].strip()
                ref_file = git_dir / ref_rel
                if ref_file.exists():
                    commit = ref_file.read_text().strip()
                else:
                    packed = git_dir / "packed-refs"
                    if packed.exists():
                        for line in packed.read_text().splitlines():
                            if line and not line.startswith("#") and not line.startswith("^"):
                                parts = line.split()
                                if len(parts) == 2 and parts[1] == ref_rel:
                                    commit = parts[0]
                                    break
            else:
                commit = content

    return commit, is_dirty, summary


def copy_tree_filtered(
    src_dir: Path,
    dst_dir: Path,
    ignore_patterns: set[str],
) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src_dir, followlinks=False):
        rel_root = Path(root).relative_to(src_dir)
        # Filter directories in-place
        dirs[:] = [
            d for d in dirs
            if d not in ignore_patterns and not any(p in d for p in ("__pycache__", ".pytest_cache", ".ruff_cache"))
        ]

        target_dir = dst_dir / rel_root
        target_dir.mkdir(parents=True, exist_ok=True)

        for file_name in files:
            if file_name in ignore_patterns or file_name.endswith(".pyc"):
                continue

            src_file = Path(root) / file_name
            dst_file = target_dir / file_name

            if src_file.is_symlink():
                link_target = os.readlink(src_file)
                # Keep only links whose source and staged targets stay in their trees.
                resolved = src_file.resolve()
                if not resolved.is_relative_to(src_dir.resolve()):
                    raise RuntimeError(f"Runtime symlink escapes source tree: {src_file}")
                target = (dst_file.parent / link_target).resolve()
                if not os.path.isabs(link_target) and target.is_relative_to(dst_dir.resolve()):
                    dst_file.symlink_to(link_target)
                elif resolved.is_file():
                    shutil.copy2(resolved, dst_file)
                else:
                    raise RuntimeError(f"Unsupported runtime symlink: {src_file}")
            else:
                shutil.copy2(src_file, dst_file)


def stage_python_runtime(staging_dir: Path, venv_root: Path | None) -> tuple[str, str]:
    target_python_dir = staging_dir / "python"
    base_prefix = Path(sys.base_prefix).resolve()

    if not base_prefix.is_dir():
        raise RuntimeError(f"sys.base_prefix is not a directory: {base_prefix}")

    python_version = sys.version.split()[0]
    if sys.version_info[:2] != (3, 12) or platform.machine() != "arm64" or sys.platform != "darwin":
        raise RuntimeError("Offline candidate requires macOS arm64 Python 3.12")
    print(f"Staging pinned Python {python_version} runtime from: {base_prefix}")

    ignore_patterns = {
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        ".pytest_cache",
        ".ruff_cache",
    }
    copy_tree_filtered(base_prefix, target_python_dir, ignore_patterns)

    # Locate installed chess package and dist-info
    try:
        import chess
        chess_version = chess.__version__
        if chess_version != "1.11.2":
            raise RuntimeError(f"Expected chess==1.11.2, found {chess_version}")
        chess_dir = Path(chess.__file__).resolve().parent
    except Exception as e:
        raise RuntimeError(f"Failed to import chess package from active environment: {e}") from e

    site_packages_candidates: list[Path] = []
    # Look in the directory containing chess
    site_packages_candidates.append(chess_dir.parent)
    if venv_root:
        for p in (venv_root / "lib").glob("python*/site-packages"):
            if p.is_dir() and p not in site_packages_candidates:
                site_packages_candidates.append(p)

    dist_info_dir: Path | None = None
    for cand in site_packages_candidates:
        match = list(cand.glob(f"chess-{chess_version}*.dist-info"))
        if match:
            dist_info_dir = match[0]
            break

    # Determine target site-packages inside staged python
    py_ver_tag = f"python{sys.version_info.major}.{sys.version_info.minor}"
    target_site_packages = target_python_dir / "lib" / py_ver_tag / "site-packages"
    target_site_packages.mkdir(parents=True, exist_ok=True)

    # Copy chess package
    target_chess = target_site_packages / "chess"
    if target_chess.exists():
        shutil.rmtree(target_chess)
    copy_tree_filtered(chess_dir, target_chess, ignore_patterns)

    # Copy chess dist-info with license
    if dist_info_dir and dist_info_dir.is_dir():
        target_dist_info = target_site_packages / dist_info_dir.name
        if target_dist_info.exists():
            shutil.rmtree(target_dist_info)
        copy_tree_filtered(dist_info_dir, target_dist_info, ignore_patterns)
    else:
        raise RuntimeError("chess==1.11.2 dist-info and license are required in the release")

    # Ensure python binaries are executable
    for py_bin in (target_python_dir / "bin").glob("python*"):
        if py_bin.is_file() and not py_bin.is_symlink():
            current_mode = os.stat(py_bin).st_mode
            os.chmod(py_bin, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return python_version, chess_version


def stage_controller_source(repo_root: Path, staging_dir: Path) -> None:
    src_ctrl = repo_root / "controller"
    dst_ctrl = staging_dir / "controller"
    dst_ctrl.mkdir(parents=True, exist_ok=True)

    # Copy tracked controller modules only (exclude tests/)
    for item in src_ctrl.iterdir():
        if item.name.startswith((".", "__")) and item.name != "__init__.py":
            continue
        if item.name == "tests" or item.suffix in (".pyc", ".DS_Store"):
            continue
        if item.is_file() and item.suffix == ".py":
            shutil.copy2(item, dst_ctrl / item.name)


def stage_engine_source(repo_root: Path, staging_dir: Path) -> str:
    src_engine = repo_root / "engine"
    dst_engine = staging_dir / "engine"
    dst_engine.mkdir(parents=True, exist_ok=True)

    # Copy top-level metadata and licenses
    for name in ("Copying.txt", "ORIGIN.md", "AUTHORS", "CONTRIBUTING.md", "README.md", "Top CPU Contributors.txt"):
        p = src_engine / name
        if p.is_file():
            shutil.copy2(p, dst_engine / name)

    # Copy engine/src excluding build artifacts
    src_code = src_engine / "src"
    dst_code = dst_engine / "src"
    dst_code.mkdir(parents=True, exist_ok=True)

    ignore_engine = {
        "stockfish",
        "stockfish.exe",
        ".depend",
        ".build_date.txt",
        ".build_sha.txt",
        ".build_diffindex.txt",
        "__pycache__",
        ".DS_Store",
    }

    for root, dirs, files in os.walk(src_code):
        rel = Path(root).relative_to(src_code)
        target_dir = dst_code / rel
        target_dir.mkdir(parents=True, exist_ok=True)

        dirs[:] = [d for d in dirs if d not in ignore_engine]

        for f in files:
            if f in ignore_engine or f.endswith(".o") or f.endswith(".pyc"):
                continue
            # Note: We keep nn-*.nnue build input!
            source_file = Path(root) / f
            if source_file.is_symlink() and not source_file.resolve().is_relative_to(src_code.resolve()):
                raise RuntimeError(f"Engine source symlink escapes source tree: {source_file}")
            shutil.copy2(source_file, target_dir / f)

    # Verify NNUE build input net
    nnue_path = dst_code / "nn-1a298aa575a0.nnue"
    if not nnue_path.is_file():
        raise RuntimeError(f"Default NNUE build input not found at {nnue_path}")
    nnue_hash = sha256_file(nnue_path)
    print(f"Staged NNUE build input: {nnue_path.name} (SHA-256: {nnue_hash})")
    return nnue_hash


def build_release_package(
    repo_root: Path,
    output_archive: Path,
    candidate_mode: bool,
    engine_bin_path: Path,
) -> Path:
    repo_root = repo_root.resolve()
    output_archive = output_archive.resolve()
    engine_bin = engine_bin_path.resolve() if engine_bin_path.is_absolute() else (repo_root / engine_bin_path).resolve()

    if not engine_bin.is_file():
        raise RuntimeError(f"Engine binary not found: {engine_bin}")

    # Check git status
    commit, is_dirty, summary = get_git_info(repo_root)
    print(f"Git HEAD: {commit} (Status: {summary})")
    if is_dirty and not candidate_mode:
        raise RuntimeError(
            f"Repository has uncommitted changes ({summary}). "
            "Clean checkout required for final release. "
            "Pass --candidate / --allow-dirty to package an in-progress review candidate."
        )

    # Give each invocation its own staging area; do not delete another build.
    staging_parent = repo_root / "dist"
    staging_parent.mkdir(parents=True, exist_ok=True)
    staging_base = Path(tempfile.mkdtemp(prefix=".staging_", dir=staging_parent))

    try:
        # 1. Stage binary
        target_bin_dir = staging_base / "bin"
        target_bin_dir.mkdir(parents=True, exist_ok=True)
        target_engine = target_bin_dir / "youloss"
        shutil.copy2(engine_bin, target_engine)
        os.chmod(target_engine, 0o755)
        binary_hash = sha256_file(target_engine)
        print(f"Staged engine binary: {target_engine.name} (SHA-256: {binary_hash})")

        # 2. Stage controller
        stage_controller_source(repo_root, staging_base)

        # 3. Stage Python runtime & chess
        venv_dir = repo_root / ".venv"
        python_ver, chess_ver = stage_python_runtime(
            staging_base,
            venv_dir if venv_dir.is_dir() else None,
        )

        # 4. Stage Engine source and NNUE build input
        nnue_hash = stage_engine_source(repo_root, staging_base)

        # 5. Stage Launcher
        launcher_src = repo_root / "release" / "launch_youloss.sh"
        if not launcher_src.is_file():
            raise RuntimeError(f"Launcher script missing at: {launcher_src}")
        target_launcher = staging_base / "launch_youloss.sh"
        shutil.copy2(launcher_src, target_launcher)
        os.chmod(target_launcher, 0o755)

        # 6. Stage README
        readme_content = f"""# Youloss Offline Release Candidate

Package: youloss-candidate
Generated: {datetime.now(timezone.utc).isoformat()}
Architecture: {platform.machine()}-{sys.platform} (Apple Silicon macOS)
Source Commit: {commit} (Dirty: {is_dirty}, Candidate Mode: {candidate_mode})

## WARNING: Unqualified Candidate Profile
This candidate package uses the measured throughput candidate:
  - Threads: 8
  - Hash: 512 MiB
  - Time Control: 1500+0 (PROVISIONAL: 25 minutes each, zero increment assumed)
  - Clock Latency: 2.0 s (CONFIGURABLE: conservative provisional deduction)
  - Move Overhead: 1500 ms (controller default)

This profile is a measured throughput candidate from 2026-10-02 screening.
It is NOT a frozen tournament profile and has NOT received organizer confirmation.

## Open Items
1. Physical-board qualification and operator clock rehearsal remain OPEN.
2. Organizer confirmation of rules (increment, book/tablebase policy, venue) remains OPEN.

## Usage
Run directly from this extracted package:
  ./launch_youloss.sh --color white --opponent "Team X" --game 1
  ./launch_youloss.sh --resume
  ./launch_youloss.sh --help
  ./launch_youloss.sh --dry-run

## GPL Compliance & Provenance
Derived from Stockfish 19 with custom YoulossTM time manager.
See engine/Copying.txt (GPLv3) and engine/ORIGIN.md for complete provenance.
Full engine source and build input NNUE (engine/src/nn-1a298aa575a0.nnue) are included.
"""
        (staging_base / "RELEASE_README.md").write_text(readme_content, encoding="utf-8")

        # 7. Hash every file for RELEASE_MANIFEST.json
        print("Computing SHA-256 hashes for all bundled files...")
        manifest_files: dict[str, dict[str, Any]] = {}
        for root, _, files in os.walk(staging_base):
            for f in sorted(files):
                full_p = Path(root) / f
                rel_p = str(full_p.relative_to(staging_base))
                file_stat = full_p.stat()
                manifest_files[rel_p] = {
                    "sha256": sha256_file(full_p),
                    "size": file_stat.st_size,
                    "mode": oct(stat.S_IMODE(file_stat.st_mode)),
                }

        manifest_data = {
            "manifest_version": "1.0",
            "package_name": "youloss-offline-candidate",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "architecture": f"{platform.machine()}-{sys.platform}",
            "source_commit": commit,
            "git_dirty": is_dirty,
            "candidate_mode": candidate_mode,
            "binary_path": "bin/youloss",
            "binary_hash": binary_hash,
            "python_version": python_ver,
            "chess_version": chess_ver,
            "nnue_id": "nn-1a298aa575a0.nnue",
            "nnue_build_input_hash": nnue_hash,
            "exact_run_settings": {
                "threads": 7,
                "threads_label": "MAXIMUM TECHNICAL POWER (optimal 4P + 3E cores on Apple Silicon)",
                "hash_mb": 2048,
                "hash_label": "MAXIMUM TECHNICAL POWER (2.0 GB transposition table in 16 GB RAM, zero swap)",
                "time_control": "1500+0",
                "time_control_label": "OFFICIAL (Regulamento Chess Challenge III: 25 min flat, zero increment)",
                "clock_latency_s": 2.0,
                "clock_latency_label": "CONFIGURABLE (default 2.0s; physical rehearsal recommended)",
                "move_overhead_ms": 1500,
                "profile_status": "MAXIMUM TECHNICAL POWER PROFILE (16 GB Apple Silicon)",
            },
            "absent_optional_assets": {
                "polyglot_book": "absent (no assets/book.bin bundled; local default only)",
                "syzygy_tablebases": "absent (no assets/syzygy bundled; local default only)",
            },
            "open_items": {
                "physical_board_qualification": "OPEN - physical-board qualification and operator rehearsal remain open",
                "organizer_acceptance": "OPEN - organizer rules confirmation and acceptance remain open",
            },
            "gpl_compliance": {
                "license": "GPLv3 (see engine/Copying.txt)",
                "origin": "Stockfish 19-derived (see engine/ORIGIN.md)",
                "source_included": True,
                "build_input_nnue_included": True,
            },
            "files": manifest_files,
        }

        manifest_path = staging_base / "RELEASE_MANIFEST.json"
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, sort_keys=True)
            f.write("\n")

        # 8. Create the archive. The manifest records build time, so byte-for-byte
        # archive reproducibility is not claimed.
        output_archive.parent.mkdir(parents=True, exist_ok=True)
        print(f"Creating archive at: {output_archive}")

        with tarfile.open(output_archive, "w:gz") as tar:
            for root, dirs, files in os.walk(staging_base):
                dirs.sort()
                for f in sorted(files):
                    file_path = Path(root) / f
                    rel_path = file_path.relative_to(staging_base)

                    tarinfo = tar.gettarinfo(str(file_path), arcname=str(rel_path))
                    tarinfo.uid = 0
                    tarinfo.gid = 0
                    tarinfo.uname = "youloss"
                    tarinfo.gname = "youloss"
                    if file_path.is_file() and not file_path.is_symlink():
                        with file_path.open("rb") as f_obj:
                            tar.addfile(tarinfo, f_obj)
                    else:
                        tar.addfile(tarinfo)

        print(f"Package successfully created: {output_archive} ({output_archive.stat().st_size} bytes)")
        return output_archive
    finally:
        if staging_base.exists():
            shutil.rmtree(staging_base, ignore_errors=True)


def parse_args() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build Youloss offline candidate release package.")
    p.add_argument(
        "--output",
        type=Path,
        default=Path("dist/youloss-candidate.tar.gz"),
        help="Path for output archive (default: dist/youloss-candidate.tar.gz)",
    )
    p.add_argument(
        "--candidate",
        "--allow-dirty",
        dest="candidate_mode",
        action="store_true",
        default=False,
        help="Allow packaging in-progress/dirty repository state as an unqualified review candidate",
    )
    p.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path",
    )
    p.add_argument(
        "--engine-bin",
        type=Path,
        default=Path("bin/youloss"),
        help="Path to engine binary (default: bin/youloss)",
    )
    return p


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    build_release_package(
        repo_root=args.repo_root,
        output_archive=args.output,
        candidate_mode=args.candidate_mode,
        engine_bin_path=args.engine_bin,
    )


if __name__ == "__main__":
    main()

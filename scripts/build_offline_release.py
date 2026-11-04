#!/usr/bin/env python3
"""Monta o pacote offline: Stockfish 19 + interface (macOS Apple Silicon).

Conteúdo:
  1. bin/stockfish (NNUE embutida; ARMv8.2 genérico, roda em M4 e M5)
     e assets/book.bin (livro de aberturas checado pelo engine)
  2. controller/ sem testes, incluindo a interface web
  3. vendor/chess: python-chess 1.11.2 (usa o python3 da máquina, 3.9+)
  4. engine/: código-fonte do Stockfish, GPLv3 e ORIGIN
  5. launch_stockfish.sh e LEIA-ME.md
  6. RELEASE_MANIFEST.json com o hash de cada arquivo

Fora do pacote: testes, logs, .venv, tablebases (939 MB) e a cópia da NNUE (já vai no binário).
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


NNUE_ID = "nn-1a298aa575a0.nnue"
ENGINE_BENCH = 2497913


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


def stage_vendored_chess(staging_dir: Path) -> str:
    """Copia python-chess (Python puro) para vendor/, com licença e metadados."""
    import chess

    if chess.__version__ != "1.11.2":
        raise RuntimeError(f"Expected chess==1.11.2, found {chess.__version__}")
    chess_dir = Path(chess.__file__).resolve().parent
    target = staging_dir / "vendor"
    ignore = {"__pycache__", ".DS_Store"}
    copy_tree_filtered(chess_dir, target / "chess", ignore)
    dist_info = list(chess_dir.parent.glob(f"chess-{chess.__version__}*.dist-info"))
    if not dist_info:
        raise RuntimeError("chess==1.11.2 dist-info and license are required in the release")
    copy_tree_filtered(dist_info[0], target / dist_info[0].name, ignore)
    return chess.__version__


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
        if item.is_file() and item.suffix in (".py", ".html"):
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
            if f in ignore_engine or f.endswith((".o", ".pyc", ".nnue")):
                continue
            source_file = Path(root) / f
            if source_file.is_symlink() and not source_file.resolve().is_relative_to(src_code.resolve()):
                raise RuntimeError(f"Engine source symlink escapes source tree: {source_file}")
            shutil.copy2(source_file, target_dir / f)

    net_path = src_code / NNUE_ID
    if not net_path.is_file():
        raise RuntimeError(f"Default NNUE not found at {net_path}")
    return sha256_file(net_path)


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
        target_engine = target_bin_dir / "stockfish"
        shutil.copy2(engine_bin, target_engine)
        os.chmod(target_engine, 0o755)
        binary_hash = sha256_file(target_engine)
        print(f"Staged engine binary: {target_engine.name} (SHA-256: {binary_hash})")

        # 2. Stage controller
        stage_controller_source(repo_root, staging_base)

        book_src = repo_root / "assets" / "book.bin"
        if not book_src.is_file():
            raise RuntimeError(f"Opening book missing: {book_src}")
        (staging_base / "assets").mkdir()
        shutil.copy2(book_src, staging_base / "assets" / "book.bin")

        # 3. Stage python-chess
        chess_ver = stage_vendored_chess(staging_base)

        # 4. Stage Engine source and NNUE build input
        nnue_hash = stage_engine_source(repo_root, staging_base)

        # 5. Stage Launcher
        launcher_src = repo_root / "release" / "launch_stockfish.sh"
        if not launcher_src.is_file():
            raise RuntimeError(f"Launcher script missing at: {launcher_src}")
        target_launcher = staging_base / "launch_stockfish.sh"
        shutil.copy2(launcher_src, target_launcher)
        os.chmod(target_launcher, 0o755)

        # 6. Stage README
        readme_content = f"""# Stockfish 19 para o III Chess Challenge

Programa offline para Mac Apple Silicon (testado no M5; feito para M4 e M5).
Engine: Stockfish 19 com o gerenciador de tempo YoulossTM. Interface, gerenciador de
tempo e repertório de aberturas: autoria da equipe Youloss.

Gerado em {datetime.now(timezone.utc).date().isoformat()} a partir do commit {commit[:10]} (alterações locais: {is_dirty}).

## Como usar

No Terminal, dentro desta pasta:

    ./launch_stockfish.sh --dry-run   # confere o Mac; rode antes da partida
    ./launch_stockfish.sh             # abre o tabuleiro no navegador

Se o macOS recusar a execução: `bash launch_stockfish.sh`. É preciso ter python3
(`xcode-select --install`, com internet, se ainda não houver).

## Durante a partida

1. Escolha a cor, o adversário e inicie junto com o relógio físico.
2. Digite o lance do adversário e tecle Enter: e2e4, e7e8q, Nf3, Cf3 ou O-O.
3. O nosso lance aparece em destaque e no tabuleiro. Jogue-o e aperte o relógio.

O relógio da tela é estimativa; o físico é a referência. Use "Corrigir relógio" se
divergir. "Desfazer" volta para antes do último lance do adversário. Não feche a
tampa do Mac: mantenha na tomada. Logs ficam em `logs/`.

Tablebases de finais (939 MB) não vêm no pacote: copie a pasta `assets/syzygy` para cá e elas
são usadas automaticamente. A tela inicial deve mostrar "com tablebases".

## Licença

GPLv3. Código-fonte em `engine/`; origem e verificação em `engine/ORIGIN.md`.
A rede NNUE está embutida em `bin/stockfish` (comando UCI `export_net` a extrai).
"""
        (staging_base / "LEIA-ME.md").write_text(readme_content, encoding="utf-8")

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
            "manifest_version": "2.0",
            "package_name": "stockfish-chess-challenge",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "architecture": f"{platform.machine()}-{sys.platform}",
            "source_commit": commit,
            "git_dirty": is_dirty,
            "candidate_mode": candidate_mode,
            "binary_path": "bin/stockfish",
            "binary_hash": binary_hash,
            "engine_bench": ENGINE_BENCH,
            "chess_version": chess_ver,
            "nnue_id": NNUE_ID,
            "nnue_sha256": nnue_hash,
            "exact_run_settings": {
                "threads": "auto",
                "hash_mb": "auto",
                "time_control": "1500+0",
                "clock_latency_s": 2.0,
            },
            "absent_optional_assets": {
                "polyglot_book": "assets/book.bin",
                "syzygy_tablebases": "absent",
            },
            "open_items": {
                "physical_board_qualification": "OPEN",
            },
            "organizer_acceptance": "CONFIRMED by project owner report on 2026-11-04",
            "gpl_compliance": {
                "license": "GPLv3 (see engine/Copying.txt)",
                "origin": "Stockfish 19 + YoulossTM (see engine/ORIGIN.md)",
                "source_included": True,
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
                    tarinfo.uname = "stockfish"
                    tarinfo.gname = "stockfish"
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
    p = argparse.ArgumentParser(description="Build the offline Stockfish release package.")
    p.add_argument(
        "--output",
        type=Path,
        default=Path("dist/stockfish-chess-challenge.tar.gz"),
        help="Path for output archive (default: dist/stockfish-chess-challenge.tar.gz)",
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
        default=Path("bin/stockfish"),
        help="Path to engine binary (default: bin/stockfish)",
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

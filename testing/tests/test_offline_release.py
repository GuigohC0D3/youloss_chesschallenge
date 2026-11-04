"""Focused fail-closed checks for the offline candidate verifier."""

import json
import subprocess
import tarfile

import pytest

from scripts.verify_offline_release import (
    VerificationError,
    check_archive_safety,
    verify_engine_uci,
    verify_manifest,
)


class Members:
    def __init__(self, *members):
        self.members = members

    def getmembers(self):
        return self.members


@pytest.mark.parametrize("name", ["/tmp/escape", "../escape", "root/../../escape"])
def test_archive_rejects_escaping_member(name):
    with pytest.raises(VerificationError):
        check_archive_safety(Members(tarfile.TarInfo(name)))


def test_archive_rejects_duplicate_member():
    with pytest.raises(VerificationError, match="Duplicate"):
        check_archive_safety(Members(tarfile.TarInfo("same"), tarfile.TarInfo("same")))


def test_archive_rejects_escaping_symlink():
    link = tarfile.TarInfo("python/lib/alias")
    link.type = tarfile.SYMTYPE
    link.linkname = "../../../outside"
    with pytest.raises(VerificationError, match="escapes"):
        check_archive_safety(Members(link))


def test_manifest_rejects_path_traversal(tmp_path):
    manifest = {
        "manifest_version": "1.0", "package_name": "test", "created_at": "test",
        "architecture": "arm64-darwin", "source_commit": "a" * 40,
        "git_dirty": True, "candidate_mode": True, "binary_path": "bin/stockfish",
        "binary_hash": "0" * 64, "engine_bench": 2497913,
        "chess_version": "1.11.2", "nnue_id": "net.nnue",
        "exact_run_settings": {
            "threads": "auto", "hash_mb": "auto", "time_control": "1500+0",
            "clock_latency_s": 2.0,
        },
        "absent_optional_assets": {
            "polyglot_book": "absent", "syzygy_tablebases": "absent",
        },
        "open_items": {
            "physical_board_qualification": "OPEN", "organizer_acceptance": "OPEN",
        },
        "gpl_compliance": {},
        "files": {"../outside": {"sha256": "0" * 64, "size": 0}},
    }
    (tmp_path / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest))
    with pytest.raises(VerificationError, match="escapes package"):
        verify_manifest(tmp_path)


def test_uci_timeout_is_reported(tmp_path, monkeypatch):
    binary = tmp_path / "bin" / "stockfish"
    binary.parent.mkdir()
    binary.write_text("fake")

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 10)

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(VerificationError, match="timed out"):
        verify_engine_uci(tmp_path)

"""Focused fail-closed harness checks (no assets, no build, no match runs).

Covers testing/check_fastchess_log.sh behavior via fixture logs plus
static fail-closed constraints on testing/tm_match.sh and
scripts/build_fastchess.sh.
"""

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "testing" / "check_fastchess_log.sh"
TM_MATCH = ROOT / "testing" / "tm_match.sh"
BUILD = ROOT / "scripts" / "build_fastchess.sh"
FETCH_OPENINGS = ROOT / "scripts" / "fetch_openings.sh"

FIXED_CLEAN = """\
Results of tm vs sf (10+0.1, 1t, 16MB, UHO_Lichess_4852_v1.epd):
Elo: 1.25 +/- 3.40, nElo: 2.10 +/- 5.70
Games: 200, Wins: 50, Losses: 48, Draws: 102, Points: 101.0 (50.50 %)
Ptnml(0-2): [2, 20, 54, 22, 2], WL/DD Ratio: 1.00
"""

SPRT_H1 = """\
Results of tm vs sf (60+0.6, 1t, 16MB, UHO_Lichess_4852_v1.epd):
Elo: 1.25 +/- 3.40, nElo: 2.10 +/- 5.70
Games: 4000, Wins: 900, Losses: 886, Draws: 2214, Points: 2007.0 (50.18 %)
LLR: 2.96 (100.5%) (-2.94, 2.94) [-5.00, 0.00]
SPRT ([-5.00, 0.00]) completed - H1 was accepted
"""

SPRT_H0 = SPRT_H1.replace("LLR: 2.96 (100.5%)", "LLR: -2.96 (-100.5%)").replace(
    "H1 was accepted", "H0 was accepted"
)

# Pinned fastchess v1.8.2-alpha prints "H1 was accepted" on max-round
# exhaustion even when the SPRT verdict is still CONTINUE: final LLR is
# in-bounds, so this must be rejected as inconclusive.
SPRT_MISLEADING_H1_AT_CAP = """\
Results of tm vs sf (60+0.6, 1t, 16MB, UHO_Lichess_4852_v1.epd):
Elo: 0.40 +/- 3.10, nElo: 0.70 +/- 5.20
Games: 100000, Wins: 20000, Losses: 19950, Draws: 60050, Points: 50025.0 (50.03 %)
LLR: 1.10 (37.4%) (-2.94, 2.94) [-5.00, 0.00]
SPRT ([-5.00, 0.00]) completed - H1 was accepted
"""


def run_checker(
    tmp_path: Path, text: str | None, *args: str
) -> subprocess.CompletedProcess[str]:
    log = tmp_path / "match.log"
    if text is not None:
        log.write_text(text, encoding="utf-8")
    return subprocess.run(
        ["bash", str(CHECK), str(log), *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def run_opening_fetch(tmp_path: Path, expected: bytes, downloaded: bytes):
    """Run the downloader in an isolated fake repo with a local ZIP response."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "assets").mkdir()
    (repo / ".venv" / "bin").mkdir(parents=True)
    (repo / "scripts" / "fetch_openings.sh").write_bytes(FETCH_OPENINGS.read_bytes())
    (repo / "scripts" / "platform.sh").write_bytes(
        (ROOT / "scripts" / "platform.sh").read_bytes()
    )
    manifest = repo / "assets" / "MANIFEST"
    expected_sha = hashlib.sha256(expected).hexdigest()
    manifest_bytes = f"{expected_sha} *openings/UHO_Lichess_4852_v1.epd\n".encode()
    manifest.write_bytes(manifest_bytes)

    fixture_zip = tmp_path / "uho.zip"
    with zipfile.ZipFile(fixture_zip, "w") as archive:
        archive.writestr("UHO_Lichess_4852_v1.epd", downloaded)

    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake_curl = fake_bin / "curl"
    fake_curl.write_text(
        "#!/bin/sh\n"
        "set -eu\n"
        'while [ "$#" -gt 0 ]; do\n'
        '  if [ "$1" = \'-o\' ]; then cp "$FIXTURE_ZIP" "$2"; shift 2; '
        "else shift; fi\n"
        "done\n",
        encoding="utf-8",
    )
    fake_curl.chmod(0o755)
    python = repo / ".venv" / "bin" / "python"
    python.write_text('#!/bin/sh\nexec "$TEST_REAL_PYTHON" "$@"\n', encoding="utf-8")
    python.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["FIXTURE_ZIP"] = str(fixture_zip)
    env["TEST_REAL_PYTHON"] = sys.executable
    result = subprocess.run(
        ["bash", str(repo / "scripts" / "fetch_openings.sh")],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    opening = repo / "assets" / "openings" / "UHO_Lichess_4852_v1.epd"
    return result, manifest, manifest_bytes, opening


def test_opening_fetch_checks_manifest_hash_without_rewriting_it(tmp_path):
    expected = b"position 1\n"
    result, manifest, original_manifest, opening = run_opening_fetch(
        tmp_path, expected, b"different position data\n"
    )
    assert result.returncode != 0
    assert "checksum" in result.stderr
    assert manifest.read_bytes() == original_manifest
    assert not opening.exists()


def test_fixed_clean_passes(tmp_path):
    r = run_checker(tmp_path, FIXED_CLEAN, "--expect-games", "200")
    assert r.returncode == 0, r.stderr
    assert "PASS" in r.stdout


def test_fixed_expect_games_mismatch_fails(tmp_path):
    r = run_checker(tmp_path, FIXED_CLEAN, "--expect-games", "201")
    assert r.returncode == 1
    assert "!= esperado" in r.stderr


def test_games_summary_counts_must_reconcile(tmp_path):
    text = FIXED_CLEAN.replace("Losses: 48", "Losses: 49")
    r = run_checker(tmp_path, text, "--expect-games", "200")
    assert r.returncode == 1
    assert "Wins + Losses + Draws" in r.stderr


def test_missing_games_summary_fails(tmp_path):
    r = run_checker(
        tmp_path, "Elo: 1.0 +/- 2.0\nLLR: 0.1 (1%) (-2.94, 2.94) [-5.00, 0.00]\n"
    )
    assert r.returncode == 1
    assert "Games" in r.stderr


def test_zero_games_fails(tmp_path):
    r = run_checker(tmp_path, FIXED_CLEAN.replace("Games: 200,", "Games: 0,"))
    assert r.returncode == 1
    assert "nenhuma partida" in r.stderr


def test_fixed_malformed_games_junk_fails(tmp_path):
    """Numeric Games count followed by junk must fail as malformed."""
    text = FIXED_CLEAN.replace(
        "Games: 200, Wins: 50, Losses: 48, Draws: 102, Points: 101.0 (50.50 %)",
        "Games: 200oops, Wins: 50, Losses: 48, Draws: 102, Points: 101.0 (50.50 %)",
    )
    r = run_checker(tmp_path, text, "--expect-games", "200")
    assert r.returncode == 1
    assert "malformado" in r.stderr


def test_fixed_malformed_games_fields_fails(tmp_path):
    """Games row with missing/malformed summary fields must fail."""
    text = FIXED_CLEAN.replace(
        "Games: 200, Wins: 50, Losses: 48, Draws: 102, Points: 101.0 (50.50 %)",
        "Games: 200, Wins: 50, Losses: 48, Points: 101.0 (50.50 %)",
    )
    r = run_checker(tmp_path, text, "--expect-games", "200")
    assert r.returncode == 1
    assert "malformado" in r.stderr


def test_fixed_truncated_missing_penta_fails(tmp_path):
    """Fixed report with matching Games but no final Ptnml row must fail."""
    text = "".join(
        line + "\n"
        for line in FIXED_CLEAN.splitlines()
        if not line.startswith("Ptnml(0-2):")
    )
    assert "Games: 200," in text
    assert "Ptnml(0-2):" not in text
    r = run_checker(tmp_path, text, "--expect-games", "200")
    assert r.returncode == 1
    assert "Ptnml" in r.stderr


def test_fixed_all_zero_pentanomial_fails(tmp_path):
    text = FIXED_CLEAN.replace(
        "Ptnml(0-2): [2, 20, 54, 22, 2], WL/DD Ratio: 1.00",
        "Ptnml(0-2): [0, 0, 0, 0, 0], WL/DD Ratio: nan",
    )
    r = run_checker(tmp_path, text, "--expect-games", "200")
    assert r.returncode == 1
    assert "Ptnml" in r.stderr


@pytest.mark.parametrize(
    "bad_penta",
    [
        "Ptnml(0-2): [0, 0, 0, 0, 0], WL/DD Ratio: nan",
        "Ptnml(0-2): [2, 20, 54, 22, 1], WL/DD Ratio: 1.00",
    ],
)
def test_fixed_penta_pair_counts_must_reconcile(tmp_path, bad_penta):
    text = FIXED_CLEAN.replace(
        "Ptnml(0-2): [2, 20, 54, 22, 2], WL/DD Ratio: 1.00", bad_penta
    )
    r = run_checker(tmp_path, text, "--expect-games", "200")
    assert r.returncode == 1
    assert "Ptnml" in r.stderr


@pytest.mark.parametrize(
    "line",
    [
        "Finished game 3 (tm vs sf): 0-1 (White loses on time)",
        "Warning: engine disconnect detected on sf",
        "Finished game 7 (tm vs sf): 1-0 (illegal move by Black)",
        "Error: engine crash (signal 11) on tm",
        "Warning: sf stalls for 60s, adjudicating",
    ],
)
def test_incident_classes_fail(tmp_path, line):
    r = run_checker(tmp_path, FIXED_CLEAN + line + "\n", "--expect-games", "200")
    assert r.returncode == 1, line
    assert "incidente" in r.stderr


def test_sprt_h1_crossing_passes(tmp_path):
    r = run_checker(tmp_path, SPRT_H1, "--sprt", "-5", "0")
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize(
    "bad_line",
    [
        "LLR: 3.0oops (101.5%) (-2.94, 2.94) [-5.00, 0.00]",
        "LLR: 2.96 (100.5oops%) (-2.94, 2.94) [-5.00, 0.00]",
        "LLR: 2.96 (100.5%) (-2.94oops, 2.94) [-5.00, 0.00]",
        "LLR: 2.96 (100.5%) (-2.94, 2.94oops) [-5.00, 0.00]",
        "LLR: 2.96 (100.5%) (-2.94, 2.94) [-5.00oops, 0.00]",
    ],
)
def test_sprt_malformed_numeric_field_in_full_llr_row_fails(tmp_path, bad_line):
    original = "LLR: 2.96 (100.5%) (-2.94, 2.94) [-5.00, 0.00]"
    text = SPRT_H1.replace(original, bad_line)
    r = run_checker(tmp_path, text, "--sprt", "-5", "0")
    assert r.returncode == 1
    assert "malform" in r.stderr


def test_sprt_rounded_h1_boundary_is_inconclusive(tmp_path):
    """A printed 2.94 is ambiguous against the exact upper SPRT threshold."""
    text = SPRT_H1.replace("LLR: 2.96 (100.5%)", "LLR: 2.94 (100.0%)")
    r = run_checker(tmp_path, text, "--sprt", "-5", "0")
    assert r.returncode == 1
    assert "inconclusivo" in r.stderr


def test_sprt_h0_crossing_passes(tmp_path):
    r = run_checker(tmp_path, SPRT_H0, "--sprt", "-5", "0")
    assert r.returncode == 0, r.stderr


def test_sprt_misleading_h1_at_cap_fails(tmp_path):
    """In-bounds final LLR + textual H1 phrase must fail closed."""
    r = run_checker(tmp_path, SPRT_MISLEADING_H1_AT_CAP, "--sprt", "-5", "0")
    assert r.returncode == 1
    assert "inconclusivo" in r.stderr


def test_sprt_inconclusive_without_marker_fails(tmp_path):
    text = SPRT_MISLEADING_H1_AT_CAP.replace(
        "SPRT ([-5.00, 0.00]) completed - H1 was accepted", ""
    )
    r = run_checker(tmp_path, text, "--sprt", "-5", "0")
    assert r.returncode == 1
    assert "inconclusivo" in r.stderr


def test_sprt_marker_mismatch_fails(tmp_path):
    text = SPRT_H1.replace("H1 was accepted", "H0 was accepted")
    r = run_checker(tmp_path, text, "--sprt", "-5", "0")
    assert r.returncode == 1
    assert "malformado" in r.stderr


def test_sprt_missing_llr_fails(tmp_path):
    r = run_checker(tmp_path, FIXED_CLEAN, "--sprt", "-5", "0")
    assert r.returncode == 1
    assert "LLR" in r.stderr


def test_sprt_configured_bounds_mismatch_fails(tmp_path):
    r = run_checker(tmp_path, SPRT_H1, "--sprt", "-5", "5")
    assert r.returncode == 1
    assert "bounds" in r.stderr


def test_missing_log_fails(tmp_path):
    r = run_checker(tmp_path, None)
    assert r.returncode == 1


def test_tm_match_failclosed_constraints():
    text = TM_MATCH.read_text(encoding="utf-8")
    assert "-srand" in text  # reproducible opening seed
    assert "TIME_CAP_S" in text  # configurable wall-clock cap
    assert "check_fastchess_log.sh" in text  # incident checker always runs
    assert "--expect-games" in text  # exact count for fixed runs
    assert "--sprt" in text  # bound-crossing verdict for SPRT
    assert "meta.json" in text  # per-run metadata record
    assert "config.json" in text  # per-run dir, no overwrite
    assert "PIPESTATUS" in text or "STATUS_F" in text  # runner/tee status propagation
    assert (
        re.search(r"(?:^|\s)-noswap(?:\s|$|\"|')", text) is None
    )  # intended color-paired behavior kept
    assert (
        re.search(r"(?:^|\s)-recover(?:\s|$|\"|')", text) is None
    )  # no incident-hiding restart
    # Fanless M4 safety defaults: 1 match concurrency and 30m screening cap
    assert 'CONC="${CONC:-1}"' in text
    assert 'THREADS="${THREADS:-1}"' in text
    assert 'HASH_MB="${HASH_MB:-16}"' in text
    assert 'MOVE_OVERHEAD_MS="${MOVE_OVERHEAD_MS:-1500}"' in text
    assert 'TIME_CAP_S="${TIME_CAP_S:-1800}"' in text
    assert (
        '"option.Threads=$THREADS" "option.Hash=$HASH_MB" '
        '"option.Move Overhead=$MOVE_OVERHEAD_MS"'
    ) in text
    assert '"threads": %s' in text and '"hash_mb": %s' in text
    assert '"move_overhead_ms": %s' in text
    assert '"syzygy_enabled": %s' in text
    assert '"syzygy_fingerprint": %s' in text
    assert '"sf_engine_sha256": "%s"' in text
    assert "SF_ENGINE" in text


def test_build_fastchess_pin_matches_tm_match():
    build = BUILD.read_text(encoding="utf-8")
    tm = TM_MATCH.read_text(encoding="utf-8")
    assert "v1.8.2-alpha" in build
    assert "f618e34540f94f4719ad3817950618dabe441318" in build
    assert "ls-remote" in build and "rev-parse HEAD" in build
    m_tag = re.search(r'FASTCHESS_TAG="([^"]+)"', tm)
    m_commit = re.search(r'FASTCHESS_COMMIT="([^"]+)"', tm)
    assert m_tag and m_commit
    assert m_tag.group(1) in build
    assert m_commit.group(1) in build


def test_tm_match_rundir_is_collision_safe():
    """Repeated same-parameter runs must not overwrite: mktemp -d + basename."""
    text = TM_MATCH.read_text(encoding="utf-8")
    assert "mktemp -d" in text
    assert "XXXXXX" in text  # random suffix template
    assert 'mkdir -p "$RUNDIR"' not in text  # created atomically, not mkdir -p
    assert "basename" in text  # NAME derived from the created dir
    assert '"rundir"' in text  # recorded path unambiguous in meta.json
    # Timestamp prefix kept for readability, uniqueness from mktemp suffix.
    assert "date +%Y%m%d-%H%M%S" in text


def test_build_fastchess_writes_pinned_sidecar():
    build = BUILD.read_text(encoding="utf-8")
    assert "fastchess.build.json" in build
    assert '"tag"' in build
    assert '"commit"' in build
    assert '"sha256"' in build
    assert "v1.8.2-alpha" in build
    assert "f618e34540f94f4719ad3817950618dabe441318" in build


def test_tm_match_validates_pinned_sidecar():
    text = TM_MATCH.read_text(encoding="utf-8")
    assert "fastchess.build.json" in text
    assert "SIDECAR_TAG" in text
    assert "SIDECAR_COMMIT" in text
    assert "SIDECAR_SHA" in text
    assert "sidecar ausente" in text  # fail-closed when sidecar missing
    assert "FASTCHESS_SHA" in text
    # Verified values recorded in meta.json.
    assert "runner_sidecar" in text
    assert "runner_tag_verified" in text
    assert "runner_commit_verified" in text
    assert "runner_sha256_verified" in text
    # Verified pairing behavior preserved.
    assert "-games" in text
    assert re.search(r"(?:^|\s)-noswap(?:\s|$|\"|')", text) is None
    assert re.search(r"(?:^|\s)-recover(?:\s|$|\"|')", text) is None


def _make_fake_root(tmp_path: Path) -> Path:
    """Scaffold a minimal fake ROOT so tm_match runs with stub binaries.

    No real build, download, game, or long SPRT: fake fastchess exits
    nonzero immediately after printing to stdout+stderr.
    """
    fake = tmp_path / "fakeroot"
    (fake / "scripts").mkdir(parents=True)
    (fake / "testing").mkdir(parents=True)
    (fake / "assets" / "openings").mkdir(parents=True)
    (fake / "tools").mkdir(parents=True)
    (fake / "bin").mkdir(parents=True)
    shutil.copy(ROOT / "scripts" / "platform.sh", fake / "scripts" / "platform.sh")
    shutil.copy(
        ROOT / "testing" / "check_fastchess_log.sh",
        fake / "testing" / "check_fastchess_log.sh",
    )
    shutil.copy(ROOT / "testing" / "tm_match.sh", fake / "testing" / "tm_match.sh")
    for mod in ["__init__.py", "time_profile.py", "sprt_result.py"]:
        src = ROOT / "testing" / mod
        if src.exists():
            shutil.copy(src, fake / "testing" / mod)
    (fake / "assets" / "openings" / "UHO_Lichess_4852_v1.epd").write_text(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\n",
        encoding="utf-8",
    )
    eng = fake / "bin" / "youloss"
    eng.write_text("#!/usr/bin/env bash\necho fake-engine\n", encoding="utf-8")
    eng.chmod(0o755)
    fc = fake / "tools" / "fastchess"
    fc.write_text(
        "#!/usr/bin/env bash\n"
        'printf \'%s\\n\' "$@" > "$FAKE_FASTCHESS_ARGS"\n'
        "echo 'FAKE-STDOUT-MARKER'\n"
        "echo 'FAKE-STDERR-MARKER' >&2\n"
        "exit 1\n",
        encoding="utf-8",
    )
    fc.chmod(0o755)
    import hashlib

    sha = hashlib.sha256(fc.read_bytes()).hexdigest()
    (fake / "tools" / "fastchess.build.json").write_text(
        json.dumps(
            {
                "tag": "v1.8.2-alpha",
                "commit": "f618e34540f94f4719ad3817950618dabe441318",
                "sha256": sha,
            }
        ),
        encoding="utf-8",
    )
    venv_bin = fake / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    link = venv_bin / "python"
    if not link.exists():
        os.symlink(sys.executable, link)
    return fake


@pytest.mark.parametrize(
    ("time_control", "move_overhead_ms"),
    [
        ("60+0", "1000"),
        ("60+0", "1500"),
        ("10+0.1", "1500"),
    ],
)
def test_tm_match_rejects_overhead_above_scaled_budget_policy(
    tmp_path, time_control, move_overhead_ms
):
    fake = _make_fake_root(tmp_path)
    result = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), time_control, "1"],
        cwd=str(fake),
        env=dict(
            os.environ,
            CONC="1",
            MOVE_OVERHEAD_MS=move_overhead_ms,
            SRAND="12345",
        ),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 2
    assert "exceeds the 10% initial-budget policy" in result.stderr
    assert "10%" in result.stderr
    assert not (fake / "logs" / "sprt").exists()


@pytest.mark.parametrize(
    ("time_control", "move_overhead_ms"),
    [("60+0", "60"), ("1500+0", "1500")],
)
def test_tm_match_allows_calibrated_overhead_horizons(
    tmp_path, time_control, move_overhead_ms
):
    fake = _make_fake_root(tmp_path)
    args_file = fake / "fastchess-args.txt"
    result = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), time_control, "1"],
        cwd=str(fake),
        env=dict(
            os.environ,
            CONC="1",
            MOVE_OVERHEAD_MS=move_overhead_ms,
            TIME_CAP_S="7000",
            SRAND="12345",
            FAKE_FASTCHESS_ARGS=str(args_file),
        ),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    # The stub intentionally exits nonzero after printing; reaching it proves
    # the calibrated control passed preflight and match setup.
    assert result.returncode != 0
    assert "FAKE-STDOUT-MARKER" in result.stdout
    assert f"option.Move Overhead={move_overhead_ms}" in args_file.read_text()
    rundirs = list((fake / "logs" / "sprt").glob("tm_*"))
    assert len(rundirs) == 1
    meta = json.loads((rundirs[0] / "meta.json").read_text(encoding="utf-8"))
    assert meta["move_overhead_ms"] == int(move_overhead_ms)


@pytest.mark.parametrize(
    "bad_tc",
    [
        "60",
        "60+",
        "+0",
        "60+0+0",
        "invalid",
        "60+abc",
        "-10+0",
        "0+0",
    ],
)
def test_tm_match_rejects_unsupported_or_malformed_time_control(tmp_path, bad_tc):
    fake = _make_fake_root(tmp_path)
    result = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), bad_tc, "1"],
        cwd=str(fake),
        env=dict(os.environ, CONC="1", SRAND="12345"),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 2
    assert "FAIL:" in result.stderr
    assert not (fake / "logs" / "sprt").exists()


@pytest.mark.parametrize(
    ("tc", "rounds", "time_cap_s", "should_fail"),
    [
        ("60+0", "1", "200", True),
        ("60+0", "1", "270", False),
        ("1500+0", "1", "1800", True),
        ("1500+0", "1", "6030", False),
    ],
)
def test_tm_match_zero_increment_time_cap_preflight(
    tmp_path, tc, rounds, time_cap_s, should_fail
):
    fake = _make_fake_root(tmp_path)
    args_file = fake / "fastchess-args.txt"
    overhead = "60" if tc == "60+0" else "1500"
    result = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), tc, rounds],
        cwd=str(fake),
        env=dict(
            os.environ,
            CONC="1",
            MOVE_OVERHEAD_MS=overhead,
            TIME_CAP_S=time_cap_s,
            SRAND="12345",
            FAKE_FASTCHESS_ARGS=str(args_file),
        ),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    if should_fail:
        assert result.returncode == 2
        assert "cannot cover maximum clock time" in result.stderr
        assert not (fake / "logs" / "sprt").exists()
    else:
        assert result.returncode != 0
        assert "cannot cover maximum clock time" not in result.stderr
        assert "FAKE-STDOUT-MARKER" in result.stdout


def test_tm_match_does_not_reject_incremented_or_sprt_cap_without_bound(tmp_path):
    fake = _make_fake_root(tmp_path)
    args_file = fake / "fastchess-args.txt"
    # Incremented control with TIME_CAP_S smaller than 4 * base:
    # 10+0.1 with TIME_CAP_S=15 (4*10 = 40s > 15s) must not fail cap preflight
    r1 = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=dict(
            os.environ,
            CONC="1",
            MOVE_OVERHEAD_MS="20",
            TIME_CAP_S="15",
            SRAND="12345",
            FAKE_FASTCHESS_ARGS=str(args_file),
        ),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert "cannot cover maximum clock time" not in r1.stderr
    assert "FAKE-STDOUT-MARKER" in r1.stdout

    # SPRT run with 60+0, 100 rounds, default TIME_CAP_S=1800 (100*4*60 = 24000s > 1800s)
    # SPRT terminates on early bound crossing, must not be rejected by zero-increment fixed run preflight
    r2 = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "60+0", "100", "-5", "0"],
        cwd=str(fake),
        env=dict(
            os.environ,
            CONC="1",
            MOVE_OVERHEAD_MS="60",
            TIME_CAP_S="1800",
            SRAND="12345",
            FAKE_FASTCHESS_ARGS=str(args_file),
        ),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert "cannot cover maximum clock time" not in r2.stderr
    assert "FAKE-STDOUT-MARKER" in r2.stdout


def _run_fake_tm(fake: Path) -> subprocess.CompletedProcess[str]:
    env = dict(
        os.environ,
        CONC="1",
        MOVE_OVERHEAD_MS="20",
        TIME_CAP_S="15",
        SRAND="12345",
        FAKE_FASTCHESS_ARGS=str(fake / "fastchess-args.txt"),
    )
    return subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


@pytest.mark.parametrize(
    "elo_args",
    [("-5",), ("", "0")],
)
def test_tm_match_rejects_partial_sprt_bounds_before_starting_run(tmp_path, elo_args):
    fake = _make_fake_root(tmp_path)
    result = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1", *elo_args],
        cwd=str(fake),
        env=dict(os.environ, CONC="1", SRAND="12345"),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 2
    assert "elo0 e elo1 devem ser fornecidos juntos" in result.stderr
    assert not (fake / "logs" / "sprt").exists()


def test_tm_match_synthetic_nonzero_runner_fails_closed(tmp_path):
    """Fake nonzero fastchess must fail closed with stdout+stderr captured.

    The fake runner exits immediately, so each run must return well before
    TIME_CAP_S=15: the watchdog timer is cancelled/reaped on normal
    completion and never holds the tee pipe open.
    """
    fake = _make_fake_root(tmp_path)
    start = time.monotonic()
    r = _run_fake_tm(fake)
    elapsed = time.monotonic() - start
    assert elapsed < 10, f"watchdog held tee pipe: {elapsed:.1f}s >= 10s"
    assert r.returncode != 0
    # Checker always runs even on runner nonzero.
    assert "checker reprovou" in r.stderr or "FAIL" in r.stderr
    rundirs = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    assert len(rundirs) == 1
    rundir = rundirs[0]
    log = rundir / "match.log"
    assert log.is_file()
    content = log.read_text(encoding="utf-8")
    assert "FAKE-STDOUT-MARKER" in content  # stdout captured via tee
    assert "FAKE-STDERR-MARKER" in content  # stderr captured via 2>&1 | tee
    meta_path = rundir / "meta.json"
    assert meta_path.is_file()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["exit_fastchess"] == "1"
    assert meta["exit_checker"] != "0"
    assert meta["runner_tag_verified"] == "v1.8.2-alpha"
    assert meta["runner_commit_verified"] == "f618e34540f94f4719ad3817950618dabe441318"
    assert meta["runner_sha256_verified"] == meta["runner_sha256"]
    assert meta["rundir"] == str(rundir)
    assert meta["name"] == rundir.name
    assert meta["move_overhead_ms"] == 20
    assert (
        "option.Move Overhead=20"
        in (fake / "fastchess-args.txt").read_text().splitlines()
    )
    # Same-parameter second run must land in a distinct directory (no overwrite).
    start2 = time.monotonic()
    r2 = _run_fake_tm(fake)
    elapsed2 = time.monotonic() - start2
    assert elapsed2 < 10, f"watchdog held tee pipe: {elapsed2:.1f}s >= 10s"
    assert r2.returncode != 0
    rundirs2 = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    assert len(rundirs2) == 2
    assert rundirs2[0].name != rundirs2[1].name


def _write_term_ignoring_runner(fake: Path) -> None:
    """Replace fastchess with a TERM-ignoring parent and a pipe-holding child."""
    fc = fake / "tools" / "fastchess"
    fc.write_text(
        "#!/usr/bin/env bash\n"
        "trap '' TERM\n"
        "echo 'FAKE-STDOUT-MARKER'\n"
        "echo 'FAKE-STDERR-MARKER' >&2\n"
        "sleep 8 &\n"
        "child=$!\n"
        'if [ -n "${FAKE_CHILD_PID_FILE:-}" ]; then echo "$child" >"$FAKE_CHILD_PID_FILE"; fi\n'
        'wait "$child"\n',
        encoding="utf-8",
    )
    fc.chmod(0o755)
    import hashlib

    sha = hashlib.sha256(fc.read_bytes()).hexdigest()
    sidecar = fake / "tools" / "fastchess.build.json"
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    data["sha256"] = sha
    sidecar.write_text(json.dumps(data), encoding="utf-8")


def _run_fake_timeout_tm(fake: Path) -> subprocess.CompletedProcess[str]:
    env = dict(
        os.environ,
        CONC="1",
        MOVE_OVERHEAD_MS="20",
        TIME_CAP_S="1",
        KILL_GRACE_S="1",
        SRAND="12345",
        FAKE_CHILD_PID_FILE=str(fake / "child.pid"),
    )
    return subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_tm_match_synthetic_timeout_fails_closed(tmp_path):
    """Timeout must kill runner descendants that would otherwise hold tee open."""
    fake = _make_fake_root(tmp_path)
    _write_term_ignoring_runner(fake)
    start = time.monotonic()
    r = _run_fake_timeout_tm(fake)
    elapsed = time.monotonic() - start
    assert elapsed < 6, f"timeout left a pipe-holding child alive: {elapsed:.1f}s >= 6s"
    assert r.returncode != 0
    # Checker always runs, even on the incomplete timeout log.
    assert "checker reprovou" in r.stderr or "FAIL" in r.stderr
    rundirs = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    assert len(rundirs) == 1
    rundir = rundirs[0]
    log = rundir / "match.log"
    assert log.is_file()
    content = log.read_text(encoding="utf-8")
    assert "FAKE-STDOUT-MARKER" in content  # stdout captured via tee
    assert "FAKE-STDERR-MARKER" in content  # stderr captured via 2>&1 | tee
    meta_path = rundir / "meta.json"
    assert meta_path.is_file()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["timeout"] == 1
    assert meta["kill_grace_s"] == 1
    assert meta["exit_fastchess"] != "0"
    assert "timeout" in str(meta["exit_fastchess"])  # runner failure recorded
    assert meta["exit_checker"] != "0"
    assert meta["runner_tag_verified"] == "v1.8.2-alpha"
    assert meta["runner_commit_verified"] == "f618e34540f94f4719ad3817950618dabe441318"
    assert meta["runner_sha256_verified"] == meta["runner_sha256"]
    assert meta["rundir"] == str(rundir)
    assert meta["name"] == rundir.name
    # Watchdog timer/grace children cleaned up on timeout.
    assert not (rundir / ".watchdog.sleep.pid").exists()
    assert (rundir / ".timeout").is_file()


def _write_runner_with_live_descendant(fake: Path, child_pid_file: Path) -> None:
    runner = fake / "tools" / "fastchess"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        "(trap '' TERM; sleep 30) &\n"
        "CHILD_PID=$!\n"
        'printf \'%s\\n\' "$CHILD_PID" >"$FAKE_CHILD_PID_FILE"\n'
        "echo 'FAKE-STDOUT-MARKER'\n"
        "echo 'FAKE-STDERR-MARKER' >&2\n"
        "exit 0\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)
    sidecar = fake / "tools" / "fastchess.build.json"
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    import hashlib

    data["sha256"] = hashlib.sha256(runner.read_bytes()).hexdigest()
    sidecar.write_text(json.dumps(data), encoding="utf-8")


def _pid_is_live(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    result = subprocess.run(
        ["ps", "-o", "stat=", "-p", str(pid)],
        capture_output=True,
        text=True,
        timeout=2,
        check=False,
    )
    state = result.stdout.strip()
    return bool(state) and not state.startswith("Z")


def test_tm_match_timeout_kills_descendant_holding_tee_pipe(tmp_path):
    fake = _make_fake_root(tmp_path)
    child_pid_file = tmp_path / "descendant.pid"
    _write_runner_with_live_descendant(fake, child_pid_file)
    env = dict(
        os.environ,
        CONC="1",
        MOVE_OVERHEAD_MS="20",
        TIME_CAP_S="1",
        KILL_GRACE_S="1",
        SRAND="12345",
        FAKE_CHILD_PID_FILE=str(child_pid_file),
    )
    proc = subprocess.Popen(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    start = time.monotonic()
    timed_out = False
    child_alive_at_timeout = False
    try:
        stdout, stderr = proc.communicate(timeout=4)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            child_pid = int(child_pid_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            child_pid = -1
        child_alive_at_timeout = child_pid > 0 and _pid_is_live(child_pid)
        # Bound RED cleanup too: terminate the isolated test process group.
        if child_pid > 0:
            try:
                os.killpg(os.getpgid(child_pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = proc.communicate(timeout=3)
    elapsed = time.monotonic() - start
    try:
        child_pid = int(child_pid_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        child_pid = -1

    assert not timed_out, f"tee stayed open after cap+grace ({elapsed:.2f}s)"
    assert elapsed < 4
    assert proc.returncode != 0
    assert "FAKE-STDOUT-MARKER" in stdout
    assert "FAKE-STDERR-MARKER" in stdout + stderr
    rundirs = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    assert len(rundirs) == 1
    meta = json.loads((rundirs[0] / "meta.json").read_text(encoding="utf-8"))
    assert meta["timeout"] == 1
    assert "timeout" in str(meta["exit_fastchess"])
    assert child_pid > 0
    assert not child_alive_at_timeout
    assert not _pid_is_live(child_pid)


def test_build_fastchess_creates_missing_tools_dir(tmp_path):
    """Fresh-clone bootstrap: builder must create ignored tools/ before clone.

    No network / no build: stubbed git + make. The git stub fails the
    clone when the destination parent is missing, so this test fails if
    mkdir -p "$ROOT/tools" does not precede git clone, and passes only
    when the builder creates tools/ itself.
    """
    build = BUILD.read_text(encoding="utf-8")
    mkdir_idx = build.index('mkdir -p "$ROOT/tools"')
    clone_idx = build.index("git clone")
    assert mkdir_idx < clone_idx, "mkdir tools/ must precede git clone"

    fake = tmp_path / "fcroot"
    (fake / "scripts").mkdir(parents=True)
    shutil.copy(ROOT / "scripts" / "platform.sh", fake / "scripts" / "platform.sh")
    shutil.copy(BUILD, fake / "scripts" / "build_fastchess.sh")
    assert not (fake / "tools").exists()  # fresh-clone precondition

    stubbin = tmp_path / "stubbin"
    stubbin.mkdir(parents=True)
    pinned = "f618e34540f94f4719ad3817950618dabe441318"
    git_stub = stubbin / "git"
    git_stub.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'PINNED="{pinned}"\n'
        'if [ "${1:-}" = "ls-remote" ]; then\n'
        '  printf "%s\\trefs/tags/v1.8.2-alpha\\n" "$PINNED"\n'
        "  exit 0\n"
        "fi\n"
        'if [ "${1:-}" = "clone" ]; then\n'
        '  dest="${@: -1}"\n'
        '  parent="$(dirname "$dest")"\n'
        '  if [ ! -d "$parent" ]; then\n'
        '    echo "FAIL: parent $parent missing (fresh-clone bootstrap)" >&2\n'
        "    exit 1\n"
        "  fi\n"
        '  mkdir -p "$dest"\n'
        '  printf "%s\\n" "$PINNED" > "$dest/.stub-head"\n'
        "  exit 0\n"
        "fi\n"
        'if [ "${1:-}" = "-C" ]; then\n'
        '  if [ "${3:-}" = "rev-parse" ]; then\n'
        '    printf "%s\\n" "$PINNED"\n'
        "    exit 0\n"
        "  fi\n"
        "fi\n"
        'echo "stub git: unhandled args: $*" >&2\n'
        "exit 1\n",
        encoding="utf-8",
    )
    make_stub = stubbin / "make"
    make_stub.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'SRCDIR=""\n'
        'PREV=""\n'
        'for a in "$@"; do\n'
        '  if [ "$PREV" = "-C" ]; then SRCDIR="$a"; fi\n'
        '  PREV="$a"\n'
        "done\n"
        '[ -n "$SRCDIR" ] || { echo "stub make: missing -C" >&2; exit 1; }\n'
        'mkdir -p "$SRCDIR"\n'
        'printf "#!/usr/bin/env bash\\necho stub-fastchess\\n" > "$SRCDIR/fastchess"\n'
        'chmod +x "$SRCDIR/fastchess"\n'
        'printf "#!/usr/bin/env bash\\necho stub-fastchess\\n" > "$SRCDIR/fastchess.exe"\n'
        'chmod +x "$SRCDIR/fastchess.exe"\n'
        "exit 0\n",
        encoding="utf-8",
    )
    git_stub.chmod(0o755)
    make_stub.chmod(0o755)

    env = dict(os.environ, PATH=str(stubbin) + os.pathsep + os.environ.get("PATH", ""))
    r = subprocess.run(
        ["bash", str(fake / "scripts" / "build_fastchess.sh")],
        cwd=str(fake),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"
    assert (fake / "tools").is_dir()  # builder created missing parent
    assert (fake / "tools" / "fastchess-src").is_dir()
    binaries = [
        p
        for p in [
            fake / "tools" / "fastchess",
            fake / "tools" / "fastchess.exe",
        ]
        if p.is_file()
    ]
    assert binaries, "stubbed build must produce tools/fastchess binary"
    sidecar = fake / "tools" / "fastchess.build.json"
    assert sidecar.is_file()
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert data["tag"] == "v1.8.2-alpha"
    assert data["commit"] == pinned
    import hashlib

    assert data["sha256"] == hashlib.sha256(binaries[0].read_bytes()).hexdigest()


def test_tm_match_external_baseline_command_arguments_and_metadata(tmp_path):
    """External baseline binary must be invoked without YoulossTM option,

    and recorded in meta.json with its SHA, label, and options description.
    """
    fake = _make_fake_root(tmp_path)
    sf_ext = fake / "bin" / "stockfish_official"
    sf_ext.write_text("#!/usr/bin/env bash\necho fake-sf19\n", encoding="utf-8")
    sf_ext.chmod(0o755)
    import hashlib

    sf_sha = hashlib.sha256(sf_ext.read_bytes()).hexdigest()
    youloss_sha = hashlib.sha256((fake / "bin" / "youloss").read_bytes()).hexdigest()
    assert sf_sha != youloss_sha

    args_file = fake / "fastchess-args.txt"
    env = dict(
        os.environ,
        CONC="1",
        MOVE_OVERHEAD_MS="20",
        TIME_CAP_S="15",
        SRAND="12345",
        SF_ENGINE=str(sf_ext),
        SF_ENGINE_LABEL="sf19-official",
        FAKE_FASTCHESS_ARGS=str(args_file),
    )
    r = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert r.returncode != 0  # fake fastchess exits 1
    args = args_file.read_text().splitlines()

    # tm side has option.YoulossTM=true
    assert f"cmd={fake / 'bin' / 'youloss'}" in args
    assert "option.YoulossTM=true" in args

    # sf side points to external binary and DOES NOT have YoulossTM
    assert f"cmd={sf_ext}" in args
    assert "option.YoulossTM=false" not in args

    rundirs = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    assert len(rundirs) == 1
    meta = json.loads((rundirs[0] / "meta.json").read_text(encoding="utf-8"))
    assert meta["engine"] == str(fake / "bin" / "youloss")
    assert meta["engine_sha256"] == youloss_sha
    assert meta["sf_engine"] == str(sf_ext)
    assert meta["sf_engine_sha256"] == sf_sha
    assert meta["sf_engine_label"] == "sf19-official"
    assert meta["sf_engine_options"] == "external:sf19-official"
    assert "sf: external:sf19-official;" in meta["engine_options"]


def test_tm_match_applies_identical_syzygy_to_both_engines_and_records_it(tmp_path):
    fake = _make_fake_root(tmp_path)
    syzygy = fake / "assets" / "syzygy"
    syzygy.mkdir()
    contents = {
        "KQvK.rtbw": b"wdl-table-data",
        "KQvK.rtbz": b"dtz-table-data",
    }
    manifest_rows = []
    for name, data in contents.items():
        (syzygy / name).write_bytes(data)
        manifest_rows.append(f"{hashlib.sha256(data).hexdigest()} *syzygy/{name}\n")
    (fake / "assets" / "MANIFEST").write_text("".join(manifest_rows), encoding="utf-8")

    sf_ext = fake / "bin" / "stockfish_official"
    sf_ext.write_text("#!/usr/bin/env bash\necho fake-sf19\n", encoding="utf-8")
    sf_ext.chmod(0o755)
    args_file = fake / "fastchess-args.txt"
    result = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=dict(
            os.environ,
            CONC="1",
            MOVE_OVERHEAD_MS="20",
            TIME_CAP_S="15",
            SRAND="12345",
            SYZYGY_PATH=str(syzygy),
            SF_ENGINE=str(sf_ext),
            FAKE_FASTCHESS_ARGS=str(args_file),
        ),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode != 0  # fake fastchess stops after recording arguments
    args = args_file.read_text(encoding="utf-8").splitlines()
    syzygy_path = str(syzygy.resolve())
    assert args.count(f"option.SyzygyPath={syzygy_path}") == 1
    assert args.count("option.SyzygyProbeLimit=5") == 1
    assert "-each" in args

    rundirs = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    assert len(rundirs) == 1
    meta = json.loads((rundirs[0] / "meta.json").read_text(encoding="utf-8"))
    expected_fingerprint = hashlib.sha256(
        "".join(
            f"syzygy/{name} {hashlib.sha256(data).hexdigest()}\n"
            for name, data in sorted(contents.items())
        ).encode()
    ).hexdigest()
    assert meta["syzygy_enabled"] is True
    assert meta["syzygy_path"] == syzygy_path
    assert meta["syzygy_wdl_files"] == 1
    assert meta["syzygy_dtz_files"] == 1
    assert meta["syzygy_probe_limit"] == 5
    assert meta["syzygy_fingerprint_source"] == "asset_manifest"
    assert meta["syzygy_fingerprint"] == expected_fingerprint
    assert "Syzygy=true" in meta["engine_options"]


def test_tm_match_can_explicitly_disable_available_syzygy_tables(tmp_path):
    fake = _make_fake_root(tmp_path)
    syzygy = fake / "assets" / "syzygy"
    syzygy.mkdir()
    (syzygy / "KQvK.rtbw").write_bytes(b"wdl-table-data")
    (syzygy / "KQvK.rtbz").write_bytes(b"dtz-table-data")
    args_file = fake / "fastchess-args.txt"
    result = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=dict(
            os.environ,
            CONC="1",
            MOVE_OVERHEAD_MS="20",
            TIME_CAP_S="15",
            SRAND="12345",
            SYZYGY_PATH="",
            FAKE_FASTCHESS_ARGS=str(args_file),
        ),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode != 0
    args = args_file.read_text(encoding="utf-8").splitlines()
    assert not any(arg.startswith("option.Syzygy") for arg in args)
    rundirs = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    meta = json.loads((rundirs[0] / "meta.json").read_text(encoding="utf-8"))
    assert meta["syzygy_enabled"] is False
    assert meta["syzygy_path"] == ""
    assert meta["syzygy_wdl_files"] == 0
    assert meta["syzygy_dtz_files"] == 0
    assert meta["syzygy_probe_limit"] is None
    assert meta["syzygy_fingerprint_source"] == "none"
    assert meta["syzygy_fingerprint"] == ""


def test_tm_match_hashes_tables_from_external_directory(tmp_path):
    fake = _make_fake_root(tmp_path)
    syzygy = tmp_path / "external tables"
    syzygy.mkdir()
    contents = {
        "KQvK.rtbw": b"external-wdl",
        "KQvK.rtbz": b"external-dtz",
    }
    for name, data in contents.items():
        (syzygy / name).write_bytes(data)

    args_file = fake / "fastchess-args.txt"
    result = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=dict(
            os.environ,
            CONC="1",
            MOVE_OVERHEAD_MS="20",
            TIME_CAP_S="15",
            SRAND="12345",
            SYZYGY_PATH=str(syzygy),
            FAKE_FASTCHESS_ARGS=str(args_file),
        ),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode != 0
    assert f"option.SyzygyPath={syzygy.resolve()}" in args_file.read_text().splitlines()
    rundirs = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    meta = json.loads((rundirs[0] / "meta.json").read_text(encoding="utf-8"))
    expected_fingerprint = hashlib.sha256(
        "".join(
            f"{name} {hashlib.sha256(data).hexdigest()}\n"
            for name, data in sorted(contents.items())
        ).encode()
    ).hexdigest()
    assert meta["syzygy_path"] == str(syzygy.resolve())
    assert meta["syzygy_fingerprint_source"] == "content_sha256"
    assert meta["syzygy_fingerprint"] == expected_fingerprint


def test_tm_match_rejects_unpaired_syzygy_tables(tmp_path):
    fake = _make_fake_root(tmp_path)
    syzygy = fake / "assets" / "syzygy"
    syzygy.mkdir()
    (syzygy / "KQvK.rtbw").write_bytes(b"wdl-table-data")

    result = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=dict(
            os.environ,
            CONC="1",
            MOVE_OVERHEAD_MS="20",
            TIME_CAP_S="15",
            SYZYGY_PATH=str(syzygy),
        ),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 2
    assert "WDL/DTZ files must be present in matching counts" in result.stderr
    assert not (fake / "fastchess-args.txt").exists()


def test_tm_match_external_baseline_default_label(tmp_path):
    fake = _make_fake_root(tmp_path)
    sf_ext = fake / "bin" / "stockfish_official"
    sf_ext.write_text("#!/usr/bin/env bash\necho fake-sf\n", encoding="utf-8")
    sf_ext.chmod(0o755)

    args_file = fake / "fastchess-args.txt"
    env = dict(
        os.environ,
        CONC="1",
        MOVE_OVERHEAD_MS="20",
        TIME_CAP_S="15",
        SRAND="12345",
        SF_ENGINE=str(sf_ext),
        FAKE_FASTCHESS_ARGS=str(args_file),
    )
    r = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert r.returncode != 0
    rundirs = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    assert len(rundirs) == 1
    meta = json.loads((rundirs[0] / "meta.json").read_text(encoding="utf-8"))
    assert meta["sf_engine_label"] == "stockfish-baseline"
    assert meta["sf_engine_options"] == "external:stockfish-baseline"


def test_tm_match_same_binary_baseline_options_and_metadata(tmp_path):
    fake = _make_fake_root(tmp_path)
    args_file = fake / "fastchess-args.txt"
    env = dict(
        os.environ,
        CONC="1",
        MOVE_OVERHEAD_MS="20",
        TIME_CAP_S="15",
        SRAND="12345",
        FAKE_FASTCHESS_ARGS=str(args_file),
    )
    r = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert r.returncode != 0
    args = args_file.read_text().splitlines()
    assert "option.YoulossTM=false" in args

    rundirs = sorted((fake / "logs" / "sprt").glob("tm_10+0.1_r1_*"))
    assert len(rundirs) == 1
    meta = json.loads((rundirs[0] / "meta.json").read_text(encoding="utf-8"))
    assert meta["sf_engine_sha256"] == meta["engine_sha256"]
    assert meta["sf_engine_label"] == "YoulossTM-off"
    assert meta["sf_engine_options"] == "YoulossTM=false"
    assert "sf: YoulossTM=false;" in meta["engine_options"]


def test_tm_match_rejects_missing_or_nonexecutable_sf_engine(tmp_path):
    fake = _make_fake_root(tmp_path)
    r = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=dict(
            os.environ,
            MOVE_OVERHEAD_MS="20",
            SF_ENGINE=str(fake / "bin" / "nonexistent_engine"),
        ),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert r.returncode == 2
    assert "baseline engine ausente ou nao executavel" in r.stderr


def test_tm_match_rejects_invalid_sf_engine_label(tmp_path):
    fake = _make_fake_root(tmp_path)
    r = subprocess.run(
        ["bash", str(fake / "testing" / "tm_match.sh"), "10+0.1", "1"],
        cwd=str(fake),
        env=dict(
            os.environ,
            MOVE_OVERHEAD_MS="20",
            SF_ENGINE_LABEL="invalid label with spaces",
        ),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert r.returncode == 2
    assert "SF_ENGINE_LABEL deve usar apenas letras" in r.stderr

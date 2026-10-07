import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "testing" / "continuous_screening.sh"
PY = sys.executable


def is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def supervisor_record(
    pid: int, script_argument: Path, canonical_path: Path, cwd: Path
) -> dict:
    lstart = subprocess.run(
        ["ps", "-p", str(pid), "-o", "lstart="],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return {
        "pid": pid,
        "lstart": lstart,
        "canonical_path": str(canonical_path),
        "script_argument": str(script_argument),
        "working_directory": str(cwd),
    }


def test_status_when_stopped(tmp_path):
    res = subprocess.run(
        ["bash", str(SCRIPT), "status"],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "State: STOPPED" in res.stdout


def test_stop_when_not_running(tmp_path):
    res = subprocess.run(
        ["bash", str(SCRIPT), "stop"],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "No screening process running." in res.stdout


def test_start_preserves_lock_with_unverifiable_owner(tmp_path):
    lock_dir = tmp_path / "supervisor.lock"
    lock_dir.mkdir()
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 1
    assert "owner cannot be verified" in res.stderr
    assert lock_dir.is_dir()


def test_rejects_concurrent_instance_and_race_safe(tmp_path):
    # Test concurrent startup race safety
    proc1 = subprocess.Popen(
        ["bash", str(SCRIPT), "start"],
        env=dict(
            os.environ,
            SCREENING_DIR=str(tmp_path),
            MOCK_POWER_FAIL="stop_preflight_1",
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    proc2 = subprocess.Popen(
        ["bash", str(SCRIPT), "start"],
        env=dict(
            os.environ,
            SCREENING_DIR=str(tmp_path),
            MOCK_POWER_FAIL="stop_preflight_2",
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    _out1, _err1 = proc1.communicate(timeout=5)
    _out2, _err2 = proc2.communicate(timeout=5)

    # Both must terminate; if one acquired lock and failed preflight, the other saw lock
    assert proc1.returncode != 0
    assert proc2.returncode != 0


def test_stop_does_not_signal_unrelated_bash_pid(tmp_path):
    # Spawn a fake unrelated bash process (e.g. sleep 20)
    fake_proc = subprocess.Popen(["bash", "-c", "sleep 20"])
    fake_pid = fake_proc.pid

    # Write fake PID record pointing to the unrelated bash process
    pid_file = tmp_path / "screening.pid"
    data = {
        "pid": fake_pid,
        "lstart": "fake_lstart",
        "canonical_path": "/fake/path/continuous_screening.sh",
    }
    pid_file.write_text(json.dumps(data), encoding="utf-8")

    res = subprocess.run(
        ["bash", str(SCRIPT), "stop"],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Leaving unharmed" in res.stdout
    # The unrelated bash process must still be alive!
    assert is_alive(fake_pid)

    # Clean up fake process
    fake_proc.terminate()
    fake_proc.wait(timeout=2)


def test_stop_rejects_bash_c_that_mentions_screening_script(tmp_path):
    fake_proc = subprocess.Popen(
        ["bash", "-c", f"echo {SCRIPT}; read -t 30 _"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    pid_file = tmp_path / "screening.pid"
    record = supervisor_record(fake_proc.pid, SCRIPT, SCRIPT, ROOT)
    pid_file.write_text(json.dumps(record), encoding="utf-8")

    res = subprocess.run(
        ["bash", str(SCRIPT), "stop"],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Leaving unharmed" in res.stdout
    assert is_alive(fake_proc.pid)
    fake_proc.terminate()
    fake_proc.wait(timeout=2)


def test_stop_rejects_direct_bash_with_wrong_canonical_script(tmp_path):
    fake_script = tmp_path / "continuous_screening.sh"
    fake_script.write_text("read -t 30 _\n", encoding="utf-8")
    fake_proc = subprocess.Popen(
        ["bash", str(fake_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        cwd=tmp_path,
    )
    pid_file = tmp_path / "screening.pid"
    record = supervisor_record(fake_proc.pid, fake_script, SCRIPT, tmp_path)
    pid_file.write_text(json.dumps(record), encoding="utf-8")

    res = subprocess.run(
        ["bash", str(SCRIPT), "stop"],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Leaving unharmed" in res.stdout
    assert is_alive(fake_proc.pid)
    fake_proc.terminate()
    fake_proc.wait(timeout=2)


def test_running_supervisor_has_exact_validated_identity_and_stops_cleanly(tmp_path):
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake_caffeinate = fake_bin / "caffeinate"
    fake_caffeinate.write_text(
        f"#!/bin/bash\nexec {sys.executable} -c 'import time; time.sleep(60)'\n",
        encoding="utf-8",
    )
    fake_caffeinate.chmod(0o755)
    fake_bash = fake_bin / "bash"
    fake_bash.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_bash.chmod(0o755)

    env = dict(
        os.environ,
        PATH=f"{fake_bin}:{os.environ['PATH']}",
        SCREENING_DIR=str(tmp_path / "screening"),
        MOCK_POWER_OUTPUT="Now drawing from 'AC Power'\n-InternalBattery-0 100%; charged\n",
        MOCK_THERM_OUTPUT=(
            "Note: No thermal warning level has been recorded\n"
            "Note: No performance warning level has been recorded\n"
        ),
        MOCK_MEM_FREE_PCT="50",
        MOCK_SWAP_USED_MB="0",
        MOCK_SWAP_FREE_MB="4096",
        MIN_DISK_MB="0",
        MIN_FREE_SWAP_MB="2048",
        MIN_FREE_MEM_PCT="10",
        DEADLINE_S="30",
        PAUSE_S="2",
    )
    proc = subprocess.Popen(
        ["/bin/bash", str(SCRIPT), "start"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    pid_file = Path(env["SCREENING_DIR"]) / "screening.pid"
    try:
        for _ in range(50):
            if pid_file.is_file():
                status = subprocess.run(
                    ["/bin/bash", str(SCRIPT), "status"],
                    cwd=ROOT,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                if "State: RUNNING" in status.stdout:
                    break
            time.sleep(0.05)
        else:
            raise AssertionError(
                "supervisor never published a validated running PID record"
            )

        stopped = subprocess.run(
            ["/bin/bash", str(SCRIPT), "stop"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        assert stopped.returncode == 0, stopped.stderr
        assert "Stopping validated screening supervisor" in stopped.stdout
        proc.wait(timeout=5)
        assert not (Path(env["SCREENING_DIR"]) / "supervisor.lock").exists()
    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=5)


def test_scoreboard_accumulation_and_status(tmp_path):
    batch_dir = tmp_path / "batch_001"
    batch_dir.mkdir()
    meta = {
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
        "timeout": 0,
        "expected_games": 10,
        "completed_games": 10,
    }
    (batch_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (batch_dir / "match.log").write_text(
        "Games: 10, Wins: 4, Losses: 2, Draws: 4, Points: 6.0 (60.00 %)\n",
        encoding="utf-8",
    )

    scoreboard_file = tmp_path / "scoreboard.json"

    res = subprocess.run(
        [
            "bash",
            "-c",
            f'source "{SCRIPT}" && update_scoreboard "{batch_dir}"',
        ],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, f"update_scoreboard failed: {res.stdout}\n{res.stderr}"

    assert scoreboard_file.is_file()
    with scoreboard_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["batches_completed"] == 1
    assert data["total_games"] == 10
    assert data["youloss_wins"] == 4
    assert data["baseline_wins"] == 2
    assert data["draws"] == 4

    status_res = subprocess.run(
        ["bash", str(SCRIPT), "status"],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Total Games Played : 10" in status_res.stdout
    assert "4W - 4D - 2L" in status_res.stdout
    assert "Score Percentage   : 60.00% (6.0/10)" in status_res.stdout


def test_scoreboard_recalculates_legacy_derived_fields(tmp_path):
    scoreboard_file = tmp_path / "scoreboard.json"
    scoreboard_file.write_text(
        json.dumps(
            {
                "started_at": "2026-10-03T00:00:00+00:00",
                "batches_completed": 10,
                "batches_failed": 0,
                "total_games": 100,
                "youloss_wins": 20,
                "baseline_wins": 30,
                "draws": 50,
                "points": 16.5,
                "score_pct": 41.25,
                "recent_batches": [],
                "incidents": [],
            }
        ),
        encoding="utf-8",
    )
    batch_dir = tmp_path / "batch_001"
    batch_dir.mkdir()
    meta = {
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
        "timeout": 0,
        "expected_games": 10,
        "completed_games": 10,
    }
    (batch_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (batch_dir / "match.log").write_text(
        "Games: 10, Wins: 4, Losses: 2, Draws: 4, Points: 6.0 (60.00 %)\n",
        encoding="utf-8",
    )

    res = subprocess.run(
        ["bash", "-c", f'source "{SCRIPT}" && update_scoreboard "{batch_dir}"'],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=False,
    )

    assert res.returncode == 0, f"update_scoreboard failed: {res.stdout}\n{res.stderr}"
    data = json.loads(scoreboard_file.read_text(encoding="utf-8"))
    assert data["total_games"] == 110
    assert data["youloss_wins"] == 24
    assert data["baseline_wins"] == 32
    assert data["draws"] == 54
    assert data["points"] == 51.0
    assert data["score_pct"] == 46.36


def test_scoreboard_uses_final_fastchess_summary(tmp_path):
    batch_dir = tmp_path / "batch_periodic_summaries"
    batch_dir.mkdir()
    meta = {
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
        "timeout": 0,
        "expected_games": 100,
        "completed_games": 100,
    }
    (batch_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (batch_dir / "match.log").write_text(
        "Games: 20, Wins: 5, Losses: 4, Draws: 11, Points: 10.5 (52.50 %)\n"
        "Games: 100, Wins: 26, Losses: 24, Draws: 50, Points: 51.0 (51.00 %)\n",
        encoding="utf-8",
    )

    res = subprocess.run(
        ["bash", "-c", f'source "{SCRIPT}" && update_scoreboard "{batch_dir}"'],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=False,
    )

    assert res.returncode == 0, f"update_scoreboard failed: {res.stdout}\n{res.stderr}"
    assert res.stdout.strip() == "completed"
    data = json.loads((tmp_path / "scoreboard.json").read_text(encoding="utf-8"))
    assert data["batches_completed"] == 1
    assert data["total_games"] == 100
    assert data["youloss_wins"] == 26
    assert data["baseline_wins"] == 24
    assert data["draws"] == 50


def test_scoreboard_excludes_failed_batch_and_atomic_write(tmp_path):
    batch_dir = tmp_path / "batch_failed"
    batch_dir.mkdir()
    # Checker failed and time profile failed
    meta = {
        "exit_fastchess": 0,
        "exit_checker": 1,
        "exit_time_profile": 1,
        "exit_tee": 0,
        "timeout": 0,
        "expected_games": 10,
        "completed_games": 10,
    }
    (batch_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (batch_dir / "match.log").write_text(
        "Games: 10, Wins: 10, Losses: 0, Draws: 0, Points: 10.0 (100.00 %)\n",
        encoding="utf-8",
    )

    scoreboard_file = tmp_path / "scoreboard.json"

    res = subprocess.run(
        [
            "bash",
            "-c",
            f'source "{SCRIPT}" && update_scoreboard "{batch_dir}"',
        ],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0

    assert scoreboard_file.is_file()
    with scoreboard_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["batches_completed"] == 0
    assert data["batches_failed"] == 1
    assert data["total_games"] == 0
    assert data["youloss_wins"] == 0
    assert len(data["incidents"]) == 1
    assert "Checker exited with non-zero status" in data["incidents"][0]["reason"]


def test_scoreboard_rejects_nonzero_supervisor_child_even_if_metadata_says_success(
    tmp_path,
):
    batch_dir = tmp_path / "batch_child_failed"
    batch_dir.mkdir()
    meta = {
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
        "timeout": 0,
        "expected_games": 10,
        "completed_games": 10,
    }
    (batch_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (batch_dir / "match.log").write_text(
        "Games: 10, Wins: 10, Losses: 0, Draws: 0, Points: 10.0 (100.00 %)\n",
        encoding="utf-8",
    )

    res = subprocess.run(
        [
            "bash",
            "-c",
            f'source "{SCRIPT}" && update_scoreboard "{batch_dir}" 7',
        ],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert res.stdout.strip() == "failed"
    data = json.loads((tmp_path / "scoreboard.json").read_text(encoding="utf-8"))
    assert data["batches_completed"] == 0
    assert data["total_games"] == 0
    assert (
        "Match child exited with non-zero status (7)" in data["incidents"][0]["reason"]
    )


def test_scoreboard_requires_completed_game_count(tmp_path):
    batch_dir = tmp_path / "batch_missing_count"
    batch_dir.mkdir()
    meta = {
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
        "timeout": 0,
        "expected_games": 1,
        "completed_games": None,
    }
    (batch_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (batch_dir / "match.log").write_text(
        "Games: 1, Wins: 1, Losses: 0, Draws: 0, Points: 1.0 (100.00 %)\n",
        encoding="utf-8",
    )

    res = subprocess.run(
        ["bash", "-c", f'source "{SCRIPT}" && update_scoreboard "{batch_dir}"'],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert res.stdout.strip() == "failed"
    data = json.loads((tmp_path / "scoreboard.json").read_text(encoding="utf-8"))
    assert data["total_games"] == 0
    assert "Missing meta.completed_games" in data["incidents"][0]["reason"]


def test_unreadable_power_telemetry_halts(tmp_path):
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        env=dict(
            os.environ,
            SCREENING_DIR=str(tmp_path),
            MOCK_POWER_FAIL="simulated_pmset_io_error",
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 1
    assert "SAFETY STOP" in res.stderr
    assert "Power telemetry unreadable" in res.stderr
    assert not (tmp_path / "screening.pid").is_file()


def test_thermal_warning_and_memory_telemetry_halts(tmp_path):
    ac_power_mock = "Now drawing from 'AC Power'\n -InternalBattery-0 100%; charged\n"
    # 1. Thermal throttle warning
    res_therm = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        env=dict(
            os.environ,
            SCREENING_DIR=str(tmp_path),
            MOCK_POWER_OUTPUT=ac_power_mock,
            MOCK_THERM_FAIL="CPU throttled to 50%",
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res_therm.returncode == 1
    assert "System thermal/performance warning" in res_therm.stderr

    # 2. Swap usage below 2048 MiB (using host evidence 1236.5 MiB)
    res_swap = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        env=dict(
            os.environ,
            SCREENING_DIR=str(tmp_path),
            MOCK_POWER_OUTPUT=ac_power_mock,
            MOCK_SWAP_FREE_MB="1236.5",
            MIN_FREE_SWAP_MB="2048",
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res_swap.returncode == 1
    assert "Free swap (1236.50 MiB) < minimum threshold" in res_swap.stderr


def test_thermal_parser_accepts_real_no_warning_output_and_fails_closed(tmp_path):
    ac_power = "Now drawing from 'AC Power'\n-InternalBattery-0 100%; charged\n"
    safe_base = dict(
        os.environ,
        SCREENING_DIR=str(tmp_path),
        MOCK_POWER_OUTPUT=ac_power,
        MOCK_MEM_FREE_PCT="50",
        MOCK_SWAP_USED_MB="0",
        MOCK_SWAP_FREE_MB="4096",
        MIN_DISK_MB="0",
        MIN_FREE_SWAP_MB="2048",
        MIN_FREE_MEM_PCT="10",
    )

    def run_check(therm: str) -> subprocess.CompletedProcess:
        env = dict(safe_base, MOCK_THERM_OUTPUT=therm)
        return subprocess.run(
            [
                "bash",
                "-c",
                f'source "{SCRIPT}" && check_safety_telemetry "$SCREENING_DIR"',
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    normal = run_check(
        "Note: No thermal warning level has been recorded\n"
        "Note: No performance warning level has been recorded\n"
        "Note: No CPU power status has been recorded\n"
    )
    assert normal.returncode == 0, normal.stderr

    warning = run_check("Thermal warning level 2\nPerformance warning level 0\n")
    assert warning.returncode == 15
    assert "thermal warning level 2" in warning.stderr.lower()

    throttled = run_check(
        "Note: No thermal warning level has been recorded\n"
        "Note: No performance warning level has been recorded\n"
        "CPU_Speed_Limit = 80\n"
    )
    assert throttled.returncode == 15
    assert "cpu speed limit is 80%" in throttled.stderr.lower()

    unknown = run_check("pmset changed its format unexpectedly\n")
    assert unknown.returncode == 15
    assert "unrecognized or incomplete" in unknown.stderr


def test_verified_child_cleanup_terminates_nonmatching_grandchild(tmp_path):
    token = f"token_test_{os.getpid()}_{int(time.time())}"
    cmd = [
        "bash",
        "-c",
        (
            f": 'tm_match.sh' 'token={token}'; "
            f"{sys.executable} -c '"
            "import subprocess, time; "
            'p = subprocess.Popen(["sleep", "100"]); '
            "time.sleep(100)' & "
            "wait"
        ),
    ]
    proc = subprocess.Popen(cmd)
    root_pid = proc.pid

    child_pid = None
    grandchild_pid = None
    for _ in range(30):
        time.sleep(0.1)
        child_pids = subprocess.run(
            ["pgrep", "-P", str(root_pid)], capture_output=True, text=True, check=False
        ).stdout.split()
        if child_pids:
            child_pid = int(child_pids[0])
            gc = subprocess.run(
                ["pgrep", "-P", str(child_pid)],
                capture_output=True,
                text=True,
                check=False,
            ).stdout.split()
            if gc:
                grandchild_pid = int(gc[0])
                break

    assert child_pid is not None, "Failed to spawn child process"
    assert grandchild_pid is not None, "Failed to spawn grandchild sleep process"

    assert is_alive(root_pid)
    assert is_alive(child_pid)
    assert is_alive(grandchild_pid)

    # 1. Invalid token MUST refuse to signal
    invalid_res = subprocess.run(
        [
            "bash",
            "-c",
            f'source "{SCRIPT}" && terminate_child_tree {root_pid} "wrong_token"',
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid_res.returncode != 0
    assert "does not match verified owned screening child" in invalid_res.stderr
    assert is_alive(root_pid)
    assert is_alive(child_pid)
    assert is_alive(grandchild_pid)

    # 2. Valid token: cleanup must terminate verified root AND all descendants
    cleanup_res = subprocess.run(
        [
            "bash",
            "-c",
            f'source "{SCRIPT}" && terminate_child_tree {root_pid} "{token}"',
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert cleanup_res.returncode == 0

    proc.wait(timeout=5)
    assert not is_alive(root_pid)
    assert not is_alive(child_pid)
    assert not is_alive(grandchild_pid)


def test_failing_child_exit_code_captured_on_failure(tmp_path):
    # Setup mock batch directory with a failing child run
    batch_dir = tmp_path / "batch_fail"
    batch_dir.mkdir()
    meta = {
        "exit_fastchess": 42,
        "exit_checker": 1,
        "exit_time_profile": 0,
        "exit_tee": 0,
        "timeout": 0,
        "expected_games": 10,
        "completed_games": 10,
    }
    (batch_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (batch_dir / "match.log").write_text(
        "Games: 10, Wins: 0, Losses: 10, Draws: 0, Points: 0.0 (0.00 %)\n",
        encoding="utf-8",
    )

    scoreboard_file = tmp_path / "scoreboard.json"
    res = subprocess.run(
        [
            "bash",
            "-c",
            f'source "{SCRIPT}" && update_scoreboard "{batch_dir}"',
        ],
        env=dict(os.environ, SCREENING_DIR=str(tmp_path)),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    with scoreboard_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["batches_failed"] == 1
    assert data["batches_completed"] == 0
    assert (
        "Fastchess exited with non-zero status (42)" in data["incidents"][0]["reason"]
    )


def test_swap_used_cap_telemetry(tmp_path):
    ac_power = "Now drawing from 'AC Power'\n-InternalBattery-0 100%; charged\n"
    base_env = dict(
        os.environ,
        SCREENING_DIR=str(tmp_path),
        MOCK_POWER_OUTPUT=ac_power,
        MOCK_MEM_FREE_PCT="50",
        MOCK_SWAP_FREE_MB="4096",
        MIN_DISK_MB="0",
        MIN_FREE_SWAP_MB="2048",
        MIN_FREE_MEM_PCT="10",
    )

    def check_telemetry(env_overrides: dict) -> subprocess.CompletedProcess:
        env = dict(base_env, **env_overrides)
        return subprocess.run(
            [
                "bash",
                "-c",
                f'source "{SCRIPT}" && check_safety_telemetry "$SCREENING_DIR"',
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    # 1. Just below default cap (20480 MiB): nominal pass (rc=0)
    res_below = check_telemetry({"MOCK_SWAP_USED_MB": "20479.9"})
    assert res_below.returncode == 0, res_below.stderr
    assert "swap_used=" in res_below.stdout

    # 2. Exactly at default cap (20480 MiB): fails closed (rc=20)
    res_at = check_telemetry({"MOCK_SWAP_USED_MB": "20480.0"})
    assert res_at.returncode == 20
    assert (
        "SAFETY_STOP: Swap used (20480.00 MiB) >= maximum threshold (20480.00 MiB)"
        in res_at.stderr
    )

    # 3. Above default cap (e.g. 21000 MiB): fails closed (rc=20)
    res_above = check_telemetry({"MOCK_SWAP_USED_MB": "21000.5"})
    assert res_above.returncode == 20
    assert (
        "SAFETY_STOP: Swap used (21000.50 MiB) >= maximum threshold (20480.00 MiB)"
        in res_above.stderr
    )

    # 4. Custom cap override: just below passes, at and above fail closed
    custom_cap_env = {"MAX_SWAP_USED_MB": "10240"}
    res_custom_below = check_telemetry(
        {**custom_cap_env, "MOCK_SWAP_USED_MB": "10239.0"}
    )
    assert res_custom_below.returncode == 0, res_custom_below.stderr

    res_custom_at = check_telemetry({**custom_cap_env, "MOCK_SWAP_USED_MB": "10240.0"})
    assert res_custom_at.returncode == 20
    assert (
        "SAFETY_STOP: Swap used (10240.00 MiB) >= maximum threshold (10240.00 MiB)"
        in res_custom_at.stderr
    )

    res_custom_above = check_telemetry(
        {**custom_cap_env, "MOCK_SWAP_USED_MB": "10500.0"}
    )
    assert res_custom_above.returncode == 20
    assert (
        "SAFETY_STOP: Swap used (10500.00 MiB) >= maximum threshold (10240.00 MiB)"
        in res_custom_above.stderr
    )


def test_swap_used_cap_halts_supervisor_preflight(tmp_path):
    ac_power_mock = "Now drawing from 'AC Power'\n -InternalBattery-0 100%; charged\n"
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        env=dict(
            os.environ,
            SCREENING_DIR=str(tmp_path),
            MOCK_POWER_OUTPUT=ac_power_mock,
            MOCK_SWAP_USED_MB="20480",
            MOCK_SWAP_FREE_MB="4096",
            MIN_DISK_MB="0",
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 1
    assert "SAFETY STOP before batch #1" in res.stderr
    assert "Swap used (20480.00 MiB) >= maximum threshold (20480.00 MiB)" in res.stderr
    assert not (tmp_path / "screening.pid").is_file()


def _write_stub_tm_match(stub_path: Path, mode_env_name: str = "STUB_MODE") -> None:
    stub_path.write_text(
        "#!/bin/bash\n"
        "set -euo pipefail\n"
        'tc="${1:-10+0.1}"\n'
        'rounds="${2:-1}"\n'
        'mode="${' + mode_env_name + ':-success}"\n'
        'screening_dir="${SCREENING_DIR:-/tmp}"\n'
        'batch_dir="$(mktemp -d "$screening_dir/stub_batch_XXXXXX")"\n'
        "expected=$(( rounds * 2 ))\n"
        'if [ "$mode" = "fail_validation" ]; then\n'
        '  printf \'{"exit_fastchess": 0, "exit_checker": 1, "exit_time_profile": 0, "exit_tee": 0, "timeout": 0, "expected_games": %s, "completed_games": %s}\' "$expected" "$expected" >"$batch_dir/meta.json"\n'
        '  printf \'Games: %s, Wins: %s, Losses: 0, Draws: 0, Points: %s.0 (100.00 %%)\\n\' "$expected" "$expected" "$expected" >"$batch_dir/match.log"\n'
        "else\n"
        "  wins=$(( expected / 2 ))\n"
        "  draws=$(( expected - wins ))\n"
        '  printf \'{"exit_fastchess": 0, "exit_checker": 0, "exit_time_profile": 0, "exit_tee": 0, "timeout": 0, "expected_games": %s, "completed_games": %s}\' "$expected" "$expected" >"$batch_dir/meta.json"\n'
        '  printf \'Games: %s, Wins: %s, Losses: 0, Draws: %s, Points: %s.0\\n\' "$expected" "$wins" "$draws" "$expected" >"$batch_dir/match.log"\n'
        "fi\n"
        'echo "rundir=$batch_dir"\n',
        encoding="utf-8",
    )
    stub_path.chmod(0o755)


def _bounded_env(tmp_path: Path, stub_path: Path, extra: dict | None = None) -> dict:
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir(exist_ok=True)
    fake_caffeinate = fake_bin / "caffeinate"
    if not fake_caffeinate.is_file():
        fake_caffeinate.write_text(
            f"#!/bin/bash\nexec {sys.executable} -c 'import time; time.sleep(60)'\n",
            encoding="utf-8",
        )
        fake_caffeinate.chmod(0o755)
    env = dict(
        os.environ,
        PATH=f"{fake_bin}:{os.environ['PATH']}",
        SCREENING_DIR=str(tmp_path / "screening"),
        TM_MATCH_SCRIPT=str(stub_path),
        MOCK_POWER_OUTPUT="Now drawing from 'AC Power'\n-InternalBattery-0 100%; charged\n",
        MOCK_THERM_OUTPUT=(
            "Note: No thermal warning level has been recorded\n"
            "Note: No performance warning level has been recorded\n"
        ),
        MOCK_MEM_FREE_PCT="50",
        MOCK_SWAP_USED_MB="0",
        MOCK_SWAP_FREE_MB="4096",
        MIN_DISK_MB="0",
        MIN_FREE_SWAP_MB="2048",
        MIN_FREE_MEM_PCT="10",
        DEADLINE_S="120",
        PAUSE_S="0",
        STUB_MODE="success",
    )
    if extra:
        env.update(extra)
    return env


def test_bounded_successful_completion(tmp_path):
    stub = tmp_path / "stub_tm_match.sh"
    _write_stub_tm_match(stub)
    env = _bounded_env(
        tmp_path,
        stub,
        extra={
            "MAX_BATCHES": "2",
            "ROUNDS_PER_BATCH": "5",
            "TC": "10+0.1",
            "STUB_MODE": "success",
        },
    )
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert res.returncode == 0, f"stdout={res.stdout}\nstderr={res.stderr}"
    combined = res.stdout + res.stderr
    assert "Bounded session complete: 2/2 validated batches." in combined
    screening_dir = Path(env["SCREENING_DIR"])
    run_log = (screening_dir / "continuous.log").read_text(encoding="utf-8")
    assert "Bounded session complete: 2/2 validated batches." in run_log
    data = json.loads((screening_dir / "scoreboard.json").read_text(encoding="utf-8"))
    assert data["batches_completed"] == 2
    assert data["batches_failed"] == 0
    # ROUNDS_PER_BATCH=5 -> 10 games per batch -> 20 total.
    assert data["total_games"] == 20
    assert not (screening_dir / "screening.pid").is_file()
    assert not (screening_dir / "supervisor.lock").exists()


def test_bounded_failed_batch_fails_closed(tmp_path):
    stub = tmp_path / "stub_tm_match.sh"
    _write_stub_tm_match(stub)
    env = _bounded_env(
        tmp_path,
        stub,
        extra={
            "MAX_BATCHES": "2",
            "ROUNDS_PER_BATCH": "5",
            "STUB_MODE": "fail_validation",
        },
    )
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert res.returncode == 1, f"stdout={res.stdout}\nstderr={res.stderr}"
    combined = res.stdout + res.stderr
    assert "Bounded session aborted" in combined
    screening_dir = Path(env["SCREENING_DIR"])
    run_log = (screening_dir / "continuous.log").read_text(encoding="utf-8")
    assert "Bounded session aborted" in run_log
    data = json.loads((screening_dir / "scoreboard.json").read_text(encoding="utf-8"))
    assert data["batches_completed"] == 0
    assert data["batches_failed"] == 1
    assert data["total_games"] == 0
    assert not (screening_dir / "screening.pid").is_file()


def test_bounded_invalid_max_batches_fails_closed(tmp_path):
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        env=dict(
            os.environ,
            SCREENING_DIR=str(tmp_path),
            MAX_BATCHES="not-a-number",
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 2
    assert "MAX_BATCHES" in res.stderr
    assert not (tmp_path / "screening.pid").is_file()
    assert not (tmp_path / "supervisor.lock").exists()


def test_startup_logs_effective_config_and_thresholds(tmp_path):
    stub = tmp_path / "stub_tm_match.sh"
    _write_stub_tm_match(stub)
    secret = "supersecret-xyz-123"
    env = _bounded_env(
        tmp_path,
        stub,
        extra={
            "MAX_BATCHES": "1",
            "ROUNDS_PER_BATCH": "5",
            "TC": "10+0.1",
            "THREADS": "1",
            "CONC": "1",
            "HASH_MB": "128",
            "MOVE_OVERHEAD_MS": "10",
            "TIME_CAP_S": "600",
            "DEADLINE_S": "120",
            "PAUSE_S": "0",
            "REQUIRE_AC": "0",
            "BATTERY_MIN": "20",
            "MAX_SWAP_USED_MB": "1536",
            "MIN_FREE_SWAP_MB": "512",
            "MIN_FREE_MEM_PCT": "10",
            "MIN_DISK_MB": "500",
            "STUB_MODE": "success",
            "DEFINITELY_NOT_A_REAL_SECRET": secret,
        },
    )
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert res.returncode == 0, f"stdout={res.stdout}\nstderr={res.stderr}"
    run_log = (Path(env["SCREENING_DIR"]) / "continuous.log").read_text(
        encoding="utf-8"
    )
    for needle in [
        "TC=10+0.1",
        "ROUNDS_PER_BATCH=5",
        "MAX_BATCHES=1",
        "THREADS=1",
        "CONC=1",
        "HASH_MB=128",
        "MOVE_OVERHEAD_MS=10",
        "TIME_CAP_S=600",
        "DEADLINE_S=120",
        "PAUSE_S=0",
        "REQUIRE_AC=0",
        "BATTERY_MIN=20",
        "MAX_SWAP_USED_MB=1536",
        "MIN_FREE_SWAP_MB=512",
        "MIN_FREE_MEM_PCT=10",
        "MIN_DISK_MB=500",
    ]:
        assert needle in run_log, f"missing audit field: {needle}"
    assert secret not in run_log


def test_bounded_midbatch_safety_alert_hardstops_without_second_batch(tmp_path):
    trip_file = tmp_path / "swap_tripped"
    invocation_log = tmp_path / "stub_invocations.log"
    stub = tmp_path / "stub_tm_match.sh"
    stub.write_text(
        "#!/bin/bash\n"
        "set -euo pipefail\n"
        'tc="${1:-10+0.1}"\n'
        'rounds="${2:-1}"\n'
        'screening_dir="${SCREENING_DIR:-/tmp}"\n'
        'batch_dir="$(mktemp -d "$screening_dir/stub_batch_XXXXXX")"\n'
        "expected=$(( rounds * 2 ))\n"
        'printf \'{"exit_fastchess": 0, "exit_checker": 0, "exit_time_profile": 0, "exit_tee": 0, "timeout": 0, "expected_games": %s, "completed_games": %s}\' "$expected" "$expected" >"$batch_dir/meta.json"\n'
        'printf \'Games: %s, Wins: %s, Losses: 0, Draws: %s, Points: %s.0\\n\' "$expected" "$(( expected / 2 ))" "$(( expected - expected / 2 ))" "$expected" >"$batch_dir/match.log"\n'
        'echo "invocation" >>"$STUB_INVOCATION_LOG"\n'
        'echo "rundir=$batch_dir"\n'
        'touch "$SWAP_TRIP_FILE"\n'
        "sleep 10\n",
        encoding="utf-8",
    )
    stub.chmod(0o755)

    env = _bounded_env(
        tmp_path,
        stub,
        extra={
            "MAX_BATCHES": "2",
            "ROUNDS_PER_BATCH": "5",
            "MAX_SWAP_USED_MB": "1536",
            "MIN_FREE_SWAP_MB": "512",
            "SWAP_TRIP_FILE": str(trip_file),
            "STUB_INVOCATION_LOG": str(invocation_log),
        },
    )
    # Use a fake sysctl so swap telemetry passes preflight and trips mid-batch.
    env.pop("MOCK_SWAP_USED_MB", None)
    env.pop("MOCK_SWAP_FREE_MB", None)
    fake_sysctl = Path(env["PATH"].split(":")[0]) / "sysctl"
    fake_sysctl.write_text(
        "#!/bin/bash\n"
        'if [ "${1:-}" = "vm.swapusage" ]; then\n'
        '  if [ -n "${SWAP_TRIP_FILE:-}" ] && [ -f "$SWAP_TRIP_FILE" ]; then\n'
        "    echo 'vm.swapusage: total = 4096.00M  used = 2000.00M  free = 2096.00M  (encrypted)'\n"
        "  else\n"
        "    echo 'vm.swapusage: total = 2048.00M  used = 100.00M  free = 1948.00M  (encrypted)'\n"
        "  fi\n"
        "  exit 0\n"
        "fi\n"
        'exec /usr/sbin/sysctl "$@"\n',
        encoding="utf-8",
    )
    fake_sysctl.chmod(0o755)

    assert not trip_file.exists()
    started = time.monotonic()
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    elapsed = time.monotonic() - started
    assert res.returncode == 1, f"stdout={res.stdout}\nstderr={res.stderr}"
    combined = res.stdout + res.stderr
    assert "Bounded session aborted" in combined
    assert "0/2 validated batches" in combined
    assert "Swap used" in combined
    screening_dir = Path(env["SCREENING_DIR"])
    run_log = (screening_dir / "continuous.log").read_text(encoding="utf-8")
    assert "Bounded session aborted" in run_log
    assert "0/2 validated batches" in run_log
    # No retry: no second batch is ever launched and no 30s wait occurs.
    assert "Pre-batch check #2" not in run_log
    assert "Waiting 30s" not in run_log
    assert elapsed < 25, (
        f"bounded hardstop must not sleep-and-retry (took {elapsed:.1f}s)"
    )
    assert invocation_log.is_file()
    invocations = invocation_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(invocations) == 1, (
        f"expected exactly one batch launch, got {len(invocations)}"
    )
    data = json.loads((screening_dir / "scoreboard.json").read_text(encoding="utf-8"))
    assert data["batches_completed"] == 0
    assert len(data.get("incidents", [])) >= 1
    assert "Swap used" in data["incidents"][-1]["reason"]
    assert not (screening_dir / "screening.pid").is_file()
    assert not (screening_dir / "supervisor.lock").exists()


def test_bounded_predeadline_incomplete_cannot_succeed(tmp_path):
    stub = tmp_path / "stub_tm_match.sh"
    _write_stub_tm_match(stub)
    env = _bounded_env(
        tmp_path,
        stub,
        extra={
            "MAX_BATCHES": "2",
            "ROUNDS_PER_BATCH": "5",
            "DEADLINE_S": "0",
            "PAUSE_S": "0",
            "STUB_MODE": "success",
        },
    )
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert res.returncode == 1, f"stdout={res.stdout}\nstderr={res.stderr}"
    combined = res.stdout + res.stderr
    assert "Bounded session aborted" in combined
    assert "0/2 validated batches" in combined
    screening_dir = Path(env["SCREENING_DIR"])
    run_log = (screening_dir / "continuous.log").read_text(encoding="utf-8")
    assert "Bounded session aborted" in run_log
    assert "0/2 validated batches" in run_log
    # Deadline fires before any batch launches: no retry, no second attempt.
    assert "Pre-batch check #1" not in run_log
    assert "Waiting 30s" not in run_log
    assert not (screening_dir / "screening.pid").is_file()
    assert not (screening_dir / "supervisor.lock").exists()


def test_bounded_midbatch_deadline_aborts_without_retry(tmp_path):
    invocation_log = tmp_path / "stub_invocations.log"
    stub = tmp_path / "stub_tm_match.sh"
    stub.write_text(
        "#!/bin/bash\n"
        "set -euo pipefail\n"
        'tc="${1:-10+0.1}"\n'
        'rounds="${2:-1}"\n'
        'screening_dir="${SCREENING_DIR:-/tmp}"\n'
        'batch_dir="$(mktemp -d "$screening_dir/stub_batch_XXXXXX")"\n'
        "expected=$(( rounds * 2 ))\n"
        'printf \'{"exit_fastchess": 0, "exit_checker": 0, "exit_time_profile": 0, "exit_tee": 0, "timeout": 0, "expected_games": %s, "completed_games": %s}\' "$expected" "$expected" >"$batch_dir/meta.json"\n'
        'printf \'Games: %s, Wins: %s, Losses: 0, Draws: %s, Points: %s.0\\n\' "$expected" "$(( expected / 2 ))" "$(( expected - expected / 2 ))" "$expected" >"$batch_dir/match.log"\n'
        'echo "invocation" >>"$STUB_INVOCATION_LOG"\n'
        'echo "rundir=$batch_dir"\n'
        "sleep 10\n",
        encoding="utf-8",
    )
    stub.chmod(0o755)

    env = _bounded_env(
        tmp_path,
        stub,
        extra={
            "MAX_BATCHES": "2",
            "ROUNDS_PER_BATCH": "5",
            "DEADLINE_S": "2",
            "PAUSE_S": "0",
            "STUB_MODE": "success",
            "STUB_INVOCATION_LOG": str(invocation_log),
        },
    )

    started = time.monotonic()
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    elapsed = time.monotonic() - started
    assert res.returncode == 1, f"stdout={res.stdout}\nstderr={res.stderr}"
    combined = res.stdout + res.stderr
    assert "Bounded session aborted" in combined
    assert "0/2 validated batches" in combined
    assert "DEADLINE_EXCEEDED" in combined
    screening_dir = Path(env["SCREENING_DIR"])
    run_log = (screening_dir / "continuous.log").read_text(encoding="utf-8")
    assert "Bounded session aborted" in run_log
    assert "0/2 validated batches" in run_log
    assert "DEADLINE_EXCEEDED" in run_log
    # Mid-batch deadline must not retry: no second batch, no safety sleep.
    assert "Pre-batch check #2" not in run_log
    assert "Waiting 30s" not in run_log
    assert elapsed < 25, (
        f"bounded deadline must not sleep-and-retry (took {elapsed:.1f}s)"
    )
    assert invocation_log.is_file()
    invocations = invocation_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(invocations) == 1, (
        f"expected exactly one batch launch, got {len(invocations)}"
    )
    data = json.loads((screening_dir / "scoreboard.json").read_text(encoding="utf-8"))
    assert data["batches_completed"] == 0
    assert len(data.get("incidents", [])) >= 1
    assert "DEADLINE_EXCEEDED" in data["incidents"][-1]["reason"]
    assert not (screening_dir / "screening.pid").is_file()
    assert not (screening_dir / "supervisor.lock").exists()


def test_bounded_runs_automatic_diagnostics_scoped_to_scoreboard(tmp_path):
    stub = tmp_path / "stub_tm_match.sh"
    pgn_content = (
        '[Event "Fastchess"]\n[White "tm"]\n[Black "sf"]\n[Result "1-0"]\n\n'
        "1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0\n\n"
        '[Event "Fastchess"]\n[White "sf"]\n[Black "tm"]\n[Result "0-1"]\n\n'
        "1. d4 {+0.15/10 0.1s} d5 {-0.15/10 0.1s} 0-1\n"
    )
    stub.write_text(
        "#!/bin/bash\n"
        "set -euo pipefail\n"
        'screening_dir="${SCREENING_DIR:-/tmp}"\n'
        'batch_dir="$(mktemp -d "$screening_dir/stub_batch_XXXXXX")"\n'
        "cat <<'JSON' >\"$batch_dir/meta.json\"\n"
        "{\n"
        '  "engine_sha256": "fake_sha_engine",\n'
        '  "sf_engine_sha256": "fake_sha_sf",\n'
        '  "runner_sha256": "fake_sha_runner",\n'
        '  "runner_tag": "v1.8.2-alpha",\n'
        '  "tc": "10+0.1",\n'
        '  "threads": 1,\n'
        '  "hash_mb": 128,\n'
        '  "concurrency": 1,\n'
        '  "move_overhead_ms": 10,\n'
        '  "book": "book_uho",\n'
        '  "book_sha256": "sha_book",\n'
        '  "engine_options": "default",\n'
        '  "expected_games": 2,\n'
        '  "completed_games": 2,\n'
        '  "timeout": 0,\n'
        '  "exit_fastchess": 0,\n'
        '  "exit_checker": 0,\n'
        '  "exit_time_profile": 0,\n'
        '  "exit_tee": 0\n'
        "}\n"
        "JSON\n"
        f"cat <<'PGN' >\"$batch_dir/match.pgn\"\n{pgn_content}PGN\n"
        'printf "Games: 2, Wins: 2, Losses: 0, Draws: 0, Points: 2.0\\n" >"$batch_dir/match.log"\n'
        'echo "rundir=$batch_dir"\n',
        encoding="utf-8",
    )
    stub.chmod(0o755)

    env = _bounded_env(
        tmp_path,
        stub,
        extra={
            "MAX_BATCHES": "1",
            "ROUNDS_PER_BATCH": "1",
            "TC": "10+0.1",
        },
    )
    res = subprocess.run(
        ["bash", str(SCRIPT), "start"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert res.returncode == 0, f"stdout={res.stdout}\nstderr={res.stderr}"
    screening_dir = Path(env["SCREENING_DIR"])
    analyzer_log = (screening_dir / "analyzer_last.log").read_text(encoding="utf-8")
    assert "Analyzed 1 runs (1 valid partition(s), 0 excluded)" in analyzer_log
    diag = json.loads((screening_dir / "diagnostics.json").read_text(encoding="utf-8"))
    assert diag["total_runs_inspected"] == 1
    assert diag["valid_partitions_count"] == 1
    assert diag["excluded_runs_count"] == 0


def test_terminate_kills_child_when_exec_drops_token_from_argv(tmp_path):
    """Bash execs the final command of its -c list, dropping token= from argv.

    Reproduces the 2026-10-06 SAFETY_STOP orphan: the wrapper PID became
    `bash .../tm_match.sh TC ROUNDS` with no token visible in ps, so
    terminate_child_tree refused to signal and the match survived the stop.
    Ownership must be re-established via fork ancestry when the token is gone.
    """
    fake_tm = tmp_path / "tm_match.sh"
    fake_tm.write_text("#!/bin/sh\nsleep 120\n", encoding="utf-8")
    fake_tm.chmod(0o755)
    token = f"token_exec_{os.getpid()}_{int(time.time())}"
    pid_file = tmp_path / "child.pid"

    driver = (
        f'source "{SCRIPT}"\n'
        f'bash -c "exec bash {fake_tm} 5 1" >/dev/null 2>&1 &\n'
        "c=$!\n"
        f'echo "$c" > "{pid_file}"\n'
        "sleep 0.5\n"
        'terminate_child_tree "$c" "$1"\n'
        "exit $?\n"
    )
    res = subprocess.run(
        ["bash", "-c", driver, "driver", token],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    child_pid = int(pid_file.read_text().strip())
    try:
        deadline = time.time() + 3
        while is_alive(child_pid) and time.time() < deadline:
            time.sleep(0.1)
        assert "does not match verified owned screening child" not in res.stderr, (
            f"refused to signal exec'd child: {res.stderr}"
        )
        assert not is_alive(child_pid), "exec'd child survived terminate_child_tree"
    finally:
        if is_alive(child_pid):
            os.kill(child_pid, 9)

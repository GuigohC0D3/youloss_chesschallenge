import chess
import pytest

from controller.game_log import check_log
from controller.main import main
from controller.state import latest_unfinished, load_state, save_state
from controller.engine_client import EngineClient
from controller.tests.scripted import REAL, Script, fake_engine


def base_args(tmp_path) -> list[str]:
    return [
        "--logs",
        str(tmp_path / "logs"),
        "--no-book",
        "--syzygy",
        str(tmp_path / "sem_syzygy"),
        "--threads",
        "1",
        "--hash",
        "16",
    ]


def run(argv, answers=(), mode="ok"):
    out: list[str] = []
    code = main(
        argv,
        input_fn=Script(list(answers)),
        output_fn=out.append,
        engine_factory=lambda path: fake_engine(mode),
    )
    return code, "\n".join(out)


def test_color_required_without_resume(tmp_path):
    code, text = run(["start", *base_args(tmp_path)])
    assert code == 2 and "--color" in text


def test_bad_tc(tmp_path):
    code, text = run(
        ["start", "--color", "white", "--tc", "15min", *base_args(tmp_path)]
    )
    assert code == 2 and "controle de tempo" in text


def test_refuses_to_overwrite_existing_log(tmp_path):
    argv = ["start", "--color", "black", "--opponent", "X", *base_args(tmp_path)]
    assert run(argv)[0] == 0
    code, text = run(argv)
    assert code == 2 and "já existe" in text


def test_missing_book_is_an_error(tmp_path):
    args = [a for a in base_args(tmp_path) if a != "--no-book"]
    code, text = run(
        ["start", "--color", "white", "--book", str(tmp_path / "x.bin"), *args]
    )
    assert code == 2 and "x.bin" in text


def test_warns_without_book_and_syzygy(tmp_path):
    code, text = run(["start", "--color", "black", *base_args(tmp_path)])
    assert code == 0 and "sem book" in text and "sem tablebases" in text


def test_engine_crash_records_forfeit_and_refuses_resume(tmp_path):
    code, text = run(
        ["start", "--color", "white", *base_args(tmp_path)],
        answers=["begin"],
        mode="dieongo",
    )
    assert code == 2 and "FALHA DE SOFTWARE" in text and "Não retome" in text
    state_file = next((tmp_path / "logs").glob("*.state.json"))
    state = load_state(state_file)
    assert state.finished and state.result == "0-1" and state.reason == "software-failure"
    log_file = next((tmp_path / "logs").glob("*.log"))
    assert "# result=0-1 reason=software-failure" in log_file.read_text(encoding="utf-8")

    code, text = run(
        ["start", "--resume", *base_args(tmp_path)],
    )
    assert code == 2 and "encerrada após falha de software" in text


def test_quit_after_game_begins_records_forfeit(tmp_path):
    code, text = run(
        ["start", "--color", "white", *base_args(tmp_path)],
        answers=["begin", "quit"],
    )
    assert code == 2 and "controlador encerrado durante a partida" in text
    state_file = next((tmp_path / "logs").glob("*.state.json"))
    state = load_state(state_file)
    assert state.finished and state.result == "0-1" and state.reason == "software-failure"


def test_resume_after_unexpected_exit_marks_started_game_lost(tmp_path):
    code, _ = run(
        ["start", "--color", "white", *base_args(tmp_path)],
        answers=["begin", "quit"],
    )
    assert code == 2
    state_file = next((tmp_path / "logs").glob("*.state.json"))
    log_file = next((tmp_path / "logs").glob("*.log"))
    state = load_state(state_file)
    state.result = None
    state.reason = None
    save_state(state, state_file)
    log_lines = log_file.read_text(encoding="utf-8").splitlines()
    log_file.write_text(
        "\n".join(line for line in log_lines if not line.startswith("# result=")) + "\n",
        encoding="utf-8",
    )

    code, text = run(["start", "--resume", *base_args(tmp_path)])
    assert code == 2 and "controlador foi reiniciado depois do início" in text
    state = load_state(state_file)
    assert state.finished and state.reason == "software-failure"


def test_software_failure_log_blocks_resume_if_state_write_fails(tmp_path, monkeypatch):
    import controller.main as main_mod

    real_save = main_mod.save_state

    def fail_terminal_state(state, path):
        if state.reason == "software-failure":
            raise OSError("disco cheio")
        real_save(state, path)

    monkeypatch.setattr(main_mod, "save_state", fail_terminal_state)
    code, text = run(
        ["start", "--color", "white", *base_args(tmp_path)],
        answers=["begin"],
        mode="dieongo",
    )
    assert code == 2 and "disco cheio" in text
    code, text = run(["start", "--resume", *base_args(tmp_path)])
    assert code == 2 and "partida encerrada após falha de software" in text


def test_resume_without_games(tmp_path):
    code, text = run(["start", "--resume", *base_args(tmp_path)])
    assert code == 2 and "nenhuma partida" in text


def test_resume_finished_game_refused(tmp_path):
    assert (
        run(["start", "--color", "black", *base_args(tmp_path)], answers=["draw", "s"])[
            0
        ]
        == 0
    )
    state_file = next((tmp_path / "logs").glob("*.state.json"))
    code, text = run(["start", "--resume", str(state_file), *base_args(tmp_path)])
    assert code == 2 and "encerrada" in text


@pytest.mark.skipif(not REAL.exists(), reason="engine não compilado")
def test_full_game_against_weak_opponent_real_engine(tmp_path):
    logs = tmp_path / "logs"

    calls = {"n": 0, "pressed": False}

    def opponent(prompt: str) -> str:
        # Adversário fraco com protocolo físico: begin → played/press →
        # UCI → played ... (menor lance legal em ordem UCI).
        calls["n"] += 1
        if calls["n"] == 1:
            return "begin"
        state = load_state(next(logs.glob("*.state.json")))
        board = state.board()
        if state.pending_uci is not None:
            calls["pressed"] = False
            return "played"
        # Nós somos white: vez do adversário (black) exige press + UCI.
        if board.turn == chess.BLACK:
            if not calls["pressed"]:
                calls["pressed"] = True
                return "press 00:18 00:19"
            calls["pressed"] = False
            return min(m.uci() for m in board.legal_moves)
        return "go"

    out: list[str] = []
    code = main(
        [
            "start",
            "--color",
            "white",
            "--tc",
            "20+0.2",
            "--opponent",
            "bot",
            "--engine",
            str(REAL),
            *base_args(tmp_path),
        ],
        input_fn=opponent,
        output_fn=out.append,
    )
    assert code == 0
    state = load_state(next(logs.glob("*.state.json")))
    assert (state.result, state.reason) == ("1-0", "checkmate")
    log_file = next(logs.glob("*.log"))
    assert check_log(log_file) == []
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert sum(l.startswith("move=") for l in lines) == len(state.moves)
    assert lines[-1] == "# result=1-0 reason=checkmate"


def test_engine_failing_at_start_allows_same_start_again(tmp_path):
    argv = ["start", "--color", "white", "--opponent", "X", *base_args(tmp_path)]
    out: list[str] = []
    code = main(
        argv,
        input_fn=Script([]),
        output_fn=out.append,
        engine_factory=lambda path: EngineClient(tmp_path / "nope.exe"),
    )
    assert code == 2 and any("nope.exe" in o for o in out)
    code, text = run(argv)
    assert code == 0
    log_file = next((tmp_path / "logs").glob("*.log"))
    assert log_file.read_text(encoding="utf-8").startswith("# engine=")


def test_io_error_after_game_begins_records_software_failure(tmp_path, monkeypatch):
    import controller.game as game_mod

    def locked(state, path):
        raise PermissionError("arquivo em uso")

    monkeypatch.setattr(game_mod, "save_state", locked)
    code, text = run(
        ["start", "--color", "white", *base_args(tmp_path)], answers=["begin"]
    )
    assert code == 2 and "arquivo em uso" in text and "FALHA DE SOFTWARE" in text


@pytest.mark.parametrize("bad_val", ["-1", "-0.1", "nan", "inf", "-inf", "61", "100"])
def test_clock_latency_cli_validation(tmp_path, bad_val):
    with pytest.raises(SystemExit):
        main(["start", "--color", "white", "--clock-latency", bad_val, *base_args(tmp_path)])


def test_incident_persistence_on_startup_crash(tmp_path):
    code, text = run(
        ["start", "--color", "white", *base_args(tmp_path)],
        mode="crash_with_stderr",
    )
    assert code == 2
    assert "nada foi gravado; corrija o problema e repita o mesmo start" in text
    assert "fatal: corrupted hash table" not in text
    incident_files = list((tmp_path / "logs").glob("*.incident.json"))
    assert len(incident_files) == 1
    import json

    data = json.loads(incident_files[0].read_text(encoding="utf-8"))
    assert data["failure_class"] == "EngineCrashed"
    assert data["engine_exit_status"] == 5
    assert data["fen"] == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    assert data["clock"] is None
    assert any("corrupted hash table" in line for line in data["stderr_tail"])
    assert "T" in data["timestamp"]

    # Pregame retry guidance: repeating start with ok engine succeeds
    code, _ = run(["start", "--color", "white", *base_args(tmp_path)], mode="ok")
    assert code == 0


def test_incident_persistence_on_search_crash(tmp_path):
    code, text = run(
        ["start", "--color", "white", *base_args(tmp_path)],
        answers=["begin"],
        mode="dieongo_with_stderr",
    )
    assert code == 2
    assert "FALHA DE SOFTWARE" in text
    assert "critical: assertion failed" not in text
    incident_files = list((tmp_path / "logs").glob("*.incident.json"))
    assert len(incident_files) == 1
    import json

    data = json.loads(incident_files[0].read_text(encoding="utf-8"))
    assert data["failure_class"] == "EngineCrashed"
    assert data["engine_exit_status"] == 4
    assert data["clock"] is not None
    assert "white_ms" in data["clock"] and "black_ms" in data["clock"]
    assert any("assertion failed" in line for line in data["stderr_tail"])

    # Terminal loss preserved and log has incident note
    state_file = next((tmp_path / "logs").glob("*.state.json"))
    state = load_state(state_file)
    assert state.finished and state.result == "0-1" and state.reason == "software-failure"
    log_file = next((tmp_path / "logs").glob("*.log"))
    log_content = log_file.read_text(encoding="utf-8")
    assert "# incident failure_class=EngineCrashed" in log_content
    assert "# result=0-1 reason=software-failure" in log_content


def test_incident_persistence_failure_does_not_suppress_terminal_loss(tmp_path, monkeypatch):
    import controller.main as main_mod

    def fail_incident(*args, **kwargs):
        raise OSError("falha de disco no sidecar")

    monkeypatch.setattr(main_mod, "record_incident", fail_incident)
    code, text = run(
        ["start", "--color", "white", *base_args(tmp_path)],
        answers=["begin"],
        mode="dieongo_with_stderr",
    )
    assert code == 2
    assert "FALHA DE SOFTWARE" in text
    state_file = next((tmp_path / "logs").glob("*.state.json"))
    state = load_state(state_file)
    assert state.finished and state.result == "0-1" and state.reason == "software-failure"

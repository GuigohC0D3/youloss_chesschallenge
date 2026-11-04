"""Sessão da interface web e rotas HTTP, com engine falso."""
import http.client
import json
import sys
import time
from pathlib import Path

import chess
import pytest

from controller.engine_client import EngineClient
from controller.state import load_state
from controller.web import ActionError, MoveInputError, WebSession, make_server, parse_move

FAKE = Path(__file__).with_name("fake_engine.py")
OPTIONS = {"Threads": 1, "Hash": 16, "Move Overhead": 0}


def wait_idle(session, timeout=10.0):
    deadline = time.monotonic() + timeout
    while session.thinking and time.monotonic() < deadline:
        time.sleep(0.01)
    assert not session.thinking


@pytest.fixture
def make_session(tmp_path):
    made = []

    def factory(mode="ok", latency=0.0):
        session = WebSession(
            lambda: EngineClient(sys.executable, args=[str(FAKE), mode]),
            OPTIONS, tmp_path, clock_latency_s=latency,
        )
        session.open()
        made.append(session)
        return session

    yield factory
    for session in made:
        session.close()


@pytest.mark.parametrize(
    "text,uci",
    [
        ("e2e4", "e2e4"), ("E2-E4", "e2e4"), (" e4 ", "e2e4"),
        ("Nf3", "g1f3"), ("Cf3", "g1f3"), ("g1f3", "g1f3"),
    ],
)
def test_parse_move_formats(text, uci):
    assert parse_move(chess.Board(), text).uci() == uci


@pytest.mark.parametrize("text", ["O-O", "0-0", "o-o", "Rg1"])
def test_parse_castling_and_portuguese_king(text):
    board = chess.Board("r3k2r/8/8/8/8/8/8/4K2R w Kkq - 0 1")
    if text == "Rg1":  # em inglês é a torre; em português não há lance do rei para g1
        assert parse_move(board, text).uci() == "h1g1"
    else:
        assert parse_move(board, text).uci() == "e1g1"


def test_parse_long_castling():
    board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    assert parse_move(board, "0-0-0").uci() == "e1c1"


def test_parse_ambiguous_between_languages_is_refused():
    # Rd2: torre d1-d2 em inglês, rei e1-d2 em português.
    board = chess.Board("4k3/8/8/8/8/8/8/3RK3 w - - 0 1")
    with pytest.raises(MoveInputError, match="ambíguo"):
        parse_move(board, "Rd2")


@pytest.mark.parametrize("text", ["e7e8q", "e7e8=Q", "e7e8d", "e7e8=D", "e8=D", "e8=Q"])
def test_parse_promotion(text):
    board = chess.Board("8/4P3/8/8/8/8/8/k1K5 w - - 0 1")
    assert parse_move(board, text).uci() == "e7e8q"


def test_parse_promotion_without_piece_explains():
    board = chess.Board("8/4P3/8/8/8/8/8/k1K5 w - - 0 1")
    with pytest.raises(MoveInputError, match="promoção"):
        parse_move(board, "e7e8")


@pytest.mark.parametrize("text", ["", "e2e5", "xyz", "Qh5", "e2e4e5"])
def test_parse_rejects_bad_input(text):
    with pytest.raises(MoveInputError):
        parse_move(chess.Board(), text)


def test_black_waits_then_answers_each_opponent_move(make_session):
    session = make_session()
    session.start_game("black", "Equipe X", 1, "1500+0")
    assert not session.thinking and session.snapshot()["our_move"] is None

    session.opponent_move("e4")
    wait_idle(session)

    snap = session.snapshot()
    assert snap["our_move"] is not None
    assert snap["moves"][0] == "e4" and len(snap["moves"]) == 2
    assert snap["our_turn"] is False
    assert len(load_state(session.state_path).moves) == 2


def test_white_gets_first_move_without_typing(make_session):
    session = make_session()
    session.start_game("white", "Equipe X", 1, "1500+0")
    wait_idle(session)
    assert len(session.board.move_stack) == 1
    assert session.snapshot()["our_move"]["source"] == "engine"


def test_illegal_opponent_move_changes_nothing(make_session):
    session = make_session()
    session.start_game("black", "Equipe X", 1, "1500+0")
    with pytest.raises(ActionError, match="ilegal"):
        session.opponent_move("e2e5")
    assert not session.board.move_stack and not session.thinking


def test_undo_returns_to_before_opponent_move(make_session):
    session = make_session()
    session.start_game("black", "Equipe X", 1, "1500+0")
    session.opponent_move("e4")
    wait_idle(session)

    session.undo()

    assert not session.board.move_stack
    assert session.snapshot()["our_move"] is None
    session.opponent_move("d4")
    wait_idle(session)
    assert session.board.move_stack[0].uci() == "d2d4"


def test_undo_cancels_running_search(make_session):
    session = make_session("slow")
    session.start_game("black", "Equipe X", 1, "1500+0")
    session.opponent_move("e4")
    assert session.thinking

    session.undo()

    assert not session.thinking and not session.board.move_stack
    assert session.snapshot()["our_move"] is None


def test_undo_with_nothing_played_keeps_white_search_alive(make_session):
    session = make_session("slow")
    session.start_game("white", "Equipe X", 1, "1500+0")
    with pytest.raises(ActionError, match="nada a desfazer"):
        session.undo()
    assert session.thinking


def test_input_refused_while_thinking(make_session):
    session = make_session("slow")
    session.start_game("black", "Equipe X", 1, "1500+0")
    session.opponent_move("e4")
    with pytest.raises(ActionError, match="aguarde"):
        session.opponent_move("d5")
    session.undo()


def test_latency_is_charged_on_both_transitions(make_session):
    session = make_session(latency=2.0)
    session.start_game("black", "Equipe X", 1, "1500+0")
    session.opponent_move("e4")
    wait_idle(session)
    ours = session.clock.remaining(chess.BLACK)
    assert 1500_000 - 5000 < ours <= 1500_000 - 4000


def test_set_clock_takes_physical_reading(make_session):
    session = make_session()
    session.start_game("black", "Equipe X", 1, "1500+0")
    session.set_clock("20:00", "19:00")
    snap = session.snapshot()
    assert 1199_000 <= snap["ours_ms"] <= 1200_000
    assert 1130_000 <= snap["theirs_ms"] <= 1140_000


def test_bad_clock_reading_is_refused(make_session):
    session = make_session()
    session.start_game("black", "Equipe X", 1, "1500+0")
    with pytest.raises(ActionError, match="mm:ss"):
        session.set_clock("abc", "19:00")


def test_exhausted_clock_gives_immediate_legal_move_with_warning(make_session):
    session = make_session("slow")
    session.start_game("black", "Equipe X", 1, "1500+0")
    session.set_clock("00:00", "10:00")
    session.opponent_move("e4")
    wait_idle(session, timeout=2)
    snap = session.snapshot()
    assert snap["our_move"]["source"] == "fallback"
    assert snap["warning"]


def test_engine_crash_restarts_and_still_answers(make_session, tmp_path):
    modes = iter(["ok", "ok"])
    session = WebSession(
        lambda: EngineClient(sys.executable, args=[str(FAKE), next(modes)]),
        OPTIONS, tmp_path, clock_latency_s=0.0,
    )
    session.open()
    try:
        session.start_game("black", "Equipe X", 1, "1500+0")
        session.engine._proc.kill()
        session.opponent_move("e4")
        wait_idle(session)
        assert session.snapshot()["our_move"]["source"] == "engine"
        assert "incident" in Path(session.state.log_path).read_text()
    finally:
        session.close()


def test_engine_gone_for_good_falls_back_to_legal_move(tmp_path):
    clients = iter(["ok"])

    def factory():
        return EngineClient(sys.executable, args=[str(FAKE), next(clients, "crash")])

    session = WebSession(factory, OPTIONS, tmp_path, clock_latency_s=0.0)
    session.open()
    try:
        session.start_game("black", "Equipe X", 1, "1500+0")
        session.engine._proc.kill()
        session.opponent_move("e4")
        wait_idle(session, timeout=20)
        snap = session.snapshot()
        assert snap["our_move"]["source"] == "fallback"
        assert "Engine falhou" in snap["warning"]
    finally:
        session.close()


def test_checkmate_by_opponent_finishes_game_without_search(make_session):
    session = make_session()
    session.start_game("black", "Equipe X", 1, "1500+0")
    session.board = chess.Board("6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1")
    session.state.start_fen = session.board.fen()

    session.opponent_move("Ra8")

    snap = session.snapshot()
    assert snap["phase"] == "finished" and snap["result"] == "1-0"
    assert snap["reason"] == "checkmate" and not snap["thinking"]


def test_manual_finish_records_result_and_blocks_input(make_session):
    session = make_session()
    session.start_game("black", "Equipe X", 1, "1500+0")
    session.finish("win", "abandono")
    assert session.state.result == "0-1"
    assert load_state(session.state_path).result == "0-1"
    with pytest.raises(ActionError):
        session.opponent_move("e4")


def test_new_game_after_finish_and_duplicate_log_refused(make_session):
    session = make_session()
    session.start_game("black", "Equipe X", 1, "1500+0")
    session.finish("draw", "acordo")
    with pytest.raises(ActionError, match="outro número"):
        session.start_game("black", "Equipe X", 1, "1500+0")
    session.start_game("white", "Equipe X", 2, "1500+0")
    wait_idle(session)
    assert session.state.game == 2 and len(session.board.move_stack) == 1


def test_second_game_refused_while_one_is_running(make_session):
    session = make_session()
    session.start_game("black", "Equipe X", 1, "1500+0")
    with pytest.raises(ActionError, match="em andamento"):
        session.start_game("black", "Equipe Y", 1, "1500+0")


def test_resume_restores_board_after_restart(make_session):
    first = make_session()
    first.start_game("black", "Equipe X", 1, "1500+0")
    first.opponent_move("e4")
    wait_idle(first)
    first.close()

    second = make_session()
    assert second.snapshot()["resume"]["plies"] == 2
    second.resume_game()
    assert len(second.board.move_stack) == 2
    assert "confira" in second.snapshot()["warning"].lower()
    second.opponent_move("d4")
    wait_idle(second)
    assert len(second.board.move_stack) == 4


def test_snapshot_board_svg_marks_our_move(make_session):
    session = make_session()
    session.start_game("white", "Equipe X", 1, "1500+0")
    wait_idle(session)
    svg = session.snapshot()["board_svg"]
    assert svg.startswith("<svg") and "arrow" in svg


@pytest.fixture
def server(make_session):
    session = make_session()
    srv = make_server(session, 0)
    import threading

    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv, session
    srv.shutdown()
    srv.server_close()


def request(srv, method, path, body=None, headers=None):
    port = srv.server_address[1]
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    hdrs = {"Content-Type": "application/json"} if body is not None else {}
    hdrs.update(headers or {})
    conn.request(method, path, json.dumps(body) if body is not None else None, hdrs)
    resp = conn.getresponse()
    raw = resp.read()
    conn.close()
    return resp.status, raw


def test_http_serves_ui_and_runs_a_move(server):
    srv, session = server
    status, html = request(srv, "GET", "/")
    assert status == 200 and b"Lance do advers" in html

    status, _ = request(srv, "POST", "/api/start", {"color": "black", "opponent": "X", "game": 1, "tc": "1500+0"})
    assert status == 200
    status, raw = request(srv, "POST", "/api/move", {"move": "e2e5"})
    assert status == 400 and "ilegal" in json.loads(raw)["error"]
    status, _ = request(srv, "POST", "/api/move", {"move": "e4"})
    assert status == 200
    wait_idle(session)
    status, raw = request(srv, "GET", "/api/state")
    assert json.loads(raw)["our_move"] is not None


def test_http_refuses_foreign_host_and_non_json_post(server):
    srv, _ = server
    status, _ = request(srv, "GET", "/api/state", headers={"Host": "evil.example"})
    assert status == 403
    status, _ = request(srv, "POST", "/api/undo", {}, headers={"Content-Type": "text/plain"})
    assert status == 403


def test_http_invalid_body_does_not_crash_server(server):
    srv, _ = server
    status, _ = request(srv, "POST", "/api/start", {"game": "nope"})
    assert status == 400
    status, _ = request(srv, "GET", "/api/state")
    assert status == 200

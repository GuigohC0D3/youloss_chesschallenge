import chess
import pytest

from controller.engine_client import EngineCrashed
from controller.game_log import LINE_RE
from controller.state import load_state
from controller.tests.polyglot import write_book


def log_lines(tmp_path) -> list[str]:
    return (tmp_path / "g.log").read_text(encoding="utf-8").splitlines()


def moves_in_log(tmp_path) -> list[str]:
    return [l for l in log_lines(tmp_path) if l.startswith("move=")]


def test_engine_and_opponent_moves_logged_and_saved(tmp_path, games):
    game, out = games(tmp_path, ["begin", "played", "press 00:58 00:59", "e7e5", "played"])
    assert game.run() is None  # EOF depois do played final → quit
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]
    lines = moves_in_log(tmp_path)
    assert len(lines) == 3 and all(LINE_RE.match(l) for l in lines)
    assert "source=engine" in lines[0] and "eval=+0.12" in lines[0]
    assert lines[1].startswith("move=1 color=black uci=e7e5 ")
    assert load_state(tmp_path / "g.state.json").moves == game.state.moves
    assert any("LANCE CONFIRMADO: a2a3" in o for o in out)


def test_bad_input_reprompts_without_advancing(tmp_path, games):
    game, out = games(
        tmp_path,
        ["begin", "played", "press 00:58 00:59", "e2e4", "xyz", "", "  E7E5  ", "played"],
    )
    game.run()
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]
    text = "\n".join(out)
    assert "lance ilegal: e2e4" in text
    assert "entrada inválida" in text


def test_lowtime_fallback_prefers_valuable_legal_capture(tmp_path, games):
    game, _ = games(
        tmp_path,
        [],
        fen="7k/8/8/3q4/8/8/8/K2R4 w - - 0 1",
    )
    legal = list(game.board.legal_moves)
    game._propose_fallback_lowtime(legal, ours_ms=50, reserve_ms=2000, stop_ms=1000)
    assert game.state.pending_uci == "d1d5"
    assert game.state.moves == []  # fallback is still only a proposal


def test_lowtime_fallback_takes_immediate_checkmate(tmp_path, games):
    game, _ = games(
        tmp_path,
        [],
        fen="7k/8/5KQ1/8/8/8/8/8 w - - 0 1",
    )
    game._propose_fallback_lowtime(
        list(game.board.legal_moves), ours_ms=50, reserve_ms=2000, stop_ms=1000
    )
    assert game.state.pending_uci == "g6g7"
    assert game.state.moves == []


def test_resume_is_not_marked_as_started_before_reconciliation(tmp_path, games):
    game, _ = games(tmp_path, [], resumed=True)
    assert not game.begun


def test_promotion_without_piece_gets_hint(tmp_path, games):
    game, out = games(
        tmp_path,
        ["begin", "played", "press 00:58 00:59", "a2a1", "a2a1q"],
        fen="8/8/8/8/8/k7/p7/7K w - - 0 1",
    )
    game.run()
    assert game.state.moves[:2] == ["h1g1", "a2a1q"]
    assert any("promoção" in o for o in out)


def test_forced_move_skips_engine(tmp_path, games):
    # Só Kxb2 é legal; o engine "deaf" estouraria o teste se fosse chamado.
    game, _ = games(
        tmp_path,
        ["begin", "played"],
        fen="k7/8/8/8/8/8/1r6/K7 w - - 0 1",
        mode="deaf",
    )
    assert game.run() == "1/2-1/2"  # K x K: material insuficiente
    moves = moves_in_log(tmp_path)
    assert "source=forced" in moves[0] and "eval=forced" in moves[0]
    lines = log_lines(tmp_path)
    assert lines[-1] == "# result=1/2-1/2 reason=insufficient_material"


def test_book_move_used(tmp_path, games):
    path = tmp_path / "b.bin"
    write_book(path, [(chess.Board(), "e2e4", 1)])
    game, _ = games(tmp_path, ["begin", "played"], book=path, mode="deaf")
    game.run()
    assert game.state.moves == ["e2e4"]
    assert "source=book" in moves_in_log(tmp_path)[0]


def test_opponent_checkmate_ends_game(tmp_path, games):
    game, out = games(
        tmp_path,
        ["begin", "press 00:58 00:59", "a1a8"],
        color="black",
        fen="6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1",
    )
    assert game.run() == "1-0"
    state = load_state(tmp_path / "g.state.json")
    assert (state.result, state.reason) == ("1-0", "checkmate")
    assert log_lines(tmp_path)[-1] == "# result=1-0 reason=checkmate"


def test_slow_engine_is_stopped(tmp_path, games):
    game, out = games(
        tmp_path,
        ["begin", "played"],
        mode="slow",
        base_ms=5_000,
        safety=0.2,
    )
    game.run()
    assert game.state.moves == ["a2a3"]
    assert any("stop enviado" in o for o in out)


def test_expired_estimate_flags_only_after_physical_zero_without_search(tmp_path, games):
    game, _ = games(tmp_path, ["begin", "clock 00:00 01:00 nos"])
    game.clock.start(chess.WHITE)
    game.clock.set(chess.WHITE, -500)
    sent = []
    real_search = game.engine.search

    def spy(position, go, timeout, stop_grace=2.0):
        sent.append((go, timeout))
        return real_search(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy
    assert game.run() == "0-1"
    assert game.state.reason == "flag"
    assert sent == []
    assert "physical flag confirmed" in (tmp_path / "g.log").read_text(encoding="utf-8")


def test_low_time_positive_still_sends_honest_times(tmp_path, games):
    game, _ = games(tmp_path, ["begin", "played"], base_ms=60_000)
    game.clock.start(chess.WHITE)
    game.clock.set(chess.WHITE, 30_000)
    game.clock.set(chess.BLACK, 60_000)
    sent = []
    real_search = game.engine.search

    def spy(position, go, timeout, stop_grace=2.0):
        sent.append((go, timeout))
        return real_search(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy
    game.run()
    go, timeout = sent[0]
    assert "wtime 30000" in go or "wtime 299" in go
    assert "btime 60000" in go or "btime 599" in go
    assert timeout > 0


def test_engine_crash_propagates(tmp_path, games):
    game, _ = games(tmp_path, ["begin"], mode="dieongo")
    with pytest.raises(EngineCrashed):
        game.run()


def test_confirmed_move_log_survives_state_save_failure(tmp_path, games):
    # Proposta pendente continua persistida antes da confirmação física;
    # na confirmação, `move=` vai antes do commit do estado.
    import controller.game as game_mod

    game, _ = games(tmp_path, ["begin"], base_ms=60_000)
    assert game.run() is None  # begin + proposta (quit via EOF)
    assert game.state.pending_uci == "a2a3"
    prior = load_state(tmp_path / "g.state.json")
    assert prior.moves == [] and prior.pending_uci == "a2a3"

    def failing_save(state, path):
        raise OSError("disco cheio (fault-injection)")

    real_save = game_mod.save_state
    game_mod.save_state = failing_save
    try:
        try:
            game._cmd_played("")
        except OSError:
            pass
        else:
            raise AssertionError("save deveria falhar na confirmação")
    finally:
        game_mod.save_state = real_save

    # Linha durável existe mesmo com o commit falhando.
    lines = (tmp_path / "g.log").read_text(encoding="utf-8").splitlines()
    moves = [l for l in lines if l.startswith("move=")]
    assert len(moves) == 1 and all(LINE_RE.match(l) for l in moves)
    assert "uci=a2a3" in moves[0]
    # Estado anterior segue carregável para reconciliação via FEN.
    recovered = load_state(tmp_path / "g.state.json")
    assert recovered.moves == [] and recovered.pending_uci == "a2a3"
    assert recovered.board().fen() == chess.STARTING_FEN

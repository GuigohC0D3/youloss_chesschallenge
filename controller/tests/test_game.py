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
    game, out = games(tmp_path, ["e7e5"])
    assert game.run() is None  # EOF depois do e7e5 → quit
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]
    lines = moves_in_log(tmp_path)
    assert len(lines) == 3 and all(LINE_RE.match(l) for l in lines)
    assert "source=engine" in lines[0] and "eval=+0.12" in lines[0]
    assert lines[1].startswith("move=1 color=black uci=e7e5 ")
    assert load_state(tmp_path / "g.state.json").moves == game.state.moves
    assert any("NOSSO LANCE: a2a3" in o for o in out)


def test_bad_input_reprompts_without_advancing(tmp_path, games):
    game, out = games(tmp_path, ["e2e4", "xyz", "", "  E7E5  "])
    game.run()
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]
    text = "\n".join(out)
    assert "lance ilegal: e2e4" in text
    assert "entrada inválida" in text


def test_promotion_without_piece_gets_hint(tmp_path, games):
    game, out = games(tmp_path, ["a2a1", "a2a1q"], fen="8/8/8/8/8/k7/p7/7K w - - 0 1")
    game.run()
    assert game.state.moves[:2] == ["h1g1", "a2a1q"]
    assert any("promoção" in o for o in out)


def test_forced_move_skips_engine(tmp_path, games):
    # Só Kxb2 é legal; o engine "deaf" estouraria o teste se fosse chamado.
    game, _ = games(tmp_path, [], fen="k7/8/8/8/8/8/1r6/K7 w - - 0 1", mode="deaf")
    assert game.run() == "1/2-1/2"  # K x K: material insuficiente
    lines = log_lines(tmp_path)
    assert "source=forced" in lines[0] and "eval=forced" in lines[0]
    assert lines[-1] == "# result=1/2-1/2 reason=insufficient_material"


def test_book_move_used(tmp_path, games):
    path = tmp_path / "b.bin"
    write_book(path, [(chess.Board(), "e2e4", 1)])
    game, _ = games(tmp_path, [], book=path, mode="deaf")
    game.run()
    assert game.state.moves == ["e2e4"]
    assert "source=book" in moves_in_log(tmp_path)[0]


def test_opponent_checkmate_ends_game(tmp_path, games):
    game, out = games(tmp_path, ["a1a8"], color="black",
                      fen="6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1")
    assert game.run() == "1-0"
    state = load_state(tmp_path / "g.state.json")
    assert (state.result, state.reason) == ("1-0", "checkmate")
    assert log_lines(tmp_path)[-1] == "# result=1-0 reason=checkmate"


def test_slow_engine_is_stopped(tmp_path, games):
    game, out = games(tmp_path, [], mode="slow", base_ms=400, safety=0.2)
    game.run()
    assert game.state.moves == ["a2a3"]
    assert any("stop enviado" in o for o in out)


def test_go_never_sends_non_positive_time(tmp_path, games):
    game, _ = games(tmp_path, [])
    game.clock.start(chess.WHITE)
    game.clock.set(chess.WHITE, -500)
    sent = []
    real_search = game.engine.search

    def spy(position, go, timeout):
        sent.append((go, timeout))
        return real_search(position, go, timeout)

    game.engine.search = spy
    game.run()
    go, timeout = sent[0]
    assert go.startswith("go wtime 1 btime 60000 winc 100 binc 100")
    assert timeout > 0


def test_engine_crash_propagates(tmp_path, games):
    game, _ = games(tmp_path, [], mode="dieongo")
    with pytest.raises(EngineCrashed):
        game.run()

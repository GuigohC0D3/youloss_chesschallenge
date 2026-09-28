import chess

from controller.state import load_state

BLACK_TO_MOVE = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"


def test_undo_twice_then_new_opponent_move(tmp_path, games):
    # a2a3 (nós), e7e5, a1a2 (nós) → undo, undo → d7d5 → engine joga de novo
    game, out = games(tmp_path, ["e7e5", "undo", "undo", "d7d5"])
    game.run()
    assert game.state.moves[:2] == ["a2a3", "d7d5"] and len(game.state.moves) == 3
    assert any(l.startswith("# undo") for l in
               (tmp_path / "g.log").read_text(encoding="utf-8").splitlines())


def test_undo_pauses_on_our_turn_and_rejects_moves(tmp_path, games):
    game, out = games(tmp_path, ["e7e5", "undo", "h2h3", "go"])
    game.run()
    assert any("nossa vez" in o for o in out)
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]


def test_undo_with_nothing(tmp_path, games):
    game, out = games(tmp_path, ["undo"], color="black")
    game.run()
    assert any("nada a desfazer" in o for o in out)


def test_fen_resync_pauses_then_go(tmp_path, games):
    game, _ = games(tmp_path, [f"fen {BLACK_TO_MOVE}", "go"], color="black")
    game.run()
    state = load_state(tmp_path / "g.state.json")
    assert state.start_fen == BLACK_TO_MOVE and len(state.moves) == 1


def test_invalid_fen_rejected(tmp_path, games):
    game, out = games(tmp_path, ["fen lixo", "fen 8/8/8/8/8/8/8/8 w - - 0 1"], color="black")
    game.run()
    assert sum("FEN inválida" in o for o in out) == 2
    assert game.state.start_fen == chess.STARTING_FEN


def test_clock_sync(tmp_path, games):
    game, out = games(tmp_path, ["clock 10:00 12:30", "clock 10 12"], color="black")
    game.run()
    assert abs(game.clock.remaining(chess.BLACK) - 600_000) < 500
    assert abs(game.clock.remaining(chess.WHITE) - 750_000) < 500
    assert any("mm:ss" in o for o in out)


def test_board_shows_fen(tmp_path, games):
    game, out = games(tmp_path, ["board"], color="black")
    game.run()
    assert any(chess.STARTING_FEN in o for o in out)


def test_go_on_opponent_turn_is_rejected(tmp_path, games):
    game, out = games(tmp_path, ["go"], color="black")
    game.run()
    assert any("vez do adversário" in o for o in out)


def test_resign_and_draw(tmp_path, games):
    for answers, color, expected in [
        (["resign nos"], "black", ("1-0", "resign_us")),
        (["resign adv"], "black", ("0-1", "resign_opponent")),
        (["resign"], "black", (None, None)),
        (["draw"], "black", ("1/2-1/2", "draw_agreed")),
    ]:
        sub = tmp_path / f"{answers[0].replace(' ', '_')}"
        sub.mkdir()
        game, _ = games(sub, answers, color=color)
        game.run()
        assert (game.state.result, game.state.reason) == expected


def test_help_lists_commands(tmp_path, games):
    game, out = games(tmp_path, ["help"], color="black")
    game.run()
    assert any("undo" in o and "clock" in o for o in out)

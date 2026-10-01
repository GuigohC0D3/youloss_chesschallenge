import chess

from controller.state import load_state

BLACK_TO_MOVE = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"


def test_undo_twice_then_new_opponent_move(tmp_path, games):
    # begin → a2a3 (proposta+played), press+e7e5, a1a2 (proposta+played),
    # undo, undo (param o relógio; exigem 'clock' novo) → clock adv →
    # press+d7d5 → engine propõe de novo + played
    game, out = games(
        tmp_path,
        [
            "begin",
            "played",
            "press 24:30 24:45",
            "e7e5",
            "played",
            "undo",
            "undo",
            "clock 25:00 25:00 adv",
            "press 24:30 24:45",
            "d7d5",
            "played",
        ],
    )
    game.run()
    assert game.state.moves[:2] == ["a2a3", "d7d5"] and len(game.state.moves) == 3
    assert any(
        l.startswith("# undo")
        for l in (tmp_path / "g.log").read_text(encoding="utf-8").splitlines()
    )


def test_undo_pauses_on_our_turn_and_rejects_moves(tmp_path, games):
    # undo para o relógio e exige 'clock' novo: sem ele, go/played recusam.
    game, out = games(
        tmp_path,
        [
            "begin",
            "played",
            "press 24:30 24:45",
            "e7e5",
            "played",
            "undo",
            "clock 25:00 25:00 nos",
            "h2h3",
            "go",
            "played",
        ],
    )
    game.run()
    assert any("nossa vez" in o for o in out)
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]


def test_undo_with_nothing(tmp_path, games):
    game, out = games(tmp_path, ["undo"], color="black")
    game.run()
    assert any("nada a desfazer" in o for o in out)


def test_fen_resync_pauses_then_go(tmp_path, games):
    # fen para o relógio e exige 'clock' novo com seleção explícita.
    game, _ = games(
        tmp_path,
        ["begin", f"fen {BLACK_TO_MOVE}", "clock 25:00 25:00 nos", "go", "played"],
        color="black",
    )
    game.run()
    state = load_state(tmp_path / "g.state.json")
    assert state.start_fen == BLACK_TO_MOVE and len(state.moves) == 1


def test_invalid_fen_rejected(tmp_path, games):
    game, out = games(
        tmp_path, ["fen lixo", "fen 8/8/8/8/8/8/8/8 w - - 0 1"], color="black"
    )
    game.run()
    assert sum("FEN inválida" in o for o in out) == 2
    assert game.state.start_fen == chess.STARTING_FEN


def test_clock_sync(tmp_path, games):
    game, out = games(tmp_path, ["clock 10:00 12:30", "clock 10 12"], color="black")
    game.run()
    assert abs(game.clock.remaining(chess.BLACK) - 600_000) < 500
    assert abs(game.clock.remaining(chess.WHITE) - 750_000) < 500
    assert any("mm:ss" in o for o in out)


def test_undo_stops_clock_and_requires_fresh_sync(tmp_path, games):
    # undo para o relógio: go sem 'clock' novo não busca; com 'nos' volta a buscar.
    game, out = games(
        tmp_path,
        [
            "begin",
            "played",
            "press 24:30 24:45",
            "e7e5",
            "played",
            "undo",
            "go",
            "played",
        ],
    )
    sent = []
    real = game.engine.search

    def spy(position, go, timeout, stop_grace=2.0):
        sent.append((go, timeout))
        return real(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy
    game.run()
    assert (
        len(sent) == 2
    )  # 2 buscas antes do undo; go após undo com relógio parado não busca
    assert any("ressincronize" in o for o in out)
    assert game.state.moves == ["a2a3", "e7e5"]  # nada confirmado sem clock+go+played

    game2, out2 = games(
        tmp_path,
        [
            "begin",
            "played",
            "press 24:30 24:45",
            "e7e5",
            "played",
            "undo",
            "clock 25:00 25:00 nos",
            "go",
            "played",
        ],
    )
    game2.run()
    assert game2.state.moves == ["a2a3", "e7e5", "a1a2"]


def test_fen_stops_clock_and_requires_fresh_sync(tmp_path, games):
    game, out = games(
        tmp_path,
        ["begin", f"fen {BLACK_TO_MOVE}", "go", "played"],
        color="black",
    )
    game.run()
    assert any("ressincronize" in o for o in out)
    assert game.state.moves == []
    assert game.clock.running is None


def test_clock_selection_nos_adv_stop(tmp_path, games):
    game, out = games(
        tmp_path,
        [
            "begin",
            "played",
            "press 24:30 24:45",
            "e7e5",
            "played",
            "undo",
            "clock 25:00 24:00 stop",
            "go",
            "clock 25:00 24:00 nos",
            "go",
            "played",
        ],
    )
    game.run()
    text = "\n".join(out)
    assert "nosso relógio não está correndo" in text  # go com stop não busca
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]

    game2, out2 = games(tmp_path, ["clock 10:00 12:30 lado"], color="black")
    game2.run()
    assert any("uso: clock" in o for o in out2)


def test_board_shows_fen(tmp_path, games):
    game, out = games(tmp_path, ["board"], color="black")
    game.run()
    assert any(chess.STARTING_FEN in o for o in out)


def test_go_on_opponent_turn_is_rejected(tmp_path, games):
    game, out = games(tmp_path, ["begin", "go"], color="black")
    game.run()
    assert any("vez do adversário" in o for o in out)


def test_begin_required_before_search(tmp_path, games):
    game, out = games(tmp_path, ["go", "begin", "played"])
    game.run()
    text = "\n".join(out)
    assert "ainda não começou" in text
    assert game.state.moves == ["a2a3"]


def test_press_before_uci_and_played_once(tmp_path, games):
    game, out = games(
        tmp_path, ["begin", "played", "e7e5", "press 24:30 24:45", "e7e5", "played"]
    )
    game.run()
    text = "\n".join(out)
    assert "registre 'press' antes" in text
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]


def test_resign_and_draw(tmp_path, games):
    for answers, color, expected in [
        (["resign nos", "s"], "black", ("1-0", "resign_us")),
        (["resign adv", "sim"], "black", ("0-1", "resign_opponent")),
        (["resign"], "black", (None, None)),
        (["draw", "S"], "black", ("1/2-1/2", "draw_agreed")),
        (["draw", "n"], "black", (None, None)),
        (["resign adv", ""], "black", (None, None)),
    ]:
        sub = tmp_path / "_".join(answers).replace(" ", "-")
        sub.mkdir()
        game, _ = games(sub, answers, color=color)
        game.run()
        assert (game.state.result, game.state.reason) == expected


def test_help_lists_commands(tmp_path, games):
    game, out = games(tmp_path, ["help"], color="black")
    game.run()
    text = "\n".join(out)
    assert "undo" in text and "clock" in text
    assert "begin" in text and "press" in text and "played" in text


def test_undo_discards_pending_first_move_proposal(tmp_path, games):
    """Defect 3 RED: undo must discard a pending first-move proposal even with
    no confirmed moves. Matches established undo: pause clock, require fresh
    clock sync, persist cleared proposal, leave board/history unchanged."""
    game, out = games(tmp_path, ["begin", "undo"])
    assert game.run() is None
    assert game.state.moves == []
    assert game.state.pending_uci is None
    assert game.state.pending_source is None
    assert game.clock.running is None
    assert game._needs_clock is True
    assert game.paused is True
    assert game.board.fen() == chess.STARTING_FEN
    st = load_state(tmp_path / "g.state.json")
    assert st.pending_uci is None
    assert st.moves == []
    text = "\n".join(out)
    assert "nada a desfazer" not in text
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "undo" in log

    # Full flow after clearing: clock resync + go + played reproposes.
    game2, _ = games(
        tmp_path,
        ["begin", "undo", "clock 25:00 25:00 nos", "go", "played"],
    )
    game2.run()
    assert game2.state.moves == ["a2a3"]
    assert game2.state.pending_uci is None

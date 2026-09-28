import chess
import pytest

from controller.book import OpeningBook
from controller.clock import GameClock
from controller.game import Game
from controller.game_log import GameLog
from controller.state import GameState
from controller.tests.scripted import Script, fake_engine


@pytest.fixture
def games():
    made = []

    def factory(tmp_path, answers, color="white", fen=chess.STARTING_FEN, mode="ok",
                book=None, base_ms=60_000, paused=False, safety=2.0):
        state = GameState(color=color, opponent="teste", game=1, base_ms=base_ms,
                          inc_ms=100, start_fen=fen, white_ms=base_ms, black_ms=base_ms,
                          log_path=str(tmp_path / "g.log"))
        engine = fake_engine(mode)
        engine.start()
        engine.handshake(timeout=5)
        log = GameLog(tmp_path / "g.log")
        out: list[str] = []
        game = Game(state, tmp_path / "g.state.json", engine, OpeningBook(book), log,
                    GameClock(base_ms, 100), input_fn=Script(answers),
                    output_fn=out.append, paused=paused, safety_margin_s=safety)
        made.append((engine, log))
        return game, out

    yield factory
    for engine, log in made:
        engine.quit()
        log.close()

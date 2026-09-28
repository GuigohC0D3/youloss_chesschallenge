from datetime import date

from controller.engine_client import SearchInfo
from controller.game_log import (
    LINE_RE, GameLog, _main, check_log, format_eval, log_path, slug,
)


def test_format_eval():
    assert format_eval(42, None) == "+0.42"
    assert format_eval(-130, None) == "-1.30"
    assert format_eval(0, None) == "+0.00"
    assert format_eval(None, 5) == "M5"
    assert format_eval(None, -3) == "-M3"
    assert format_eval(None, None) == "none"


def test_slug_and_log_path(tmp_path):
    assert slug("Équipe Xadrez 2!") == "equipe-xadrez-2"
    assert slug("***") == "adversario"
    p = log_path(tmp_path, "Time X", 3, date(2026, 10, 28))
    assert p == tmp_path / "2026-10-28_time-x_g3.log"


def test_engine_line_matches_spec(tmp_path):
    log = GameLog(tmp_path / "g.log")
    info = SearchInfo(bestmove="g1f3", depth=31, seldepth=44, nodes=182334112,
                      score_cp=42, pv=["g1f3", "d7d5"])
    log.our_move(12, "white", "g1f3", "engine", 21873, info)
    line = (tmp_path / "g.log").read_text(encoding="utf-8").splitlines()[0]
    assert line == ('move=12 color=white uci=g1f3 depth=31 seldepth=44 nodes=182334112 '
                    'eval=+0.42 pv="g1f3 d7d5" time_ms=21873 source=engine')
    assert LINE_RE.match(line)
    log.close()


def test_book_forced_and_opponent_lines(tmp_path):
    log = GameLog(tmp_path / "g.log")
    log.our_move(1, "white", "e2e4", "book", 3)
    log.our_move(2, "white", "e1f1", "forced", 1)
    log.opponent_move(1, "black", "e7e5", 5000)
    lines = (tmp_path / "g.log").read_text(encoding="utf-8").splitlines()
    assert lines[0] == 'move=1 color=white uci=e2e4 depth=0 seldepth=0 nodes=0 eval=book pv="e2e4" time_ms=3 source=book'
    assert lines[2] == "move=1 color=black uci=e7e5 time_ms=5000 source=opponent"
    assert all(LINE_RE.match(line) for line in lines)
    log.close()


def test_header_note_result_and_append(tmp_path):
    path = tmp_path / "g.log"
    log = GameLog(path)
    log.header(color="white", start_fen="rnbqkbnr/8 w - - 0 1")
    log.close()
    log = GameLog(path)  # reabrir (resume) não apaga o que já existe
    log.note("resume")
    log.result("1-0", "checkmate")
    log.close()
    assert path.read_text(encoding="utf-8").splitlines() == [
        '# color=white start_fen="rnbqkbnr/8 w - - 0 1"',
        "# resume",
        "# result=1-0 reason=checkmate",
    ]


def test_lines_visible_before_close(tmp_path):
    log = GameLog(tmp_path / "g.log")
    log.opponent_move(1, "black", "e7e5", 10)
    assert "e7e5" in (tmp_path / "g.log").read_text(encoding="utf-8")
    log.close()


def test_check_log_flags_bad_lines(tmp_path):
    path = tmp_path / "g.log"
    path.write_text("# ok\nmove=1 color=white uci=e2e4 time_ms=1 source=opponent\nlixo\n",
                    encoding="utf-8")
    assert check_log(path) == ["3: lixo"]
    assert _main([str(path)]) == 1

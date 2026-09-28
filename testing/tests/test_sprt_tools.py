from testing.sprt_result import summarize
from testing.time_profile import mean_total, profile

LOG_H1 = """
Results of tm vs sf (10+0.1, 1t, 16MB, UHO_Lichess_4852_v1.epd):
Elo: 1.25 +/- 3.40, nElo: 2.10 +/- 5.70
Games: 4000, Wins: 900, Losses: 886, Draws: 2214, Points: 2007.0 (50.18 %)
LLR: 2.96 (100.5%) (-2.94, 2.94) [-5.00, 0.00]
SPRT ([-5.00, 0.00]) completed - H1 was accepted
"""


def test_h1_accepted():
    code, line = summarize(LOG_H1)
    assert code == 0
    assert "H1" in line and "4000" in line and "2.96" in line


def test_h0_accepted():
    code, _ = summarize(LOG_H1.replace("H1 was accepted", "H0 was accepted"))
    assert code == 1


def test_inconclusive_uses_last_block():
    text = LOG_H1.replace("SPRT ([-5.00, 0.00]) completed - H1 was accepted", "")
    text += "Games: 5000, Wins: 1\nLLR: 1.10 (37.4%) (-2.94, 2.94) [-5.00, 0.00]\n"
    code, line = summarize(text)
    assert code == 2 and "5000" in line and "1.10" in line


PGN = """[Event "Fastchess Tournament"]
[White "tm"]
[Black "sf"]
[Result "0-1"]
[FEN "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"]
[Termination "time forfeit"]

1... e5 {+0.10/10 0.500s} 2. Nf3 {+0.20/11 1.000s} Nc6 {-0.10/9 0.250s}
3. Bb5 {+0.30/12 2.000s, White loses on time} 0-1

[Event "Fastchess Tournament"]
[White "sf"]
[Black "tm"]
[Result "1/2-1/2"]
[FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]
[Termination "adjudication"]

1. d4 {+0.10/10 1.500s} d5 {-0.05/10 0.500s} 1/2-1/2
"""


def test_profile_assigns_moves_to_engines_and_buckets():
    prof = profile(PGN)
    assert prof["tm"].games == 2 and prof["sf"].games == 2
    assert abs(prof["tm"].total_s - (1.0 + 2.0 + 0.5)) < 1e-9
    assert abs(prof["sf"].total_s - (0.5 + 0.25 + 1.5)) < 1e-9
    assert prof["tm"].buckets["1-10"] == [1.0, 2.0, 0.5]
    assert prof["tm"].forfeits == 1 and prof["sf"].forfeits == 0
    assert abs(mean_total(prof["tm"]) - 1.75) < 1e-9

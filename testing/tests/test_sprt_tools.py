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
    text = LOG_H1.replace("LLR: 2.96", "LLR: -2.96").replace("H1 was accepted", "H0 was accepted")
    code, line = summarize(text)
    assert code == 1
    assert "H0" in line and "-2.96" in line


def test_misleading_inbound_h1_marker():
    text = LOG_H1.replace("LLR: 2.96", "LLR: 1.10")
    code, line = summarize(text)
    assert code == 2
    assert "inconclusivo" in line and "1.10" in line


def test_misleading_inbound_h0_marker():
    text = LOG_H1.replace("LLR: 2.96", "LLR: -1.10").replace("H1 was accepted", "H0 was accepted")
    code, line = summarize(text)
    assert code == 2
    assert "inconclusivo" in line and "-1.10" in line


def test_missing_numeric_data():
    text = LOG_H1.replace("LLR: 2.96 (100.5%) (-2.94, 2.94) [-5.00, 0.00]\n", "")
    code, line = summarize(text)
    assert code == 2
    assert "inconclusivo" in line and "llr=?" in line


def test_malformed_numeric_data():
    text1 = LOG_H1.replace("LLR: 2.96 (100.5%) (-2.94, 2.94) [-5.00, 0.00]", "LLR: corrupt")
    code1, line1 = summarize(text1)
    assert code1 == 2 and "inconclusivo" in line1

    text2 = LOG_H1.replace("(-2.94, 2.94)", "(bad, bounds)")
    code2, line2 = summarize(text2)
    assert code2 == 2 and "inconclusivo" in line2

    text3 = LOG_H1.replace("LLR: 2.96 (100.5%) (-2.94, 2.94) [-5.00, 0.00]", "LLR: 2.96")
    code3, line3 = summarize(text3)
    assert code3 == 2 and "inconclusivo" in line3


def test_llr_with_trailing_numeric_junk_is_inconclusive():
    text = LOG_H1.replace("LLR: 2.96", "LLR: 3.0oops")
    code, line = summarize(text)
    assert code == 2 and "inconclusivo" in line


def test_rounded_boundary_does_not_claim_sprt_acceptance():
    text = LOG_H1.replace("LLR: 2.96", "LLR: 2.94")
    code, line = summarize(text)
    assert code == 2 and "inconclusivo" in line


def test_zero_games_cannot_be_reported_as_accepted():
    text = LOG_H1.replace("Games: 4000,", "Games: 0,")
    code, line = summarize(text)
    assert code == 2 and "inconclusivo" in line


def test_mismatched_markers():
    text_mismatch_h0 = LOG_H1.replace("H1 was accepted", "H0 was accepted")
    code, line = summarize(text_mismatch_h0)
    assert code == 2 and "inconclusivo" in line

    text_mismatch_h1 = LOG_H1.replace("LLR: 2.96", "LLR: -2.96")
    code, line = summarize(text_mismatch_h1)
    assert code == 2 and "inconclusivo" in line


def test_inconclusive_uses_last_block():
    text = LOG_H1.replace("SPRT ([-5.00, 0.00]) completed - H1 was accepted", "")
    text += (
        "Games: 5000, Wins: 1, Losses: 1, Draws: 4998, Points: 2500.0 "
        "(50.00 %)\nLLR: 1.10 (37.4%) (-2.94, 2.94) [-5.00, 0.00]\n"
    )
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

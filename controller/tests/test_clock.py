import chess
import pytest

from controller.clock import (
    ClockFormatError, GameClock, format_mmss, parse_mmss, parse_tc,
)


class FakeTime:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


def test_parse_tc():
    assert parse_tc("900+10") == (900_000, 10_000)
    assert parse_tc(" 60+0.6 ") == (60_000, 600)


@pytest.mark.parametrize("bad", ["900", "abc", "0+1", "900+", "+10", "-5+1"])
def test_parse_tc_rejects(bad):
    with pytest.raises(ClockFormatError):
        parse_tc(bad)


def test_parse_mmss():
    assert parse_mmss("14:59") == 899_000
    assert parse_mmss("0:05") == 5_000
    assert parse_mmss("100:00") == 6_000_000


@pytest.mark.parametrize("bad", ["1:60", "abc", "-1:00", "10", "1:5"])
def test_parse_mmss_rejects(bad):
    with pytest.raises(ClockFormatError):
        parse_mmss(bad)


def test_format_mmss():
    assert format_mmss(899_000) == "14:59"
    assert format_mmss(500) == "0:00"
    assert format_mmss(-3_000) == "-0:03"


def test_press_charges_mover_adds_increment_and_switches():
    t = FakeTime()
    clock = GameClock(60_000, 1_000, now=t)
    clock.start(chess.WHITE)
    t.t += 3
    assert clock.remaining(chess.WHITE) == 57_000
    assert clock.press() == 3_000
    assert clock.remaining(chess.WHITE) == 58_000
    assert clock.running == chess.BLACK
    t.t += 2
    assert clock.remaining(chess.BLACK) == 58_000


def test_set_overrides_running_side():
    t = FakeTime()
    clock = GameClock(60_000, 1_000, now=t)
    clock.start(chess.BLACK)
    t.t += 10
    clock.set(chess.BLACK, 5_000)
    assert clock.remaining(chess.BLACK) == 5_000
    t.t += 1
    assert clock.remaining(chess.BLACK) == 4_000


def test_start_switches_without_increment():
    t = FakeTime()
    clock = GameClock(60_000, 1_000, now=t)
    clock.start(chess.WHITE)
    t.t += 2
    clock.start(chess.BLACK)
    assert clock.remaining(chess.WHITE) == 58_000
    assert clock.running == chess.BLACK


def test_press_when_stopped_raises():
    with pytest.raises(RuntimeError):
        GameClock(60_000, 0).press()

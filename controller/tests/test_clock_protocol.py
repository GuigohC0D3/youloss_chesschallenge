"""Regressão do protocolo físico: begin/press/played, proposta única, resume e teto de busca."""

import chess
import pytest

from controller.game import MAX_THINK_FRACTION, STOP_GRACE_S
from controller.game_log import LINE_RE
from controller.state import load_state


def test_normal_order_white(tmp_path, games):
    game, out = games(
        tmp_path,
        ["begin", "played", "press 24:30 24:45", "e7e5", "played"],
        clock_latency=1.5,
    )
    assert game.run() is None
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]
    assert game.state.pending_uci is None
    text = "\n".join(out)
    assert "PROPOSTA: a2a3" in text
    assert "LANCE CONFIRMADO: a2a3" in text
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "# proposal" in log and "# press" in log
    assert "latency_allowance_ms=1500" in log
    assert game.clock.running == chess.BLACK  # após confirmar, vez do adversário


def test_duplicate_events_rejected_once(tmp_path, games):
    # played duplo confirma exatamente uma vez (sem duplicatas no log).
    game, out = games(
        tmp_path,
        [
            "begin",
            "begin",
            "played",
            "played",
            "press 24:30 24:45",
            "press 24:30 24:45",
            "e7e5",
            "e7e5",
            "played",
            "played",
        ],
    )
    game.run()
    text = "\n".join(out)
    assert "já iniciada" in text
    assert "sem proposta pendente" in text
    assert "já registrado" in text
    assert "nossa vez" in text  # segundo e7e5 cai na nossa vez
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]
    moves = [
        l
        for l in (tmp_path / "g.log").read_text(encoding="utf-8").splitlines()
        if l.startswith("move=")
    ]
    assert len(moves) == 3


def test_bare_press_rejected_blocks_opponent_uci_until_reading_supplied(
    tmp_path, games
):
    """Bare press é estritamente rejeitado, bloqueia o lance UCI seguinte até que
    uma leitura física seja fornecida, e press com leituras físicas libera a vez."""
    game, out = games(
        tmp_path,
        [
            "begin",
            "played",
            "press",  # 1. Bare press rejeitado (leitura física obrigatória)
            "e7e5",  # 2. UCI do adversário rejeitado pois relógio não avançou
            "press 24:30 24:45",  # 3. Press com leituras físicas aceito
            "e7e5",  # 4. UCI do adversário aceito
            "played",  # 5. Lance nosso proposto e confirmado
        ],
    )
    assert game.run() is None
    text = "\n".join(out)
    assert "leitura física obrigatória" in text
    assert (
        "relógio do adversário ainda correndo: registre 'press' antes do lance" in text
    )
    assert (
        "relógio sincronizado com leitura física (-2.0s latência conservadora deduzida)"
        in text
    )
    assert game.state.moves == ["a2a3", "e7e5", "a1a2"]
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "latency_allowance_ms=2000" in log


def test_clock_latency_validation_and_rejection():
    """--clock-latency e Game.__init__ rejeitam negativo, NaN, inf e valores desarrazoados (> 60s)."""
    from controller.game import Game
    from controller.main import build_parser

    parser = build_parser()
    # CLI aceita valor válido
    args = parser.parse_args(["start", "--color", "white", "--clock-latency", "1.5"])
    assert args.clock_latency == 1.5

    # CLI rejeita valores inválidos
    for bad in ["-1", "-0.1", "nan", "NaN", "inf", "-inf", "60.1", "100"]:
        with pytest.raises(SystemExit):
            parser.parse_args(["start", "--color", "white", f"--clock-latency={bad}"])

    # Game.__init__ rejeita diretamente valores inválidos na primeira linha do construtor
    for bad_f in [-1.0, -0.01, float("nan"), float("inf"), float("-inf"), 60.1, 100.0]:
        with pytest.raises(ValueError, match="fora da faixa"):
            Game(
                state=None,  # type: ignore[arg-type]
                state_path=None,  # type: ignore[arg-type]
                engine=None,  # type: ignore[arg-type]
                book=None,  # type: ignore[arg-type]
                log=None,  # type: ignore[arg-type]
                clock=None,  # type: ignore[arg-type]
                clock_latency_s=bad_f,
            )


def test_press_positive_reading_with_zero_margin_triggers_fallback_not_flag(
    tmp_path, games
):
    """Leitura física positiva (00:01) com latência 2.0s zera a margem:
    usa piso de 1s e aciona fallback imediato seguro sem declarar flag prematuro."""
    game, out = games(
        tmp_path,
        [
            "begin",
            "played",
            "press 00:01 24:45",  # 1s físico - 2s latência <= 0 -> floor 1s
            "e7e5",
            "played",
        ],
        clock_latency=2.0,
    )
    assert game.run() is None
    text = "\n".join(out)
    assert "fallback imediato ativado (sem flag)" in text
    assert game.state.result is None  # não declarou flag
    assert game.state.moves == ["a2a3", "e7e5", "a3a4"]
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "floor 1s: leitura física positiva, fallback sem flag prematuro" in log


def test_positive_reading_tiny_conservative_margin_emits_fallback_not_flag(
    tmp_path, games
):
    """Leitura física positiva (00:02 = 2000ms) com latência 1.995s deixa apenas 5ms de margem.
    O overhead do controlador (simulado com avanço determinístico de 50ms no relógio monotônico)
    expira a estimativa interna antes da proposta: não deve gerar flag da estimativa,
    exige leitura física fresca; leitura fresca positiva (00:01) permite fallback
    imediato rotulado e persiste o lance."""
    game, out = games(
        tmp_path,
        [
            "begin",
            "played",
            "press 00:02 24:45",  # 2000ms físico - 1995ms latência = 5ms margem
            "e7e5",
            "clock 00:01 24:45 nos",  # leitura fresca positiva após expiry
            "played",
        ],
        clock_latency=1.995,
    )

    class FakeMonotonic:
        def __init__(self) -> None:
            self.t = 1000.0

        def __call__(self) -> float:
            return self.t

    fake = FakeMonotonic()
    game.clock._now = fake  # type: ignore[attr-defined]

    orig_input = game.input_fn
    sync: list = []

    def advancing_input(prompt: str) -> str:
        cmd = orig_input(prompt)
        if "e7e5" in cmd:
            fake.t += 0.050  # 50 ms decorridos > 5 ms de margem
        elif cmd.startswith("clock "):
            sync.append(
                (
                    game.state.result,
                    game._needs_clock,
                    game.clock.running,
                    getattr(game, "_physical_read_required", False),
                )
            )
        return cmd

    game.input_fn = advancing_input

    assert game.run() is None
    assert sync == [(None, True, None, True)]
    assert game.state.result is None  # Não houve flag prematuro
    assert game.state.moves == ["a2a3", "e7e5", "a3a4"]
    text = "\n".join(out)
    assert "PROPOSTA IMEDIATA (fallback-lowtime)" in text or "fallback-lowtime" in text
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "physical_ours=00:02" in log
    assert "latency_allowance_ms=1995" in log
    assert "adjusted_estimate_ms=5" in log
    assert "clock-sync-recovery" in log
    assert "fallback-lowtime" in log
    assert "source=fallback" in log


def test_resume_requires_fen_and_clock_without_autoconfirm(tmp_path, games):
    # go/press/played antes da reconciliação são recusados e nada anda.
    game, out = games(
        tmp_path,
        ["go", "press", "played"],
        paused=True,
        resumed=True,
    )
    assert game.run() is None
    assert game.state.moves == []
    assert "ressincronize" in "\n".join(out)

    # Proposta pendente salva nunca é auto-confirmada no resume.
    game2, _ = games(tmp_path, ["begin"])  # propõe a2a3 e sai (quit via EOF)
    game2.run()
    st = load_state(tmp_path / "g.state.json")
    assert st.pending_uci == "a2a3"
    assert st.moves == []

    # Quit imediato no resume não empurra a proposta sozinho.
    game_tmp, _ = games(tmp_path, [], paused=True, resumed=True)
    game_tmp.state = load_state(tmp_path / "g.state.json")
    game_tmp.board = game_tmp.state.board()
    assert game_tmp.run() is None
    assert load_state(tmp_path / "g.state.json").pending_uci == "a2a3"
    assert load_state(tmp_path / "g.state.json").moves == []

    # fen descarta a proposta antiga; clock com 'nos' religa; go+played confirmam.
    game3, out3 = games(
        tmp_path,
        [
            "played",
            f"fen {chess.STARTING_FEN}",
            "clock 25:00 25:00 nos",
            "go",
            "played",
        ],
        paused=True,
        resumed=True,
    )
    # Reidrata o estado com a proposta pendente (simula o --resume real).
    game3.state = load_state(tmp_path / "g.state.json")
    game3.board = game3.state.board()
    game3.run()
    text3 = "\n".join(out3)
    assert "ressincronize" in text3  # played antes de fen+clock é recusado
    assert game3.state.moves == ["a2a3"]  # só entra após go+played explícitos
    assert game3.state.pending_uci is None


def test_resume_stop_then_nos_selection(tmp_path, games):
    # Resume reconcilia FEN/tempo com 'stop': go não busca; com 'nos' busca e confirma.
    game, out = games(
        tmp_path,
        [
            f"fen {chess.STARTING_FEN}",
            "clock 25:00 25:00 stop",
            "go",
            "clock 25:00 25:00 nos",
            "go",
            "played",
        ],
        paused=True,
        resumed=True,
    )
    sent = []
    real = game.engine.search

    def spy(position, go, timeout, stop_grace=2.0):
        sent.append((go, timeout, stop_grace))
        return real(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy
    assert game.run() is None
    text = "\n".join(out)
    assert "não está correndo" in text  # go com relógio parado é recusado
    assert "PROPOSTA" in text  # após 'nos', go volta a propor
    assert len(sent) == 1  # exatamente uma busca: só a legítima
    go, timeout, stop_grace = sent[0]
    ours = 25 * 60  # 25:00 sincronizado
    assert timeout + stop_grace + game.safety_margin_s <= ours + 0.5
    assert game.state.moves == ["a2a3"]
    assert game.state.pending_uci is None
    assert game.state.result is None


def test_wrong_side_and_stopped_clock_guards(tmp_path, games):
    # press na nossa vez é recusado.
    game, out = games(tmp_path, ["begin", "press", "played"])
    game.run()
    assert any("não é a vez do adversário" in o for o in out)
    assert game.state.moves == ["a2a3"]

    # UCI sem press é recusado.
    game, out = games(tmp_path, ["begin", "played", "e7e5"])
    game.run()
    assert any("registre 'press' antes" in o for o in out)
    assert game.state.moves == ["a2a3"]  # só a nossa confirmada

    # played sem proposta é recusado.
    game, out = games(tmp_path, ["begin", "played", "played"])
    game.run()
    assert any("sem proposta pendente" in o for o in out)

    # clock parado não habilita busca: sync parado + go recusado.
    game, out = games(tmp_path, ["clock 10:00 10:00", "go", "begin", "played"])
    game.run()
    text = "\n".join(out)
    assert "ainda não começou" in text  # go antes do begin
    assert game.state.moves == ["a2a3"]


def test_search_budget_fits_remaining(tmp_path, games):
    game, _ = games(tmp_path, ["begin", "played"], base_ms=60_000, safety=2.0)
    seen = []
    real = game.engine.search

    def spy(position, go, timeout, stop_grace=2.0):
        seen.append((go, timeout, stop_grace))
        return real(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy
    game.run()
    assert seen, "deveria ter buscado uma vez"
    go, timeout, stop_grace = seen[0]
    assert stop_grace == STOP_GRACE_S == 1.0
    ours = 60_000  # base do fixture (deriva de ms não conta aqui)
    assert timeout <= ours * MAX_THINK_FRACTION / 1000 + 0.5
    assert timeout + stop_grace + game.safety_margin_s <= ours / 1000 + 0.5
    assert "wtime" in go and "btime" in go


def test_low_time_fallback_is_labeled_not_flag(tmp_path, games):
    # 2,5 s restantes não cobrem stop (1 s) + reserva (2 s) → fallback imediato.
    game, out = games(tmp_path, ["begin", "played"], base_ms=2_500, safety=2.0)
    assert game.run() is None
    assert len(game.state.moves) == 1
    assert game.state.result is None  # não é flag
    text = "\n".join(out)
    assert "fallback-lowtime" in text
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "fallback-lowtime" in log
    assert "source=fallback" in log
    moves = [l for l in log.splitlines() if l.startswith("move=")]
    assert len(moves) == 1 and all(LINE_RE.match(l) for l in moves)


@pytest.mark.parametrize("base_ms", [3001, 3050, 3099])
def test_fallback_boundary_no_engine_wait_no_flag(tmp_path, games, base_ms):
    # 3001–3099 ms com stop (1 s) + reserva (2 s): margem útil < 100 ms →
    # nenhum wait no engine, proposta fallback imediata, sem flag prematura.
    game, out = games(tmp_path, ["begin", "played"], base_ms=base_ms, safety=2.0)
    sent = []
    real = game.engine.search

    def spy(position, go, timeout, stop_grace=2.0):
        sent.append((go, timeout, stop_grace))
        return real(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy
    assert game.run() is None
    assert sent == []  # nenhum wait no engine excede o orçamento
    assert game.state.result is None  # sem flag prematura com tempo restante
    assert len(game.state.moves) == 1
    text = "\n".join(out)
    assert "fallback-lowtime" in text
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "fallback-lowtime" in log
    assert "source=fallback" in log


def test_estimated_zero_requires_confirmed_physical_zero(tmp_path, games):
    game, out = games(
        tmp_path,
        ["begin", "clock 00:00 01:00 nos"],
        base_ms=60_000,
    )
    game.clock.set(chess.WHITE, 0)
    searches = []
    real_search = game.engine.search

    def spy_search(position, go, timeout, stop_grace=2.0):
        searches.append((position, go, timeout))
        return real_search(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy_search

    assert game.run() == "0-1"
    assert game.state.reason == "flag"
    assert searches == []
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "clock-sync-recovery" in log
    assert "physical flag confirmed" in log
    assert any("FIM DE PARTIDA" in o and "flag" in o for o in out)


def delayed_clock_sync_game(tmp_path, games, fresh_ours: str):
    """Reproduce a slow UCI entry after the opponent starts our physical clock."""
    game, out = games(
        tmp_path,
        [
            "begin",
            "press 00:10 00:59",
            "e2e4",
            f"clock {fresh_ours} 00:59 nos",
            "played",
        ],
        color="black",
        clock_latency=2.0,
    )

    class FakeMonotonic:
        t = 1000.0

        def __call__(self) -> float:
            return self.t

    now = FakeMonotonic()
    game.clock._now = now  # type: ignore[attr-defined]
    searches = []
    real_search = game.engine.search

    def spy_search(position, go, timeout, stop_grace=2.0):
        searches.append((position, go, timeout))
        return real_search(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy_search
    sync_observations = []
    original_input = game.input_fn

    def advancing_input(prompt: str) -> str:
        answer = original_input(prompt)
        if answer == "e2e4":
            now.t += 8.1
        elif answer.startswith("clock "):
            sync_observations.append(
                (
                    game.state.result,
                    len(searches),
                    game._needs_clock,
                    game.clock.running,
                    getattr(game, "_physical_read_required", False),
                )
            )
        return answer

    game.input_fn = advancing_input
    return game, out, searches, sync_observations


def test_delayed_uci_expiry_requires_fresh_physical_reading_before_search(
    tmp_path, games
):
    # 00:10 at press minus 2s latency leaves 8s. Typing e2e4 takes 8.1s,
    # making only the conservative estimate negative; the physical display
    # still has about 1.9s. A fresh 00:01 reading must use immediate fallback.
    game, out, searches, sync = delayed_clock_sync_game(tmp_path, games, "00:01")

    assert game.run() is None
    assert sync == [(None, 0, True, None, True)]
    assert searches == []
    assert game.state.result is None
    assert game.state.reason is None
    assert game.state.moves[0] == "e2e4"
    assert game.state.pending_uci is None  # fallback was physically confirmed
    assert "clock-sync-recovery" in (tmp_path / "g.log").read_text(encoding="utf-8")
    assert any("PROPOSTA IMEDIATA (fallback-lowtime)" in line for line in out)


def test_fresh_positive_reading_deducts_latency_before_search(tmp_path, games):
    game, _, searches, sync = delayed_clock_sync_game(tmp_path, games, "00:10")

    assert game.run() is None
    assert sync == [(None, 0, True, None, True)]
    assert len(searches) == 1
    assert "btime 8000" in searches[0][1]
    assert game.state.result is None


def test_confirmed_physical_zero_after_estimate_expiry_flags(tmp_path, games):
    game, out, searches, sync = delayed_clock_sync_game(tmp_path, games, "00:00")

    assert game.run() == "1-0"
    assert sync == [(None, 0, True, None, True)]
    assert searches == []
    assert game.state.reason == "flag"
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "physical flag confirmed" in log
    assert any("FIM DE PARTIDA" in line and "flag" in line for line in out)


def test_press_physical_zero_flags_after_recording_opponent_move(tmp_path, games):
    game, out = games(
        tmp_path,
        ["begin", "press 00:00 00:59", "e2e4"],
        color="black",
    )

    assert game.run() == "1-0"
    assert game.state.reason == "flag"
    assert game.state.moves == ["e2e4"]
    assert "physical flag confirmed" in (tmp_path / "g.log").read_text(encoding="utf-8")
    assert any("FIM DE PARTIDA" in line and "flag" in line for line in out)


def test_search_budget_rechecked_at_dispatch(tmp_path, games):
    # stop (1 s) + reserva (2 s) + mínimo (100 ms) = 3100 ms.
    # Começa em 3200 ms (avail 200, buscaria) e o relógio avança 700 ms
    # durante a seleção de book → 2500 ms (avail negativo, fallback).
    # Sem engine call, sem flag prematura, fallback imediato proposto.
    from controller.game import MIN_USEFUL_SEARCH_MS

    assert MIN_USEFUL_SEARCH_MS == 100
    game, out = games(tmp_path, ["begin", "played"], base_ms=3_200, safety=2.0)

    class FakeMonotonic:
        def __init__(self) -> None:
            self.t = 1000.0

        def __call__(self) -> float:
            return self.t

    fake = FakeMonotonic()
    game.clock._now = fake  # type: ignore[attr-defined]

    orig_pick = game.book.pick

    def pick_and_advance(board):
        fake.t += 0.7
        return orig_pick(board)

    game.book.pick = pick_and_advance  # type: ignore[method-assign]
    sent = []
    real = game.engine.search

    def spy(position, go, timeout, stop_grace=2.0):
        sent.append((go, timeout, stop_grace))
        return real(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy
    assert game.run() is None
    assert sent == []  # nenhuma chamada ao engine após o relógio cruzar
    assert game.state.result is None  # sem flag prematura com tempo positivo
    assert len(game.state.moves) == 1
    text = "\n".join(out)
    assert "fallback-lowtime" in text
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "fallback-lowtime" in log
    assert "source=fallback" in log
    moves = [l for l in log.splitlines() if l.startswith("move=")]
    assert len(moves) == 1 and all(LINE_RE.match(l) for l in moves)


def test_low_margin_must_not_bypass_estimate_expiry(tmp_path, games):
    """Defect 1 RED: low-margin press (00:02 - 1.995s = 5ms) expiring during
    opponent UCI entry (50ms) must stop and require a fresh physical reading,
    not emit an immediate fallback without reconciliation."""
    game, out = games(
        tmp_path,
        [
            "begin",
            "played",
            "press 00:02 24:45",
            "e7e5",
            "played",
        ],
        clock_latency=1.995,
    )

    class FakeMonotonic:
        def __init__(self) -> None:
            self.t = 1000.0

        def __call__(self) -> float:
            return self.t

    fake = FakeMonotonic()
    game.clock._now = fake  # type: ignore[attr-defined]
    orig_input = game.input_fn

    def advancing_input(prompt: str) -> str:
        cmd = orig_input(prompt)
        if cmd == "e7e5":
            fake.t += 0.050
        return cmd

    game.input_fn = advancing_input
    assert game.run() is None
    # No flag from estimate alone.
    assert game.state.result is None
    assert game.state.reason is None
    # Opponent move recorded, but our fallback NOT confirmed without fresh reading.
    assert game.state.moves == ["a2a3", "e7e5"]
    assert game.state.pending_uci is None
    assert game._needs_clock is True
    assert game.clock.running is None
    assert getattr(game, "_physical_read_required", False) is True
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "clock-sync-recovery" in log
    text = "\n".join(out)
    assert "PROPOSTA IMEDIATA" not in text


def low_margin_delayed_game(tmp_path, games, fresh_ours: str):
    """Low-margin variant of delayed_clock_sync_game: press 00:02 - 1.995s = 5ms,
    then 50ms typing expiry. Fresh reading decides fallback vs flag."""
    game, out = games(
        tmp_path,
        [
            "begin",
            "played",
            "press 00:02 24:45",
            "e7e5",
            f"clock {fresh_ours} 00:59 nos",
            "played",
        ],
        clock_latency=1.995,
    )

    class FakeMonotonic:
        t = 1000.0

        def __call__(self) -> float:
            return self.t

    now = FakeMonotonic()
    game.clock._now = now  # type: ignore[attr-defined]
    searches: list = []
    real_search = game.engine.search

    def spy_search(position, go, timeout, stop_grace=2.0):
        searches.append((position, go, timeout))
        return real_search(position, go, timeout, stop_grace=stop_grace)

    game.engine.search = spy_search
    sync_observations = []
    original_input = game.input_fn

    def advancing_input(prompt: str) -> str:
        answer = original_input(prompt)
        if answer == "e7e5":
            now.t += 0.050
        elif answer.startswith("clock "):
            sync_observations.append(
                (
                    game.state.result,
                    len(searches),
                    game._needs_clock,
                    game.clock.running,
                    getattr(game, "_physical_read_required", False),
                )
            )
        return answer

    game.input_fn = advancing_input
    return game, out, searches, sync_observations


def test_low_margin_expiry_fresh_positive_permits_fallback(tmp_path, games):
    game, out, searches, sync = low_margin_delayed_game(tmp_path, games, "00:01")
    assert game.run() is None
    # One engine search for the initial a2a3 proposal; expiry blocks any further
    # search until the fresh physical reading, then immediate fallback.
    assert sync == [(None, 1, True, None, True)]
    assert len(searches) == 1
    assert game.state.result is None
    assert game.state.moves == ["a2a3", "e7e5", "a3a4"]
    assert game.state.pending_uci is None
    assert any("PROPOSTA IMEDIATA (fallback-lowtime)" in line for line in out)


def test_low_margin_expiry_fresh_zero_flags(tmp_path, games):
    game, out, searches, sync = low_margin_delayed_game(tmp_path, games, "00:00")
    assert game.run() == "0-1"
    assert sync == [(None, 1, True, None, True)]
    assert len(searches) == 1
    assert game.state.reason == "flag"
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "physical flag confirmed" in log


def test_played_after_estimate_expiry_requires_fresh_reading(tmp_path, games):
    """Defect 2 RED: played must not silently confirm after estimate expiry.
    Positive fresh reading allows continuing and confirming the proposal;
    estimate alone must not flag."""
    game, out = games(
        tmp_path,
        ["begin", "played", "clock 00:05 01:00 nos", "played"],
        base_ms=60_000,
    )
    orig = game.input_fn
    expired_once = False
    sync: list = []

    def expiring_input(prompt: str) -> str:
        nonlocal expired_once
        ans = orig(prompt)
        if ans == "played" and not expired_once:
            expired_once = True
            game.clock.set(game.us, 0)
        elif ans.startswith("clock "):
            sync.append(
                (
                    game.state.result,
                    len(game.state.moves),
                    game._needs_clock,
                    game.clock.running,
                    getattr(game, "_physical_read_required", False),
                    game.state.pending_uci,
                )
            )
        return ans

    game.input_fn = expiring_input
    assert game.run() is None
    # Estimate expiry blocked the first played: still 0 moves at clock time,
    # pending preserved, recovery required, no flag from estimate.
    assert sync == [(None, 0, True, None, True, "a2a3")]
    assert game.state.result is None
    assert game.state.reason is None
    assert game.state.moves == ["a2a3"]
    assert game.state.pending_uci is None
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "clock-sync-recovery" in log
    assert "physical flag confirmed" not in log


def test_played_expiry_confirmed_zero_flags(tmp_path, games):
    """Defect 2 RED (zero path): after estimate expiry, confirmed physical
    00:00 must record a flag; estimate alone must not."""
    game, out = games(
        tmp_path,
        ["begin", "played", "clock 00:00 01:00 nos"],
        base_ms=60_000,
    )
    orig = game.input_fn
    expired_once = False

    def expiring_input(prompt: str) -> str:
        nonlocal expired_once
        ans = orig(prompt)
        if ans == "played" and not expired_once:
            expired_once = True
            game.clock.set(game.us, 0)
        return ans

    game.input_fn = expiring_input
    assert game.run() == "0-1"
    assert game.state.reason == "flag"
    assert game.state.moves == []
    log = (tmp_path / "g.log").read_text(encoding="utf-8")
    assert "physical flag confirmed" in log

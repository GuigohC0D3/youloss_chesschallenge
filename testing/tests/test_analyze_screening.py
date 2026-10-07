import json
import sys
from pathlib import Path

import pytest

from testing.analyze_screening import (
    EngineTelemetry,
    _student_t_critical_975,
    analyze_screening_runs,
    generate_recommendations,
    load_scoreboard_run_dirs,
    main,
    parse_eval_cp,
    parse_paired_scores,
    parse_pgn_file,
    summarize_paired_scores,
)

SAMPLE_FEN_PGN = """[Event "Fastchess Tournament"]
[Site "?"]
[Date "2026.10.03"]
[Round "1"]
[White "tm"]
[Black "sf"]
[Result "0-1"]
[SetUp "1"]
[FEN "r1bqk2r/1pp1bppp/p1n1pn2/3p4/2PP4/1PNBPN2/P4PPP/R1BQ1RK1 b kq - 0 8"]

8... b6 {-0.92/25 2.000s} 9. Bb2 {+1.17/19 0.400s} Bb7 {-1.02/16 0.100s}
10. Qe2 {+1.18/16 0.200s} O-O {-0.94/18 0.200s} 11. e4 {+1.12/19 0.500s}
Nb4 {-3.10/16 0.150s} 12. Bb1 {-1.00/15 0.100s} 0-1
"""


def test_fen_black_to_move_pgn(tmp_path: Path):
    pgn_path = tmp_path / "match.pgn"
    pgn_path.write_text(SAMPLE_FEN_PGN, encoding="utf-8")

    results, tm_stats, sf_stats, count = parse_pgn_file(pgn_path)

    assert count == 1
    assert results["sf_wins"] == 1
    assert results["tm_wins"] == 0
    assert results["draws"] == 0

    assert sf_stats.opening.moves == 3
    assert tm_stats.opening.moves == 2
    assert sf_stats.early_mid.moves == 1
    assert tm_stats.early_mid.moves == 2

    assert sf_stats.opening.avg_depth > 15.0
    assert sf_stats.opening.total_time_s == pytest.approx(2.3)

    assert sf_stats.score_drops_200cp == 1
    assert tm_stats.score_drops_200cp == 1


def test_mate_scores_are_excluded_from_centipawn_drop_proxy(tmp_path: Path):
    pgn_path = tmp_path / "mate-score.pgn"
    pgn_path.write_text(
        '[Event "Fastchess"]\n'
        '[White "tm"]\n'
        '[Black "sf"]\n'
        '[Result "1-0"]\n\n'
        "1. e4 {+M2/10 0.1s} e5 {-0.20/10 0.1s} "
        "2. Nf3 {+1.00/10 0.1s} 1-0\n",
        encoding="utf-8",
    )

    _, tm_stats, _, _ = parse_pgn_file(pgn_path)

    assert parse_eval_cp("+M2") is None
    assert parse_eval_cp("-M2") is None
    assert tm_stats.score_drops_200cp == 0


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        ("+9.99", 999.0),
        ("-9.99", -999.0),
        ("+10.00", 1000.0),
        ("-10.00", -1000.0),
        ("+10.01", None),
        ("-10.01", None),
        ("+91.65", None),
        ("-91.65", None),
        ("+M2", None),
        ("-M2", None),
    ],
)
def test_parse_eval_cp_excludes_extreme_non_mate_scores(score, expected):
    assert parse_eval_cp(score) == expected


def test_extreme_eval_is_counted_and_resets_drop_baseline(tmp_path: Path):
    pgn_path = tmp_path / "extreme-score.pgn"
    pgn_path.write_text(
        '[Event "Fastchess"]\n'
        '[White "tm"]\n'
        '[Black "sf"]\n'
        '[Result "1-0"]\n\n'
        "1. e4 {+0.10/10 0.1s} e5 {-0.20/10 0.1s} "
        "2. Nf3 {+91.65/10 0.1s} Nc6 {+0.10/10 0.1s} "
        "3. Bb5 {+2.50/10 0.1s} 1-0\n",
        encoding="utf-8",
    )

    _, tm_stats, _, _ = parse_pgn_file(pgn_path)

    assert tm_stats.excluded_eval_outliers == 1
    assert tm_stats.score_drops_100cp == 0
    assert tm_stats.score_drops_200cp == 0


def test_unverified_score_drops_do_not_drive_tuning_recommendations():
    tm = EngineTelemetry(score_drops_200cp=20)
    sf = EngineTelemetry(score_drops_200cp=1)

    recommendations = generate_recommendations(tm, sf, {})

    assert all("score-change proxy" not in rec for rec in recommendations)


def test_grouping_different_binary_and_settings(tmp_path: Path):
    run_a = tmp_path / "run_a"
    run_a.mkdir()
    meta_a = {
        "engine_sha256": "sha_engine_v1",
        "runner_sha256": "sha_runner_v1",
        "runner_tag": "v1.0",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book_1",
        "engine_options": "tm: opt1",
        "expected_games": 2,
        "completed_games": 2,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }
    (run_a / "meta.json").write_text(json.dumps(meta_a), encoding="utf-8")
    pgn_a = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 2. Nf3 {+0.25/10 0.1s} Nc6 {-0.25/10 0.1s} 1-0

[Event "Fastchess"]
[White "sf"]
[Black "tm"]
[Result "1/2-1/2"]

1. d4 {+0.15/10 0.1s} d5 {-0.15/10 0.1s} 1/2-1/2
"""
    (run_a / "match.pgn").write_text(pgn_a, encoding="utf-8")

    run_b = tmp_path / "run_b"
    run_b.mkdir()
    meta_b = {
        "engine_sha256": "sha_engine_v2",  # Different binary!
        "runner_sha256": "sha_runner_v2",  # Different runner build!
        "runner_tag": "v2.0",
        "tc": "60+0",  # Different TC!
        "threads": 2,
        "hash_mb": 256,
        "concurrency": 1,
        "move_overhead_ms": 60,
        "book": "book_closed",
        "book_sha256": "sha_book_2",
        "engine_options": "tm: opt2",
        "expected_games": 2,
        "completed_games": 2,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }
    (run_b / "meta.json").write_text(json.dumps(meta_b), encoding="utf-8")
    (run_b / "match.pgn").write_text(pgn_a, encoding="utf-8")

    partitions, excluded = analyze_screening_runs([run_a, run_b])

    assert len(excluded) == 0
    assert len(partitions) == 2

    keys = list(partitions.keys())
    assert any(
        k.engine_sha256 == "sha_engine_v1"
        and k.runner_sha256 == "sha_runner_v1"
        and k.tc == "10+0.1"
        for k in keys
    )
    assert any(
        k.engine_sha256 == "sha_engine_v2"
        and k.runner_sha256 == "sha_runner_v2"
        and k.tc == "60+0"
        for k in keys
    )


def test_failed_and_incomplete_runs_excluded(tmp_path: Path):
    pgn_2_games = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0

[Event "Fastchess"]
[White "sf"]
[Black "tm"]
[Result "0-1"]

1. d4 {+0.15/10 0.1s} d5 {-0.15/10 0.1s} 0-1
"""
    base_meta = {
        "engine_sha256": "sha_valid",
        "runner_sha256": "runner_sha_valid",
        "runner_tag": "v1",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book",
        "engine_options": "default",
        "expected_games": 2,
        "completed_games": 2,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }

    # 1. Valid run
    run_valid = tmp_path / "valid"
    run_valid.mkdir()
    (run_valid / "meta.json").write_text(json.dumps(base_meta), encoding="utf-8")
    (run_valid / "match.pgn").write_text(pgn_2_games, encoding="utf-8")

    # 2. Timed out run
    run_timeout = tmp_path / "timeout"
    run_timeout.mkdir()
    meta_to = dict(base_meta, timeout=1, exit_fastchess="timeout (143)")
    (run_timeout / "meta.json").write_text(json.dumps(meta_to), encoding="utf-8")
    (run_timeout / "match.pgn").write_text(pgn_2_games, encoding="utf-8")

    # 3. Checker failed run
    run_chk_fail = tmp_path / "chk_fail"
    run_chk_fail.mkdir()
    meta_chk = dict(base_meta, exit_checker=1)
    (run_chk_fail / "meta.json").write_text(json.dumps(meta_chk), encoding="utf-8")
    (run_chk_fail / "match.pgn").write_text(pgn_2_games, encoding="utf-8")

    # 4. Incomplete run
    run_incomp = tmp_path / "incomplete"
    run_incomp.mkdir()
    meta_inc = dict(base_meta, expected_games=2, completed_games=2)
    (run_incomp / "meta.json").write_text(json.dumps(meta_inc), encoding="utf-8")
    (run_incomp / "match.pgn").write_text(
        """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0
""",
        encoding="utf-8",
    )

    partitions, excluded = analyze_screening_runs(
        [run_valid, run_timeout, run_chk_fail, run_incomp]
    )

    assert len(partitions) == 1
    p = next(iter(partitions.values()))
    assert len(p["source_runs"]) == 1
    assert p["source_runs"][0] == str(run_valid)
    assert p["results"]["total_games"] == 2

    assert len(excluded) == 3
    excluded_dirs = {Path(e.rundir).name for e in excluded}
    assert excluded_dirs == {"timeout", "chk_fail", "incomplete"}


def test_exclude_runs_with_failed_tee_or_time_profile(tmp_path: Path):
    pgn = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0
"""
    base_meta = {
        "engine_sha256": "sha_valid",
        "runner_sha256": "runner_sha_valid",
        "runner_tag": "v1",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book",
        "engine_options": "default",
        "expected_games": 1,
        "completed_games": 1,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 1,  # FAILED
        "exit_tee": 0,
    }

    run_tp_fail = tmp_path / "tp_fail"
    run_tp_fail.mkdir()
    (run_tp_fail / "meta.json").write_text(json.dumps(base_meta), encoding="utf-8")
    (run_tp_fail / "match.pgn").write_text(pgn, encoding="utf-8")

    run_tee_fail = tmp_path / "tee_fail"
    run_tee_fail.mkdir()
    meta_tee = dict(base_meta, exit_time_profile=0, exit_tee=1)  # FAILED TEE
    (run_tee_fail / "meta.json").write_text(json.dumps(meta_tee), encoding="utf-8")
    (run_tee_fail / "match.pgn").write_text(pgn, encoding="utf-8")

    partitions, excluded = analyze_screening_runs([run_tp_fail, run_tee_fail])
    assert len(partitions) == 0
    assert len(excluded) == 2
    assert any("Time profile failed" in e.reason for e in excluded)
    assert any("Tee output failed" in e.reason for e in excluded)


def test_exclude_pgn_with_unfinished_games_or_invalid_engines(tmp_path: Path):
    pgn_unfinished = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "*"]

1. e4 e5 *
"""
    pgn_invalid_engine = """[Event "Fastchess"]
[White "alice"]
[Black "bob"]
[Result "1-0"]

1. e4 e5 1-0
"""
    base_meta = {
        "engine_sha256": "sha_valid",
        "runner_sha256": "runner_sha_valid",
        "runner_tag": "v1",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book",
        "engine_options": "default",
        "expected_games": 1,
        "completed_games": 1,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }

    run_unfin = tmp_path / "unfinished"
    run_unfin.mkdir()
    (run_unfin / "meta.json").write_text(json.dumps(base_meta), encoding="utf-8")
    (run_unfin / "match.pgn").write_text(pgn_unfinished, encoding="utf-8")

    run_inv_eng = tmp_path / "invalid_eng"
    run_inv_eng.mkdir()
    (run_inv_eng / "meta.json").write_text(json.dumps(base_meta), encoding="utf-8")
    (run_inv_eng / "match.pgn").write_text(pgn_invalid_engine, encoding="utf-8")

    partitions, excluded = analyze_screening_runs([run_unfin, run_inv_eng])
    assert len(partitions) == 0
    assert len(excluded) == 2
    assert any("Unfinished or invalid game result" in e.reason for e in excluded)
    assert any("Invalid engine labels" in e.reason for e in excluded)


def test_missing_identity_metadata_excluded(tmp_path: Path):
    pgn = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0
"""
    # Missing engine_sha256
    run_no_sha = tmp_path / "no_sha"
    run_no_sha.mkdir()
    meta = {
        "engine_sha256": "",
        "runner_sha256": "runner_sha_valid",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book",
        "expected_games": 1,
        "completed_games": 1,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }
    (run_no_sha / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (run_no_sha / "match.pgn").write_text(pgn, encoding="utf-8")

    partitions, excluded = analyze_screening_runs([run_no_sha])
    assert len(partitions) == 0
    assert len(excluded) == 1
    assert "Missing immutable engine SHA" in excluded[0].reason


def test_exclude_runs_missing_completed_count_or_comparison_settings(tmp_path: Path):
    pgn = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0
"""
    base_meta = {
        "engine_sha256": "sha_engine",
        "runner_sha256": "sha_runner",
        "runner_tag": "v1",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book",
        "engine_options": "YoulossTM=true",
        "expected_games": 1,
        "completed_games": 1,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }

    run_missing_count = tmp_path / "missing_count"
    run_missing_count.mkdir()
    (run_missing_count / "meta.json").write_text(
        json.dumps(dict(base_meta, completed_games=None)), encoding="utf-8"
    )
    (run_missing_count / "match.pgn").write_text(pgn, encoding="utf-8")

    run_missing_settings = tmp_path / "missing_settings"
    run_missing_settings.mkdir()
    meta_no_hash = dict(base_meta)
    meta_no_hash.pop("hash_mb")
    (run_missing_settings / "meta.json").write_text(
        json.dumps(meta_no_hash), encoding="utf-8"
    )
    (run_missing_settings / "match.pgn").write_text(pgn, encoding="utf-8")

    partitions, excluded = analyze_screening_runs(
        [run_missing_count, run_missing_settings]
    )

    assert not partitions
    assert len(excluded) == 2
    reasons = {Path(item.rundir).name: item.reason for item in excluded}
    assert "completed_games" in reasons["missing_count"]
    assert "hash_mb" in reasons["missing_settings"]


@pytest.mark.parametrize(
    ("tc", "overhead_ms", "is_valid"),
    [
        ("60+0", 1500, False),
        ("10+0", 1500, False),
        ("1500+0", 1500, True),
        ("60+0", 60, True),
    ],
)
def test_overhead_policy_excludes_unfair_time_control_runs(
    tmp_path: Path, tc: str, overhead_ms: int, is_valid: bool
):
    run = tmp_path / f"{tc.replace('+', '_')}_{overhead_ms}"
    run.mkdir()
    metadata = {
        "engine_sha256": "sha_engine",
        "runner_sha256": "sha_runner",
        "runner_tag": "v1",
        "tc": tc,
        "threads": 8,
        "hash_mb": 512,
        "concurrency": 1,
        "move_overhead_ms": overhead_ms,
        "book": "book_uho",
        "book_sha256": "sha_book",
        "engine_options": "YoulossTM=true",
        "expected_games": 1,
        "completed_games": 1,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }
    pgn = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0
"""
    (run / "meta.json").write_text(json.dumps(metadata), encoding="utf-8")
    (run / "match.pgn").write_text(pgn, encoding="utf-8")

    partitions, excluded = analyze_screening_runs([run])

    if is_valid:
        assert len(partitions) == 1
        assert not excluded
    else:
        assert not partitions
        assert len(excluded) == 1
        assert (
            "Move Overhead exceeds the 10% initial-budget policy" in excluded[0].reason
        )


def test_analyzer_partitions_by_baseline_sha(tmp_path: Path):
    pgn = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0
"""
    base_meta = {
        "engine_sha256": "sha_youloss_v1",
        "runner_sha256": "sha_runner_v1",
        "runner_tag": "v1.8.2-alpha",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book",
        "expected_games": 1,
        "completed_games": 1,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }

    # Run A: baseline SF 19
    run_a = tmp_path / "run_sf19_a"
    run_a.mkdir()
    meta_a = dict(
        base_meta,
        sf_engine_sha256="sha_stockfish_19",
        sf_engine_label="stockfish-19",
        engine_options="tm: YoulossTM=true; sf: external:stockfish-19; each: Threads=1 Hash=128 Move Overhead=10ms",
    )
    (run_a / "meta.json").write_text(json.dumps(meta_a), encoding="utf-8")
    (run_a / "match.pgn").write_text(pgn, encoding="utf-8")

    # Run B: baseline SF 18 (same Youloss binary, different baseline binary)
    run_b = tmp_path / "run_sf18"
    run_b.mkdir()
    meta_b = dict(
        base_meta,
        sf_engine_sha256="sha_stockfish_18",
        sf_engine_label="stockfish-18",
        engine_options="tm: YoulossTM=true; sf: external:stockfish-18; each: Threads=1 Hash=128 Move Overhead=10ms",
    )
    (run_b / "meta.json").write_text(json.dumps(meta_b), encoding="utf-8")
    (run_b / "match.pgn").write_text(pgn, encoding="utf-8")

    # Run C: baseline SF 19 second batch (should partition with Run A)
    run_c = tmp_path / "run_sf19_b"
    run_c.mkdir()
    meta_c = dict(
        base_meta,
        sf_engine_sha256="sha_stockfish_19",
        sf_engine_label="stockfish-19",
        engine_options="tm: YoulossTM=true; sf: external:stockfish-19; each: Threads=1 Hash=128 Move Overhead=10ms",
    )
    (run_c / "meta.json").write_text(json.dumps(meta_c), encoding="utf-8")
    (run_c / "match.pgn").write_text(pgn, encoding="utf-8")

    partitions, excluded = analyze_screening_runs([run_a, run_b, run_c])
    assert not excluded
    assert len(partitions) == 2

    keys = list(partitions.keys())
    part_sf19 = next(k for k in keys if k.sf_engine_sha256 == "sha_stockfish_19")
    part_sf18 = next(k for k in keys if k.sf_engine_sha256 == "sha_stockfish_18")

    assert len(partitions[part_sf19]["source_runs"]) == 2
    assert sorted(partitions[part_sf19]["source_runs"]) == sorted(
        [str(run_a), str(run_c)]
    )
    assert partitions[part_sf19]["results"]["total_games"] == 2

    assert len(partitions[part_sf18]["source_runs"]) == 1
    assert partitions[part_sf18]["source_runs"] == [str(run_b)]
    assert partitions[part_sf18]["results"]["total_games"] == 1


def test_legacy_metadata_without_baseline_sha_interpreted_as_same_binary_ab(
    tmp_path: Path,
):
    pgn = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0
"""
    # Legacy run without sf_engine_sha256 key
    run_legacy = tmp_path / "legacy_run"
    run_legacy.mkdir()
    meta_legacy = {
        "engine_sha256": "sha_youloss_v1",
        "runner_sha256": "sha_runner_v1",
        "runner_tag": "v1.8.2-alpha",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book",
        "engine_options": "tm: YoulossTM=true; sf: YoulossTM=false; each: Threads=1 Hash=128 Move Overhead=10ms",
        "expected_games": 1,
        "completed_games": 1,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }
    (run_legacy / "meta.json").write_text(json.dumps(meta_legacy), encoding="utf-8")
    (run_legacy / "match.pgn").write_text(pgn, encoding="utf-8")

    # Modern same-binary run with explicit sf_engine_sha256 matching engine_sha256
    run_modern = tmp_path / "modern_run"
    run_modern.mkdir()
    meta_modern = dict(
        meta_legacy,
        sf_engine_sha256="sha_youloss_v1",
        sf_engine_label="YoulossTM-off",
        sf_engine_options="YoulossTM=false",
    )
    (run_modern / "meta.json").write_text(json.dumps(meta_modern), encoding="utf-8")
    (run_modern / "match.pgn").write_text(pgn, encoding="utf-8")

    partitions, excluded = analyze_screening_runs([run_legacy, run_modern])
    assert not excluded
    assert len(partitions) == 1

    key = next(iter(partitions.keys()))
    assert key.engine_sha256 == "sha_youloss_v1"
    assert key.sf_engine_sha256 == "sha_youloss_v1"
    assert len(partitions[key]["source_runs"]) == 2
    assert sorted(partitions[key]["source_runs"]) == sorted(
        [str(run_legacy), str(run_modern)]
    )


def test_invalid_or_missing_explicit_baseline_sha_excluded(tmp_path: Path):
    pgn = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0
"""
    base_meta = {
        "engine_sha256": "sha_youloss_v1",
        "runner_sha256": "sha_runner_v1",
        "runner_tag": "v1.8.2-alpha",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book",
        "engine_options": "default",
        "expected_games": 1,
        "completed_games": 1,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }

    run_empty = tmp_path / "empty_sf_sha"
    run_empty.mkdir()
    (run_empty / "meta.json").write_text(
        json.dumps(dict(base_meta, sf_engine_sha256="")), encoding="utf-8"
    )
    (run_empty / "match.pgn").write_text(pgn, encoding="utf-8")

    run_unknown = tmp_path / "unknown_sf_sha"
    run_unknown.mkdir()
    (run_unknown / "meta.json").write_text(
        json.dumps(dict(base_meta, sf_engine_sha256="unknown")), encoding="utf-8"
    )
    (run_unknown / "match.pgn").write_text(pgn, encoding="utf-8")

    run_none = tmp_path / "none_sf_sha"
    run_none.mkdir()
    (run_none / "meta.json").write_text(
        json.dumps(dict(base_meta, sf_engine_sha256=None)), encoding="utf-8"
    )
    (run_none / "match.pgn").write_text(pgn, encoding="utf-8")

    partitions, excluded = analyze_screening_runs([run_empty, run_unknown, run_none])
    assert not partitions
    assert len(excluded) == 3
    for exc in excluded:
        assert "Missing immutable baseline engine SHA (sf_engine_sha256)" in exc.reason


def test_scoreboard_analyzes_exact_session_runs_and_excludes_unrelated_historical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
):
    base_meta = {
        "engine_sha256": "sha_engine_v1",
        "sf_engine_sha256": "sha_sf_v1",
        "runner_sha256": "sha_runner_v1",
        "runner_tag": "v1.8.2-alpha",
        "tc": "10+0.1",
        "threads": 1,
        "hash_mb": 128,
        "concurrency": 1,
        "move_overhead_ms": 10,
        "book": "book_uho",
        "book_sha256": "sha_book_1",
        "engine_options": "default",
        "expected_games": 1,
        "completed_games": 1,
        "timeout": 0,
        "exit_fastchess": 0,
        "exit_checker": 0,
        "exit_time_profile": 0,
        "exit_tee": 0,
    }
    pgn = """[Event "Fastchess"]
[White "tm"]
[Black "sf"]
[Result "1-0"]

1. e4 {+0.20/10 0.1s} e5 {-0.20/10 0.1s} 1-0
"""
    runs_dir = tmp_path / "sprt"
    runs_dir.mkdir()

    # Two session runs
    run_s1 = runs_dir / "run_s1"
    run_s1.mkdir()
    (run_s1 / "meta.json").write_text(json.dumps(base_meta), encoding="utf-8")
    (run_s1 / "match.pgn").write_text(pgn, encoding="utf-8")

    run_s2 = runs_dir / "run_s2"
    run_s2.mkdir()
    (run_s2 / "meta.json").write_text(json.dumps(base_meta), encoding="utf-8")
    (run_s2 / "match.pgn").write_text(pgn, encoding="utf-8")

    # Unrelated historical run in the same sprt tree
    run_unrelated = runs_dir / "run_historical_unrelated"
    run_unrelated.mkdir()
    (run_unrelated / "meta.json").write_text(json.dumps(base_meta), encoding="utf-8")
    (run_unrelated / "match.pgn").write_text(pgn, encoding="utf-8")

    session_dir = tmp_path / "session_output"
    session_dir.mkdir()
    scoreboard_file = session_dir / "scoreboard.json"
    scoreboard_data = {
        "recent_batches": [
            {"rundir": str(run_s1)},
            {"rundir": str(run_s2)},
        ]
    }
    scoreboard_file.write_text(json.dumps(scoreboard_data), encoding="utf-8")

    # Direct function test: only the 2 session runs returned
    selected_dirs = load_scoreboard_run_dirs(scoreboard_file)
    assert len(selected_dirs) == 2
    assert run_s1 in selected_dirs
    assert run_s2 in selected_dirs
    assert run_unrelated not in selected_dirs

    # CLI test: --scoreboard writes output for exactly the 2 runs
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "analyze_screening.py",
            "--scoreboard",
            str(scoreboard_file),
            "--output-dir",
            str(session_dir),
        ],
    )
    rc = main()
    assert rc == 0
    captured = capsys.readouterr()
    assert "Analyzed 2 runs (1 valid partition(s), 0 excluded)" in captured.out

    diag = json.loads((session_dir / "diagnostics.json").read_text(encoding="utf-8"))
    assert diag["total_runs_inspected"] == 2
    assert diag["excluded_runs_count"] == 0
    partition = diag["partitions"][0]
    assert sorted(partition["source_runs"]) == sorted([str(run_s1), str(run_s2)])
    assert str(run_unrelated) not in partition["source_runs"]
    assert partition["paired_results"]["paired_openings"] == 0
    assert partition["paired_results"]["score"] is None
    assert "Paired-color score" in (session_dir / "tuning_insights.md").read_text(
        encoding="utf-8"
    )


def test_scoreboard_missing_and_invalid_runs_fail_clearly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
):
    valid_run = tmp_path / "valid_run"
    valid_run.mkdir()
    (valid_run / "meta.json").write_text(
        json.dumps({"exit_fastchess": 0}), encoding="utf-8"
    )

    missing_run = tmp_path / "does_not_exist_run"

    # Case 1: Run directory does not exist
    sb_missing_run = tmp_path / "sb_missing_run.json"
    sb_missing_run.write_text(
        json.dumps({"recent_batches": [{"rundir": str(missing_run)}]}),
        encoding="utf-8",
    )
    with pytest.raises(FileNotFoundError, match="does not exist"):
        load_scoreboard_run_dirs(sb_missing_run)

    monkeypatch.setattr(
        sys, "argv", ["analyze_screening.py", "--scoreboard", str(sb_missing_run)]
    )
    assert main() == 1
    err = capsys.readouterr().err
    assert "Error: Run directory listed in scoreboard does not exist" in err

    # Case 2: Run directory missing meta.json
    invalid_run = tmp_path / "invalid_run_no_meta"
    invalid_run.mkdir()
    sb_invalid_run = tmp_path / "sb_invalid_run.json"
    sb_invalid_run.write_text(
        json.dumps({"recent_batches": [{"rundir": str(invalid_run)}]}),
        encoding="utf-8",
    )
    with pytest.raises(FileNotFoundError, match="missing meta.json"):
        load_scoreboard_run_dirs(sb_invalid_run)

    monkeypatch.setattr(
        sys, "argv", ["analyze_screening.py", "--scoreboard", str(sb_invalid_run)]
    )
    assert main() == 1
    assert "missing meta.json" in capsys.readouterr().err

    # Case 3: Scoreboard file itself does not exist
    with pytest.raises(FileNotFoundError, match="does not exist"):
        load_scoreboard_run_dirs(tmp_path / "nonexistent_sb.json")

    # Case 4: Scoreboard has malformed JSON
    malformed_sb = tmp_path / "malformed.json"
    malformed_sb.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed scoreboard JSON"):
        load_scoreboard_run_dirs(malformed_sb)

    # Case 5: Scoreboard has empty batches
    empty_sb = tmp_path / "empty_sb.json"
    empty_sb.write_text(json.dumps({"recent_batches": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="zero completed runs"):
        load_scoreboard_run_dirs(empty_sb)


def test_paired_scores_require_same_round_fen_and_color_swap(tmp_path: Path):
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    other_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"

    def game(round_no: int, white: str, result: str, start_fen: str) -> str:
        return (
            '[Event "Fastchess"]\n'
            f'[Round "{round_no}"]\n'
            f'[White "{white}"]\n'
            f'[Black "{"sf" if white == "tm" else "tm"}"]\n'
            f'[Result "{result}"]\n'
            '[SetUp "1"]\n'
            f'[FEN "{start_fen}"]\n\n'
            "1. e4 {+0.20/10 0.1s} 1-0\n\n"
        )

    pgn_path = tmp_path / "match.pgn"
    pgn_path.write_text(
        game(1, "tm", "1-0", fen)
        + game(1, "sf", "1/2-1/2", fen)
        + game(2, "tm", "1-0", fen)
        + game(2, "tm", "0-1", fen)
        + game(3, "tm", "1-0", fen)
        + game(3, "sf", "0-1", other_fen),
        encoding="utf-8",
    )

    paired_scores, unpaired_games = parse_paired_scores(pgn_path)

    assert paired_scores == [0.75]
    assert unpaired_games == 4


def test_paired_student_t_critical_values():
    assert _student_t_critical_975(29) == pytest.approx(2.0452296, abs=1e-6)
    assert _student_t_critical_975(49) == pytest.approx(2.0095752, abs=1e-6)
    assert _student_t_critical_975(99) == pytest.approx(1.9842170, abs=1e-6)


def test_paired_score_summary_reports_student_t_interval_and_small_sample_limit():
    scores = [0.75] * 50 + [0.25] * 50
    summary = summarize_paired_scores(scores, unpaired_games=3)

    assert summary["paired_openings"] == 100
    assert summary["paired_games"] == 200
    assert summary["unpaired_games"] == 3
    assert summary["score"] == pytest.approx(0.5)
    assert summary["ci95_low"] == pytest.approx(0.450145, abs=0.00001)
    assert summary["ci95_high"] == pytest.approx(0.549855, abs=0.00001)
    assert "paired Student-t CI" in summary["method"]
    assert "df=n-1" in summary["method"]

    too_small = summarize_paired_scores([0.5], unpaired_games=0)
    assert too_small["score"] == pytest.approx(0.5)
    assert too_small["ci95_low"] is None
    assert too_small["ci95_high"] is None

    small_identical_sample = summarize_paired_scores([0.5, 0.5], unpaired_games=0)
    assert small_identical_sample["score"] == pytest.approx(0.5)
    assert small_identical_sample["ci95_low"] is None
    assert small_identical_sample["ci95_high"] is None

    zero_variance_sample = summarize_paired_scores([0.5] * 30, unpaired_games=0)
    assert zero_variance_sample["ci95_low"] is None
    assert zero_variance_sample["ci95_high"] is None


def test_cli_sprt_dir_standalone_and_conflict_handling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
):
    sb_path = tmp_path / "sb.json"
    sb_path.write_text("{}", encoding="utf-8")

    # Specifying both --scoreboard and --sprt-dir fails
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "analyze_screening.py",
            "--scoreboard",
            str(sb_path),
            "--sprt-dir",
            str(tmp_path),
        ],
    )
    assert main() == 1
    assert "Cannot specify both --scoreboard and --sprt-dir" in capsys.readouterr().err

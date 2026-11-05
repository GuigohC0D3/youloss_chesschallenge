import chess

from scripts.vet_opening_book import collect_tree


def test_tree_has_one_entry_per_position():
    tree = collect_tree()
    epds = [board.epd() for board, _ in tree.values()]
    assert len(epds) == len(set(epds))


def test_keys_rebuild_a_board_with_the_same_polyglot_key():
    for key, (board, _) in collect_tree().items():
        rebuilt = chess.Board(f"{key} 0 1")
        assert chess.polyglot.zobrist_hash(rebuilt) == chess.polyglot.zobrist_hash(board)

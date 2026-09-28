"""Engine UCI falso para testes. Modo via argv[1]:
ok | hang | crash | spam | slow (só responde ao stop) | deaf (ignora go/stop) | dieongo."""
import sys
import time

import chess

mode = sys.argv[1] if len(sys.argv) > 1 else "ok"
board = chess.Board()


def set_position(tokens: list[str]) -> None:
    global board
    if tokens[1] == "startpos":
        board, rest = chess.Board(), tokens[2:]
    else:  # position fen <6 campos> [moves ...]
        board, rest = chess.Board(" ".join(tokens[2:8])), tokens[8:]
    if rest and rest[0] == "moves":
        for uci in rest[1:]:
            board.push_uci(uci)


def answer_bestmove() -> None:
    moves = sorted(m.uci() for m in board.legal_moves)
    if not moves:
        print("bestmove (none)")
        return
    print(f"info depth 5 seldepth 7 multipv 1 score cp 12 nodes 1234 nps 1000 time 1 pv {moves[0]}")
    print(f"bestmove {moves[0]}")


for line in sys.stdin:
    cmd = line.strip()
    if mode == "crash":
        sys.exit(3)
    if mode == "spam" and cmd.startswith("go"):
        while True:
            print("info depth 1 score cp 0 pv e2e4", flush=True)
            time.sleep(0.05)
    if mode == "hang":
        continue
    if cmd == "uci":
        print("id name FakeFish 1.0")
        print("id author Youloss")
        print("option name Hash type spin default 16 min 1 max 1024")
        print("uciok")
    elif cmd == "isready":
        print("readyok")
    elif cmd.startswith("position"):
        set_position(cmd.split())
    elif cmd.startswith("go"):
        if mode == "dieongo":
            sys.exit(4)
        if mode not in ("slow", "deaf"):
            answer_bestmove()
    elif cmd == "stop" and mode == "slow":
        answer_bestmove()
    elif cmd == "quit":
        break
    sys.stdout.flush()

"""Engine UCI falso para testes. Modo via argv[1]:
ok | hang | crash | spam | slow (só responde ao stop) | deaf (ignora go/stop) | dieongo |
ponder (sugere lance de ponder; `go ponder` espera ponderhit ou stop) |
jump (mate depois de ...h6, para o aviso de lance digitado)."""
import sys
import time

import chess

mode = sys.argv[1] if len(sys.argv) > 1 else "ok"
board = chess.Board()
pondering = False
ponderhits = 0


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
    score = "cp 12"
    if mode == "jump" and board.move_stack and board.peek().uci() == "h7h6":
        score = "mate 3"  # simula o adversário (ou a digitação) entregando a partida
    print(f"info depth 5 seldepth 7 multipv 1 score {score} nodes 1234 nps 1000 time 1 pv {moves[0]}")
    if mode == "ponder":
        board.push_uci(moves[0])
        replies = sorted(m.uci() for m in board.legal_moves)
        board.pop()
        if replies:
            print(f"bestmove {moves[0]} ponder {replies[0]}")
            return
    print(f"bestmove {moves[0]}")


for line in sys.stdin:
    cmd = line.strip()
    if mode == "crash":
        sys.exit(3)
    if mode == "crash_with_stderr":
        sys.stderr.write("fatal: corrupted hash table\n")
        sys.stderr.flush()
        sys.exit(5)
    if mode == "spam" and cmd.startswith("go"):
        while True:
            print("info depth 1 score cp 0 pv e2e4", flush=True)
            time.sleep(0.05)
    if mode == "hang":
        continue
    if cmd == "uci":
        if mode == "control_chars":
            sys.stderr.write("\x1b[31merror with ansi\x1b[0m\x00\x07\r\nclean line\n")
            sys.stderr.flush()
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
        if mode == "dieongo_with_stderr":
            sys.stderr.write("critical: assertion failed in search.cpp:42\n")
            sys.stderr.flush()
            sys.exit(4)
        if mode == "stderr_flood":
            for i in range(2000):
                sys.stderr.write(f"flood line {i}: " + "x" * 80 + "\n")
            sys.stderr.flush()
        if mode == "stderr_giant_no_newline":
            sys.stderr.write("x" * (1024 * 1024))
            sys.stderr.flush()
        if mode == "ponder" and " ponder" in cmd:
            pondering = True
        elif mode not in ("slow", "deaf"):
            answer_bestmove()
    elif cmd == "stop" and mode == "slow":
        answer_bestmove()
    elif cmd in ("stop", "ponderhit") and mode == "ponder" and pondering:
        pondering = False
        ponderhits += cmd == "ponderhit"
        print(f"info string ponderhits {ponderhits}")
        answer_bestmove()
    elif cmd == "quit":
        break
    sys.stdout.flush()

"""Engine UCI falso para testes. Modo via argv[1]: ok | hang | crash."""
import sys

mode = sys.argv[1] if len(sys.argv) > 1 else "ok"
for line in sys.stdin:
    cmd = line.strip()
    if mode == "crash":
        sys.exit(3)
    if mode == "hang":
        continue
    if cmd == "uci":
        print("id name FakeFish 1.0")
        print("id author Youloss")
        print("option name Hash type spin default 16 min 1 max 1024")
        print("uciok")
    elif cmd == "isready":
        print("readyok")
    elif cmd == "quit":
        break
    sys.stdout.flush()

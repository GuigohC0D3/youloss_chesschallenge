#!/usr/bin/env python3
"""Build an offline tournament opening book (assets/book.bin) in Polyglot format.

Covers grandmaster-grade sound openings for White and Black up to ply 8-12.
Sorted strictly by Polyglot Zobrist hash key for standard binary search.
"""

from __future__ import annotations

from pathlib import Path
import struct
import sys

import chess
import chess.polyglot

ROOT = Path(__file__).resolve().parents[1]
BOOK_PATH = ROOT / "assets" / "book.bin"

# Standard master-level opening lines (SAN move sequences)
OPENING_LINES = [
    # --- 1. e4: Open Game (1... e5) ---
    # Ruy Lopez (Main Closed)
    "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3 Nb8 d4 Nbd7",
    "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3 Na5 Bc2 c5 d4 Qc7",
    # Ruy Lopez (Berlin Defense)
    "e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Nxe4 d4 Nd6 Bxc6 dxc6 dxe5 Nf5 Qxd8+ Kxd8 Nc3 Ke8",
    # Ruy Lopez (Open)
    "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Nxe4 d4 b5 Bb3 d5 dxe5 Be6 c3 Be7",
    # Italian Game (Giuoco Piano & Two Knights)
    "e4 e5 Nf3 Nc6 Bc4 Bc5 c3 Nf6 d3 d6 O-O O-O Re1 a5 Bb3 h6 Nbd2 Be6",
    "e4 e5 Nf3 Nc6 Bc4 Bc5 O-O Nf6 d3 O-O c3 d6 a4 a5 h3 Be6 Bxe6 fxe6",
    "e4 e5 Nf3 Nc6 Bc4 Nf6 d3 Bc5 c3 O-O O-O d6 a4 a6 Re1 Ba7 Nbd2",
    "e4 e5 Nf3 Nc6 Bc4 Nf6 d4 exd4 O-O Nxe4 Re1 d5 Bxd5 Qxd5 Nc3 Qa5 Nxe4 Be6",
    # Scotch Game
    "e4 e5 Nf3 Nc6 d4 exd4 Nxd4 Nf6 Nxc6 bxc6 e5 Qe7 Qe2 Nd5 c4 Ba6 b3 g6",
    # Petrov Defense
    "e4 e5 Nf3 Nf6 Nxe5 d6 Nf3 Nxe4 d4 d5 Bd3 Be7 O-O Nc6 c4 Nb4 Be2 O-O",
    "e4 e5 Nf3 Nf6 Nxe5 d6 Nf3 Nxe4 Nc3 Nxc3 dxc3 Be7 Be3 O-O Qd2 Nd7 O-O-O",

    # --- 1. e4: Sicilian Defense (1... c5) ---
    # Najdorf
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 Be3 e5 Nb3 Be6 f3 Nbd7 Qd2 b5 O-O-O Be7",
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 Bg5 e6 f4 Be7 Qf3 Qc7 O-O-O Nbd7 Bd3 b5",
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 Be2 e5 Nb3 Be7 O-O O-O Be3 Be6 Qd2",
    # Sveshnikov
    "e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 Nf6 Nc3 e5 Ndb5 d6 Bg5 a6 Na3 b5 Nd5 Be7 Bxf6 Bxf6 c3",
    # Classical / Richter-Rauzer
    "e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 Nf6 Nc3 d6 Bg5 e6 Qd2 a6 O-O-O Bd7 f4 Be7",
    # Dragon
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 g6 Be3 Bg7 f3 O-O Qd2 Nc6 Bc4 Bd7 O-O-O Rc8 Bb3",
    # Kan & Taimanov
    "e4 c5 Nf3 e6 d4 cxd4 Nxd4 a6 Nc3 Qc7 Bd3 Nf6 O-O Bc5 Nb3 Be7 f4 d6",
    "e4 c5 Nf3 e6 d4 cxd4 Nxd4 Nc6 Nc3 Qc7 Be2 a6 O-O Nf6 Be3 Be7 f4 d6",
    # Alapin (2. c3)
    "e4 c5 c3 d5 exd5 Qxd5 d4 Nf6 Nf3 e6 Be2 Nc6 O-O cxd4 cxd4 Be7 Nc3 Qd6",
    "e4 c5 c3 Nf6 e5 Nd5 d4 cxd4 Nf3 Nc6 cxd4 d6 Bc4 Nb6 Bb5 dxe5 Nxe5 Bd7",
    # Closed Sicilian
    "e4 c5 Nc3 Nc6 g3 g6 Bg2 Bg7 d3 d6 Be3 e5 Qd2 Nge7 Bh6 O-O h4 f6",

    # --- 1. e4: French Defense (1... e6) ---
    # Classical / Steinitz
    "e4 e6 d4 d5 Nc3 Nf6 e5 Nfd7 f4 c5 Nf3 Nc6 Be3 a6 Qd2 b5 a3 Qb6",
    # Winawer
    "e4 e6 d4 d5 Nc3 Bb4 e5 c5 a3 Bxc3+ bxc3 Ne7 Qg4 O-O Bd3 Nbc6 Qh5 Ng6",
    # Tarrasch
    "e4 e6 d4 d5 Nd2 c5 exd5 Qxd5 Ngf3 cxd4 Bc4 Qd6 O-O Nf6 Nb3 Nc6 Nbxd4 Nxd4 Nxd4 a6",
    # Advance
    "e4 e6 d4 d5 e5 c5 c3 Nc6 Nf3 Qb6 a3 Nh6 b4 cxd4 cxd4 Nf5 Bb2 Bd7",

    # --- 1. e4: Caro-Kann Defense (1... c6) ---
    # Classical (4... Bf5)
    "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Bf5 Ng3 Bg6 h4 h6 Nf3 Nd7 h5 Bh7 Bd3 Bxd3 Qxd3 e6",
    # Advance (3. e5)
    "e4 c6 d4 d5 e5 Bf5 Nf3 e6 Be2 c5 Be3 Qb6 Nc3 Nc6 O-O Qxb2 Qe1 cxd4 Nxd4",
    # Two Knights
    "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Nf6 Nxf6+ exf6 c3 Bd6 Bd3 O-O Qc2 Re8+ Ne2",
    # Panov-Botvinnik
    "e4 c6 d4 d5 exd5 cxd5 c4 Nf6 Nc3 Nc6 Nf3 Bg4 cxd5 Nxd5 Qb3 Bxf3 gxf3 e6",

    # --- 1. e4: Other Defenses ---
    # Pirc / Modern
    "e4 d6 d4 Nf6 Nc3 g6 Nf3 Bg7 Be2 O-O O-O c6 a4 Nbd7 h3 e5 Be3",
    "e4 g6 d4 Bg7 Nf3 d6 Bc4 Nf6 Qe2 O-O O-O c6 Bb3 Bg4 Nbd2 Nbd7 h3",
    # Scandinavian
    "e4 d5 exd5 Qxd5 Nc3 Qa5 d4 Nf6 Nf3 Bf5 Bd2 c6 Bc4 e6 Nd5 Qd8 Nxf6+ gxf6",

    # --- 1. d4: Queen's Gambit Declined (1... d5 2. c4 e6) ---
    "d4 d5 c4 e6 Nc3 Nf6 Bg5 Be7 e3 O-O Nf3 h6 Bh4 b6 cxd5 Nxd5 Bxe7 Qxe7 Nxd5 exd5",
    "d4 d5 c4 e6 Nc3 Nf6 cxd5 exd5 Bg5 c6 e3 Be7 Bd3 Nbd7 Qc2 O-O Nge2 Re8 O-O",
    "d4 d5 c4 e6 Nf3 Nf6 Nc3 Be7 Bf4 O-O e3 c5 dxc5 Bxc5 Qc2 Nc6 a3 Qa5",

    # --- 1. d4: Slav Defense (1... d5 2. c4 c6) ---
    "d4 d5 c4 c6 Nf3 Nf6 Nc3 dxc4 a4 Bf5 e3 e6 Bxc4 Bb4 O-O O-O Qe2 Nbd7 e4 Bg6",
    "d4 d5 c4 c6 Nc3 Nf6 e3 e6 Nf3 Nbd7 Qc2 Bd6 Bd3 O-O O-O dxc4 Bxc4 b5 Be2",

    # --- 1. d4: Queen's Gambit Accepted ---
    "d4 d5 c4 dxc4 Nf3 Nf6 e3 e6 Bxc4 c5 O-O a6 Qe2 b5 Bb3 Bb7 Rd1 Nbd7 Nc3",

    # --- 1. d4: London System ---
    "d4 d5 Bf4 Nf6 e3 c5 c3 Nc6 Nd2 Qb6 Qb3 c4 Qc2 g6 e4 dxe4 Bxc4 Bf5 Be3",
    "d4 Nf6 Bf4 g6 e3 Bg7 Nf3 O-O Be2 d6 h3 c5 c3 b6 O-O Bb7 a4 a6 Nbd2",

    # --- 1. d4: King's Indian Defense (1... Nf6 2. c4 g6) ---
    "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6 Nf3 O-O Be2 e5 O-O Nc6 d5 Ne7 Ne1 Nd7 Be3 f5 f3 f4",
    "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6 f3 O-O Be3 c5 Nge2 Nc6 Qd2 Qa5 O-O-O a6 Kb1 b5",

    # --- 1. d4: Grunfeld Defense ---
    "d4 Nf6 c4 g6 Nc3 d5 cxd5 Nxd5 e4 Nxc3 bxc3 Bg7 Nf3 c5 Be3 Qa5 Qd2 O-O Rc1 Rd8",
    "d4 Nf6 c4 g6 Nc3 d5 Nf3 Bg7 Qb3 dxc4 Qxc4 O-O e4 a6 Be2 b5 Qb3 Bb7 e5 Nd5",

    # --- 1. d4: Nimzo-Indian Defense ---
    "d4 Nf6 c4 e6 Nc3 Bb4 Qc2 O-O a3 Bxc3+ Qxc3 b6 Bg5 Bb7 f3 h6 Bh4 d5 e3 Nbd7",
    "d4 Nf6 c4 e6 Nc3 Bb4 e3 O-O Bd3 d5 Nf3 c5 O-O dxc4 Bxc4 Nbd7 Qe2 b6 Rd1",
    "d4 Nf6 c4 e6 Nc3 Bb4 f3 d5 a3 Bxc3+ bxc3 c5 cxd5 Nxd5 dxc5 f5 e4 fxe4",

    # --- 1. d4: Queen's Indian & Bogo-Indian ---
    "d4 Nf6 c4 e6 Nf3 b6 g3 Ba6 b3 Bb4+ Bd2 Be7 Bg2 c6 Bc3 d5 Ne5 Nfd7 Nxd7",
    "d4 Nf6 c4 e6 Nf3 Bb4+ Bd2 Qe7 g3 Nc6 Nc3 Bxc3 Bxc3 Ne4 Rc1 O-O Bg2 d6",

    # --- 1. d4: Benoni & Benko Gambit ---
    "d4 Nf6 c4 c5 d5 e6 Nc3 exd5 cxd5 d6 e4 g6 Nf3 Bg7 Be2 O-O O-O Re8 Nd2 Nbd7",
    "d4 Nf6 c4 c5 d5 b5 cxb5 a6 bxa6 g6 Nc3 Bxa6 g3 d6 Bg2 Bg7 Nf3 Nbd7 O-O",

    # --- 1. c4: English Opening ---
    "c4 e5 Nc3 Nf6 Nf3 Nc6 g3 d5 cxd5 Nxd5 Bg2 Nb6 O-O Be7 a3 O-O b4 Be6",
    "c4 c5 Nc3 Nc6 g3 g6 Bg2 Bg7 Nf3 Nf6 O-O O-O d4 cxd4 Nxd4 Nxd4 Qxd4 d6",
    "c4 Nf6 Nc3 e6 e4 d5 e5 d4 exf6 dxc3 bxc3 Qxf6 d4 b6 Nf3 Bb7 Be2 Bd6",

    # --- 1. Nf3: Reti Opening ---
    "Nf3 d5 g3 Nf6 Bg2 c6 O-O Bf5 c4 e6 cxd5 exd5 d3 Be7 Qb3 Qb6 Be3",
    "Nf3 Nf6 c4 g6 g3 Bg7 Bg2 O-O O-O d6 Nc3 c5 d4 Nc6 dxc5 dxc5 Bf4 Be6",

    # --- EXPANDED DEEP GM REPERTOIRE (PLIES 12-20) ---
# --- 1. e4: Open Game (1... e5) ---
    # Ruy Lopez Mainline Closed
    "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3 Nb8 d4 Nbd7 Nbd2 Bb7 Bc2 Re8 Nf1 Bf8 Ng3 g6 a4 c5 d5 c4 Bg5 h6 Be3 Nc5 Qd2 h5",
    "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3 Na5 Bc2 c5 d4 Qc7 Nbd2 cxd4 cxd4 Bd7 Nf1 Rac8 Bd3 Nc6 d5 Nb4 Bb1 Nc2 Bxc2 Qxc2 Qxc2 Rxc2",
    # Ruy Lopez Marshall Attack
    "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 O-O c3 d5 exd5 Nxd5 Nxe5 Nxe5 Rxe5 c6 d4 Bd6 Re1 Qh4 g3 Qh3 Be3 Bg4 Qd3 Rae8 Nd2 Re6 a4 Qh5",
    # Ruy Lopez Berlin Defense
    "e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Nxe4 d4 Nd6 Bxc6 dxc6 dxe5 Nf5 Qxd8+ Kxd8 Nc3 Ke8 h3 h5 Bf4 Be7 Rad1 Be6 b3 Rd8 Rxd8+ Kxd8 Rd1+ Kc8 Ng5 Bxg5 Bxg5",
    "e4 e5 Nf3 Nc6 Bb5 Nf6 d3 Bc5 Bxc6 dxc6 O-O Nd7 Nbd2 O-O Nc4 Re8 Bd2 f6 Nh4 Nf8 Nf5 Be6",
    # Italian Game Giuoco Pianissimo
    "e4 e5 Nf3 Nc6 Bc4 Bc5 c3 Nf6 d3 d6 O-O a6 Bb3 Ba7 Nbd2 O-O h3 h6 Re1 Re8 Nf1 Be6 Bc2 d5 exd5 Bxd5 Ng3 Qd7",
    "e4 e5 Nf3 Nc6 Bc4 Bc5 O-O Nf6 d3 O-O c3 d6 a4 a5 h3 Be6 Bxe6 fxe6 Nbd2 d5 Qe2 Bd6 Re1 Nh5 Nf1 Nf4 Bxf4 Rxf4",
    # Italian Evans Gambit
    "e4 e5 Nf3 Nc6 Bc4 Bc5 b4 Bxb4 c3 Ba5 d4 d6 Qb3 Qd7 dxe5 Bb6 Nbd2 Na5 Qc2 Nxc4 Nxc4 dxe5 Ncxe5 Qe6",
    # Scotch Game
    "e4 e5 Nf3 Nc6 d4 exd4 Nxd4 Nf6 Nxc6 bxc6 e5 Qe7 Qe2 Nd5 c4 Ba6 b3 g6 g3 Bg7 Bb2 O-O-O Bg2 Rhe8 O-O Bxe5 Qxe5 Qxe5 Bxe5 Rxe5 cxd5 Bxf1 Kxf1 cxd5",
    # Petrov Defense
    "e4 e5 Nf3 Nf6 Nxe5 d6 Nf3 Nxe4 d4 d5 Bd3 Be7 O-O Nc6 c4 Nb4 Be2 O-O Nc3 Bf5 a3 Nxc3 bxc3 Nc6 Re1 Re8 cxd5 Qxd5 Bf4 Rac8",
    "e4 e5 Nf3 Nf6 Nxe5 d6 Nf3 Nxe4 Nc3 Nxc3 dxc3 Be7 Be3 O-O Qd2 Nd7 O-O-O Nf6 Bd3 c5 Bg5 Be6 Kb1 Qa5 a3 b5 Rhe1 b4",

    # --- 1. e4: Sicilian Defense (1... c5) ---
    # Najdorf English Attack
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 Be3 e5 Nb3 Be6 f3 Nbd7 Qd2 b5 O-O-O Be7 g4 b4 Nd5 Bxd5 exd5 Nb6 Na5 Nbxd5 Nc6 Qc7 Nxe7 Nxe3 Qxe3 Kxe7",
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 Be3 e5 Nb3 Be6 f3 h5 Nd5 Bxd5 exd5 Nbd7 Qd2 g6 Be2 Bg7 O-O-O b6 Kb1 Qc7 h4 Nc5 g4 hxg4 fxg4",
    # Najdorf 6. Bg5 Mainline
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 Bg5 e6 f4 Be7 Qf3 Qc7 O-O-O Nbd7 g4 b5 Bxf6 Nxf6 g5 Nd7 f5 Nc5 f6 gxf6 gxf6 Bf8 Rg1 h5",
    # Najdorf 6. Be2 Classical
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 Be2 e5 Nb3 Be7 O-O O-O Be3 Be6 Qd2 Nbd7 a4 Rc8 a5 Qc7 Rfd1 Rfd8 Qe1 Qc6",
    # Sveshnikov
    "e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 Nf6 Nc3 e5 Ndb5 d6 Bg5 a6 Na3 b5 Nd5 Be7 Bxf6 Bxf6 c3 O-O Nc2 Bg5 a4 bxa4 Rxa4 a5 Bc4 Rb8 b3 Kh8 O-O f5 exf5 Bxf5",
    "e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 Nf6 Nc3 e5 Ndb5 d6 Bg5 a6 Na3 b5 Bxf6 gxf6 Nd5 f5 Bd3 Be6 Qh5 Bg7 O-O f4 c4 b4 Nc2 a5 g3 O-O",
    # Classical / Richter-Rauzer
    "e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 Nf6 Nc3 d6 Bg5 e6 Qd2 a6 O-O-O Bd7 f4 Be7 Nf3 b5 Bxf6 gxf6 Kb1 Qb6 f5 O-O-O g3 Kb8 Bh3 Bc8 fxe6 fxe6",
    # Dragon Yugoslav Attack
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 g6 Be3 Bg7 f3 O-O Qd2 Nc6 Bc4 Bd7 O-O-O Rc8 Bb3 Ne5 h4 h5 Bg5 Rc5 Kb1 b5 g4 a5 gxh5 Nxh5",
    # Taimanov & Kan
    "e4 c5 Nf3 e6 d4 cxd4 Nxd4 Nc6 Nc3 Qc7 Be2 a6 O-O Nf6 Be3 Bb4 Na4 Be7 Nxc6 bxc6 Nb6 Rb8 Nxc8 Qxc8 Bd4 O-O Qd3 c5 Be5 Rb6",
    "e4 c5 Nf3 e6 d4 cxd4 Nxd4 a6 Bd3 Bc5 Nb3 Be7 O-O d6 c4 Nf6 Nc3 O-O Be3 b6 f4 Bb7 Qf3 Nbd7 Rae1 Qc7 Qh3 Rfe8 Kh1",
    # Alapin & Rossolimo
    "e4 c5 c3 d5 exd5 Qxd5 d4 Nf6 Nf3 Bg4 Be2 e6 h3 Bh5 O-O Nc6 Be3 cxd4 cxd4 Be7 Nc3 Qd6 Qb3 O-O Rfd1 Rfd8 Rac1 Qb4",
    "e4 c5 Nf3 Nc6 Bb5 g6 Bxc6 dxc6 d3 Bg7 h3 Nf6 Nc3 O-O Be3 b6 Qd2 e5 Bh6 Qd6 Bxg7 Kxg7 O-O-O a5 Ne2",

    # --- 1. e4: French Defense (1... e6) ---
    # Winawer Poisoned Pawn
    "e4 e6 d4 d5 Nc3 Bb4 e5 c5 a3 Bxc3+ bxc3 Ne7 Qg4 Qc7 Qxg7 Rg8 Qxh7 cxd4 Ne2 Nbc6 f4 Bd7 Qd3 dxc3 h4 O-O-O h5 d4 h6 Rg6",
    # Steinitz Boleslavsky
    "e4 e6 d4 d5 Nc3 Nf6 e5 Nfd7 f4 c5 Nf3 Nc6 Be3 a6 Qd2 b5 a3 Qb6 Qf2 cxd4 Nxd4 Bc5 O-O-O O-O Nce2 b4 a4 b3 cxb3 a5",
    # Tarrasch Open & Closed
    "e4 e6 d4 d5 Nd2 c5 exd5 Qxd5 Ngf3 cxd4 Bc4 Qd6 O-O Nf6 Nb3 Nc6 Nbxd4 Nxd4 Nxd4 a6 Re1 Qc7 Bb3 Bd6 Nf5 Bxh2+ Kh1 O-O Nxg7 Kxg7",
    "e4 e6 d4 d5 Nd2 Nf6 e5 Nfd7 Bd3 c5 c3 Nc6 Ne2 cxd4 cxd4 f6 exf6 Nxf6 Nf3 Bd6 O-O Qc7 Bg5 O-O Bh4 Nh5 Qc2 h6 Bh7+ Kh8 Bg6 Rxf3",

    # --- 1. e4: Caro-Kann Defense (1... c6) ---
    # Classical Capablanca
    "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Bf5 Ng3 Bg6 h4 h6 Nf3 Nd7 h5 Bh7 Bd3 Bxd3 Qxd3 e6 Bf4 Ngf6 O-O-O Be7 Kb1 O-O Ne4 Nxe4 Qxe4 Nf6 Qe2 Qd5 Ne5",
    # Advance Tal & Short
    "e4 c6 d4 d5 e5 Bf5 h4 h5 c4 e6 Nc3 Ne7 Nge2 Nd7 Ng3 Bg6 Bg5 Qb6 Qd2 dxc4 Bxc4 Nf5 Nxf5 Bxf5 O-O f6 exf6 gxf6 Be3 O-O-O",
    "e4 c6 d4 d5 e5 Bf5 Nf3 e6 Be2 c5 Be3 Qb6 Nc3 Nc6 O-O Qxb2 Qe1 cxd4 Nxd4 Nxd4 Bxd4 Bb4 Rb1 Qa3 Rb3 Qa5 Qb1 Bxc3 Bxc3",
    # Tartakower (4... Nf6 5. Nxf6+ exf6)
    "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Nf6 Nxf6+ exf6 c3 Bd6 Bd3 O-O Qc2 Re8+ Ne2 h5 O-O h4 h3 Nd7 Be3 Nf8 c4 Be6 Rad1 Rc8",

    # --- 1. d4: Queen's Gambit Declined (1... d5 2. c4 e6) ---
    # Tartakower & Lasker
    "d4 d5 c4 e6 Nc3 Nf6 Bg5 Be7 e3 O-O Nf3 h6 Bh4 b6 cxd5 Nxd5 Bxe7 Qxe7 Nxd5 exd5 Rc1 Be6 Qa4 c5 Qa3 Rc8 Bb5 a6 dxc5 bxc5 O-O Ra7 Be2 a5",
    "d4 d5 c4 e6 Nc3 Nf6 Bg5 Be7 e3 O-O Nf3 h6 Bh4 Ne4 Bxe7 Qxe7 cxd5 Nxc3 bxc3 exd5 Qb3 Rd8 c4 dxc4 Bxc4 Nc6 O-O Na5 Qc3 Nxc4 Qxc4",
    # Exchange Variation
    "d4 d5 c4 e6 Nc3 Nf6 cxd5 exd5 Bg5 c6 e3 Be7 Bd3 Nbd7 Qc2 O-O Nge2 Re8 O-O Nf8 f3 g6 Rad1 Ne6 Bh4 Nh5 Bf2 b6 Kh1 Bb7",

    # --- 1. d4: Slav & Semi-Slav ---
    # Slav Mainline
    "d4 d5 c4 c6 Nf3 Nf6 Nc3 dxc4 a4 Bf5 Ne5 e6 f3 Bb4 e4 Bxe4 fxe4 Nxe4 Bd2 Qxd4 Nxe4 Qxe4+ Qe2 Bxd2+ Kxd2 Qd5+ Kc2 Na6 Nxc4 O-O-O",
    # Semi-Slav Meran
    "d4 d5 c4 c6 Nc3 Nf6 e3 e6 Nf3 Nbd7 Bd3 dxc4 Bxc4 b5 Bd3 a6 e4 c5 d5 c4 Bc2 Qc7 O-O Bb7 dxe6 fxe6 Ng5 Nc5 Qe2 h6 e5 hxg5 Bg6+ Ke7",
    # Semi-Slav Moscow
    "d4 d5 c4 c6 Nf3 Nf6 Nc3 e6 Bg5 h6 Bxf6 Qxf6 e3 Nd7 Bd3 dxc4 Bxc4 g6 O-O Bg7 e4 e5 d5 O-O Qe2 Nb6 Bb3 Bg4",

    # --- 1. d4: King's Indian Defense (1... Nf6 2. c4 g6) ---
    # Classical Mar del Plata
    "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6 Nf3 O-O Be2 e5 O-O Nc6 d5 Ne7 Ne1 Nd7 Be3 f5 f3 f4 Bf2 g5 Nd3 Nf6 c5 Ng6 Rc1 Rf7 cxd6 cxd6 a4 Bf8 Nb5 a6",
    # Bayonet Attack
    "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6 Nf3 O-O Be2 e5 O-O Nc6 d5 Ne7 b4 Nh5 Re1 f5 Ng5 Nf6 Bf3 c6 Bb2 Kh8 Rc1 h6 Ne6 Bxe6 dxe6 fxe4 Nxe4 Nxe4 Bxe4",

    # --- 1. d4: Grunfeld Defense ---
    # Exchange Classical
    "d4 Nf6 c4 g6 Nc3 d5 cxd5 Nxd5 e4 Nxc3 bxc3 Bg7 Bc4 c5 Ne2 O-O O-O Nc6 Be3 Bg4 f3 Na5 Bd3 cxd4 cxd4 Be6 d5 Bxa1 Qxa1 f6 Bh6 Re8 Kh1",
    # Russian System
    "d4 Nf6 c4 g6 Nc3 d5 Nf3 Bg7 Qb3 dxc4 Qxc4 O-O e4 a6 Be2 b5 Qb3 Bb7 e5 Nd5 O-O Nxc3 bxc3 c5 Be3 cxd4 cxd4 Bd5 Qb2 Nc6 Rfc1",

    # --- 1. d4: Nimzo-Indian & Catalan ---
    # Classical & Rubinstein
    "d4 Nf6 c4 e6 Nc3 Bb4 Qc2 O-O a3 Bxc3+ Qxc3 b6 Bg5 Bb7 f3 h6 Bh4 d5 e3 Nbd7 cxd5 Nxd5 Bxd8 Nxc3 Bh4 Nd5 Bf2 c5 e4 Ne7 Ne2 Rac8",
    "d4 Nf6 c4 e6 Nc3 Bb4 e3 O-O Bd3 d5 Nf3 c5 O-O dxc4 Bxc4 Nbd7 Qe2 b6 Rd1 cxd4 exd4 Bb7 d5 Bxc3 dxe6 Bxf3 gxf3 fxe6 bxc3",
    # Open Catalan
    "d4 Nf6 c4 e6 g3 d5 Bg2 Be7 Nf3 O-O O-O dxc4 Qc2 a6 Qxc4 b5 Qc2 Bb7 Bd2 Be4 Qc1 Bb7 Bf4 Bd6 Rd1 Nbd7 Nbd2 Bxf4 gxf4 Rc8 Nb3 Qe7",
    # Closed Catalan
    "d4 Nf6 c4 e6 g3 d5 Bg2 Be7 Nf3 O-O O-O c6 Qc2 Nbd7 Nbd2 b6 e4 Bb7 e5 Ne8 cxd5 cxd5 Re1 Rc8 Qd1 Nc7 Nf1 b5 h4",

    # --- 1. d4: London System ---
    "d4 d5 Bf4 Nf6 e3 c5 c3 Nc6 Nd2 Qb6 Qb3 c4 Qc2 g6 e4 dxe4 Bxc4 Bf5 Be3",
    "d4 Nf6 Bf4 g6 e3 Bg7 Nf3 O-O Be2 d6 h3 c5 c3 b6 O-O Bb7 a4 a6 Nbd2",
    "d4 Nf6 Bf4 c5 e3 Qb6 Nc3 a6 a3 cxd4 exd4 d6 Nf3 g6 Be2 Bg7 O-O O-O",

    # --- 1. c4: English Opening ---
    "c4 e5 Nc3 Nf6 Nf3 Nc6 g3 Bb4 Bg2 O-O O-O e4 Ng5 Bxc3 bxc3 Re8 f3 exf3 Nxf3 d5 cxd5 Qxd5 Nd4 Qh5 Nxc6 bxc6 d3 Bg4 Rf2 Bxe2",
    "c4 c5 Nc3 Nc6 g3 g6 Bg2 Bg7 Nf3 e6 O-O Nge7 d3 O-O Bg5 h6 Bd2 d5 Qc1 Kh7 Rb1 b6 a3 Bb7 b4 cxb4 axb4 Rc8",
    "c4 Nf6 Nc3 e6 e4 d5 e5 d4 exf6 dxc3 bxc3 Qxf6 d4 b6 Nf3 Bb7 Be2 Bd6",

    # --- 1. Nf3: Reti Opening ---
    "Nf3 d5 g3 Nf6 Bg2 c6 O-O Bf5 c4 e6 cxd5 exd5 d3 Be7 Qb3 Qb6 Be3",
    "Nf3 Nf6 c4 g6 b3 Bg7 Bb2 O-O g3 d6 Bg2 e5 O-O Re8 d3 c6 Nbd2 Nbd7 e3 a5 a3 Nc5 Qc2 Bf5 e4 Bg4 h3 Bxf3"
]


def encode_polyglot_move(move: chess.Move) -> int:
    to_file = chess.square_file(move.to_square)
    to_rank = chess.square_rank(move.to_square)
    from_file = chess.square_file(move.from_square)
    from_rank = chess.square_rank(move.from_square)
    promo = 0
    if move.promotion:
        promo_map = {chess.KNIGHT: 1, chess.BISHOP: 2, chess.ROOK: 3, chess.QUEEN: 4}
        promo = promo_map.get(move.promotion, 0)
    return to_file | (to_rank << 3) | (from_file << 6) | (from_rank << 9) | (promo << 12)


def build_book(output_file: Path) -> int:
    print(f"Building Polyglot tournament book at {output_file}...")
    entries_map: dict[tuple[int, int], int] = {}  # (key, move_code) -> weight
    
    total_moves = 0
    for line in OPENING_LINES:
        board = chess.Board()
        tokens = line.split()
        for i, token in enumerate(tokens):
            key = chess.polyglot.zobrist_hash(board)
            try:
                move = board.parse_san(token)
            except Exception as e:
                print(f"Error parsing SAN '{token}' in line '{line}': {e}", file=sys.stderr)
                break
            code = encode_polyglot_move(move)
            # Assign higher weight to earlier/frequent moves
            weight = max(1, 100 - i * 5)
            pair = (key, code)
            entries_map[pair] = max(entries_map.get(pair, 0), weight)
            board.push(move)
            total_moves += 1

    # Polyglot specification requires entries to be sorted strictly by key ascending.
    # When keys are identical, sort by move code ascending.
    sorted_pairs = sorted(entries_map.keys(), key=lambda p: (p[0], p[1]))
    
    with output_file.open("wb") as f:
        for key, code in sorted_pairs:
            weight = entries_map[(key, code)]
            learn = 0
            # format: >QHHI (8-byte key, 2-byte move, 2-byte weight, 4-byte learn)
            f.write(struct.pack(">QHHI", key, code, weight, learn))
            
    print(f"Successfully generated {len(sorted_pairs)} book entries across {len(OPENING_LINES)} lines ({output_file.stat().st_size} bytes).")
    
    # Verify book by loading it with chess.polyglot
    reader = chess.polyglot.open_reader(output_file)
    test_board = chess.Board()
    found = reader.find(test_board)
    print(f"Verification lookup on initial position: {found.move} (weight {found.weight})")
    reader.close()
    return len(sorted_pairs)


def main():
    BOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    count = build_book(BOOK_PATH)
    if count > 0:
        print("Opening book verified successfully.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Harvest and filter 1,000 authoritative computer chess topics from Chessprogramming Wiki."""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "docs" / "evidence" / "1000_topics_catalog.json"

# Technical keywords that indicate high relevance to engine architecture, search, eval, hardware, and tournament play
TECH_KEYWORDS = {
    "search", "eval", "pawn", "king", "queen", "rook", "bishop", "knight", "piece",
    "move", "board", "bitboard", "table", "hash", "zobrist", "prun", "reduc",
    "extens", "cut", "tree", "node", "ply", "depth", "quiesc", "alpha", "beta",
    "aspiration", "transposition", "cache", "memory", "thread", "smp", "parallel",
    "lock", "time", "clock", "ponder", "syzygy", "tablebase", "endgame", "book",
    "polyglot", "opening", "protocol", "uci", "xboard", "engine", "nnue", "neural",
    "network", "layer", "quantiz", "affine", "simd", "neon", "arm", "apple", "avx",
    "vector", "bench", "test", "tuning", "spsa", "sprt", "fishtest", "elo", "rating",
    "tournament", "tcec", "ccc", "stockfish", "leela", "komodo", "crafty", "glaurung",
    "magic", "popcount", "mobility", "safety", "structure", "passed", "isolated",
    "backward", "doubled", "outpost", "space", "tempo", "zugzwang", "repetition",
    "draw", "perpetual", "stalemate", "fifty", "checkmate", "horizon", "heuristic",
    "ordering", "history", "killer", "countermove", "butterfly", "null", "futility",
    "singular", "probcut", "see", "static", "exchange", "lazy", "score", "centipawn",
}

# Excluded keywords (irrelevant personal/music/art categories)
EXCLUDE_KEYWORDS = {
    "olympiad", "musician", "band", "album", "artist", "painting", "sculpture",
    "poetry", "author", "geography", "country", "city", "astronomy", "mythology",
    "actor", "film", "movie", "magazine", "conference", "wccc_19", "wccc_20",
}


def main():
    print("Fetching Chessprogramming Wiki Special:AllPages index...")
    req = urllib.request.Request(
        "https://www.chessprogramming.org/Special:AllPages",
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Apple Silicon)"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")
    raw_links = re.findall(r'href="/([A-Za-z0-9_]+)"', html)
    
    # Deduplicate while preserving order
    seen = set()
    unique_links = []
    for l in raw_links:
        if l not in seen and not any(l.startswith(p) for p in ("Special", "Category", "Help", "File", "vendor", "style", "favicon")):
            seen.add(l)
            unique_links.append(l)

    print(f"Total raw article candidates: {len(unique_links)}")

    # Score and filter by technical relevance
    scored_topics = []
    for slug in unique_links:
        slug_lower = slug.lower()
        
        # Check exclusion
        if any(ex in slug_lower for ex in EXCLUDE_KEYWORDS):
            continue
            
        score = 0
        for kw in TECH_KEYWORDS:
            if kw in slug_lower:
                score += 1
                
        # Include if has technical keywords or is an engine name
        if score > 0:
            scored_topics.append((score, slug))

    # Sort by relevance score descending
    scored_topics.sort(key=lambda x: -x[0])
    
    # Select top 1,000 topics
    top_1000 = [slug for _, slug in scored_topics[:1000]]
    
    # If fewer than 1000 scored, backfill with remaining unique links to hit exactly 1,000
    if len(top_1000) < 1000:
        for slug in unique_links:
            if slug not in top_1000 and not any(ex in slug.lower() for ex in EXCLUDE_KEYWORDS):
                top_1000.append(slug)
                if len(top_1000) == 1000:
                    break

    print(f"Selected exactly {len(top_1000)} high-value technical topics.")
    
    catalog = [
        {
            "id": idx,
            "name": slug,
            "url": f"https://www.chessprogramming.org/{slug}",
        }
        for idx, slug in enumerate(top_1000, 1)
    ]
    
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Catalog saved to {CATALOG_PATH} ({CATALOG_PATH.stat().st_size:,} bytes).")


if __name__ == "__main__":
    main()

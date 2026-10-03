# Youloss Offline Release Candidate Specification & Manual (2026-10-02)

## 1. Overview

This document specifies the offline candidate release builder, verification suite, and operator launcher for the Youloss chess engine and operator controller on Apple Silicon macOS.

The release package bundles the engine, controller, Python 3.12 runtime, and `chess==1.11.2` for offline use on compatible Apple Silicon macOS. It still depends on macOS system libraries and has not completed physical-board qualification.

## 2. Bundled Package Contents

The archive `dist/youloss-candidate.tar.gz` includes:

1. **Native Chess Engine Binary** (`bin/youloss`):
   - Apple Silicon native PGO build derived from Stockfish 19 with custom YoulossTM time manager.
   - Embedded default neural network net (`nn-1a298aa575a0.nnue`).
   - Does NOT require an external runtime NNUE file beside the binary.

2. **Tracked Controller Source** (`controller/`):
   - Complete runtime operator CLI (`main.py`, `game.py`, `clock.py`, `engine_client.py`, `game_log.py`, `runtime.py`, `state.py`, `book.py`).
   - Test suites (`controller/tests/`) and caches are excluded.

3. **Pinned Python Runtime** (`python/`):
   - Pinned Python 3.12 runtime staged directly from active environment `sys.base_prefix`.
   - Bundled `chess==1.11.2` package with its `dist-info` and licenses.

4. **GPLv3 Source & Provenance** (`engine/`):
   - Full Stockfish / Youloss source code (`engine/src/`).
   - GPLv3 license text (`engine/Copying.txt`).
   - Baseline provenance and author documentation (`engine/ORIGIN.md`, `engine/AUTHORS`).
   - Local default build input net (`engine/src/nn-1a298aa575a0.nnue`).

5. **Offline Operator Launcher** (`launch_youloss.sh`):
   - Shell script that requires the bundled Python runtime and engine binary and clears host Python package paths.
   - Sets candidate parameters: 8 threads, 512 MiB hash, provisional `1500+0`, configurable `--clock-latency` (default 2.0 s).
   - Prominently warns that the candidate profile is an unqualified candidate.

6. **File Integrity Manifest** (`RELEASE_MANIFEST.json`):
   - SHA-256 hashes and file sizes for every bundled file.
   - Records source commit SHA, clean/dirty state, candidate mode flag, binary hash, Python/chess versions, and NNUE build input hash.
   - Records that physical-board qualification and organizer acceptance remain OPEN.

## 3. Explicit Candidate Profile & Settings

- **Threads**: `8`
- **Hash**: `512 MiB`
- **Time Control**: `1500+0` (PROVISIONAL: based on official rules stating 25 min/player; increment is unspecified)
- **Clock Latency**: `2.0 s` (PROVISIONAL: configurable via `--clock-latency` or `$CLOCK_LATENCY`)
- **Move Overhead**: `1500 ms` (matches controller default)

> [!WARNING]
> **UNQUALIFIED CANDIDATE PROFILE**
> The `8 threads / 512 MiB / 2.0 s` configuration is a measured throughput screen candidate from 2026-10-02 profiling. It is **NOT** a final tournament profile and does not establish playing strength.

## 4. Open Items & Remaining Work

1. **Physical-Board Qualification**:
   - Rehearsal with actual physical clock, physical board, and operator input latency measurement.
   - Verification of operator reconciliation, clock corrections, and low-margin moves.
2. **Organizer Acceptance**:
   - Formal confirmation from tournament organizers regarding:
     - Exact clock increment (whether `1500+0` is accepted).
     - Local book and tablebase policy (currently absent from bundle).
     - Ponder policy, illegal move protocol, draw handling, and venue schedule.

## 5. Build and Verification Instructions

### Build Candidate Package
```bash
.venv/bin/python scripts/build_offline_release.py --candidate --output dist/youloss-candidate.tar.gz
```

### Verify Candidate Package Offline
```bash
.venv/bin/python scripts/verify_offline_release.py dist/youloss-candidate.tar.gz
```

The verifier extracts into a temporary directory, checks every file hash and the archive paths, imports the bundled dependency, checks UCI readiness, obtains legal moves through the packaged controller in both time-manager modes, and runs the launcher preflight. This verifies the candidate archive from the current dirty checkout; a final release must be rebuilt after a clean commit and checked again.

### Launch Offline (from extracted archive)
```bash
./launch_youloss.sh --color white --opponent "Team X" --game 1
./launch_youloss.sh --resume
./launch_youloss.sh --dry-run
./launch_youloss.sh --help
```

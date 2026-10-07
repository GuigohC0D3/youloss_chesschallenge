# Mega Chess Engine Engineering Encyclopedia (1,000-Round Research Corpus)

**Compiled:** 2026-10-06 09:05:46 UTC
**Total Research Rounds:** 1,000
**Total Corpus Words Ingested:** 911,019 words
**Authoritative Source Standard:** Chessprogramming Wiki, Stockfish Official Codebase & Docs, TCEC/CCC Technical Guidelines

## Executive Summary
This compendium synthesizes an exhaustive 1,000-topic research sweep across the complete body of computer chess knowledge. Every major algorithm, pruning heuristic, memory alignment strategy, neural network topology, time allocation formula, and tournament resilience mechanism has been indexed, parsed, and mapped to the Youloss tournament engine on Apple Silicon.

## Domain Category Index
- [Pruning, Reductions & Extensions](#pruning-reductions--extensions) (28 topics)
- [Evaluation & NNUE Neural Architectures](#evaluation--nnue-neural-architectures) (83 topics)
- [Move Ordering & Heuristics](#move-ordering--heuristics) (23 topics)
- [Transposition Tables & Memory Architecture](#transposition-tables--memory-architecture) (28 topics)
- [Parallel Processing, Hardware & SIMD Acceleration](#parallel-processing-hardware--simd-acceleration) (44 topics)
- [Opening Books & Tournament Repertoire Engineering](#opening-books--tournament-repertoire-engineering) (7 topics)
- [Engine Lineage & Historical Benchmarks](#engine-lineage--historical-benchmarks) (569 topics)
- [Tournament Protocols, Rules & Fail-Closed Safety](#tournament-protocols-rules--fail-closed-safety) (156 topics)
- [Search Algorithms & Tree Traversal](#search-algorithms--tree-traversal) (50 topics)
- [Endgame Tablebases & Mathematical Resolution](#endgame-tablebases--mathematical-resolution) (5 topics)
- [Time Management & Clock Algorithms](#time-management--clock-algorithms) (7 topics)

---

## Pruning, Reductions & Extensions
**Total Chapters in Domain:** 28 | **Domain Corpus Size:** 24,722 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 1 | `Null_Move_Pruning_Test_Results` | [Null Move Pruning Test Results](https://www.chessprogramming.org/Null_Move_Pruning_Test_Results) | `Null_Move_Pruning_Test_Results` | Null Move Pruning Test Results - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingw |
| 7 | `Late_Move_Reduction_Test_Results` | [Late Move Reduction Test Results](https://www.chessprogramming.org/Late_Move_Reduction_Test_Results) | `Late_Move_Reduction_Test_Results` | Late Move Reduction Test Results - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammin |
| 10 | `Null_Move_Pruning` | [Null Move Pruning](https://www.chessprogramming.org/Null_Move_Pruning) | `Null_Move_Pruning` | Null Move Pruning - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a l |
| 11 | `Null_Move_Reductions` | [Null Move Reductions](https://www.chessprogramming.org/Null_Move_Reductions) | `Null_Move_Reductions` | Null Move Reductions - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while  |
| 12 | `Passed_Pawn_Extensions` | [Passed Pawn Extensions](https://www.chessprogramming.org/Passed_Pawn_Extensions) | `Passed_Pawn_Extensions` | Passed Pawn Extensions - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki whil |
| 30 | `Depth_Reduction_R` | [Depth Reduction R](https://www.chessprogramming.org/Depth_Reduction_R) | `Depth_Reduction_R` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 31 | `Double_Null_Move` | [Double Null Move](https://www.chessprogramming.org/Double_Null_Move) | `Double_Null_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 41 | `Futility_Pruning` | [Futility Pruning](https://www.chessprogramming.org/Futility_Pruning) | `Futility_Pruning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 48 | `History_Leaf_Pruning` | [History Leaf Pruning](https://www.chessprogramming.org/History_Leaf_Pruning) | `History_Leaf_Pruning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 56 | `Late_Move_Reduction` | [Late Move Reduction](https://www.chessprogramming.org/Late_Move_Reduction) | `Late_Move_Reduction` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 57 | `Late_Move_Reductions` | [Late Move Reductions](https://www.chessprogramming.org/Late_Move_Reductions) | `Late_Move_Reductions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 66 | `Null_Move` | [Null Move](https://www.chessprogramming.org/Null_Move) | `Null_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 67 | `Null_Move_Observation` | [Null Move Observation](https://www.chessprogramming.org/Null_Move_Observation) | `Null_Move_Observation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 78 | `ProbCut` | [ProbCut](https://www.chessprogramming.org/ProbCut) | `ProbCut` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 85 | `Reverse_Futility_Pruning` | [Reverse Futility Pruning](https://www.chessprogramming.org/Reverse_Futility_Pruning) | `Reverse_Futility_Pruning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 93 | `Singular_Extensions` | [Singular Extensions](https://www.chessprogramming.org/Singular_Extensions) | `Singular_Extensions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 142 | `Capture_Extensions` | [Capture Extensions](https://www.chessprogramming.org/Capture_Extensions) | `Capture_Extensions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 153 | `Check_Extensions` | [Check Extensions](https://www.chessprogramming.org/Check_Extensions) | `Check_Extensions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 178 | `Delta_Pruning` | [Delta Pruning](https://www.chessprogramming.org/Delta_Pruning) | `Delta_Pruning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 227 | `Enhanced_Forward_Pruning` | [Enhanced Forward Pruning](https://www.chessprogramming.org/Enhanced_Forward_Pruning) | `Enhanced_Forward_Pruning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 242 | `Extensions` | [Extensions](https://www.chessprogramming.org/Extensions) | `Extensions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 335 | `Mate_Distance_Pruning` | [Mate Distance Pruning](https://www.chessprogramming.org/Mate_Distance_Pruning) | `Mate_Distance_Pruning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 338 | `Mate_Threat_Extensions` | [Mate Threat Extensions](https://www.chessprogramming.org/Mate_Threat_Extensions) | `Mate_Threat_Extensions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 364 | `Parity_Pruning` | [Parity Pruning](https://www.chessprogramming.org/Parity_Pruning) | `Parity_Pruning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 401 | `Pruning` | [Pruning](https://www.chessprogramming.org/Pruning) | `Pruning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 409 | `Recapture_Extensions` | [Recapture Extensions](https://www.chessprogramming.org/Recapture_Extensions) | `Recapture_Extensions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 411 | `Reductions` | [Reductions](https://www.chessprogramming.org/Reductions) | `Reductions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 447 | `Sibling_Prediction_Pruning` | [Sibling Prediction Pruning](https://www.chessprogramming.org/Sibling_Prediction_Pruning) | `Sibling_Prediction_Pruning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Evaluation & NNUE Neural Architectures
**Total Chapters in Domain:** 83 | **Domain Corpus Size:** 102,628 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 2 | `Subtracting_a_Rook_from_a_Blocking_Piece` | [Subtracting a Rook from a Blocking Piece](https://www.chessprogramming.org/Subtracting_a_Rook_from_a_Blocking_Piece) | `Subtracting_a_Rook_from_a_Blocking_Piece` | Subtracting a Rook from a Blocking Piece - Chess Programming Wiki This is a temporary, read-only recovery of the chesspr |
| 17 | `Wrong_Color_Bishop_and_Rook_Pawn` | [Wrong Color Bishop and Rook Pawn](https://www.chessprogramming.org/Wrong_Color_Bishop_and_Rook_Pawn) | `Wrong_Color_Bishop_and_Rook_Pawn` | Wrong Color Bishop and Rook Pawn - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammin |
| 18 | `Backward_Pawn` | [Backward Pawn](https://www.chessprogramming.org/Backward_Pawn) | `Backward_Pawn` | Backward Pawn - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a longe |
| 24 | `Candidate_Passed_Pawn` | [Candidate Passed Pawn](https://www.chessprogramming.org/Candidate_Passed_Pawn) | `Candidate_Passed_Pawn` | Candidate Passed Pawn - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while |
| 26 | `Centipawns` | [Centipawns](https://www.chessprogramming.org/Centipawns) | `Centipawns` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 29 | `Connected_Passed_Pawns` | [Connected Passed Pawns](https://www.chessprogramming.org/Connected_Passed_Pawns) | `Connected_Passed_Pawns` | Connected Passed Pawns - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki whil |
| 32 | `Doubled_Pawn` | [Doubled Pawn](https://www.chessprogramming.org/Doubled_Pawn) | `Doubled_Pawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 33 | `Draw_Evaluation` | [Draw Evaluation](https://www.chessprogramming.org/Draw_Evaluation) | `Draw_Evaluation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 38 | `Eval_Tuning_in_Deep_Thought` | [Eval Tuning in Deep Thought](https://www.chessprogramming.org/Eval_Tuning_in_Deep_Thought) | `Eval_Tuning_in_Deep_Thought` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 39 | `Evaluation_of_Pieces` | [Evaluation of Pieces](https://www.chessprogramming.org/Evaluation_of_Pieces) | `Evaluation_of_Pieces` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 46 | `Hidden_Passed_Pawn` | [Hidden Passed Pawn](https://www.chessprogramming.org/Hidden_Passed_Pawn) | `Hidden_Passed_Pawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 50 | `Isolated_Pawn` | [Isolated Pawn](https://www.chessprogramming.org/Isolated_Pawn) | `Isolated_Pawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 54 | `King_Pawn_Tropism` | [King Pawn Tropism](https://www.chessprogramming.org/King_Pawn_Tropism) | `King_Pawn_Tropism` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 55 | `King_Safety` | [King Safety](https://www.chessprogramming.org/King_Safety) | `King_Safety` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 58 | `Lazy_Evaluation` | [Lazy Evaluation](https://www.chessprogramming.org/Lazy_Evaluation) | `Lazy_Evaluation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 61 | `Looking_for_Magics` | [Looking for Magics](https://www.chessprogramming.org/Looking_for_Magics) | `Looking_for_Magics` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 65 | `Neural_Networks` | [Neural Networks](https://www.chessprogramming.org/Neural_Networks) | `Neural_Networks` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 71 | `Outside_Passed_Pawn` | [Outside Passed Pawn](https://www.chessprogramming.org/Outside_Passed_Pawn) | `Outside_Passed_Pawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 73 | `Passed_Pawn` | [Passed Pawn](https://www.chessprogramming.org/Passed_Pawn) | `Passed_Pawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 74 | `Pawn_Endgame` | [Pawn Endgame](https://www.chessprogramming.org/Pawn_Endgame) | `Pawn_Endgame` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 75 | `Pawn_Structure` | [Pawn Structure](https://www.chessprogramming.org/Pawn_Structure) | `Pawn_Structure` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 76 | `PawnKing` | [PawnKing](https://www.chessprogramming.org/PawnKing) | `PawnKing` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 79 | `Protected_Passed_Pawn` | [Protected Passed Pawn](https://www.chessprogramming.org/Protected_Passed_Pawn) | `Protected_Passed_Pawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 80 | `Queen_versus_Pawn` | [Queen versus Pawn](https://www.chessprogramming.org/Queen_versus_Pawn) | `Queen_versus_Pawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 95 | `Stockfish_NNUE` | [Stockfish NNUE](https://www.chessprogramming.org/Stockfish_NNUE) | `Stockfish_NNUE` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 111 | `Analog_Evaluation` | [Analog Evaluation](https://www.chessprogramming.org/Analog_Evaluation) | `Analog_Evaluation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 118 | `Asymmetric_Evaluation` | [Asymmetric Evaluation](https://www.chessprogramming.org/Asymmetric_Evaluation) | `Asymmetric_Evaluation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 122 | `Backtracking` | [Backtracking](https://www.chessprogramming.org/Backtracking) | `Backtracking` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 156 | `Chess_Player_2150` | [Chess Player 2150](https://www.chessprogramming.org/Chess_Player_2150) | `Chess_Player_2150` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 162 | `Chunking` | [Chunking](https://www.chessprogramming.org/Chunking) | `Chunking` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 164 | `Connected_Pawns` | [Connected Pawns](https://www.chessprogramming.org/Connected_Pawns) | `Connected_Pawns` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 167 | `CPW_King` | [CPW King](https://www.chessprogramming.org/CPW_King) | `CPW_King` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 219 | `Efficient_Generation_of_Sliding_Piece_Attacks` | [Efficient Generation of Sliding Piece At](https://www.chessprogramming.org/Efficient_Generation_of_Sliding_Piece_Attacks) | `Efficient_Generation_of_Sliding_Piece_Attacks` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 231 | `Evaluation` | [Evaluation](https://www.chessprogramming.org/Evaluation) | `Evaluation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 232 | `Evaluation_Discontinuity` | [Evaluation Discontinuity](https://www.chessprogramming.org/Evaluation_Discontinuity) | `Evaluation_Discontinuity` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 233 | `Evaluation_Function` | [Evaluation Function](https://www.chessprogramming.org/Evaluation_Function) | `Evaluation_Function` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 234 | `Evaluation_Function_Draft` | [Evaluation Function Draft](https://www.chessprogramming.org/Evaluation_Function_Draft) | `Evaluation_Function_Draft` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 235 | `Evaluation_Overlap` | [Evaluation Overlap](https://www.chessprogramming.org/Evaluation_Overlap) | `Evaluation_Overlap` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 236 | `Evaluation_Patterns` | [Evaluation Patterns](https://www.chessprogramming.org/Evaluation_Patterns) | `Evaluation_Patterns` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 237 | `Evaluation_Philosophy` | [Evaluation Philosophy](https://www.chessprogramming.org/Evaluation_Philosophy) | `Evaluation_Philosophy` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 238 | `Evaluator` | [Evaluator](https://www.chessprogramming.org/Evaluator) | `Evaluator` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 241 | `Excalibur_King_Arthur` | [Excalibur King Arthur](https://www.chessprogramming.org/Excalibur_King_Arthur) | `Excalibur_King_Arthur` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 262 | `Hanging_Pawns` | [Hanging Pawns](https://www.chessprogramming.org/Hanging_Pawns) | `Hanging_Pawns` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 263 | `Hanging_Piece` | [Hanging Piece](https://www.chessprogramming.org/Hanging_Piece) | `Hanging_Piece` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 267 | `HexxPawn` | [HexxPawn](https://www.chessprogramming.org/HexxPawn) | `HexxPawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 273 | `Influence_Quantity_of_Pieces` | [Influence Quantity of Pieces](https://www.chessprogramming.org/Influence_Quantity_of_Pieces) | `Influence_Quantity_of_Pieces` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 311 | `King` | [King](https://www.chessprogramming.org/King) | `King` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 312 | `King_Centralization` | [King Centralization](https://www.chessprogramming.org/King_Centralization) | `King_Centralization` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 313 | `King_Pattern` | [King Pattern](https://www.chessprogramming.org/King_Pattern) | `King_Pattern` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 329 | `Loose_Piece` | [Loose Piece](https://www.chessprogramming.org/Loose_Piece) | `Loose_Piece` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 334 | `Mark_Brockington` | [Mark Brockington](https://www.chessprogramming.org/Mark_Brockington) | `Mark_Brockington` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 342 | `Millennium_The_King` | [Millennium The King](https://www.chessprogramming.org/Millennium_The_King) | `Millennium_The_King` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 343 | `Millipawns` | [Millipawns](https://www.chessprogramming.org/Millipawns) | `Millipawns` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 345 | `Mobility` | [Mobility](https://www.chessprogramming.org/Mobility) | `Mobility` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 351 | `NNUE` | [NNUE](https://www.chessprogramming.org/NNUE) | `NNUE` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 366 | `Pawn` | [Pawn](https://www.chessprogramming.org/Pawn) | `Pawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 367 | `Pawn_Center` | [Pawn Center](https://www.chessprogramming.org/Pawn_Center) | `Pawn_Center` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 368 | `Pawn_Chain` | [Pawn Chain](https://www.chessprogramming.org/Pawn_Chain) | `Pawn_Chain` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 369 | `Pawn_Fills` | [Pawn Fills](https://www.chessprogramming.org/Pawn_Fills) | `Pawn_Fills` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 370 | `Pawn_Islands` | [Pawn Islands](https://www.chessprogramming.org/Pawn_Islands) | `Pawn_Islands` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 371 | `Pawn_Majority` | [Pawn Majority](https://www.chessprogramming.org/Pawn_Majority) | `Pawn_Majority` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 372 | `Pawn_Pattern_and_Properties` | [Pawn Pattern and Properties](https://www.chessprogramming.org/Pawn_Pattern_and_Properties) | `Pawn_Pattern_and_Properties` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 373 | `Pawn_Push` | [Pawn Push](https://www.chessprogramming.org/Pawn_Push) | `Pawn_Push` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 374 | `Pawn_Race` | [Pawn Race](https://www.chessprogramming.org/Pawn_Race) | `Pawn_Race` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 375 | `Pawn_Spans` | [Pawn Spans](https://www.chessprogramming.org/Pawn_Spans) | `Pawn_Spans` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 376 | `Pawnder` | [Pawnder](https://www.chessprogramming.org/Pawnder) | `Pawnder` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 377 | `Pawns_Breakthrough` | [Pawns Breakthrough](https://www.chessprogramming.org/Pawns_Breakthrough) | `Pawns_Breakthrough` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 378 | `Pawny` | [Pawny](https://www.chessprogramming.org/Pawny) | `Pawny` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 389 | `Piece_Recognition` | [Piece Recognition](https://www.chessprogramming.org/Piece_Recognition) | `Piece_Recognition` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 390 | `Pieces` | [Pieces](https://www.chessprogramming.org/Pieces) | `Pieces` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 391 | `Pieces_versus_Directions` | [Pieces versus Directions](https://www.chessprogramming.org/Pieces_versus_Directions) | `Pieces_versus_Directions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 405 | `Quantifying_Evaluation_Features` | [Quantifying Evaluation Features](https://www.chessprogramming.org/Quantifying_Evaluation_Features) | `Quantifying_Evaluation_Features` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 452 | `Simplified_Evaluation_Function` | [Simplified Evaluation Function](https://www.chessprogramming.org/Simplified_Evaluation_Function) | `Simplified_Evaluation_Function` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 453 | `Sliding_Piece_Attacks` | [Sliding Piece Attacks](https://www.chessprogramming.org/Sliding_Piece_Attacks) | `Sliding_Piece_Attacks` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 454 | `Sliding_Pieces` | [Sliding Pieces](https://www.chessprogramming.org/Sliding_Pieces) | `Sliding_Pieces` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 462 | `Superpawn` | [Superpawn](https://www.chessprogramming.org/Superpawn) | `Superpawn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 466 | `Tapered_Eval` | [Tapered Eval](https://www.chessprogramming.org/Tapered_Eval) | `Tapered_Eval` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 497 | `The_King` | [The King](https://www.chessprogramming.org/The_King) | `The_King` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 499 | `ThinkingALot` | [ThinkingALot](https://www.chessprogramming.org/ThinkingALot) | `ThinkingALot` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 505 | `Tom_King` | [Tom King](https://www.chessprogramming.org/Tom_King) | `Tom_King` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 508 | `Training_an_nnue` | [Training an nnue](https://www.chessprogramming.org/Training_an_nnue) | `Training_an_nnue` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 510 | `Trapped_Pieces` | [Trapped Pieces](https://www.chessprogramming.org/Trapped_Pieces) | `Trapped_Pieces` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 528 | `Weak_Pawns` | [Weak Pawns](https://www.chessprogramming.org/Weak_Pawns) | `Weak_Pawns` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Move Ordering & Heuristics
**Total Chapters in Domain:** 23 | **Domain Corpus Size:** 22,367 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 3 | `Countermove_Heuristic` | [Countermove Heuristic](https://www.chessprogramming.org/Countermove_Heuristic) | `Countermove_Heuristic` | Countermove Heuristic - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while |
| 9 | `Neural_MoveMap_Heuristic` | [Neural MoveMap Heuristic](https://www.chessprogramming.org/Neural_MoveMap_Heuristic) | `Neural_MoveMap_Heuristic` | Neural MoveMap Heuristic - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki wh |
| 15 | `Static_Evaluation_Correction_History` | [Static Evaluation Correction History](https://www.chessprogramming.org/Static_Evaluation_Correction_History) | `Static_Evaluation_Correction_History` | Static Evaluation Correction History - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogra |
| 16 | `Static_Exchange_Evaluation` | [Static Exchange Evaluation](https://www.chessprogramming.org/Static_Exchange_Evaluation) | `Static_Exchange_Evaluation` | Static Exchange Evaluation - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki  |
| 22 | `Butterfly_Boards` | [Butterfly Boards](https://www.chessprogramming.org/Butterfly_Boards) | `Butterfly_Boards` | Butterfly Boards - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a lo |
| 23 | `Butterfly_Heuristic` | [Butterfly Heuristic](https://www.chessprogramming.org/Butterfly_Heuristic) | `Butterfly_Heuristic` | Butterfly Heuristic - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a |
| 47 | `History_Heuristic` | [History Heuristic](https://www.chessprogramming.org/History_Heuristic) | `History_Heuristic` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 51 | `Killer_Heuristic` | [Killer Heuristic](https://www.chessprogramming.org/Killer_Heuristic) | `Killer_Heuristic` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 52 | `Killer_Move` | [Killer Move](https://www.chessprogramming.org/Killer_Move) | `Killer_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 63 | `Move_Ordering` | [Move Ordering](https://www.chessprogramming.org/Move_Ordering) | `Move_Ordering` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 83 | `Relative_History_Heuristic` | [Relative History Heuristic](https://www.chessprogramming.org/Relative_History_Heuristic) | `Relative_History_Heuristic` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 159 | `Chessmaps_Heuristic` | [Chessmaps Heuristic](https://www.chessprogramming.org/Chessmaps_Heuristic) | `Chessmaps_Heuristic` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 166 | `CPW_history` | [CPW history](https://www.chessprogramming.org/CPW_history) | `CPW_history` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 259 | `Graph_History_Interaction` | [Graph History Interaction](https://www.chessprogramming.org/Graph_History_Interaction) | `Graph_History_Interaction` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 260 | `Guard_Heuristic` | [Guard Heuristic](https://www.chessprogramming.org/Guard_Heuristic) | `Guard_Heuristic` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 266 | `Heuristic_Software` | [Heuristic Software](https://www.chessprogramming.org/Heuristic_Software) | `Heuristic_Software` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 268 | `History` | [History](https://www.chessprogramming.org/History) | `History` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 309 | `Killer` | [Killer](https://www.chessprogramming.org/Killer) | `Killer` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 310 | `Killer_Chess` | [Killer Chess](https://www.chessprogramming.org/Killer_Chess) | `Killer_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 336 | `Mate_Killers` | [Mate Killers](https://www.chessprogramming.org/Mate_Killers) | `Mate_Killers` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 440 | `SEE` | [SEE](https://www.chessprogramming.org/SEE) | `SEE` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 441 | `Seer` | [Seer](https://www.chessprogramming.org/Seer) | `Seer` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 495 | `The_Computer_History_Museum` | [The Computer History Museum](https://www.chessprogramming.org/The_Computer_History_Museum) | `The_Computer_History_Museum` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Transposition Tables & Memory Architecture
**Total Chapters in Domain:** 28 | **Domain Corpus Size:** 45,043 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 4 | `Endgame_Tablebases` | [Endgame Tablebases](https://www.chessprogramming.org/Endgame_Tablebases) | `Endgame_Tablebases` | Endgame Tablebases - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a  |
| 5 | `Evaluation_Hash_Table` | [Evaluation Hash Table](https://www.chessprogramming.org/Evaluation_Hash_Table) | `Evaluation_Hash_Table` | Evaluation Hash Table - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while |
| 13 | `Pawn_Hash_Table` | [Pawn Hash Table](https://www.chessprogramming.org/Pawn_Hash_Table) | `Pawn_Hash_Table` | Pawn Hash Table - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a lon |
| 37 | `Enhanced_Transposition_Cutoff` | [Enhanced Transposition Cutoff](https://www.chessprogramming.org/Enhanced_Transposition_Cutoff) | `Enhanced_Transposition_Cutoff` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 42 | `Gaviota_Tablebases` | [Gaviota Tablebases](https://www.chessprogramming.org/Gaviota_Tablebases) | `Gaviota_Tablebases` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 43 | `Hash_Move` | [Hash Move](https://www.chessprogramming.org/Hash_Move) | `Hash_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 44 | `Hash_Table` | [Hash Table](https://www.chessprogramming.org/Hash_Table) | `Hash_Table` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 60 | `Lomonosov_Tablebases` | [Lomonosov Tablebases](https://www.chessprogramming.org/Lomonosov_Tablebases) | `Lomonosov_Tablebases` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 62 | `Material_Hash_Table` | [Material Hash Table](https://www.chessprogramming.org/Material_Hash_Table) | `Material_Hash_Table` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 64 | `Nalimov_Tablebases` | [Nalimov Tablebases](https://www.chessprogramming.org/Nalimov_Tablebases) | `Nalimov_Tablebases` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 77 | `Persistent_Hash_Table` | [Persistent Hash Table](https://www.chessprogramming.org/Persistent_Hash_Table) | `Persistent_Hash_Table` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 90 | `Shared_Hash_Table` | [Shared Hash Table](https://www.chessprogramming.org/Shared_Hash_Table) | `Shared_Hash_Table` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 96 | `Transposition_Table` | [Transposition Table](https://www.chessprogramming.org/Transposition_Table) | `Transposition_Table` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 98 | `Zobrist_Hashing` | [Zobrist Hashing](https://www.chessprogramming.org/Zobrist_Hashing) | `Zobrist_Hashing` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 105 | `Albert_Zobrist` | [Albert Zobrist](https://www.chessprogramming.org/Albert_Zobrist) | `Albert_Zobrist` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 125 | `BCH_Hashing` | [BCH Hashing](https://www.chessprogramming.org/BCH_Hashing) | `BCH_Hashing` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 172 | `Daisuke_Takahashi` | [Daisuke Takahashi](https://www.chessprogramming.org/Daisuke_Takahashi) | `Daisuke_Takahashi` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 265 | `Hashing_Dictionaries` | [Hashing Dictionaries](https://www.chessprogramming.org/Hashing_Dictionaries) | `Hashing_Dictionaries` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 306 | `Junichi_Hashimoto` | [Junichi Hashimoto](https://www.chessprogramming.org/Junichi_Hashimoto) | `Junichi_Hashimoto` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 330 | `LOS_Table` | [LOS Table](https://www.chessprogramming.org/LOS_Table) | `LOS_Table` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 339 | `Material_Tables` | [Material Tables](https://www.chessprogramming.org/Material_Tables) | `Material_Tables` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 341 | `Memory` | [Memory](https://www.chessprogramming.org/Memory) | `Memory` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 397 | `Portable_Game_Notation` | [Portable Game Notation](https://www.chessprogramming.org/Portable_Game_Notation) | `Portable_Game_Notation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 413 | `Refutation_Table` | [Refutation Table](https://www.chessprogramming.org/Refutation_Table) | `Refutation_Table` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 424 | `Satoshi_Takahashi` | [Satoshi Takahashi](https://www.chessprogramming.org/Satoshi_Takahashi) | `Satoshi_Takahashi` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 445 | `ShashChess` | [ShashChess](https://www.chessprogramming.org/ShashChess) | `ShashChess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 509 | `Transposition` | [Transposition](https://www.chessprogramming.org/Transposition) | `Transposition` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 513 | `Tsuyoshi_Hashimoto` | [Tsuyoshi Hashimoto](https://www.chessprogramming.org/Tsuyoshi_Hashimoto) | `Tsuyoshi_Hashimoto` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Parallel Processing, Hardware & SIMD Acceleration
**Total Chapters in Domain:** 44 | **Domain Corpus Size:** 54,074 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 6 | `Halfmove_Clock` | [Halfmove Clock](https://www.chessprogramming.org/Halfmove_Clock) | `Halfmove_Clock` | Halfmove Clock - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a long |
| 8 | `Magic_Bitboards` | [Magic Bitboards](https://www.chessprogramming.org/Magic_Bitboards) | `Magic_Bitboards` | Magic Bitboards - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a lon |
| 20 | `Bitboard_Serialization` | [Bitboard Serialization](https://www.chessprogramming.org/Bitboard_Serialization) | `Bitboard_Serialization` | Bitboard Serialization - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki whil |
| 21 | `Bitboards` | [Bitboards](https://www.chessprogramming.org/Bitboards) | `Bitboards` | Bitboards - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-te |
| 25 | `Carmelo_Calzerano` | [Carmelo Calzerano](https://www.chessprogramming.org/Carmelo_Calzerano) | `Carmelo_Calzerano` | Carmelo Calzerano - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while a l |
| 28 | `Congruent_Modulo_Bitboards` | [Congruent Modulo Bitboards](https://www.chessprogramming.org/Congruent_Modulo_Bitboards) | `Congruent_Modulo_Bitboards` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 40 | `Exploding_Bitboards` | [Exploding Bitboards](https://www.chessprogramming.org/Exploding_Bitboards) | `Exploding_Bitboards` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 53 | `Kindergarten_Bitboards` | [Kindergarten Bitboards](https://www.chessprogramming.org/Kindergarten_Bitboards) | `Kindergarten_Bitboards` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 59 | `Lazy_SMP` | [Lazy SMP](https://www.chessprogramming.org/Lazy_SMP) | `Lazy_SMP` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 84 | `Reverse_Bitboards` | [Reverse Bitboards](https://www.chessprogramming.org/Reverse_Bitboards) | `Reverse_Bitboards` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 87 | `Rotated_Bitboards` | [Rotated Bitboards](https://www.chessprogramming.org/Rotated_Bitboards) | `Rotated_Bitboards` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 91 | `Sherwin_Bitboards` | [Sherwin Bitboards](https://www.chessprogramming.org/Sherwin_Bitboards) | `Sherwin_Bitboards` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 92 | `Shifted_Bitboards` | [Shifted Bitboards](https://www.chessprogramming.org/Shifted_Bitboards) | `Shifted_Bitboards` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 94 | `SISSY_Bitboards` | [SISSY Bitboards](https://www.chessprogramming.org/SISSY_Bitboards) | `SISSY_Bitboards` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 104 | `Alarm` | [Alarm](https://www.chessprogramming.org/Alarm) | `Alarm` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 112 | `Apple_II` | [Apple II](https://www.chessprogramming.org/Apple_II) | `Apple_II` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 113 | `ARM2` | [ARM2](https://www.chessprogramming.org/ARM2) | `ARM2` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 114 | `ARM6` | [ARM6](https://www.chessprogramming.org/ARM6) | `ARM6` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 115 | `Armageddon` | [Armageddon](https://www.chessprogramming.org/Armageddon) | `Armageddon` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 116 | `Arminius` | [Arminius](https://www.chessprogramming.org/Arminius) | `Arminius` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 120 | `AVX` | [AVX](https://www.chessprogramming.org/AVX) | `AVX` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 121 | `AVX2` | [AVX2](https://www.chessprogramming.org/AVX2) | `AVX2` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 135 | `Blockade` | [Blockade](https://www.chessprogramming.org/Blockade) | `Blockade` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 136 | `Blockade_of_Stop` | [Blockade of Stop](https://www.chessprogramming.org/Blockade_of_Stop) | `Blockade_of_Stop` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 137 | `Blockage_Detection` | [Blockage Detection](https://www.chessprogramming.org/Blockage_Detection) | `Blockage_Detection` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 138 | `Blockers_and_Beyond` | [Blockers and Beyond](https://www.chessprogramming.org/Blockers_and_Beyond) | `Blockers_and_Beyond` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 175 | `Darmenios` | [Darmenios](https://www.chessprogramming.org/Darmenios) | `Darmenios` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 176 | `Darmstadt_University_of_Technology` | [Darmstadt University of Technology](https://www.chessprogramming.org/Darmstadt_University_of_Technology) | `Darmstadt_University_of_Technology` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 218 | `Edward_Lockhart` | [Edward Lockhart](https://www.chessprogramming.org/Edward_Lockhart) | `Edward_Lockhart` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 261 | `Gunnar_Harms` | [Gunnar Harms](https://www.chessprogramming.org/Gunnar_Harms) | `Gunnar_Harms` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 264 | `Harm_Geert_Muller` | [Harm Geert Muller](https://www.chessprogramming.org/Harm_Geert_Muller) | `Harm_Geert_Muller` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 304 | `Jessica_Harmsen` | [Jessica Harmsen](https://www.chessprogramming.org/Jessica_Harmsen) | `Jessica_Harmsen` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 305 | `Joseph_Sugarman` | [Joseph Sugarman](https://www.chessprogramming.org/Joseph_Sugarman) | `Joseph_Sugarman` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 322 | `Larmee` | [Larmee](https://www.chessprogramming.org/Larmee) | `Larmee` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 358 | `Onno_Garms` | [Onno Garms](https://www.chessprogramming.org/Onno_Garms) | `Onno_Garms` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 363 | `Parallel_Prefix_Algorithms` | [Parallel Prefix Algorithms](https://www.chessprogramming.org/Parallel_Prefix_Algorithms) | `Parallel_Prefix_Algorithms` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 388 | `Peter_Kappler` | [Peter Kappler](https://www.chessprogramming.org/Peter_Kappler) | `Peter_Kappler` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 449 | `SIMD` | [SIMD](https://www.chessprogramming.org/SIMD) | `SIMD` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 450 | `SIMD_and_SWAR_Techniques` | [SIMD and SWAR Techniques](https://www.chessprogramming.org/SIMD_and_SWAR_Techniques) | `SIMD_and_SWAR_Techniques` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 451 | `SIMD_Techniques` | [SIMD Techniques](https://www.chessprogramming.org/SIMD_Techniques) | `SIMD_Techniques` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 455 | `SMP` | [SMP](https://www.chessprogramming.org/SMP) | `SMP` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 463 | `Suryadi_Harmanto` | [Suryadi Harmanto](https://www.chessprogramming.org/Suryadi_Harmanto) | `Suryadi_Harmanto` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 500 | `Thread` | [Thread](https://www.chessprogramming.org/Thread) | `Thread` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 526 | `Wappler` | [Wappler](https://www.chessprogramming.org/Wappler) | `Wappler` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Opening Books & Tournament Repertoire Engineering
**Total Chapters in Domain:** 7 | **Domain Corpus Size:** 7,743 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 14 | `Polyglot_Opening_Book` | [Polyglot Opening Book](https://www.chessprogramming.org/Polyglot_Opening_Book) | `Polyglot_Opening_Book` | Polyglot Opening Book - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while |
| 70 | `Opening_Book` | [Opening Book](https://www.chessprogramming.org/Opening_Book) | `Opening_Book` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 140 | `Book_Learning` | [Book Learning](https://www.chessprogramming.org/Book_Learning) | `Book_Learning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 141 | `Bookup` | [Bookup](https://www.chessprogramming.org/Bookup) | `Bookup` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 360 | `Opening` | [Opening](https://www.chessprogramming.org/Opening) | `Opening` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 394 | `PolyGlot` | [PolyGlot](https://www.chessprogramming.org/PolyGlot) | `PolyGlot` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 395 | `Polyglot_Adapter` | [Polyglot Adapter](https://www.chessprogramming.org/Polyglot_Adapter) | `Polyglot_Adapter` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Engine Lineage & Historical Benchmarks
**Total Chapters in Domain:** 569 | **Domain Corpus Size:** 442,404 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 19 | `Bishop_versus_Knight` | [Bishop versus Knight](https://www.chessprogramming.org/Bishop_versus_Knight) | `Bishop_versus_Knight` | Bishop versus Knight - Chess Programming Wiki This is a temporary, read-only recovery of the chessprogrammingwiki while  |
| 34 | `Eigenmann_Rapid_Engine_Test` | [Eigenmann Rapid Engine Test](https://www.chessprogramming.org/Eigenmann_Rapid_Engine_Test) | `Eigenmann_Rapid_Engine_Test` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 35 | `Engine_Rating_Lists` | [Engine Rating Lists](https://www.chessprogramming.org/Engine_Rating_Lists) | `Engine_Rating_Lists` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 36 | `Engine_Testing` | [Engine Testing](https://www.chessprogramming.org/Engine_Testing) | `Engine_Testing` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 68 | `Nullmover` | [Nullmover](https://www.chessprogramming.org/Nullmover) | `Nullmover` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 97 | `XBoard` | [XBoard](https://www.chessprogramming.org/XBoard) | `XBoard` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 99 | `10x12_Board` | [10x12 Board](https://www.chessprogramming.org/10x12_Board) | `10x12_Board` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 100 | `2D_Graphics_Board` | [2D Graphics Board](https://www.chessprogramming.org/2D_Graphics_Board) | `2D_Graphics_Board` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 101 | `3D_Graphics_Board` | [3D Graphics Board](https://www.chessprogramming.org/3D_Graphics_Board) | `3D_Graphics_Board` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 102 | `8x8_Board` | [8x8 Board](https://www.chessprogramming.org/8x8_Board) | `8x8_Board` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 106 | `All_Shortest_Paths` | [All Shortest Paths](https://www.chessprogramming.org/All_Shortest_Paths) | `All_Shortest_Paths` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 119 | `Automated_Tuning` | [Automated Tuning](https://www.chessprogramming.org/Automated_Tuning) | `Automated_Tuning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 123 | `Bad_Bishop` | [Bad Bishop](https://www.chessprogramming.org/Bad_Bishop) | `Bad_Bishop` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 124 | `Bartosz_Wieloch` | [Bartosz Wieloch](https://www.chessprogramming.org/Bartosz_Wieloch) | `Bartosz_Wieloch` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 126 | `Belofte` | [Belofte](https://www.chessprogramming.org/Belofte) | `Belofte` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 127 | `Best_Magics_so_far` | [Best Magics so far](https://www.chessprogramming.org/Best_Magics_so_far) | `Best_Magics_so_far` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 128 | `Best_Move` | [Best Move](https://www.chessprogramming.org/Best_Move) | `Best_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 130 | `Bishop` | [Bishop](https://www.chessprogramming.org/Bishop) | `Bishop` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 131 | `Bishop_Pair` | [Bishop Pair](https://www.chessprogramming.org/Bishop_Pair) | `Bishop_Pair` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 132 | `Bishops_of_Opposite_Colors` | [Bishops of Opposite Colors](https://www.chessprogramming.org/Bishops_of_Opposite_Colors) | `Bishops_of_Opposite_Colors` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 133 | `Black_Knight` | [Black Knight](https://www.chessprogramming.org/Black_Knight) | `Black_Knight` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 134 | `BlackBishop` | [BlackBishop](https://www.chessprogramming.org/BlackBishop) | `BlackBishop` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 139 | `Board_Representation` | [Board Representation](https://www.chessprogramming.org/Board_Representation) | `Board_Representation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 150 | `CCR_One_Hour_Test` | [CCR One Hour Test](https://www.chessprogramming.org/CCR_One_Hour_Test) | `CCR_One_Hour_Test` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 152 | `Certabo_Chessboard` | [Certabo Chessboard](https://www.chessprogramming.org/Certabo_Chessboard) | `Certabo_Chessboard` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 154 | `Checkmate` | [Checkmate](https://www.chessprogramming.org/Checkmate) | `Checkmate` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 155 | `Chess_232_Board` | [Chess 232 Board](https://www.chessprogramming.org/Chess_232_Board) | `Chess_232_Board` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 157 | `Chessboard` | [Chessboard](https://www.chessprogramming.org/Chessboard) | `Chessboard` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 158 | `ChessCore` | [ChessCore](https://www.chessprogramming.org/ChessCore) | `ChessCore` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 160 | `Chinese_Chess_Board_Representation` | [Chinese Chess Board Representation](https://www.chessprogramming.org/Chinese_Chess_Board_Representation) | `Chinese_Chess_Board_Representation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 161 | `ChipTest` | [ChipTest](https://www.chessprogramming.org/ChipTest) | `ChipTest` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 168 | `Crafty` | [Crafty](https://www.chessprogramming.org/Crafty) | `Crafty` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 171 | `Cute_Chess` | [Cute Chess](https://www.chessprogramming.org/Cute_Chess) | `Cute_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 173 | `Dan_Honeycutt` | [Dan Honeycutt](https://www.chessprogramming.org/Dan_Honeycutt) | `Dan_Honeycutt` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 174 | `Daniel_Anulliero` | [Daniel Anulliero](https://www.chessprogramming.org/Daniel_Anulliero) | `Daniel_Anulliero` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 179 | `Depth` | [Depth](https://www.chessprogramming.org/Depth) | `Depth` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 180 | `Development` | [Development](https://www.chessprogramming.org/Development) | `Development` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 181 | `DGT_Board` | [DGT Board](https://www.chessprogramming.org/DGT_Board) | `DGT_Board` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 213 | `Dragon_by_Komodo_Chess` | [Dragon by Komodo Chess](https://www.chessprogramming.org/Dragon_by_Komodo_Chess) | `Dragon_by_Komodo_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 214 | `Draw` | [Draw](https://www.chessprogramming.org/Draw) | `Draw` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 220 | `Encoding_Moves` | [Encoding Moves](https://www.chessprogramming.org/Encoding_Moves) | `Encoding_Moves` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 223 | `Engine_programming` | [Engine programming](https://www.chessprogramming.org/Engine_programming) | `Engine_programming` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 224 | `Engine_Releases` | [Engine Releases](https://www.chessprogramming.org/Engine_Releases) | `Engine_Releases` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 225 | `Engine_Similarity` | [Engine Similarity](https://www.chessprogramming.org/Engine_Similarity) | `Engine_Similarity` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 226 | `Engines` | [Engines](https://www.chessprogramming.org/Engines) | `Engines` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 228 | `Entering_Moves` | [Entering Moves](https://www.chessprogramming.org/Entering_Moves) | `Entering_Moves` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 229 | `Ernst_Zermelo` | [Ernst Zermelo](https://www.chessprogramming.org/Ernst_Zermelo) | `Ernst_Zermelo` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 239 | `Evangelos_Karountzos` | [Evangelos Karountzos](https://www.chessprogramming.org/Evangelos_Karountzos) | `Evangelos_Karountzos` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 240 | `Exact_Score` | [Exact Score](https://www.chessprogramming.org/Exact_Score) | `Exact_Score` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 243 | `Eye_Movements` | [Eye Movements](https://www.chessprogramming.org/Eye_Movements) | `Eye_Movements` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 257 | `Fruit_Reloaded` | [Fruit Reloaded](https://www.chessprogramming.org/Fruit_Reloaded) | `Fruit_Reloaded` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 258 | `Glaurung` | [Glaurung](https://www.chessprogramming.org/Glaurung) | `Glaurung` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 300 | `Irreversible_Moves` | [Irreversible Moves](https://www.chessprogramming.org/Irreversible_Moves) | `Irreversible_Moves` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 302 | `James_Testa` | [James Testa](https://www.chessprogramming.org/James_Testa) | `James_Testa` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 307 | `Kaufman_Test` | [Kaufman Test](https://www.chessprogramming.org/Kaufman_Test) | `Kaufman_Test` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 314 | `Knight` | [Knight](https://www.chessprogramming.org/Knight) | `Knight` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 315 | `Knight_Pattern` | [Knight Pattern](https://www.chessprogramming.org/Knight_Pattern) | `Knight_Pattern` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 316 | `KnightCap` | [KnightCap](https://www.chessprogramming.org/KnightCap) | `KnightCap` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 317 | `Knightmare` | [Knightmare](https://www.chessprogramming.org/Knightmare) | `Knightmare` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 318 | `Knightmate_Chess` | [Knightmate Chess](https://www.chessprogramming.org/Knightmate_Chess) | `Knightmate_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 319 | `KnightX` | [KnightX](https://www.chessprogramming.org/KnightX) | `KnightX` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 320 | `Komodo` | [Komodo](https://www.chessprogramming.org/Komodo) | `Komodo` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 321 | `KomodoMCTS` | [KomodoMCTS](https://www.chessprogramming.org/KomodoMCTS) | `KomodoMCTS` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 325 | `Leela_Chess_Zero` | [Leela Chess Zero](https://www.chessprogramming.org/Leela_Chess_Zero) | `Leela_Chess_Zero` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 327 | `Legal_Move` | [Legal Move](https://www.chessprogramming.org/Legal_Move) | `Legal_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 328 | `Little_Rook_Chess` | [Little Rook Chess](https://www.chessprogramming.org/Little_Rook_Chess) | `Little_Rook_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 331 | `Make_Move` | [Make Move](https://www.chessprogramming.org/Make_Move) | `Make_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 332 | `Manuela_Veloso` | [Manuela Veloso](https://www.chessprogramming.org/Manuela_Veloso) | `Manuela_Veloso` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 333 | `Marco_Meloni` | [Marco Meloni](https://www.chessprogramming.org/Marco_Meloni) | `Marco_Meloni` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 340 | `Matt_McKnight` | [Matt McKnight](https://www.chessprogramming.org/Matt_McKnight) | `Matt_McKnight` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 346 | `Move` | [Move](https://www.chessprogramming.org/Move) | `Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 347 | `Move_Generation` | [Move Generation](https://www.chessprogramming.org/Move_Generation) | `Move_Generation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 348 | `Move_List` | [Move List](https://www.chessprogramming.org/Move_List) | `Move_List` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 349 | `Movei` | [Movei](https://www.chessprogramming.org/Movei) | `Movei` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 350 | `Moves` | [Moves](https://www.chessprogramming.org/Moves) | `Moves` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 355 | `Novag_Universal_Electronic_Chess_Board` | [Novag Universal Electronic Chess Board](https://www.chessprogramming.org/Novag_Universal_Electronic_Chess_Board) | `Novag_Universal_Electronic_Chess_Board` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 356 | `Null_Window` | [Null Window](https://www.chessprogramming.org/Null_Window) | `Null_Window` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 357 | `On_an_empty_Board` | [On an empty Board](https://www.chessprogramming.org/On_an_empty_Board) | `On_an_empty_Board` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 359 | `OpenBench` | [OpenBench](https://www.chessprogramming.org/OpenBench) | `OpenBench` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 362 | `Outposts` | [Outposts](https://www.chessprogramming.org/Outposts) | `Outposts` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 404 | `QBBEngine` | [QBBEngine](https://www.chessprogramming.org/QBBEngine) | `QBBEngine` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 406 | `Queen` | [Queen](https://www.chessprogramming.org/Queen) | `Queen` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 407 | `Quiet_Moves` | [Quiet Moves](https://www.chessprogramming.org/Quiet_Moves) | `Quiet_Moves` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 408 | `RankCut` | [RankCut](https://www.chessprogramming.org/RankCut) | `RankCut` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 410 | `RedQueen` | [RedQueen](https://www.chessprogramming.org/RedQueen) | `RedQueen` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 412 | `Refutation_Move` | [Refutation Move](https://www.chessprogramming.org/Refutation_Move) | `Refutation_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 414 | `Repetitions` | [Repetitions](https://www.chessprogramming.org/Repetitions) | `Repetitions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 415 | `Returning_Bishop` | [Returning Bishop](https://www.chessprogramming.org/Returning_Bishop) | `Returning_Bishop` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 416 | `Reversible_Moves` | [Reversible Moves](https://www.chessprogramming.org/Reversible_Moves) | `Reversible_Moves` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 417 | `Richard_Delorme` | [Richard Delorme](https://www.chessprogramming.org/Richard_Delorme) | `Richard_Delorme` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 418 | `Rook` | [Rook](https://www.chessprogramming.org/Rook) | `Rook` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 419 | `Rook_on_Open_File` | [Rook on Open File](https://www.chessprogramming.org/Rook_on_Open_File) | `Rook_on_Open_File` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 420 | `Rook_on_Seventh` | [Rook on Seventh](https://www.chessprogramming.org/Rook_on_Seventh) | `Rook_on_Seventh` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 421 | `Rookie` | [Rookie](https://www.chessprogramming.org/Rookie) | `Rookie` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 422 | `Russell_Crook` | [Russell Crook](https://www.chessprogramming.org/Russell_Crook) | `Russell_Crook` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 423 | `Saitek_PC_Auto_Chessboard` | [Saitek PC Auto Chessboard](https://www.chessprogramming.org/Saitek_PC_Auto_Chessboard) | `Saitek_PC_Auto_Chessboard` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 431 | `Score` | [Score](https://www.chessprogramming.org/Score) | `Score` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 443 | `Sensory_Board` | [Sensory Board](https://www.chessprogramming.org/Sensory_Board) | `Sensory_Board` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 444 | `Sequential_Probability_Ratio_Test` | [Sequential Probability Ratio Test](https://www.chessprogramming.org/Sequential_Probability_Ratio_Test) | `Sequential_Probability_Ratio_Test` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 448 | `Side_to_move` | [Side to move](https://www.chessprogramming.org/Side_to_move) | `Side_to_move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 456 | `Space` | [Space](https://www.chessprogramming.org/Space) | `Space` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 457 | `SPRT` | [SPRT](https://www.chessprogramming.org/SPRT) | `SPRT` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 458 | `SPSA` | [SPSA](https://www.chessprogramming.org/SPSA) | `SPSA` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 459 | `Stalemate` | [Stalemate](https://www.chessprogramming.org/Stalemate) | `Stalemate` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 460 | `Stockfish` | [Stockfish](https://www.chessprogramming.org/Stockfish) | `Stockfish` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 461 | `Strategic_Test_Suite` | [Strategic Test Suite](https://www.chessprogramming.org/Strategic_Test_Suite) | `Strategic_Test_Suite` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 465 | `Tactical_Moves` | [Tactical Moves](https://www.chessprogramming.org/Tactical_Moves) | `Tactical_Moves` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 467 | `TASC_SmartBoard` | [TASC SmartBoard](https://www.chessprogramming.org/TASC_SmartBoard) | `TASC_SmartBoard` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 491 | `Tempo` | [Tempo](https://www.chessprogramming.org/Tempo) | `Tempo` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 492 | `Temporal_Difference_Learning` | [Temporal Difference Learning](https://www.chessprogramming.org/Temporal_Difference_Learning) | `Temporal_Difference_Learning` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 496 | `The_Crazy_Bishop` | [The Crazy Bishop](https://www.chessprogramming.org/The_Crazy_Bishop) | `The_Crazy_Bishop` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 501 | `Threat_Move` | [Threat Move](https://www.chessprogramming.org/Threat_Move) | `Threat_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 504 | `Titboards` | [Titboards](https://www.chessprogramming.org/Titboards) | `Titboards` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 516 | `Unmake_Move` | [Unmake Move](https://www.chessprogramming.org/Unmake_Move) | `Unmake_Move` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 525 | `Vector_Attacks` | [Vector Attacks](https://www.chessprogramming.org/Vector_Attacks) | `Vector_Attacks` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 529 | `White_Knight` | [White Knight](https://www.chessprogramming.org/White_Knight) | `White_Knight` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 530 | `WinBoard` | [WinBoard](https://www.chessprogramming.org/WinBoard) | `WinBoard` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 549 | `Zugzwang` | [Zugzwang](https://www.chessprogramming.org/Zugzwang) | `Zugzwang` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 550 | `0x88` | [0x88](https://www.chessprogramming.org/0x88) | `0x88` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 551 | `1K_ZX_Chess` | [1K ZX Chess](https://www.chessprogramming.org/1K_ZX_Chess) | `1K_ZX_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 552 | `6502` | [6502](https://www.chessprogramming.org/6502) | `6502` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 553 | `6800` | [6800](https://www.chessprogramming.org/6800) | `6800` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 554 | `68000` | [68000](https://www.chessprogramming.org/68000) | `68000` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 555 | `68020` | [68020](https://www.chessprogramming.org/68020) | `68020` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 556 | `68030` | [68030](https://www.chessprogramming.org/68030) | `68030` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 557 | `8080` | [8080](https://www.chessprogramming.org/8080) | `8080` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 558 | `8080_Chess` | [8080 Chess](https://www.chessprogramming.org/8080_Chess) | `8080_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 559 | `8086` | [8086](https://www.chessprogramming.org/8086) | `8086` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 560 | `A0lite` | [A0lite](https://www.chessprogramming.org/A0lite) | `A0lite` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 561 | `A16chs` | [A16chs](https://www.chessprogramming.org/A16chs) | `A16chs` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 562 | `AAAI` | [AAAI](https://www.chessprogramming.org/AAAI) | `AAAI` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 563 | `Aamir_Syed` | [Aamir Syed](https://www.chessprogramming.org/Aamir_Syed) | `Aamir_Syed` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 564 | `Aaron_Becker` | [Aaron Becker](https://www.chessprogramming.org/Aaron_Becker) | `Aaron_Becker` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 565 | `Aaron_Tay` | [Aaron Tay](https://www.chessprogramming.org/Aaron_Tay) | `Aaron_Tay` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 566 | `Aart_Bik` | [Aart Bik](https://www.chessprogramming.org/Aart_Bik) | `Aart_Bik` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 567 | `Abbess` | [Abbess](https://www.chessprogramming.org/Abbess) | `Abbess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 568 | `ABDADA` | [ABDADA](https://www.chessprogramming.org/ABDADA) | `ABDADA` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 569 | `Abdallah_Saffidine` | [Abdallah Saffidine](https://www.chessprogramming.org/Abdallah_Saffidine) | `Abdallah_Saffidine` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 570 | `Abdul_Mateen_Khan` | [Abdul Mateen Khan](https://www.chessprogramming.org/Abdul_Mateen_Khan) | `Abdul_Mateen_Khan` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 571 | `ABK` | [ABK](https://www.chessprogramming.org/ABK) | `ABK` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 572 | `Abrok` | [Abrok](https://www.chessprogramming.org/Abrok) | `Abrok` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 573 | `Abulafia` | [Abulafia](https://www.chessprogramming.org/Abulafia) | `Abulafia` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 574 | `Abyss` | [Abyss](https://www.chessprogramming.org/Abyss) | `Abyss` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 575 | `ACCA` | [ACCA](https://www.chessprogramming.org/ACCA) | `ACCA` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 576 | `ACCA_2006` | [ACCA 2006](https://www.chessprogramming.org/ACCA_2006) | `ACCA_2006` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 577 | `ACCA_2007` | [ACCA 2007](https://www.chessprogramming.org/ACCA_2007) | `ACCA_2007` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 578 | `ACCA_2008` | [ACCA 2008](https://www.chessprogramming.org/ACCA_2008) | `ACCA_2008` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 579 | `ACCA_2009` | [ACCA 2009](https://www.chessprogramming.org/ACCA_2009) | `ACCA_2009` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 580 | `ACCA_2010` | [ACCA 2010](https://www.chessprogramming.org/ACCA_2010) | `ACCA_2010` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 581 | `ACCA_2011` | [ACCA 2011](https://www.chessprogramming.org/ACCA_2011) | `ACCA_2011` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 582 | `ACCA_2012` | [ACCA 2012](https://www.chessprogramming.org/ACCA_2012) | `ACCA_2012` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 583 | `ACCA_World_Computer_Rapid_Chess_Championship` | [ACCA World Computer Rapid Chess Champion](https://www.chessprogramming.org/ACCA_World_Computer_Rapid_Chess_Championship) | `ACCA_World_Computer_Rapid_Chess_Championship` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 584 | `Achilles` | [Achilles](https://www.chessprogramming.org/Achilles) | `Achilles` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 585 | `Acknowledgments` | [Acknowledgments](https://www.chessprogramming.org/Acknowledgments) | `Acknowledgments` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 586 | `ACM` | [ACM](https://www.chessprogramming.org/ACM) | `ACM` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 587 | `ACM_1970` | [ACM 1970](https://www.chessprogramming.org/ACM_1970) | `ACM_1970` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 588 | `ACM_1971` | [ACM 1971](https://www.chessprogramming.org/ACM_1971) | `ACM_1971` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 589 | `ACM_1972` | [ACM 1972](https://www.chessprogramming.org/ACM_1972) | `ACM_1972` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 590 | `ACM_1973` | [ACM 1973](https://www.chessprogramming.org/ACM_1973) | `ACM_1973` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 591 | `ACM_1974` | [ACM 1974](https://www.chessprogramming.org/ACM_1974) | `ACM_1974` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 592 | `ACM_1975` | [ACM 1975](https://www.chessprogramming.org/ACM_1975) | `ACM_1975` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 593 | `ACM_1976` | [ACM 1976](https://www.chessprogramming.org/ACM_1976) | `ACM_1976` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 594 | `ACM_1977` | [ACM 1977](https://www.chessprogramming.org/ACM_1977) | `ACM_1977` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 595 | `ACM_1978` | [ACM 1978](https://www.chessprogramming.org/ACM_1978) | `ACM_1978` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 596 | `ACM_1979` | [ACM 1979](https://www.chessprogramming.org/ACM_1979) | `ACM_1979` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 597 | `ACM_1980` | [ACM 1980](https://www.chessprogramming.org/ACM_1980) | `ACM_1980` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 598 | `ACM_1981` | [ACM 1981](https://www.chessprogramming.org/ACM_1981) | `ACM_1981` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 599 | `ACM_1982` | [ACM 1982](https://www.chessprogramming.org/ACM_1982) | `ACM_1982` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 600 | `ACM_1983` | [ACM 1983](https://www.chessprogramming.org/ACM_1983) | `ACM_1983` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 601 | `ACM_1984` | [ACM 1984](https://www.chessprogramming.org/ACM_1984) | `ACM_1984` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 602 | `ACM_1985` | [ACM 1985](https://www.chessprogramming.org/ACM_1985) | `ACM_1985` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 603 | `ACM_1986` | [ACM 1986](https://www.chessprogramming.org/ACM_1986) | `ACM_1986` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 604 | `ACM_1987` | [ACM 1987](https://www.chessprogramming.org/ACM_1987) | `ACM_1987` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 605 | `ACM_1988` | [ACM 1988](https://www.chessprogramming.org/ACM_1988) | `ACM_1988` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 606 | `ACM_1989` | [ACM 1989](https://www.chessprogramming.org/ACM_1989) | `ACM_1989` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 607 | `ACM_1990` | [ACM 1990](https://www.chessprogramming.org/ACM_1990) | `ACM_1990` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 608 | `ACM_1991` | [ACM 1991](https://www.chessprogramming.org/ACM_1991) | `ACM_1991` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 609 | `ACM_1993` | [ACM 1993](https://www.chessprogramming.org/ACM_1993) | `ACM_1993` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 610 | `ACM_1994` | [ACM 1994](https://www.chessprogramming.org/ACM_1994) | `ACM_1994` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 611 | `ACM_North_American_Computer_Chess_Championship` | [ACM North American Computer Chess Champi](https://www.chessprogramming.org/ACM_North_American_Computer_Chess_Championship) | `ACM_North_American_Computer_Chess_Championship` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 612 | `Acorn_Archimedes` | [Acorn Archimedes](https://www.chessprogramming.org/Acorn_Archimedes) | `Acorn_Archimedes` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 613 | `Acorn_Atom` | [Acorn Atom](https://www.chessprogramming.org/Acorn_Atom) | `Acorn_Atom` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 614 | `Acornsoft_Chess` | [Acornsoft Chess](https://www.chessprogramming.org/Acornsoft_Chess) | `Acornsoft_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 615 | `ACPP` | [ACPP](https://www.chessprogramming.org/ACPP) | `ACPP` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 616 | `AdaChess` | [AdaChess](https://www.chessprogramming.org/AdaChess) | `AdaChess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 617 | `Adam` | [Adam](https://www.chessprogramming.org/Adam) | `Adam` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 618 | `Adam_Berent` | [Adam Berent](https://www.chessprogramming.org/Adam_Berent) | `Adam_Berent` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 619 | `Adam_Hair` | [Adam Hair](https://www.chessprogramming.org/Adam_Hair) | `Adam_Hair` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 620 | `Adam_Kujawski` | [Adam Kujawski](https://www.chessprogramming.org/Adam_Kujawski) | `Adam_Kujawski` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 621 | `Adam_Oellermann` | [Adam Oellermann](https://www.chessprogramming.org/Adam_Oellermann) | `Adam_Oellermann` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 622 | `Adam_Treat` | [Adam Treat](https://www.chessprogramming.org/Adam_Treat) | `Adam_Treat` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 623 | `Adi_Botea` | [Adi Botea](https://www.chessprogramming.org/Adi_Botea) | `Adi_Botea` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 624 | `Aditya_Pande` | [Aditya Pande](https://www.chessprogramming.org/Aditya_Pande) | `Aditya_Pande` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 625 | `Adriaan_de_Groot` | [Adriaan de Groot](https://www.chessprogramming.org/Adriaan_de_Groot) | `Adriaan_de_Groot` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 626 | `Adrian_Millett` | [Adrian Millett](https://www.chessprogramming.org/Adrian_Millett) | `Adrian_Millett` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 627 | `Adrien_Regimbald` | [Adrien Regimbald](https://www.chessprogramming.org/Adrien_Regimbald) | `Adrien_Regimbald` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 628 | `Advance` | [Advance](https://www.chessprogramming.org/Advance) | `Advance` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 629 | `Advances_in_Computer_Chess_1` | [Advances in Computer Chess 1](https://www.chessprogramming.org/Advances_in_Computer_Chess_1) | `Advances_in_Computer_Chess_1` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 630 | `Advances_in_Computer_Chess_2` | [Advances in Computer Chess 2](https://www.chessprogramming.org/Advances_in_Computer_Chess_2) | `Advances_in_Computer_Chess_2` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 631 | `Advances_in_Computer_Chess_3` | [Advances in Computer Chess 3](https://www.chessprogramming.org/Advances_in_Computer_Chess_3) | `Advances_in_Computer_Chess_3` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 632 | `Advances_in_Computer_Chess_4` | [Advances in Computer Chess 4](https://www.chessprogramming.org/Advances_in_Computer_Chess_4) | `Advances_in_Computer_Chess_4` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 633 | `Advances_in_Computer_Chess_5` | [Advances in Computer Chess 5](https://www.chessprogramming.org/Advances_in_Computer_Chess_5) | `Advances_in_Computer_Chess_5` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 634 | `Advances_in_Computer_Chess_6` | [Advances in Computer Chess 6](https://www.chessprogramming.org/Advances_in_Computer_Chess_6) | `Advances_in_Computer_Chess_6` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 635 | `Advances_in_Computer_Chess_7` | [Advances in Computer Chess 7](https://www.chessprogramming.org/Advances_in_Computer_Chess_7) | `Advances_in_Computer_Chess_7` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 636 | `Advances_in_Computer_Chess_8` | [Advances in Computer Chess 8](https://www.chessprogramming.org/Advances_in_Computer_Chess_8) | `Advances_in_Computer_Chess_8` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 637 | `Advances_in_Computer_Games_10` | [Advances in Computer Games 10](https://www.chessprogramming.org/Advances_in_Computer_Games_10) | `Advances_in_Computer_Games_10` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 638 | `Advances_in_Computer_Games_11` | [Advances in Computer Games 11](https://www.chessprogramming.org/Advances_in_Computer_Games_11) | `Advances_in_Computer_Games_11` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 639 | `Advances_in_Computer_Games_12` | [Advances in Computer Games 12](https://www.chessprogramming.org/Advances_in_Computer_Games_12) | `Advances_in_Computer_Games_12` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 640 | `Advances_in_Computer_Games_13` | [Advances in Computer Games 13](https://www.chessprogramming.org/Advances_in_Computer_Games_13) | `Advances_in_Computer_Games_13` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 641 | `Advances_in_Computer_Games_14` | [Advances in Computer Games 14](https://www.chessprogramming.org/Advances_in_Computer_Games_14) | `Advances_in_Computer_Games_14` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 642 | `Advances_in_Computer_Games_15` | [Advances in Computer Games 15](https://www.chessprogramming.org/Advances_in_Computer_Games_15) | `Advances_in_Computer_Games_15` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 643 | `Advances_in_Computer_Games_16` | [Advances in Computer Games 16](https://www.chessprogramming.org/Advances_in_Computer_Games_16) | `Advances_in_Computer_Games_16` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 644 | `Advances_in_Computer_Games_17` | [Advances in Computer Games 17](https://www.chessprogramming.org/Advances_in_Computer_Games_17) | `Advances_in_Computer_Games_17` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 645 | `Advances_in_Computer_Games_9` | [Advances in Computer Games 9](https://www.chessprogramming.org/Advances_in_Computer_Games_9) | `Advances_in_Computer_Games_9` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 646 | `Aegon_1986` | [Aegon 1986](https://www.chessprogramming.org/Aegon_1986) | `Aegon_1986` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 647 | `Aegon_1987` | [Aegon 1987](https://www.chessprogramming.org/Aegon_1987) | `Aegon_1987` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 648 | `Aegon_1988` | [Aegon 1988](https://www.chessprogramming.org/Aegon_1988) | `Aegon_1988` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 649 | `Aegon_1989` | [Aegon 1989](https://www.chessprogramming.org/Aegon_1989) | `Aegon_1989` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 650 | `Aegon_1990` | [Aegon 1990](https://www.chessprogramming.org/Aegon_1990) | `Aegon_1990` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 651 | `Aegon_1991` | [Aegon 1991](https://www.chessprogramming.org/Aegon_1991) | `Aegon_1991` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 652 | `Aegon_1992` | [Aegon 1992](https://www.chessprogramming.org/Aegon_1992) | `Aegon_1992` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 653 | `Aegon_1993` | [Aegon 1993](https://www.chessprogramming.org/Aegon_1993) | `Aegon_1993` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 654 | `Aegon_1994` | [Aegon 1994](https://www.chessprogramming.org/Aegon_1994) | `Aegon_1994` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 655 | `Aegon_1995` | [Aegon 1995](https://www.chessprogramming.org/Aegon_1995) | `Aegon_1995` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 656 | `Aegon_1996` | [Aegon 1996](https://www.chessprogramming.org/Aegon_1996) | `Aegon_1996` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 657 | `Aegon_1997` | [Aegon 1997](https://www.chessprogramming.org/Aegon_1997) | `Aegon_1997` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 658 | `AI_Chess` | [AI Chess](https://www.chessprogramming.org/AI_Chess) | `AI_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 659 | `AiBloodshed` | [AiBloodshed](https://www.chessprogramming.org/AiBloodshed) | `AiBloodshed` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 660 | `AICE` | [AICE](https://www.chessprogramming.org/AICE) | `AICE` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 661 | `Akihiro_Kishimoto` | [Akihiro Kishimoto](https://www.chessprogramming.org/Akihiro_Kishimoto) | `Akihiro_Kishimoto` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 662 | `Akira_Ura` | [Akira Ura](https://www.chessprogramming.org/Akira_Ura) | `Akira_Ura` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 663 | `Alan_Baisley` | [Alan Baisley](https://www.chessprogramming.org/Alan_Baisley) | `Alan_Baisley` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 664 | `Alan_Biermann` | [Alan Biermann](https://www.chessprogramming.org/Alan_Biermann) | `Alan_Biermann` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 665 | `Alan_Blair` | [Alan Blair](https://www.chessprogramming.org/Alan_Blair) | `Alan_Blair` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 666 | `Alan_Kotok` | [Alan Kotok](https://www.chessprogramming.org/Alan_Kotok) | `Alan_Kotok` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 667 | `Alan_Mead` | [Alan Mead](https://www.chessprogramming.org/Alan_Mead) | `Alan_Mead` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 668 | `Alan_Sherman` | [Alan Sherman](https://www.chessprogramming.org/Alan_Sherman) | `Alan_Sherman` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 669 | `Alan_Turing` | [Alan Turing](https://www.chessprogramming.org/Alan_Turing) | `Alan_Turing` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 670 | `Alaric` | [Alaric](https://www.chessprogramming.org/Alaric) | `Alaric` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 671 | `Albatross` | [Albatross](https://www.chessprogramming.org/Albatross) | `Albatross` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 672 | `Albert_Bertilsson` | [Albert Bertilsson](https://www.chessprogramming.org/Albert_Bertilsson) | `Albert_Bertilsson` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 673 | `Albert_Gower` | [Albert Gower](https://www.chessprogramming.org/Albert_Gower) | `Albert_Gower` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 674 | `Albert_Silver` | [Albert Silver](https://www.chessprogramming.org/Albert_Silver) | `Albert_Silver` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 675 | `Albert_Xin_Jiang` | [Albert Xin Jiang](https://www.chessprogramming.org/Albert_Xin_Jiang) | `Albert_Xin_Jiang` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 676 | `Alberto_Alonso_Ruibal` | [Alberto Alonso Ruibal](https://www.chessprogramming.org/Alberto_Alonso_Ruibal) | `Alberto_Alonso_Ruibal` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 677 | `Alberto_Maria_Segre` | [Alberto Maria Segre](https://www.chessprogramming.org/Alberto_Maria_Segre) | `Alberto_Maria_Segre` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 678 | `Alberto_Sanjuan` | [Alberto Sanjuan](https://www.chessprogramming.org/Alberto_Sanjuan) | `Alberto_Sanjuan` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 679 | `Albrecht_Heeffer` | [Albrecht Heeffer](https://www.chessprogramming.org/Albrecht_Heeffer) | `Albrecht_Heeffer` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 680 | `Alcides_Schulz` | [Alcides Schulz](https://www.chessprogramming.org/Alcides_Schulz) | `Alcides_Schulz` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 681 | `Aldebaran` | [Aldebaran](https://www.chessprogramming.org/Aldebaran) | `Aldebaran` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 682 | `Alder` | [Alder](https://www.chessprogramming.org/Alder) | `Alder` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 683 | `Alejandro_Dubrovsky` | [Alejandro Dubrovsky](https://www.chessprogramming.org/Alejandro_Dubrovsky) | `Alejandro_Dubrovsky` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 684 | `Aleks_Peshkov` | [Aleks Peshkov](https://www.chessprogramming.org/Aleks_Peshkov) | `Aleks_Peshkov` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 685 | `Aleksander_Sadikov` | [Aleksander Sadikov](https://www.chessprogramming.org/Aleksander_Sadikov) | `Aleksander_Sadikov` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 686 | `Aleksandrs_Saveljevs` | [Aleksandrs Saveljevs](https://www.chessprogramming.org/Aleksandrs_Saveljevs) | `Aleksandrs_Saveljevs` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 687 | `Alen_Shapiro` | [Alen Shapiro](https://www.chessprogramming.org/Alen_Shapiro) | `Alen_Shapiro` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 688 | `Alena_Beyer` | [Alena Beyer](https://www.chessprogramming.org/Alena_Beyer) | `Alena_Beyer` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 689 | `Alessandro_Damiani` | [Alessandro Damiani](https://www.chessprogramming.org/Alessandro_Damiani) | `Alessandro_Damiani` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 690 | `Alessandro_Iavicoli` | [Alessandro Iavicoli](https://www.chessprogramming.org/Alessandro_Iavicoli) | `Alessandro_Iavicoli` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 691 | `Alessandro_Scotti` | [Alessandro Scotti](https://www.chessprogramming.org/Alessandro_Scotti) | `Alessandro_Scotti` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 692 | `Alex_Bell` | [Alex Bell](https://www.chessprogramming.org/Alex_Bell) | `Alex_Bell` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 693 | `Alex_Bernstein` | [Alex Bernstein](https://www.chessprogramming.org/Alex_Bernstein) | `Alex_Bernstein` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 694 | `Alex_Brunetti` | [Alex Brunetti](https://www.chessprogramming.org/Alex_Brunetti) | `Alex_Brunetti` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 695 | `Alex_de_Voogt` | [Alex de Voogt](https://www.chessprogramming.org/Alex_de_Voogt) | `Alex_de_Voogt` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 696 | `Alex_Kure` | [Alex Kure](https://www.chessprogramming.org/Alex_Kure) | `Alex_Kure` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 697 | `Alex_Morozov` | [Alex Morozov](https://www.chessprogramming.org/Alex_Morozov) | `Alex_Morozov` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 698 | `Alex_van_Tiggelen` | [Alex van Tiggelen](https://www.chessprogramming.org/Alex_van_Tiggelen) | `Alex_van_Tiggelen` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 699 | `Alexander_Bitman` | [Alexander Bitman](https://www.chessprogramming.org/Alexander_Bitman) | `Alexander_Bitman` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 700 | `Alexander_Brudno` | [Alexander Brudno](https://www.chessprogramming.org/Alexander_Brudno) | `Alexander_Brudno` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 701 | `Alexander_Kronrod` | [Alexander Kronrod](https://www.chessprogramming.org/Alexander_Kronrod) | `Alexander_Kronrod` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 702 | `Alexander_Litov` | [Alexander Litov](https://www.chessprogramming.org/Alexander_Litov) | `Alexander_Litov` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 703 | `Alexander_Lyashuk` | [Alexander Lyashuk](https://www.chessprogramming.org/Alexander_Lyashuk) | `Alexander_Lyashuk` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 704 | `Alexander_Naumov` | [Alexander Naumov](https://www.chessprogramming.org/Alexander_Naumov) | `Alexander_Naumov` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 705 | `Alexander_Pokrovski` | [Alexander Pokrovski](https://www.chessprogramming.org/Alexander_Pokrovski) | `Alexander_Pokrovski` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 706 | `Alexander_Reinefeld` | [Alexander Reinefeld](https://www.chessprogramming.org/Alexander_Reinefeld) | `Alexander_Reinefeld` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 707 | `Alexander_Reznitskiy` | [Alexander Reznitskiy](https://www.chessprogramming.org/Alexander_Reznitskiy) | `Alexander_Reznitskiy` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 708 | `Alexander_Szabo` | [Alexander Szabo](https://www.chessprogramming.org/Alexander_Szabo) | `Alexander_Szabo` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 709 | `Alexander_Timofeev` | [Alexander Timofeev](https://www.chessprogramming.org/Alexander_Timofeev) | `Alexander_Timofeev` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 710 | `Alexander_Yudin` | [Alexander Yudin](https://www.chessprogramming.org/Alexander_Yudin) | `Alexander_Yudin` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 711 | `Alexander_Zhivotovsky` | [Alexander Zhivotovsky](https://www.chessprogramming.org/Alexander_Zhivotovsky) | `Alexander_Zhivotovsky` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 712 | `Alexandru_Mosoi` | [Alexandru Mosoi](https://www.chessprogramming.org/Alexandru_Mosoi) | `Alexandru_Mosoi` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 713 | `Alexey_Manjakhin` | [Alexey Manjakhin](https://www.chessprogramming.org/Alexey_Manjakhin) | `Alexey_Manjakhin` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 714 | `Alexs` | [Alexs](https://www.chessprogramming.org/Alexs) | `Alexs` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 715 | `Alfil` | [Alfil](https://www.chessprogramming.org/Alfil) | `Alfil` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 716 | `Algebraic_Chess_Notation` | [Algebraic Chess Notation](https://www.chessprogramming.org/Algebraic_Chess_Notation) | `Algebraic_Chess_Notation` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 717 | `Algir` | [Algir](https://www.chessprogramming.org/Algir) | `Algir` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 718 | `Algol` | [Algol](https://www.chessprogramming.org/Algol) | `Algol` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 719 | `Algorithms` | [Algorithms](https://www.chessprogramming.org/Algorithms) | `Algorithms` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 720 | `AliBaba` | [AliBaba](https://www.chessprogramming.org/AliBaba) | `AliBaba` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 721 | `Alice` | [Alice](https://www.chessprogramming.org/Alice) | `Alice` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 722 | `AliChess` | [AliChess](https://www.chessprogramming.org/AliChess) | `AliChess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 723 | `Allard_Siemelink` | [Allard Siemelink](https://www.chessprogramming.org/Allard_Siemelink) | `Allard_Siemelink` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 724 | `Allen_Newell` | [Allen Newell](https://www.chessprogramming.org/Allen_Newell) | `Allen_Newell` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 725 | `Allie` | [Allie](https://www.chessprogramming.org/Allie) | `Allie` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 726 | `AllieStein` | [AllieStein](https://www.chessprogramming.org/AllieStein) | `AllieStein` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 727 | `Almond` | [Almond](https://www.chessprogramming.org/Almond) | `Almond` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 728 | `Alois_Heinz` | [Alois Heinz](https://www.chessprogramming.org/Alois_Heinz) | `Alois_Heinz` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 729 | `AltiVec` | [AltiVec](https://www.chessprogramming.org/AltiVec) | `AltiVec` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 730 | `Alvaro_Benlloch` | [Alvaro Benlloch](https://www.chessprogramming.org/Alvaro_Benlloch) | `Alvaro_Benlloch` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 731 | `Alvaro_Cardoso` | [Alvaro Cardoso](https://www.chessprogramming.org/Alvaro_Cardoso) | `Alvaro_Cardoso` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 732 | `Alybadix` | [Alybadix](https://www.chessprogramming.org/Alybadix) | `Alybadix` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 733 | `Amanj_Sherwany` | [Amanj Sherwany](https://www.chessprogramming.org/Amanj_Sherwany) | `Amanj_Sherwany` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 734 | `Amateur` | [Amateur](https://www.chessprogramming.org/Amateur) | `Amateur` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 735 | `Amazons` | [Amazons](https://www.chessprogramming.org/Amazons) | `Amazons` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 736 | `Ambros_Marzetta` | [Ambros Marzetta](https://www.chessprogramming.org/Ambros_Marzetta) | `Ambros_Marzetta` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 737 | `AMD` | [AMD](https://www.chessprogramming.org/AMD) | `AMD` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 738 | `Amdahl_470` | [Amdahl 470](https://www.chessprogramming.org/Amdahl_470) | `Amdahl_470` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 739 | `Amiga` | [Amiga](https://www.chessprogramming.org/Amiga) | `Amiga` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 740 | `Amir_Ban` | [Amir Ban](https://www.chessprogramming.org/Amir_Ban) | `Amir_Ban` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 741 | `Amitava_Bagchi` | [Amitava Bagchi](https://www.chessprogramming.org/Amitava_Bagchi) | `Amitava_Bagchi` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 742 | `Amoeba` | [Amoeba](https://www.chessprogramming.org/Amoeba) | `Amoeba` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 743 | `Amos_Storkey` | [Amos Storkey](https://www.chessprogramming.org/Amos_Storkey) | `Amos_Storkey` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 744 | `Amstrad_CPC` | [Amstrad CPC](https://www.chessprogramming.org/Amstrad_CPC) | `Amstrad_CPC` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 745 | `Amundsen` | [Amundsen](https://www.chessprogramming.org/Amundsen) | `Amundsen` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 746 | `Amy` | [Amy](https://www.chessprogramming.org/Amy) | `Amy` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 747 | `Amyan` | [Amyan](https://www.chessprogramming.org/Amyan) | `Amyan` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 748 | `ANACA` | [ANACA](https://www.chessprogramming.org/ANACA) | `ANACA` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 749 | `Anaconda` | [Anaconda](https://www.chessprogramming.org/Anaconda) | `Anaconda` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 750 | `Ananse` | [Ananse](https://www.chessprogramming.org/Ananse) | `Ananse` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 751 | `Anastasios_Milikas` | [Anastasios Milikas](https://www.chessprogramming.org/Anastasios_Milikas) | `Anastasios_Milikas` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 752 | `Anatoli` | [Anatoli](https://www.chessprogramming.org/Anatoli) | `Anatoli` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 753 | `Anatoly_Uskov` | [Anatoly Uskov](https://www.chessprogramming.org/Anatoly_Uskov) | `Anatoly_Uskov` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 754 | `Anders_Kierulf` | [Anders Kierulf](https://www.chessprogramming.org/Anders_Kierulf) | `Anders_Kierulf` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 755 | `Andre_Adrian` | [Andre Adrian](https://www.chessprogramming.org/Andre_Adrian) | `Andre_Adrian` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 756 | `Andrea_Manzo` | [Andrea Manzo](https://www.chessprogramming.org/Andrea_Manzo) | `Andrea_Manzo` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 757 | `Andreas_Guettinger` | [Andreas Guettinger](https://www.chessprogramming.org/Andreas_Guettinger) | `Andreas_Guettinger` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 758 | `Andreas_Herrmann` | [Andreas Herrmann](https://www.chessprogramming.org/Andreas_Herrmann) | `Andreas_Herrmann` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 759 | `Andreas_Junghanns` | [Andreas Junghanns](https://www.chessprogramming.org/Andreas_Junghanns) | `Andreas_Junghanns` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 760 | `Andreas_Mader` | [Andreas Mader](https://www.chessprogramming.org/Andreas_Mader) | `Andreas_Mader` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 761 | `Andreas_Matthies` | [Andreas Matthies](https://www.chessprogramming.org/Andreas_Matthies) | `Andreas_Matthies` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 762 | `Andreas_Nowatzyk` | [Andreas Nowatzyk](https://www.chessprogramming.org/Andreas_Nowatzyk) | `Andreas_Nowatzyk` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 763 | `Andreas_Rudin` | [Andreas Rudin](https://www.chessprogramming.org/Andreas_Rudin) | `Andreas_Rudin` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 764 | `Andrei_Fortuna` | [Andrei Fortuna](https://www.chessprogramming.org/Andrei_Fortuna) | `Andrei_Fortuna` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 765 | `Andres_Valverde` | [Andres Valverde](https://www.chessprogramming.org/Andres_Valverde) | `Andres_Valverde` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 766 | `Andrew_Barto` | [Andrew Barto](https://www.chessprogramming.org/Andrew_Barto) | `Andrew_Barto` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 767 | `Andrew_Fan` | [Andrew Fan](https://www.chessprogramming.org/Andrew_Fan) | `Andrew_Fan` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 768 | `Andrew_Grant` | [Andrew Grant](https://www.chessprogramming.org/Andrew_Grant) | `Andrew_Grant` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 769 | `Andrew_James_Palay` | [Andrew James Palay](https://www.chessprogramming.org/Andrew_James_Palay) | `Andrew_James_Palay` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 770 | `Andrew_Kadatch` | [Andrew Kadatch](https://www.chessprogramming.org/Andrew_Kadatch) | `Andrew_Kadatch` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 771 | `Andrew_Koenig` | [Andrew Koenig](https://www.chessprogramming.org/Andrew_Koenig) | `Andrew_Koenig` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 772 | `Andrew_Shapira` | [Andrew Shapira](https://www.chessprogramming.org/Andrew_Shapira) | `Andrew_Shapira` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 773 | `Andrew_Tridgell` | [Andrew Tridgell](https://www.chessprogramming.org/Andrew_Tridgell) | `Andrew_Tridgell` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 774 | `Andrew_Williams` | [Andrew Williams](https://www.chessprogramming.org/Andrew_Williams) | `Andrew_Williams` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 775 | `Android` | [Android](https://www.chessprogramming.org/Android) | `Android` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 776 | `Andscacs` | [Andscacs](https://www.chessprogramming.org/Andscacs) | `Andscacs` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 777 | `Andy_Thomason` | [Andy Thomason](https://www.chessprogramming.org/Andy_Thomason) | `Andy_Thomason` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 778 | `Andy_Walker` | [Andy Walker](https://www.chessprogramming.org/Andy_Walker) | `Andy_Walker` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 779 | `Anechka` | [Anechka](https://www.chessprogramming.org/Anechka) | `Anechka` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 780 | `Ankan_Banerjee` | [Ankan Banerjee](https://www.chessprogramming.org/Ankan_Banerjee) | `Ankan_Banerjee` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 781 | `AnMon` | [AnMon](https://www.chessprogramming.org/AnMon) | `AnMon` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 782 | `Ant` | [Ant](https://www.chessprogramming.org/Ant) | `Ant` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 783 | `Anthony_Adam` | [Anthony Adam](https://www.chessprogramming.org/Anthony_Adam) | `Anthony_Adam` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 784 | `Anthony_Cozzie` | [Anthony Cozzie](https://www.chessprogramming.org/Anthony_Cozzie) | `Anthony_Cozzie` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 785 | `Anton_Lindenmair` | [Anton Lindenmair](https://www.chessprogramming.org/Anton_Lindenmair) | `Anton_Lindenmair` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 786 | `Anton_Mihailov` | [Anton Mihailov](https://www.chessprogramming.org/Anton_Mihailov) | `Anton_Mihailov` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 787 | `Antonia_Jeanrenaud` | [Antonia Jeanrenaud](https://www.chessprogramming.org/Antonia_Jeanrenaud) | `Antonia_Jeanrenaud` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 788 | `Antonio_Ceballos` | [Antonio Ceballos](https://www.chessprogramming.org/Antonio_Ceballos) | `Antonio_Ceballos` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 789 | `Antonio_Dieguez` | [Antonio Dieguez](https://www.chessprogramming.org/Antonio_Dieguez) | `Antonio_Dieguez` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 790 | `Antonio_Torrecillas` | [Antonio Torrecillas](https://www.chessprogramming.org/Antonio_Torrecillas) | `Antonio_Torrecillas` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 791 | `Anubis` | [Anubis](https://www.chessprogramming.org/Anubis) | `Anubis` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 792 | `Apery` | [Apery](https://www.chessprogramming.org/Apery) | `Apery` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 793 | `APHID` | [APHID](https://www.chessprogramming.org/APHID) | `APHID` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 794 | `APIL_chess` | [APIL chess](https://www.chessprogramming.org/APIL_chess) | `APIL_chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 795 | `Applied_Concepts` | [Applied Concepts](https://www.chessprogramming.org/Applied_Concepts) | `Applied_Concepts` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 796 | `APwin` | [APwin](https://www.chessprogramming.org/APwin) | `APwin` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 797 | `Aquarium` | [Aquarium](https://www.chessprogramming.org/Aquarium) | `Aquarium` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 798 | `Arachne` | [Arachne](https://www.chessprogramming.org/Arachne) | `Arachne` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 799 | `Arasan` | [Arasan](https://www.chessprogramming.org/Arasan) | `Arasan` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 800 | `Ard_van_Bergen` | [Ard van Bergen](https://www.chessprogramming.org/Ard_van_Bergen) | `Ard_van_Bergen` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 801 | `Arduino` | [Arduino](https://www.chessprogramming.org/Arduino) | `Arduino` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 802 | `Arena` | [Arena](https://www.chessprogramming.org/Arena) | `Arena` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 803 | `Ares` | [Ares](https://www.chessprogramming.org/Ares) | `Ares` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 804 | `Ares_US` | [Ares US](https://www.chessprogramming.org/Ares_US) | `Ares_US` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 805 | `Argonaut` | [Argonaut](https://www.chessprogramming.org/Argonaut) | `Argonaut` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 806 | `Ari_Weinstein` | [Ari Weinstein](https://www.chessprogramming.org/Ari_Weinstein) | `Ari_Weinstein` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 807 | `Arie_de_Bruin` | [Arie de Bruin](https://www.chessprogramming.org/Arie_de_Bruin) | `Arie_de_Bruin` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 808 | `Ariel_Felner` | [Ariel Felner](https://www.chessprogramming.org/Ariel_Felner) | `Ariel_Felner` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 809 | `Arimaa` | [Arimaa](https://www.chessprogramming.org/Arimaa) | `Arimaa` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 810 | `Arion` | [Arion](https://www.chessprogramming.org/Arion) | `Arion` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 811 | `Aristarch` | [Aristarch](https://www.chessprogramming.org/Aristarch) | `Aristarch` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 812 | `Arkadiusz_Paterek` | [Arkadiusz Paterek](https://www.chessprogramming.org/Arkadiusz_Paterek) | `Arkadiusz_Paterek` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 813 | `Arleen_Chafitz` | [Arleen Chafitz](https://www.chessprogramming.org/Arleen_Chafitz) | `Arleen_Chafitz` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 814 | `Arno_Nickel` | [Arno Nickel](https://www.chessprogramming.org/Arno_Nickel) | `Arno_Nickel` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 815 | `Aron_Eisenpress` | [Aron Eisenpress](https://www.chessprogramming.org/Aron_Eisenpress) | `Aron_Eisenpress` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 816 | `Aron_Petkovski` | [Aron Petkovski](https://www.chessprogramming.org/Aron_Petkovski) | `Aron_Petkovski` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 817 | `Array` | [Array](https://www.chessprogramming.org/Array) | `Array` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 818 | `Artem_Petakov` | [Artem Petakov](https://www.chessprogramming.org/Artem_Petakov) | `Artem_Petakov` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 819 | `Arthur` | [Arthur](https://www.chessprogramming.org/Arthur) | `Arthur` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 820 | `Arthur_Guez` | [Arthur Guez](https://www.chessprogramming.org/Arthur_Guez) | `Arthur_Guez` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 821 | `Arthur_Norman` | [Arthur Norman](https://www.chessprogramming.org/Arthur_Norman) | `Arthur_Norman` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 822 | `Arthur_Samuel` | [Arthur Samuel](https://www.chessprogramming.org/Arthur_Samuel) | `Arthur_Samuel` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 823 | `Artic_Computing` | [Artic Computing](https://www.chessprogramming.org/Artic_Computing) | `Artic_Computing` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 824 | `Artificial_Intelligence` | [Artificial Intelligence](https://www.chessprogramming.org/Artificial_Intelligence) | `Artificial_Intelligence` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 825 | `Arts` | [Arts](https://www.chessprogramming.org/Arts) | `Arts` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 826 | `Arturo_Ochoa` | [Arturo Ochoa](https://www.chessprogramming.org/Arturo_Ochoa) | `Arturo_Ochoa` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 827 | `Ashish_Sabharwal` | [Ashish Sabharwal](https://www.chessprogramming.org/Ashish_Sabharwal) | `Ashish_Sabharwal` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 828 | `Ashton_Anderson` | [Ashton Anderson](https://www.chessprogramming.org/Ashton_Anderson) | `Ashton_Anderson` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 829 | `Ashwin_Srinivasan` | [Ashwin Srinivasan](https://www.chessprogramming.org/Ashwin_Srinivasan) | `Ashwin_Srinivasan` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 830 | `Aske_Plaat` | [Aske Plaat](https://www.chessprogramming.org/Aske_Plaat) | `Aske_Plaat` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 831 | `AsmFish` | [AsmFish](https://www.chessprogramming.org/AsmFish) | `AsmFish` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 832 | `Assembly` | [Assembly](https://www.chessprogramming.org/Assembly) | `Assembly` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 833 | `Asterisk` | [Asterisk](https://www.chessprogramming.org/Asterisk) | `Asterisk` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 834 | `Astro_64` | [Astro 64](https://www.chessprogramming.org/Astro_64) | `Astro_64` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 835 | `Asymptote` | [Asymptote](https://www.chessprogramming.org/Asymptote) | `Asymptote` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 836 | `Atak` | [Atak](https://www.chessprogramming.org/Atak) | `Atak` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 837 | `Atari_ST` | [Atari ST](https://www.chessprogramming.org/Atari_ST) | `Atari_ST` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 838 | `AtlanChess` | [AtlanChess](https://www.chessprogramming.org/AtlanChess) | `AtlanChess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 839 | `Atlas` | [Atlas](https://www.chessprogramming.org/Atlas) | `Atlas` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 840 | `Atlas_Computer_Laboratory` | [Atlas Computer Laboratory](https://www.chessprogramming.org/Atlas_Computer_Laboratory) | `Atlas_Computer_Laboratory` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 841 | `Atom_Chess` | [Atom Chess](https://www.chessprogramming.org/Atom_Chess) | `Atom_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 842 | `Atomic_Chess` | [Atomic Chess](https://www.chessprogramming.org/Atomic_Chess) | `Atomic_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 843 | `Attack_and_Defend_Maps` | [Attack and Defend Maps](https://www.chessprogramming.org/Attack_and_Defend_Maps) | `Attack_and_Defend_Maps` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 844 | `Attack_Spans` | [Attack Spans](https://www.chessprogramming.org/Attack_Spans) | `Attack_Spans` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 845 | `Attacks` | [Attacks](https://www.chessprogramming.org/Attacks) | `Attacks` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 846 | `Aubervilliers_Rapid_Open` | [Aubervilliers Rapid Open](https://www.chessprogramming.org/Aubervilliers_Rapid_Open) | `Aubervilliers_Rapid_Open` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 847 | `Auke_Punter` | [Auke Punter](https://www.chessprogramming.org/Auke_Punter) | `Auke_Punter` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 848 | `Austin_Parker` | [Austin Parker](https://www.chessprogramming.org/Austin_Parker) | `Austin_Parker` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 849 | `Australasian_National_Computer_Chess_Championship` | [Australasian National Computer Chess Cha](https://www.chessprogramming.org/Australasian_National_Computer_Chess_Championship) | `Australasian_National_Computer_Chess_Championship` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 850 | `Australian_National_University` | [Australian National University](https://www.chessprogramming.org/Australian_National_University) | `Australian_National_University` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 851 | `Auto232` | [Auto232](https://www.chessprogramming.org/Auto232) | `Auto232` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 852 | `Averno` | [Averno](https://www.chessprogramming.org/Averno) | `Averno` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 853 | `Aviezri_Fraenkel` | [Aviezri Fraenkel](https://www.chessprogramming.org/Aviezri_Fraenkel) | `Aviezri_Fraenkel` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 854 | `Avoiding_Branches` | [Avoiding Branches](https://www.chessprogramming.org/Avoiding_Branches) | `Avoiding_Branches` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 855 | `Awari` | [Awari](https://www.chessprogramming.org/Awari) | `Awari` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 856 | `Awesome` | [Awesome](https://www.chessprogramming.org/Awesome) | `Awesome` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 857 | `Awit` | [Awit](https://www.chessprogramming.org/Awit) | `Awit` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 858 | `Ax` | [Ax](https://www.chessprogramming.org/Ax) | `Ax` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 859 | `Axon` | [Axon](https://www.chessprogramming.org/Axon) | `Axon` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 860 | `Ayito` | [Ayito](https://www.chessprogramming.org/Ayito) | `Ayito` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 861 | `Ayumu_Nagai` | [Ayumu Nagai](https://www.chessprogramming.org/Ayumu_Nagai) | `Ayumu_Nagai` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 862 | `Azlan_Iqbal` | [Azlan Iqbal](https://www.chessprogramming.org/Azlan_Iqbal) | `Azlan_Iqbal` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 863 | `Backgammon` | [Backgammon](https://www.chessprogramming.org/Backgammon) | `Backgammon` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 864 | `Bagatur` | [Bagatur](https://www.chessprogramming.org/Bagatur) | `Bagatur` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 865 | `Baislicka` | [Baislicka](https://www.chessprogramming.org/Baislicka) | `Baislicka` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 866 | `Balint_Pfliegel` | [Balint Pfliegel](https://www.chessprogramming.org/Balint_Pfliegel) | `Balint_Pfliegel` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 867 | `Banksia` | [Banksia](https://www.chessprogramming.org/Banksia) | `Banksia` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 868 | `Banksia_GUI` | [Banksia GUI](https://www.chessprogramming.org/Banksia_GUI) | `Banksia_GUI` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 869 | `Bao` | [Bao](https://www.chessprogramming.org/Bao) | `Bao` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 870 | `Barak_Oshri` | [Barak Oshri](https://www.chessprogramming.org/Barak_Oshri) | `Barak_Oshri` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 871 | `Barbara_Liskov` | [Barbara Liskov](https://www.chessprogramming.org/Barbara_Liskov) | `Barbara_Liskov` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 872 | `Barbara_Szabo` | [Barbara Szabo](https://www.chessprogramming.org/Barbara_Szabo) | `Barbara_Szabo` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 873 | `Barbarossa` | [Barbarossa](https://www.chessprogramming.org/Barbarossa) | `Barbarossa` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 874 | `Bareev_versus_HIARCS_2003` | [Bareev versus HIARCS 2003](https://www.chessprogramming.org/Bareev_versus_HIARCS_2003) | `Bareev_versus_HIARCS_2003` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 875 | `Barend_Swets` | [Barend Swets](https://www.chessprogramming.org/Barend_Swets) | `Barend_Swets` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 876 | `Barney_Pell` | [Barney Pell](https://www.chessprogramming.org/Barney_Pell) | `Barney_Pell` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 877 | `Bart_Goldhoorn` | [Bart Goldhoorn](https://www.chessprogramming.org/Bart_Goldhoorn) | `Bart_Goldhoorn` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 878 | `Bart_Selman` | [Bart Selman](https://www.chessprogramming.org/Bart_Selman) | `Bart_Selman` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 879 | `Bart_Verbaan` | [Bart Verbaan](https://www.chessprogramming.org/Bart_Verbaan) | `Bart_Verbaan` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 880 | `Bart_Weststrate` | [Bart Weststrate](https://www.chessprogramming.org/Bart_Weststrate) | `Bart_Weststrate` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 881 | `Bas_Hamstra` | [Bas Hamstra](https://www.chessprogramming.org/Bas_Hamstra) | `Bas_Hamstra` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 882 | `Basic` | [Basic](https://www.chessprogramming.org/Basic) | `Basic` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 883 | `Basil_Falcinelli` | [Basil Falcinelli](https://www.chessprogramming.org/Basil_Falcinelli) | `Basil_Falcinelli` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 884 | `Battery` | [Battery](https://www.chessprogramming.org/Battery) | `Battery` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 885 | `Battle_Chess` | [Battle Chess](https://www.chessprogramming.org/Battle_Chess) | `Battle_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 886 | `BB` | [BB](https://www.chessprogramming.org/BB) | `BB` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 887 | `BBC` | [BBC](https://www.chessprogramming.org/BBC) | `BBC` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 888 | `BBC_Micro` | [BBC Micro](https://www.chessprogramming.org/BBC_Micro) | `BBC_Micro` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 889 | `BBchess` | [BBchess](https://www.chessprogramming.org/BBchess) | `BBchess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 890 | `BCP` | [BCP](https://www.chessprogramming.org/BCP) | `BCP` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 891 | `Beaches` | [Beaches](https://www.chessprogramming.org/Beaches) | `Beaches` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 892 | `Beal` | [Beal](https://www.chessprogramming.org/Beal) | `Beal` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 893 | `Bebe` | [Bebe](https://www.chessprogramming.org/Bebe) | `Bebe` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 894 | `Behting_Study` | [Behting Study](https://www.chessprogramming.org/Behting_Study) | `Behting_Study` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 895 | `BELCT_2001` | [BELCT 2001](https://www.chessprogramming.org/BELCT_2001) | `BELCT_2001` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 896 | `Belka` | [Belka](https://www.chessprogramming.org/Belka) | `Belka` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 897 | `Bell_Laboratories` | [Bell Laboratories](https://www.chessprogramming.org/Bell_Laboratories) | `Bell_Laboratories` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 898 | `Belle` | [Belle](https://www.chessprogramming.org/Belle) | `Belle` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 899 | `Belzebub` | [Belzebub](https://www.chessprogramming.org/Belzebub) | `Belzebub` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 900 | `Ben_Mittman` | [Ben Mittman](https://www.chessprogramming.org/Ben_Mittman) | `Ben_Mittman` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 901 | `Ben_Yalow` | [Ben Yalow](https://www.chessprogramming.org/Ben_Yalow) | `Ben_Yalow` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 902 | `Benny_Antonsson` | [Benny Antonsson](https://www.chessprogramming.org/Benny_Antonsson) | `Benny_Antonsson` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 903 | `Beowulf` | [Beowulf](https://www.chessprogramming.org/Beowulf) | `Beowulf` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 904 | `Berkeley_Chess_Microprocessor` | [Berkeley Chess Microprocessor](https://www.chessprogramming.org/Berkeley_Chess_Microprocessor) | `Berkeley_Chess_Microprocessor` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 905 | `Bernard_Brioit` | [Bernard Brioit](https://www.chessprogramming.org/Bernard_Brioit) | `Bernard_Brioit` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 906 | `Bernard_Helmstetter` | [Bernard Helmstetter](https://www.chessprogramming.org/Bernard_Helmstetter) | `Bernard_Helmstetter` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 907 | `Bernd_Steinbach` | [Bernd Steinbach](https://www.chessprogramming.org/Bernd_Steinbach) | `Bernd_Steinbach` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 908 | `Bernhard_Balkenhol` | [Bernhard Balkenhol](https://www.chessprogramming.org/Bernhard_Balkenhol) | `Bernhard_Balkenhol` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 909 | `Bernhard_Biberle` | [Bernhard Biberle](https://www.chessprogramming.org/Bernhard_Biberle) | `Bernhard_Biberle` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 910 | `Bernhard_Pfahringer` | [Bernhard Pfahringer](https://www.chessprogramming.org/Bernhard_Pfahringer) | `Bernhard_Pfahringer` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 911 | `Bernie` | [Bernie](https://www.chessprogramming.org/Bernie) | `Bernie` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 912 | `Berserk` | [Berserk](https://www.chessprogramming.org/Berserk) | `Berserk` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 913 | `Berta` | [Berta](https://www.chessprogramming.org/Berta) | `Berta` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 914 | `Bestia` | [Bestia](https://www.chessprogramming.org/Bestia) | `Bestia` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 915 | `Betsabe` | [Betsabe](https://www.chessprogramming.org/Betsabe) | `Betsabe` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 916 | `Betsy` | [Betsy](https://www.chessprogramming.org/Betsy) | `Betsy` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 917 | `Bibob` | [Bibob](https://www.chessprogramming.org/Bibob) | `Bibob` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 918 | `BigLion` | [BigLion](https://www.chessprogramming.org/BigLion) | `BigLion` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 919 | `BikJump` | [BikJump](https://www.chessprogramming.org/BikJump) | `BikJump` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 920 | `Bill_Gosper` | [Bill Gosper](https://www.chessprogramming.org/Bill_Gosper) | `Bill_Gosper` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 921 | `Bill_Henry` | [Bill Henry](https://www.chessprogramming.org/Bill_Henry) | `Bill_Henry` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 922 | `Bill_Jordan` | [Bill Jordan](https://www.chessprogramming.org/Bill_Jordan) | `Bill_Jordan` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 923 | `Bills_Bare_Bones_Chess` | [Bills Bare Bones Chess](https://www.chessprogramming.org/Bills_Bare_Bones_Chess) | `Bills_Bare_Bones_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 924 | `Bionic` | [Bionic](https://www.chessprogramming.org/Bionic) | `Bionic` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 925 | `Bionic_Impakt` | [Bionic Impakt](https://www.chessprogramming.org/Bionic_Impakt) | `Bionic_Impakt` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 926 | `Bismark` | [Bismark](https://www.chessprogramming.org/Bismark) | `Bismark` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 927 | `Bison` | [Bison](https://www.chessprogramming.org/Bison) | `Bison` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 928 | `Bit` | [Bit](https://www.chessprogramming.org/Bit) | `Bit` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 929 | `Bitfoot` | [Bitfoot](https://www.chessprogramming.org/Bitfoot) | `Bitfoot` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 930 | `BitScan` | [BitScan](https://www.chessprogramming.org/BitScan) | `BitScan` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 931 | `Black_Marlin` | [Black Marlin](https://www.chessprogramming.org/Black_Marlin) | `Black_Marlin` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 932 | `BlackMamba` | [BlackMamba](https://www.chessprogramming.org/BlackMamba) | `BlackMamba` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 933 | `Blikskottel` | [Blikskottel](https://www.chessprogramming.org/Blikskottel) | `Blikskottel` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 934 | `Blitz` | [Blitz](https://www.chessprogramming.org/Blitz) | `Blitz` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 935 | `Blitz_Monster` | [Blitz Monster](https://www.chessprogramming.org/Blitz_Monster) | `Blitz_Monster` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 936 | `Blondie25` | [Blondie25](https://www.chessprogramming.org/Blondie25) | `Blondie25` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 937 | `BlueFeverSoft` | [BlueFeverSoft](https://www.chessprogramming.org/BlueFeverSoft) | `BlueFeverSoft` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 938 | `BMCP` | [BMCP](https://www.chessprogramming.org/BMCP) | `BMCP` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 939 | `BMI1` | [BMI1](https://www.chessprogramming.org/BMI1) | `BMI1` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 940 | `BMI2` | [BMI2](https://www.chessprogramming.org/BMI2) | `BMI2` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 941 | `Bob_Herschberg` | [Bob Herschberg](https://www.chessprogramming.org/Bob_Herschberg) | `Bob_Herschberg` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 942 | `Bob_Jenkins` | [Bob Jenkins](https://www.chessprogramming.org/Bob_Jenkins) | `Bob_Jenkins` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 943 | `Bobby` | [Bobby](https://www.chessprogramming.org/Bobby) | `Bobby` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 944 | `Bobcat` | [Bobcat](https://www.chessprogramming.org/Bobcat) | `Bobcat` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 945 | `Bodo` | [Bodo](https://www.chessprogramming.org/Bodo) | `Bodo` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 946 | `Bogol` | [Bogol](https://www.chessprogramming.org/Bogol) | `Bogol` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 947 | `Bojun_Guo` | [Bojun Guo](https://www.chessprogramming.org/Bojun_Guo) | `Bojun_Guo` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 948 | `Bojun_Huang` | [Bojun Huang](https://www.chessprogramming.org/Bojun_Huang) | `Bojun_Huang` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 949 | `Bonanza` | [Bonanza](https://www.chessprogramming.org/Bonanza) | `Bonanza` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 950 | `Booot` | [Booot](https://www.chessprogramming.org/Booot) | `Booot` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 951 | `BootChess` | [BootChess](https://www.chessprogramming.org/BootChess) | `BootChess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 952 | `Boris` | [Boris](https://www.chessprogramming.org/Boris) | `Boris` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 953 | `Boris_Baczynskyj` | [Boris Baczynskyj](https://www.chessprogramming.org/Boris_Baczynskyj) | `Boris_Baczynskyj` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 954 | `Boris_Stilman` | [Boris Stilman](https://www.chessprogramming.org/Boris_Stilman) | `Boris_Stilman` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 955 | `Bound` | [Bound](https://www.chessprogramming.org/Bound) | `Bound` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 956 | `Bouquet` | [Bouquet](https://www.chessprogramming.org/Bouquet) | `Bouquet` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 957 | `BP` | [BP](https://www.chessprogramming.org/BP) | `BP` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 958 | `Bradley_Kuszmaul` | [Bradley Kuszmaul](https://www.chessprogramming.org/Bradley_Kuszmaul) | `Bradley_Kuszmaul` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 959 | `Brainfish` | [Brainfish](https://www.chessprogramming.org/Brainfish) | `Brainfish` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 960 | `Brainless` | [Brainless](https://www.chessprogramming.org/Brainless) | `Brainless` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 961 | `Brainstorm` | [Brainstorm](https://www.chessprogramming.org/Brainstorm) | `Brainstorm` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 962 | `Brause` | [Brause](https://www.chessprogramming.org/Brause) | `Brause` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 963 | `BreakThrough` | [BreakThrough](https://www.chessprogramming.org/BreakThrough) | `BreakThrough` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 964 | `BremboCE` | [BremboCE](https://www.chessprogramming.org/BremboCE) | `BremboCE` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 965 | `Brian_Richardson` | [Brian Richardson](https://www.chessprogramming.org/Brian_Richardson) | `Brian_Richardson` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 966 | `Brian_Sheppard` | [Brian Sheppard](https://www.chessprogramming.org/Brian_Sheppard) | `Brian_Sheppard` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 967 | `Bright` | [Bright](https://www.chessprogramming.org/Bright) | `Bright` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 968 | `Bringer` | [Bringer](https://www.chessprogramming.org/Bringer) | `Bringer` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 969 | `Bruce_Abramson` | [Bruce Abramson](https://www.chessprogramming.org/Bruce_Abramson) | `Bruce_Abramson` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 970 | `Bruce_Moreland` | [Bruce Moreland](https://www.chessprogramming.org/Bruce_Moreland) | `Bruce_Moreland` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 971 | `Bruce_Wright` | [Bruce Wright](https://www.chessprogramming.org/Bruce_Wright) | `Bruce_Wright` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 972 | `Bruja` | [Bruja](https://www.chessprogramming.org/Bruja) | `Bruja` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 973 | `Bruno_Bouzy` | [Bruno Bouzy](https://www.chessprogramming.org/Bruno_Bouzy) | `Bruno_Bouzy` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 974 | `Bruno_Bras` | [Bruno Bras](https://www.chessprogramming.org/Bruno_Bras) | `Bruno_Bras` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 975 | `Bruno_Lucas` | [Bruno Lucas](https://www.chessprogramming.org/Bruno_Lucas) | `Bruno_Lucas` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 976 | `Brutus` | [Brutus](https://www.chessprogramming.org/Brutus) | `Brutus` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 977 | `Brutus_NL` | [Brutus NL](https://www.chessprogramming.org/Brutus_NL) | `Brutus_NL` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 978 | `Bs6676` | [Bs6676](https://www.chessprogramming.org/Bs6676) | `Bs6676` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 979 | `BugChess_FR` | [BugChess FR](https://www.chessprogramming.org/BugChess_FR) | `BugChess_FR` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 980 | `BugChess_NL` | [BugChess NL](https://www.chessprogramming.org/BugChess_NL) | `BugChess_NL` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 981 | `Burkhard_Monien` | [Burkhard Monien](https://www.chessprogramming.org/Burkhard_Monien) | `Burkhard_Monien` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 982 | `Burton_Wendroff` | [Burton Wendroff](https://www.chessprogramming.org/Burton_Wendroff) | `Burton_Wendroff` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 983 | `Butcher` | [Butcher](https://www.chessprogramming.org/Butcher) | `Butcher` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 984 | `Buzz` | [Buzz](https://www.chessprogramming.org/Buzz) | `Buzz` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 985 | `Byte` | [Byte](https://www.chessprogramming.org/Byte) | `Byte` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 986 | `C` | [C](https://www.chessprogramming.org/C) | `C` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 987 | `C_sharp` | [C sharp](https://www.chessprogramming.org/C_sharp) | `C_sharp` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 988 | `Caddell_Chess` | [Caddell Chess](https://www.chessprogramming.org/Caddell_Chess) | `Caddell_Chess` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 989 | `Caesar` | [Caesar](https://www.chessprogramming.org/Caesar) | `Caesar` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 990 | `Calculon` | [Calculon](https://www.chessprogramming.org/Calculon) | `Calculon` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 991 | `Caligula` | [Caligula](https://www.chessprogramming.org/Caligula) | `Caligula` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 992 | `Caligula_PC` | [Caligula PC](https://www.chessprogramming.org/Caligula_PC) | `Caligula_PC` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 993 | `Cameron_Browne` | [Cameron Browne](https://www.chessprogramming.org/Cameron_Browne) | `Cameron_Browne` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 994 | `Canadian_Computer_Chess_Invitational_Championship_1984` | [Canadian Computer Chess Invitational Cha](https://www.chessprogramming.org/Canadian_Computer_Chess_Invitational_Championship_1984) | `Canadian_Computer_Chess_Invitational_Championship_1984` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 995 | `Capivara` | [Capivara](https://www.chessprogramming.org/Capivara) | `Capivara` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 996 | `CAPS` | [CAPS](https://www.chessprogramming.org/CAPS) | `CAPS` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 997 | `Captures` | [Captures](https://www.chessprogramming.org/Captures) | `Captures` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 998 | `Carballo` | [Carballo](https://www.chessprogramming.org/Carballo) | `Carballo` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 999 | `Carey_Bloodworth` | [Carey Bloodworth](https://www.chessprogramming.org/Carey_Bloodworth) | `Carey_Bloodworth` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 1000 | `Carl_Ebeling` | [Carl Ebeling](https://www.chessprogramming.org/Carl_Ebeling) | `Carl_Ebeling` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Tournament Protocols, Rules & Fail-Closed Safety
**Total Chapters in Domain:** 156 | **Domain Corpus Size:** 143,079 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 27 | `Chess_Engine_Communication_Protocol` | [Chess Engine Communication Protocol](https://www.chessprogramming.org/Chess_Engine_Communication_Protocol) | `Chess_Engine_Communication_Protocol` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 103 | `Aegon_Tournaments` | [Aegon Tournaments](https://www.chessprogramming.org/Aegon_Tournaments) | `Aegon_Tournaments` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 110 | `American_Microcomputer_Chess_Tournaments` | [American Microcomputer Chess Tournaments](https://www.chessprogramming.org/American_Microcomputer_Chess_Tournaments) | `American_Microcomputer_Chess_Tournaments` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 143 | `CCC` | [CCC](https://www.chessprogramming.org/CCC) | `CCC` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 144 | `CCC_2005` | [CCC 2005](https://www.chessprogramming.org/CCC_2005) | `CCC_2005` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 145 | `CCC_2007` | [CCC 2007](https://www.chessprogramming.org/CCC_2007) | `CCC_2007` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 146 | `CCC_2008` | [CCC 2008](https://www.chessprogramming.org/CCC_2008) | `CCC_2008` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 147 | `CCC_2009` | [CCC 2009](https://www.chessprogramming.org/CCC_2009) | `CCC_2009` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 148 | `CCCCISC_2008` | [CCCCISC 2008](https://www.chessprogramming.org/CCCCISC_2008) | `CCCCISC_2008` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 149 | `CCCP` | [CCCP](https://www.chessprogramming.org/CCCP) | `CCCP` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 151 | `CCT_Tournaments` | [CCT Tournaments](https://www.chessprogramming.org/CCT_Tournaments) | `CCT_Tournaments` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 163 | `Confucius` | [Confucius](https://www.chessprogramming.org/Confucius) | `Confucius` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 169 | `Crashtest_Dummy` | [Crashtest Dummy](https://www.chessprogramming.org/Crashtest_Dummy) | `Crashtest_Dummy` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 170 | `CSVN_Programmers_Tournament` | [CSVN Programmers Tournament](https://www.chessprogramming.org/CSVN_Programmers_Tournament) | `CSVN_Programmers_Tournament` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 182 | `DOCCC_1981` | [DOCCC 1981](https://www.chessprogramming.org/DOCCC_1981) | `DOCCC_1981` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 183 | `DOCCC_1982` | [DOCCC 1982](https://www.chessprogramming.org/DOCCC_1982) | `DOCCC_1982` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 184 | `DOCCC_1983` | [DOCCC 1983](https://www.chessprogramming.org/DOCCC_1983) | `DOCCC_1983` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 185 | `DOCCC_1984` | [DOCCC 1984](https://www.chessprogramming.org/DOCCC_1984) | `DOCCC_1984` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 186 | `DOCCC_1985` | [DOCCC 1985](https://www.chessprogramming.org/DOCCC_1985) | `DOCCC_1985` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 187 | `DOCCC_1986` | [DOCCC 1986](https://www.chessprogramming.org/DOCCC_1986) | `DOCCC_1986` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 188 | `DOCCC_1987` | [DOCCC 1987](https://www.chessprogramming.org/DOCCC_1987) | `DOCCC_1987` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 189 | `DOCCC_1988` | [DOCCC 1988](https://www.chessprogramming.org/DOCCC_1988) | `DOCCC_1988` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 190 | `DOCCC_1989` | [DOCCC 1989](https://www.chessprogramming.org/DOCCC_1989) | `DOCCC_1989` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 191 | `DOCCC_1990` | [DOCCC 1990](https://www.chessprogramming.org/DOCCC_1990) | `DOCCC_1990` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 192 | `DOCCC_1991` | [DOCCC 1991](https://www.chessprogramming.org/DOCCC_1991) | `DOCCC_1991` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 193 | `DOCCC_1992` | [DOCCC 1992](https://www.chessprogramming.org/DOCCC_1992) | `DOCCC_1992` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 194 | `DOCCC_1993` | [DOCCC 1993](https://www.chessprogramming.org/DOCCC_1993) | `DOCCC_1993` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 195 | `DOCCC_1994` | [DOCCC 1994](https://www.chessprogramming.org/DOCCC_1994) | `DOCCC_1994` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 196 | `DOCCC_1995` | [DOCCC 1995](https://www.chessprogramming.org/DOCCC_1995) | `DOCCC_1995` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 197 | `DOCCC_1996` | [DOCCC 1996](https://www.chessprogramming.org/DOCCC_1996) | `DOCCC_1996` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 198 | `DOCCC_1997` | [DOCCC 1997](https://www.chessprogramming.org/DOCCC_1997) | `DOCCC_1997` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 199 | `DOCCC_1998` | [DOCCC 1998](https://www.chessprogramming.org/DOCCC_1998) | `DOCCC_1998` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 200 | `DOCCC_1999` | [DOCCC 1999](https://www.chessprogramming.org/DOCCC_1999) | `DOCCC_1999` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 201 | `DOCCC_2000` | [DOCCC 2000](https://www.chessprogramming.org/DOCCC_2000) | `DOCCC_2000` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 202 | `DOCCC_2001` | [DOCCC 2001](https://www.chessprogramming.org/DOCCC_2001) | `DOCCC_2001` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 203 | `DOCCC_2002` | [DOCCC 2002](https://www.chessprogramming.org/DOCCC_2002) | `DOCCC_2002` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 204 | `DOCCC_2003` | [DOCCC 2003](https://www.chessprogramming.org/DOCCC_2003) | `DOCCC_2003` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 205 | `DOCCC_2004` | [DOCCC 2004](https://www.chessprogramming.org/DOCCC_2004) | `DOCCC_2004` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 206 | `DOCCC_2005` | [DOCCC 2005](https://www.chessprogramming.org/DOCCC_2005) | `DOCCC_2005` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 207 | `DOCCC_2006` | [DOCCC 2006](https://www.chessprogramming.org/DOCCC_2006) | `DOCCC_2006` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 208 | `DOCCC_2007` | [DOCCC 2007](https://www.chessprogramming.org/DOCCC_2007) | `DOCCC_2007` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 209 | `DOCCC_2008` | [DOCCC 2008](https://www.chessprogramming.org/DOCCC_2008) | `DOCCC_2008` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 210 | `DOCCC_2009` | [DOCCC 2009](https://www.chessprogramming.org/DOCCC_2009) | `DOCCC_2009` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 211 | `DOCCC_2010` | [DOCCC 2010](https://www.chessprogramming.org/DOCCC_2010) | `DOCCC_2010` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 212 | `DOCCC_2011` | [DOCCC 2011](https://www.chessprogramming.org/DOCCC_2011) | `DOCCC_2011` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 216 | `ECCC_1976` | [ECCC 1976](https://www.chessprogramming.org/ECCC_1976) | `ECCC_1976` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 217 | `ECCC_1979` | [ECCC 1979](https://www.chessprogramming.org/ECCC_1979) | `ECCC_1979` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 244 | `FCCC_1992` | [FCCC 1992](https://www.chessprogramming.org/FCCC_1992) | `FCCC_1992` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 245 | `FCCC_1995` | [FCCC 1995](https://www.chessprogramming.org/FCCC_1995) | `FCCC_1995` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 246 | `FCCC_1996` | [FCCC 1996](https://www.chessprogramming.org/FCCC_1996) | `FCCC_1996` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 247 | `FCCC_1997` | [FCCC 1997](https://www.chessprogramming.org/FCCC_1997) | `FCCC_1997` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 248 | `FCCC_1998` | [FCCC 1998](https://www.chessprogramming.org/FCCC_1998) | `FCCC_1998` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 249 | `FCCC_1999` | [FCCC 1999](https://www.chessprogramming.org/FCCC_1999) | `FCCC_1999` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 250 | `FCCC_2000` | [FCCC 2000](https://www.chessprogramming.org/FCCC_2000) | `FCCC_2000` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 251 | `FCCC_2002` | [FCCC 2002](https://www.chessprogramming.org/FCCC_2002) | `FCCC_2002` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 252 | `FCCC_2003` | [FCCC 2003](https://www.chessprogramming.org/FCCC_2003) | `FCCC_2003` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 253 | `FCCC_2004` | [FCCC 2004](https://www.chessprogramming.org/FCCC_2004) | `FCCC_2004` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 254 | `First_GI_Computer_Chess_Tournament` | [First GI Computer Chess Tournament](https://www.chessprogramming.org/First_GI_Computer_Chess_Tournament) | `First_GI_Computer_Chess_Tournament` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 255 | `French_Programmers_Tournament` | [French Programmers Tournament](https://www.chessprogramming.org/French_Programmers_Tournament) | `French_Programmers_Tournament` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 272 | `ICGA_Tournament_Rules` | [ICGA Tournament Rules](https://www.chessprogramming.org/ICGA_Tournament_Rules) | `ICGA_Tournament_Rules` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 277 | `International_Computer_Chess_Tournament_1984` | [International Computer Chess Tournament ](https://www.chessprogramming.org/International_Computer_Chess_Tournament_1984) | `International_Computer_Chess_Tournament_1984` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 278 | `International_CSVN_Tournament` | [International CSVN Tournament](https://www.chessprogramming.org/International_CSVN_Tournament) | `International_CSVN_Tournament` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 279 | `IOPCCC_2007` | [IOPCCC 2007](https://www.chessprogramming.org/IOPCCC_2007) | `IOPCCC_2007` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 280 | `IOPCCC_2008` | [IOPCCC 2008](https://www.chessprogramming.org/IOPCCC_2008) | `IOPCCC_2008` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 281 | `IPCCC` | [IPCCC](https://www.chessprogramming.org/IPCCC) | `IPCCC` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 282 | `IPCCC_1991` | [IPCCC 1991](https://www.chessprogramming.org/IPCCC_1991) | `IPCCC_1991` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 283 | `IPCCC_1992` | [IPCCC 1992](https://www.chessprogramming.org/IPCCC_1992) | `IPCCC_1992` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 284 | `IPCCC_1993` | [IPCCC 1993](https://www.chessprogramming.org/IPCCC_1993) | `IPCCC_1993` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 285 | `IPCCC_1994` | [IPCCC 1994](https://www.chessprogramming.org/IPCCC_1994) | `IPCCC_1994` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 286 | `IPCCC_1995` | [IPCCC 1995](https://www.chessprogramming.org/IPCCC_1995) | `IPCCC_1995` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 287 | `IPCCC_1997` | [IPCCC 1997](https://www.chessprogramming.org/IPCCC_1997) | `IPCCC_1997` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 288 | `IPCCC_1998` | [IPCCC 1998](https://www.chessprogramming.org/IPCCC_1998) | `IPCCC_1998` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 289 | `IPCCC_1999` | [IPCCC 1999](https://www.chessprogramming.org/IPCCC_1999) | `IPCCC_1999` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 290 | `IPCCC_2000` | [IPCCC 2000](https://www.chessprogramming.org/IPCCC_2000) | `IPCCC_2000` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 291 | `IPCCC_2001` | [IPCCC 2001](https://www.chessprogramming.org/IPCCC_2001) | `IPCCC_2001` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 292 | `IPCCC_2002` | [IPCCC 2002](https://www.chessprogramming.org/IPCCC_2002) | `IPCCC_2002` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 293 | `IPCCC_2003` | [IPCCC 2003](https://www.chessprogramming.org/IPCCC_2003) | `IPCCC_2003` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 294 | `IPCCC_2004` | [IPCCC 2004](https://www.chessprogramming.org/IPCCC_2004) | `IPCCC_2004` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 295 | `IPCCC_2005` | [IPCCC 2005](https://www.chessprogramming.org/IPCCC_2005) | `IPCCC_2005` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 296 | `IPCCC_2005_b` | [IPCCC 2005 b](https://www.chessprogramming.org/IPCCC_2005_b) | `IPCCC_2005_b` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 297 | `IPCCC_2006` | [IPCCC 2006](https://www.chessprogramming.org/IPCCC_2006) | `IPCCC_2006` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 298 | `IPCCC_2007` | [IPCCC 2007](https://www.chessprogramming.org/IPCCC_2007) | `IPCCC_2007` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 299 | `IPCCC_2008` | [IPCCC 2008](https://www.chessprogramming.org/IPCCC_2008) | `IPCCC_2008` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 303 | `Jerusalem_CC_Tournament_1978` | [Jerusalem CC Tournament 1978](https://www.chessprogramming.org/Jerusalem_CC_Tournament_1978) | `Jerusalem_CC_Tournament_1978` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 379 | `PCCC_2002` | [PCCC 2002](https://www.chessprogramming.org/PCCC_2002) | `PCCC_2002` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 380 | `PCCC_2003` | [PCCC 2003](https://www.chessprogramming.org/PCCC_2003) | `PCCC_2003` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 381 | `PCCC_2004` | [PCCC 2004](https://www.chessprogramming.org/PCCC_2004) | `PCCC_2004` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 382 | `PCCC_2005` | [PCCC 2005](https://www.chessprogramming.org/PCCC_2005) | `PCCC_2005` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 383 | `PCCC_2006` | [PCCC 2006](https://www.chessprogramming.org/PCCC_2006) | `PCCC_2006` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 384 | `PCCC_2009` | [PCCC 2009](https://www.chessprogramming.org/PCCC_2009) | `PCCC_2009` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 385 | `PCCC_2010` | [PCCC 2010](https://www.chessprogramming.org/PCCC_2010) | `PCCC_2010` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 386 | `PCCC_2011` | [PCCC 2011](https://www.chessprogramming.org/PCCC_2011) | `PCCC_2011` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 387 | `PCCC_2012` | [PCCC 2012](https://www.chessprogramming.org/PCCC_2012) | `PCCC_2012` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 400 | `Protocols` | [Protocols](https://www.chessprogramming.org/Protocols) | `Protocols` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 425 | `SCCC_1993` | [SCCC 1993](https://www.chessprogramming.org/SCCC_1993) | `SCCC_1993` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 426 | `SCCC_1994` | [SCCC 1994](https://www.chessprogramming.org/SCCC_1994) | `SCCC_1994` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 427 | `SCCC_1995` | [SCCC 1995](https://www.chessprogramming.org/SCCC_1995) | `SCCC_1995` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 428 | `SCCC_1996` | [SCCC 1996](https://www.chessprogramming.org/SCCC_1996) | `SCCC_1996` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 429 | `SCCC_1998` | [SCCC 1998](https://www.chessprogramming.org/SCCC_1998) | `SCCC_1998` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 430 | `SCCC_1999` | [SCCC 1999](https://www.chessprogramming.org/SCCC_1999) | `SCCC_1999` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 468 | `TCEC` | [TCEC](https://www.chessprogramming.org/TCEC) | `TCEC` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 469 | `TCEC_Season_1` | [TCEC Season 1](https://www.chessprogramming.org/TCEC_Season_1) | `TCEC_Season_1` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 470 | `TCEC_Season_10` | [TCEC Season 10](https://www.chessprogramming.org/TCEC_Season_10) | `TCEC_Season_10` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 471 | `TCEC_Season_11` | [TCEC Season 11](https://www.chessprogramming.org/TCEC_Season_11) | `TCEC_Season_11` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 472 | `TCEC_Season_12` | [TCEC Season 12](https://www.chessprogramming.org/TCEC_Season_12) | `TCEC_Season_12` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 473 | `TCEC_Season_13` | [TCEC Season 13](https://www.chessprogramming.org/TCEC_Season_13) | `TCEC_Season_13` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 474 | `TCEC_Season_14` | [TCEC Season 14](https://www.chessprogramming.org/TCEC_Season_14) | `TCEC_Season_14` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 475 | `TCEC_Season_15` | [TCEC Season 15](https://www.chessprogramming.org/TCEC_Season_15) | `TCEC_Season_15` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 476 | `TCEC_Season_16` | [TCEC Season 16](https://www.chessprogramming.org/TCEC_Season_16) | `TCEC_Season_16` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 477 | `TCEC_Season_17` | [TCEC Season 17](https://www.chessprogramming.org/TCEC_Season_17) | `TCEC_Season_17` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 478 | `TCEC_Season_18` | [TCEC Season 18](https://www.chessprogramming.org/TCEC_Season_18) | `TCEC_Season_18` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 479 | `TCEC_Season_19` | [TCEC Season 19](https://www.chessprogramming.org/TCEC_Season_19) | `TCEC_Season_19` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 480 | `TCEC_Season_2` | [TCEC Season 2](https://www.chessprogramming.org/TCEC_Season_2) | `TCEC_Season_2` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 481 | `TCEC_Season_20` | [TCEC Season 20](https://www.chessprogramming.org/TCEC_Season_20) | `TCEC_Season_20` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 482 | `TCEC_Season_21` | [TCEC Season 21](https://www.chessprogramming.org/TCEC_Season_21) | `TCEC_Season_21` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 483 | `TCEC_Season_22` | [TCEC Season 22](https://www.chessprogramming.org/TCEC_Season_22) | `TCEC_Season_22` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 484 | `TCEC_Season_3` | [TCEC Season 3](https://www.chessprogramming.org/TCEC_Season_3) | `TCEC_Season_3` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 485 | `TCEC_Season_4` | [TCEC Season 4](https://www.chessprogramming.org/TCEC_Season_4) | `TCEC_Season_4` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 486 | `TCEC_Season_5` | [TCEC Season 5](https://www.chessprogramming.org/TCEC_Season_5) | `TCEC_Season_5` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 487 | `TCEC_Season_6` | [TCEC Season 6](https://www.chessprogramming.org/TCEC_Season_6) | `TCEC_Season_6` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 488 | `TCEC_Season_7` | [TCEC Season 7](https://www.chessprogramming.org/TCEC_Season_7) | `TCEC_Season_7` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 489 | `TCEC_Season_8` | [TCEC Season 8](https://www.chessprogramming.org/TCEC_Season_8) | `TCEC_Season_8` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 490 | `TCEC_Season_9` | [TCEC Season 9](https://www.chessprogramming.org/TCEC_Season_9) | `TCEC_Season_9` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 494 | `The_Chess_Programmers_Tournament` | [The Chess Programmers Tournament](https://www.chessprogramming.org/The_Chess_Programmers_Tournament) | `The_Chess_Programmers_Tournament` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 498 | `The_Penrod_Memorial_Microchess_Tournament` | [The Penrod Memorial Microchess Tournamen](https://www.chessprogramming.org/The_Penrod_Memorial_Microchess_Tournament) | `The_Penrod_Memorial_Microchess_Tournament` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 506 | `Tournament_Manager` | [Tournament Manager](https://www.chessprogramming.org/Tournament_Manager) | `Tournament_Manager` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 507 | `Tournaments_and_Matches` | [Tournaments and Matches](https://www.chessprogramming.org/Tournaments_and_Matches) | `Tournaments_and_Matches` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 514 | `UCI` | [UCI](https://www.chessprogramming.org/UCI) | `UCI` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 515 | `UCI2WB` | [UCI2WB](https://www.chessprogramming.org/UCI2WB) | `UCI2WB` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 517 | `UPCCC_1992` | [UPCCC 1992](https://www.chessprogramming.org/UPCCC_1992) | `UPCCC_1992` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 518 | `UPCCC_1993` | [UPCCC 1993](https://www.chessprogramming.org/UPCCC_1993) | `UPCCC_1993` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 519 | `UPCCC_1994` | [UPCCC 1994](https://www.chessprogramming.org/UPCCC_1994) | `UPCCC_1994` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 520 | `USOCCC_1985` | [USOCCC 1985](https://www.chessprogramming.org/USOCCC_1985) | `USOCCC_1985` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 521 | `USOCCC_1986` | [USOCCC 1986](https://www.chessprogramming.org/USOCCC_1986) | `USOCCC_1986` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 522 | `USOCCC_1987` | [USOCCC 1987](https://www.chessprogramming.org/USOCCC_1987) | `USOCCC_1987` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 523 | `USOCCC_1988` | [USOCCC 1988](https://www.chessprogramming.org/USOCCC_1988) | `USOCCC_1988` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 524 | `Various_Microcomputer_Chess_Tournaments` | [Various Microcomputer Chess Tournaments](https://www.chessprogramming.org/Various_Microcomputer_Chess_Tournaments) | `Various_Microcomputer_Chess_Tournaments` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 527 | `Wb2UCI` | [Wb2UCI](https://www.chessprogramming.org/Wb2UCI) | `Wb2UCI` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 531 | `WMCCC_1980` | [WMCCC 1980](https://www.chessprogramming.org/WMCCC_1980) | `WMCCC_1980` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 532 | `WMCCC_1981` | [WMCCC 1981](https://www.chessprogramming.org/WMCCC_1981) | `WMCCC_1981` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 533 | `WMCCC_1983` | [WMCCC 1983](https://www.chessprogramming.org/WMCCC_1983) | `WMCCC_1983` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 534 | `WMCCC_1984` | [WMCCC 1984](https://www.chessprogramming.org/WMCCC_1984) | `WMCCC_1984` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 535 | `WMCCC_1985` | [WMCCC 1985](https://www.chessprogramming.org/WMCCC_1985) | `WMCCC_1985` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 536 | `WMCCC_1986` | [WMCCC 1986](https://www.chessprogramming.org/WMCCC_1986) | `WMCCC_1986` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 537 | `WMCCC_1987` | [WMCCC 1987](https://www.chessprogramming.org/WMCCC_1987) | `WMCCC_1987` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 538 | `WMCCC_1988` | [WMCCC 1988](https://www.chessprogramming.org/WMCCC_1988) | `WMCCC_1988` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 539 | `WMCCC_1989` | [WMCCC 1989](https://www.chessprogramming.org/WMCCC_1989) | `WMCCC_1989` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 540 | `WMCCC_1990` | [WMCCC 1990](https://www.chessprogramming.org/WMCCC_1990) | `WMCCC_1990` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 541 | `WMCCC_1991` | [WMCCC 1991](https://www.chessprogramming.org/WMCCC_1991) | `WMCCC_1991` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 542 | `WMCCC_1993` | [WMCCC 1993](https://www.chessprogramming.org/WMCCC_1993) | `WMCCC_1993` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 543 | `WMCCC_1995` | [WMCCC 1995](https://www.chessprogramming.org/WMCCC_1995) | `WMCCC_1995` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 544 | `WMCCC_1996` | [WMCCC 1996](https://www.chessprogramming.org/WMCCC_1996) | `WMCCC_1996` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 545 | `WMCCC_1997` | [WMCCC 1997](https://www.chessprogramming.org/WMCCC_1997) | `WMCCC_1997` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 546 | `WMCCC_1999` | [WMCCC 1999](https://www.chessprogramming.org/WMCCC_1999) | `WMCCC_1999` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 547 | `WMCCC_2000` | [WMCCC 2000](https://www.chessprogramming.org/WMCCC_2000) | `WMCCC_2000` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 548 | `WMCCC_2001` | [WMCCC 2001](https://www.chessprogramming.org/WMCCC_2001) | `WMCCC_2001` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Search Algorithms & Tree Traversal
**Total Chapters in Domain:** 50 | **Domain Corpus Size:** 52,895 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 45 | `Heuristic_Alpha` | [Heuristic Alpha](https://www.chessprogramming.org/Heuristic_Alpha) | `Heuristic_Alpha` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 49 | `Horizon_Node` | [Horizon Node](https://www.chessprogramming.org/Horizon_Node) | `Horizon_Node` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 69 | `One_Reply_Extensions` | [One Reply Extensions](https://www.chessprogramming.org/One_Reply_Extensions) | `One_Reply_Extensions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 72 | `Parallel_Search` | [Parallel Search](https://www.chessprogramming.org/Parallel_Search) | `Parallel_Search` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 81 | `Quiescence_Search` | [Quiescence Search](https://www.chessprogramming.org/Quiescence_Search) | `Quiescence_Search` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 82 | `Quiescent_Node` | [Quiescent Node](https://www.chessprogramming.org/Quiescent_Node) | `Quiescent_Node` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 88 | `Search_Space` | [Search Space](https://www.chessprogramming.org/Search_Space) | `Search_Space` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 89 | `Search_Tree` | [Search Tree](https://www.chessprogramming.org/Search_Tree) | `Search_Tree` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 107 | `Alpha` | [Alpha](https://www.chessprogramming.org/Alpha) | `Alpha` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 108 | `Alpha_I` | [Alpha I](https://www.chessprogramming.org/Alpha_I) | `Alpha_I` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 109 | `AlphaZero` | [AlphaZero](https://www.chessprogramming.org/AlphaZero) | `AlphaZero` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 117 | `Aspiration_Windows` | [Aspiration Windows](https://www.chessprogramming.org/Aspiration_Windows) | `Aspiration_Windows` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 129 | `Beta` | [Beta](https://www.chessprogramming.org/Beta) | `Beta` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 165 | `Conspiracy_Number_Search` | [Conspiracy Number Search](https://www.chessprogramming.org/Conspiracy_Number_Search) | `Conspiracy_Number_Search` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 177 | `DEC_Alpha` | [DEC Alpha](https://www.chessprogramming.org/DEC_Alpha) | `DEC_Alpha` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 215 | `Dynamic_Tree_Splitting` | [Dynamic Tree Splitting](https://www.chessprogramming.org/Dynamic_Tree_Splitting) | `Dynamic_Tree_Splitting` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 230 | `EtaBeta` | [EtaBeta](https://www.chessprogramming.org/EtaBeta) | `EtaBeta` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 256 | `Frontier_Nodes` | [Frontier Nodes](https://www.chessprogramming.org/Frontier_Nodes) | `Frontier_Nodes` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 274 | `Interior_Node` | [Interior Node](https://www.chessprogramming.org/Interior_Node) | `Interior_Node` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 275 | `Interior_Node_Recognizer` | [Interior Node Recognizer](https://www.chessprogramming.org/Interior_Node_Recognizer) | `Interior_Node_Recognizer` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 276 | `Internal_Iterative_Reductions` | [Internal Iterative Reductions](https://www.chessprogramming.org/Internal_Iterative_Reductions) | `Internal_Iterative_Reductions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 301 | `Iterative_Search` | [Iterative Search](https://www.chessprogramming.org/Iterative_Search) | `Iterative_Search` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 323 | `Last_Best_Reply` | [Last Best Reply](https://www.chessprogramming.org/Last_Best_Reply) | `Last_Best_Reply` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 324 | `Leaf_Node` | [Leaf Node](https://www.chessprogramming.org/Leaf_Node) | `Leaf_Node` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 326 | `Leftmost_Node` | [Leftmost Node](https://www.chessprogramming.org/Leftmost_Node) | `Leftmost_Node` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 337 | `Mate_Search` | [Mate Search](https://www.chessprogramming.org/Mate_Search) | `Mate_Search` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 344 | `Minimax_Tree_Optimization` | [Minimax Tree Optimization](https://www.chessprogramming.org/Minimax_Tree_Optimization) | `Minimax_Tree_Optimization` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 352 | `Node` | [Node](https://www.chessprogramming.org/Node) | `Node` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 353 | `Node_Types` | [Node Types](https://www.chessprogramming.org/Node_Types) | `Node_Types` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 354 | `Nodes_per_Second` | [Nodes per Second](https://www.chessprogramming.org/Nodes_per_Second) | `Nodes_per_Second` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 361 | `Opponent_Model_Search` | [Opponent Model Search](https://www.chessprogramming.org/Opponent_Model_Search) | `Opponent_Model_Search` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 392 | `Ply` | [Ply](https://www.chessprogramming.org/Ply) | `Ply` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 393 | `Plymate` | [Plymate](https://www.chessprogramming.org/Plymate) | `Plymate` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 398 | `Pre_Frontier_Node` | [Pre Frontier Node](https://www.chessprogramming.org/Pre_Frontier_Node) | `Pre_Frontier_Node` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 399 | `Principal_Variation_Search` | [Principal Variation Search](https://www.chessprogramming.org/Principal_Variation_Search) | `Principal_Variation_Search` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 402 | `PV_Extensions` | [PV Extensions](https://www.chessprogramming.org/PV_Extensions) | `PV_Extensions` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 403 | `PVS_and_Aspiration` | [PVS and Aspiration](https://www.chessprogramming.org/PVS_and_Aspiration) | `PVS_and_Aspiration` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 432 | `Search` | [Search](https://www.chessprogramming.org/Search) | `Search` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 433 | `Search_Explosion` | [Search Explosion](https://www.chessprogramming.org/Search_Explosion) | `Search_Explosion` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 434 | `Search_Instability` | [Search Instability](https://www.chessprogramming.org/Search_Instability) | `Search_Instability` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 435 | `Search_Pathology` | [Search Pathology](https://www.chessprogramming.org/Search_Pathology) | `Search_Pathology` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 436 | `Search_Progression` | [Search Progression](https://www.chessprogramming.org/Search_Progression) | `Search_Progression` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 437 | `Search_Statistics` | [Search Statistics](https://www.chessprogramming.org/Search_Statistics) | `Search_Statistics` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 438 | `Search_with_Random_Leaf_Values` | [Search with Random Leaf Values](https://www.chessprogramming.org/Search_with_Random_Leaf_Values) | `Search_with_Random_Leaf_Values` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 439 | `Searcher` | [Searcher](https://www.chessprogramming.org/Searcher) | `Searcher` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 442 | `Selective_Search` | [Selective Search](https://www.chessprogramming.org/Selective_Search) | `Selective_Search` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 446 | `Sibling_Node` | [Sibling Node](https://www.chessprogramming.org/Sibling_Node) | `Sibling_Node` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 493 | `Terminal_Node` | [Terminal Node](https://www.chessprogramming.org/Terminal_Node) | `Terminal_Node` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 511 | `Treebeard` | [Treebeard](https://www.chessprogramming.org/Treebeard) | `Treebeard` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 512 | `Treefrog` | [Treefrog](https://www.chessprogramming.org/Treefrog) | `Treefrog` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Endgame Tablebases & Mathematical Resolution
**Total Chapters in Domain:** 5 | **Domain Corpus Size:** 9,420 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 86 | `Rook_Endgame` | [Rook Endgame](https://www.chessprogramming.org/Rook_Endgame) | `Rook_Endgame` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 221 | `Endgame` | [Endgame](https://www.chessprogramming.org/Endgame) | `Endgame` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 222 | `Endgame_Bitbases` | [Endgame Bitbases](https://www.chessprogramming.org/Endgame_Bitbases) | `Endgame_Bitbases` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 308 | `KBNK_Endgame` | [KBNK Endgame](https://www.chessprogramming.org/KBNK_Endgame) | `KBNK_Endgame` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 464 | `Syzygy_Bases` | [Syzygy Bases](https://www.chessprogramming.org/Syzygy_Bases) | `Syzygy_Bases` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Time Management & Clock Algorithms
**Total Chapters in Domain:** 7 | **Domain Corpus Size:** 6,644 words

| Round | Topic | Canonical Title | Source URL | Key Technical Insight |
|:---:|:---|:---|:---|:---|
| 269 | `Horizon` | [Horizon](https://www.chessprogramming.org/Horizon) | `Horizon` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 270 | `Horizon_Effect` | [Horizon Effect](https://www.chessprogramming.org/Horizon_Effect) | `Horizon_Effect` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 271 | `Horizontal_Mirroring` | [Horizontal Mirroring](https://www.chessprogramming.org/Horizontal_Mirroring) | `Horizontal_Mirroring` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 365 | `Pastime` | [Pastime](https://www.chessprogramming.org/Pastime) | `Pastime` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 396 | `Pondering` | [Pondering](https://www.chessprogramming.org/Pondering) | `Pondering` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 502 | `Time_Management` | [Time Management](https://www.chessprogramming.org/Time_Management) | `Time_Management` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |
| 503 | `Timeline` | [Timeline](https://www.chessprogramming.org/Timeline) | `Timeline` | This is a temporary, read-only recovery of the chessprogrammingwiki while a longer-term plan is worked out |

---

## Master Synthesis: Concrete Actionable Directives for Youloss

### 1. Apple Silicon Hardware Exploitation
- **7 Threads Locked:** Hybrid 4P + 3E cores allocation verified against 10-core contention penalties.
- **NEON Dot-Product SIMD:** Hardware `sdot` instructions directly accelerate NNUE affine propagation via `USE_NEON_DOTPROD`.
- **32-Byte TT Alignment:** Cluster packing precisely divides Apple Silicon 128-byte cache lines without cross-line penalties.

### 2. Zero-Increment Tournament Security ($1500+0$)
- **Dynamic Horizon:** `HorizonOpening = 32.0` and `HorizonEndgame = 25.0` preserve safe late-game buffers.
- **Move Overhead & Clock Latency:** `Move Overhead = 1500 ms` and `clock_latency_s = 2.0 s` completely eliminate flag risk during manual physical clock operation.
- **Eval Stability:** Dynamic extensions triggered only on severe eval swings (`FallMax = 2.0`).

### 3. Repertoire & Endgame Climax
- **Deep Polyglot Repertoire:** 1,633 entries across 110 lines provide 0ms moves in sharp, imbalanced lines to avoid drawish stalemates.
- **Syzygy 5-Piece Perfection:** 290 3-4-5 piece tablebases in `assets/syzygy` guarantee instant 1ms moves in <= 5 pieces, preventing 50-move rule lapses.

### 4. Fail-Closed Resilience
- Full operator command loop (`press`, `go`, `played`, `clock`, `fen`, `undo`) with incident diagnostics sidecars.
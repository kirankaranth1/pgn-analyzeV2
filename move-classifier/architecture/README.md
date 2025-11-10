# Chess Move Classification Architecture

> Comprehensive architectural documentation for the Wintrchess move classification system

## Overview

This documentation suite provides a complete architectural specification of the chess move classification system. The system analyzes chess games using engine evaluations and classifies each move into categories such as BRILLIANT, BEST, MISTAKE, BLUNDER, and more.

## Architecture at a Glance

**Core Components:**
- **Hybrid Engine System** - Cloud (Lichess) + Local (Stockfish 17)
- **Multi-PV Analysis** - Evaluates multiple candidate moves
- **Classification Hierarchy** - Priority-based move categorization
- **Supporting Systems** - Attack/defense analysis, piece safety, opening book

**Move Classifications:**
- `BRILLIANT` - Spectacular sacrifices with compensation
- `CRITICAL` - Essential moves to maintain advantage
- `BEST` - Optimal moves (including checkmates)
- `EXCELLENT` - Strong moves with minimal loss
- `OKAY` - Acceptable moves
- `INACCURACY` - Questionable moves
- `MISTAKE` - Clear errors
- `BLUNDER` - Serious mistakes
- `THEORY` - Known opening moves
- `FORCED` - Only legal move available

## Documentation Structure

### Getting Started

1. **[Core Concepts](./01-core-concepts.md)** - Start here
   - Chess notation (FEN, SAN, UCI)
   - Engine evaluations (centipawns, mate scores)
   - Expected points and win probability
   - State tree and node extraction

### Classification System

2. **[Classification Overview](./02-classification-overview.md)**
   - Classification hierarchy and priority
   - Decision flow and waterfall logic
   - Configuration options

3. **[Basic Classifications](./03-basic-classifications.md)**
   - FORCED - Only legal move
   - THEORY - Opening book moves
   - CHECKMATE - Mating moves

4. **[Point Loss Classification](./04-point-loss-classification.md)**
   - Expected points calculation
   - Point loss thresholds
   - BEST, EXCELLENT, OKAY, INACCURACY, MISTAKE, BLUNDER

5. **[Advanced Classifications](./05-advanced-classifications.md)**
   - CRITICAL - Essential only moves
   - BRILLIANT - Spectacular sacrifices

### Supporting Systems

6. **[Attack and Defense Systems](./06-attack-defense.md)**
   - Direct and x-ray attacks
   - Defender analysis
   - Piece safety calculations

7. **[Tactical Analysis](./07-tactical-analysis.md)**
   - Danger levels and counter-threats
   - Trapped pieces
   - Material evaluation

8. **[Supporting Utilities](./08-utilities.md)**
   - Board manipulation
   - Move parsing and validation
   - Node extraction
   - Subjective evaluation

### Reference

9. **[Data Structures](./09-data-structures.md)**
   - Core types and interfaces
   - Type conversions and guards
   - Board representation

10. **[Constants and Configuration](./10-constants-config.md)**
    - Thresholds and formulas
    - Piece values
    - Engine settings
    - Performance limits

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Game Analysis Input                     │
│                    (PGN / State Tree)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Engine Evaluation                         │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ Lichess Cloud    │ ◄─────► │ Stockfish 17     │         │
│  │ (Preferred)      │ Fallback│ (Local)          │         │
│  └──────────────────┘         └──────────────────┘         │
│                                                              │
│  Output: Multi-PV Lines + Evaluations (CP / Mate)          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Node Extraction Layer                       │
│  • Extract previous position (before move)                  │
│  • Extract current position (after move)                    │
│  • Compute subjective evaluations                           │
│  • Identify top move and second-best move                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Classification Decision Tree                    │
│                                                              │
│  1. FORCED? ──────────────► Only 1 legal move?             │
│       │ No                                                   │
│       ▼                                                      │
│  2. THEORY? ──────────────► In opening book?               │
│       │ No                                                   │
│       ▼                                                      │
│  3. CHECKMATE? ───────────► Delivers mate?                  │
│       │ No                                                   │
│       ▼                                                      │
│  4. Point Loss ───────────► Calculate expected point loss   │
│       │                     (BEST/EXCELLENT/.../BLUNDER)    │
│       ▼                                                      │
│  5. CRITICAL? ─────────────► Top move + 2nd move weak?      │
│       │ No                                                   │
│       ▼                                                      │
│  6. BRILLIANT? ────────────► Sacrifice with compensation?   │
│                                                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Classification Output                     │
│  • Move classification (enum)                               │
│  • Accuracy score (0-100)                                   │
│  • Opening name (if applicable)                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Algorithms

### Expected Points Calculation
```
Win Probability = 1 / (1 + e^(-0.0035 × centipawns))
```
Converts engine evaluation to expected game outcome (0.0 = certain loss, 1.0 = certain win).

### Point Loss
```
Point Loss = max(0, EP(before) - EP(after)) × perspective_multiplier
```
Measures the decrease in win probability caused by a move.

### Move Accuracy
```
Accuracy = 103.16 × e^(-4 × pointLoss) - 3.17
```
Converts point loss into a 0-100 accuracy score.

## Implementation Notes

### Technology Stack
- **Language:** TypeScript/JavaScript
- **Chess Engine:** Stockfish 17 (via Web Workers)
- **Cloud Engine:** Lichess Cloud API
- **Chess Library:** chess.js
- **Execution:** Client-side browser (analysis), Server-side Node.js (game storage)

### Performance Characteristics
- **Depth:** 20 plies (default), configurable 15-30
- **Multi-PV:** 2 lines (required for CRITICAL classification)
- **Time:** ~2-5 seconds per position (cloud), ~5-15 seconds (local)
- **Complexity:** O(n) for basic classifications, O(n²) for BRILLIANT (piece safety)

### Configuration
All classifications can be toggled via `AnalysisOptions`:
```typescript
{
  includeTheory: boolean,      // Enable THEORY classification
  includeCritical: boolean,    // Enable CRITICAL classification
  includeBrilliant: boolean    // Enable BRILLIANT classification (expensive)
}
```

## Quick Reference

### Classification Priority Order
1. **FORCED** (highest priority)
2. **THEORY**
3. **CHECKMATE → BEST**
4. **Point Loss** (BEST/EXCELLENT/OKAY/INACCURACY/MISTAKE/BLUNDER)
5. **CRITICAL** (refines BEST)
6. **BRILLIANT** (refines BEST+)

### Point Loss Thresholds
| Classification | Point Loss Range | Win % Loss |
|---------------|------------------|------------|
| BEST          | < 0.01           | < 1%       |
| EXCELLENT     | 0.01 - 0.045     | 1% - 4.5%  |
| OKAY          | 0.045 - 0.08     | 4.5% - 8%  |
| INACCURACY    | 0.08 - 0.12      | 8% - 12%   |
| MISTAKE       | 0.12 - 0.22      | 12% - 22%  |
| BLUNDER       | ≥ 0.22           | ≥ 22%      |

### Special Thresholds
- **CRITICAL:** Second-best move loses ≥ 0.10 points (10%)
- **Completely Winning:** Evaluation ≥ 700 centipawns (+7.00)

## Related Documentation

- **[Contributing Guide](../contributing.md)** - How to contribute to Wintrchess
- **[Hosting Guide](../hosting.md)** - Self-hosting instructions
- **[README](../readme.md)** - Project overview

## Version

**Architecture Version:** 1.0  
**Last Updated:** 2024  
**Wintrchess Version:** Current (main branch)

---

*This documentation describes the production system as implemented in the Wintrchess open-source project.*


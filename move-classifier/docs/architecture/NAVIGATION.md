# Navigation Guide

Quick reference for finding specific topics in the architecture documentation.

## By Topic

### Preprocessing and Setup
- **PGN parsing** → [00-preprocessing-pipeline.md](./00-preprocessing-pipeline.md#stage-1-parse-game-into-state-tree)
- **State tree building** → [00-preprocessing-pipeline.md](./00-preprocessing-pipeline.md#stage-1-parse-game-into-state-tree)
- **Engine analysis** → [00-preprocessing-pipeline.md](./00-preprocessing-pipeline.md#stage-2-engine-analysis)
- **Cloud evaluation (Lichess)** → [00-preprocessing-pipeline.md](./00-preprocessing-pipeline.md#process-a-cloud-evaluation-lichess)
- **Local engine (Stockfish)** → [00-preprocessing-pipeline.md](./00-preprocessing-pipeline.md#process-b-local-engine-stockfish-uci)
- **Node extraction** → [00-preprocessing-pipeline.md](./00-preprocessing-pipeline.md#stage-4-extract-nodes)
- **Expected points calculation** → [00-preprocessing-pipeline.md](./00-preprocessing-pipeline.md#expected-points)

### Chess Fundamentals
- **FEN notation** → [01-core-concepts.md](./01-core-concepts.md#fen-forsyth-edwards-notation)
- **SAN notation** → [01-core-concepts.md](./01-core-concepts.md#san-standard-algebraic-notation)
- **UCI notation** → [01-core-concepts.md](./01-core-concepts.md#uci-universal-chess-interface-notation)
- **Engine evaluations** → [01-core-concepts.md](./01-core-concepts.md#engine-evaluations)

### Classification Logic
- **Decision flow** → [02-classification-overview.md](./02-classification-overview.md#decision-flow-waterfall-logic)
- **Priority order** → [02-classification-overview.md](./02-classification-overview.md#classification-hierarchy)
- **FORCED moves** → [03-basic-classifications.md](./03-basic-classifications.md#forced-classification)
- **THEORY moves** → [03-basic-classifications.md](./03-basic-classifications.md#theory-classification)
- **CHECKMATE** → [03-basic-classifications.md](./03-basic-classifications.md#checkmate--best-classification)
- **Point loss** → [04-point-loss-classification.md](./04-point-loss-classification.md)
- **CRITICAL** → [05-advanced-classifications.md](./05-advanced-classifications.md#critical-classification)
- **BRILLIANT** → [05-advanced-classifications.md](./05-advanced-classifications.md#brilliant-classification)

### Mathematical Concepts
- **Expected points** → [01-core-concepts.md](./01-core-concepts.md#expected-points-and-win-probability)
- **Win probability** → [01-core-concepts.md](./01-core-concepts.md#expected-points-and-win-probability)
- **Point loss formula** → [04-point-loss-classification.md](./04-point-loss-classification.md#point-loss-calculation)
- **Accuracy formula** → [10-constants-config.md](./10-constants-config.md#move-accuracy)
- **Sigmoid function** → [01-core-concepts.md](./01-core-concepts.md#for-centipawn-evaluations)

### Technical Implementation
- **Data structures** → [09-data-structures.md](./09-data-structures.md)
- **Type definitions** → [09-data-structures.md](./09-data-structures.md)
- **Constants** → [10-constants-config.md](./10-constants-config.md)
- **Thresholds** → [10-constants-config.md](./10-constants-config.md#classification-thresholds)
- **Configuration** → [10-constants-config.md](./10-constants-config.md#analysis-options)

### Supporting Systems
- **Piece safety** → [06-attack-defense.md](./06-attack-defense.md#piece-safety)
- **Attack analysis** → [06-attack-defense.md](./06-attack-defense.md#direct-attacks)
- **X-ray attacks** → [06-attack-defense.md](./06-attack-defense.md#x-ray-attacks)
- **Defender analysis** → [06-attack-defense.md](./06-attack-defense.md#defenders)
- **Danger levels** → [07-tactical-analysis.md](./07-tactical-analysis.md#danger-levels)
- **Trapped pieces** → [07-tactical-analysis.md](./07-tactical-analysis.md#trapped-pieces)
- **Piece values** → [07-tactical-analysis.md](./07-tactical-analysis.md#piece-values)

### Utilities
- **FEN parsing** → [08-utilities.md](./08-utilities.md#fen-parsing)
- **Move parsing** → [08-utilities.md](./08-utilities.md#move-parsing)
- **Node extraction** → [08-utilities.md](./08-utilities.md#node-extraction)
- **Board manipulation** → [08-utilities.md](./08-utilities.md#board-manipulation)

## By Use Case

### "I want to understand how the system works"
1. [README.md](./README.md) - Overview
2. [02-classification-overview.md](./02-classification-overview.md) - Decision flow
3. [04-point-loss-classification.md](./04-point-loss-classification.md) - Core algorithm

### "I want to implement this in another language"
1. **[00-preprocessing-pipeline.md](./00-preprocessing-pipeline.md)** - Complete pre-classification flow
2. [09-data-structures.md](./09-data-structures.md) - Types
3. [10-constants-config.md](./10-constants-config.md) - Constants
4. [02-classification-overview.md](./02-classification-overview.md) - Algorithm
5. [03-basic-classifications.md](./03-basic-classifications.md) - Simple cases
6. [04-point-loss-classification.md](./04-point-loss-classification.md) - Core
7. [05-advanced-classifications.md](./05-advanced-classifications.md) - Complex cases
8. [06-attack-defense.md](./06-attack-defense.md) - Supporting logic

### "I want to understand the math"
1. [01-core-concepts.md](./01-core-concepts.md) - Expected points
2. [10-constants-config.md](./10-constants-config.md) - Formulas
3. [04-point-loss-classification.md](./04-point-loss-classification.md) - Application

### "I want to modify thresholds/config"
1. [10-constants-config.md](./10-constants-config.md) - All constants
2. [02-classification-overview.md](./02-classification-overview.md#configuration-options) - Options

### "I want to understand BRILLIANT moves"
1. [05-advanced-classifications.md](./05-advanced-classifications.md#brilliant-classification) - Algorithm
2. [06-attack-defense.md](./06-attack-defense.md) - Piece safety
3. [07-tactical-analysis.md](./07-tactical-analysis.md) - Danger levels & trapped pieces

## File Size Reference

| File | Lines | Complexity |
|------|-------|------------|
| README.md | ~240 | Overview |
| 00-preprocessing-pipeline.md | ~1900 | Comprehensive |
| 01-core-concepts.md | 433 | Foundational |
| 02-classification-overview.md | 385 | Core |
| 03-basic-classifications.md | 363 | Simple |
| 04-point-loss-classification.md | 129 | Core |
| 05-advanced-classifications.md | 186 | Complex |
| 06-attack-defense.md | 90 | Supporting |
| 07-tactical-analysis.md | 90 | Supporting |
| 08-utilities.md | 113 | Reference |
| 09-data-structures.md | 177 | Reference |
| 10-constants-config.md | 169 | Reference |

---

**Tip:** Use your editor's "Find in Files" to search across all documents for specific terms.

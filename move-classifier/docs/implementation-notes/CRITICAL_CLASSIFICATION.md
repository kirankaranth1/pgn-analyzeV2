# Critical Classification Implementation

## Overview

Successfully implemented CRITICAL move classification following the JavaScript logic. Critical moves are top engine moves where playing the second-best move would result in ≥10% point loss (expected points).

## Files Created

### 1. `src/classification/critical_move.py`
Contains the `is_move_critical_candidate()` function that checks preliminary conditions:
- Position not completely winning even with second-best move (< 700 centipawns)
- Move not in losing position (subjective eval ≥ 0)
- Not a queen promotion
- Not escaping check (not forced)

### 2. `src/classification/critical_classifier.py`
Contains the `consider_critical_classification()` function that determines if a move is critical:
- Must pass candidate check
- Not finding mate (mate value > 0)
- Not capturing free material (hanging pieces)
- Must have second-best engine line
- Second-best move must lose ≥10% expected points

## Integration

### Updated Files

1. **`src/classification/classifier.py`**
   - Removed stub for `_consider_critical_classification()`
   - Imported `consider_critical_classification()` from `critical_classifier.py`
   - Critical classification runs after point loss, before brilliant
   - Only considers CRITICAL if top move was played

2. **`src/utils/chess_utils.py`**
   - Added missing utility functions: `generate_unique_id()`, `chess_color_to_piece_color()`, `is_black_to_move()`
   - Required by other modules in the codebase

3. **`visualize_capablanca_nodes.py`**
   - Added CRITICAL to classification display
   - Shows "Only move preventing significant loss (≥10% point loss)"
   - Added CRITICAL to summary statistics

## Test Results

✅ All 8 existing classifier tests pass
✅ Critical classification integrated without breaking existing functionality

## Real-World Example: Morphy Game

Running the famous Morphy vs Duke/Count game (1858 Opera House):

```
🎯 CLASSIFICATION SUMMARY:
  FORCED (only 1 legal move):        1
  THEORY (in opening book):           5
  BEST (top move or checkmate):       13
  CRITICAL (prevents major loss):     3    ← NEW!
  EXCELLENT (point loss < 0.045):     5
  GOOD (point loss < 0.08):           3
  INACCURACY (point loss < 0.12):     2
  MISTAKE (point loss < 0.22):        0
  BLUNDER (point loss ≥ 0.22):        0
  N/A (extraction failed):            1
```

**3 critical moves detected** where Morphy played the only move that prevented significant advantage loss!

## Classification Priority

The classification logic follows this priority (JavaScript equivalent):

1. **FORCED** - Only 1 legal move
2. **THEORY** - Position in opening book  
3. **CHECKMATE** → BEST
4. **Top move played** → BEST, then check for CRITICAL
5. **Not top move** → Point loss classification (EXCELLENT, GOOD, INACCURACY, MISTAKE, BLUNDER)
6. **BRILLIANT** (stub, not yet implemented)

## Critical Classification Criteria

A move is **CRITICAL** if ALL of these are true:

1. ✅ Top engine move was played
2. ✅ Position is winning but not completely winning (subjective eval > 0, < 700cp for second-best)
3. ✅ Not a queen promotion
4. ✅ Not escaping check
5. ✅ Not finding mate (subjective eval is not mate > 0)
6. ✅ Not capturing free material (unsafe pieces)
7. ✅ Second-best move exists
8. ✅ Second-best move loses ≥10% expected points (≥0.1 point loss)

## Usage

### Via Classifier

```python
from src.classification import Classifier
from src.config import ClassificationConfig

classifier = Classifier(config=ClassificationConfig(include_critical=True))
classification = classifier.classify(node)  # May return Classification.CRITICAL
```

### Via Visualizer

```bash
python visualize_capablanca_nodes.py morphy \
  --with-engine \
  --depth 16 \
  --cloud \
  --classify
```

### Disable Critical Classification

```python
config = ClassificationConfig(include_critical=False)
classifier = Classifier(config=config)
```

## Next Steps

- ✅ Critical classification implemented
- ⏸️ Brilliant classification (stub exists, uses critical candidate check)
- 📋 The tactical utilities (attackers, defenders, piece safety) are ready for brilliant classification

## Dependencies

Critical classification uses:
- `piece_safety.is_piece_safe()` - Check if captured piece was hanging
- `evaluation_utils.get_expected_points_loss()` - Calculate point loss for second-best move
- `critical_move.is_move_critical_candidate()` - Preliminary checks
- Requires second engine line (MultiPV ≥ 2)


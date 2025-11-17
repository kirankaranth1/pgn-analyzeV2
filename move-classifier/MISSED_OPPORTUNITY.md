# Missed Opportunity Classification

## Overview

The "Missed Opportunity" classification is an **additional tag** that can be applied on top of existing move classifications (INACCURACY, MISTAKE, or BLUNDER). It identifies situations where a player failed to capitalize on their opponent's previous error.

## Classification Logic

A move is tagged as a **MISSED OPPORTUNITY** when ALL of the following conditions are met:

1. **Current move must be suboptimal**: The move being evaluated is classified as:
   - `INACCURACY`
   - `MISTAKE`
   - `BLUNDER`

2. **Opponent's previous move was an error**: The immediately preceding move by the opponent was classified as:
   - `MISTAKE`
   - `BLUNDER`

## Implementation Details

### Core Components

1. **`MoveClassificationResult`** (`src/models/enums.py`)
   ```python
   @dataclass
   class MoveClassificationResult:
       classification: Classification
       is_missed_opportunity: bool = False
   ```
   - Replaces plain `Classification` enum returns
   - Stores both primary classification and missed opportunity flag

2. **`consider_missed_opportunity_classification()`** (`src/classification/missed_opportunity_classifier.py`)
   - Implements the simple 2-condition logic
   - No additional point loss calculations
   - Returns `True` if move should be tagged as missed opportunity

3. **`Classifier` class updates** (`src/classification/classifier.py`)
   - Tracks `_last_classification` to know opponent's previous move classification
   - Returns `MoveClassificationResult` instead of `Classification`
   - Calls `consider_missed_opportunity_classification()` when enabled

4. **`ClassificationConfig`** (`src/config.py`)
   ```python
   include_missed_opportunity: bool = True
   ```
   - Enables/disables missed opportunity detection

### Visualizer Integration

The visualizer (`visualize_game.py`) now:
- Displays missed opportunity tag alongside primary classification
- Shows count of missed opportunities in the summary
- Adds explanatory note: "Failed to capitalize on opponent's mistake/blunder"

## Examples

### Example 1: Missed Opportunity Detected
```
Move 12: Rook to d1
  Classification: INACCURACY + MISSED OPPORTUNITY
  Reason:         Moderate point loss (< 0.12)
  Note:           Failed to capitalize on opponent's mistake/blunder
```

### Example 2: No Missed Opportunity
```
Move 13: Knight to f6
  Classification: INACCURACY
  Reason:         Moderate point loss (< 0.12)
```
(No missed opportunity tag because opponent's previous move was not a MISTAKE or BLUNDER)

## Usage

### In Code
```python
from src.classification import Classifier
from src.config import ClassificationConfig

# Enable missed opportunity detection (default)
config = ClassificationConfig(include_missed_opportunity=True)
classifier = Classifier(config=config)

# Classify a move
result = classifier.classify(node)

print(f"Classification: {result.classification.value}")
if result.is_missed_opportunity:
    print("⚠️ This was a missed opportunity!")
```

### With Visualizer
```bash
# Show missed opportunities in game analysis
python visualize_game.py morphy --with-engine --classify

# Disable missed opportunity detection
python visualize_game.py morphy --with-engine --classify \
  --config '{"include_missed_opportunity": false}'
```

## Design Principles

1. **Simplicity**: Only uses opponent's previous classification (no complex calculations)
2. **Non-invasive**: Additional tag, doesn't replace primary classification
3. **Context-aware**: Requires tracking game state across moves
4. **Configurable**: Can be enabled/disabled via `ClassificationConfig`

## Related Classifications

- **BRILLIANT**: Sacrifice or risky move that works out
- **CRITICAL**: Only move that maintains advantage
- **BLUNDER/MISTAKE/INACCURACY**: Point loss classifications

## Testing

Run tests with:
```bash
pytest tests/unit/test_missed_opportunity.py
```

## Future Enhancements

Potential improvements (not currently implemented):
- Track severity of missed opportunity (how big was the opponent's mistake?)
- Identify specific tactical themes that were missed
- Calculate "cost" of the missed opportunity in centipawns


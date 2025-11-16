# JavaScript Implementation Alignment

## Overview

This document describes how the Python preprocessing pipeline and data structures have been updated to match the JavaScript implementation from `ExtractNode.ts` and `ExtractedNode.ts`.

## Changes Made

### 1. Data Structures (`src/models/extracted_nodes.py`)

Updated the `ExtractedPreviousNode` and `ExtractedCurrentNode` dataclasses to match the JavaScript interfaces:

#### ExtractedPreviousNode
- `topMove`: **REQUIRED** (matches JS)
- `subjective_evaluation`: **OPTIONAL** (matches JS: `subjectiveEvaluation?`)
- `played_move`: **OPTIONAL** (matches JS: `playedMove?`)
- Added second-best move fields: `second_top_line`, `second_top_move`, `second_subjective_evaluation`

#### ExtractedCurrentNode
- `topMove`: **OPTIONAL** (matches JS: `topMove?`)
- `subjective_evaluation`: **REQUIRED** (matches JS)
- `played_move`: **REQUIRED** (matches JS)
- Added second-best move fields: `second_top_line`, `second_top_move`, `second_subjective_evaluation`

### 2. Extraction Logic (`src/preprocessing/node_extractor.py`)

Refactored extraction functions to match JavaScript implementation:

#### New Helper Functions

1. **`_safe_move(fen: str, move: Union[str, chess.Move]) -> Optional[chess.Move]`**
   - Matches JavaScript `safeMove()` function
   - Returns `None` instead of raising exceptions when move parsing fails
   - Safely parses SAN moves and validates them in the given position

2. **`_extract_second_top_move(node, top_line, player_color)`**
   - Matches JavaScript `extractSecondTopMove()` function
   - Extracts the second-best engine line and move
   - Calculates subjective evaluation for the second-best move
   - Returns tuple: `(second_top_line, second_top_move, second_subjective_eval)`

#### Updated Extraction Functions

1. **`extract_previous_state_tree_node()`**
   - Matches JavaScript `extractPreviousStateTreeNode()`
   - Uses `_safe_move()` for all move parsing
   - Defaults to `PieceColor.WHITE` when no played move exists (matches JS: `playedMove?.color || WHITE`)
   - Returns `None` if top move cannot be extracted
   - Includes second-best move extraction

2. **`extract_current_state_tree_node()`**
   - Matches JavaScript `extractCurrentStateTreeNode()`
   - Requires parent node (returns `None` if missing)
   - Top move is optional (can be `None`)
   - Played move is required (returns `None` if missing)
   - Subjective evaluation is always calculated (required field)
   - Includes second-best move extraction

### 3. Key Logic Changes

#### Player Color Determination
```python
# Previous node - uses played move color or defaults to WHITE
if played_move:
    parent_board = chess.Board(node.parent.state.fen)
    player_color = PieceColor.WHITE if parent_board.turn == chess.WHITE else PieceColor.BLACK
else:
    player_color = PieceColor.WHITE  # Default (matches JS)

# Current node - always uses parent board turn
parent_board = chess.Board(node.parent.state.fen)
player_color = PieceColor.WHITE if parent_board.turn == chess.WHITE else PieceColor.BLACK
```

#### Error Handling
```python
# Old approach - raised exceptions
try:
    top_move = board.parse_san(top_move_san)
except (ValueError, chess.IllegalMoveError):
    return None

# New approach - uses _safe_move()
top_move = _safe_move(node.state.fen, top_move_san)
if not top_move:
    return None
```

## Usage Example

Both `ExtractedPreviousNode` and `ExtractedCurrentNode` are required for classification:

```python
from src.preprocessing.node_extractor import (
    extract_previous_state_tree_node,
    extract_current_state_tree_node
)
from src.classification.basic_classifier import BasicClassifier

# Extract both nodes
previous_node = extract_previous_state_tree_node(parent_state_node)
current_node = extract_current_state_tree_node(state_node)

if previous_node and current_node:
    # Use both nodes for classification
    classifier = BasicClassifier()
    classification = classifier.classify(previous_node, current_node)
```

## Compatibility with JavaScript

The Python implementation now mirrors the JavaScript logic:

| Feature | JavaScript | Python | Status |
|---------|-----------|--------|--------|
| `safeMove()` function | ✓ | `_safe_move()` | ✅ Matching |
| `extractSecondTopMove()` | ✓ | `_extract_second_top_move()` | ✅ Matching |
| Previous node extraction | ✓ | `extract_previous_state_tree_node()` | ✅ Matching |
| Current node extraction | ✓ | `extract_current_state_tree_node()` | ✅ Matching |
| Required/Optional fields | ✓ | Dataclass fields | ✅ Matching |
| Player color default (WHITE) | ✓ | `PieceColor.WHITE` | ✅ Matching |
| Second-best move extraction | ✓ | Included in both nodes | ✅ Matching |

## Testing

All existing tests pass with the new implementation:
- ✅ Unit tests: 62 passed, 1 skipped
- ✅ Integration tests: 61 passed (excluding engine tests)

## Benefits

1. **Consistency**: Python and JavaScript implementations now follow the same logic
2. **Robustness**: Better error handling with `_safe_move()` function
3. **Completeness**: Second-best moves are now properly extracted
4. **Type Safety**: Clear distinction between required and optional fields
5. **Classification**: Both nodes available for comprehensive move analysis

## Files Modified

- `src/models/extracted_nodes.py` - Updated data structures
- `src/preprocessing/node_extractor.py` - Updated extraction logic

## Files Verified Compatible

- `src/classification/basic_classifier.py` - Uses both node types correctly
- `src/preprocessing/calculator.py` - Works with updated structures
- `tests/unit/test_basic_classifier.py` - All tests pass
- `tests/integration/test_preprocessing_pipeline.py` - All tests pass


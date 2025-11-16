# Preprocessing Pipeline: JavaScript Alignment

## Architecture Overview

```
StateTreeNode (position before move)
        ↓
    [Extract Previous Node]
        ↓
ExtractedPreviousNode
    • board: chess.Board
    • top_move: Move (REQUIRED)
    • subjective_evaluation: Evaluation (optional)
    • played_move: Move (optional)
    • second_top_line, second_top_move (optional)
        
        +
        
StateTreeNode (position after move)
        ↓
    [Extract Current Node]
        ↓
ExtractedCurrentNode
    • board: chess.Board
    • top_move: Move (optional)
    • subjective_evaluation: Evaluation (REQUIRED)
    • played_move: Move (REQUIRED)
    • second_top_line, second_top_move (optional)
        
        ↓
        
    [Classification]
        ↓
    Move Quality Label
```

## Extraction Flow

### Previous Node Extraction
```
Input: StateTreeNode
    ↓
Get top engine line → Return None if missing
    ↓
Get top move (first from line) → Return None if missing
    ↓
Parse top move with _safe_move() → Return None if invalid
    ↓
Get played move from child (if exists)
    ↓
Determine player color:
    - If played_move exists → Use parent board turn
    - Otherwise → Default to WHITE (matches JS)
    ↓
Calculate subjective evaluation
    ↓
Extract second-best move (optional)
    ↓
Return ExtractedPreviousNode
```

### Current Node Extraction
```
Input: StateTreeNode
    ↓
Check has parent → Return None if missing
    ↓
Get top engine line → Return None if missing
    ↓
Get top move (optional, can be None)
    ↓
Get played move → Return None if missing
    ↓
Parse played move with _safe_move() → Return None if invalid
    ↓
Determine player color from parent board turn
    ↓
Calculate subjective evaluation (REQUIRED)
    ↓
Extract second-best move (optional)
    ↓
Return ExtractedCurrentNode
```

## Key Helper Functions

### _safe_move(fen, move)
```
JavaScript: safeMove(fen, move)

Purpose: Safely parse and validate a move
Returns: chess.Move | None

try:
    board = chess.Board(fen)
    if isinstance(move, str):
        return board.parse_san(move)
    else:
        if move in board.legal_moves:
            return move
except:
    return None
```

### _extract_second_top_move(node, top_line, player_color)
```
JavaScript: extractSecondTopMove(node, topLine)

Purpose: Extract second-best engine line and move
Returns: (second_line, second_move, second_eval) | (None, None, None)

Get line_group_sibling with index=2
    ↓
If found and has moves:
    Parse first move with _safe_move()
    Calculate subjective evaluation
    ↓
Return tuple
```

## Data Structure Comparison

### ExtractedPreviousNode

| Field | JavaScript | Python | Notes |
|-------|-----------|--------|-------|
| board | Chess | chess.Board | Position state |
| state | BoardState | BoardState | Full position data |
| topLine | EngineLine | EngineLine | Best engine line |
| topMove | Move | Move | **REQUIRED** in both |
| evaluation | Evaluation | Evaluation | White's perspective |
| subjectiveEvaluation | Evaluation? | Optional[Evaluation] | Player's perspective |
| playedMove | Move? | Optional[Move] | Actually played |
| secondTopLine | EngineLine? | Optional[EngineLine] | 2nd best line |
| secondTopMove | Move? | Optional[Move] | 2nd best move |
| secondSubjectiveEvaluation | Evaluation? | Optional[Evaluation] | 2nd best eval |

### ExtractedCurrentNode

| Field | JavaScript | Python | Notes |
|-------|-----------|--------|-------|
| board | Chess | chess.Board | Position state |
| state | BoardState | BoardState | Full position data |
| topLine | EngineLine | EngineLine | Best continuation |
| topMove | Move? | Optional[Move] | **OPTIONAL** in both |
| evaluation | Evaluation | Evaluation | White's perspective |
| subjectiveEvaluation | Evaluation | Evaluation | **REQUIRED** in both |
| playedMove | Move | Move | **REQUIRED** in both |
| secondTopLine | EngineLine? | Optional[EngineLine] | 2nd best line |
| secondTopMove | Move? | Optional[Move] | 2nd best move |
| secondSubjectiveEvaluation | Evaluation? | Optional[Evaluation] | 2nd best eval |

## Player Color Logic

### Previous Node
```javascript
// JavaScript
const playedMove = node.parent && node.state.move
    && safeMove(node.parent.state.fen, node.state.move.san);

const subjectiveEvaluation = getSubjectiveEvaluation(
    topLine.evaluation,
    adaptPieceColour(playedMove?.color || WHITE)
);
```

```python
# Python
if played_move:
    parent_board = chess.Board(node.parent.state.fen)
    player_color = PieceColor.WHITE if parent_board.turn == chess.WHITE else PieceColor.BLACK
else:
    player_color = PieceColor.WHITE  # Default (matches JS)

subjective_evaluation = get_subjective_evaluation(
    top_line.evaluation,
    player_color
)
```

### Current Node
```javascript
// JavaScript
const playedMove = safeMove(node.parent.state.fen, playedMoveSan);

const subjectiveEvaluation = getSubjectiveEvaluation(
    topLine.evaluation,
    adaptPieceColour(playedMove?.color || WHITE)
);
```

```python
# Python
parent_board = chess.Board(node.parent.state.fen)
player_color = PieceColor.WHITE if parent_board.turn == chess.WHITE else PieceColor.BLACK

subjective_evaluation = get_subjective_evaluation(
    top_line.evaluation,
    player_color
)
```

## Usage in Classification

```python
# Both nodes required for classification
previous_node = extract_previous_state_tree_node(parent_state_node)
current_node = extract_current_state_tree_node(state_node)

if previous_node and current_node:
    # Basic classification
    basic_result = basic_classifier.classify(previous_node, current_node)
    
    # Advanced classification (future)
    # advanced_result = advanced_classifier.classify(previous_node, current_node)
    
    # Point loss classification (future)
    # point_loss = calculate_point_loss(previous_node, current_node)
```

## Testing Coverage

✅ **Unit Tests (62 passed, 1 skipped)**
- Opening book loading and lookup
- Basic classifier rules (FORCED, THEORY, CHECKMATE)
- Classification priority
- Direct classification from state tree nodes

✅ **Integration Tests (87 passed, 3 skipped)**
- Full preprocessing pipeline
- Real game analysis (Capablanca-Marshall, Morphy Opera Game)
- Node extraction with engine analysis
- Move accuracy calculation
- **JavaScript alignment verification (7 tests)**

✅ **JavaScript Alignment Tests (7 passed)**
- Previous node extraction with second-best moves
- Current node extraction with second-best moves
- Player color defaults to WHITE
- Current node requires parent
- Current node requires played move
- Safe move parsing
- End-to-end classification integration

## Code Coverage

```
src/preprocessing/node_extractor.py    92% coverage
src/models/extracted_nodes.py          100% coverage
src/utils/evaluation_utils.py          93% coverage
Overall:                               89% coverage
```

## Migration Checklist

- ✅ Data structures updated (`ExtractedPreviousNode`, `ExtractedCurrentNode`)
- ✅ Helper functions implemented (`_safe_move`, `_extract_second_top_move`)
- ✅ Previous node extraction aligned with JavaScript
- ✅ Current node extraction aligned with JavaScript
- ✅ Player color logic matches JavaScript
- ✅ Second-best move extraction working
- ✅ All existing tests pass
- ✅ New alignment tests added
- ✅ Documentation created
- ✅ Backward compatibility maintained

## References

- JavaScript source: `ExtractNode.ts`, `ExtractedNode.ts`
- Python implementation: `src/preprocessing/node_extractor.py`, `src/models/extracted_nodes.py`
- Tests: `tests/integration/test_javascript_alignment.py`
- Documentation: `JAVASCRIPT_ALIGNMENT.md`, `SUMMARY_OF_CHANGES.md`


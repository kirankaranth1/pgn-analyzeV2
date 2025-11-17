# Preprocessing Pipeline Implementation

This document describes the complete implementation of the 5-stage preprocessing pipeline for the chess move classifier.

## Overview

The preprocessing pipeline transforms raw PGN game data into structured, analyzed data ready for classification. It consists of 5 sequential stages:

```
PGN String → State Tree → Engine Analysis → Node Chain → Extracted Nodes → Classification-Ready Data
```

## Quick Start

### Basic Usage

```python
from src.preprocessing import run_full_preprocessing_pipeline

# Simple usage with defaults (depth=16, multi_pv=2)
root_node = run_full_preprocessing_pipeline("1. e4 e5 2. Nf3 Nc6")

# The root_node now contains the complete analyzed game tree
```

### With Custom Configuration

```python
from src.preprocessing import run_full_preprocessing_pipeline
from src.config import EngineConfig

# Configure engine analysis
config = EngineConfig(
    depth=16,              # Search depth in plies
    multi_pv=2,            # Number of principal variations
    use_cloud_eval=True,   # Try Lichess cloud API first
    stockfish_path=None    # Auto-detect Stockfish (or specify path)
)

root_node = run_full_preprocessing_pipeline(
    pgn="1. e4 e5 2. Nf3 Nc6 3. Bb5",
    initial_position=None,  # Optional: custom starting position (FEN)
    config=config
)
```

## The 5 Stages

### Stage 1: Parse PGN to State Tree

Converts PGN notation into a tree structure representing all positions.

```python
from src.preprocessing.parser import parse_pgn_game

root_node = parse_pgn_game("1. e4 e5 2. Nf3")
```

**Output:** `StateTreeNode` with tree structure containing:
- Position (FEN)
- Moves (SAN and UCI)
- Parent/child relationships
- Mainline vs variation flags

### Stage 2: Engine Analysis

Adds engine evaluations using Lichess cloud API or local Stockfish.

```python
from src.preprocessing.engine_analyzer import analyze_state_tree
from src.config import EngineConfig

config = EngineConfig(depth=16, multi_pv=2)
analyze_state_tree(root_node, config)
```

**Features:**
- **Cloud-first:** Tries Lichess API first (faster, no setup)
- **Fallback:** Uses local Stockfish if cloud fails
- **MultiPV:** Analyzes multiple best moves (configurable)
- **Normalized evaluations:** All from White's perspective

### Stage 3: Build Node Chain

Converts tree to linear array for sequential processing.

```python
from src.preprocessing.node_chain_builder import get_node_chain

# Mainline only
mainline_nodes = get_node_chain(root_node, expand_all_variations=False)

# Include all variations
all_nodes = get_node_chain(root_node, expand_all_variations=True)
```

### Stage 4: Extract Nodes

Creates simplified structures for classification.

```python
from src.preprocessing.node_extractor import (
    extract_previous_state_tree_node,
    extract_current_state_tree_node
)

# For a given node
previous = extract_previous_state_tree_node(node.parent)
current = extract_current_state_tree_node(node)
```

**Output:**
- `ExtractedPreviousNode`: Position before move
- `ExtractedCurrentNode`: Position after move

Both include:
- Chess board object
- Top engine line
- Best move
- Subjective evaluation (player's perspective)
- Second-best line (for CRITICAL classification)

### Stage 5: Calculate Derived Values

Computes metrics for classification.

```python
from src.preprocessing.calculator import calculate_move_metrics

point_loss, accuracy = calculate_move_metrics(previous, current)
```

**Calculated Values:**
- **Expected Points:** Win probability (0.0 to 1.0)
- **Point Loss:** Win probability lost by playing move
- **Move Accuracy:** 0-100 score based on point loss
- **Subjective Evaluation:** From player's perspective

## Configuration

### EngineConfig

```python
@dataclass
class EngineConfig:
    depth: int = 16                    # Search depth (default: 16)
    multi_pv: int = 2                  # Principal variations (default: 2)
    time_limit: Optional[int] = None   # Time limit in ms (optional)
    use_cloud_eval: bool = True        # Try cloud first (default: True)
    stockfish_path: Optional[str] = None  # Path to Stockfish (auto-detect if None)
```

## Requirements

### Required

- **python-chess** (>= 1.10.0) - Chess library for move parsing and board manipulation
- **requests** (>= 2.31.0) - HTTP client for Lichess API

### Optional

- **Stockfish** - UCI chess engine for local analysis (auto-detected in PATH)
  - Download: https://stockfishchess.org/download/
  - Or use cloud evaluation only

## Engine Sources

The system supports two engine sources:

### 1. Lichess Cloud API

**Advantages:**
- No setup required
- Fast (cached evaluations)
- Free

**Limitations:**
- Requires internet connection
- Limited to existing positions in database
- Fixed depth (varies by position popularity)

**Usage:** Enabled by default when `use_cloud_eval=True`

### 2. Local Stockfish

**Advantages:**
- Works offline
- Configurable depth and time
- Analyzes any position
- Consistent quality

**Requirements:**
- Stockfish binary in PATH or specified path
- More compute time per position

**Usage:** Automatically used as fallback or when cloud disabled

## Data Flow

Complete data flow through the pipeline:

```
Input: PGN String
  ↓
[Stage 1: parser.py]
  → StateTreeNode (root)
  ↓
[Stage 2: engine_analyzer.py]
  → StateTreeNode (with engine lines)
  ↓
[Stage 3: node_chain_builder.py]
  → List[StateTreeNode]
  ↓
[Stage 4: node_extractor.py]
  → (ExtractedPreviousNode, ExtractedCurrentNode)
  ↓
[Stage 5: calculator.py]
  → StateTreeNode (with accuracy scores)
  ↓
Output: Classification-ready data
```

## Key Formulas

### Expected Points

Converts evaluations to win probability:

```python
EP = 1 / (1 + e^(-0.0035 × centipawns))
```

### Point Loss

Win probability lost by playing a move:

```python
loss = max(0, EP_before - EP_after)  # With perspective adjustment
```

### Move Accuracy

Converts point loss to 0-100 score:

```python
accuracy = 103.16 × e^(-4 × point_loss) - 3.17
```

## Error Handling

The pipeline handles various error conditions:

- **Invalid PGN:** Raises `ValueError` with details
- **No engine available:** Raises `FileNotFoundError` if Stockfish not found
- **Cloud API failure:** Automatically falls back to local engine
- **Missing engine lines:** Returns `None` from extraction (skips node)
- **Invalid moves:** Catches and handles `IllegalMoveError`

## Performance

### Time Complexity

- **Stage 1:** O(n) where n = moves
- **Stage 2:** O(n × d) where d = depth (dominates)
- **Stage 3:** O(n)
- **Stage 4:** O(n × m) where m = MultiPV lines
- **Stage 5:** O(n)

**Total:** O(n × d) dominated by engine analysis

### Optimization Tips

1. **Use cloud evaluation:** Much faster than local engine
2. **Lower depth:** Faster but less accurate (16 is good balance)
3. **Reduce MultiPV:** Only 2 lines needed for most classifications
4. **Cache results:** Store analyzed games for reuse

## Example Output

After preprocessing, each node contains:

```python
{
    "fen": "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
    "move": {"san": "Nf6", "uci": "g8f6"},
    "move_color": "BLACK",
    "engine_lines": [
        {
            "evaluation": {"type": "centipawn", "value": 15.0},
            "source": "lichess-cloud",
            "depth": 20,
            "index": 1,
            "moves": [{"san": "d3"}, {"san": "Be7"}, ...]
        }
    ],
    "accuracy": 98.5,
    "classification": None  # Added by classification module
}
```

## Next Steps

After preprocessing, the data is ready for classification:

```python
from src.classification import classify_move

# Get extracted nodes
previous, current = extract_node_pair(node)

# Classify the move
if previous and current:
    classification = classify_move(previous, current)
    node.state.classification = classification
```

## Troubleshooting

### "Stockfish not found in PATH"

- Install Stockfish: `brew install stockfish` (macOS) or download from website
- Or specify path: `EngineConfig(stockfish_path="/path/to/stockfish")`
- Or use cloud only: `EngineConfig(use_cloud_eval=True)` (fallback disabled)

### "Cloud evaluation failed"

- Check internet connection
- Position might not be in Lichess database (use local engine)
- API rate limiting (wait and retry)

### Slow analysis

- Reduce depth: `EngineConfig(depth=12)`
- Use cloud evaluation: `EngineConfig(use_cloud_eval=True)`
- Reduce MultiPV: `EngineConfig(multi_pv=1)`

## References

- Architecture docs: `docs/architecture/00-preprocessing-pipeline.md`
- Core concepts: `docs/architecture/01-core-concepts.md`
- python-chess: https://python-chess.readthedocs.io/
- Lichess API: https://lichess.org/api


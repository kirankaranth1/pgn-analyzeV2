# Tactical Analysis Utilities

Utilities for attackers, defenders, and piece safety detection required for advanced move classifications (brilliant and critical).

## Overview

These utilities provide low-level chess position analysis capabilities:
- **Attackers**: Detect pieces attacking a target square, including batteries
- **Defenders**: Detect pieces defending a target piece
- **Piece Safety**: Determine if pieces are safe or hanging

## Files Created

### 1. `src/constants.py` (updated)
Added `PIECE_VALUES` dictionary:
```python
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: float('inf')
}
```

### 2. `src/models/chess_types.py` (new)
Data structures for representing chess pieces and moves:
- `BoardPiece`: Represents a piece on the board with square, type, and color
- `RawMove`: Simplified move representation with piece, color, from/to squares
- Helper functions: `to_raw_move()`, `to_board_piece()`, `get_board_pieces()`

### 3. `src/utils/chess_utils.py` (new)
Chess utility functions:
- `set_fen_turn(fen, color)`: Modify FEN to set the turn
- `get_capture_square(move)`: Get the square where a capture occurs
- `flip_piece_color(color)`: Flip between WHITE and BLACK

### 4. `src/utils/attackers.py` (new)
Attack detection with battery support:
- `get_attacking_moves(board, piece, transitive=True)`: Get all moves attacking a piece
- Detects direct attackers (pieces that can immediately capture)
- Detects transitive attackers (pieces behind other pieces in batteries)

**Example:**
```python
from src.models.chess_types import BoardPiece
from src.utils.attackers import get_attacking_moves
import chess

board = chess.Board("8/8/8/2p5/3N4/8/8/8 w - - 0 1")
knight = BoardPiece(square=chess.D4, type=chess.KNIGHT, color=chess.WHITE)
attackers = get_attacking_moves(board, knight)
# Returns: [RawMove(piece=PAWN, from_square=C5, to_square=D4)]
```

### 5. `src/utils/defenders.py` (new)
Defender detection:
- `get_defending_moves(board, piece, transitive=True)`: Get all moves defending a piece

Defenders are determined by:
1. If attackers exist: simulate each capture and find recapturers
2. If no attackers: flip piece color and count attackers of flipped piece

### 6. `src/utils/piece_safety.py` (new)
Piece safety analysis:
- `is_piece_safe(board, piece, played_move=None)`: Check if a piece is safe
- `get_unsafe_pieces(board, color, played_move=None)`: Get all hanging pieces

**Safety Rules (in order):**
1. Special case: Favorable sacrifices (e.g., rook for 2 pieces)
2. If attacked by lower-value piece → unsafe
3. If defenders ≥ attackers → safe
4. If piece value < lowest attacker value AND has defender < lowest attacker value → safe
5. If defended by pawn → safe
6. Otherwise → unsafe

**Example:**
```python
from src.utils.piece_safety import is_piece_safe, get_unsafe_pieces

# Queen attacked by pawn (unsafe)
board = chess.Board("8/8/8/2p5/3Q4/8/8/8 w - - 0 1")
queen = BoardPiece(square=chess.D4, type=chess.QUEEN, color=chess.WHITE)
is_safe = is_piece_safe(board, queen)  # False

# Get all unsafe pieces
unsafe = get_unsafe_pieces(board, chess.WHITE)  # [queen]
```

## Testing

Created comprehensive test suite in `tests/unit/test_tactical_utils.py`:
- ✅ 10 passing tests covering:
  - Direct attackers
  - Multiple attackers
  - Transitive attackers (batteries)
  - Defenders
  - Piece safety with various scenarios
  - Piece values
  - Board piece utilities

## Usage in Advanced Classifications

These utilities will be used for:

### Brilliant Move Detection
- Check if move leaves pieces unsafe
- Detect if escaping trapped pieces
- Identify favorable sacrifices

### Critical Move Detection
- Identify hanging pieces before/after move
- Detect if opponent can create threats
- Analyze attack/defense balance

## API Summary

```python
# Import utilities
from src.models.chess_types import BoardPiece, get_board_pieces
from src.utils.attackers import get_attacking_moves
from src.utils.defenders import get_defending_moves
from src.utils.piece_safety import is_piece_safe, get_unsafe_pieces
from src.constants import PIECE_VALUES

# Get all pieces
pieces = get_board_pieces(board)

# Check attackers
attackers = get_attacking_moves(board, piece, transitive=True)

# Check defenders
defenders = get_defending_moves(board, piece, transitive=True)

# Check safety
safe = is_piece_safe(board, piece)

# Get all unsafe pieces
unsafe_pieces = get_unsafe_pieces(board, chess.WHITE)
```

## Implementation Notes

1. **Follows JavaScript Logic**: All functions closely match the TypeScript implementations
2. **Transitive Attacks**: Battery detection uses frontier-based algorithm to find pieces behind other pieces
3. **Type Safety**: Uses chess.py's built-in types (Square, PieceType, Color)
4. **Performance**: Efficient algorithms with early returns and minimal board copying

## Next Steps

These utilities are ready to be used when implementing:
- `_consider_brilliant_classification()` in `classifier.py`
- `_consider_critical_classification()` in `classifier.py`


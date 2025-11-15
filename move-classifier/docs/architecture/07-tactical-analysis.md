# Tactical Analysis

> Danger levels, trapped pieces, and material evaluation

[← Back to Index](./README.md)

## Danger Levels

### Concept

When a piece is left hanging, the opponent might not want to capture it if doing so creates a bigger counter-threat.

### Algorithm

```
hasDangerLevels(board, unsafePiece, attackingMoves) -> boolean
```

For each way the opponent can capture the unsafe piece:
1. Simulate the capture
2. Evaluate threats created
3. If counter-threat ≥ value of captured piece → protected

**Example:**
```
Queen on d5 (hanging)
If Bxd5, then Rxe8# (mate)
→ Queen protected by danger levels (mate threat > queen value)
```

---

## Trapped Pieces

### Definition

A piece is **trapped** if:
1. It is unsafe (under attack)
2. It cannot move to any safe square

### Algorithm

```
isPieceTrapped(board, piece) -> boolean
```

1. Check if piece is currently safe → not trapped
2. Generate all legal moves for the piece
3. For each move:
   - Simulate the move
   - Check if piece becomes safe
   - Check if move creates counter-threat
4. If NO moves make piece safe → trapped

**Usage:** Brilliant moves must NOT be escaping trapped pieces.

---

## Material Evaluation

### Piece Values

```
PAWN:   1
KNIGHT: 3
BISHOP: 3
ROOK:   5
QUEEN:  9
KING:   ∞
```

### Usage

- Determine if captures are favorable
- Calculate sacrifice value
- Compare attacker/defender values
- Identify "free" vs "compensated" material

---

## Implementation Reference

**Files:**
- `shared/src/lib/reporter/utils/dangerLevels.ts`
- `shared/src/lib/reporter/utils/pieceTrapped.ts`
- `shared/src/constants/utils.ts` (piece values)

---

[← Back to Index](./README.md) | [Next: Supporting Utilities →](./08-utilities.md)

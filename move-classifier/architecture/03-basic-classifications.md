# Basic Classifications

> Simple rule-based classifications: FORCED, THEORY, and CHECKMATE

[← Back to Index](./README.md) | [← Previous: Classification Overview](./02-classification-overview.md)

## Table of Contents

1. [FORCED Classification](#forced-classification)
2. [THEORY Classification](#theory-classification)
3. [CHECKMATE → BEST Classification](#checkmate--best-classification)

---

## FORCED Classification

### Overview

**Definition:** A move is FORCED when it is the only legal move available.

**Priority:** Highest (checked first in waterfall)

**Rationale:** No choice = no evaluation needed

### Algorithm

```
FUNCTION isForcedMove(board: ChessBoard) -> boolean:
    legalMoves = board.generateLegalMoves()
    RETURN legalMoves.length <= 1
```

**Note:** Uses `<= 1` to handle positions with zero legal moves (checkmate/stalemate), though these are typically filtered earlier.

### Examples

#### Example 1: King in Check with One Escape

```
FEN: 8/8/8/8/8/2r5/1K6/2r5 w - - 0 1
```

```
  a b c d e f g h
8 . . . . . . . .
7 . . . . . . . .
6 . . . . . . . .
5 . . . . . . . .
4 . . . . . . . .
3 . . r . . . . .
2 . K . . . . . .
1 . . r . . . . .
```

**White to move:**
- King on b2 is in check from rook on c1
- Only legal move: `Ka2` (escape to a2)
- All other squares attacked or blocked
- **Classification: FORCED** ✅

#### Example 2: Interposition is Only Move

```
FEN: 3qk3/8/8/8/8/8/5PPP/5RK1 w - - 0 1
```

```
  a b c d e f g h
8 . . . q k . . .
7 . . . . . . . .
6 . . . . . . . .
5 . . . . . . . .
4 . . . . . . . .
3 . . . . . . . .
2 . . . . . P P P
1 . . . . . R K .
```

**White to move:**
- King on g1 is in check from queen on d8
- Only legal move: `Rf1` (block with rook)
- King cannot move (f1, h1 still in check)
- **Classification: FORCED** ✅

#### Example 3: Zugzwang (Only Move, But Losing)

```
FEN: 8/8/5k2/8/6K1/6P1/8/8 w - - 0 50
```

```
  a b c d e f g h
8 . . . . . . . .
7 . . . . . . . .
6 . . . . . k . .
5 . . . . . . . .
4 . . . . . . K .
3 . . . . . . P .
2 . . . . . . . .
1 . . . . . . . .
```

**White to move:**
- Only legal move: `Kf4` (pawn on g3 is blocked by king)
- After `Kf4`, Black plays `Kf6` and will capture pawn
- Position is zugzwang (White would prefer not to move)
- **Classification: FORCED** ✅ (Even though it loses!)

### Edge Cases

**Multiple pieces, one legal move total:**
```
Even if you have 16 pieces, if only ONE total legal move exists,
it is FORCED.
```

**Stalemate:**
```
Stalemate positions (0 legal moves) are detected earlier in the
analysis pipeline and don't reach classification.
```

### Performance

**Complexity:** O(n) where n = number of legal moves (at most ~218, typically 20-40)

**Optimization:** Most chess libraries cache legal move generation, making this very fast.

---

## THEORY Classification

### Overview

**Definition:** A move is THEORY when the resulting position matches a known opening book.

**Priority:** Second (after FORCED)

**Rationale:** Opening moves are "correct by definition" according to established theory.

### Data Requirements

**Opening Book Database:**
- Format: JSON map of FEN → opening name
- Key: Piece placement only (first component of FEN)
- Value: Opening name string
- Source: `shared/src/resources/openings.json`

**Example Database:**
```json
{
  "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": "King's Pawn Opening",
  "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR": "King's Pawn Game",
  "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R": "King's Knight Opening"
}
```

### Algorithm

```
FUNCTION getOpeningName(fen: string, openingDb: Map) -> Optional<string>:
    // Extract piece placement (before first space)
    piecePlacement = fen.split(" ")[0]
    
    // Lookup in database
    IF piecePlacement IN openingDb:
        RETURN openingDb[piecePlacement]
    ELSE:
        RETURN None

FUNCTION classifyTheory(currentNode: ExtractedCurrentNode, options: Options) -> Optional<Classification>:
    IF NOT options.includeTheory:
        RETURN None
    
    openingName = getOpeningName(currentNode.state.fen, openingDatabase)
    
    IF openingName EXISTS:
        // Store opening name in node
        currentNode.state.opening = openingName
        RETURN Classification.THEORY
    
    RETURN None
```

### Why Piece Placement Only?

**Rationale:**
- Openings are defined by piece positions, not whose turn it is
- Same position can be reached via different move orders (transposition)
- Castling rights and en passant are positional features, not opening definitions

**Example:**
```
Position after 1.e4 e5:
"rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR"

This is "King's Pawn Game" regardless of:
- Whose turn it is (w or b)
- Castling rights (KQkq, Kq, etc.)
- En passant square
```

### Examples

#### Example 1: Standard Opening

```
Moves: 1.e4
Position: rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1

Lookup: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"
Result: "King's Pawn Opening"
Classification: THEORY
```

#### Example 2: Deep Theory

```
Moves: 1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.O-O Be7
Position: (Ruy Lopez)

Lookup: Found in database
Result: "Ruy Lopez: Closed Variation"
Classification: THEORY
```

#### Example 3: Out of Book

```
Moves: 1.e4 e5 2.Nf3 Nc6 ... (20 moves deep)
Position: Novel position

Lookup: Not found in database
Result: None
Classification: (proceed to next check)
```

### Configuration

**Enable/Disable:**
```typescript
// Enable (default)
{ includeTheory: true }

// Disable (treat as normal moves)
{ includeTheory: false }
```

**When to Disable:**
- Analyzing games with unusual openings
- Testing theoretical novelties
- Engine training positions

### Database Maintenance

**Updating the Opening Book:**
1. Source: ECO (Encyclopedia of Chess Openings) codes
2. Format: Convert to FEN piece placement → name map
3. File: `shared/src/resources/openings.json`
4. Size: Typically 5,000-10,000 positions

**Quality Considerations:**
- Include mainline theory
- Include popular sidelines
- Avoid obscure variations (noise)
- Update periodically with modern theory

---

## CHECKMATE → BEST Classification

### Overview

**Definition:** A move that delivers checkmate is classified as BEST.

**Priority:** Third (after FORCED and THEORY)

**Rationale:** Checkmate ends the game and is always optimal.

**Note:** There is no separate "CHECKMATE" classification enum value; checkmate moves receive `Classification.BEST`.

### Algorithm

```
FUNCTION isCheckmateMove(currentNode: ExtractedCurrentNode) -> boolean:
    RETURN currentNode.board.isCheckmate()

FUNCTION classifyCheckmate(currentNode: ExtractedCurrentNode) -> Optional<Classification>:
    IF currentNode.board.isCheckmate():
        RETURN Classification.BEST
    ELSE:
        RETURN None
```

### Why BEST, Not Separate Enum?

**Design Decision:**
- Checkmate is objectively the best possible outcome
- No need for separate classification value
- Simplifies logic (fewer enum values)
- NAG annotation can still be added separately if desired

### Examples

#### Example 1: Simple Back Rank Mate

```
FEN: 6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1
```

```
  a b c d e f g h
8 . . . . . . k .
7 . . . . . p p p
6 . . . . . . . .
5 . . . . . . . .
4 . . . . . . . .
3 . . . . . . . .
2 . . . . . P P P
1 . . . . R . K .
```

**White to move:**
- Move: `Re8#` (rook to e8, checkmate)
- Black king on g8 has no escape squares (pawns on f7, g7, h7 block)
- After move: `Board.isCheckmate()` → true
- **Classification: BEST** ✅

#### Example 2: Smothered Mate

```
FEN: 6rk/6pp/7P/5N2/8/8/8/6K1 w - - 0 1
```

```
  a b c d e f g h
8 . . . . . . r k
7 . . . . . . p p
6 . . . . . . . P
5 . . . . . N . .
4 . . . . . . . .
3 . . . . . . . .
2 . . . . . . . .
1 . . . . . . K .
```

**White to move:**
- Move: `Nf7#` (knight to f7, checkmate)
- Black king on h8 is smothered by its own pieces
- Rook on g8 and pawns on g7, h7 block all escape squares
- After move: `Board.isCheckmate()` → true
- **Classification: BEST** ✅

#### Example 3: Scholar's Mate

```
FEN: r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4
```

```
  a b c d e f g h
8 r . b q k b . r
7 p p p p . Q p p
6 . . n . . n . .
5 . . . . p . . .
4 . . B . P . . .
3 . . . . . . . .
2 P P P P . P P P
1 R N B . K . N R
```

**Position after White's 4th move:**
- White just played: `Qxf7#` (queen takes pawn on f7, checkmate)
- Black king on e8 cannot capture (queen protected by bishop on c4)
- No piece can interpose or capture the queen
- **Classification: BEST** ✅ (Checkmate ends the game)

#### Example 4: Missed Mate (Not Checkmate)

```
FEN: 6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1
```

```
  a b c d e f g h
8 . . . . . . k .
7 . . . . . p p p
6 . . . . . . . .
5 . . . . . . . .
4 . . . . . . . .
3 . . . . . . . .
2 . . . . . P P P
1 . . . . R . K .
```

**White to move:**
- Best move: `Re8#` (checkmate)
- Move played: `Re7` (not checkmate, but still good)
- Evaluation: +5.00 (winning but not mate)
- After move: `Board.isCheckmate()` → false
- **Classification:** EXCELLENT or OKAY (proceed to point loss calculation)
- **Note:** Missed the mate! Not classified as BEST.

### Distinguishing From Other BEST Moves

While checkmate moves get `Classification.BEST`, they can be distinguished:

**Method 1: Check board state**
```typescript
if (classification === Classification.BEST && board.isCheckmate()) {
  // This is a checkmate move
}
```

**Method 2: Check evaluation**
```typescript
if (classification === Classification.BEST && evaluation.type === "mate" && evaluation.value === 0) {
  // Mate delivered
}
```

### Interaction with CRITICAL/BRILLIANT

**Question:** Can a checkmate be CRITICAL or BRILLIANT?

**Answer:** No.

**Reason:**
- CRITICAL/BRILLIANT checks only run on non-checkmate BEST moves
- Checkmate short-circuits the classification (returns early)
- This is intentional: checkmate doesn't need further refinement

### Edge Cases

**Stalemate:**
```
Position: Stalemate delivered
Board.isCheckmate() → false
Board.isStalemate() → true

Classification: (Not BEST, proceed to point loss)
Note: Stalemate typically classified as BLUNDER/MISTAKE
       depending on who stalemated whom
```

**Check vs. Checkmate:**
```
Check only: Board.isCheck() → true, Board.isCheckmate() → false
→ Not classified as BEST (unless top engine move)

Checkmate: Board.isCheck() → true, Board.isCheckmate() → true
→ Classified as BEST
```

---

## Summary Table

| Classification | Priority | Condition | Skips Further Checks? |
|---------------|----------|-----------|----------------------|
| FORCED | 1st | Only 1 legal move | Yes |
| THEORY | 2nd | In opening book | Yes |
| BEST (Mate) | 3rd | Delivers checkmate | Yes |

**All three classifications short-circuit the decision flow.**

Once any of these conditions is met, the move is classified immediately without evaluating point loss or checking for CRITICAL/BRILLIANT.

---

## Next Steps

- **[Point Loss Classification](./04-point-loss-classification.md)** - The core evaluation system for most moves
- **[Advanced Classifications](./05-advanced-classifications.md)** - CRITICAL and BRILLIANT refinements

---

[← Back to Index](./README.md) | [← Previous: Classification Overview](./02-classification-overview.md) | [Next: Point Loss Classification →](./04-point-loss-classification.md)

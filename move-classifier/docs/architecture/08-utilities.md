# Supporting Utilities

> Low-level utility functions and helpers

[← Back to Index](./README.md)

## Board Manipulation

### FEN Parsing

```
parseFen(fen: string) -> FenComponents
```

Splits FEN into components: pieces, turn, castling, en passant, clocks.

### Set Turn

```
setFenTurn(fen: string, color: PieceColor) -> string
```

Modifies FEN to change whose turn it is (for defender analysis).

### Board Operations

```
copyBoard(board: ChessBoard) -> ChessBoard
putPiece(board, piece, square) -> boolean
removePiece(board, square) -> Piece | null
```

---

## Move Parsing

### SAN Parsing

```
parseSanMove(san: string) -> MoveInfo
```

Extracts: piece type, capture, check, checkmate, promotion.

### UCI Parsing

```
parseUciMove(uci: string) -> { from, to, promotion }
```

Converts UCI notation to structured format.

### Move Conversion

```
toRawMove(move: Move) -> RawMove
```

Simplifies move to lightweight format.

---

## Node Extraction

### Extract Previous Node

```
extractPreviousStateTreeNode(node: StateTreeNode) -> ExtractedPreviousNode
```

Extracts data needed from position **before** move:
- Top move
- Second-best move
- Evaluations
- Board state

### Extract Current Node

```
extractCurrentStateTreeNode(node: StateTreeNode) -> ExtractedCurrentNode
```

Extracts data from position **after** move:
- Played move
- Evaluation
- Board state
- Checkmate status

---

## Subjective Evaluation

```
getSubjectiveEvaluation(evaluation: Evaluation, playerColor: PieceColor) -> Evaluation
```

Adjusts White-perspective evaluation to player's perspective:
```
subjective = evaluation × (playerColor == WHITE ? +1 : -1)
```

---

## Implementation Reference

**Files:**
- `shared/src/lib/utils/chess.ts`
- `shared/src/lib/reporter/utils/extractNode.ts`
- `shared/src/lib/reporter/utils/opening.ts`

---

[← Back to Index](./README.md) | [Next: Data Structures →](./09-data-structures.md)

# Data Structures

> Type definitions and interfaces

[← Back to Index](./README.md)

## Core Types

### Classification

```typescript
enum Classification {
  BRILLIANT = "brilliant",
  CRITICAL = "critical",
  BEST = "best",
  EXCELLENT = "excellent",
  OKAY = "okay",
  INACCURACY = "inaccuracy",
  MISTAKE = "mistake",
  BLUNDER = "blunder",
  THEORY = "theory",
  FORCED = "forced",
  RISKY = "risky"
}
```

### Evaluation

```typescript
interface Evaluation {
  type: "centipawn" | "mate";
  value: number;  // Centipawns or moves to mate
}
```

### Move

```typescript
interface Move {
  san: string;           // "Nf3", "e4"
  uci: string;           // "g1f3", "e2e4"
  from: Square;          // "g1"
  to: Square;            // "f3"
  piece: PieceType;      // "n"
  color: PieceColor;     // "white"
  captured?: PieceType;  // "p"
  promotion?: PieceType; // "q"
  flags: string;         // "n", "c", "k", etc.
}
```

### EngineLine

```typescript
interface EngineLine {
  evaluation: Evaluation;
  source: EngineVersion;
  depth: number;
  index: number;  // 1 = best, 2 = second-best
  moves: Move[];  // Principal variation
}
```

---

## Game State

### StateTreeNode

```typescript
interface StateTreeNode {
  id: string;
  parent?: StateTreeNode;
  children: StateTreeNode[];
  mainline: boolean;
  state: BoardState;
}
```

### BoardState

```typescript
interface BoardState {
  fen: string;
  move?: Move;
  engineLines: EngineLine[];
  classification?: Classification;
  accuracy?: number;
  opening?: string;
  moveColour?: PieceColor;
}
```

---

## Extracted Nodes

### ExtractedPreviousNode

```typescript
interface ExtractedPreviousNode {
  board: ChessBoard;
  state: BoardState;
  topLine: EngineLine;
  topMove: Move;
  evaluation: Evaluation;
  subjectiveEvaluation: Evaluation;
  secondTopLine?: EngineLine;
  secondTopMove?: Move;
  secondSubjectiveEval?: Evaluation;
  playedMove?: Move;
}
```

### ExtractedCurrentNode

```typescript
interface ExtractedCurrentNode {
  board: ChessBoard;
  state: BoardState;
  topLine: EngineLine;
  topMove?: Move;
  evaluation: Evaluation;
  subjectiveEvaluation: Evaluation;
  secondTopLine?: EngineLine;
  secondTopMove?: Move;
  secondSubjectiveEval?: Evaluation;
  playedMove: Move;  // Required
}
```

---

## Supporting Types

### BoardPiece

```typescript
interface BoardPiece {
  type: PieceType;    // "n", "b", "r", etc.
  color: PieceColor;  // "white" | "black"
  square: Square;     // "e4"
}
```

### Square

```typescript
type Square = "a1" | "a2" | ... | "h8";  // 64 total
```

### PieceType

```typescript
type PieceType = "p" | "n" | "b" | "r" | "q" | "k";
```

### PieceColor

```typescript
enum PieceColor {
  WHITE = "white",
  BLACK = "black"
}
```

---

## Implementation Reference

**File:** `shared/src/types/` (various files)

See full type definitions in the codebase.

---

[← Back to Index](./README.md) | [Next: Constants & Configuration →](./10-constants-config.md)

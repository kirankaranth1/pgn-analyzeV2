# Core Concepts

> Fundamental concepts and terminology used throughout the classification system

[← Back to Index](./README.md)

## Table of Contents

1. [Chess Notation Systems](#chess-notation-systems)
2. [Engine Evaluations](#engine-evaluations)
3. [Expected Points and Win Probability](#expected-points-and-win-probability)
4. [State Tree and Game Representation](#state-tree-and-game-representation)
5. [Node Extraction](#node-extraction)

---

## Chess Notation Systems

### FEN (Forsyth-Edwards Notation)

**Purpose:** Complete position representation

**Format:** `<pieces> <turn> <castling> <enpassant> <halfmove> <fullmove>`

**Example:**
```
rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1
```

**Components:**
1. **Piece Placement:** `rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR`
   - Rank 8 → Rank 1 (top to bottom)
   - Lowercase = black pieces, Uppercase = white pieces
   - Numbers = empty squares
   - `/` separates ranks

2. **Active Color:** `b` (black to move) or `w` (white to move)

3. **Castling Rights:** `KQkq`
   - `K` = White kingside, `Q` = White queenside
   - `k` = Black kingside, `q` = Black queenside
   - `-` = no castling available

4. **En Passant:** `e3` (target square) or `-` (not available)

5. **Halfmove Clock:** `0` (fifty-move rule counter)

6. **Fullmove Number:** `1` (increments after Black's move)

### SAN (Standard Algebraic Notation)

**Purpose:** Human-readable move notation

**Format:** `<piece><from><capture><to><promotion><check>`

**Examples:**
```
e4          Pawn to e4
Nf3         Knight to f3
Bxc5        Bishop captures on c5
O-O         Kingside castling
O-O-O       Queenside castling
e8=Q+       Pawn promotes to Queen with check
Nbd7        Knight from b-file to d7 (disambiguation)
R1a3        Rook from rank 1 to a3 (disambiguation)
```

**Suffixes:**
- `+` = Check
- `#` = Checkmate
- `!` = Good move
- `!!` = Brilliant move
- `?` = Mistake
- `??` = Blunder
- `!?` = Interesting move
- `?!` = Questionable move

### UCI (Universal Chess Interface) Notation

**Purpose:** Engine-friendly move notation

**Format:** `<from><to><promotion>`

**Examples:**
```
e2e4        e2 to e4
g1f3        g1 to f3
e7e8q       e7 to e8, promote to queen
e1g1        Kingside castling (king moves)
e1c1        Queenside castling
```

**Lichess Variation:**
Lichess uses king-to-rook notation for castling:
```
e1h1  →  e1g1   (White kingside)
e1a1  →  e1c1   (White queenside)
e8h8  →  e8g8   (Black kingside)
e8a8  →  e8c8   (Black queenside)
```

---

## Engine Evaluations

### Evaluation Types

The system uses two types of evaluations:

#### 1. Centipawn Evaluation

**Format:** `{ type: "centipawn", value: number }`

**Interpretation:**
- Measured in 1/100th of a pawn
- Positive = advantage for White
- Negative = advantage for Black

**Examples:**
```
{ type: "centipawn", value: 0 }     Equal position
{ type: "centipawn", value: 100 }   White ahead by 1 pawn
{ type: "centipawn", value: -250 }  Black ahead by 2.5 pawns
{ type: "centipawn", value: 450 }   White ahead by ~rook (4.5 pawns)
```

**Typical Ranges:**
- `-50 to +50` - Roughly equal
- `±100 to ±200` - Slight advantage
- `±200 to ±500` - Clear advantage
- `±500 to ±1000` - Winning position
- `±1000+` - Completely winning

#### 2. Mate Evaluation

**Format:** `{ type: "mate", value: number }`

**Interpretation:**
- Value = number of moves until mate
- Positive = White mates Black
- Negative = Black mates White
- Zero = mate delivered (game over)

**Examples:**
```
{ type: "mate", value: 3 }    White mates in 3 moves
{ type: "mate", value: -5 }   Black mates in 5 moves
{ type: "mate", value: 0 }    Checkmate (game ended)
{ type: "mate", value: 1 }    Mate in 1 (forced mate next move)
```

### Engine Lines (Multi-PV)

**Purpose:** Engine provides multiple "best" move sequences

**Structure:**
```typescript
{
  evaluation: Evaluation,    // Position evaluation
  source: EngineVersion,     // Which engine produced this
  depth: number,             // Search depth in plies
  index: number,             // Line ranking (1, 2, 3, ...)
  moves: Move[]              // Principal variation
}
```

**Example:**
```json
[
  {
    "evaluation": { "type": "centipawn", "value": 45 },
    "source": "stockfish-17",
    "depth": 20,
    "index": 1,
    "moves": [
      { "san": "Nf3" },
      { "san": "d5" },
      { "san": "d4" }
    ]
  },
  {
    "evaluation": { "type": "centipawn", "value": 38 },
    "source": "stockfish-17",
    "depth": 20,
    "index": 2,
    "moves": [
      { "san": "d4" },
      { "san": "Nf6" },
      { "san": "c4" }
    ]
  }
]
```

**Usage:**
- `index: 1` = Best move (top engine line)
- `index: 2` = Second-best move (used for CRITICAL classification)
- Higher index = progressively weaker alternatives

---

## Expected Points and Win Probability

### Concept

**Expected Points** converts engine evaluations into a 0-1 probability representing the expected game outcome:
- `0.0` = Certain loss
- `0.5` = Equal position (draw expected)
- `1.0` = Certain win

### Calculation Formula

#### For Centipawn Evaluations

```
Expected Points = 1 / (1 + e^(-0.0035 × evaluation))
```

**Sigmoid Function Properties:**
- Smooth S-curve from 0 to 1
- Centered at 0 (equal position)
- Gradient calibrated to chess outcomes

**Examples:**
| Evaluation | Expected Points | Interpretation |
|-----------|----------------|----------------|
| 0 cp      | 0.500          | Equal (50% win) |
| +100 cp   | 0.587          | ~59% win chance |
| +200 cp   | 0.668          | ~67% win chance |
| +300 cp   | 0.737          | ~74% win chance |
| +500 cp   | 0.845          | ~85% win chance |
| +800 cp   | 0.933          | ~93% win chance |
| -200 cp   | 0.332          | ~33% win chance |

#### For Mate Evaluations

```
Expected Points = {
  1.0   if mate value > 0 (winning mate)
  0.0   if mate value < 0 (losing mate)
  white_win_value  if mate value == 0 (mate delivered)
}
```

**Rationale:** Forced mate = guaranteed outcome, binary probability.

### Perspective Adjustment

Evaluations are **always from White's perspective**. To get the perspective of the moving player:

```
Subjective Evaluation = evaluation × (player == WHITE ? +1 : -1)
```

**Example:**
- Evaluation: `+200` (White ahead)
- White's perspective: `+200` (good)
- Black's perspective: `-200` (bad)

### Point Loss

**Definition:** Decrease in expected points caused by playing a move.

**Formula:**
```
Point Loss = max(0, EP(before, opponent) - EP(after, player))
```

**Example:**
```
Before move: +150 cp → EP = 0.605 (White's perspective after Black moves)
After move:  +80 cp  → EP = 0.569 (Black's perspective after Black moves)

Point Loss = 0.605 - 0.569 = 0.036 (3.6% win probability lost)
```

**Classification:**
- `0.036` → EXCELLENT (< 4.5% loss)

---

## State Tree and Game Representation

### State Tree Node

**Purpose:** Represents a single position in the game tree, including variations.

**Structure:**
```typescript
{
  id: string,                  // Unique identifier
  parent?: StateTreeNode,      // Previous position
  children: StateTreeNode[],   // Next positions (variations)
  mainline: boolean,           // Part of main game line?
  state: BoardState            // Position data
}
```

**Tree Structure:**
```
Root (starting position)
  │
  ├─ 1.e4 (mainline)
  │   │
  │   ├─ 1...e5 (mainline)
  │   │   │
  │   │   ├─ 2.Nf3 (mainline)
  │   │   └─ 2.Bc4 (variation)
  │   │
  │   └─ 1...c5 (variation, Sicilian)
  │
  └─ 1.d4 (variation)
```

### Board State

**Purpose:** Complete data for a single position.

**Structure:**
```typescript
{
  fen: string,                      // Position
  move?: Move,                      // Move that created this position
  engineLines: EngineLine[],        // Engine analysis
  classification?: Classification,  // Move quality
  accuracy?: number,                // Move accuracy (0-100)
  opening?: string,                 // Opening name
  moveColour?: PieceColor          // Who played the move
}
```

### Game Analysis

**Purpose:** Complete analysis result for a game.

**Structure:**
```typescript
{
  estimatedRatings: {
    white: number,    // Estimated Elo
    black: number
  },
  stateTree: StateTreeNode  // Root of game tree
}
```

---

## Node Extraction

### Purpose

The classification system operates on **extracted nodes** - simplified data structures that contain only the information needed for classification, extracted from the full state tree.

### Extracted Node Types

#### ExtractedPreviousNode

**Represents:** Position **before** the move was played.

**Contains:**
```typescript
{
  board: ChessBoard,                  // Board state
  state: BoardState,                  // State data
  topLine: EngineLine,                // Best engine line
  topMove: Move,                      // Best move from this position
  evaluation: Evaluation,             // Top line evaluation
  subjectiveEvaluation: Evaluation,   // Adjusted to player perspective
  secondTopLine?: EngineLine,         // Second-best line
  secondTopMove?: Move,               // Second-best move
  secondSubjectiveEval?: Evaluation,  // Second line subjective
  playedMove?: Move                   // Move that was actually played
}
```

**Usage:** Compare played move against best move.

#### ExtractedCurrentNode

**Represents:** Position **after** the move was played.

**Contains:**
```typescript
{
  board: ChessBoard,                  // Board state after move
  state: BoardState,                  // State data
  topLine: EngineLine,                // Best continuation
  topMove?: Move,                     // Best move from here
  evaluation: Evaluation,             // Position evaluation
  subjectiveEvaluation: Evaluation,   // Player's perspective (required)
  secondTopLine?: EngineLine,         // Second-best continuation
  secondTopMove?: Move,               // Second-best move
  secondSubjectiveEval?: Evaluation,  // Second line subjective
  playedMove: Move                    // Move that was played (required)
}
```

**Usage:** Evaluate position after move, check for checkmate, etc.

### Extraction Process

```
StateTreeNode
    ↓
Extract Previous (parent node)
    ↓
Extract Current (current node)
    ↓
Classify(previous, current) → Classification
```

**Key Operations:**
1. Get top engine line from `engineLines` array
2. Parse first move from top line as `topMove`
3. Get second-best line (index 2) if available
4. Calculate subjective evaluations
5. Create simplified node structures

---

## Next Steps

Now that you understand the core concepts, explore the classification system:

- **[Classification Overview](./02-classification-overview.md)** - How classifications are determined
- **[Basic Classifications](./03-basic-classifications.md)** - Simple classification rules
- **[Point Loss Classification](./04-point-loss-classification.md)** - The core evaluation system

---

[← Back to Index](./README.md) | [← Previous: Preprocessing Pipeline](./00-preprocessing-pipeline.md) | [Next: Classification Overview →](./02-classification-overview.md)


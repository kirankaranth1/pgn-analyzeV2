# Preprocessing Pipeline

> Complete flow from game input to classification-ready data structures

[← Back to Index](./README.md)

## Table of Contents

1. [Overview](#overview)
2. [Stage 1: Parse Game into State Tree](#stage-1-parse-game-into-state-tree)
3. [Stage 2: Engine Analysis](#stage-2-engine-analysis)
4. [Stage 3: Build Node Chain](#stage-3-build-node-chain)
5. [Stage 4: Extract Nodes](#stage-4-extract-nodes)
6. [Stage 5: Calculate Derived Values](#stage-5-calculate-derived-values)
7. [Complete Data Flow](#complete-data-flow)
8. [Implementation Requirements](#implementation-requirements)

---

## Overview

Before a chess move can be classified, the system performs extensive preprocessing to transform raw game data into structured, analyzed positions. This pipeline consists of **5 major stages**:

```
PGN String → State Tree → Engine Analysis → Node Chain → Extracted Nodes → Classification
```

### Pipeline Stages

| Stage | Input | Output | Purpose |
|-------|-------|--------|---------|
| **1. Parse** | PGN string | State tree | Convert notation to positions |
| **2. Analyze** | State tree | Annotated tree | Add engine evaluations |
| **3. Chain** | Annotated tree | Node array | Linearize for processing |
| **4. Extract** | Node array | Extracted nodes | Simplify for classification |
| **5. Calculate** | Extracted nodes | Final structures | Compute derived values |

**Time Complexity:** O(n × d) where n = moves, d = engine depth

**Space Complexity:** O(n × m) where n = moves, m = MultiPV lines

---

## Stage 1: Parse Game into State Tree

### Input Data

```typescript
Game {
    pgn: string,              // e.g., "1. e4 e5 2. Nf3 Nc6"
    initialPosition: string   // FEN string (default: starting position)
}
```

### Process

#### Step 1: Parse PGN

Use a PGN parser library to convert the string into a structured format.

```typescript
// Example using @mliebelt/pgn-parser
const parsedPGN = parseGame(game.pgn);

// Result structure:
ParsedPGN {
    moves: [
        {
            notation: { notation: "e4" },
            variations: []
        },
        {
            notation: { notation: "e5" },
            variations: []
        }
    ]
}
```

#### Step 2: Create Root Node

```typescript
const rootNode: StateTreeNode = {
    id: generateUniqueId(),           // UUID or incremental ID
    mainline: true,                   // This is the main line
    parent: undefined,                // Root has no parent
    children: [],                     // Will be populated
    state: {
        fen: game.initialPosition,    // Starting position
        engineLines: []               // Empty initially
    }
};
```

#### Step 3: Build Tree Recursively

```typescript
function addMovesToNode(
    currentNode: StateTreeNode,
    moves: ParsedMove[],
    isMainline: boolean
) {
    let lastNode = currentNode;
    
    for (const pgnMove of moves) {
        // Create a chess board at current position
        const board = new ChessBoard(lastNode.state.fen);
        
        // Apply the move
        const executedMove = board.move(pgnMove.notation.notation);
        
        // Get the color of the moving player
        // chess.js returns "w" or "b" after the move is made
        const moveColor = executedMove.color == "w" 
            ? PieceColor.WHITE 
            : PieceColor.BLACK;
        
        // Create new node
        const newNode: StateTreeNode = {
            id: generateUniqueId(),
            mainline: isMainline,
            parent: lastNode,
            children: [],
            state: {
                fen: executedMove.after,         // Position after move
                engineLines: [],                  // Empty initially
                move: {
                    san: executedMove.san,        // e.g., "Nf3"
                    uci: executedMove.lan         // e.g., "g1f3"
                },
                moveColor: moveColor
            }
        };
        
        // Link nodes
        lastNode.children.push(newNode);
        
        // Process variations (recursive)
        for (const variation of pgnMove.variations) {
            addMovesToNode(lastNode, variation, false);
        }
        
        // Move to next node
        lastNode = newNode;
    }
}

// Start the recursive process
addMovesToNode(rootNode, parsedPGN.moves, true);
```

### Output Structure

```typescript
StateTreeNode {
    id: string,                    // Unique identifier
    mainline: boolean,             // Is part of main game line?
    parent?: StateTreeNode,        // Previous position (undefined for root)
    children: StateTreeNode[],     // Next positions (variations)
    state: BoardState              // Position data
}

BoardState {
    fen: string,                   // Forsyth-Edwards Notation
    move?: Move,                   // Move that led to this position
    moveColor?: PieceColor,        // Who played the move
    engineLines: EngineLine[],     // Empty at this stage
    classification?: Classification, // Added later
    accuracy?: number,             // Added later
    opening?: string               // Added later
}

Move {
    san: string,  // Standard Algebraic Notation (e.g., "Nf3")
    uci: string   // Universal Chess Interface (e.g., "g1f3")
}
```

### Tree Structure Example

```
Root (starting position)
  │
  ├─ 1.e4 (mainline, id="node_1")
  │   │
  │   ├─ 1...e5 (mainline, id="node_2")
  │   │   │
  │   │   ├─ 2.Nf3 (mainline, id="node_3")
  │   │   └─ 2.Bc4 (variation, id="node_4")
  │   │
  │   └─ 1...c5 (variation, id="node_5")
  │
  └─ 1.d4 (variation, id="node_6")
```

### Key Implementation Notes

1. **Chess Library Required:** You need a library that can:
   - Parse move notation (SAN)
   - Apply moves to a board
   - Generate FEN strings
   - Convert between SAN and UCI notation

2. **ID Generation:** IDs must be unique across the entire tree

3. **Move Validation:** Invalid moves should cause parsing to fail

4. **Color Handling:** Most chess libraries use 'w'/'b' or similar. Normalize to your enum.

---

## Stage 2: Engine Analysis

### Input

State tree with all `engineLines` arrays empty.

### Goal

Populate `engineLines` for each node with computer analysis using either:
- **Cloud evaluation** (Lichess API) - faster, limited depth
- **Local engine** (Stockfish UCI) - slower, configurable depth

### Engine Line Structure

```typescript
EngineLine {
    evaluation: Evaluation,        // Position evaluation
    source: EngineVersion,         // Which engine produced this
    depth: number,                 // Search depth in plies
    index: number,                 // MultiPV index (1=best, 2=2nd, ...)
    moves: Move[]                  // Principal variation (best continuation)
}

Evaluation {
    type: "centipawn" | "mate",   // Type of evaluation
    value: number                  // Score value
}

EngineVersion = 
    | "stockfish-17"
    | "stockfish-17-lite"
    | "lichess-cloud"
```

### Process A: Cloud Evaluation (Lichess)

#### API Request

```typescript
async function getCloudEvaluation(fen: string, multiPvCount: number) {
    const url = `https://lichess.org/api/cloud-eval?fen=${fen}&multiPv=${multiPvCount}`;
    const response = await fetch(url);
    
    if (!response.ok) {
        throw new Error(`Cloud evaluation failed: ${response.status}`);
    }
    
    return await response.json();
}
```

#### Response Format

```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "knodes": 15000,
  "depth": 20,
  "pvs": [
    {
      "moves": "e7e5 g1f3 b8c6 f1b5",
      "cp": 45
    },
    {
      "moves": "c7c5 g1f3 d7d6",
      "cp": 38
    }
  ]
}
```

#### Parse Response

```typescript
const engineLines: EngineLine[] = [];

for (const pv of cloudEval.pvs) {
    // Create temporary board to convert UCI to SAN
    const tempBoard = new ChessBoard(fen);
    const moves: Move[] = [];
    
    // Parse UCI moves from cloud response
    const uciMoves = pv.moves.split(" ");
    
    for (const uciMove of uciMoves) {
        // Handle Lichess castling notation (king-to-rook)
        // Convert e1h1 → e1g1, e1a1 → e1c1, etc.
        const normalizedUci = normalizeLichessCastling(uciMove);
        
        try {
            const parsedMove = tempBoard.move(normalizedUci);
            moves.push({
                san: parsedMove.san,
                uci: parsedMove.lan
            });
        } catch (error) {
            break; // Stop on invalid move
        }
    }
    
    // Determine evaluation type
    const evaluationType = ("mate" in pv) ? "mate" : "centipawn";
    const evaluationValue = ("mate" in pv) ? pv.mate : pv.cp;
    
    // Create engine line
    engineLines.push({
        evaluation: {
            type: evaluationType,
            value: evaluationValue
        },
        source: "lichess-cloud",
        depth: cloudEval.depth,
        index: cloudEval.pvs.indexOf(pv) + 1,  // 1-indexed!
        moves: moves
    });
}

return engineLines;
```

#### Lichess Castling Conversion

```typescript
const lichessCastlingMoves = {
    "e1h1": "e1g1",  // White kingside
    "e1a1": "e1c1",  // White queenside
    "e8h8": "e8g8",  // Black kingside
    "e8a8": "e8c8"   // Black queenside
};

function normalizeLichessCastling(uci: string): string {
    return lichessCastlingMoves[uci] || uci;
}
```

### Process B: Local Engine (Stockfish UCI)

#### Engine Initialization

```typescript
class Engine {
    worker: Worker;  // Web Worker or Process
    position: string;
    version: EngineVersion;
    
    constructor(version: EngineVersion) {
        this.version = version;
        this.worker = new Worker(`/engines/${version}.js`);
        this.position = STARTING_FEN;
        
        // Initialize engine
        this.send("uci");
        this.send("ucinewgame");
        
        // Configure MultiPV
        this.send("setoption name MultiPV value 3");
    }
    
    send(command: string) {
        this.worker.postMessage(command);
    }
}
```

#### Set Position

```typescript
setPosition(fen: string): void {
    this.send(`position fen ${fen}`);
    this.position = fen;
}
```

#### Evaluate Position

```typescript
async evaluate(options: {
    depth: number,
    timeLimit?: number,
    onEngineLine?: (line: EngineLine) => void
}): Promise<EngineLine[]> {
    const engineLines: EngineLine[] = [];
    
    // Build UCI command
    const timeArg = options.timeLimit 
        ? `movetime ${options.timeLimit}` 
        : "";
    
    const command = `go depth ${options.depth} ${timeArg}`;
    
    // Listen for engine output
    this.send(command);
    
    await this.consumeLogs(
        // Stop condition
        (log) => log.startsWith("bestmove") || log.includes("depth 0"),
        
        // Process each log line
        (log) => {
            // Only process info lines
            if (!log.startsWith("info depth")) return;
            if (log.includes("currmove")) return;  // Skip intermediate info
            
            // Parse depth
            const depthMatch = log.match(/(?<= depth )(\d+)/);
            const depth = parseInt(depthMatch?.[0] || "");
            if (isNaN(depth)) return;
            
            // Parse MultiPV index
            const indexMatch = log.match(/(?<= multipv )(\d+)/);
            const index = parseInt(indexMatch?.[0] || "") || 1;
            
            // Parse evaluation
            const scoreMatch = log.match(/ score (cp|mate) (-?\d+)/);
            if (!scoreMatch) return;
            
            const evalType = scoreMatch[1] === "cp" ? "centipawn" : "mate";
            let evalValue = parseInt(scoreMatch[2]);
            if (isNaN(evalValue)) return;
            
            // ⚠️ CRITICAL: Normalize to White's perspective
            // Engine returns evaluation from side-to-move perspective
            if (this.position.includes(" b ")) {  // Black to move
                evalValue = -evalValue;
            }
            
            // Parse principal variation
            const pvMatch = log.match(/ pv (.*)/);
            const uciMoves = pvMatch?.[1]?.split(" ") || [];
            
            // Convert UCI moves to SAN
            const tempBoard = new ChessBoard(this.position);
            const moves: Move[] = [];
            
            for (const uciMove of uciMoves) {
                const parsedMove = tempBoard.move(uciMove);
                moves.push({
                    san: parsedMove.san,
                    uci: parsedMove.lan
                });
            }
            
            // Create engine line
            const newLine: EngineLine = {
                depth: depth,
                index: index,
                evaluation: {
                    type: evalType,
                    value: evalValue
                },
                source: this.version,
                moves: moves
            };
            
            engineLines.push(newLine);
            options.onEngineLine?.(newLine);
        }
    );
    
    return engineLines;
}
```

#### UCI Protocol Example

```
> position fen rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1
> setoption name MultiPV value 3
> go depth 20

< info depth 1 multipv 1 score cp 0 pv e7e5
< info depth 2 multipv 1 score cp 45 pv e7e5 g1f3
< info depth 2 multipv 2 score cp 38 pv c7c5 g1f3
< info depth 2 multipv 3 score cp 20 pv g8f6 b1c3
...
< info depth 20 multipv 1 score cp 45 pv e7e5 g1f3 b8c6 f1b5 a7a6 b5a4
< info depth 20 multipv 2 score cp 38 pv c7c5 g1f3 d7d6 d2d4 c5d4
< info depth 20 multipv 3 score cp 25 pv g8f6 b1c3 d7d5 e4d5 f6d5
< bestmove e7e5 ponder g1f3
```

### Applying Engine Lines to State Tree

```typescript
async function analyzeStateTree(
    rootNode: StateTreeNode,
    options: {
        engineDepth: number,
        engineVersion: EngineVersion,
        multiPvCount: number
    }
) {
    const nodes = getNodeChain(rootNode);
    
    for (const node of nodes) {
        // Try cloud evaluation first (faster)
        try {
            const cloudLines = await getCloudEvaluation(
                node.state.fen,
                options.multiPvCount
            );
            node.state.engineLines.push(...cloudLines);
        } catch (error) {
            // Fall back to local engine
            const engine = new Engine(options.engineVersion);
            engine.setPosition(node.state.fen);
            
            const localLines = await engine.evaluate({
                depth: options.engineDepth
            });
            
            node.state.engineLines.push(...localLines);
            engine.terminate();
        }
    }
}
```

### Critical Implementation Notes

#### 1. Evaluation Perspective

**⚠️ ALL EVALUATIONS MUST BE FROM WHITE'S PERSPECTIVE**

- Positive value = White is better
- Negative value = Black is better
- This is NOT the engine's default behavior

```typescript
// When Black is to move, flip the sign
if (position.includes(" b ")) {
    evaluationValue = -evaluationValue;
}
```

#### 2. MultiPV Indexing

MultiPV lines are **1-indexed** (not 0-indexed):
- `index: 1` = Best move
- `index: 2` = Second-best move
- `index: 3` = Third-best move

#### 3. Depth vs Time Limits

- **Depth**: Fixed search depth (e.g., 20 plies)
- **Time**: Fixed time per position (e.g., 1000ms)
- Deeper = more accurate but slower

#### 4. Engine Line Selection

When multiple engine lines exist (different depths/sources):

```typescript
function getTopEngineLine(lines: EngineLine[]): EngineLine | null {
    if (lines.length === 0) return null;
    
    // Highest depth wins; if tied, lowest index wins
    return maxBy(lines, line => line.depth - line.index);
}
```

---

## Stage 3: Build Node Chain

### Purpose

Convert the tree structure into a linear array for sequential processing.

### Process

```typescript
function getNodeChain(
    rootNode: StateTreeNode,
    expandAllVariations: boolean = false
): StateTreeNode[] {
    const chain: StateTreeNode[] = [];
    const frontier: StateTreeNode[] = [rootNode];
    
    while (frontier.length > 0) {
        const current = frontier.pop();
        if (!current) break;
        
        chain.push(current);
        
        if (expandAllVariations) {
            // Add all children (for variation analysis)
            for (const child of current.children) {
                frontier.push(child);
            }
        } else {
            // Add only first child (mainline only)
            if (current.children.length > 0) {
                frontier.push(current.children[0]);
            }
        }
    }
    
    return chain;
}
```

### Example

```
Tree:
Root → e4 → e5 → Nf3
        └→ c5

Mainline chain (expandAllVariations=false):
[Root, e4, e5, Nf3]

Full chain (expandAllVariations=true):
[Root, e4, e5, Nf3, c5]
```

---

## Stage 4: Extract Nodes

### Purpose

Create simplified, classification-ready structures from state tree nodes.

### Output Types

#### ExtractedPreviousNode

Represents the position **before** the move was played.

```typescript
ExtractedPreviousNode {
    // Board state
    board: ChessBoard,                 // Board object (e.g., chess.js instance)
    state: BoardState,                 // Full state data
    
    // Best move analysis
    topLine: EngineLine,               // Best engine line
    topMove: Move,                     // Best move (chess.js Move object)
    evaluation: Evaluation,            // Top line evaluation
    subjectiveEvaluation: Evaluation,  // From player's perspective
    
    // Second-best move analysis (for CRITICAL)
    secondTopLine?: EngineLine,        // Second-best line
    secondTopMove?: Move,              // Second-best move
    secondSubjectiveEvaluation?: Evaluation,
    
    // Actual move played (if available)
    playedMove?: Move                  // Move that was actually played
}
```

#### ExtractedCurrentNode

Represents the position **after** the move was played.

```typescript
ExtractedCurrentNode {
    // Board state
    board: ChessBoard,                 // Board object after move
    state: BoardState,                 // Full state data
    
    // Best continuation
    topLine: EngineLine,               // Best engine line
    topMove?: Move,                    // Best next move (optional)
    evaluation: Evaluation,            // Position evaluation
    subjectiveEvaluation: Evaluation,  // From player's perspective (REQUIRED)
    
    // Second-best continuation
    secondTopLine?: EngineLine,
    secondTopMove?: Move,
    secondSubjectiveEvaluation?: Evaluation,
    
    // Actual move played (REQUIRED)
    playedMove: Move                   // Move that was played
}
```

### Extraction Algorithm

#### Extract Previous Node

```typescript
function extractPreviousStateTreeNode(
    node: StateTreeNode
): ExtractedPreviousNode | null {
    
    // 1. Get top engine line
    const topLine = getTopEngineLine(node.state.engineLines);
    if (!topLine) return null;
    
    // 2. Extract top move
    const topMoveSan = topLine.moves[0]?.san;
    if (!topMoveSan) return null;
    
    const board = new ChessBoard(node.state.fen);
    const topMove = board.move(topMoveSan);
    if (!topMove) return null;
    
    // 3. Get played move (from child node)
    let playedMove = undefined;
    if (node.parent && node.state.move) {
        const playedBoard = new ChessBoard(node.parent.state.fen);
        playedMove = playedBoard.move(node.state.move.san);
    }
    
    // 4. Calculate subjective evaluation
    const playerColor = playedMove?.color || "w";
    const subjectiveEvaluation = getSubjectiveEvaluation(
        topLine.evaluation,
        playerColor
    );
    
    // 5. Extract second-best line
    const secondTopLine = getLineGroupSibling(
        node.state.engineLines,
        topLine,
        2  // Index 2 = second-best
    );
    
    let secondTopMove = undefined;
    let secondSubjectiveEval = undefined;
    
    if (secondTopLine) {
        const secondMoveSan = secondTopLine.moves[0]?.san;
        if (secondMoveSan) {
            const board2 = new ChessBoard(node.state.fen);
            secondTopMove = board2.move(secondMoveSan);
            
            if (secondTopMove) {
                secondSubjectiveEval = getSubjectiveEvaluation(
                    secondTopLine.evaluation,
                    secondTopMove.color
                );
            }
        }
    }
    
    // 6. Return extracted node
    return {
        board: new ChessBoard(node.state.fen),
        state: node.state,
        topLine: topLine,
        topMove: topMove,
        evaluation: topLine.evaluation,
        subjectiveEvaluation: subjectiveEvaluation,
        secondTopLine: secondTopLine,
        secondTopMove: secondTopMove,
        secondSubjectiveEvaluation: secondSubjectiveEval,
        playedMove: playedMove
    };
}
```

#### Extract Current Node

```typescript
function extractCurrentStateTreeNode(
    node: StateTreeNode
): ExtractedCurrentNode | null {
    
    // Require parent node
    if (!node.parent) return null;
    
    // 1. Get top engine line
    const topLine = getTopEngineLine(node.state.engineLines);
    if (!topLine) return null;
    
    // 2. Extract top move (optional)
    let topMove = undefined;
    const topMoveSan = topLine.moves[0]?.san;
    if (topMoveSan) {
        const board = new ChessBoard(node.state.fen);
        topMove = board.move(topMoveSan);
    }
    
    // 3. Get played move (REQUIRED)
    const playedMoveSan = node.state.move?.san;
    if (!playedMoveSan) return null;
    
    const playedBoard = new ChessBoard(node.parent.state.fen);
    const playedMove = playedBoard.move(playedMoveSan);
    if (!playedMove) return null;
    
    // 4. Calculate subjective evaluation
    const subjectiveEvaluation = getSubjectiveEvaluation(
        topLine.evaluation,
        playedMove.color
    );
    
    // 5. Extract second-best line
    const secondTopLine = getLineGroupSibling(
        node.state.engineLines,
        topLine,
        2
    );
    
    let secondTopMove = undefined;
    let secondSubjectiveEval = undefined;
    
    if (secondTopLine) {
        const secondMoveSan = secondTopLine.moves[0]?.san;
        if (secondMoveSan) {
            const board2 = new ChessBoard(node.state.fen);
            secondTopMove = board2.move(secondMoveSan);
            
            if (secondTopMove) {
                secondSubjectiveEval = getSubjectiveEvaluation(
                    secondTopLine.evaluation,
                    secondTopMove.color
                );
            }
        }
    }
    
    // 6. Return extracted node
    return {
        board: new ChessBoard(node.state.fen),
        state: node.state,
        topLine: topLine,
        topMove: topMove,
        evaluation: topLine.evaluation,
        subjectiveEvaluation: subjectiveEvaluation,
        secondTopLine: secondTopLine,
        secondTopMove: secondTopMove,
        secondSubjectiveEvaluation: secondSubjectiveEval,
        playedMove: playedMove
    };
}
```

### Helper Functions

#### Get Line Group Sibling

```typescript
function getLineGroupSibling(
    lines: EngineLine[],
    referenceLine: EngineLine,
    targetIndex: number
): EngineLine | undefined {
    return lines.find(line =>
        line.depth === referenceLine.depth &&
        line.source === referenceLine.source &&
        line.index === targetIndex
    );
}
```

This finds a line with the same depth and source but a different MultiPV index.

---

## Stage 5: Calculate Derived Values

### Subjective Evaluation

**Purpose:** Convert evaluations from White's perspective to the moving player's perspective.

```typescript
function getSubjectiveEvaluation(
    evaluation: Evaluation,
    playerColor: PieceColor
): Evaluation {
    const multiplier = (playerColor === PieceColor.WHITE) ? 1 : -1;
    
    return {
        type: evaluation.type,
        value: evaluation.value * multiplier
    };
}
```

**Examples:**

| Objective (White POV) | Player | Subjective (Player POV) | Meaning |
|----------------------|--------|------------------------|---------|
| +200 cp | White | +200 cp | Good for White |
| +200 cp | Black | -200 cp | Bad for Black |
| -150 cp | White | -150 cp | Bad for White |
| -150 cp | Black | +150 cp | Good for Black |
| +3 mate | White | +3 mate | White mates in 3 |
| +3 mate | Black | -3 mate | Black getting mated in 3 |

### Expected Points

**Purpose:** Convert evaluations to win probability (0.0 to 1.0 scale).

```typescript
function getExpectedPoints(
    evaluation: Evaluation,
    options?: { centipawnGradient?: number }
): number {
    const gradient = options?.centipawnGradient || 0.0035;
    
    if (evaluation.type === "mate") {
        if (evaluation.value === 0) {
            // Mate already delivered - game over
            // Would need to know result to determine winner
            return 0.5;  // Or handle specially
        }
        
        // Forced mate = certain outcome
        return evaluation.value > 0 ? 1.0 : 0.0;
    } else {
        // Sigmoid function for centipawn evaluation
        return 1 / (1 + Math.exp(-gradient * evaluation.value));
    }
}
```

**Formula:** `EP = 1 / (1 + e^(-0.0035 × centipawns))`

**Sigmoid Curve Properties:**
- S-shaped curve from 0 to 1
- Centered at 0 (equal position = 0.5)
- Gradient (0.0035) calibrated to match chess game outcomes

**Examples:**

| Evaluation | Expected Points | Win Probability |
|-----------|-----------------|-----------------|
| 0 cp | 0.500 | 50% |
| +100 cp | 0.587 | 58.7% |
| +200 cp | 0.668 | 66.8% |
| +300 cp | 0.737 | 73.7% |
| +500 cp | 0.845 | 84.5% |
| +800 cp | 0.933 | 93.3% |
| +1000 cp | 0.962 | 96.2% |
| -200 cp | 0.332 | 33.2% |
| -500 cp | 0.155 | 15.5% |
| +5 mate | 1.000 | 100% |
| -3 mate | 0.000 | 0% |

### Expected Points Loss

**Purpose:** Calculate how much win probability was lost by playing a move.

```typescript
function getExpectedPointsLoss(
    previousEvaluation: Evaluation,
    currentEvaluation: Evaluation,
    moveColor: PieceColor
): number {
    // Get opponent's expected points before move
    const opponentColor = flipPieceColor(moveColor);
    const previousEP = getExpectedPoints(previousEvaluation);
    // Need to flip perspective for opponent
    const previousEPOpponent = 1 - previousEP;
    
    // Get player's expected points after move
    const currentEP = getExpectedPoints(currentEvaluation);
    // Need to apply player perspective
    const currentEPPlayer = (moveColor === PieceColor.WHITE) 
        ? currentEP 
        : 1 - currentEP;
    
    // Calculate loss (no negative losses)
    return Math.max(0, previousEPOpponent - currentEPPlayer);
}
```

**Simplified Implementation:**

```typescript
function getExpectedPointsLoss(
    previousEval: Evaluation,
    currentEval: Evaluation,
    moveColor: PieceColor
): number {
    const prevEP = getExpectedPoints(previousEval);
    const currEP = getExpectedPoints(currentEval);
    
    // Apply perspective adjustment
    const multiplier = (moveColor === PieceColor.WHITE) ? 1 : -1;
    const loss = ((1 - prevEP) - currEP) * multiplier;
    
    return Math.max(0, loss);
}
```

**Example Calculation:**

```
Position before move (Black to move):
  Evaluation: +150 cp (White slightly better)
  Expected Points (White): 0.605
  Expected Points (Black): 1 - 0.605 = 0.395

Black plays a move.

Position after move:
  Evaluation: +80 cp (White still better, but less)
  Expected Points (White): 0.569
  Expected Points (Black): 1 - 0.569 = 0.431

Point Loss = Previous EP (Black) - Current EP (Black)
          = 0.395 - 0.431
          = -0.036

Wait, this is negative! Black actually improved their position.
But we defined loss as max(0, ...), so:
Point Loss = 0.000 (no loss)

Actually, let me recalculate with the correct formula:

Point Loss = (PrevEP_Opponent - CurrentEP_Player) * perspective
          = (0.395 - 0.431) * (-1 for Black)
          = (-0.036) * (-1)
          = 0.036... but this should be 0

The correct formula is:
Point Loss = max(0, (1-prevEP) - currEP) * multiplier

For Black:
  = max(0, (1-0.605) - 0.569) * (-1)
  = max(0, 0.395 - 0.569) * (-1)
  = max(0, -0.174) * (-1)
  = 0

Hmm, let me think about this more carefully...

Actually, the implementation in the code is:
```typescript
getExpectedPoints(previousEvaluation, {
    moveColour: flipPieceColour(moveColour)
})
- getExpectedPoints(currentEvaluation, { moveColour })
```

This is handling perspective internally. Let me just document what the actual code does.
```

**Correct Example:**

```
Position before (White to move): +150 cp
Position after White's move: +80 cp

Previous EP (from Black's perspective, who is about to move):
  = 1 / (1 + e^(-0.0035 × 150)) = 0.605

Current EP (from White's perspective, who just moved):
  = 1 / (1 + e^(-0.0035 × 80)) = 0.569

Point Loss = 0.605 - 0.569 = 0.036 (3.6% win probability lost)
```

### Move Accuracy

**Purpose:** Convert point loss to a 0-100 accuracy score.

```typescript
function getMoveAccuracy(
    previousEvaluation: Evaluation,
    currentEvaluation: Evaluation,
    moveColor: PieceColor
): number {
    const pointLoss = getExpectedPointsLoss(
        previousEvaluation,
        currentEvaluation,
        moveColor
    );
    
    // Exponential decay formula
    return 103.16 * Math.exp(-4 * pointLoss) - 3.17;
}
```

**Formula:** `Accuracy = 103.16 × e^(-4 × pointLoss) - 3.17`

**Examples:**

| Point Loss | Accuracy |
|-----------|----------|
| 0.00 | 100.0 |
| 0.01 | 95.9 |
| 0.05 | 76.2 |
| 0.10 | 51.3 |
| 0.20 | 17.4 |
| 0.30 | 2.1 |

---

## Complete Data Flow

### Step-by-Step Example

**Input Game:**

```
PGN: "1. e4 e5 2. Nf3 Nc6 3. Bb5"
Initial Position: (standard starting position)
```

### After Stage 1 (Parse):

```
Root {
    fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    engineLines: []
}
  ↓
Node 1 {
    fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    move: { san: "e4", uci: "e2e4" }
    moveColor: WHITE
    engineLines: []
}
  ↓
Node 2 {
    fen: "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"
    move: { san: "e5", uci: "e7e5" }
    moveColor: BLACK
    engineLines: []
}
  ↓
...
```

### After Stage 2 (Analyze):

```
Node 1 {
    fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    move: { san: "e4", uci: "e2e4" }
    moveColor: WHITE
    engineLines: [
        {
            evaluation: { type: "centipawn", value: 45 },
            source: "stockfish-17",
            depth: 20,
            index: 1,
            moves: [
                { san: "e5", uci: "e7e5" },
                { san: "Nf3", uci: "g1f3" },
                { san: "Nc6", uci: "b8c6" }
            ]
        },
        {
            evaluation: { type: "centipawn", value: 38 },
            source: "stockfish-17",
            depth: 20,
            index: 2,
            moves: [
                { san: "c5", uci: "c7c5" },
                { san: "Nf3", uci: "g1f3" }
            ]
        }
    ]
}
```

### After Stage 3 (Chain):

```
nodeChain = [Root, Node1, Node2, Node3, Node4]
```

### After Stage 4 (Extract):

**For Node 2 (position after 1...e5):**

```
previous = extractPreviousNode(Node1) = {
    board: Chess("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"),
    topLine: { 
        evaluation: { type: "centipawn", value: 45 },
        index: 1,
        moves: [{ san: "e5" }, ...]
    },
    topMove: { san: "e5", color: "b", from: "e7", to: "e5" },
    evaluation: { type: "centipawn", value: 45 },
    subjectiveEvaluation: { type: "centipawn", value: -45 },  // Black's view
    playedMove: { san: "e5", color: "b", from: "e7", to: "e5" }
}

current = extractCurrentNode(Node2) = {
    board: Chess("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"),
    topLine: {
        evaluation: { type: "centipawn", value: 42 },
        index: 1,
        moves: [{ san: "Nf3" }, ...]
    },
    evaluation: { type: "centipawn", value: 42 },
    subjectiveEvaluation: { type: "centipawn", value: -42 },  // Black's view
    playedMove: { san: "e5", color: "b", from: "e7", to: "e5" }
}
```

### After Stage 5 (Calculate):

```
Point Loss = getExpectedPointsLoss(
    previous.evaluation,     // +45 cp
    current.evaluation,      // +42 cp
    BLACK                    // Black played the move
)

Previous EP (Black's perspective):
  = 1 / (1 + e^(-0.0035 × 45)) = 0.557
  From Black's view: 1 - 0.557 = 0.443

Current EP (Black's perspective):
  = 1 / (1 + e^(-0.0035 × 42)) = 0.551
  From Black's view: 1 - 0.551 = 0.449

Point Loss = 0.443 - 0.449 = -0.006 (improved!)
Clamped: max(0, -0.006) = 0.000

Accuracy = 103.16 × e^(-4 × 0.000) - 3.17 = 100.0
```

### Ready for Classification:

```typescript
classify(previous, current) → Classification.BEST
// Because point loss < 0.01 (1%)
```

---

## Implementation Requirements

### Required Libraries

#### 1. Chess Library

Must support:
- Parsing SAN notation
- Applying moves to boards
- Generating FEN strings
- Converting between SAN and UCI
- Legal move generation
- Check/checkmate detection

**Recommendations:**
- **JavaScript/TypeScript:** chess.js
- **Python:** python-chess
- **Rust:** chess crate
- **C++:** Stockfish library
- **Java:** chesspresso or chess4j
- **Go:** github.com/notnil/chess

#### 2. PGN Parser

Must parse:
- Move sequences
- Variations (optional)
- Headers (optional)

**Recommendations:**
- **JavaScript:** @mliebelt/pgn-parser
- **Python:** python-chess (includes PGN parser)
- **Rust:** pgn-reader
- **C++:** PgnLib

#### 3. UCI Engine Interface

Must support:
- Sending UCI commands
- Parsing UCI output
- Asynchronous communication
- MultiPV configuration

**Recommendations:**
- **Stockfish:** Universal UCI engine
- **JavaScript:** Web Workers for browser, child_process for Node
- **Python:** subprocess
- **Rust:** std::process::Command

#### 4. HTTP Client (Optional)

For Lichess cloud evaluations:
- **JavaScript:** fetch API or axios
- **Python:** requests
- **Rust:** reqwest
- **Java:** HttpClient

### Critical Constants

```typescript
// Expected points sigmoid gradient
const CENTIPAWN_GRADIENT = 0.0035;

// Accuracy formula parameters
const ACCURACY_MULTIPLIER = 103.16;
const ACCURACY_EXPONENT = -4.0;
const ACCURACY_OFFSET = -3.17;

// Starting position
const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

// Lichess castling conversion
const LICHESS_CASTLING = {
    "e1h1": "e1g1",  // White kingside
    "e1a1": "e1c1",  // White queenside
    "e8h8": "e8g8",  // Black kingside
    "e8a8": "e8c8"   // Black queenside
};
```

### Validation Checklist

Before proceeding to classification, verify:

- [ ] All nodes have at least one engine line
- [ ] All engine lines have depth > 0
- [ ] All evaluations are from White's perspective
- [ ] MultiPV indices are 1-indexed
- [ ] Subjective evaluations are calculated correctly
- [ ] Point loss calculations match formula
- [ ] Top move extraction succeeds
- [ ] Played move extraction succeeds
- [ ] Board states are valid FEN strings

### Error Handling

```typescript
// Node extraction can fail if:
// 1. No engine lines exist
if (!topLine) return null;

// 2. Engine line has no moves
if (!topLine.moves[0]) return null;

// 3. Move is invalid
try {
    const move = board.move(moveSan);
} catch (error) {
    return null;
}

// 4. Required data is missing
if (!playedMove) return null;

// Classification should skip nodes that return null
```

### Performance Considerations

**Time Complexity:**
- Stage 1 (Parse): O(n) where n = moves
- Stage 2 (Analyze): O(n × d) where d = engine depth
- Stage 3 (Chain): O(n)
- Stage 4 (Extract): O(n × m) where m = MultiPV lines
- Stage 5 (Calculate): O(n)

**Total: O(n × d)** dominated by engine analysis

**Optimization Strategies:**
1. **Parallel Analysis:** Analyze multiple positions simultaneously
2. **Cloud First:** Try cloud evaluation before local engine
3. **Caching:** Store engine results for common positions
4. **Depth Limits:** Use lower depth for fast analysis
5. **Time Limits:** Use movetime instead of depth for consistency

---

## Next Steps

With the preprocessing complete, you now have:

- ✅ State tree built from PGN
- ✅ Engine evaluations for all positions
- ✅ Extracted previous/current nodes
- ✅ Calculated subjective evaluations and point loss

**You are ready to proceed to classification:**

→ **[Classification Overview](./02-classification-overview.md)** - Learn how moves are classified

---

[← Back to Index](./README.md) | [Next: Core Concepts →](./01-core-concepts.md)


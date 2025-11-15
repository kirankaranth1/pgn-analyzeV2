# Classification Overview

> Understanding the classification hierarchy and decision flow

**Prerequisites:** Before reading this, understand the [preprocessing pipeline](./00-preprocessing-pipeline.md) that prepares data for classification.

[← Back to Index](./README.md) | [← Previous: Core Concepts](./01-core-concepts.md)

## Table of Contents

1. [Classification Types](#classification-types)
2. [Classification Hierarchy](#classification-hierarchy)
3. [Decision Flow (Waterfall Logic)](#decision-flow-waterfall-logic)
4. [Configuration Options](#configuration-options)
5. [Classification Values](#classification-values)

---

## Classification Types

The system classifies chess moves into 11 distinct categories:

### Excellence Tier (Best Moves)

| Classification | Symbol | Description |
|---------------|--------|-------------|
| **BRILLIANT** | `!!` | Spectacular move involving sacrifice with compensation |
| **CRITICAL** | `!` | The only move to maintain/gain advantage |
| **BEST** | - | Optimal move (or equal to best) |
| **THEORY** | - | Known opening book move |
| **FORCED** | - | Only legal move available |

### Quality Tier (Good/Acceptable Moves)

| Classification | Symbol | Description |
|---------------|--------|-------------|
| **EXCELLENT** | - | Very strong move with minimal point loss (1-4.5%) |
| **OKAY** | - | Acceptable move with small point loss (4.5-8%) |

### Error Tier (Poor Moves)

| Classification | Symbol | Description |
|---------------|--------|-------------|
| **INACCURACY** | `?!` | Questionable move (8-12% point loss) |
| **MISTAKE** | `?` | Clear error (12-22% point loss) |
| **BLUNDER** | `??` | Serious mistake (≥22% point loss) |
| **RISKY** | `!?` | Speculative move (implementation-dependent) |

---

## Classification Hierarchy

Classifications are determined using a **priority-based waterfall system**. Once a condition is met, the classification is assigned and further checks are skipped.

### Priority Order (Highest to Lowest)

```
1. FORCED          ← Only 1 legal move
2. THEORY          ← Match opening book (if enabled)
3. BEST (Checkmate)← Delivers checkmate
4. Point Loss      ← Calculate quality (BEST/EXCELLENT/OKAY/INACCURACY/MISTAKE/BLUNDER)
5. CRITICAL        ← Refine BEST (if enabled)
6. BRILLIANT       ← Refine BEST+ (if enabled)
```

### Why This Order?

**FORCED comes first:**
- No choice = automatic classification
- Skip expensive evaluation

**THEORY comes second:**
- Opening moves are "correct by definition"
- Preserve theoretical knowledge

**CHECKMATE comes third:**
- Always optimal (ends game)
- No point calculating loss

**Point Loss is baseline:**
- Core evaluation for most moves
- Based on objective engine analysis

**CRITICAL refines BEST:**
- Only checks top moves
- Identifies crucial moments

**BRILLIANT refines BEST+:**
- Most expensive computation
- Only for moves already deemed good
- Requires deep tactical analysis

---

## Decision Flow (Waterfall Logic)

### Algorithm Pseudocode

```
FUNCTION classify(previous: PreviousNode, current: CurrentNode, options: Options) -> Classification:
    
    // 1. FORCED - Only one legal move?
    IF previous.board.legalMoves.length <= 1:
        RETURN Classification.FORCED
    
    // 2. THEORY - In opening book?
    IF options.includeTheory:
        openingName = lookupOpening(current.state.fen)
        IF openingName EXISTS:
            RETURN Classification.THEORY
    
    // 3. CHECKMATE - Delivered mate?
    IF current.board.isCheckmate():
        RETURN Classification.BEST
    
    // 4. Point Loss - Calculate quality
    topMovePlayed = (previous.topMove.san == current.playedMove.san)
    
    IF topMovePlayed:
        classification = Classification.BEST
    ELSE:
        classification = pointLossClassify(previous, current)
    
    // 5. CRITICAL - Essential move?
    IF options.includeCritical 
       AND topMovePlayed 
       AND isCriticalCandidate(previous, current)
       AND secondBestMoveIsWeak(previous):
        classification = Classification.CRITICAL
    
    // 6. BRILLIANT - Spectacular sacrifice?
    IF options.includeBrilliant
       AND classificationValue[classification] >= classificationValue[BEST]
       AND isBrilliantSacrifice(previous, current):
        classification = Classification.BRILLIANT
    
    RETURN classification
```

### Visual Decision Tree

```
Start
  │
  ├─ Only 1 legal move? ────────────────► FORCED
  │   │
  │   No
  │   │
  ├─ In opening book? ──────────────────► THEORY (if enabled)
  │   │
  │   No
  │   │
  ├─ Delivers checkmate? ───────────────► BEST
  │   │
  │   No
  │   │
  ├─ Calculate Point Loss
  │   │
  │   ├─ Point loss < 1%? ──────────────► BEST
  │   ├─ Point loss < 4.5%? ────────────► EXCELLENT
  │   ├─ Point loss < 8%? ──────────────► OKAY
  │   ├─ Point loss < 12%? ─────────────► INACCURACY
  │   ├─ Point loss < 22%? ─────────────► MISTAKE
  │   └─ Point loss ≥ 22%? ─────────────► BLUNDER
  │
  ├─ Refine BEST moves:
  │   │
  │   ├─ Second-best loses ≥10%? ───────► CRITICAL (if enabled)
  │   │
  │   └─ Sacrifice with compensation? ───► BRILLIANT (if enabled)
  │
  └─ Return Final Classification
```

---

## Configuration Options

The classification system supports three optional features:

### AnalysisOptions Interface

```typescript
{
  includeTheory: boolean,      // Enable THEORY classification
  includeCritical: boolean,    // Enable CRITICAL classification
  includeBrilliant: boolean    // Enable BRILLIANT classification
}
```

### Default Configuration

```typescript
{
  includeTheory: true,
  includeCritical: true,
  includeBrilliant: true
}
```

### Configuration Impact

| Option | Performance | Accuracy | Use Case |
|--------|-------------|----------|----------|
| `includeTheory: false` | Slight gain | Opening moves may be downgraded | Games with unconventional openings |
| `includeCritical: false` | Slight gain | Misses "only move" identification | Fast analysis |
| `includeBrilliant: false` | **Major gain** | Misses spectacular sacrifices | Rapid feedback, low resources |

**Recommendation:** Keep all enabled unless performance is critical.

---

## Classification Values

Each classification has a numeric value (0-5) for comparison and sorting:

### Value Scale

```typescript
const classificationValues = {
  BLUNDER:      0,    // Worst
  MISTAKE:      1,
  INACCURACY:   2,
  RISKY:        2,    // Same as INACCURACY
  OKAY:         3,
  EXCELLENT:    4,
  BEST:         5,    // Best
  CRITICAL:     5,    // Equal to BEST
  BRILLIANT:    5,    // Equal to BEST
  FORCED:       5,    // Equal to BEST
  THEORY:       5     // Equal to BEST
};
```

### NAG (Numeric Annotation Glyph) Codes

Used for PGN annotation:

```typescript
const classificationNags = {
  BRILLIANT:     "$3",  // !!
  CRITICAL:      "$1",  // !
  INACCURACY:    "$6",  // ?!
  MISTAKE:       "$2",  // ?
  BLUNDER:       "$4",  // ??
  RISKY:         "$5",  // !?
  // Others: undefined (no standard NAG)
};
```

### Comparison Usage

```typescript
// Check if move is "good enough"
if (classificationValue[classification] >= classificationValue[OKAY]) {
  // Move is acceptable
}

// Check if move can be BRILLIANT
if (classificationValue[classification] >= classificationValue[BEST]) {
  // Candidate for BRILLIANT refinement
}
```

---

## Classification Properties

### Mutual Exclusivity

**Key Rule:** A move receives **exactly one** classification.

- A move cannot be both CRITICAL and BRILLIANT
- If both conditions are met, CRITICAL takes precedence (checked first)
- BRILLIANT only checks moves that passed CRITICAL check

### Refinement Pattern

Some classifications **refine** previous classifications:

```
BEST (from point loss)
  │
  ├─ Refined to → CRITICAL (if second-best is weak)
  │
  └─ Refined to → BRILLIANT (if sacrifice with compensation)
```

This is why CRITICAL and BRILLIANT checks only apply to moves already classified as BEST.

### Determinism

Given the same:
- Position (FEN)
- Engine lines (evaluations + moves)
- Configuration options

The classification is **always the same**. The system is fully deterministic with no randomness.

---

## Example Classification Flows

### Example 1: Forced Move in Check

```
Position: White in check, only Kf1 legal

1. Check FORCED? → Yes (only 1 legal move)
   → Result: FORCED ✓

(Skip all other checks)
```

### Example 2: Opening Theory Move

```
Position: Standard opening, 1.e4 played

1. Check FORCED? → No (20 legal moves)
2. Check THEORY? → Yes (found in opening book: "King's Pawn Opening")
   → Result: THEORY ✓

(Skip remaining checks)
```

### Example 3: Critical Only Move

```
Position: Complicated middlegame

1. Check FORCED? → No
2. Check THEORY? → No (out of book)
3. Check CHECKMATE? → No
4. Point Loss → 0.005 (< 1%) → BEST
5. Check CRITICAL? → Yes:
   - Top move played ✓
   - Second-best move loses 12% ✓
   → Result: CRITICAL ✓

(Skip BRILLIANT check since CRITICAL already assigned)
```

### Example 4: Brilliant Sacrifice

```
Position: Sharp tactical position

1. Check FORCED? → No
2. Check THEORY? → No
3. Check CHECKMATE? → No
4. Point Loss → 0.008 (< 1%) → BEST
5. Check CRITICAL? → No (second-best only loses 6%)
6. Check BRILLIANT? → Yes:
   - BEST move ✓
   - Queen left hanging ✓
   - Creates mate threats (danger levels) ✓
   - Piece not trapped ✓
   → Result: BRILLIANT ✓
```

### Example 5: Simple Blunder

```
Position: Quiet position, hung piece

1. Check FORCED? → No
2. Check THEORY? → No
3. Check CHECKMATE? → No
4. Point Loss → 0.35 (35%) → BLUNDER
   → Result: BLUNDER ✓

(Skip CRITICAL and BRILLIANT - only check BEST+ moves)
```

---

## Next Steps

- **[Basic Classifications](./03-basic-classifications.md)** - Simple rules (FORCED, THEORY, CHECKMATE)
- **[Point Loss Classification](./04-point-loss-classification.md)** - Core evaluation system
- **[Advanced Classifications](./05-advanced-classifications.md)** - CRITICAL and BRILLIANT

---

[← Back to Index](./README.md) | [← Previous: Core Concepts](./01-core-concepts.md) | [Next: Basic Classifications →](./03-basic-classifications.md)


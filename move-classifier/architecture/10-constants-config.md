# Constants and Configuration

> Thresholds, formulas, and configuration parameters

[← Back to Index](./README.md)

## Classification Thresholds

### Point Loss Thresholds

```typescript
const POINT_LOSS_THRESHOLDS = {
  BEST:        0.01,   // < 1% win probability loss
  EXCELLENT:   0.045,  // < 4.5%
  OKAY:        0.08,   // < 8%
  INACCURACY:  0.12,   // < 12%
  MISTAKE:     0.22,   // < 22%
  // BLUNDER:  ≥ 0.22  (≥ 22%)
};
```

### Special Thresholds

```typescript
const CRITICAL_THRESHOLD = 0.10;              // 10% loss for second-best
const COMPLETELY_WINNING = 700;               // +7.00 centipawns
```

---

## Formulas

### Expected Points

```typescript
const CENTIPAWN_GRADIENT = 0.0035;

function getExpectedPoints(evaluation: Evaluation): number {
  if (evaluation.type === "mate") {
    return evaluation.value > 0 ? 1.0 : 0.0;
  }
  return 1 / (1 + Math.exp(-CENTIPAWN_GRADIENT * evaluation.value));
}
```

### Move Accuracy

```typescript
const ACCURACY_MULTIPLIER = 103.16;
const ACCURACY_OFFSET = -3.17;
const ACCURACY_EXPONENT = -4;

function getMoveAccuracy(pointLoss: number): number {
  return ACCURACY_MULTIPLIER * Math.exp(ACCURACY_EXPONENT * pointLoss) + ACCURACY_OFFSET;
}
```

---

## Piece Values

```typescript
const pieceValues = {
  p: 1,   // Pawn
  n: 3,   // Knight
  b: 3,   // Bishop
  r: 5,   // Rook
  q: 9,   // Queen
  k: Infinity  // King
};
```

---

## Analysis Options

```typescript
interface AnalysisOptions {
  includeTheory: boolean;      // Default: true
  includeCritical: boolean;    // Default: true
  includeBrilliant: boolean;   // Default: true
}
```

### Recommended Configurations

**Full Analysis (default):**
```typescript
{ includeTheory: true, includeCritical: true, includeBrilliant: true }
```

**Fast Analysis:**
```typescript
{ includeTheory: true, includeCritical: true, includeBrilliant: false }
```

**Minimal:**
```typescript
{ includeTheory: false, includeCritical: false, includeBrilliant: false }
```

---

## Engine Configuration

### Default Settings

```typescript
const defaultEngineConfig = {
  depth: 20,           // Search depth (plies)
  multiPV: 2,          // Number of lines
  threads: 1,          // CPU threads
  hash: 128,           // Hash table (MB)
  timeLimit: undefined // No time limit
};
```

### Minimum Requirements

```typescript
const minimumEngineRequirements = {
  depth: 15,   // Reliable classification
  multiPV: 2   // Required for CRITICAL
};
```

---

## Performance Limits

```typescript
const performanceLimits = {
  maxEngineCount: 4,
  maxDepth: 50,
  maxMultiPV: 5,
  cacheSize: 1000,
  maxGameMoves: 500,
  xRayDepthLimit: 10
};
```

---

## NAG Codes

```typescript
const classificationNags = {
  BRILLIANT:   "$3",  // !!
  CRITICAL:    "$1",  // !
  INACCURACY:  "$6",  // ?!
  MISTAKE:     "$2",  // ?
  BLUNDER:     "$4",  // ??
  RISKY:       "$5"   // !?
};
```

---

## Implementation Reference

**Files:**
- `shared/src/constants/Classification.ts`
- `shared/src/constants/utils.ts`
- `shared/src/lib/reporter/expectedPoints.ts`
- `shared/src/lib/reporter/accuracy.ts`

---

[← Back to Index](./README.md)

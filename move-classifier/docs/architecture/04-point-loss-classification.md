# Point Loss Classification

> Core evaluation-based classification system

[← Back to Index](./README.md) | [← Previous: Basic Classifications](./03-basic-classifications.md)

## Overview

Point Loss Classification is the **core evaluation system** used for most moves. It calculates how much win probability was lost by playing a move compared to the best available option.

**Priority:** 4th (after FORCED, THEORY, CHECKMATE)

**Output:** One of six classifications based on point loss thresholds:
- BEST (< 1% loss)
- EXCELLENT (1-4.5% loss)
- OKAY (4.5-8% loss)
- INACCURACY (8-12% loss)
- MISTAKE (12-22% loss)
- BLUNDER (≥ 22% loss)

---

## Expected Points Formula

### Centipawn Evaluations

```
Expected Points = 1 / (1 + e^(-0.0035 × centipawns))
```

**Example Conversions:**

| Centipawns | Expected Points | Win Probability |
|-----------|----------------|-----------------|
| -500 | 0.155 | 15.5% |
| -200 | 0.332 | 33.2% |
| -100 | 0.413 | 41.3% |
| 0 | 0.500 | 50.0% |
| +100 | 0.587 | 58.7% |
| +200 | 0.668 | 66.8% |
| +500 | 0.845 | 84.5% |
| +800 | 0.933 | 93.3% |

### Mate Evaluations

```
Expected Points = {
  1.0  if mate > 0 (winning)
  0.0  if mate < 0 (losing)
}
```

---

## Point Loss Calculation

```
Point Loss = max(0, EP(before, opponent_perspective) - EP(after, player_perspective))
```

**Example:**
```
Before: +150 cp → EP = 0.605 (from Black's perspective)
After:  +80 cp  → EP = 0.569 (from Black's perspective)
Loss: 0.605 - 0.569 = 0.036 = 3.6%
Classification: EXCELLENT
```

---

## Thresholds

```typescript
const thresholds = {
  BEST:        0.01,   // < 1%
  EXCELLENT:   0.045,  // 1-4.5%
  OKAY:        0.08,   // 4.5-8%
  INACCURACY:  0.12,   // 8-12%
  MISTAKE:     0.22,   // 12-22%
  BLUNDER:     ∞       // ≥ 22%
};
```

---

## Special Cases

### 1. Centipawn → Centipawn

Standard case (see thresholds above).

### 2. Mate → Mate

**Winning mate to losing mate:** MISTAKE or BLUNDER

**Mate loss for winning side:**
- Loss 0-1: BEST
- Loss 1-2: EXCELLENT
- Loss 2-7: OKAY
- Loss ≥7: INACCURACY

### 3. Mate → Centipawn

**Lost winning mate:**
- Result ≥ +800 cp: EXCELLENT
- Result ≥ +400 cp: OKAY
- Result ≥ +200 cp: INACCURACY
- Result ≥ 0 cp: MISTAKE
- Result < 0 cp: BLUNDER

### 4. Centipawn → Mate

**Found mate:**
- Mate > 0: BEST
- Mate ≥ -2: BLUNDER (lost to mate in 2)
- Mate ≥ -5: MISTAKE
- Mate < -5: INACCURACY

---

## Implementation Reference

**File:** `shared/src/lib/reporter/classification/pointLoss.ts`

**Function:** `pointLossClassify(previous, current)`

---

[← Previous: Basic Classifications](./03-basic-classifications.md) | [Next: Advanced Classifications →](./05-advanced-classifications.md)

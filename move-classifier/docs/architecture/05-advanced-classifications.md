# Advanced Classifications

> CRITICAL and BRILLIANT move classifications

[← Back to Index](./README.md) | [← Previous: Point Loss Classification](./04-point-loss-classification.md)

## Table of Contents

1. [CRITICAL Classification](#critical-classification)
2. [BRILLIANT Classification](#brilliant-classification)

---

## CRITICAL Classification

### Overview

**Definition:** A move is CRITICAL when it is the only good move to maintain or achieve an advantage, and all alternatives are significantly worse.

**Priority:** 5th (refines BEST moves only)

### Conditions

All must be true:
1. ✅ Move classified as BEST (top engine move played)
2. ✅ Second-best move loses ≥ 10% expected points
3. ✅ Not already completely winning (< +700 cp)
4. ✅ Position not lost (evaluation ≥ 0 from player perspective)
5. ✅ Not trivial:
   - Not escaping check
   - Not capturing free material
   - Not queen promotion

### Algorithm

```
FUNCTION isCritical(previous, current) -> boolean:
    // Must be top move
    IF NOT isTopMovePlayed(previous, current):
        RETURN false
    
    // Must not be already mate
    IF current.subjectiveEval.type == "mate" AND current.subjectiveEval.value > 0:
        RETURN false
    
    // Must not be free capture
    IF current.playedMove.captured AND NOT isPieceSafe(capturedPiece):
        RETURN false
    
    // Check second-best move point loss
    IF NOT previous.secondTopLine:
        RETURN false
    
    secondBestLoss = calculatePointLoss(
        previous.evaluation,
        previous.secondTopLine.evaluation,
        current.playedMove.color
    )
    
    RETURN secondBestLoss >= 0.10  // 10% threshold
```

### Examples

#### Example 1: Critical Rook Sacrifice

**Position:** Tal vs Smyslov, 1959
```
FEN: r3kb1r/1bqn1pp1/p2ppn1p/1p6/3NPP2/2N1B3/PPPQ2PP/2KR3R w kq - 0 13
```

```
  a b c d e f g h
8 r . . . k b . r
7 . b q n . p p .
6 p . . p p n . p
5 . p . . . . . .
4 . . . N P P . .
3 . . N . B . . .
2 P P P Q . . P P
1 . . K R . . . R
```

**White to move:**
- Best move: `Nxe6!` (eval: +2.50) - Knight sacrifice forcing win
- Second-best: `Qe2` (eval: +0.30) - Loses most of the advantage
- Point loss of second-best: 0.25 (25%)
- **Result: CRITICAL** ✅ (Only move to maintain winning advantage)

#### Example 2: Critical Defense

**Position:** Sharp tactical position
```
FEN: r2q1rk1/1p1bbppp/p1np1n2/4p3/4P3/2NPBN2/PPPQ1PPP/R3K2R b KQ - 0 10
```

```
  a b c d e f g h
8 r . . q . r k .
7 . p . b b p p p
6 p . n p . n . .
5 . . . . p . . .
4 . . . . P . . .
3 . . N P B N . .
2 P P P Q . P P P
1 R . . . K . . R
```

**Black to move:**
- Best move: `Nd4!` (eval: -0.10) - Only move to hold position
- Second-best: `Qc7` (eval: -1.20) - Loses piece
- Point loss of second-best: 0.15 (15%)
- **Result: CRITICAL** ✅ (Defensive critical move)

---

## BRILLIANT Classification

### Overview

**Definition:** A move is BRILLIANT when it involves a spectacular piece sacrifice that maintains or increases the advantage through tactical compensation.

**Priority:** 6th (last, refines BEST+ moves only)

### Conditions

All must be true:
1. ✅ Move classified as BEST or better
2. ✅ Passes critical move candidate filter
3. ✅ Not a promotion
4. ✅ Leaves piece(s) hanging (unsafe)
5. ✅ Hanging pieces NOT protected by danger levels (counter-threats)
6. ✅ Hanging pieces NOT trapped (had to be sacrificed)
7. ✅ Not merely moving to safety

### Key Concepts

**Unsafe Piece:** Attacked more than defended, or attacked by lower-value piece.

**Danger Levels:** Counter-threats that make capturing the hanging piece risky.

**Trapped Piece:** Cannot move to any safe square.

### Algorithm (Simplified)

```
FUNCTION isBrilliant(previous, current) -> boolean:
    // Must pass basic filters
    IF NOT isCriticalCandidate(previous, current):
        RETURN false
    
    // Cannot be promotion
    IF current.playedMove.promotion:
        RETURN false
    
    // Find unsafe pieces after move
    unsafePieces = getUnsafePieces(current.board, current.playedMove.color)
    
    // Must have unsafe pieces (sacrifice)
    IF unsafePieces.length == 0:
        RETURN false
    
    // Check if not moving to safety
    previousUnsafe = getUnsafePieces(previous.board, current.playedMove.color)
    IF unsafePieces.length < previousUnsafe.length:
        RETURN false  // Moved to safety
    
    // Check danger levels (counter-threats)
    IF unsafePieces.every(piece => hasDangerLevels(piece)):
        RETURN false  // Protected by tactics
    
    // Check trapped pieces
    trappedPieces = unsafePieces.filter(piece => isPieceTrapped(piece))
    IF trappedPieces.length == unsafePieces.length:
        RETURN false  // All pieces trapped (had no choice)
    
    RETURN true
```

### Examples

#### Example 1: Queen Sacrifice with Mating Attack

**Position:** Levitsky vs Marshall, 1912 (Famous "Gold Coins Game")
```
FEN: r1b2k1r/ppp1q1pp/5n2/4p3/1bBPn3/2P1NN2/PP3PPP/R2Q1RK1 b - - 0 14
```

```
  a b c d e f g h
8 r . b . . k . r
7 p p p . q . p p
6 . . . . . n . .
5 . . . . p . . .
4 . b B P n . . .
3 . . P . N N . .
2 P P . . . P P P
1 R . . Q . R K .
```

**Black to move:**
- Move: `Qg3!!` (eval before: +0.40, eval after: +0.60)
- Queen is left completely hanging on g3
- But creates unstoppable mating threats:
  - If `fxg3`, then `Ne2#` is mate
  - If White doesn't take, threats like `Qg2#` or `Qf2#` are coming
  - White's pieces are too uncoordinated to defend
- **Result: BRILLIANT** ✅ (Spectacular sacrifice with forced mate)

#### Example 2: Rook Sacrifice Opening Lines

**Position:** Tactical middlegame
```
FEN: r2q1rk1/pp3ppp/2p1bn2/3p4/3P4/2PB1N2/PP2QPPP/R4RK1 w - - 0 14
```

```
  a b c d e f g h
8 r . . q . r k .
7 p p . . . p p p
6 . . p . b n . .
5 . . . p . . . .
4 . . . P . . . .
3 . . P B . N . .
2 P P . . Q P P P
1 R . . . . R K .
```

**White to move:**
- Move: `Bxh7+!` (eval before: +0.30, eval after: +0.35)
- Bishop sacrifice on h7 (classic Greek gift)
- After `Kxh7 Ng5+ Kg8 Qh5`:
  - Rook on a1 still hangs
  - But White has unstoppable attack
  - Black cannot safely capture material
- **Result: BRILLIANT** ✅ (Leaves pieces hanging for attack)

#### Example 3: Not Brilliant (Trapped Piece)

**Position:** Endgame with trapped knight
```
FEN: 8/8/3k4/p1p5/PnP5/1P6/3K4/8 w - - 0 35
```

```
  a b c d e f g h
8 . . . . . . . .
7 . . . . . . . .
6 . . . k . . . .
5 p . p . . . . .
4 P n P . . . . .
3 . P . . . . . .
2 . . . K . . . .
1 . . . . . . . .
```

**Black to move:**
- Knight on b4 is trapped (no safe squares)
- Move: `Nd3` (leaves knight on d3)
- Knight still trapped and will be captured
- Eval: -2.50 (losing)
- **Result: BEST** ❌ (Not BRILLIANT - piece was already trapped, no choice)

#### Example 4: Not Brilliant (Protected by Danger Levels)

**Position:** Tactical position
```
FEN: r1bq1rk1/pp1n1ppp/2p1pn2/8/1bPP4/2NBPN2/PP3PPP/R1BQK2R w KQ - 0 9
```

```
  a b c d e f g h
8 r . b q . r k .
7 p p . n . p p p
6 . . p . p n . .
5 . . . . . . . .
4 . b P P . . . .
3 . . N B P N . .
2 P P . . . P P P
1 R . B Q K . . R
```

**White to move:**
- Move: `Nxe4` (captures pawn, leaves knight hanging)
- Eval: +0.60
- If `Nxe4`, then `Bxf7+` wins queen
- Knight "hanging" but protected by counter-threat
- **Result: BEST** ❌ (Not BRILLIANT - protected by danger levels)

---

## Comparison

| Aspect | CRITICAL | BRILLIANT |
|--------|----------|-----------|
| **Frequency** | Rare (~1-2% of moves) | Very rare (~0.1-0.5%) |
| **Computation** | Fast (compare 2 evaluations) | Expensive (piece safety analysis) |
| **Philosophy** | "Only move" | "Spectacular sacrifice" |
| **Evaluation** | Best move by default | Finds hidden tactics |

---

## Implementation References

**CRITICAL:**
- File: `shared/src/lib/reporter/classification/critical.ts`
- Function: `considerCriticalClassification`

**BRILLIANT:**
- File: `shared/src/lib/reporter/classification/brilliant.ts`
- Function: `considerBrilliantClassification`

**Supporting:**
- `shared/src/lib/reporter/utils/pieceSafety.ts`
- `shared/src/lib/reporter/utils/dangerLevels.ts`
- `shared/src/lib/reporter/utils/pieceTrapped.ts`

---

[← Previous: Point Loss Classification](./04-point-loss-classification.md) | [Next: Attack & Defense Systems →](./06-attack-defense.md)

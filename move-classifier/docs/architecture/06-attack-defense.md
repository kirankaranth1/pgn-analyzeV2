# Attack and Defense Systems

> Tactical analysis for piece safety and brilliant moves

[← Back to Index](./README.md)

## Overview

The attack and defense analysis system identifies which pieces attack and defend specific squares, including x-ray (transitive) attacks through pieces.

## Core Functions

### Direct Attacks

```
getDirectAttackingMoves(board, targetPiece) -> Move[]
```

Returns all pieces that directly attack a target square.

### X-Ray Attacks

```
getAllAttackingMoves(board, targetPiece, transitive=true) -> Move[]
```

Discovers hidden attackers (pins, batteries, x-rays):
1. Find direct attackers
2. For each attacker, simulate its removal
3. Check for revealed attackers
4. Recursively process revealed attackers

**Example:**
```
Position: Rook on a1, Queen on a4, Enemy King on a8
Direct attacker: Queen
Remove Queen → Rook attacks king (x-ray through queen)
Result: [Queen, Rook] (both attack a8)
```

### Defenders

```
getDefendingMoves(board, targetPiece) -> Move[]
```

Finds pieces that can recapture if target is taken:
1. Simulate capture by each attacker
2. Find pieces that can recapture
3. Return minimum set of defenders

### Piece Safety

```
isPieceSafe(board, piece) -> boolean
```

Complex algorithm considering:
- Number of attackers vs defenders
- Piece values (can lower-value piece capture?)
- Special cases (rook for two pieces, pawn defenders)

**Returns:**
- `true` if piece is safe
- `false` if piece is hanging/unsafe

---

## Usage in Classification

**BRILLIANT moves:**
- Identifies hanging pieces (unsafe)
- Checks if sacrifice is justified (danger levels)
- Validates pieces aren't trapped

**CRITICAL moves:**
- Checks if captured piece was safe (not free material)

---

## Implementation Reference

**Files:**
- `shared/src/lib/reporter/utils/attackers.ts`
- `shared/src/lib/reporter/utils/defenders.ts`
- `shared/src/lib/reporter/utils/pieceSafety.ts`

---

[← Back to Index](./README.md) | [Next: Tactical Analysis →](./07-tactical-analysis.md)

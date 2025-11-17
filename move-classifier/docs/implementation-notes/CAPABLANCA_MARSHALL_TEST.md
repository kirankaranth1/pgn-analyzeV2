# Capablanca vs Marshall (1918) - Standard Integration Test

## Overview

This test suite uses the famous historical game between **Jose Raul Capablanca** and **Frank James Marshall** from **New York 1918**. This game is significant because it introduced the **Marshall Attack** in the Ruy Lopez opening, one of the most aggressive gambits against the Ruy Lopez.

## Game Details

- **Event**: New York
- **Site**: New York, NY USA
- **Date**: 1918.10.23
- **Round**: 1
- **Result**: 1-0 (White wins)
- **White**: Jose Raul Capablanca
- **Black**: Frank James Marshall
- **ECO**: C89 (Ruy Lopez, Marshall Attack)
- **Moves**: 36 full moves (71 half-moves)

## Why This Game?

This game serves as the **STANDARD TEST CASE** for all integration tests of the chess move classifier for several reasons:

1. **Historical Significance**: First public appearance of the Marshall Attack
2. **Complexity**: Contains tactical complications, sacrifices, and precise defensive play
3. **Length**: 36 moves provides substantial data for testing
4. **Variety**: Includes opening theory, tactical middlegame, and endgame
5. **Quality**: High-level play from two world-class players

## Test Coverage

The test suite (`test_capablanca_marshall.py`) includes **16 comprehensive tests**:

### Parsing Tests (5 tests)
- ✅ Parse complete 71-move game
- ✅ Verify opening moves (Ruy Lopez structure)
- ✅ Identify Marshall Attack critical move (8...d5)
- ✅ Parse castling notation (both sides)
- ✅ Verify final position and check

### Full Pipeline Tests (3 tests)
- ✅ Complete pipeline with cloud evaluation
- ✅ Complete pipeline with local Stockfish
- ✅ Parse game without engine analysis (fast test)

### Move Pair Extraction (1 test)
- ✅ Extract all 70 move pairs for classification

### Position Verification (3 tests)
- ✅ Marshall Attack position (after 8...d5)
- ✅ Complex tactical position (17...Bh2+ check)
- ✅ Endgame position before final move

### Metrics Calculation (1 test)
- ✅ Calculate move accuracy for all moves

### Standard Integration Suite (3 tests)
These tests are marked with `@pytest.mark.standard_integration_test` and **MUST PASS** for any implementation:
- ✅ Parse standard game correctly
- ✅ Maintain correct tree structure
- ✅ Extract nodes for classification

## Running the Tests

### Quick Tests (0.7 seconds)
Tests that don't require network or engine:
```bash
pytest tests/integration/test_capablanca_marshall.py -m "not slow and not network and not engine"
```

### All Tests (varies)
Complete test suite including cloud/engine tests:
```bash
pytest tests/integration/test_capablanca_marshall.py -v
```

### Only Standard Integration Tests
Tests that must always pass:
```bash
pytest tests/integration/test_capablanca_marshall.py -m standard_integration_test
```

## Usage in Future Implementations

**ALL FUTURE IMPLEMENTATIONS** must pass these tests:

1. **Parsing**: Must correctly parse all 71 moves
2. **Structure**: Must maintain parent-child relationships
3. **Extraction**: Must extract 60+ move pairs for classification
4. **Accuracy**: Must calculate valid accuracy metrics (0-100)
5. **Integration**: Must process complete game through full pipeline

## Game PGN

```pgn
1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.O-O Be7 6.Re1 b5 7.Bb3
O-O 8.c3 d5 9.exd5 Nxd5 10.Nxe5 Nxe5 11.Rxe5 Nf6 12.Re1 Bd6
13.h3 Ng4 14.Qf3 Qh4 15.d4 Nxf2 16.Re2 Bg4 17.hxg4 Bh2+ 18.Kf1
Bg3 19.Rxf2 Qh1+ 20.Ke2 Bxf2 21.Bd2 Bh4 22.Qh3 Rae8+ 23.Kd3
Qf1+ 24.Kc2 Bf2 25.Qf3 Qg1 26.Bd5 c5 27.dxc5 Bxc5 28.b4 Bd6
29.a4 a5 30.axb5 axb4 31.Ra6 bxc3 32.Nxc3 Bb4 33.b6 Bxc3
34.Bxc3 h6 35.b7 Re3 36.Bxf7+
```

## Key Positions to Test

### Position 1: Marshall Attack (After 8...d5)
Black sacrifices a pawn with d5, beginning the Marshall Attack.
- **FEN**: `r1bq1rk1/2p1bppp/p1n2n2/1p1Pp3/8/1BP2N2/PP1P1PPP/RNBQR1K1 b - - 0 9`
- **Test**: Verify pawn on d5, typical Marshall structure

### Position 2: Tactical Check (After 17...Bh2+)
Black delivers check, forcing the white king to move.
- **Test**: Verify board.is_check() returns True
- **Test**: Verify White must respond to check

### Position 3: Endgame (Before 36.Bxf7+)
The final tactical blow, winning Black's rook.
- **Test**: Verify position is valid
- **Test**: Verify correct piece placement

## Integration with Main Test Suite

This test file integrates with the overall test suite:

```bash
# Run ALL integration tests (including Capablanca-Marshall)
pytest tests/integration/ -v

# Count all tests
pytest tests/integration/ --collect-only
```

**Total Integration Tests**: 53 (37 original + 16 Capablanca-Marshall)

## Best Practices for Future Tests

When adding new features, ensure they:

1. ✅ Can parse the Capablanca-Marshall game
2. ✅ Can extract all 70 move pairs
3. ✅ Can calculate accuracy for all moves
4. ✅ Maintain tree structure integrity
5. ✅ Process the game in reasonable time

## References

- Original game: New York 1918
- Chess opening: ECO C89 (Marshall Attack)
- Historical context: This was the first public appearance of Marshall's prepared innovation
- Result: Capablanca successfully defended and won a brilliant game

## Notes

- The game ends at move 36 (Bxf7+) with Black resigning, though the notation doesn't show the resignation
- Move 8...d5 is the critical Marshall Attack gambit
- Capablanca's defense is considered one of the finest examples of precise play against this gambit
- This game has been extensively analyzed and appears in many chess textbooks

---

**This test suite ensures the chess move classifier can handle real, high-quality historical games with complex tactical and strategic themes.**


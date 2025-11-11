# Classification Analysis - Morphy Opera Game

## Settings
- **Depth**: 16
- **Multi-PV**: 2
- **Expected**: depth 16, lines 2

## Mismatched Moves

### Move 6: Bg4 (Black)
- **Expected**: EXCELLENT
- **Actual**: MISTAKE
- **Issue**: Not in top 2 multi-PV lines
- **Engine best**: Nf6
- **Analysis**: This is a playable move in the Philidor Defense. Engine at depth 16 prefers Nf6, but Bg4 is not a mistake - it's a reasonable alternative. Should be EXCELLENT or at worst OKAY.

### Move 7: dxe5 (White) 
- **Expected**: BEST
- **Actual**: MISTAKE (47.04%)
- **Issue**: Engine says Be3 is better
- **Analysis**: This is the critical decision point. At depth 16, the engine might think Be3 is slightly better, but dxe5 is the principled continuation. This move leads to White's advantage.

###  Move 8: Bxf3 (Black)
- **Expected**: EXCELLENT  
- **Actual**: BLUNDER
- **Issue**: Not in multi-PV
- **Analysis**: After dxe5, this is a natural recapture. Not the best but not a blunder.

### Move 12: Nf6 (Black)
- **Expected**: EXCELLENT
- **Actual**: BLUNDER
- **Issue**: Not in multi-PV
- **Analysis**: Developing the knight. This is a standard defensive move.

### Move 13: Qb3 (White)
- **Expected**: CRITICAL
- **Actual**: BEST
- **Issue**: CRITICAL detection not working
- **Analysis**: This move is indeed critical - it attacks f7 and b7 simultaneously. The second-best move must lose significant advantage.

### Move 17: Bg5 (White)  
- **Expected**: EXCELLENT
- **Actual**: BEST
- **Issue**: Move is in top 2, but might not be #1
- **Analysis**: Excellent attacking move, pinning the knight.

### Move 18: b5 (Black)
- **Expected**: INACCURACY
- **Actual**: BLUNDER
- **Issue**: Classification too harsh
- **Analysis**: A defensive attempt that doesn't work well, but calling it a BLUNDER is too harsh.

### Move 19: Nxb5 (White)
- **Expected**: BRILLIANT
- **Actual**: BEST
- **Issue**: BRILLIANT detection not working
- **Analysis**: This is the famous knight sacrifice! It leaves the knight hanging but creates unstoppable threats. Classic BRILLIANT move.

### Move 20: cxb5 (Black)
- **Expected**: INACCURACY  
- **Actual**: BLUNDER
- **Issue**: Classification too harsh
- **Analysis**: Taking the knight is somewhat forced. Engine says Qb4+ is better, but cxb5 is human.

### Move 25: Rxd7 (White)
- **Expected**: BRILLIANT
- **Actual**: BEST
- **Issue**: BRILLIANT detection not working
- **Analysis**: The spectacular rook sacrifice! Leaves material hanging for mating attack.

### Move 27: Rd1 (White)
- **Expected**: CRITICAL  
- **Actual**: BEST
- **Issue**: CRITICAL detection not working
- **Analysis**: The only move to maintain the mating attack.

### Move 28: Qe6 (Black)
- **Expected**: INACCURACY
- **Actual**: BLUNDER
- **Issue**: Classification too harsh

### Move 31: Qb8+ (White)
- **Expected**: BRILLIANT
- **Actual**: CRITICAL
- **Issue**: Should be BRILLIANT - the quiet queen move that forces mate
- **Analysis**: This is the famous quiet queen sacrifice! The most brilliant move of the game.

### Move 33: Rd8# (Checkmate)
- **Expected**: BEST
- **Actual**: none
- **Issue**: Checkmate not being classified

## Root Causes

### 1. Multi-PV Limitation
With only 2 lines analyzed, many reasonable moves aren't in the engine's top choices and fall back to broken comparison logic.

### 2. BRILLIANT Detection Not Working  
Moves 19, 25, and 31 should all be BRILLIANT but aren't detected:
- Nxb5: Sacrifice with compensation
- Rxd7: Rook sacrifice
- Qb8+: Quiet queen sacrifice leading to mate

### 3. Classification Too Harsh
When moves aren't in multi-PV, the fallback makes them BLUNDER/MISTAKE even when they're reasonable moves.

### 4. CRITICAL Detection Issues
Moves 13, 27 should be CRITICAL (only good move) but aren't detected.

### 5. Checkmate Not Classified
The final move Rd8# isn't classified at all.

## Recommended Fixes

1. **Increase Multi-PV to 5+** when moves aren't found in top 2
2. **Fix BRILLIANT detection** - check for sacrifices with tactical compensation
3. **Fix CRITICAL detection** - check second-best move point loss
4. **Fix Checkmate classification** - should be BEST automatically
5. **Improve fallback** - when move not in multi-PV, be more lenient or analyze that move specifically

## Fundamental Issue

The original system likely either:
- Analyzed more than 2 lines
- Had post-processing to detect tactical themes (sacrifices, mating attacks)
- Used hybrid human+engine analysis for famous games
- Had a completely different approach to moves not in multi-PV

With strict engine analysis at depth 16, multi-PV 2, it's impossible to match the expected output perfectly because many good moves simply aren't in the top 2 and can't be accurately evaluated.


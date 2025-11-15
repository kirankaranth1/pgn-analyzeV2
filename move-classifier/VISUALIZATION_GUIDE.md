# Capablanca vs Marshall (1918) - Visualization Tools

This directory contains tools to visualize and inspect the preprocessed nodes from the famous Capablanca vs Marshall game before implementing the classification logic.

## Quick Start

### View Specific Move

```bash
python visualize_capablanca_nodes.py --move 8
```

Shows move 8 (both 8.c3 and 8...d5 - the Marshall Attack!)

### View First 10 Moves

```bash
python visualize_capablanca_nodes.py --end 10
```

### View with Engine Analysis

```bash
python visualize_capablanca_nodes.py --with-engine --move 15
```

**Warning:** This is slow and requires either internet connection (for cloud) or Stockfish installed.

### Save Output to File

```bash
python visualize_capablanca_nodes.py --move 8 --save output.txt
```

## Command-Line Options

### Basic Options

- `--move N` - Show only move N (e.g., `--move 8` shows 8.c3 and 8...d5)
- `--start N` - Start from node N
- `--end N` - End at node N
- `--show-fen` - Display full FEN strings
- `--show-extracted` - Show extracted node pairs for classification

### Engine Options (Slow!)

- `--with-engine` - Run full preprocessing with engine analysis
- `--depth N` - Set engine depth (default: 12)
- `--cloud` - Use Lichess cloud evaluation

### Output Options

- `--save FILE` - Save visualization to file

## Examples

### Explore the Marshall Attack

```bash
# Move 8: The famous Marshall Attack gambit
python visualize_capablanca_nodes.py --move 8 --show-fen
```

Output shows:
- Node 15: 8.c3 (White's quiet move)
- Node 16: 8...d5! (Black's Marshall Attack gambit)

### Check the Tactical Sequence

```bash
# Moves 17-19: Complex tactical play
python visualize_capablanca_nodes.py --start 33 --end 39
```

### View Final Moves

```bash
# Last 5 moves of the game
python visualize_capablanca_nodes.py --start 67
```

### Full Game with Engine Analysis

```bash
# Complete analysis (takes 10-15 minutes!)
python visualize_capablanca_nodes.py --with-engine --depth 12 --cloud --save full_analysis.txt
```

## What Each Node Shows

### Basic Information
- Node ID (unique identifier)
- Mainline flag (always True for this game)
- Parent/Children relationships

### Move Details
- SAN notation (e.g., "Nf3", "O-O", "Qxf7+")
- UCI notation (e.g., "g1f3", "e1g1", "f7f7")
- Move color (WHITE or BLACK)

### Position Information
- FEN string (if `--show-fen` is used)
- Whose turn it is
- Castling rights
- Check/Checkmate status
- Material count (in pawns)

### Engine Analysis (with `--with-engine`)
- Evaluation (centipawns or mate score)
- Engine source (lichess-cloud or stockfish-17)
- Search depth
- Top continuation moves
- Second-best line (MultiPV)

### Move Quality (with `--with-engine`)
- Move accuracy (0-100%)
- Point loss
- Comparison with top engine move

### Extracted Pairs (with `--show-extracted`)
Shows the data that will be passed to classification:
- Previous node state (before move)
- Current node state (after move)
- Both subjective evaluations
- Top moves from both positions
- Calculated accuracy

## Key Positions to Explore

### 1. The Marshall Attack (Move 8)
```bash
python visualize_capablanca_nodes.py --move 8
```
Black plays 8...d5!, sacrificing a pawn to launch an attack.

### 2. Tactical Check (Move 17)
```bash
python visualize_capablanca_nodes.py --move 17
```
Black plays 17...Bh2+, delivering check and forcing White's king to move.

### 3. King March (Moves 22-24)
```bash
python visualize_capablanca_nodes.py --start 43 --end 49
```
Capablanca's king walks up the board under Black's attack!

### 4. Final Blow (Move 36)
```bash
python visualize_capablanca_nodes.py --move 36
```
White plays 36.Bxf7+, winning Black's rook and the game.

## Node Structure for Classification

Each node contains:

```python
StateTreeNode:
  - id: str                    # Unique identifier
  - mainline: bool             # True for main game line
  - parent: StateTreeNode      # Previous position
  - children: List[StateTreeNode]  # Next positions
  - state: BoardState
      - fen: str               # Position in FEN notation
      - move: Move            # Move that led here
      - move_color: str       # "WHITE" or "BLACK"
      - engine_lines: List[EngineLine]  # Engine analysis
      - classification: Optional[Classification]  # To be implemented
      - accuracy: Optional[float]  # 0-100
      - opening: Optional[str]     # Opening name
```

## Using the Data for Classification

The visualization helps you:

1. **Verify Parsing** - Ensure all 71 moves are parsed correctly
2. **Check Structure** - Verify parent-child relationships
3. **Inspect Positions** - Manually check critical positions
4. **Review Engine Data** - See what evaluations are available
5. **Test Extraction** - Verify node pairs can be extracted
6. **Plan Classification** - Understand what data classifiers will receive

## Interactive Exploration with Jupyter

For interactive exploration with chess board visualization:

```bash
jupyter notebook visualize_capablanca.ipynb
```

**Features:**
- Visual chess boards for each position
- Interactive position explorer
- Move-by-move navigation
- Detailed node inspection
- Summary tables

## Tips

1. **Start Simple** - First run without `--with-engine` to see the structure
2. **Focus on Key Moves** - Use `--move` to inspect specific positions
3. **Save Analysis** - Use `--save` to keep a record of engine analysis
4. **Check Accuracy** - With engine analysis, verify accuracy calculations
5. **Test Extraction** - Use `--show-extracted` to see classification input

## Performance

- **Without engine**: Instant (~0.1 seconds)
- **With cloud**: 30-60 seconds (depends on network)
- **With local engine**: 5-15 minutes (depends on depth)

## Troubleshooting

### "No engine lines available"
Run with `--with-engine` to get engine analysis.

### "Cannot extract pair"
Engine analysis is required for extraction. Run with `--with-engine`.

### "Stockfish not installed"
Either install Stockfish 17 or use `--cloud` for cloud evaluation.

### "Rate limited"
Lichess cloud API has rate limits. Wait a few seconds and retry.

## Next Steps

After verifying the node structure:

1. Review extracted node pairs with `--show-extracted`
2. Understand what data is available for classification
3. Implement classification logic based on the documentation
4. Test classification on this game
5. Verify classification results manually

## Files

- **`visualize_capablanca_nodes.py`** - Command-line visualization tool
- **`visualize_capablanca.ipynb`** - Jupyter notebook (interactive)
- **`CAPABLANCA_MARSHALL_TEST.md`** - Test documentation
- **`test_capablanca_marshall.py`** - Integration tests

---

**Ready to implement classification?** Use this tool to understand the input data structure first!


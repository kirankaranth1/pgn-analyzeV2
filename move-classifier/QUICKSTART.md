# Quick Start Guide

## Installation

1. Install Python dependencies:
```bash
cd move-classifier
pip install -r requirements.txt
```

2. Verify Stockfish is installed:
```bash
# On macOS with Homebrew:
brew install stockfish

# Verify installation:
which stockfish
# Should output: /opt/homebrew/bin/stockfish (or similar)
```

## Running Your First Analysis

1. Use the included example game:
```bash
python main.py \
  --pgn example.pgn \
  --stockfish /opt/homebrew/bin/stockfish \
  --output example-analysis.json
```

2. View the results:
```bash
cat example-analysis.json | python -m json.tool | head -50
```

## Common Commands

### Quick Analysis (Lower Depth)
```bash
python main.py \
  --pgn game.pgn \
  --stockfish stockfish \
  --output analysis.json \
  --depth 15
```

### Fast Analysis (Skip BRILLIANT)
```bash
python main.py \
  --pgn game.pgn \
  --stockfish stockfish \
  --output analysis.json \
  --no-brilliant
```

### Deep Analysis (High Depth, More Threads)
```bash
python main.py \
  --pgn game.pgn \
  --stockfish stockfish \
  --output analysis.json \
  --depth 25 \
  --threads 4 \
  --hash 512
```

## Understanding the Output

The JSON output contains three main sections:

1. **game_info**: Player names, date, result, etc.
2. **moves**: Detailed analysis of each move
3. **statistics**: Summary counts and average accuracy per player

### Move Analysis Example
```json
{
  "move_number": 10,
  "color": "white",
  "san": "Nf3",
  "classification": "best",
  "accuracy": 98.5,
  "evaluation": {
    "type": "centipawn",
    "value": 45
  }
}
```

### Classification Meanings

- **brilliant**: Spectacular sacrifice (rare!)
- **critical**: Only move to maintain advantage
- **best**: Optimal move (< 1% loss)
- **excellent**: Strong move (1-4.5% loss)
- **okay**: Acceptable (4.5-8% loss)
- **inaccuracy**: Questionable (8-12% loss)
- **mistake**: Clear error (12-22% loss)
- **blunder**: Serious mistake (≥ 22% loss)

## Troubleshooting

### "Stockfish not found"
Make sure the path is correct:
```bash
# Find stockfish location:
which stockfish

# Use the full path in the command:
python main.py --pgn game.pgn --stockfish /full/path/to/stockfish --output out.json
```

### Analysis is slow
- Reduce depth: `--depth 15`
- Skip BRILLIANT: `--no-brilliant`
- Use only 1 PV: `--multipv 1` (disables CRITICAL too)

### Out of memory
Reduce hash size: `--hash 64`

## Next Steps

- Read the full [README.md](README.md) for all options
- Check the [architecture documentation](architecture/README.md) for technical details
- Analyze your own games!


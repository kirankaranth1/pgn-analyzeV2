# Chess Move Classifier

A comprehensive chess move classification system that analyzes PGN files using Stockfish and classifies each move into categories like **BRILLIANT**, **CRITICAL**, **BEST**, **EXCELLENT**, **OKAY**, **INACCURACY**, **MISTAKE**, and **BLUNDER**.

## Features

- **Stockfish Integration**: Uses Stockfish UCI protocol with multi-PV analysis
- **11 Classification Types**: Comprehensive move quality assessment
- **Opening Book**: Recognizes thousands of opening positions
- **Accuracy Scoring**: Calculates 0-100 accuracy scores for each move
- **JSON Output**: Detailed analysis reports with statistics
- **Configurable**: Adjustable depth, multi-PV, and classification options

## Classifications

| Classification | Description | Criteria |
|---------------|-------------|----------|
| **BRILLIANT** | Spectacular sacrifice | Leaves pieces hanging with compensation |
| **CRITICAL** | Essential only move | Only move to maintain advantage |
| **BEST** | Optimal move | < 1% win probability loss |
| **EXCELLENT** | Very strong move | 1-4.5% loss |
| **OKAY** | Acceptable move | 4.5-8% loss |
| **INACCURACY** | Questionable move | 8-12% loss |
| **MISTAKE** | Clear error | 12-22% loss |
| **BLUNDER** | Serious mistake | ≥ 22% loss |
| **THEORY** | Opening book move | Found in opening database |
| **FORCED** | Only legal move | No choice available |

## Installation

### Requirements

- Python 3.7+
- Stockfish chess engine

### Setup

1. Clone or download this repository

2. Install Python dependencies:
```bash
cd move-classifier
pip install -r requirements.txt
```

3. Download Stockfish:
   - **macOS/Linux**: [Stockfish Downloads](https://stockfishchess.org/download/)
   - **macOS Homebrew**: `brew install stockfish`
   - Extract and note the path to the binary

## Usage

### Basic Usage

```bash
python main.py \
  --pgn game.pgn \
  --stockfish /path/to/stockfish \
  --output analysis.json
```

### Advanced Options

```bash
python main.py \
  --pgn game.pgn \
  --stockfish /usr/local/bin/stockfish \
  --output analysis.json \
  --depth 25 \
  --multipv 3 \
  --threads 4 \
  --hash 256 \
  --no-brilliant
```

### Command-Line Arguments

**Required:**
- `--pgn PATH` - Path to PGN file to analyze
- `--stockfish PATH` - Path to Stockfish binary
- `--output PATH` - Output JSON file path

**Engine Configuration:**
- `--depth N` - Search depth in plies (default: 20)
- `--multipv N` - Number of principal variations (default: 2)
- `--threads N` - Number of CPU threads (default: 1)
- `--hash N` - Hash table size in MB (default: 128)

**Classification Options:**
- `--no-theory` - Disable THEORY classification
- `--no-critical` - Disable CRITICAL classification
- `--no-brilliant` - Disable BRILLIANT classification (faster)

**Other:**
- `--openings PATH` - Path to openings.json (default: openings.json)

## Output Format

The analysis generates a JSON file with the following structure:

```json
{
  "game_info": {
    "white": "Player1",
    "black": "Player2",
    "result": "1-0",
    "date": "2024.01.01",
    "event": "Tournament Name",
    "site": "Location"
  },
  "moves": [
    {
      "move_number": 1,
      "half_move": 1,
      "color": "white",
      "san": "e4",
      "uci": "e2e4",
      "fen_after": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
      "classification": "theory",
      "accuracy": 100.0,
      "opening": "King's Pawn Opening",
      "evaluation": {
        "type": "centipawn",
        "value": 45
      },
      "best_move": "e4"
    }
  ],
  "statistics": {
    "white": {
      "brilliant": 0,
      "critical": 1,
      "best": 8,
      "excellent": 5,
      "okay": 3,
      "inaccuracy": 2,
      "mistake": 1,
      "blunder": 0,
      "average_accuracy": 87.5
    },
    "black": {
      "brilliant": 0,
      "critical": 0,
      "best": 6,
      "excellent": 4,
      "okay": 4,
      "inaccuracy": 3,
      "mistake": 2,
      "blunder": 1,
      "average_accuracy": 82.3
    }
  }
}
```

## Architecture

The system follows a modular architecture:

```
move-classifier/
├── src/
│   ├── core/              # Domain models and constants
│   ├── engine/            # Stockfish UCI integration
│   ├── parser/            # PGN parsing
│   ├── classification/    # Classification algorithms
│   ├── analysis/          # Supporting analysis
│   ├── utils/             # Utilities
│   └── output/            # Report generation
├── architecture/          # Detailed documentation
├── openings.json          # Opening book database
└── main.py               # CLI entry point
```

### Classification Algorithm

The system uses a **waterfall priority system**:

1. **FORCED** - Only legal move available
2. **THEORY** - Position found in opening book
3. **CHECKMATE** - Delivers checkmate (→ BEST)
4. **Point Loss** - Calculate expected point loss
   - BEST (< 1% loss)
   - EXCELLENT (1-4.5%)
   - OKAY (4.5-8%)
   - INACCURACY (8-12%)
   - MISTAKE (12-22%)
   - BLUNDER (≥ 22%)
5. **CRITICAL** - Refines BEST when second-best loses ≥ 10%
6. **BRILLIANT** - Refines BEST+ for spectacular sacrifices

### Key Formulas

**Expected Points (Win Probability):**
```
EP = 1 / (1 + e^(-0.0035 × centipawns))
```

**Move Accuracy:**
```
Accuracy = 103.16 × e^(-4 × pointLoss) - 3.17
```

## Performance

- **Analysis Speed**: ~2-5 seconds per position with Stockfish
- **Typical Game**: 40-50 moves ≈ 2-4 minutes total
- **BRILLIANT Detection**: Most expensive (optional, can be disabled)

### Optimization Tips

1. **Reduce depth** for faster analysis: `--depth 15`
2. **Disable BRILLIANT** for speed: `--no-brilliant`
3. **Increase threads** on multi-core systems: `--threads 4`
4. **Increase hash** for deeper searches: `--hash 512`

## Examples

### Example 1: Quick Analysis

```bash
python main.py \
  --pgn games/kasparov-topalov.pgn \
  --stockfish stockfish \
  --output kasparov-topalov-analysis.json \
  --depth 18 \
  --no-brilliant
```

### Example 2: Deep Analysis

```bash
python main.py \
  --pgn games/immortal-game.pgn \
  --stockfish /usr/local/bin/stockfish \
  --output immortal-game-analysis.json \
  --depth 30 \
  --multipv 3 \
  --threads 8 \
  --hash 2048
```

## Documentation

Detailed architecture documentation is available in the `architecture/` directory:

- **[README.md](architecture/README.md)** - Architecture overview
- **[01-core-concepts.md](architecture/01-core-concepts.md)** - Chess notation and evaluations
- **[02-classification-overview.md](architecture/02-classification-overview.md)** - Classification system
- **[03-basic-classifications.md](architecture/03-basic-classifications.md)** - FORCED, THEORY, CHECKMATE
- **[04-point-loss-classification.md](architecture/04-point-loss-classification.md)** - Core algorithm
- **[05-advanced-classifications.md](architecture/05-advanced-classifications.md)** - CRITICAL, BRILLIANT
- **[06-attack-defense.md](architecture/06-attack-defense.md)** - Tactical analysis
- And more...

## Troubleshooting

### Stockfish Not Found

```
Error: Stockfish binary not found: /path/to/stockfish
```

**Solution**: Verify the Stockfish path is correct:
```bash
which stockfish  # On macOS/Linux
```

### Analysis Too Slow

**Solutions**:
- Reduce depth: `--depth 15`
- Disable BRILLIANT: `--no-brilliant`
- Use fewer PVs: `--multipv 1` (disables CRITICAL)

### Memory Issues

**Solution**: Reduce hash size:
```bash
--hash 64  # Use smaller hash table
```

## License

This project implements the move classification system as documented in the architecture specifications.

## Credits

- **Chess Engine**: Stockfish (GPLv3)
- **Chess Library**: python-chess
- **Classification Algorithm**: Based on Wintrchess architecture

## Contributing

Contributions are welcome! Areas for improvement:

- Additional output formats (HTML, PGN with annotations)
- GUI interface
- Batch analysis of multiple games
- Database integration
- Alternative engine support

## Version

**Version**: 1.0.0
**Last Updated**: 2024


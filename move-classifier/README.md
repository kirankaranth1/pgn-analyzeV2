# Chess Move Classifier

A comprehensive Python system for analyzing and classifying chess moves based on engine evaluation and tactical patterns.

## Overview

This system implements a 5-stage preprocessing pipeline that transforms raw game data (PGN) into classification-ready data structures, then applies sophisticated classification rules to evaluate move quality.

### Pipeline Stages

1. **Parse Game** - Convert PGN string into state tree
2. **Engine Analysis** - Add engine evaluations (cloud or local)
3. **Build Node Chain** - Linearize tree for processing
4. **Extract Nodes** - Create simplified structures
5. **Calculate Derived Values** - Compute metrics (accuracy, point loss, etc.)

### Classifications

The system classifies moves into the following categories:

**Basic:**
- CHECKMATE - Delivers checkmate
- FORCED - Only legal move
- BOOK - Opening theory move

**Point Loss:**
- BEST - Optimal move (< 1% win probability loss)
- EXCELLENT - Very strong (1-4.5% loss)
- GOOD - Solid (4.5-10% loss)
- INACCURACY - Suboptimal (10-20% loss)
- MISTAKE - Significant error (20-30% loss)
- BLUNDER - Major error (> 30% loss)
- CRITICAL - Wrong choice between two similar moves

**Advanced:**
- BRILLIANT - Sacrificial best move
- GREAT_FIND - Only move preventing significant loss

**Tactical:**
- ATTACKING_MOVE - Aggressive play
- DEFENSIVE_MOVE - Defensive response

## Project Structure

```
move-classifier/
├── src/
│   ├── __init__.py
│   ├── constants.py           # System constants
│   ├── config.py              # Configuration settings
│   │
│   ├── models/                # Data structures
│   │   ├── __init__.py
│   │   ├── enums.py          # Enumerations
│   │   ├── state_tree.py     # State tree structures
│   │   ├── extracted_nodes.py # Extracted node types
│   │   └── game_analysis.py  # Analysis results
│   │
│   ├── preprocessing/         # 5-stage pipeline
│   │   ├── __init__.py
│   │   ├── parser.py         # Stage 1: Parse PGN
│   │   ├── engine_analyzer.py # Stage 2: Engine analysis
│   │   ├── node_chain_builder.py # Stage 3: Build chain
│   │   ├── node_extractor.py # Stage 4: Extract nodes
│   │   └── calculator.py     # Stage 5: Calculate metrics
│   │
│   ├── engine/               # Engine interfaces
│   │   ├── __init__.py
│   │   ├── uci_engine.py    # Local UCI engine
│   │   └── cloud_evaluator.py # Cloud API
│   │
│   ├── classification/       # Classification system
│   │   ├── __init__.py
│   │   ├── classifier.py    # Main classifier
│   │   ├── basic_classifier.py # Basic rules
│   │   ├── point_loss_classifier.py # Core evaluation
│   │   ├── advanced_classifier.py # Advanced rules
│   │   ├── attack_defense_classifier.py # Attack/defense
│   │   └── tactical_analyzer.py # Tactical patterns
│   │
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── chess_utils.py  # Chess helpers
│       ├── evaluation_utils.py # Evaluation calculations
│       └── notation_converter.py # Notation conversion
│
├── docs/                    # Documentation
│   └── architecture/        # Architecture docs
│
├── requirements.txt         # Dependencies
├── setup.py                # Package setup
└── README.md               # This file
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Dependencies

- **chess** - Chess library for move parsing and board manipulation
- **requests** - HTTP client for cloud evaluation API

## Documentation

Comprehensive architecture documentation is available in `docs/architecture/`:

- `00-preprocessing-pipeline.md` - Complete preprocessing pipeline
- `01-core-concepts.md` - Fundamental concepts and terminology
- `02-classification-overview.md` - Classification system overview
- And more...

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
```

## License

MIT License

## Contributing

Contributions are welcome! Please read the architecture documentation before contributing.


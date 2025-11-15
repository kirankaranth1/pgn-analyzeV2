# Integration Tests

This directory contains comprehensive integration tests for the chess move classifier preprocessing pipeline.

## Overview

The integration tests verify the end-to-end functionality of each stage of the preprocessing pipeline, as well as the complete pipeline integration. These tests use real chess games and actual engine evaluations (both cloud and local) to ensure the system works correctly in production scenarios.

## Test Files

### `test_preprocessing_pipeline.py`

Tests each of the 5 stages of the preprocessing pipeline:

#### Stage 1: PGN Parser
- **test_parse_simple_game**: Parses a basic 4-move game
- **test_parse_with_checkmate**: Handles checkmate correctly
- **test_parse_with_custom_starting_position**: Supports custom FEN positions
- **test_parse_invalid_pgn**: Gracefully handles invalid PGN
- **test_parse_creates_proper_tree_structure**: Verifies parent-child relationships

#### Stage 2: Engine Analysis
- **test_analyze_with_cloud_evaluation**: Tests Lichess cloud API integration
- **test_analyze_with_local_engine**: Tests local Stockfish UCI engine
- **test_get_top_engine_line**: Extracts best engine line correctly

#### Stage 3: Node Chain Builder
- **test_get_mainline_chain**: Extracts mainline nodes
- **test_node_chain_preserves_order**: Maintains move order
- **test_empty_tree_returns_root_only**: Handles empty games

#### Stage 4: Node Extraction
- **test_extract_previous_node**: Extracts previous position data
- **test_extract_current_node**: Extracts current position data
- **test_extract_fails_without_engine_lines**: Returns None without analysis
- **test_extract_current_fails_without_parent**: Returns None for root

#### Stage 5: Calculator
- **test_calculate_move_metrics**: Computes point loss and accuracy
- **test_expected_points_calculation**: Converts eval to win probability
- **test_subjective_evaluation**: Flips eval for player perspective

#### Full Pipeline Integration
- **test_full_pipeline_with_cloud**: Complete pipeline with cloud eval
- **test_full_pipeline_with_checkmate**: Handles checkmate games
- **test_pipeline_with_custom_config**: Supports custom configuration
- **test_pipeline_preserves_game_structure**: Maintains tree structure

#### Error Handling
- **test_invalid_pgn_raises_error**: Handles invalid PGN gracefully
- **test_empty_pgn_handled**: Handles empty PGN
- **test_extraction_without_engine_returns_none**: Returns None without analysis

### `test_engine_integration.py`

Tests engine component integration:

#### Cloud Evaluator
- **test_get_cloud_evaluation_starting_position**: Queries Lichess API for starting position
- **test_cloud_evaluation_after_e4**: Queries for position after 1. e4
- **test_cloud_evaluation_returns_multiple_lines**: Tests MultiPV functionality
- **test_convert_uci_moves_to_san**: Converts UCI moves to SAN notation
- **test_convert_handles_lichess_castling**: Handles Lichess castling format

#### UCI Engine
- **test_uci_engine_initialization**: Initializes Stockfish
- **test_uci_engine_evaluate_starting_position**: Evaluates starting position
- **test_uci_engine_multipv**: Tests MultiPV with local engine
- **test_uci_engine_normalized_evaluation**: Verifies White-perspective normalization
- **test_uci_engine_handles_mate**: Detects mate-in-N positions

#### Engine Analyzer Integration
- **test_analyzer_tries_cloud_first**: Prioritizes cloud evaluation
- **test_analyzer_fallback_to_local**: Falls back to local engine

## Running Tests

### Run all integration tests
```bash
pytest tests/integration/ -v
```

### Run only fast tests (no network, no engine)
```bash
pytest tests/integration/ -m "not slow and not network and not engine"
```

### Run only network tests (cloud API)
```bash
pytest tests/integration/ -m network
```

### Run only engine tests (Stockfish)
```bash
pytest tests/integration/ -m engine
```

### Run specific test file
```bash
pytest tests/integration/test_preprocessing_pipeline.py -v
pytest tests/integration/test_engine_integration.py -v
```

### Run with coverage
```bash
pytest tests/integration/ --cov=src --cov-report=html --cov-report=term
```

## Test Markers

Integration tests use the following pytest markers:

- **@pytest.mark.integration**: All integration tests
- **@pytest.mark.slow**: Tests that take longer (engine analysis)
- **@pytest.mark.network**: Tests requiring internet (Lichess API)
- **@pytest.mark.engine**: Tests requiring Stockfish installation

## Dependencies

### Required
- `python-chess`: Chess library for PGN parsing and board representation
- `pytest`: Testing framework
- `pytest-cov`: Code coverage plugin

### Optional (for full test suite)
- **Internet connection**: For cloud evaluation tests
- **Stockfish 17**: For local engine tests (install separately)

## Test Data

Tests use simple PGN strings defined at the top of each test file:

- `SIMPLE_GAME`: "1. e4 e5 2. Nf3 Nc6" - Basic 4-move game
- `SCHOLARS_MATE`: "1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7#" - Checkmate game
- `WITH_VARIATIONS`: "1. e4 e5 (1... c5) 2. Nf3" - Game with variations

## Code Coverage

Current integration test coverage: **90%**

Coverage by module:
- `src/engine/cloud_evaluator.py`: 92%
- `src/engine/uci_engine.py`: 88%
- `src/preprocessing/engine_analyzer.py`: 94%
- `src/preprocessing/node_extractor.py`: 87%
- `src/preprocessing/parser.py`: 88%
- `src/utils/evaluation_utils.py`: 93%

## Known Limitations

1. **Cloud API Rate Limiting**: Lichess API has rate limits. If tests fail due to rate limiting, wait a few seconds and retry.

2. **Stockfish Installation**: Engine tests require Stockfish 17 to be installed and accessible in PATH. Tests will be skipped if Stockfish is not found.

3. **PGN Parsing Tolerance**: The `python-chess` library is quite tolerant of invalid PGN, so some "invalid PGN" tests verify graceful handling rather than strict rejection.

4. **Network Dependency**: Cloud evaluation tests require a stable internet connection. They will skip if the network is unavailable.

## Best Practices

1. **Run fast tests first**: Use `-m "not slow and not network and not engine"` for quick feedback during development.

2. **Run full suite before commit**: Run all tests with `pytest tests/integration/` before committing changes.

3. **Check coverage**: Aim to maintain or improve code coverage with each change.

4. **Handle skipped tests**: Tests that require Stockfish or network will skip gracefully. This is expected behavior.

## Future Enhancements

Future integration tests could include:

- **Performance tests**: Measure pipeline execution time
- **Large game tests**: Test with 100+ move games
- **Variation handling**: More extensive tests of PGN variations
- **Classification integration**: End-to-end tests with full classification
- **Concurrent processing**: Tests for parallel game analysis
- **Error recovery**: Tests for handling engine crashes or timeouts


# Test Documentation

This directory contains all tests for the chess-move-classifier project.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests for individual components
│   ├── test_project_structure.py  # Verify project setup
│   └── (future unit tests)
└── integration/             # Integration tests for end-to-end workflows
    └── (future integration tests)
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run only unit tests
```bash
pytest tests/unit/
```

### Run only integration tests
```bash
pytest tests/integration/
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### Run a specific test file
```bash
pytest tests/unit/test_project_structure.py
```

### Run a specific test class
```bash
pytest tests/unit/test_project_structure.py::TestModelsModule
```

### Run a specific test
```bash
pytest tests/unit/test_project_structure.py::TestModelsModule::test_enums_import
```

### Run with verbose output
```bash
pytest -v
```

### Run with print statements visible
```bash
pytest -s
```

## Test Categories

### Unit Tests (`tests/unit/`)

Unit tests verify individual components in isolation:

- **test_project_structure.py**: Verifies project setup
  - All modules can be imported
  - Constants are defined correctly
  - Configuration classes work
  - Data structures can be instantiated
  - Files and directories exist

Future unit tests will include:
- `test_models.py`: Data structure tests
- `test_parser.py`: PGN parsing tests
- `test_engine_analyzer.py`: Engine analysis tests
- `test_node_extractor.py`: Node extraction tests
- `test_calculator.py`: Calculation tests
- `test_classifiers.py`: Classification logic tests
- `test_utils.py`: Utility function tests

### Integration Tests (`tests/integration/`)

Integration tests verify end-to-end workflows:

Future integration tests will include:
- `test_preprocessing_pipeline.py`: Complete preprocessing pipeline
- `test_engine_integration.py`: Engine communication tests
- `test_game_analysis.py`: Full game analysis workflows
- `test_classification_workflow.py`: Complete classification process

## Test Conventions

### Naming
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Organization
- Group related tests in classes
- Use descriptive test names
- One assertion per test when possible
- Use fixtures for shared setup

### Assertions
```python
# Good
assert result == expected_value

# With custom message
assert result == expected_value, "Result should match expected value"

# Using pytest helpers
pytest.fail("Explicit failure message")
```

### Fixtures
Define shared fixtures in `conftest.py`:
```python
@pytest.fixture
def sample_board_state():
    return BoardState(fen=STARTING_FEN)
```

## Coverage Goals

- **Unit tests**: Aim for >90% code coverage
- **Integration tests**: Cover all main workflows
- **Critical paths**: 100% coverage for classification logic and calculations

## Continuous Integration

Tests should be run automatically on:
- Pull requests
- Commits to main branch
- Before releases

## Writing New Tests

When adding new functionality:

1. Write unit tests for the component
2. Add integration tests if it's part of a workflow
3. Ensure tests are independent (can run in any order)
4. Use meaningful test names that describe what's being tested
5. Include both positive and negative test cases

### Example Unit Test
```python
def test_get_expected_points_equal_position():
    """Test expected points for equal position (0 cp = 50%)."""
    from src.utils.evaluation_utils import get_expected_points
    from src.models.state_tree import Evaluation
    
    evaluation = Evaluation(type="centipawn", value=0.0)
    result = get_expected_points(evaluation)
    
    assert result == 0.5, "Equal position should give 50% win probability"
```

### Example Integration Test
```python
def test_complete_preprocessing_pipeline():
    """Test full pipeline from PGN to extracted nodes."""
    pgn = "1. e4 e5 2. Nf3 Nc6"
    
    # Parse
    state_tree = parse_pgn(pgn)
    
    # Analyze
    analyze_state_tree(state_tree, config)
    
    # Extract
    nodes = extract_nodes(state_tree)
    
    # Verify
    assert len(nodes) > 0
    assert all(node.evaluation is not None for node in nodes)
```


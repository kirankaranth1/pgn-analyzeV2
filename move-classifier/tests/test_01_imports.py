"""Test 1: Basic imports - verify all modules can be imported."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_core_imports():
    """Test that core modules can be imported."""
    from src.core import types, evaluation, move, engine_line, state_tree, constants
    assert types is not None
    assert evaluation is not None
    assert move is not None
    assert engine_line is not None
    assert state_tree is not None
    assert constants is not None


def test_classification_imports():
    """Test that classification modules can be imported."""
    from src.classification import (
        classifier, node_extractor, forced, theory,
        checkmate, point_loss, critical, brilliant
    )
    assert classifier is not None
    assert node_extractor is not None
    assert forced is not None
    assert theory is not None
    assert checkmate is not None
    assert point_loss is not None
    assert critical is not None
    assert brilliant is not None


def test_analysis_imports():
    """Test that analysis modules can be imported."""
    from src.analysis import (
        expected_points, attackers, defenders,
        piece_safety, danger_levels, trapped_pieces, material
    )
    assert expected_points is not None
    assert attackers is not None
    assert defenders is not None
    assert piece_safety is not None
    assert danger_levels is not None
    assert trapped_pieces is not None
    assert material is not None


def test_engine_imports():
    """Test that engine modules can be imported."""
    from src.engine import engine_config, stockfish_engine
    assert engine_config is not None
    assert stockfish_engine is not None


def test_parser_imports():
    """Test that parser modules can be imported."""
    from src.parser import pgn_parser, state_tree_builder
    assert pgn_parser is not None
    assert state_tree_builder is not None


def test_utils_imports():
    """Test that utility modules can be imported."""
    from src.utils import opening_book, fen_utils, chess_utils
    assert opening_book is not None
    assert fen_utils is not None
    assert chess_utils is not None


def test_output_imports():
    """Test that output modules can be imported."""
    from src.output import json_reporter
    assert json_reporter is not None


def test_main_analyzer_import():
    """Test that main analyzer can be imported."""
    from src import analyzer
    assert analyzer is not None


if __name__ == "__main__":
    print("Running import tests...")
    test_core_imports()
    print("✓ Core imports successful")
    test_classification_imports()
    print("✓ Classification imports successful")
    test_analysis_imports()
    print("✓ Analysis imports successful")
    test_engine_imports()
    print("✓ Engine imports successful")
    test_parser_imports()
    print("✓ Parser imports successful")
    test_utils_imports()
    print("✓ Utils imports successful")
    test_output_imports()
    print("✓ Output imports successful")
    test_main_analyzer_import()
    print("✓ Main analyzer import successful")
    print("\n✅ All import tests passed!")


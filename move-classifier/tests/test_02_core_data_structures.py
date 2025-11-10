"""Test 2: Core data structures - verify types, evaluations, moves work correctly."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.types import Classification, PieceColor, CLASSIFICATION_VALUES
from src.core.evaluation import Evaluation
from src.core.move import Move
from src.core.engine_line import EngineLine


def test_classification_enum():
    """Test Classification enum values."""
    assert Classification.BRILLIANT.value == "brilliant"
    assert Classification.BEST.value == "best"
    assert Classification.BLUNDER.value == "blunder"
    assert Classification.THEORY.value == "theory"
    assert Classification.FORCED.value == "forced"
    print("✓ Classification enum works")


def test_classification_values():
    """Test classification value ordering."""
    assert CLASSIFICATION_VALUES[Classification.BLUNDER] == 0
    assert CLASSIFICATION_VALUES[Classification.BEST] == 5
    assert CLASSIFICATION_VALUES[Classification.BRILLIANT] == 5
    assert CLASSIFICATION_VALUES[Classification.FORCED] == 5
    assert CLASSIFICATION_VALUES[Classification.BEST] > CLASSIFICATION_VALUES[Classification.OKAY]
    print("✓ Classification values correct")


def test_piece_color_enum():
    """Test PieceColor enum."""
    assert PieceColor.WHITE.value == "white"
    assert PieceColor.BLACK.value == "black"
    print("✓ PieceColor enum works")


def test_evaluation_centipawn():
    """Test centipawn evaluation."""
    eval1 = Evaluation(type="centipawn", value=100)
    assert eval1.type == "centipawn"
    assert eval1.value == 100
    assert "+1.00" in str(eval1)
    
    eval2 = Evaluation(type="centipawn", value=-250)
    assert eval2.value == -250
    assert "-2.50" in str(eval2)
    print("✓ Centipawn evaluation works")


def test_evaluation_mate():
    """Test mate evaluation."""
    eval1 = Evaluation(type="mate", value=3)
    assert eval1.type == "mate"
    assert eval1.value == 3
    assert "M+3" in str(eval1)
    
    eval2 = Evaluation(type="mate", value=-5)
    assert eval2.value == -5
    assert "M-5" in str(eval2)
    print("✓ Mate evaluation works")


def test_evaluation_serialization():
    """Test evaluation to/from dict."""
    eval1 = Evaluation(type="centipawn", value=150)
    dict1 = eval1.to_dict()
    assert dict1["type"] == "centipawn"
    assert dict1["value"] == 150
    
    eval2 = Evaluation.from_dict(dict1)
    assert eval2.type == eval1.type
    assert eval2.value == eval1.value
    print("✓ Evaluation serialization works")


def test_move_creation():
    """Test Move object creation."""
    move = Move(
        san="Nf3",
        uci="g1f3",
        from_square="g1",
        to_square="f3",
        piece="n",
        color=PieceColor.WHITE,
        captured=None,
        promotion=None
    )
    assert move.san == "Nf3"
    assert move.uci == "g1f3"
    assert move.from_square == "g1"
    assert move.to_square == "f3"
    assert move.piece == "n"
    assert move.color == PieceColor.WHITE
    print("✓ Move creation works")


def test_move_capture():
    """Test capture detection."""
    move1 = Move(
        san="Bxc5",
        uci="f1c5",
        from_square="f1",
        to_square="c5",
        piece="b",
        color=PieceColor.WHITE,
        captured="p"
    )
    assert move1.is_capture()
    
    move2 = Move(
        san="Nf3",
        uci="g1f3",
        from_square="g1",
        to_square="f3",
        piece="n",
        color=PieceColor.WHITE
    )
    assert not move2.is_capture()
    print("✓ Capture detection works")


def test_move_promotion():
    """Test promotion detection."""
    move1 = Move(
        san="e8=Q",
        uci="e7e8q",
        from_square="e7",
        to_square="e8",
        piece="p",
        color=PieceColor.WHITE,
        promotion="q"
    )
    assert move1.is_promotion()
    
    move2 = Move(
        san="e4",
        uci="e2e4",
        from_square="e2",
        to_square="e4",
        piece="p",
        color=PieceColor.WHITE
    )
    assert not move2.is_promotion()
    print("✓ Promotion detection works")


def test_move_castling():
    """Test castling detection."""
    move1 = Move(
        san="O-O",
        uci="e1g1",
        from_square="e1",
        to_square="g1",
        piece="k",
        color=PieceColor.WHITE
    )
    assert move1.is_castling()
    
    move2 = Move(
        san="Ke2",
        uci="e1e2",
        from_square="e1",
        to_square="e2",
        piece="k",
        color=PieceColor.WHITE
    )
    assert not move2.is_castling()
    print("✓ Castling detection works")


def test_engine_line():
    """Test EngineLine creation."""
    eval1 = Evaluation(type="centipawn", value=45)
    move1 = Move(
        san="Nf3",
        uci="g1f3",
        from_square="g1",
        to_square="f3",
        piece="n",
        color=PieceColor.WHITE
    )
    
    line = EngineLine(
        evaluation=eval1,
        source="stockfish",
        depth=20,
        index=1,
        moves=[move1]
    )
    
    assert line.evaluation.value == 45
    assert line.depth == 20
    assert line.index == 1
    assert len(line.moves) == 1
    
    first_move = line.get_first_move()
    assert first_move.san == "Nf3"
    print("✓ EngineLine works")


if __name__ == "__main__":
    print("Running core data structure tests...\n")
    test_classification_enum()
    test_classification_values()
    test_piece_color_enum()
    test_evaluation_centipawn()
    test_evaluation_mate()
    test_evaluation_serialization()
    test_move_creation()
    test_move_capture()
    test_move_promotion()
    test_move_castling()
    test_engine_line()
    print("\n✅ All core data structure tests passed!")


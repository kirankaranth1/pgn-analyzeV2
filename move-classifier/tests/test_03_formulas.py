"""Test 3: Mathematical formulas - expected points, accuracy, point loss."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import math
from src.core.evaluation import Evaluation
from src.core.types import PieceColor
from src.core.constants import (
    get_expected_points,
    get_move_accuracy,
    CENTIPAWN_GRADIENT
)
from src.analysis.expected_points import (
    get_expected_points as get_ep_from_eval,
    get_subjective_evaluation,
    calculate_point_loss
)


def test_expected_points_formula():
    """Test expected points sigmoid formula."""
    # Test equal position (0 cp)
    ep_0 = get_expected_points(0, "centipawn")
    assert abs(ep_0 - 0.5) < 0.01, f"Expected ~0.5, got {ep_0}"
    
    # Test white advantage (+100 cp)
    ep_100 = get_expected_points(100, "centipawn")
    assert 0.58 < ep_100 < 0.59, f"Expected ~0.587, got {ep_100}"
    
    # Test black advantage (-100 cp)
    ep_neg100 = get_expected_points(-100, "centipawn")
    assert 0.41 < ep_neg100 < 0.42, f"Expected ~0.413, got {ep_neg100}"
    
    # Test large advantage (+500 cp)
    ep_500 = get_expected_points(500, "centipawn")
    assert 0.84 < ep_500 < 0.86, f"Expected ~0.845, got {ep_500}"
    
    print("✓ Expected points formula works")


def test_mate_expected_points():
    """Test expected points for mate scores."""
    # Winning mate
    ep_mate_plus = get_expected_points(5, "mate")
    assert ep_mate_plus == 1.0
    
    # Losing mate
    ep_mate_minus = get_expected_points(-5, "mate")
    assert ep_mate_minus == 0.0
    
    print("✓ Mate expected points work")


def test_accuracy_formula():
    """Test move accuracy formula."""
    # Perfect move (0 loss)
    acc_0 = get_move_accuracy(0.0)
    assert abs(acc_0 - 100.0) < 1.0
    
    # Small loss (1%)
    acc_1 = get_move_accuracy(0.01)
    assert 95 < acc_1 < 100
    
    # Medium loss (5%)
    acc_5 = get_move_accuracy(0.05)
    assert 80 < acc_5 < 90
    
    # Large loss (10%)
    acc_10 = get_move_accuracy(0.10)
    assert 60 < acc_10 < 75
    
    # Blunder (25%)
    acc_25 = get_move_accuracy(0.25)
    assert acc_25 < 50
    
    print("✓ Accuracy formula works")


def test_subjective_evaluation_white():
    """Test subjective evaluation for white."""
    eval_white = Evaluation(type="centipawn", value=100)
    subjective = get_subjective_evaluation(eval_white, PieceColor.WHITE)
    assert subjective.value == 100  # Same for white
    
    eval_black = Evaluation(type="centipawn", value=-100)
    subjective = get_subjective_evaluation(eval_black, PieceColor.WHITE)
    assert subjective.value == -100  # Same for white
    
    print("✓ Subjective evaluation for white works")


def test_subjective_evaluation_black():
    """Test subjective evaluation for black."""
    eval_white = Evaluation(type="centipawn", value=100)
    subjective = get_subjective_evaluation(eval_white, PieceColor.BLACK)
    assert subjective.value == -100  # Flipped for black
    
    eval_black = Evaluation(type="centipawn", value=-100)
    subjective = get_subjective_evaluation(eval_black, PieceColor.BLACK)
    assert subjective.value == 100  # Flipped for black
    
    print("✓ Subjective evaluation for black works")


def test_point_loss_calculation():
    """Test point loss calculation."""
    # Good move: position improves slightly
    eval_before = Evaluation(type="centipawn", value=0)  # Equal
    eval_after = Evaluation(type="centipawn", value=50)  # White slightly better
    
    loss = calculate_point_loss(eval_before, eval_after, PieceColor.WHITE)
    assert loss < 0.05, f"Expected small loss, got {loss}"
    
    # Bad move: position worsens
    eval_before2 = Evaluation(type="centipawn", value=100)  # White better
    eval_after2 = Evaluation(type="centipawn", value=-100)  # Black better
    
    loss2 = calculate_point_loss(eval_before2, eval_after2, PieceColor.WHITE)
    assert loss2 > 0.15, f"Expected large loss, got {loss2}"
    
    print("✓ Point loss calculation works")


def test_centipawn_gradient_constant():
    """Test that centipawn gradient is correct."""
    assert abs(CENTIPAWN_GRADIENT - 0.0035) < 0.0001
    print("✓ Centipawn gradient constant correct")


def test_expected_points_symmetry():
    """Test that expected points are symmetric around 0."""
    ep_100 = get_expected_points(100, "centipawn")
    ep_neg100 = get_expected_points(-100, "centipawn")
    
    # Should sum to 1.0 (symmetry)
    assert abs((ep_100 + ep_neg100) - 1.0) < 0.01
    
    ep_300 = get_expected_points(300, "centipawn")
    ep_neg300 = get_expected_points(-300, "centipawn")
    assert abs((ep_300 + ep_neg300) - 1.0) < 0.01
    
    print("✓ Expected points symmetry verified")


def test_sigmoid_shape():
    """Test sigmoid function has correct shape."""
    # Test monotonic increase
    ep_values = []
    for cp in range(-500, 501, 100):
        ep = get_expected_points(cp, "centipawn")
        ep_values.append(ep)
    
    # Should be strictly increasing
    for i in range(len(ep_values) - 1):
        assert ep_values[i] < ep_values[i + 1]
    
    # Center point should be 0.5
    ep_0 = get_expected_points(0, "centipawn")
    assert abs(ep_0 - 0.5) < 0.01
    
    # Asymptotes
    ep_large_pos = get_expected_points(2000, "centipawn")
    assert ep_large_pos > 0.999
    
    ep_large_neg = get_expected_points(-2000, "centipawn")
    assert ep_large_neg < 0.001
    
    print("✓ Sigmoid shape verified")


if __name__ == "__main__":
    print("Running formula tests...\n")
    test_expected_points_formula()
    test_mate_expected_points()
    test_accuracy_formula()
    test_subjective_evaluation_white()
    test_subjective_evaluation_black()
    test_point_loss_calculation()
    test_centipawn_gradient_constant()
    test_expected_points_symmetry()
    test_sigmoid_shape()
    print("\n✅ All formula tests passed!")


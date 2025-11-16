"""
Test Expected Points and Point Loss JavaScript Alignment

Verifies that the Python implementation matches the JavaScript exactly.
"""

import pytest
from src.utils.evaluation_utils import get_expected_points, get_expected_points_loss
from src.models.state_tree import Evaluation
from src.models.enums import PieceColor


def test_expected_points_centipawn():
    """Test expected points calculation for centipawn evaluations."""
    eval_positive = Evaluation(type="centipawn", value=100.0)
    eval_negative = Evaluation(type="centipawn", value=-100.0)
    eval_zero = Evaluation(type="centipawn", value=0.0)
    
    # Positive evaluation favors White
    ep_pos = get_expected_points(eval_positive)
    assert 0.5 < ep_pos < 1.0  # White winning
    
    # Negative evaluation favors Black
    ep_neg = get_expected_points(eval_negative)
    assert 0.0 < ep_neg < 0.5  # Black winning
    
    # Zero evaluation is even
    ep_zero = get_expected_points(eval_zero)
    assert abs(ep_zero - 0.5) < 0.01  # Should be close to 0.5


def test_expected_points_mate_positive():
    """Test expected points for forced mate (White winning)."""
    eval_mate = Evaluation(type="mate", value=5)
    
    ep = get_expected_points(eval_mate)
    assert ep == 1.0  # White wins


def test_expected_points_mate_negative():
    """Test expected points for forced mate (Black winning)."""
    eval_mate = Evaluation(type="mate", value=-5)
    
    ep = get_expected_points(eval_mate)
    assert ep == 0.0  # Black wins


def test_expected_points_mate_zero_white():
    """Test expected points for mate already delivered (White won)."""
    eval_mate = Evaluation(type="mate", value=0)
    
    # JavaScript: return Number(opts.moveColour == PieceColour.WHITE)
    ep_white = get_expected_points(eval_mate, move_colour=PieceColor.WHITE)
    assert ep_white == 1.0  # White won
    
    ep_black = get_expected_points(eval_mate, move_colour=PieceColor.BLACK)
    assert ep_black == 0.0  # Black lost


def test_expected_points_mate_zero_black():
    """Test expected points for mate already delivered (Black won)."""
    eval_mate = Evaluation(type="mate", value=0)
    
    # JavaScript: return Number(opts.moveColour == PieceColour.WHITE)
    ep_black = get_expected_points(eval_mate, move_colour=PieceColor.BLACK)
    assert ep_black == 0.0  # Black won (but from Black's perspective)
    
    ep_white = get_expected_points(eval_mate, move_colour=PieceColor.WHITE)
    assert ep_white == 1.0  # White won


def test_expected_points_mate_zero_no_color():
    """Test expected points for mate=0 without color (fallback)."""
    eval_mate = Evaluation(type="mate", value=0)
    
    # Without color, should return 0.5 (unknown winner)
    ep = get_expected_points(eval_mate)
    assert ep == 0.5


def test_expected_points_loss_white_loses_material():
    """Test point loss when White loses material."""
    # Before: +100cp (White slightly better)
    # After: 0cp (equal)
    prev_eval = Evaluation(type="centipawn", value=100.0)
    curr_eval = Evaluation(type="centipawn", value=0.0)
    
    # White's perspective: lost advantage
    loss = get_expected_points_loss(prev_eval, curr_eval, PieceColor.WHITE)
    assert loss > 0.0  # White lost advantage


def test_expected_points_loss_black_loses_material():
    """Test point loss when Black loses material."""
    # Before: -100cp (Black slightly better)
    # After: 0cp (equal)
    prev_eval = Evaluation(type="centipawn", value=-100.0)
    curr_eval = Evaluation(type="centipawn", value=0.0)
    
    # Black's perspective: lost advantage
    loss = get_expected_points_loss(prev_eval, curr_eval, PieceColor.BLACK)
    assert loss > 0.0  # Black lost advantage


def test_expected_points_loss_perfect_move():
    """Test point loss for a perfect move (no loss)."""
    # Before and after same evaluation
    prev_eval = Evaluation(type="centipawn", value=50.0)
    curr_eval = Evaluation(type="centipawn", value=50.0)
    
    loss_white = get_expected_points_loss(prev_eval, curr_eval, PieceColor.WHITE)
    loss_black = get_expected_points_loss(prev_eval, curr_eval, PieceColor.BLACK)
    
    assert loss_white == 0.0
    assert loss_black == 0.0


def test_expected_points_loss_improves_position():
    """Test point loss for move that improves position (negative loss clamped to 0)."""
    # Before: 0cp
    # After: +100cp (White improved)
    prev_eval = Evaluation(type="centipawn", value=0.0)
    curr_eval = Evaluation(type="centipawn", value=100.0)
    
    # White improved, so loss should be 0 (not negative)
    loss = get_expected_points_loss(prev_eval, curr_eval, PieceColor.WHITE)
    assert loss == 0.0


def test_expected_points_loss_blunder():
    """Test point loss for a blunder."""
    # Before: +200cp (White winning)
    # After: -200cp (Black winning) - major blunder!
    prev_eval = Evaluation(type="centipawn", value=200.0)
    curr_eval = Evaluation(type="centipawn", value=-200.0)
    
    # White blundered badly
    loss = get_expected_points_loss(prev_eval, curr_eval, PieceColor.WHITE)
    assert loss > 0.3  # Significant point loss


def test_expected_points_custom_gradient():
    """Test expected points with custom centipawn gradient."""
    eval_100 = Evaluation(type="centipawn", value=100.0)
    
    # Default gradient
    ep_default = get_expected_points(eval_100)
    
    # Custom gradient (steeper)
    ep_custom = get_expected_points(eval_100, centipawn_gradient=0.005)
    
    # Steeper gradient means more advantage for same centipawn value
    assert ep_custom > ep_default


def test_javascript_alignment_formula():
    """
    Verify the exact formula matches JavaScript:
    EP = 1 / (1 + exp(-0.0035 * evaluation))
    """
    import math
    
    eval_val = 100.0
    evaluation = Evaluation(type="centipawn", value=eval_val)
    
    # Python result
    python_result = get_expected_points(evaluation)
    
    # JavaScript formula (manual calculation)
    js_result = 1.0 / (1.0 + math.exp(-0.0035 * eval_val))
    
    # Should be identical
    assert abs(python_result - js_result) < 0.0001


def test_javascript_alignment_point_loss_formula():
    """
    Verify the exact point loss formula matches JavaScript:
    max(0, (prevEP - currEP) * (moveColour == WHITE ? 1 : -1))
    """
    prev_eval = Evaluation(type="centipawn", value=100.0)
    curr_eval = Evaluation(type="centipawn", value=50.0)
    
    # Python result
    python_loss_white = get_expected_points_loss(prev_eval, curr_eval, PieceColor.WHITE)
    python_loss_black = get_expected_points_loss(prev_eval, curr_eval, PieceColor.BLACK)
    
    # Manual calculation matching JavaScript
    from src.utils.evaluation_utils import flip_piece_color
    prev_ep = get_expected_points(prev_eval, move_colour=flip_piece_color(PieceColor.WHITE))
    curr_ep = get_expected_points(curr_eval, move_colour=PieceColor.WHITE)
    js_loss_white = max(0.0, (prev_ep - curr_ep) * 1)
    
    prev_ep_black = get_expected_points(prev_eval, move_colour=flip_piece_color(PieceColor.BLACK))
    curr_ep_black = get_expected_points(curr_eval, move_colour=PieceColor.BLACK)
    js_loss_black = max(0.0, (prev_ep_black - curr_ep_black) * -1)
    
    # Should be identical
    assert abs(python_loss_white - js_loss_white) < 0.0001
    assert abs(python_loss_black - js_loss_black) < 0.0001


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


"""
Evaluation Utility Functions

Helper functions for evaluation calculations:
- Expected points conversion
- Point loss calculation
- Accuracy computation
- Subjective evaluation conversion
"""

import math
from typing import Optional

from ..models.state_tree import Evaluation
from ..models.enums import PieceColor
from ..constants import (
    CENTIPAWN_GRADIENT,
    ACCURACY_MULTIPLIER,
    ACCURACY_EXPONENT,
    ACCURACY_OFFSET
)


def get_expected_points(
    evaluation: Evaluation,
    move_colour: Optional[PieceColor] = None,
    centipawn_gradient: Optional[float] = None
) -> float:
    """
    Convert evaluation to win probability (0.0 to 1.0 scale).
    
    Matches JavaScript implementation from getExpectedPoints.
    
    Formula for centipawn: EP = 1 / (1 + e^(-0.0035 × evaluation))
    Formula for mate: 1.0 if winning, 0.0 if losing
    
    Args:
        evaluation: Position evaluation
        move_colour: Color of the moving player (used for mate=0 case)
        centipawn_gradient: Optional custom gradient (default: 0.0035)
        
    Returns:
        Expected points (win probability) from 0.0 to 1.0
    """
    gradient = centipawn_gradient or CENTIPAWN_GRADIENT
    
    if evaluation.type == "mate":
        if evaluation.value == 0:
            # Mate already delivered - winner determined by move colour
            # Return 1.0 if WHITE won, 0.0 if BLACK won
            if move_colour is not None:
                return 1.0 if move_colour == PieceColor.WHITE else 0.0
            # If no move colour specified, return 0.5 (unknown)
            return 0.5
        
        # Forced mate = certain outcome (positive = White winning, negative = Black winning)
        return 1.0 if evaluation.value > 0 else 0.0
    else:
        # Sigmoid function for centipawn evaluation
        return 1.0 / (1.0 + math.exp(-gradient * evaluation.value))


def get_subjective_evaluation(
    evaluation: Evaluation,
    player_color: PieceColor
) -> Evaluation:
    """
    Convert evaluation from White's perspective to player's perspective.
    
    Args:
        evaluation: Evaluation from White's perspective
        player_color: Color of the moving player
        
    Returns:
        Evaluation from player's perspective
    """
    multiplier = 1 if player_color == PieceColor.WHITE else -1
    
    return Evaluation(
        type=evaluation.type,
        value=evaluation.value * multiplier
    )


def get_expected_points_loss(
    previous_evaluation: Evaluation,
    current_evaluation: Evaluation,
    move_color: PieceColor
) -> float:
    """
    Calculate how much win probability was lost by playing a move.
    
    Matches JavaScript implementation from getExpectedPointsLoss.
    
    Args:
        previous_evaluation: Evaluation before the move
        current_evaluation: Evaluation after the move
        move_color: Color that played the move
        
    Returns:
        Point loss (0.0 or positive value)
    """
    # Get expected points from opponent's perspective (before move)
    prev_ep = get_expected_points(
        previous_evaluation,
        move_colour=flip_piece_color(move_color)
    )
    
    # Get expected points from player's perspective (after move)
    curr_ep = get_expected_points(
        current_evaluation,
        move_colour=move_color
    )
    
    # Calculate loss with perspective adjustment
    multiplier = 1 if move_color == PieceColor.WHITE else -1
    loss = (prev_ep - curr_ep) * multiplier
    
    return max(0.0, loss)


def get_move_accuracy(
    previous_evaluation: Evaluation,
    current_evaluation: Evaluation,
    move_color: PieceColor
) -> float:
    """
    Convert point loss to a 0-100 accuracy score.
    
    Formula: Accuracy = 103.16 × e^(-4 × pointLoss) - 3.17
    
    Args:
        previous_evaluation: Evaluation before the move
        current_evaluation: Evaluation after the move
        move_color: Color that played the move
        
    Returns:
        Accuracy score (0-100)
    """
    point_loss = get_expected_points_loss(
        previous_evaluation,
        current_evaluation,
        move_color
    )
    
    # Exponential decay formula
    accuracy = ACCURACY_MULTIPLIER * math.exp(ACCURACY_EXPONENT * point_loss) + ACCURACY_OFFSET
    
    return accuracy


def flip_piece_color(color: PieceColor) -> PieceColor:
    """
    Flip piece color.
    
    Args:
        color: Piece color to flip
        
    Returns:
        Opposite color
    """
    return PieceColor.BLACK if color == PieceColor.WHITE else PieceColor.WHITE

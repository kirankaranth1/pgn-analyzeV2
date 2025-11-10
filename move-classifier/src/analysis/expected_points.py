"""Expected points calculation from evaluations."""

from ..core.evaluation import Evaluation
from ..core.types import PieceColor
from ..core.constants import get_expected_points as calc_ep
import chess


def get_expected_points(evaluation: Evaluation) -> float:
    """Calculate expected points from evaluation.
    
    Uses sigmoid formula: 1 / (1 + e^(-0.0035 × centipawns))
    
    Args:
        evaluation: Position evaluation
        
    Returns:
        Expected points (0.0 to 1.0)
    """
    return calc_ep(evaluation.value, evaluation.type)


def get_subjective_evaluation(
    evaluation: Evaluation,
    player_color: PieceColor
) -> Evaluation:
    """Convert evaluation to player's perspective.
    
    Evaluations are always from White's perspective.
    This adjusts them to the player's perspective.
    
    Args:
        evaluation: Position evaluation (White's perspective)
        player_color: Color of the player
        
    Returns:
        Evaluation from player's perspective
    """
    if player_color == PieceColor.WHITE:
        return evaluation
    
    # Flip evaluation for Black
    return Evaluation(
        type=evaluation.type,
        value=-evaluation.value
    )


def calculate_point_loss(
    eval_before: Evaluation,
    eval_after: Evaluation,
    player_color: PieceColor
) -> float:
    """Calculate point loss from a move.
    
    Point Loss = max(0, EP(before, opponent_perspective) - EP(after, player_perspective))
    
    Args:
        eval_before: Evaluation before the move (from opponent's perspective after their move)
        eval_after: Evaluation after the move (from player's perspective after their move)
        player_color: Color of the player who made the move
        
    Returns:
        Point loss (0.0 to 1.0)
    """
    # Get expected points before (from player's perspective looking at position they're about to play in)
    # This is from the opponent's perspective after their last move
    opponent_color = PieceColor.BLACK if player_color == PieceColor.WHITE else PieceColor.WHITE
    eval_before_subjective = get_subjective_evaluation(eval_before, player_color)
    ep_before = get_expected_points(eval_before_subjective)
    
    # Get expected points after the move (from player's perspective)
    eval_after_subjective = get_subjective_evaluation(eval_after, player_color)
    ep_after = get_expected_points(eval_after_subjective)
    
    # Point loss is the decrease in expected points
    loss = max(0.0, ep_before - ep_after)
    return loss


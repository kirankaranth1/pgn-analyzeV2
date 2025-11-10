"""Point loss classification - core evaluation system."""

from ..core.types import Classification
from ..core.constants import (
    POINT_LOSS_THRESHOLDS,
    MATE_TO_CP_THRESHOLDS,
    MATE_LOSS_THRESHOLDS,
    CP_TO_MATE_THRESHOLDS,
    get_move_accuracy
)
from ..analysis.expected_points import (
    get_expected_points,
    calculate_point_loss
)
from .node_extractor import ExtractedPreviousNode, ExtractedCurrentNode


def is_top_move_played(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode
) -> bool:
    """Check if the top engine move was played.
    
    Args:
        previous: Previous node data
        current: Current node data
        
    Returns:
        True if top move was played
    """
    if not current.played_move or not previous.top_move:
        return False
    
    # Compare by SAN notation
    return previous.top_move.san == current.played_move.san


def classify_by_point_loss(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode
) -> Classification:
    """Classify move based on point loss.
    
    Handles all special cases: cp->cp, mate->mate, cp->mate, mate->cp
    
    Args:
        previous: Previous node data
        current: Current node data
        
    Returns:
        Classification based on point loss
    """
    # Check if top move was played
    if is_top_move_played(previous, current):
        return Classification.BEST
    
    eval_before = previous.subjective_evaluation
    eval_after = current.subjective_evaluation
    
    # Case 1: Centipawn -> Centipawn (standard case)
    if eval_before.type == "centipawn" and eval_after.type == "centipawn":
        return _classify_cp_to_cp(eval_before.value, eval_after.value, current.player_color)
    
    # Case 2: Mate -> Mate
    elif eval_before.type == "mate" and eval_after.type == "mate":
        return _classify_mate_to_mate(eval_before.value, eval_after.value)
    
    # Case 3: Mate -> Centipawn (lost winning mate)
    elif eval_before.type == "mate" and eval_after.type == "centipawn":
        return _classify_mate_to_cp(eval_before.value, eval_after.value)
    
    # Case 4: Centipawn -> Mate
    elif eval_before.type == "centipawn" and eval_after.type == "mate":
        return _classify_cp_to_mate(eval_before.value, eval_after.value)
    
    # Fallback
    return Classification.OKAY


def _classify_cp_to_cp(cp_before: int, cp_after: int, player_color) -> Classification:
    """Standard centipawn -> centipawn classification.
    
    Args:
        cp_before: Centipawns before (from player's perspective)
        cp_after: Centipawns after (from player's perspective)
        player_color: Player color
        
    Returns:
        Classification
    """
    # Calculate expected points
    from ..core.evaluation import Evaluation
    from ..core.types import PieceColor
    
    eval_before = Evaluation(type="centipawn", value=cp_before)
    eval_after = Evaluation(type="centipawn", value=cp_after)
    
    ep_before = get_expected_points(eval_before)
    ep_after = get_expected_points(eval_after)
    
    point_loss = max(0.0, ep_before - ep_after)
    
    # Apply thresholds
    if point_loss < POINT_LOSS_THRESHOLDS["BEST"]:
        return Classification.BEST
    elif point_loss < POINT_LOSS_THRESHOLDS["EXCELLENT"]:
        return Classification.EXCELLENT
    elif point_loss < POINT_LOSS_THRESHOLDS["OKAY"]:
        return Classification.OKAY
    elif point_loss < POINT_LOSS_THRESHOLDS["INACCURACY"]:
        return Classification.INACCURACY
    elif point_loss < POINT_LOSS_THRESHOLDS["MISTAKE"]:
        return Classification.MISTAKE
    else:
        return Classification.BLUNDER


def _classify_mate_to_mate(mate_before: int, mate_after: int) -> Classification:
    """Classify mate -> mate transition.
    
    Args:
        mate_before: Mate moves before (positive = winning)
        mate_after: Mate moves after (positive = winning)
        
    Returns:
        Classification
    """
    # Winning mate to losing mate = BLUNDER
    if mate_before > 0 and mate_after < 0:
        return Classification.BLUNDER
    
    # Still winning mate, check move loss
    if mate_before > 0 and mate_after > 0:
        move_loss = abs(mate_after) - abs(mate_before)
        
        if move_loss <= MATE_LOSS_THRESHOLDS["BEST"]:
            return Classification.BEST
        elif move_loss <= MATE_LOSS_THRESHOLDS["EXCELLENT"]:
            return Classification.EXCELLENT
        elif move_loss <= MATE_LOSS_THRESHOLDS["OKAY"]:
            return Classification.OKAY
        else:
            return Classification.INACCURACY
    
    # Losing mate to winning mate (impossible in normal play)
    if mate_before < 0 and mate_after > 0:
        return Classification.BEST
    
    # Both losing mates
    return Classification.OKAY


def _classify_mate_to_cp(mate_before: int, cp_after: int) -> Classification:
    """Classify mate -> centipawn (lost winning mate).
    
    Args:
        mate_before: Mate moves before (positive = winning)
        cp_after: Centipawns after (from player's perspective)
        
    Returns:
        Classification
    """
    # Lost winning mate
    if mate_before > 0:
        if cp_after >= MATE_TO_CP_THRESHOLDS["EXCELLENT"]:
            return Classification.EXCELLENT
        elif cp_after >= MATE_TO_CP_THRESHOLDS["OKAY"]:
            return Classification.OKAY
        elif cp_after >= MATE_TO_CP_THRESHOLDS["INACCURACY"]:
            return Classification.INACCURACY
        elif cp_after >= MATE_TO_CP_THRESHOLDS["MISTAKE"]:
            return Classification.MISTAKE
        else:
            return Classification.BLUNDER
    
    # Was losing mate anyway
    return Classification.OKAY


def _classify_cp_to_mate(cp_before: int, mate_after: int) -> Classification:
    """Classify centipawn -> mate.
    
    Args:
        cp_before: Centipawns before (from player's perspective)
        mate_after: Mate moves after (positive = winning)
        
    Returns:
        Classification
    """
    # Found winning mate
    if mate_after > 0:
        return Classification.BEST
    
    # Got mated (from perspective of player who moved, this is bad)
    # mate_after negative means opponent mates us
    if mate_after >= CP_TO_MATE_THRESHOLDS["BLUNDER"]:
        return Classification.BLUNDER
    elif mate_after >= CP_TO_MATE_THRESHOLDS["MISTAKE"]:
        return Classification.MISTAKE
    else:
        return Classification.INACCURACY


def calculate_accuracy(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode
) -> float:
    """Calculate move accuracy score.
    
    Args:
        previous: Previous node data
        current: Current node data
        
    Returns:
        Accuracy score (0-100)
    """
    point_loss = calculate_point_loss(
        previous.evaluation,
        current.evaluation,
        current.player_color
    )
    
    return get_move_accuracy(point_loss)


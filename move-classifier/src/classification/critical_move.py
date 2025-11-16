"""
Critical Move Detection

Functions to determine if a move is a critical candidate and should be
classified as critical.
"""

import chess

from ..models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from ..models.enums import PieceColor
from ..utils.evaluation_utils import flip_piece_color


def is_move_critical_candidate(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode
) -> bool:
    """
    Returns whether a move is critical to maintaining an advantage.
    
    Moves that are easy to find or forced cannot be critical.
    Also serves as a preliminary check for critical and brilliant moves.
    
    Args:
        previous: Node before the move
        current: Node after the move
        
    Returns:
        True if move is a candidate for critical classification
    """
    # Still completely winning even if this move hadn't been found
    second_subjective_eval = previous.second_subjective_evaluation
    
    if second_subjective_eval:
        if (
            second_subjective_eval.type == "centipawn"
            and second_subjective_eval.value >= 700
        ):
            return False
    else:
        if (
            current.evaluation.type == "centipawn"
            and current.subjective_evaluation.value >= 700
        ):
            return False
    
    # Moves in losing positions cannot be critical
    if current.subjective_evaluation.value < 0:
        return False
    
    # Disallow queen promotions as critical moves
    if current.played_move and current.played_move.promotion == chess.QUEEN:
        return False
    
    # Disallow moves that must be played anyway to escape check
    if previous.board.is_check():
        return False
    
    return True


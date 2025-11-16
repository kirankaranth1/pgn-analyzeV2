"""
Point Loss Classification

Classifies moves based on evaluation drop (point loss) or mate transitions.
Matches JavaScript implementation from classification/pointLoss.ts
"""

import chess
from ..models.enums import Classification, PieceColor
from ..models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from ..utils.evaluation_utils import get_expected_points_loss


def point_loss_classify(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode
) -> Classification:
    """
    Classify move using two evaluations and point loss calculation.
    
    Matches JavaScript pointLossClassify() function exactly.
    
    Args:
        previous: Position before the move
        current: Position after the move
        
    Returns:
        Classification based on point loss or mate transitions
    """
    # Determine move color (whose turn it was in previous position)
    move_color_is_white = previous.board.turn == chess.WHITE
    
    # Calculate previous subjective value (from mover's perspective)
    previousSubjectiveValue = previous.evaluation.value * (
        1 if move_color_is_white else -1
    )
    
    # Get current subjective evaluation value
    subjectiveValue = current.subjective_evaluation.value
    
    # Case 1: Mate to mate evaluations
    if (
        previous.evaluation.type == "mate"
        and current.evaluation.type == "mate"
    ):
        # Winning mate to losing mate
        if previousSubjectiveValue > 0 and subjectiveValue < 0:
            return (
                Classification.MISTAKE if subjectiveValue < -3
                else Classification.BLUNDER
            )
        
        # For the losing side, making a move that keeps the mate the same
        # is best. Only the winning side expects a mate loss of -1.
        mateLoss = (
            (current.evaluation.value - previous.evaluation.value)
            * (1 if move_color_is_white else -1)
        )
        
        if mateLoss < 0 or (mateLoss == 0 and subjectiveValue < 0):
            return Classification.BEST
        elif mateLoss < 2:
            return Classification.EXCELLENT
        elif mateLoss < 7:
            return Classification.GOOD
        else:
            return Classification.INACCURACY
    
    # Case 2: Mate to centipawn evaluations
    if (
        previous.evaluation.type == "mate"
        and current.evaluation.type == "centipawn"
    ):
        if subjectiveValue >= 800:
            return Classification.EXCELLENT
        elif subjectiveValue >= 400:
            return Classification.GOOD
        elif subjectiveValue >= 200:
            return Classification.INACCURACY
        elif subjectiveValue >= 0:
            return Classification.MISTAKE
        else:
            return Classification.BLUNDER
    
    # Case 3: Centipawn to mate evaluations
    if (
        previous.evaluation.type == "centipawn"
        and current.evaluation.type == "mate"
    ):
        if subjectiveValue > 0:
            return Classification.BEST
        elif subjectiveValue >= -2:
            return Classification.BLUNDER
        elif subjectiveValue >= -5:
            return Classification.MISTAKE
        else:
            return Classification.INACCURACY
    
    # Case 4: Centipawn to centipawn evaluations
    # Convert chess.WHITE/BLACK to PieceColor enum
    move_color = PieceColor.WHITE if move_color_is_white else PieceColor.BLACK
    
    pointLoss = get_expected_points_loss(
        previous.evaluation,
        current.evaluation,
        move_color
    )
    
    if pointLoss < 0.01:
        return Classification.BEST
    elif pointLoss < 0.045:
        return Classification.EXCELLENT
    elif pointLoss < 0.08:
        return Classification.GOOD
    elif pointLoss < 0.12:
        return Classification.INACCURACY
    elif pointLoss < 0.22:
        return Classification.MISTAKE
    else:
        return Classification.BLUNDER

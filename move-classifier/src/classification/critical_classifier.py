"""
Critical Classification

Determines if a move should be classified as CRITICAL.
"""

import chess

from ..models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from ..models.enums import PieceColor
from ..utils.evaluation_utils import get_expected_points_loss, flip_piece_color
from ..utils.piece_safety import is_piece_safe
from ..utils.chess_utils import get_capture_square
from ..models.chess_types import BoardPiece
from .critical_move import is_move_critical_candidate


def consider_critical_classification(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode
) -> bool:
    """
    Determine if a move should be classified as CRITICAL.
    
    A critical move is one where:
    - The top move was played
    - The position is winning but not completely winning
    - The second-best move would lose significant advantage (≥10% point loss)
    - Not capturing free material
    - Not already mating
    
    Args:
        previous: Node before the move
        current: Node after the move
        
    Returns:
        True if move should be classified as CRITICAL
    """
    if not is_move_critical_candidate(previous, current):
        return False
    
    # It is not critical to find moves where you have mate
    if (
        current.subjective_evaluation.type == "mate"
        and current.subjective_evaluation.value > 0
    ):
        return False
    
    # A critical move cannot be a capture of free material
    if current.played_move:
        # Get the move from chess.Move
        move = chess.Move(
            current.played_move.from_square,
            current.played_move.to_square,
            promotion=current.played_move.promotion
        )
        
        # Check if it's a capture
        captured_piece = previous.board.piece_at(get_capture_square(move))
        if captured_piece:
            # Check if the captured piece was safe (not free material)
            captured_piece_obj = BoardPiece(
                color=captured_piece.color,
                square=get_capture_square(move),
                type=captured_piece.piece_type
            )
            
            captured_piece_safety = is_piece_safe(
                previous.board,
                captured_piece_obj
            )
            
            # If piece was not safe (free material), not critical
            if not captured_piece_safety:
                return False
    
    # Must have a second-best line
    if not previous.second_top_line or not previous.second_top_line.evaluation:
        return False
    
    # Calculate point loss for second-best move
    # The player's color is the one who made the move
    player_color = PieceColor.WHITE if previous.board.turn == chess.WHITE else PieceColor.BLACK
    
    second_top_move_point_loss = get_expected_points_loss(
        previous.evaluation,
        previous.second_top_line.evaluation,
        player_color
    )
    
    # 10% loss = middle between inaccuracy and mistake
    return second_top_move_point_loss >= 0.1


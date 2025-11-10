"""CRITICAL classification - essential only moves."""

import chess
from typing import Optional
from ..core.types import Classification, PieceColor
from ..core.constants import CRITICAL_THRESHOLD, COMPLETELY_WINNING
from ..analysis.expected_points import get_expected_points, calculate_point_loss
from .node_extractor import ExtractedPreviousNode, ExtractedCurrentNode
from .point_loss import is_top_move_played


def is_critical_candidate(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode
) -> bool:
    """Check if move is a candidate for CRITICAL.
    
    Must pass basic filters before expensive checks.
    
    Args:
        previous: Previous node data
        current: Current node data
        
    Returns:
        True if move could be CRITICAL
    """
    # Must be top move
    if not is_top_move_played(previous, current):
        return False
    
    # Must not already be mate
    if current.subjective_evaluation.type == "mate" and current.subjective_evaluation.value > 0:
        return False
    
    # Must not be completely winning already
    if (current.subjective_evaluation.type == "centipawn" and 
        current.subjective_evaluation.value >= COMPLETELY_WINNING):
        return False
    
    # Must not be lost position
    if (current.subjective_evaluation.type == "centipawn" and 
        current.subjective_evaluation.value < 0):
        return False
    
    return True


def is_free_capture(board: chess.Board, move) -> bool:
    """Check if move is capturing free material.
    
    Args:
        board: Chess board (before move)
        move: Move to check
        
    Returns:
        True if capturing undefended piece
    """
    if not move.is_capture():
        return False
    
    from ..analysis.piece_safety import is_piece_safe
    
    # Check if target square has unsafe piece
    try:
        target_square = chess.parse_square(move.to_square)
        return not is_piece_safe(board, target_square)
    except:
        return False


def classify_critical(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode
) -> Optional[Classification]:
    """Classify move as CRITICAL if it's the only good move.
    
    Conditions:
    1. Top move played
    2. Second-best move loses >= 10%
    3. Not already completely winning
    4. Not lost position
    5. Not trivial (escaping check, free capture, promotion)
    
    Args:
        previous: Previous node data
        current: Current node data
        
    Returns:
        Classification.CRITICAL or None
    """
    # Check basic filters
    if not is_critical_candidate(previous, current):
        return None
    
    # Must have second-best line
    if not previous.second_top_line or not previous.second_subjective_eval:
        return None
    
    # Check if move is trivial
    # Skip if escaping check
    if previous.board.is_check():
        return None
    
    # Skip if free capture
    if current.played_move and is_free_capture(previous.board, current.played_move):
        return None
    
    # Skip if queen promotion
    if current.played_move and current.played_move.is_promotion():
        if current.played_move.promotion == 'q':
            return None
    
    # Calculate point loss of second-best move
    # This is the loss from playing second-best instead of best
    top_eval = previous.subjective_evaluation
    second_eval = previous.second_subjective_eval
    
    ep_top = get_expected_points(top_eval)
    ep_second = get_expected_points(second_eval)
    
    second_best_loss = max(0.0, ep_top - ep_second)
    
    # Check if second-best loses >= 10%
    if second_best_loss >= CRITICAL_THRESHOLD:
        return Classification.CRITICAL
    
    return None


"""BRILLIANT classification - spectacular sacrifices."""

import chess
from typing import Optional, List
from ..core.types import Classification, CLASSIFICATION_VALUES
from ..core.constants import COMPLETELY_WINNING
from ..analysis.piece_safety import get_unsafe_pieces
from ..analysis.danger_levels import has_danger_levels
from ..analysis.trapped_pieces import is_piece_trapped
from ..analysis.attackers import get_direct_attackers
from .node_extractor import ExtractedPreviousNode, ExtractedCurrentNode
from .critical import is_critical_candidate


def is_brilliant_candidate(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode,
    classification: Classification
) -> bool:
    """Check if move is a candidate for BRILLIANT.
    
    Args:
        previous: Previous node data
        current: Current node data
        classification: Current classification
        
    Returns:
        True if could be BRILLIANT
    """
    # Must be BEST or better
    if CLASSIFICATION_VALUES[classification] < CLASSIFICATION_VALUES[Classification.BEST]:
        return False
    
    # Must pass critical candidate filters
    if not is_critical_candidate(previous, current):
        return False
    
    # Cannot be promotion
    if current.played_move and current.played_move.is_promotion():
        return False
    
    # Must not be completely winning
    if (current.subjective_evaluation.type == "centipawn" and 
        current.subjective_evaluation.value >= COMPLETELY_WINNING):
        return False
    
    return True


def classify_brilliant(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode,
    classification: Classification
) -> Optional[Classification]:
    """Classify move as BRILLIANT if spectacular sacrifice.
    
    Conditions:
    1. Move is BEST or better
    2. Passes critical candidate filter
    3. Not a promotion
    4. Leaves piece(s) hanging (unsafe)
    5. Hanging pieces NOT protected by danger levels
    6. Hanging pieces NOT trapped (forced sacrifice)
    7. Not merely moving to safety
    
    Args:
        previous: Previous node data
        current: Current node data
        classification: Current classification
        
    Returns:
        Classification.BRILLIANT or None
    """
    # Check if candidate
    if not is_brilliant_candidate(previous, current, classification):
        return None
    
    # Get player color
    player_color = current.player_color
    chess_color = chess.WHITE if player_color.value == "white" else chess.BLACK
    
    # Find unsafe pieces after move
    unsafe_after = get_unsafe_pieces(current.board, chess_color)
    
    # Must have unsafe pieces (sacrifice)
    if not unsafe_after:
        return None
    
    # Check if not moving to safety
    # (If we had unsafe pieces before and now have fewer, we moved to safety)
    unsafe_before = get_unsafe_pieces(previous.board, chess_color)
    if len(unsafe_after) < len(unsafe_before):
        return None  # Moved to safety, not a sacrifice
    
    # Check each unsafe piece
    for unsafe_square in unsafe_after:
        piece = current.board.piece_at(unsafe_square)
        if not piece:
            continue
        
        # Get attackers of this piece
        opponent_color = not chess_color
        attackers = get_direct_attackers(current.board, unsafe_square, opponent_color)
        
        # Check if protected by danger levels
        if has_danger_levels(current.board, unsafe_square, attackers):
            # This piece is protected by counter-threats, skip it
            continue
        
        # Check if piece is trapped
        if is_piece_trapped(current.board, unsafe_square):
            # Piece was trapped, sacrifice was forced, skip it
            continue
        
        # Found a truly hanging piece that's:
        # - Not protected by danger levels
        # - Not trapped
        # This is a real sacrifice!
        return Classification.BRILLIANT
    
    # All unsafe pieces are either protected or trapped
    return None


"""FORCED classification - only one legal move available."""

import chess
from typing import Optional
from ..core.types import Classification
from .node_extractor import ExtractedPreviousNode


def is_forced_move(previous: ExtractedPreviousNode) -> bool:
    """Check if move is forced (only one legal move).
    
    Args:
        previous: Previous node data
        
    Returns:
        True if only one legal move available
    """
    legal_moves = list(previous.board.legal_moves)
    return len(legal_moves) <= 1


def classify_forced(previous: ExtractedPreviousNode) -> Optional[Classification]:
    """Classify move as FORCED if only legal move.
    
    Args:
        previous: Previous node data
        
    Returns:
        Classification.FORCED or None
    """
    if is_forced_move(previous):
        return Classification.FORCED
    return None


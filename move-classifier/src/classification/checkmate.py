"""CHECKMATE classification - mating moves."""

from typing import Optional
from ..core.types import Classification
from .node_extractor import ExtractedCurrentNode


def is_checkmate(current: ExtractedCurrentNode) -> bool:
    """Check if position is checkmate.
    
    Args:
        current: Current node data
        
    Returns:
        True if checkmate
    """
    return current.board.is_checkmate()


def classify_checkmate(current: ExtractedCurrentNode) -> Optional[Classification]:
    """Classify move as BEST if delivers checkmate.
    
    Args:
        current: Current node data
        
    Returns:
        Classification.BEST or None
    """
    if is_checkmate(current):
        return Classification.BEST
    return None


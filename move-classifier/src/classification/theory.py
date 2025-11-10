"""THEORY classification - opening book moves."""

from typing import Optional
from ..core.types import Classification
from ..utils.opening_book import OpeningBook
from .node_extractor import ExtractedCurrentNode


def classify_theory(
    current: ExtractedCurrentNode,
    opening_book: OpeningBook
) -> Optional[Classification]:
    """Classify move as THEORY if in opening book.
    
    Args:
        current: Current node data
        opening_book: Opening book database
        
    Returns:
        Classification.THEORY or None
    """
    opening_name = opening_book.lookup(current.fen)
    if opening_name:
        return Classification.THEORY
    return None


def get_opening_name(
    current: ExtractedCurrentNode,
    opening_book: OpeningBook
) -> Optional[str]:
    """Get opening name for position.
    
    Args:
        current: Current node data
        opening_book: Opening book database
        
    Returns:
        Opening name or None
    """
    return opening_book.lookup(current.fen)


"""Chess utility functions."""

import chess
from typing import List
from ..core.types import Square, PieceType


def square_to_index(square: Square) -> int:
    """Convert square name to index (0-63).
    
    Args:
        square: Square name (e.g., "e4")
        
    Returns:
        Square index
    """
    return chess.parse_square(square)


def index_to_square(index: int) -> Square:
    """Convert square index to name.
    
    Args:
        index: Square index (0-63)
        
    Returns:
        Square name
    """
    return chess.square_name(index)


def get_all_squares() -> List[Square]:
    """Get list of all square names.
    
    Returns:
        List of all 64 squares
    """
    return [chess.square_name(i) for i in range(64)]


def piece_symbol_to_type(symbol: str) -> PieceType:
    """Convert piece symbol to type.
    
    Args:
        symbol: Piece symbol (e.g., "N", "p")
        
    Returns:
        Piece type
    """
    return symbol.lower()


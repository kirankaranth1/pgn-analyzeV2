"""Find defending pieces."""

import chess
from typing import List


def get_defenders(
    board: chess.Board,
    square: chess.Square,
    defender_color: chess.Color
) -> List[chess.Square]:
    """Get pieces defending a square.
    
    A piece defends a square if it can recapture there.
    
    Args:
        board: Chess board
        square: Target square
        defender_color: Color of defending pieces
        
    Returns:
        List of squares with defending pieces
    """
    defenders = []
    
    # Use python-chess built-in attackers (same as defenders for our purposes)
    defender_squares = board.attackers(defender_color, square)
    
    for defender_square in defender_squares:
        defenders.append(defender_square)
    
    return defenders


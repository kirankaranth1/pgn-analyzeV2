"""Piece safety analysis."""

import chess
from typing import List
from .attackers import get_direct_attackers
from .defenders import get_defenders
from .material import get_board_piece_value


def is_piece_safe(
    board: chess.Board,
    square: chess.Square
) -> bool:
    """Check if a piece on a square is safe.
    
    A piece is safe if:
    - It's not attacked, OR
    - It's defended adequately (enough defenders, or attacker value >= piece value)
    
    Args:
        board: Chess board
        square: Square to check
        
    Returns:
        True if piece is safe
    """
    piece = board.piece_at(square)
    if not piece:
        return True  # No piece = safe
    
    piece_color = piece.color
    opponent_color = not piece_color
    
    # Get attackers and defenders
    attackers = get_direct_attackers(board, square, opponent_color)
    defenders = get_defenders(board, square, piece_color)
    
    # No attackers = safe
    if not attackers:
        return True
    
    # Get piece values
    piece_value = get_board_piece_value(piece)
    
    # Get lowest attacker value
    min_attacker_value = float('inf')
    for attacker_sq in attackers:
        attacker_piece = board.piece_at(attacker_sq)
        if attacker_piece:
            attacker_value = get_board_piece_value(attacker_piece)
            min_attacker_value = min(min_attacker_value, attacker_value)
    
    # If lowest attacker is worth more than piece, piece is safe
    # (opponent won't want to trade up)
    if min_attacker_value > piece_value:
        return True
    
    # If we have more defenders than attackers, likely safe
    if len(defenders) > len(attackers):
        return True
    
    # If equal defenders and attackers, check values
    if len(defenders) == len(attackers) and len(defenders) > 0:
        # Get lowest defender value
        min_defender_value = float('inf')
        for defender_sq in defenders:
            defender_piece = board.piece_at(defender_sq)
            if defender_piece:
                defender_value = get_board_piece_value(defender_piece)
                min_defender_value = min(min_defender_value, defender_value)
        
        # If our defender is worth less than piece, we can recapture profitably
        if min_defender_value < piece_value:
            return True
    
    # Otherwise, piece is hanging
    return False


def get_unsafe_pieces(
    board: chess.Board,
    color: chess.Color
) -> List[chess.Square]:
    """Get all unsafe (hanging) pieces for a color.
    
    Args:
        board: Chess board
        color: Color to check
        
    Returns:
        List of squares with unsafe pieces
    """
    unsafe = []
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            if not is_piece_safe(board, square):
                unsafe.append(square)
    
    return unsafe


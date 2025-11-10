"""Trapped piece detection."""

import chess
from typing import List
from .piece_safety import is_piece_safe
from .danger_levels import has_danger_levels
from .attackers import get_direct_attackers


def is_piece_trapped(
    board: chess.Board,
    square: chess.Square
) -> bool:
    """Check if a piece is trapped.
    
    A piece is trapped if:
    1. It is unsafe (under attack)
    2. It cannot move to any safe square
    3. Moving it doesn't create sufficient counter-threats
    
    Args:
        board: Chess board
        square: Square with piece to check
        
    Returns:
        True if piece is trapped
    """
    piece = board.piece_at(square)
    if not piece:
        return False
    
    # First check if piece is currently safe
    if is_piece_safe(board, square):
        return False  # Safe pieces aren't trapped
    
    piece_color = piece.color
    opponent_color = not piece_color
    
    # Get attackers
    attackers = get_direct_attackers(board, square, opponent_color)
    if not attackers:
        return False  # No attackers = not trapped
    
    # Check all legal moves for this piece
    legal_moves = [
        move for move in board.legal_moves
        if move.from_square == square
    ]
    
    for move in legal_moves:
        # Simulate the move
        board_copy = board.copy()
        board_copy.push(move)
        
        # Check if piece is now safe
        to_square = move.to_square
        if is_piece_safe(board_copy, to_square):
            return False  # Found a safe square
        
        # Check if move creates counter-threats (danger levels)
        # Get attackers of the piece in new position
        new_attackers = get_direct_attackers(board_copy, to_square, opponent_color)
        if has_danger_levels(board_copy, to_square, new_attackers):
            return False  # Protected by counter-threats
    
    # No safe moves found
    return True


def get_trapped_pieces(
    board: chess.Board,
    color: chess.Color
) -> List[chess.Square]:
    """Get all trapped pieces for a color.
    
    Args:
        board: Chess board
        color: Color to check
        
    Returns:
        List of squares with trapped pieces
    """
    trapped = []
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            if is_piece_trapped(board, square):
                trapped.append(square)
    
    return trapped


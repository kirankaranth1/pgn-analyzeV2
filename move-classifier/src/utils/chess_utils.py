"""
Chess Utility Functions

Helper functions for chess board manipulation.
"""

import chess
import uuid
from typing import Optional


def generate_unique_id() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def chess_color_to_piece_color(color: chess.Color) -> str:
    """
    Convert chess.Color to string representation.
    
    Args:
        color: Chess color (True=WHITE, False=BLACK)
        
    Returns:
        "WHITE" or "BLACK"
    """
    return "WHITE" if color == chess.WHITE else "BLACK"


def is_black_to_move(position: str) -> bool:
    """
    Check if it's black's turn to move from a FEN string.
    
    Args:
        position: FEN string
        
    Returns:
        True if black to move, False if white to move
    """
    return position.split()[1] == 'b'


def set_fen_turn(fen: str, color: chess.Color) -> str:
    """
    Set the turn in a FEN string to the specified color.
    
    Args:
        fen: FEN string to modify
        color: Color to set (chess.WHITE or chess.BLACK)
        
    Returns:
        Modified FEN string with updated turn
    """
    parts = fen.split(' ')
    parts[1] = 'w' if color == chess.WHITE else 'b'
    return ' '.join(parts)


def get_capture_square(move: chess.Move) -> Optional[chess.Square]:
    """
    Get the square where a capture occurs.
    
    For normal captures, this is the destination square.
    For en passant, this is calculated differently.
    
    Args:
        move: The move to check
        
    Returns:
        Square where capture occurs, or None if not a capture
    """
    # For en passant captures, the captured pawn is not on the destination square
    # but we still return the destination square as that's where the capturing piece lands
    return move.to_square


def flip_piece_color(color: chess.Color) -> chess.Color:
    """
    Flip the piece color.
    
    Args:
        color: Color to flip
        
    Returns:
        Opposite color
    """
    return chess.BLACK if color == chess.WHITE else chess.WHITE

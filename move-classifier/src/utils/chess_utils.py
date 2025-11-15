"""
Chess Utility Functions

Helper functions for chess-specific operations:
- Move validation
- Square manipulation
- Piece operations
- Board helpers
"""

import uuid
import chess


def generate_unique_id() -> str:
    """
    Generate a unique identifier for state tree nodes.
    
    Returns:
        Unique string identifier
    """
    return str(uuid.uuid4())


def chess_color_to_piece_color(chess_color: chess.Color) -> str:
    """
    Convert python-chess color to PieceColor enum string.
    
    Args:
        chess_color: chess.WHITE or chess.BLACK
        
    Returns:
        "WHITE" or "BLACK" string
    """
    return "WHITE" if chess_color == chess.WHITE else "BLACK"


def get_move_color_from_fen(fen: str) -> str:
    """
    Extract the active color from a FEN string.
    
    Args:
        fen: FEN string
        
    Returns:
        "WHITE" or "BLACK"
    """
    # FEN format: pieces turn castling enpassant halfmove fullmove
    # The second field is 'w' or 'b' for the active color
    parts = fen.split()
    if len(parts) >= 2:
        return "WHITE" if parts[1] == 'w' else "BLACK"
    return "WHITE"  # Default


def is_black_to_move(fen: str) -> bool:
    """
    Check if it's Black's turn to move.
    
    Args:
        fen: FEN string
        
    Returns:
        True if Black to move, False otherwise
    """
    return " b " in fen

"""FEN parsing and manipulation utilities."""

from typing import Tuple
from ..core.types import PieceColor


def parse_fen(fen: str) -> Tuple[str, str, str, str, str, str]:
    """Parse FEN into components.
    
    Args:
        fen: Full FEN string
        
    Returns:
        Tuple of (pieces, turn, castling, en_passant, halfmove, fullmove)
    """
    parts = fen.split()
    
    pieces = parts[0] if len(parts) > 0 else ""
    turn = parts[1] if len(parts) > 1 else "w"
    castling = parts[2] if len(parts) > 2 else "-"
    en_passant = parts[3] if len(parts) > 3 else "-"
    halfmove = parts[4] if len(parts) > 4 else "0"
    fullmove = parts[5] if len(parts) > 5 else "1"
    
    return pieces, turn, castling, en_passant, halfmove, fullmove


def set_fen_turn(fen: str, color: PieceColor) -> str:
    """Set whose turn it is in a FEN string.
    
    Args:
        fen: FEN string
        color: Color to set as active
        
    Returns:
        Modified FEN string
    """
    pieces, turn, castling, en_passant, halfmove, fullmove = parse_fen(fen)
    new_turn = "w" if color == PieceColor.WHITE else "b"
    return f"{pieces} {new_turn} {castling} {en_passant} {halfmove} {fullmove}"


def get_turn_from_fen(fen: str) -> PieceColor:
    """Get whose turn it is from FEN.
    
    Args:
        fen: FEN string
        
    Returns:
        PieceColor of active player
    """
    _, turn, _, _, _, _ = parse_fen(fen)
    return PieceColor.WHITE if turn == "w" else PieceColor.BLACK


"""Material evaluation and piece values."""

import chess
from ..core.constants import PIECE_VALUES
from ..core.types import PieceType


def get_piece_value(piece_type: PieceType) -> float:
    """Get material value of a piece.
    
    Args:
        piece_type: Piece type ('p', 'n', 'b', 'r', 'q', 'k')
        
    Returns:
        Piece value
    """
    return PIECE_VALUES.get(piece_type, 0)


def get_board_piece_value(piece: chess.Piece) -> float:
    """Get value of a chess.Piece.
    
    Args:
        piece: chess.Piece object
        
    Returns:
        Piece value
    """
    piece_type = piece.symbol().lower()
    return get_piece_value(piece_type)


def evaluate_material(board: chess.Board, color: chess.Color) -> float:
    """Evaluate total material for a color.
    
    Args:
        board: Chess board
        color: Color to evaluate
        
    Returns:
        Total material value
    """
    total = 0.0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            total += get_board_piece_value(piece)
    return total


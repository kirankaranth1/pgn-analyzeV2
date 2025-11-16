"""
Chess Type Definitions

Types for representing chess pieces and moves in a simplified format.
"""

from dataclasses import dataclass
from typing import Optional
import chess


@dataclass
class BoardPiece:
    """Represents a piece on the board with its location and color."""
    
    square: chess.Square
    """Square where the piece is located (0-63)."""
    
    type: chess.PieceType
    """Type of piece (PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING)."""
    
    color: chess.Color
    """Color of the piece (WHITE or BLACK)."""


@dataclass
class RawMove:
    """Represents a move in simplified format."""
    
    piece: chess.PieceType
    """Type of piece being moved."""
    
    color: chess.Color
    """Color of the piece."""
    
    from_square: chess.Square
    """Starting square (0-63)."""
    
    to_square: chess.Square
    """Destination square (0-63)."""
    
    promotion: Optional[chess.PieceType] = None
    """Promotion piece type if applicable."""


def to_raw_move(move: chess.Move, board: chess.Board) -> RawMove:
    """Convert a chess.Move to a RawMove."""
    piece = board.piece_at(move.from_square)
    if piece is None:
        raise ValueError(f"No piece at {chess.square_name(move.from_square)}")
    
    return RawMove(
        piece=piece.piece_type,
        color=piece.color,
        from_square=move.from_square,
        to_square=move.to_square,
        promotion=move.promotion
    )


def to_board_piece(raw_move: RawMove) -> BoardPiece:
    """Convert a RawMove to a BoardPiece (piece at its starting position)."""
    return BoardPiece(
        square=raw_move.from_square,
        type=raw_move.piece,
        color=raw_move.color
    )


def get_board_pieces(board: chess.Board) -> list[BoardPiece]:
    """Get all pieces on the board as BoardPiece objects."""
    pieces = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            pieces.append(BoardPiece(
                square=square,
                type=piece.piece_type,
                color=piece.color
            ))
    return pieces


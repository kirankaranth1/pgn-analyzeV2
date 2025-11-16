"""
Piece Safety Analysis

Functions to determine if pieces are safe or hanging.
"""

from typing import Optional
import chess

from ..models.chess_types import BoardPiece, RawMove, to_board_piece, get_board_pieces
from ..constants import PIECE_VALUES
from .attackers import get_attacking_moves
from .defenders import get_defending_moves


def is_piece_safe(
    board: chess.Board,
    piece: BoardPiece,
    played_move: Optional[chess.Move] = None
) -> bool:
    """
    Determine if a piece is safe (not hanging).
    
    A piece is considered safe if:
    1. It has no direct attackers of lower value
    2. It has at least as many defenders as attackers
    3. Special case: favorable/decimal sacrifices (rook for 2 pieces)
    4. It's lower in value than any direct attacker and has a defender
       lower in value than all direct attackers
    5. It's defended by a pawn (at this point in the algorithm)
    
    Args:
        board: Current board position
        piece: Piece to check
        played_move: The move that was just played (optional)
        
    Returns:
        True if piece is safe, False if hanging
    """
    direct_attackers_moves = get_attacking_moves(board, piece, transitive=False)
    direct_attackers = [to_board_piece(move) for move in direct_attackers_moves]
    
    attackers_moves = get_attacking_moves(board, piece, transitive=True)
    attackers = [to_board_piece(move) for move in attackers_moves]
    
    defenders_moves = get_defending_moves(board, piece, transitive=True)
    defenders = [to_board_piece(move) for move in defenders_moves]
    
    # Special case: Favorable, decimal sacrifices (rook for 2 pieces etc.) are safe
    if played_move:
        captured_piece = board.piece_at(played_move.to_square) if played_move else None
        if (
            captured_piece
            and piece.type == chess.ROOK
            and PIECE_VALUES[captured_piece.piece_type] == PIECE_VALUES[chess.KNIGHT]
            and len(attackers) == 1
            and len(defenders) > 0
            and PIECE_VALUES[attackers[0].type] == PIECE_VALUES[chess.KNIGHT]
        ):
            return True
    
    # A piece with a direct attacker of lower value than itself isn't safe
    has_lower_value_attacker = any(
        PIECE_VALUES[attacker.type] < PIECE_VALUES[piece.type]
        for attacker in direct_attackers
    )
    if has_lower_value_attacker:
        return False
    
    # A piece that does not have more attackers than it has defenders is safe
    if len(attackers) <= len(defenders):
        return True
    
    # A piece lower in value than any direct attacker, and with any
    # defender lower in value than all direct attackers, must be safe
    if direct_attackers:
        lowest_value_attacker = min(
            direct_attackers,
            key=lambda attacker: PIECE_VALUES[attacker.type]
        )
        
        if (
            PIECE_VALUES[piece.type] < PIECE_VALUES[lowest_value_attacker.type]
            and any(
                PIECE_VALUES[defender.type] < PIECE_VALUES[lowest_value_attacker.type]
                for defender in defenders
            )
        ):
            return True
    
    # A piece defended by any pawn, at this point, must be safe
    if any(defender.type == chess.PAWN for defender in defenders):
        return True
    
    return False


def get_unsafe_pieces(
    board: chess.Board,
    color: chess.Color,
    played_move: Optional[chess.Move] = None
) -> list[BoardPiece]:
    """
    Get all unsafe (hanging) pieces for a given color.
    
    Excludes:
    - Pawns
    - Kings
    - Pieces of lower value than a captured piece (if a capture was made)
    
    Args:
        board: Current board position
        color: Color to check for unsafe pieces
        played_move: The move that was just played (optional)
        
    Returns:
        List of unsafe pieces
    """
    # Determine captured piece value
    captured_piece_value = 0
    if played_move:
        captured_piece = board.piece_at(played_move.to_square)
        if captured_piece:
            captured_piece_value = PIECE_VALUES[captured_piece.piece_type]
    
    # Get all pieces of the specified color
    all_pieces = get_board_pieces(board)
    
    # Filter for unsafe pieces
    unsafe_pieces = []
    for piece in all_pieces:
        if (
            piece.color == color
            and piece.type != chess.PAWN
            and piece.type != chess.KING
            and PIECE_VALUES[piece.type] > captured_piece_value
            and not is_piece_safe(board, piece, played_move)
        ):
            unsafe_pieces.append(piece)
    
    return unsafe_pieces


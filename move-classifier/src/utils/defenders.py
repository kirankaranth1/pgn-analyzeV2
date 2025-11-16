"""
Defender Detection

Functions to detect pieces defending a target piece.
"""

from typing import Optional
import chess

from ..models.chess_types import BoardPiece, RawMove, to_board_piece
from .chess_utils import set_fen_turn, flip_piece_color
from .attackers import get_attacking_moves


def get_defending_moves(
    board: chess.Board,
    piece: BoardPiece,
    transitive: bool = True
) -> list[RawMove]:
    """
    Get all moves defending a piece.
    
    Defenders are determined by:
    1. If there are attackers, simulate each capture and find the smallest
       set of recapturers
    2. If there are no attackers, flip the piece color and count attackers
       of the flipped piece (these are the defenders)
    
    Args:
        board: Current board position
        piece: Piece being defended
        transitive: Whether to include transitive defenders (default: True)
        
    Returns:
        List of defending moves
    """
    defender_board = chess.Board(board.fen())
    attacking_moves = get_attacking_moves(defender_board, piece, transitive=False)
    
    # Where there are attackers, simulate taking the piece with each attacker
    # and record the minima of recaptures
    recapturer_sets: list[list[RawMove]] = []
    
    for attacking_move in attacking_moves:
        # Create board with turn set to the attacker's color
        capture_fen = set_fen_turn(
            defender_board.fen(),
            flip_piece_color(piece.color)
        )
        capture_board = chess.Board(capture_fen)
        
        # Try to make the attacking move
        try:
            move = chess.Move(
                attacking_move.from_square,
                attacking_move.to_square,
                promotion=attacking_move.promotion
            )
            capture_board.push(move)
        except (ValueError, AssertionError):
            # Invalid move, skip
            continue
        
        # Get attackers of the piece that just captured (these are recapturers)
        recapturers = get_attacking_moves(
            capture_board,
            BoardPiece(
                square=attacking_move.to_square,
                type=attacking_move.piece,
                color=attacking_move.color
            ),
            transitive=transitive
        )
        
        recapturer_sets.append(recapturers)
    
    # Find the smallest recapturer set
    if recapturer_sets:
        smallest_recapturer_set = min(recapturer_sets, key=len)
        return smallest_recapturer_set
    
    # Where there are no attackers, flip the colour of the piece and count
    # the attackers of the flipped piece
    flipped_piece = BoardPiece(
        type=piece.type,
        color=flip_piece_color(piece.color),
        square=piece.square
    )
    
    # Create a new board with the flipped piece
    flipped_board = chess.Board(defender_board.fen())
    flipped_board.remove_piece_at(piece.square)
    flipped_board.set_piece_at(
        piece.square,
        chess.Piece(flipped_piece.type, flipped_piece.color)
    )
    
    return get_attacking_moves(flipped_board, flipped_piece, transitive=transitive)


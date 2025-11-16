"""
Attacker Detection

Functions to detect pieces attacking a target square, including:
- Direct attackers (pieces that can immediately capture)
- Transitive attackers (pieces behind other pieces in batteries)
"""

from dataclasses import dataclass
from typing import Optional
import chess

from ..models.chess_types import BoardPiece, RawMove, to_raw_move, to_board_piece
from .chess_utils import set_fen_turn, get_capture_square, flip_piece_color


@dataclass
class TransitiveAttacker:
    """Represents a piece in an attacking battery."""
    
    direct_fen: str
    """FEN where this piece is a direct attacker."""
    
    square: chess.Square
    """Square where the attacking piece is located."""
    
    piece_type: chess.PieceType
    """Type of the attacking piece."""


def _direct_attacking_moves(
    board: chess.Board,
    piece: BoardPiece
) -> list[RawMove]:
    """
    Get all direct attacking moves on a piece.
    
    Args:
        board: Current board position
        piece: Piece being attacked
        
    Returns:
        List of moves that attack the piece
    """
    # Set turn to attacker's side (opposite of piece color)
    attacker_fen = set_fen_turn(board.fen(), flip_piece_color(piece.color))
    attacker_board = chess.Board(attacker_fen)
    
    # Get all legal moves that capture on the piece's square
    attacking_moves: list[RawMove] = []
    for move in attacker_board.legal_moves:
        if get_capture_square(move) == piece.square:
            attacking_moves.append(to_raw_move(move, attacker_board))
    
    # Special case: King attacks are not always in legal moves if they would
    # put the king in check. Check if king is an attacker using board.attackers()
    attackers_squares = attacker_board.attackers(
        flip_piece_color(piece.color),
        piece.square
    )
    
    for attacker_square in attackers_squares:
        attacker_piece = attacker_board.piece_at(attacker_square)
        if attacker_piece and attacker_piece.piece_type == chess.KING:
            # Check if king attack is already in the list
            if not any(
                move.piece == chess.KING and move.from_square == attacker_square
                for move in attacking_moves
            ):
                attacking_moves.append(RawMove(
                    piece=chess.KING,
                    color=flip_piece_color(piece.color),
                    from_square=attacker_square,
                    to_square=piece.square
                ))
    
    return attacking_moves


def get_attacking_moves(
    board: chess.Board,
    piece: BoardPiece,
    transitive: bool = True
) -> list[RawMove]:
    """
    Get all moves attacking a piece, including transitive (battery) attacks.
    
    Transitive attacks occur when a piece is behind another piece in a line
    (battery). For example, a rook behind a bishop on the same diagonal.
    
    Args:
        board: Current board position
        piece: Piece being attacked
        transitive: Whether to include transitive attackers (default: True)
        
    Returns:
        List of all attacking moves
    """
    attacking_moves = _direct_attacking_moves(board, piece)
    
    if not transitive:
        return attacking_moves
    
    # Keep a record of each transitive attacker and the FEN on
    # which they are considered a direct attacker
    frontier: list[TransitiveAttacker] = [
        TransitiveAttacker(
            direct_fen=board.fen(),
            square=move.from_square,
            piece_type=move.piece
        )
        for move in attacking_moves
    ]
    
    while frontier:
        transitive_attacker = frontier.pop()
        
        # A king cannot be at the front of a battery
        if transitive_attacker.piece_type == chess.KING:
            continue
        
        # Create board from the FEN where this piece was a direct attacker
        transitive_board = chess.Board(transitive_attacker.direct_fen)
        
        # Get old attacking moves before removing the piece
        old_attacking_moves = _direct_attacking_moves(transitive_board, piece)
        
        # Remove the piece at the front of the battery
        transitive_board.remove_piece_at(transitive_attacker.square)
        
        # Find revealed attackers
        new_attacking_moves = _direct_attacking_moves(transitive_board, piece)
        
        # Find moves that are in new but not in old (excluding the removed piece)
        old_attacking_moves_filtered = [
            move for move in old_attacking_moves
            if move.from_square != transitive_attacker.square
        ]
        
        # XOR: moves in new but not in old
        revealed_attacking_moves = [
            move for move in new_attacking_moves
            if not any(
                old.from_square == move.from_square and
                old.to_square == move.to_square and
                old.piece == move.piece
                for old in old_attacking_moves_filtered
            )
        ]
        
        # Record revealed attackers in final list
        attacking_moves.extend(revealed_attacking_moves)
        
        # Queue revealed attackers for further recursion
        frontier.extend([
            TransitiveAttacker(
                direct_fen=transitive_board.fen(),
                square=move.from_square,
                piece_type=move.piece
            )
            for move in revealed_attacking_moves
        ])
    
    return attacking_moves


"""
Danger Levels Analysis

Functions to determine if unsafe pieces are protected by counter-threats
(danger levels). When a piece is hanging but capturing it creates a bigger
counter-threat, it's protected by "danger levels".
"""

from typing import List, Literal, Optional
import chess

from ..models.chess_types import BoardPiece, RawMove, to_raw_move
from ..constants import PIECE_VALUES
from ..utils.piece_safety import get_unsafe_pieces
from ..utils.attackers import get_attacking_moves


def _relative_unsafe_piece_attacks(
    action_board: chess.Board,
    threatened_piece: BoardPiece,
    color: chess.Color,
    played_move: Optional[chess.Move] = None
) -> List[RawMove]:
    """
    Returns attacking moves of unsafe pieces of a given color that are
    higher or equal in value to the threatened piece.
    
    Args:
        action_board: Current board position
        threatened_piece: Piece under threat
        color: Color of pieces to check
        played_move: Optional move that was played
        
    Returns:
        List of attacking moves from valuable unsafe pieces
    """
    unsafe_pieces = get_unsafe_pieces(action_board, color, played_move)
    
    relative_attacks: List[RawMove] = []
    
    for unsafe_piece in unsafe_pieces:
        # Skip the threatened piece itself
        if unsafe_piece.square == threatened_piece.square:
            continue
        
        # Only consider pieces >= value of threatened piece
        if PIECE_VALUES[unsafe_piece.type] < PIECE_VALUES[threatened_piece.type]:
            continue
        
        # Get all attacking moves from this unsafe piece
        attacks = get_attacking_moves(action_board, unsafe_piece, transitive=False)
        relative_attacks.extend(attacks)
    
    return relative_attacks


def _parse_san_move_for_checkmate(san: str) -> bool:
    """
    Check if a SAN move string indicates checkmate.
    
    Args:
        san: Move in SAN notation
        
    Returns:
        True if move is checkmate
    """
    return san.endswith('#')


def move_creates_greater_threat(
    board: chess.Board,
    threatened_piece: BoardPiece,
    acting_move: RawMove
) -> bool:
    """
    Check if acting on a threat (e.g., capturing or moving) creates a
    greater counter-threat than the original threat.
    
    For example, if a queen is hanging but capturing it allows Rxe8#,
    the queen is protected by danger levels.
    
    Args:
        board: Current board position
        threatened_piece: Piece under threat
        acting_move: Move acting on the threat
        
    Returns:
        True if acting creates a greater counter-threat
    """
    action_board = chess.Board(board.fen())
    
    # Get unsafe pieces BEFORE the acting move
    previous_relative_attacks = _relative_unsafe_piece_attacks(
        action_board,
        threatened_piece,
        acting_move.color
    )
    
    # Try to make the acting move
    try:
        move = chess.Move(
            acting_move.from_square,
            acting_move.to_square,
            promotion=acting_move.promotion
        )
        action_board.push(move)
    except (ValueError, AssertionError):
        return False
    
    # Get unsafe pieces AFTER the acting move
    relative_attacks = _relative_unsafe_piece_attacks(
        action_board,
        threatened_piece,
        acting_move.color,
        move
    )
    
    # Find NEW attacks that didn't exist before
    new_relative_attacks = []
    for attack in relative_attacks:
        # Check if this attack is new (not in previous attacks)
        is_new = True
        for prev_attack in previous_relative_attacks:
            if (
                attack.from_square == prev_attack.from_square
                and attack.to_square == prev_attack.to_square
                and attack.piece == prev_attack.piece
            ):
                is_new = False
                break
        
        if is_new:
            new_relative_attacks.append(attack)
    
    if len(new_relative_attacks) > 0:
        return True
    
    # Lower value piece sacrifice that if taken leads to mate
    low_value_checkmate_pin = (
        PIECE_VALUES[threatened_piece.type] < PIECE_VALUES[chess.QUEEN]
        and any(
            _parse_san_move_for_checkmate(action_board.san(move))
            for move in action_board.legal_moves
        )
    )
    
    return low_value_checkmate_pin


def move_leaves_greater_threat(
    board: chess.Board,
    threatened_piece: BoardPiece,
    acting_move: RawMove
) -> bool:
    """
    Check if a move leaves a greater threat (regardless of whether it created it).
    
    Similar to move_creates_greater_threat but doesn't check if the threat
    is NEW - just checks if greater threats exist after the move.
    
    Args:
        board: Current board position
        threatened_piece: Piece under threat
        acting_move: Move acting on the threat
        
    Returns:
        True if move leaves a greater counter-threat
    """
    action_board = chess.Board(board.fen())
    
    # Try to make the acting move
    try:
        move = chess.Move(
            acting_move.from_square,
            acting_move.to_square,
            promotion=acting_move.promotion
        )
        action_board.push(move)
    except (ValueError, AssertionError):
        return False
    
    # Get unsafe pieces AFTER the acting move
    relative_attacks = _relative_unsafe_piece_attacks(
        action_board,
        threatened_piece,
        acting_move.color
    )
    
    if len(relative_attacks) > 0:
        return True
    
    # Lower value piece sacrifice that if taken leads to mate
    low_value_checkmate_pin = (
        PIECE_VALUES[threatened_piece.type] < PIECE_VALUES[chess.QUEEN]
        and any(
            _parse_san_move_for_checkmate(action_board.san(move))
            for move in action_board.legal_moves
        )
    )
    
    return low_value_checkmate_pin


def has_danger_levels(
    board: chess.Board,
    threatened_piece: BoardPiece,
    acting_moves: List[RawMove],
    equality_strategy: Literal["creates", "leaves"] = "leaves"
) -> bool:
    """
    Check if all acting moves create/leave a threat larger than that
    imposed on the threatened piece.
    
    This determines if an unsafe piece is protected by "danger levels" -
    counter-threats that make it unsafe to capture.
    
    Args:
        board: Current board position
        threatened_piece: Piece under threat
        acting_moves: Moves that could act on the threat (e.g., captures)
        equality_strategy: 
            - "creates": threats must be directly created by the move
            - "leaves": threats just need to exist after the move
            
    Returns:
        True if ALL acting moves create/leave greater threats
    """
    if equality_strategy == "creates":
        return all(
            move_creates_greater_threat(board, threatened_piece, move)
            for move in acting_moves
        )
    else:  # "leaves"
        return all(
            move_leaves_greater_threat(board, threatened_piece, move)
            for move in acting_moves
        )


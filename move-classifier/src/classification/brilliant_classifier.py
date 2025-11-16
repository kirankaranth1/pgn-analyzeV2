"""
Brilliant Classification

Determines if a move should be classified as BRILLIANT.
"""

import chess

from ..models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from ..models.chess_types import get_board_pieces
from ..constants import PIECE_VALUES
from ..utils.piece_safety import get_unsafe_pieces, is_piece_safe
from ..utils.danger_levels import has_danger_levels
from ..utils.piece_trapped import is_piece_trapped
from ..utils.attackers import get_attacking_moves
from .critical_move import is_move_critical_candidate


def consider_brilliant_classification(
    previous: ExtractedPreviousNode,
    current: ExtractedCurrentNode
) -> bool:
    """
    Determine if a move should be classified as BRILLIANT.
    
    A brilliant move is one that:
    - Passes critical candidate check (winning position, not forced)
    - Is not a promotion
    - Leaves pieces unsafe (sacrifice or risk)
    - Unsafe pieces are NOT all protected by danger levels
    - Is not escaping a trapped piece
    - Is not simply moving to safety (reducing unsafe pieces)
    
    Args:
        previous: Node before the move
        current: Node after the move
        
    Returns:
        True if move should be classified as BRILLIANT
    """
    if not is_move_critical_candidate(previous, current):
        return False
    
    # Promotions cannot be brilliant
    if current.played_move and current.played_move.promotion:
        return False
    
    # Get the player's color (who made the move)
    player_color = chess.Board(previous.state.fen).turn
    
    # Get unsafe pieces BEFORE the move
    previous_unsafe_pieces = get_unsafe_pieces(
        previous.board,
        player_color
    )
    
    # Determine what was captured (from previous board, before the move)
    captured_piece_value = 0
    if current.played_move:
        captured_piece = previous.board.piece_at(current.played_move.to_square)
        if captured_piece:
            captured_piece_value = PIECE_VALUES[captured_piece.piece_type]
    
    # Get unsafe pieces AFTER the move
    # We need to manually filter based on captured piece value
    # because get_unsafe_pieces expects board BEFORE move for capture detection
    all_pieces_after = get_board_pieces(current.board)
    unsafe_pieces = []
    
    for piece in all_pieces_after:
        if (
            piece.color == player_color
            and piece.type != chess.PAWN
            and piece.type != chess.KING
            and PIECE_VALUES[piece.type] > captured_piece_value
            and not is_piece_safe(current.board, piece)
        ):
            unsafe_pieces.append(piece)
    
    # Moving to safety (less unsafe pieces) disallows brilliant
    # UNLESS in check (desperate moves in check can be brilliant)
    if (
        not current.board.is_check()
        and len(unsafe_pieces) < len(previous_unsafe_pieces)
    ):
        return False
    
    # Check if all unsafe pieces are protected by danger levels
    # If ALL pieces are protected by counter-threats, not brilliant
    danger_levels_protected = all(
        has_danger_levels(
            current.board,
            unsafe_piece,
            get_attacking_moves(current.board, unsafe_piece, transitive=False)
        )
        for unsafe_piece in unsafe_pieces
    )
    
    if danger_levels_protected:
        return False
    
    # Check for trapped pieces
    previous_trapped_pieces = [
        piece for piece in previous_unsafe_pieces
        if is_piece_trapped(previous.board, piece)
    ]
    
    trapped_pieces = [
        piece for piece in unsafe_pieces
        if is_piece_trapped(current.board, piece)
    ]
    
    # Check if the moved piece was trapped
    moved_piece_trapped = False
    if current.played_move:
        moved_piece_trapped = any(
            trapped_piece.square == current.played_move.from_square
            for trapped_piece in previous_trapped_pieces
        )
    
    # Disallow if:
    # - All unsafe pieces are trapped (forced sacrifices)
    # - Moved piece was trapped (escaping trap, not brilliant)
    # - Reducing trapped pieces (moving to safety)
    if (
        len(trapped_pieces) == len(unsafe_pieces)  # All pieces trapped
        or moved_piece_trapped  # Escaping trap
        or len(trapped_pieces) < len(previous_trapped_pieces)  # Reducing traps
    ):
        return False
    
    # Must leave at least one piece unsafe (sacrifice/risk)
    return len(unsafe_pieces) > 0


"""
Piece Trapped Detection

Functions to determine if a piece is trapped (unable to move to safety).
"""

import chess
from typing import Optional

from ..models.chess_types import BoardPiece
from ..utils.piece_safety import is_piece_safe
from ..utils.danger_levels import move_creates_greater_threat
from ..utils.chess_utils import set_fen_turn


def is_piece_trapped(
    board: chess.Board,
    piece: BoardPiece,
    danger_levels: bool = True
) -> bool:
    """
    Check if a piece is trapped.
    
    A piece is trapped if:
    1. It is unsafe on its current square
    2. ALL moves it can make leave it unsafe OR create greater counter-threats
    
    Args:
        board: Current board position
        piece: Piece to check
        danger_levels: Whether to consider danger levels (counter-threats)
        
    Returns:
        True if piece is trapped
    """
    # Calibrate board to piece's turn
    calibrated_fen = set_fen_turn(board.fen(), piece.color)
    calibrated_board = chess.Board(calibrated_fen)
    
    # Check if piece is currently safe
    standing_piece_safety = is_piece_safe(calibrated_board, piece)
    
    # Get all legal moves for this piece
    piece_moves = []
    for move in calibrated_board.legal_moves:
        if move.from_square == piece.square:
            piece_moves.append(move)
    
    # Check if all moves leave piece unsafe
    all_moves_unsafe = True
    
    for move in piece_moves:
        # Can't capture king (shouldn't happen but safety check)
        captured_piece = calibrated_board.piece_at(move.to_square)
        if captured_piece and captured_piece.piece_type == chess.KING:
            all_moves_unsafe = False
            break
        
        escape_board = chess.Board(calibrated_board.fen())
        
        # If danger levels enabled, check if move creates greater threat
        if danger_levels:
            from ..models.chess_types import RawMove, to_raw_move
            
            raw_move = to_raw_move(move, escape_board)
            if move_creates_greater_threat(escape_board, piece, raw_move):
                # Move creates greater threat, so it's "unsafe"
                continue
        
        # Make the escape move
        escape_board.push(move)
        
        # Check if piece is safe at new square
        escaped_piece = BoardPiece(
            square=move.to_square,
            type=piece.type,
            color=piece.color
        )
        
        escaped_piece_safety = is_piece_safe(escape_board, escaped_piece, move)
        
        if escaped_piece_safety:
            # Found a safe escape
            all_moves_unsafe = False
            break
    
    # Piece is trapped if it's unsafe now AND all moves are unsafe
    return not standing_piece_safety and all_moves_unsafe


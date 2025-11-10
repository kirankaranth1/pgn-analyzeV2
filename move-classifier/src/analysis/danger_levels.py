"""Danger level analysis - counter-threats protecting hanging pieces."""

import chess
from typing import List
from .material import get_board_piece_value


def has_danger_levels(
    board: chess.Board,
    unsafe_square: chess.Square,
    attacker_squares: List[chess.Square]
) -> bool:
    """Check if an unsafe piece is protected by counter-threats (danger levels).
    
    A piece has danger levels if capturing it creates a bigger counter-threat.
    
    Args:
        board: Chess board
        unsafe_square: Square with unsafe piece
        attacker_squares: Squares of pieces attacking the unsafe piece
        
    Returns:
        True if piece is protected by danger levels
    """
    piece = board.piece_at(unsafe_square)
    if not piece:
        return False
    
    piece_value = get_board_piece_value(piece)
    piece_color = piece.color
    opponent_color = not piece_color
    
    # For each way to capture
    for attacker_sq in attacker_squares:
        # Simulate the capture
        board_copy = board.copy()
        
        # Create a pseudo-legal move (capture)
        try:
            # Find a legal move from attacker to unsafe square
            legal_capture = None
            for move in board_copy.legal_moves:
                if move.from_square == attacker_sq and move.to_square == unsafe_square:
                    legal_capture = move
                    break
            
            if not legal_capture:
                continue
            
            # Make the capture
            board_copy.push(legal_capture)
            
            # Check if this creates threats
            # Look for checks or threats to valuable pieces
            if board_copy.is_check():
                # Capturing creates check = danger level
                return True
            
            # Check if opponent's pieces are now under attack
            for square in chess.SQUARES:
                target_piece = board_copy.piece_at(square)
                if target_piece and target_piece.color == opponent_color:
                    target_value = get_board_piece_value(target_piece)
                    
                    # Check if we now attack this piece
                    attackers = board_copy.attackers(piece_color, square)
                    if attackers and target_value >= piece_value:
                        # We threaten a piece worth >= the captured piece
                        return True
            
        except Exception:
            continue
    
    return False


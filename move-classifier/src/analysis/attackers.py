"""Find attacking pieces."""

import chess
from typing import List, Set


def get_direct_attackers(
    board: chess.Board,
    square: chess.Square,
    attacker_color: chess.Color
) -> List[chess.Square]:
    """Get pieces directly attacking a square.
    
    Args:
        board: Chess board
        square: Target square
        attacker_color: Color of attacking pieces
        
    Returns:
        List of squares with attacking pieces
    """
    attackers = []
    
    # Use python-chess built-in attackers method
    attacker_squares = board.attackers(attacker_color, square)
    
    for attacker_square in attacker_squares:
        attackers.append(attacker_square)
    
    return attackers


def get_all_attackers(
    board: chess.Board,
    square: chess.Square,
    attacker_color: chess.Color,
    include_xray: bool = True
) -> List[chess.Square]:
    """Get all pieces attacking a square, including x-ray attacks.
    
    X-ray attacks are revealed when a piece is removed (e.g., rook behind queen).
    
    Args:
        board: Chess board
        square: Target square
        attacker_color: Color of attacking pieces
        include_xray: Whether to include x-ray attacks
        
    Returns:
        List of squares with attacking pieces (including x-ray)
    """
    if not include_xray:
        return get_direct_attackers(board, square, attacker_color)
    
    all_attackers = []
    seen_squares: Set[chess.Square] = set()
    
    def find_attackers_recursive(temp_board: chess.Board, depth: int = 0):
        """Recursively find attackers including x-rays."""
        if depth > 10:  # Prevent infinite recursion
            return
        
        direct = get_direct_attackers(temp_board, square, attacker_color)
        
        for attacker_sq in direct:
            if attacker_sq not in seen_squares:
                seen_squares.add(attacker_sq)
                all_attackers.append(attacker_sq)
                
                # Remove this attacker to reveal x-ray attacks
                piece = temp_board.piece_at(attacker_sq)
                if piece:
                    temp_board.remove_piece_at(attacker_sq)
                    find_attackers_recursive(temp_board, depth + 1)
                    temp_board.set_piece_at(attacker_sq, piece)
    
    # Work with a copy
    board_copy = board.copy()
    find_attackers_recursive(board_copy)
    
    return all_attackers


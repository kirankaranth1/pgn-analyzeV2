"""
Chess Notation Converters

Utilities for converting between chess notation systems:
- SAN ↔ UCI conversion
- FEN manipulation
- Lichess castling notation normalization
"""

from ..constants import LICHESS_CASTLING


def normalize_lichess_castling(uci_move: str) -> str:
    """
    Convert Lichess king-to-rook castling notation to standard UCI.
    
    Lichess uses king-to-rook notation:
    - e1h1 → e1g1 (White kingside)
    - e1a1 → e1c1 (White queenside)
    - e8h8 → e8g8 (Black kingside)
    - e8a8 → e8c8 (Black queenside)
    
    Args:
        uci_move: UCI move notation (potentially Lichess format)
        
    Returns:
        Normalized UCI move notation
    """
    return LICHESS_CASTLING.get(uci_move, uci_move)

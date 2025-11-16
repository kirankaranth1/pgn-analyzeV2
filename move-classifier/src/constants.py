"""
System Constants

Critical constants used throughout the classification system.
"""

import chess

# Expected Points Calculation
CENTIPAWN_GRADIENT = 0.0035

# Move Accuracy Calculation
ACCURACY_MULTIPLIER = 103.16
ACCURACY_EXPONENT = -4.0
ACCURACY_OFFSET = -3.17

# Starting Position
STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Lichess Castling Notation Conversion
LICHESS_CASTLING = {
    "e1h1": "e1g1",  # White kingside
    "e1a1": "e1c1",  # White queenside
    "e8h8": "e8g8",  # Black kingside
    "e8a8": "e8c8"   # Black queenside
}

# Piece Values (for tactical analysis)
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: float('inf')
}


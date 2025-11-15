"""
Enumeration Types

All enumeration types used in the classification system.
"""

from enum import Enum


class PieceColor(str, Enum):
    """Chess piece colors."""
    
    WHITE = "WHITE"
    BLACK = "BLACK"


class Classification(str, Enum):
    """Move quality classifications."""
    
    # Basic Classifications
    CHECKMATE = "CHECKMATE"
    FORCED = "FORCED"
    BOOK = "BOOK"
    
    # Point Loss Classifications
    BEST = "BEST"
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    INACCURACY = "INACCURACY"
    MISTAKE = "MISTAKE"
    BLUNDER = "BLUNDER"
    CRITICAL = "CRITICAL"
    
    # Advanced Classifications
    BRILLIANT = "BRILLIANT"
    GREAT_FIND = "GREAT_FIND"
    
    # Attack/Defense
    ATTACKING_MOVE = "ATTACKING_MOVE"
    DEFENSIVE_MOVE = "DEFENSIVE_MOVE"


class EngineVersion(str, Enum):
    """Supported chess engines."""
    
    STOCKFISH_17 = "stockfish-17"
    STOCKFISH_17_LITE = "stockfish-17-lite"
    LICHESS_CLOUD = "lichess-cloud"

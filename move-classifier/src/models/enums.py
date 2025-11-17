"""
Enumeration Types

All enumeration types used in the classification system.
"""

from enum import Enum
from dataclasses import dataclass


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


# Classification value ordering (for comparison)
CLASSIFICATION_VALUES = {
    Classification.BLUNDER: 0,
    Classification.MISTAKE: 1,
    Classification.INACCURACY: 2,
    Classification.GOOD: 3,
    Classification.EXCELLENT: 4,
    Classification.BEST: 5,
    Classification.CRITICAL: 6,
    Classification.BRILLIANT: 7,
    Classification.GREAT_FIND: 8,
    # Special classifications (not in ordering)
    Classification.FORCED: 100,
    Classification.BOOK: 100,
    Classification.CHECKMATE: 100,
}


@dataclass
class MoveClassificationResult:
    """
    Result of move classification including primary classification
    and additional tags like missed opportunity.
    """
    classification: Classification
    is_missed_opportunity: bool = False

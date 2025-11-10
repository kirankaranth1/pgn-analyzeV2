"""Core type definitions and enums."""

from enum import Enum
from typing import Literal


class Classification(Enum):
    """Move classification types."""
    BRILLIANT = "brilliant"
    CRITICAL = "critical"
    BEST = "best"
    EXCELLENT = "excellent"
    OKAY = "okay"
    INACCURACY = "inaccuracy"
    MISTAKE = "mistake"
    BLUNDER = "blunder"
    THEORY = "theory"
    FORCED = "forced"
    RISKY = "risky"


class PieceColor(Enum):
    """Chess piece colors."""
    WHITE = "white"
    BLACK = "black"


# Type aliases for clarity
PieceType = Literal["p", "n", "b", "r", "q", "k"]
Square = str  # e.g., "e4", "a1"


# Classification values for comparison
CLASSIFICATION_VALUES = {
    Classification.BLUNDER: 0,
    Classification.MISTAKE: 1,
    Classification.INACCURACY: 2,
    Classification.RISKY: 2,
    Classification.OKAY: 3,
    Classification.EXCELLENT: 4,
    Classification.BEST: 5,
    Classification.CRITICAL: 5,
    Classification.BRILLIANT: 5,
    Classification.FORCED: 5,
    Classification.THEORY: 5
}


# NAG (Numeric Annotation Glyph) codes for PGN
CLASSIFICATION_NAGS = {
    Classification.BRILLIANT: "$3",    # !!
    Classification.CRITICAL: "$1",     # !
    Classification.INACCURACY: "$6",   # ?!
    Classification.MISTAKE: "$2",      # ?
    Classification.BLUNDER: "$4",      # ??
    Classification.RISKY: "$5"         # !?
}


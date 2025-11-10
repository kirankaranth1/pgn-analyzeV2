"""Constants and configuration values from architecture documentation."""

import math

# ============================================================================
# Classification Thresholds (from 10-constants-config.md)
# ============================================================================

# Point loss thresholds for classifications
POINT_LOSS_THRESHOLDS = {
    "BEST": 0.01,         # < 1% win probability loss
    "EXCELLENT": 0.045,   # < 4.5%
    "OKAY": 0.08,         # < 8%
    "INACCURACY": 0.12,   # < 12%
    "MISTAKE": 0.22,      # < 22%
    # BLUNDER: >= 0.22    # >= 22%
}

# Special thresholds
CRITICAL_THRESHOLD = 0.10           # 10% loss for second-best move
COMPLETELY_WINNING = 700            # +7.00 centipawns


# ============================================================================
# Formulas (from 10-constants-config.md)
# ============================================================================

# Expected points calculation
CENTIPAWN_GRADIENT = 0.0035


def get_expected_points(evaluation_value: int, evaluation_type: str) -> float:
    """Calculate expected points from evaluation.
    
    Args:
        evaluation_value: Evaluation value (centipawns or mate moves)
        evaluation_type: "centipawn" or "mate"
    
    Returns:
        Expected points (0.0 to 1.0)
    """
    if evaluation_type == "mate":
        return 1.0 if evaluation_value > 0 else 0.0
    
    # Sigmoid formula: 1 / (1 + e^(-0.0035 × centipawns))
    return 1.0 / (1.0 + math.exp(-CENTIPAWN_GRADIENT * evaluation_value))


# Move accuracy calculation
ACCURACY_MULTIPLIER = 103.16
ACCURACY_OFFSET = -3.17
ACCURACY_EXPONENT = -4


def get_move_accuracy(point_loss: float) -> float:
    """Calculate move accuracy from point loss.
    
    Args:
        point_loss: Point loss (0.0 to 1.0)
    
    Returns:
        Accuracy score (0 to 100)
    """
    accuracy = ACCURACY_MULTIPLIER * math.exp(ACCURACY_EXPONENT * point_loss) + ACCURACY_OFFSET
    return max(0.0, min(100.0, accuracy))


# ============================================================================
# Piece Values (from 10-constants-config.md)
# ============================================================================

PIECE_VALUES = {
    "p": 1,    # Pawn
    "n": 3,    # Knight
    "b": 3,    # Bishop
    "r": 5,    # Rook
    "q": 9,    # Queen
    "k": float('inf')  # King
}


# ============================================================================
# Engine Configuration (from 10-constants-config.md)
# ============================================================================

DEFAULT_ENGINE_CONFIG = {
    "depth": 20,          # Search depth (plies)
    "multi_pv": 2,        # Number of lines
    "threads": 1,         # CPU threads
    "hash": 128,          # Hash table (MB)
}

MINIMUM_ENGINE_REQUIREMENTS = {
    "depth": 15,          # Minimum for reliable classification
    "multi_pv": 2         # Required for CRITICAL classification
}


# ============================================================================
# Analysis Options (from 10-constants-config.md)
# ============================================================================

DEFAULT_ANALYSIS_OPTIONS = {
    "include_theory": True,
    "include_critical": True,
    "include_brilliant": True
}


# ============================================================================
# Performance Limits (from 10-constants-config.md)
# ============================================================================

PERFORMANCE_LIMITS = {
    "max_depth": 50,
    "max_multi_pv": 5,
    "max_game_moves": 500,
    "xray_depth_limit": 10
}


# ============================================================================
# Special Case Thresholds for Point Loss Classification
# ============================================================================

# Mate → Centipawn thresholds
MATE_TO_CP_THRESHOLDS = {
    "EXCELLENT": 800,     # >= +8.00
    "OKAY": 400,          # >= +4.00
    "INACCURACY": 200,    # >= +2.00
    "MISTAKE": 0,         # >= 0
    # BLUNDER: < 0
}

# Mate loss thresholds (for mate → mate transitions)
MATE_LOSS_THRESHOLDS = {
    "BEST": 1,            # Loss 0-1 moves
    "EXCELLENT": 2,       # Loss 1-2 moves
    "OKAY": 7,            # Loss 2-7 moves
    # INACCURACY: >= 7
}

# Centipawn → Mate thresholds
CP_TO_MATE_THRESHOLDS = {
    "BLUNDER": -2,        # Mate in 2 or faster
    "MISTAKE": -5,        # Mate in 3-5
    # INACCURACY: slower mate
}


"""
Data Models Module

Contains all data structures used throughout the classification system.
"""

from .enums import PieceColor, Classification, EngineVersion, CLASSIFICATION_VALUES
from .state_tree import (
    Move,
    Evaluation,
    EngineLine,
    BoardState,
    StateTreeNode
)
from .extracted_nodes import (
    ExtractedPreviousNode,
    ExtractedCurrentNode
)
from .game_analysis import (
    EstimatedRatings,
    GameAnalysis
)

__all__ = [
    # Enums
    "PieceColor",
    "Classification",
    "EngineVersion",
    "CLASSIFICATION_VALUES",
    
    # State Tree
    "Move",
    "Evaluation",
    "EngineLine",
    "BoardState",
    "StateTreeNode",
    
    # Extracted Nodes
    "ExtractedPreviousNode",
    "ExtractedCurrentNode",
    
    # Game Analysis
    "EstimatedRatings",
    "GameAnalysis",
]

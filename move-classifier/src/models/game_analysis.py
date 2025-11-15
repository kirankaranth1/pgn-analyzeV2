"""
Game Analysis Result Structures

Complete analysis results for a chess game.
"""

from dataclasses import dataclass
from typing import Optional

from .state_tree import StateTreeNode


@dataclass
class EstimatedRatings:
    """Estimated player ratings based on move accuracy."""
    
    white: float
    """Estimated Elo rating for White."""
    
    black: float
    """Estimated Elo rating for Black."""


@dataclass
class GameAnalysis:
    """Complete analysis result for a chess game."""
    
    estimated_ratings: EstimatedRatings
    """Estimated player ratings."""
    
    state_tree: StateTreeNode
    """Root of the game state tree."""


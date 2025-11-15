"""
Extracted Node Data Structures

Simplified structures for classification, extracted from state tree nodes.
"""

from typing import Optional, Any
from dataclasses import dataclass

from .state_tree import BoardState, EngineLine, Move, Evaluation


@dataclass
class ExtractedPreviousNode:
    """
    Represents the position BEFORE a move was played.
    
    Used to compare the played move against the best move.
    """
    
    board: Any
    """Chess board object at this position."""
    
    state: BoardState
    """Full state data."""
    
    top_line: EngineLine
    """Best engine line from this position."""
    
    top_move: Move
    """Best move according to engine."""
    
    evaluation: Evaluation
    """Top line evaluation (White's perspective)."""
    
    subjective_evaluation: Evaluation
    """Evaluation from player's perspective."""
    
    second_top_line: Optional[EngineLine] = None
    """Second-best engine line."""
    
    second_top_move: Optional[Move] = None
    """Second-best move."""
    
    second_subjective_evaluation: Optional[Evaluation] = None
    """Second line evaluation (player's perspective)."""
    
    played_move: Optional[Move] = None
    """Move that was actually played."""


@dataclass
class ExtractedCurrentNode:
    """
    Represents the position AFTER a move was played.
    
    Used to evaluate the resulting position.
    """
    
    board: Any
    """Chess board object after move."""
    
    state: BoardState
    """Full state data."""
    
    top_line: EngineLine
    """Best continuation from this position."""
    
    evaluation: Evaluation
    """Position evaluation (White's perspective)."""
    
    subjective_evaluation: Evaluation
    """Evaluation from player's perspective (REQUIRED)."""
    
    played_move: Move
    """Move that was played (REQUIRED)."""
    
    top_move: Optional[Move] = None
    """Best next move from here."""
    
    second_top_line: Optional[EngineLine] = None
    """Second-best continuation."""
    
    second_top_move: Optional[Move] = None
    """Second-best next move."""
    
    second_subjective_evaluation: Optional[Evaluation] = None
    """Second line evaluation (player's perspective)."""


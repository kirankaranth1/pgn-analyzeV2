"""
Extracted Node Data Structures

Simplified structures for classification, extracted from state tree nodes.
Matches JavaScript interfaces from ExtractedNode.ts
"""

from typing import Optional, Any
from dataclasses import dataclass

from .state_tree import BoardState, EngineLine, Move, Evaluation


@dataclass
class ExtractedPreviousNode:
    """
    Represents the position BEFORE a move was played.
    
    Used to compare the played move against the best move.
    Matches JavaScript interface: ExtractedPreviousNode
    """
    
    board: Any
    """Chess board object at this position."""
    
    state: BoardState
    """Full state data."""
    
    top_line: EngineLine
    """Best engine line from this position."""
    
    top_move: Move
    """Best move according to engine (REQUIRED)."""
    
    evaluation: Evaluation
    """Top line evaluation (White's perspective)."""
    
    subjective_evaluation: Optional[Evaluation] = None
    """Evaluation from player's perspective (OPTIONAL for previous node)."""
    
    second_top_line: Optional[EngineLine] = None
    """Second-best engine line."""
    
    second_top_move: Optional[Move] = None
    """Second-best move."""
    
    second_subjective_evaluation: Optional[Evaluation] = None
    """Second line evaluation (player's perspective)."""
    
    played_move: Optional[Move] = None
    """Move that was actually played (OPTIONAL for previous node)."""


@dataclass
class ExtractedCurrentNode:
    """
    Represents the position AFTER a move was played.
    
    Used to evaluate the resulting position.
    Matches JavaScript interface: ExtractedCurrentNode
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
    """Evaluation from player's perspective (REQUIRED for current node)."""
    
    played_move: Move
    """Move that was played (REQUIRED for current node)."""
    
    top_move: Optional[Move] = None
    """Best next move from here (OPTIONAL for current node)."""
    
    second_top_line: Optional[EngineLine] = None
    """Second-best continuation."""
    
    second_top_move: Optional[Move] = None
    """Second-best next move."""
    
    second_subjective_evaluation: Optional[Evaluation] = None
    """Second line evaluation (player's perspective)."""


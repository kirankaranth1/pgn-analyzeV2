"""
State Tree Data Structures

Represents the game as a tree structure with nodes for each position.
"""

from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class Move:
    """Represents a chess move in multiple notations."""
    
    san: str
    """Standard Algebraic Notation (e.g., 'Nf3')."""
    
    uci: str
    """Universal Chess Interface notation (e.g., 'g1f3')."""


@dataclass
class Evaluation:
    """Represents an engine evaluation of a position."""
    
    type: str  # "centipawn" or "mate"
    """Type of evaluation."""
    
    value: float
    """Evaluation value (centipawns or mate moves)."""


@dataclass
class EngineLine:
    """Represents a single engine analysis line (MultiPV)."""
    
    evaluation: Evaluation
    """Position evaluation."""
    
    source: str
    """Engine version (e.g., 'stockfish-17', 'lichess-cloud')."""
    
    depth: int
    """Search depth in plies."""
    
    index: int
    """MultiPV index (1=best, 2=second-best, etc.)."""
    
    moves: List[Move]
    """Principal variation (sequence of best moves)."""


@dataclass
class BoardState:
    """Complete data for a single chess position."""
    
    fen: str
    """Position in Forsyth-Edwards Notation."""
    
    move: Optional[Move] = None
    """Move that created this position."""
    
    move_color: Optional[str] = None
    """Color that played the move ('WHITE' or 'BLACK')."""
    
    engine_lines: List[EngineLine] = field(default_factory=list)
    """Engine analysis lines for this position."""
    
    classification: Optional[str] = None
    """Move quality classification."""
    
    accuracy: Optional[float] = None
    """Move accuracy score (0-100)."""
    
    opening: Optional[str] = None
    """Opening name (if applicable)."""


@dataclass
class StateTreeNode:
    """Represents a single position in the game tree."""
    
    id: str
    """Unique identifier for this node."""
    
    mainline: bool
    """True if part of main game line, False if variation."""
    
    parent: Optional["StateTreeNode"]
    """Previous position (None for root)."""
    
    children: List["StateTreeNode"]
    """Next positions (variations)."""
    
    state: BoardState
    """Position data."""


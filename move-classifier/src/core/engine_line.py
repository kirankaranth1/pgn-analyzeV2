"""Engine analysis line data structure."""

from dataclasses import dataclass
from typing import List
from .evaluation import Evaluation
from .move import Move


@dataclass
class EngineLine:
    """Represents a single engine analysis line (principal variation).
    
    Attributes:
        evaluation: Position evaluation after this line
        source: Engine that produced this line (e.g., "stockfish-17")
        depth: Search depth in plies
        index: Line ranking (1 = best, 2 = second-best, etc.)
        moves: Sequence of moves in this variation
    """
    evaluation: Evaluation
    source: str
    depth: int
    index: int
    moves: List[Move]
    
    def get_first_move(self) -> Move:
        """Get the first move of this line."""
        if not self.moves:
            raise ValueError("Engine line has no moves")
        return self.moves[0]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "evaluation": self.evaluation.to_dict(),
            "source": self.source,
            "depth": self.depth,
            "index": self.index,
            "moves": [move.to_dict() for move in self.moves]
        }


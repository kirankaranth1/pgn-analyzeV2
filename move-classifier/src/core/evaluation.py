"""Evaluation data structures."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class Evaluation:
    """Chess position evaluation from engine.
    
    Attributes:
        type: Either "centipawn" or "mate"
        value: For centipawn - evaluation in centipawns (positive = white advantage)
               For mate - number of moves until mate (positive = white mates, negative = black mates)
    """
    type: Literal["centipawn", "mate"]
    value: int
    
    def __str__(self) -> str:
        if self.type == "centipawn":
            return f"{self.value / 100:+.2f}"
        else:
            sign = "+" if self.value > 0 else ""
            return f"M{sign}{self.value}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Evaluation":
        """Create from dictionary."""
        return cls(type=data["type"], value=data["value"])


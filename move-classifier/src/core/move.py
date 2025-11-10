"""Chess move data structure."""

from dataclasses import dataclass
from typing import Optional
from .types import PieceType, PieceColor, Square


@dataclass
class Move:
    """Represents a chess move.
    
    Attributes:
        san: Standard Algebraic Notation (e.g., "Nf3", "e4")
        uci: UCI notation (e.g., "g1f3", "e2e4")
        from_square: Starting square
        to_square: Ending square
        piece: Type of piece moved
        color: Color of piece moved
        captured: Type of piece captured (if any)
        promotion: Type of piece promoted to (if any)
        flags: Move flags (capture, check, etc.)
    """
    san: str
    uci: str
    from_square: Square
    to_square: Square
    piece: PieceType
    color: PieceColor
    captured: Optional[PieceType] = None
    promotion: Optional[PieceType] = None
    flags: str = ""
    
    def is_capture(self) -> bool:
        """Check if move is a capture."""
        return self.captured is not None or "x" in self.san
    
    def is_promotion(self) -> bool:
        """Check if move is a promotion."""
        return self.promotion is not None or "=" in self.san
    
    def is_castling(self) -> bool:
        """Check if move is castling."""
        return "O-O" in self.san or "0-0" in self.san
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "san": self.san,
            "uci": self.uci,
            "from": self.from_square,
            "to": self.to_square,
            "piece": self.piece,
            "color": self.color.value,
            "captured": self.captured,
            "promotion": self.promotion,
            "flags": self.flags
        }


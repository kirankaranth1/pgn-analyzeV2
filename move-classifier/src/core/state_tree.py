"""State tree data structures for game representation."""

from dataclasses import dataclass, field
from typing import Optional, List
from .move import Move
from .engine_line import EngineLine
from .types import Classification, PieceColor


@dataclass
class BoardState:
    """Represents the complete state of a chess position.
    
    Attributes:
        fen: Forsyth-Edwards Notation of the position
        move: Move that led to this position (None for starting position)
        engine_lines: Engine analysis lines for this position
        classification: Move classification (if analyzed)
        accuracy: Move accuracy score 0-100 (if analyzed)
        opening: Opening name (if in opening book)
        move_color: Color of the player who made the move
    """
    fen: str
    move: Optional[Move] = None
    engine_lines: List[EngineLine] = field(default_factory=list)
    classification: Optional[Classification] = None
    accuracy: Optional[float] = None
    opening: Optional[str] = None
    move_color: Optional[PieceColor] = None
    
    def get_top_line(self) -> Optional[EngineLine]:
        """Get the top engine line (index 1)."""
        for line in self.engine_lines:
            if line.index == 1:
                return line
        return None
    
    def get_second_line(self) -> Optional[EngineLine]:
        """Get the second-best engine line (index 2)."""
        for line in self.engine_lines:
            if line.index == 2:
                return line
        return None


@dataclass
class StateTreeNode:
    """Node in the game state tree.
    
    Attributes:
        id: Unique identifier for this node
        state: Board state at this position
        parent: Parent node (previous position)
        children: Child nodes (next positions/variations)
        mainline: Whether this node is part of the main line
    """
    id: str
    state: BoardState
    parent: Optional["StateTreeNode"] = None
    children: List["StateTreeNode"] = field(default_factory=list)
    mainline: bool = True
    
    def add_child(self, child: "StateTreeNode") -> None:
        """Add a child node."""
        child.parent = self
        self.children.append(child)
    
    def get_mainline_child(self) -> Optional["StateTreeNode"]:
        """Get the mainline child node."""
        for child in self.children:
            if child.mainline:
                return child
        return None
    
    def traverse_mainline(self) -> List["StateTreeNode"]:
        """Get all nodes in the mainline from this node forward."""
        nodes = []
        current = self
        while current is not None:
            if current.mainline:
                nodes.append(current)
            current = current.get_mainline_child()
        return nodes


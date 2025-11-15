"""
Basic Classifications

Handles simple classification rules including:
- FORCED: Only one legal move available
- THEORY: Position is in opening book
- CHECKMATE → BEST: Move delivers checkmate
"""

import json
import os
import chess
from typing import Optional, Dict, Union
from pathlib import Path

from ..models.enums import Classification
from ..models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from ..models.state_tree import StateTreeNode


class OpeningBook:
    """
    Opening book database for THEORY classification.
    
    Maps piece placements (first part of FEN) to opening names.
    """
    
    def __init__(self, openings_file: Optional[str] = None):
        """
        Initialize opening book from JSON file.
        
        Args:
            openings_file: Path to openings.json. If None, uses default.
        """
        if openings_file is None:
            # Default path: src/resources/openings.json
            module_dir = Path(__file__).parent.parent
            openings_file = module_dir / "resources" / "openings.json"
        
        self._openings: Dict[str, str] = {}
        self._load_openings(openings_file)
    
    def _load_openings(self, file_path: Path) -> None:
        """Load openings from JSON file."""
        try:
            with open(file_path, 'r') as f:
                self._openings = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Opening book not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in opening book: {e}")
    
    def get_opening_name(self, fen: str) -> Optional[str]:
        """
        Get opening name for a position.
        
        Args:
            fen: Full FEN string
            
        Returns:
            Opening name if found, None otherwise
        """
        # Extract piece placement (before first space)
        piece_placement = fen.split(" ")[0]
        return self._openings.get(piece_placement)
    
    @property
    def size(self) -> int:
        """Number of positions in the opening book."""
        return len(self._openings)


class BasicClassifier:
    """
    Handles basic move classifications.
    
    Checks in priority order:
    1. FORCED - only one legal move
    2. THEORY - position in opening book
    3. CHECKMATE → BEST - move delivers checkmate
    """
    
    def __init__(self, opening_book: Optional[OpeningBook] = None, include_theory: bool = True):
        """
        Initialize basic classifier.
        
        Args:
            opening_book: Opening book instance. If None, creates default.
            include_theory: Whether to check for THEORY classification.
        """
        self._opening_book = opening_book if opening_book is not None else OpeningBook()
        self._include_theory = include_theory
    
    def classify(
        self,
        previous_node: ExtractedPreviousNode,
        current_node: ExtractedCurrentNode
    ) -> Optional[Classification]:
        """
        Classify a move using basic rules.
        
        Checks in priority order:
        1. FORCED
        2. THEORY
        3. CHECKMATE → BEST
        
        Args:
            previous_node: Position before the move
            current_node: Position after the move
            
        Returns:
            Classification if rule applies, None otherwise
        """
        # Priority 1: FORCED
        forced = self._classify_forced(previous_node)
        if forced is not None:
            return forced
        
        # Priority 2: THEORY
        theory = self._classify_theory(current_node)
        if theory is not None:
            return theory
        
        # Priority 3: CHECKMATE → BEST
        checkmate = self._classify_checkmate(current_node)
        if checkmate is not None:
            return checkmate
        
        # No basic classification applies
        return None
    
    def classify_from_state_tree_node(
        self,
        node: StateTreeNode
    ) -> Optional[Classification]:
        """
        Classify a move directly from a StateTreeNode.
        
        This is useful for terminal positions (e.g., checkmate) where
        engine analysis may not be available, preventing extraction.
        
        Only checks classifications that don't require extracted nodes:
        - THEORY (uses FEN and state)
        - CHECKMATE → BEST (uses board state)
        
        Args:
            node: State tree node (position after the move)
            
        Returns:
            Classification if rule applies, None otherwise
        """
        if not node.state.move:
            return None
        
        # Check THEORY (doesn't need engine data)
        fen = node.state.fen
        opening_name = self._opening_book.get_opening_name(fen)
        
        if self._include_theory and opening_name is not None:
            # Store opening name in the node state
            node.state.opening = opening_name
            return Classification.BOOK
        
        # Check CHECKMATE (doesn't need engine data)
        board = chess.Board(node.state.fen)
        if board.is_checkmate():
            return Classification.BEST
        
        # Note: FORCED cannot be checked without the previous node's board state
        # which requires extraction. Return None to indicate further analysis needed.
        return None
    
    def _classify_forced(self, previous_node: ExtractedPreviousNode) -> Optional[Classification]:
        """
        Check if move is FORCED (only one legal move).
        
        Args:
            previous_node: Position before the move
            
        Returns:
            Classification.FORCED if only one legal move, None otherwise
        """
        board = previous_node.board
        legal_moves = list(board.legal_moves)
        
        # <= 1 handles both 0 (stalemate/checkmate) and 1 (forced)
        if len(legal_moves) <= 1:
            return Classification.FORCED
        
        return None
    
    def _classify_theory(self, current_node: ExtractedCurrentNode) -> Optional[Classification]:
        """
        Check if move is THEORY (in opening book).
        
        Args:
            current_node: Position after the move
            
        Returns:
            Classification.BOOK if position in opening book, None otherwise
        """
        if not self._include_theory:
            return None
        
        fen = current_node.state.fen
        opening_name = self._opening_book.get_opening_name(fen)
        
        if opening_name is not None:
            # Store opening name in the node state
            current_node.state.opening = opening_name
            return Classification.BOOK
        
        return None
    
    def _classify_checkmate(self, current_node: ExtractedCurrentNode) -> Optional[Classification]:
        """
        Check if move delivers checkmate.
        
        Args:
            current_node: Position after the move
            
        Returns:
            Classification.BEST if checkmate delivered, None otherwise
        """
        board = current_node.board
        
        if board.is_checkmate():
            return Classification.BEST
        
        return None
    
    @property
    def opening_book_size(self) -> int:
        """Number of positions in the opening book."""
        return self._opening_book.size
    
    def set_include_theory(self, include_theory: bool) -> None:
        """
        Enable or disable THEORY classification.
        
        Args:
            include_theory: Whether to check for THEORY
        """
        self._include_theory = include_theory


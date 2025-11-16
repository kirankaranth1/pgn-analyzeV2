"""
Main Classification Engine

Orchestrates the classification process, coordinating all classification logic
and determining move quality based on extracted node data.

Matches JavaScript implementation from classification/classify.ts
"""

from typing import Optional

from ..models.state_tree import StateTreeNode
from ..models.enums import Classification, CLASSIFICATION_VALUES
from ..config import ClassificationConfig
from ..preprocessing.node_extractor import (
    extract_previous_state_tree_node,
    extract_current_state_tree_node
)
from ..classification.basic_classifier import OpeningBook


# Stub functions for advanced classifiers (to be implemented)
def _point_loss_classify(previous_node, current_node) -> Classification:
    """
    Classify move based on point loss (evaluation drop).
    
    TODO: Implement point loss classification logic
    
    Args:
        previous_node: Position before move
        current_node: Position after move
        
    Returns:
        Classification based on point loss
    """
    # Stub: Return GOOD as default
    return Classification.GOOD


def _consider_brilliant_classification(previous_node, current_node) -> bool:
    """
    Check if move qualifies as BRILLIANT.
    
    TODO: Implement brilliant classification logic
    
    Args:
        previous_node: Position before move
        current_node: Position after move
        
    Returns:
        True if move should be classified as BRILLIANT
    """
    # Stub: Never mark as brilliant yet
    return False


def _consider_critical_classification(previous_node, current_node) -> bool:
    """
    Check if move qualifies as CRITICAL (only move).
    
    TODO: Implement critical classification logic
    
    Args:
        previous_node: Position before move
        current_node: Position after move
        
    Returns:
        True if move should be classified as CRITICAL
    """
    # Stub: Never mark as critical yet
    return False


class Classifier:
    """
    Main classification engine that orchestrates the classification process.
    
    Matches JavaScript classify() function logic.
    """
    
    def __init__(
        self,
        opening_book: Optional[OpeningBook] = None,
        config: Optional[ClassificationConfig] = None
    ):
        """
        Initialize classifier.
        
        Args:
            opening_book: Opening book for THEORY classification
            config: Classification configuration
        """
        self._opening_book = opening_book if opening_book is not None else OpeningBook()
        self._config = config if config is not None else ClassificationConfig()
    
    def classify(
        self,
        node: StateTreeNode,
        config: Optional[ClassificationConfig] = None
    ) -> Classification:
        """
        Classify a move based on position analysis.
        
        Matches JavaScript classify() function.
        
        Args:
            node: State tree node (position after the move)
            config: Optional override configuration
            
        Returns:
            Classification for the move
            
        Raises:
            ValueError: If node has no parent or extraction fails
        """
        # Validate node has parent
        if not node.parent:
            raise ValueError("no parent node exists to compare with.")
        
        # Extract both previous and current nodes
        previous = extract_previous_state_tree_node(node.parent)
        current = extract_current_state_tree_node(node)
        
        if not previous or not current:
            raise ValueError("information missing from current or previous node.")
        
        # Use provided config or default
        opts = config if config is not None else self._config
        
        # Priority 1: FORCED - only one legal move
        if len(list(previous.board.legal_moves)) <= 1:
            return Classification.FORCED
        
        # Priority 2: THEORY - position in opening book
        if opts.include_theory:
            opening_name = self._opening_book.get_opening_name(current.state.fen)
            if opening_name:
                # Store opening name in state
                current.state.opening = opening_name
                return Classification.BOOK
        
        # Priority 3: CHECKMATE → BEST
        if current.board.is_checkmate():
            return Classification.BEST
        
        # Check if top move was played
        top_move_played = previous.top_move.uci() == current.played_move.uci()
        
        # Point loss classification
        classification = (
            Classification.BEST
            if top_move_played
            else _point_loss_classify(previous, current)
        )
        
        # Consider CRITICAL classification (only if top move was played)
        if (
            opts.include_critical
            and top_move_played
            and _consider_critical_classification(previous, current)
        ):
            classification = Classification.CRITICAL
        
        # Consider BRILLIANT classification (only if classification is BEST or better)
        if (
            opts.include_brilliant
            and CLASSIFICATION_VALUES.get(classification, 0) >= CLASSIFICATION_VALUES[Classification.BEST]
            and _consider_brilliant_classification(previous, current)
        ):
            classification = Classification.BRILLIANT
        
        return classification
    
    def classify_with_fallback(
        self,
        node: StateTreeNode,
        config: Optional[ClassificationConfig] = None
    ) -> Optional[Classification]:
        """
        Classify a move with error handling (returns None instead of raising).
        
        Args:
            node: State tree node
            config: Optional classification configuration
            
        Returns:
            Classification or None if classification fails
        """
        try:
            return self.classify(node, config)
        except (ValueError, AttributeError):
            return None


def classify_node(
    node: StateTreeNode,
    opening_book: Optional[OpeningBook] = None,
    config: Optional[ClassificationConfig] = None
) -> Classification:
    """
    Convenience function to classify a single node.
    
    Args:
        node: State tree node
        opening_book: Optional opening book
        config: Optional classification configuration
        
    Returns:
        Classification for the move
    """
    classifier = Classifier(opening_book=opening_book, config=config)
    return classifier.classify(node, config)

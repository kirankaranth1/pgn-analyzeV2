"""
Main Classification Engine

Orchestrates the classification process, coordinating all classification logic
and determining move quality based on extracted node data.

Matches JavaScript implementation from classification/classify.ts
"""

from typing import Optional

from ..models.state_tree import StateTreeNode
from ..models.enums import Classification, CLASSIFICATION_VALUES, MoveClassificationResult
from ..config import ClassificationConfig
from ..preprocessing.node_extractor import (
    extract_previous_state_tree_node,
    extract_current_state_tree_node
)
from ..classification.basic_classifier import OpeningBook
from ..classification.point_loss_classifier import point_loss_classify
from ..classification.critical_classifier import consider_critical_classification
from ..classification.brilliant_classifier import consider_brilliant_classification
from ..classification.missed_opportunity_classifier import consider_missed_opportunity_classification


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
        self._last_classification: Optional[Classification] = None
    
    def classify(
        self,
        node: StateTreeNode,
        config: Optional[ClassificationConfig] = None
    ) -> MoveClassificationResult:
        """
        Classify a move based on position analysis.
        
        Matches JavaScript classify() function.
        
        Args:
            node: State tree node (position after the move)
            config: Optional override configuration
            
        Returns:
            MoveClassificationResult with classification and missed opportunity flag
            
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
            classification = Classification.FORCED
            result = MoveClassificationResult(classification=classification)
            self._last_classification = classification
            return result
        
        # Priority 2: THEORY - position in opening book
        if opts.include_theory:
            opening_name = self._opening_book.get_opening_name(current.state.fen)
            if opening_name:
                # Store opening name in state
                current.state.opening = opening_name
                classification = Classification.BOOK
                result = MoveClassificationResult(classification=classification)
                self._last_classification = classification
                return result
        
        # Priority 3: CHECKMATE → BEST
        if current.board.is_checkmate():
            classification = Classification.BEST
            result = MoveClassificationResult(classification=classification)
            self._last_classification = classification
            return result
        
        # Check if top move was played
        top_move_played = previous.top_move.uci() == current.played_move.uci()
        
        # Point loss classification
        classification = (
            Classification.BEST
            if top_move_played
            else point_loss_classify(previous, current)
        )
        
        # Consider CRITICAL classification (only if top move was played)
        if (
            opts.include_critical
            and top_move_played
            and consider_critical_classification(previous, current)
        ):
            classification = Classification.CRITICAL
        
        # Consider BRILLIANT classification (only if classification is BEST or better)
        if (
            opts.include_brilliant
            and CLASSIFICATION_VALUES.get(classification, 0) >= CLASSIFICATION_VALUES[Classification.BEST]
            and consider_brilliant_classification(previous, current)
        ):
            classification = Classification.BRILLIANT
        
        # Check for missed opportunity (if enabled)
        is_missed_opportunity = False
        if opts.include_missed_opportunity and self._last_classification:
            is_missed_opportunity = consider_missed_opportunity_classification(
                node,
                classification,
                self._last_classification
            )
        
        # Update last classification for next move
        self._last_classification = classification
        
        return MoveClassificationResult(
            classification=classification,
            is_missed_opportunity=is_missed_opportunity
        )
    
    def classify_with_fallback(
        self,
        node: StateTreeNode,
        config: Optional[ClassificationConfig] = None
    ) -> Optional[MoveClassificationResult]:
        """
        Classify a move with error handling (returns None instead of raising).
        
        Args:
            node: State tree node
            config: Optional classification configuration
            
        Returns:
            MoveClassificationResult or None if classification fails
        """
        try:
            return self.classify(node, config)
        except (ValueError, AttributeError):
            return None


def classify_node(
    node: StateTreeNode,
    opening_book: Optional[OpeningBook] = None,
    config: Optional[ClassificationConfig] = None
) -> MoveClassificationResult:
    """
    Convenience function to classify a single node.
    
    Args:
        node: State tree node
        opening_book: Optional opening book
        config: Optional classification configuration
        
    Returns:
        MoveClassificationResult with classification and missed opportunity flag
    """
    classifier = Classifier(opening_book=opening_book, config=config)
    return classifier.classify(node, config)

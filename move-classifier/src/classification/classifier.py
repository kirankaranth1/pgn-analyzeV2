"""Main classification orchestrator with waterfall logic."""

from dataclasses import dataclass
from typing import Optional, Tuple
from ..core.types import Classification
from ..core.state_tree import StateTreeNode
from ..utils.opening_book import OpeningBook
from .node_extractor import NodeExtractor, ExtractedPreviousNode, ExtractedCurrentNode
from .forced import classify_forced
from .theory import classify_theory, get_opening_name
from .checkmate import classify_checkmate
from .point_loss import classify_by_point_loss, calculate_accuracy
from .critical import classify_critical
from .brilliant import classify_brilliant


@dataclass
class AnalysisOptions:
    """Options for move classification.
    
    Attributes:
        include_theory: Enable THEORY classification
        include_critical: Enable CRITICAL classification
        include_brilliant: Enable BRILLIANT classification
    """
    include_theory: bool = True
    include_critical: bool = True
    include_brilliant: bool = True


class MoveClassifier:
    """Main move classifier using waterfall logic."""
    
    def __init__(self, opening_book: OpeningBook, options: Optional[AnalysisOptions] = None):
        """Initialize classifier.
        
        Args:
            opening_book: Opening book for THEORY classification
            options: Analysis options
        """
        self.opening_book = opening_book
        self.options = options or AnalysisOptions()
        self.extractor = NodeExtractor()
    
    def classify_move(
        self,
        node: StateTreeNode
    ) -> Tuple[Optional[Classification], Optional[float], Optional[str]]:
        """Classify a move using waterfall logic.
        
        Priority order:
        1. FORCED (only legal move)
        2. THEORY (opening book)
        3. CHECKMATE (delivers mate)
        4. Point Loss (BEST/EXCELLENT/OKAY/INACCURACY/MISTAKE/BLUNDER)
        5. CRITICAL (refines BEST)
        6. BRILLIANT (refines BEST+)
        
        Args:
            node: State tree node to classify
            
        Returns:
            Tuple of (classification, accuracy, opening_name)
        """
        # Check for checkmate first (before node extraction which requires engine lines)
        import chess
        board = chess.Board(node.state.fen)
        if board.is_checkmate():
            return Classification.BEST, 100.0, None
        
        # Extract nodes
        previous = self.extractor.extract_previous_node(node)
        current = self.extractor.extract_current_node(node)
        
        if not previous or not current:
            return None, None, None
        
        # Priority 1: FORCED
        classification = classify_forced(previous)
        if classification:
            accuracy = 100.0  # Forced moves get perfect accuracy
            return classification, accuracy, None
        
        # Priority 2: THEORY
        opening_name = None
        if self.options.include_theory:
            classification = classify_theory(current, self.opening_book)
            if classification:
                accuracy = 100.0  # Theory moves get perfect accuracy
                opening_name = get_opening_name(current, self.opening_book)
                return classification, accuracy, opening_name
        
        # Priority 3: CHECKMATE
        classification = classify_checkmate(current)
        if classification:
            accuracy = 100.0  # Checkmate gets perfect accuracy
            return classification, accuracy, opening_name
        
        # Priority 4: Point Loss
        classification = classify_by_point_loss(previous, current)
        
        # Calculate accuracy (BEST moves get 100%)
        if classification == Classification.BEST:
            accuracy = 100.0
        else:
            accuracy = calculate_accuracy(previous, current)
        
        # Priority 5: CRITICAL (refines BEST)
        if self.options.include_critical and classification == Classification.BEST:
            critical = classify_critical(previous, current)
            if critical:
                classification = critical
        
        # Priority 6: BRILLIANT (refines BEST+)
        if self.options.include_brilliant:
            brilliant = classify_brilliant(previous, current, classification)
            if brilliant:
                classification = brilliant
        
        return classification, accuracy, opening_name


"""
Stage 5: Calculate Derived Values

Computes derived metrics including:
- Subjective evaluations (player perspective)
- Expected points (win probability)
- Expected points loss
- Move accuracy

Note: Most calculation functions are in utils/evaluation_utils.py
This module provides the Stage 5 interface for applying calculations.
"""

from typing import Optional, Tuple

from ..models.state_tree import StateTreeNode
from ..models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from ..models.enums import PieceColor
from ..utils.evaluation_utils import (
    get_expected_points,
    get_expected_points_loss,
    get_move_accuracy,
    get_subjective_evaluation
)
from ..preprocessing.node_extractor import (
    extract_previous_state_tree_node,
    extract_current_state_tree_node
)


def calculate_move_metrics(
    previous_node: ExtractedPreviousNode,
    current_node: ExtractedCurrentNode
) -> Tuple[float, float]:
    """
    Calculate expected points loss and accuracy for a move.
    
    Args:
        previous_node: Position before the move
        current_node: Position after the move
        
    Returns:
        Tuple of (point_loss, accuracy)
    """
    # Determine move color from board turn (before move was played)
    # The current node has the position after the move, so we use previous node's board
    player_color_bool = previous_node.board.turn
    player_color = PieceColor.WHITE if player_color_bool else PieceColor.BLACK
    
    # Calculate point loss
    point_loss = get_expected_points_loss(
        previous_node.evaluation,
        current_node.evaluation,
        player_color
    )
    
    # Calculate accuracy
    accuracy = get_move_accuracy(
        previous_node.evaluation,
        current_node.evaluation,
        player_color
    )
    
    return point_loss, accuracy


def apply_calculations_to_node(
    node: StateTreeNode,
    previous_node: Optional[ExtractedPreviousNode] = None,
    current_node: Optional[ExtractedCurrentNode] = None
) -> None:
    """
    Apply derived calculations to a state tree node.
    
    Calculates and stores accuracy in the node's state.
    
    Args:
        node: State tree node to update
        previous_node: Extracted previous node (will extract if None)
        current_node: Extracted current node (will extract if None)
    """
    # Extract nodes if not provided
    if current_node is None:
        current_node = extract_current_state_tree_node(node)
    
    if current_node is None:
        return  # Cannot calculate without current node
    
    if previous_node is None and node.parent:
        previous_node = extract_previous_state_tree_node(node.parent)
    
    if previous_node is None:
        return  # Cannot calculate without previous node
    
    # Calculate metrics
    _, accuracy = calculate_move_metrics(previous_node, current_node)
    
    # Store in node state
    node.state.accuracy = accuracy


def calculate_expected_points_for_evaluation(
    evaluation,
    player_color: Optional[PieceColor] = None
) -> float:
    """
    Calculate expected points for an evaluation.
    
    Args:
        evaluation: Evaluation object
        player_color: If provided, adjusts from player's perspective
        
    Returns:
        Expected points (0.0 to 1.0)
    """
    if player_color is None:
        # Return from White's perspective
        return get_expected_points(evaluation)
    else:
        # Get subjective evaluation first, then calculate expected points
        subjective_eval = get_subjective_evaluation(evaluation, player_color)
        return get_expected_points(subjective_eval, move_colour=player_color)

"""
Preprocessing Pipeline Module

This module contains the 5-stage preprocessing pipeline that transforms
raw game data (PGN) into classification-ready data structures.

Stages:
    1. Parse Game into State Tree
    2. Engine Analysis
    3. Build Node Chain
    4. Extract Nodes
    5. Calculate Derived Values
"""

from typing import Optional, List, Tuple

from ..models.state_tree import StateTreeNode
from ..models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from ..config import EngineConfig

from .parser import parse_pgn_game
from .engine_analyzer import analyze_state_tree
from .node_chain_builder import get_node_chain
from .node_extractor import (
    extract_previous_state_tree_node,
    extract_current_state_tree_node
)
from .calculator import calculate_move_metrics, apply_calculations_to_node


def run_full_preprocessing_pipeline(
    pgn: str,
    initial_position: Optional[str] = None,
    config: Optional[EngineConfig] = None
) -> StateTreeNode:
    """
    Run the complete 5-stage preprocessing pipeline.
    
    Stages:
        1. Parse PGN to State Tree
        2. Analyze with engine (cloud + local)
        3. Build node chain
        4. Extract nodes
        5. Calculate derived values
    
    Args:
        pgn: PGN string (e.g., "1. e4 e5 2. Nf3")
        initial_position: Optional starting FEN
        config: Engine configuration (uses defaults if None)
        
    Returns:
        Root node of the analyzed state tree
        
    Example:
        >>> root = run_full_preprocessing_pipeline("1. e4 e5 2. Nf3")
        >>> # Root node now has complete analysis ready for classification
    """
    if config is None:
        config = EngineConfig()
    
    # Stage 1: Parse PGN to State Tree
    root_node = parse_pgn_game(pgn, initial_position)
    
    # Stage 2: Engine Analysis
    analyze_state_tree(root_node, config)
    
    # Stage 3: Build Node Chain (for iteration)
    nodes = get_node_chain(root_node, expand_all_variations=False)
    
    # Stage 4 & 5: Extract and Calculate for each node
    for i in range(1, len(nodes)):  # Skip root
        node = nodes[i]
        parent = nodes[i - 1]
        
        # Extract nodes
        previous_node = extract_previous_state_tree_node(parent)
        current_node = extract_current_state_tree_node(node)
        
        # Calculate and apply metrics
        if previous_node and current_node:
            apply_calculations_to_node(node, previous_node, current_node)
    
    return root_node


def extract_node_pair(
    node: StateTreeNode
) -> Optional[Tuple[ExtractedPreviousNode, ExtractedCurrentNode]]:
    """
    Extract both previous and current nodes for a position.
    
    Args:
        node: State tree node
        
    Returns:
        Tuple of (previous, current) or None if extraction fails
    """
    if not node.parent:
        return None
    
    previous_node = extract_previous_state_tree_node(node.parent)
    current_node = extract_current_state_tree_node(node)
    
    if previous_node and current_node:
        return (previous_node, current_node)
    
    return None


__all__ = [
    "parse_pgn_game",
    "analyze_state_tree",
    "get_node_chain",
    "extract_previous_state_tree_node",
    "extract_current_state_tree_node",
    "calculate_move_metrics",
    "apply_calculations_to_node",
    "run_full_preprocessing_pipeline",
    "extract_node_pair",
]


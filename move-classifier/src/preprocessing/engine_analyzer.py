"""
Stage 2: Engine Analysis

Populates engine evaluations for each position in the state tree
using either cloud evaluation (Lichess API) or local engine (Stockfish UCI).
"""

from typing import Optional, List
import logging

from ..models.state_tree import StateTreeNode
from ..config import EngineConfig
from ..engine.cloud_evaluator import get_cloud_evaluation
from ..engine.uci_engine import UCIEngine
from ..models.enums import EngineVersion


# Set up logging
logger = logging.getLogger(__name__)


def analyze_state_tree(
    root_node: StateTreeNode,
    config: Optional[EngineConfig] = None
) -> None:
    """
    Analyze all positions in the state tree with engine evaluation.
    
    Tries cloud evaluation first (if enabled), falls back to local engine.
    
    Args:
        root_node: Root of the state tree
        config: Engine configuration (uses defaults if None)
    """
    if config is None:
        config = EngineConfig()
    
    # Get all nodes in a chain
    from ..preprocessing.node_chain_builder import get_node_chain
    nodes = get_node_chain(root_node, expand_all_variations=False)
    
    # Initialize local engine (will be used if cloud fails)
    local_engine = None
    
    try:
        for node in nodes:
            # Skip if already has engine lines
            if node.state.engine_lines:
                continue
            
            success = False
            
            # Try cloud evaluation first (if enabled)
            if config.use_cloud_eval:
                try:
                    engine_lines = get_cloud_evaluation(
                        node.state.fen,
                        multi_pv=config.multi_pv
                    )
                    if engine_lines:
                        node.state.engine_lines.extend(engine_lines)
                        success = True
                        logger.debug(f"Cloud evaluation successful for position: {node.id}")
                except Exception as e:
                    logger.debug(f"Cloud evaluation failed: {e}, falling back to local engine")
            
            # Fall back to local engine if cloud failed or disabled
            if not success:
                if local_engine is None:
                    # Initialize engine on first use
                    local_engine = UCIEngine(
                        engine_path=config.stockfish_path,
                        version=EngineVersion.STOCKFISH_17
                    )
                
                # Evaluate with local engine
                local_engine.set_position(node.state.fen)
                engine_lines = local_engine.evaluate(
                    depth=config.depth,
                    multi_pv=config.multi_pv,
                    time_limit=config.time_limit
                )
                
                if engine_lines:
                    node.state.engine_lines.extend(engine_lines)
                    logger.debug(f"Local engine evaluation successful for position: {node.id}")
    
    finally:
        # Clean up local engine
        if local_engine:
            local_engine.terminate()


def get_top_engine_line(node: StateTreeNode):
    """
    Get the best engine line for a position.
    
    When multiple engine lines exist (different depths/sources),
    selects the one with highest depth and lowest index.
    
    Args:
        node: State tree node
        
    Returns:
        Best EngineLine or None if no lines available
    """
    if not node.state.engine_lines:
        return None
    
    # Sort by depth (descending) then index (ascending)
    sorted_lines = sorted(
        node.state.engine_lines,
        key=lambda line: (-line.depth, line.index)
    )
    
    return sorted_lines[0] if sorted_lines else None


def get_line_group_sibling(
    lines: List,
    reference_line,
    target_index: int
):
    """
    Find a line with same depth and source but different index.
    
    Args:
        lines: List of engine lines
        reference_line: Reference engine line
        target_index: Desired MultiPV index
        
    Returns:
        EngineLine or None
    """
    for line in lines:
        if (line.depth == reference_line.depth and
            line.source == reference_line.source and
            line.index == target_index):
            return line
    return None

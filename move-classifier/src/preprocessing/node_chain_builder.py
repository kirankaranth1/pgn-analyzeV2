"""
Stage 3: Build Node Chain

Converts the tree structure into a linear array for sequential processing.
Supports both mainline-only and full variation expansion.
"""

from typing import List

from ..models.state_tree import StateTreeNode


def get_node_chain(
    root_node: StateTreeNode,
    expand_all_variations: bool = False
) -> List[StateTreeNode]:
    """
    Convert state tree to linear array of nodes.
    
    Args:
        root_node: Root of the state tree
        expand_all_variations: If True, include all variations.
                               If False, only follow mainline.
        
    Returns:
        List of state tree nodes in order
    """
    chain: List[StateTreeNode] = []
    frontier: List[StateTreeNode] = [root_node]
    
    while frontier:
        current = frontier.pop(0)  # Use pop(0) for breadth-first
        chain.append(current)
        
        if expand_all_variations:
            # Add all children (for variation analysis)
            frontier.extend(current.children)
        else:
            # Add only first child (mainline only)
            if current.children:
                frontier.append(current.children[0])
    
    return chain


def get_mainline_nodes(root_node: StateTreeNode) -> List[StateTreeNode]:
    """
    Get only mainline nodes from the state tree.
    
    Args:
        root_node: Root of the state tree
        
    Returns:
        List of mainline nodes
    """
    return get_node_chain(root_node, expand_all_variations=False)


def get_all_nodes(root_node: StateTreeNode) -> List[StateTreeNode]:
    """
    Get all nodes including variations from the state tree.
    
    Args:
        root_node: Root of the state tree
        
    Returns:
        List of all nodes
    """
    return get_node_chain(root_node, expand_all_variations=True)

"""
Missed Opportunity Classification

A missed opportunity is when a player fails to take advantage of the 
opponent's mistake or blunder. It's an additional tag on top of the 
existing classification (INACCURACY, MISTAKE, or BLUNDER).
"""

from ..models.state_tree import StateTreeNode
from ..models.enums import Classification


def consider_missed_opportunity_classification(
    node: StateTreeNode,
    current_classification: Classification,
    opponent_previous_classification: Classification
) -> bool:
    """
    Determine if a move should be tagged as a MISSED OPPORTUNITY.
    
    A move is a missed opportunity if:
    1. The current move is classified as BLUNDER, MISTAKE, or INACCURACY
    2. The opponent's previous move was a MISTAKE or BLUNDER
    
    Args:
        node: Current state tree node
        current_classification: The classification of the current move
        opponent_previous_classification: The classification of opponent's previous move
        
    Returns:
        True if the move should be tagged as a missed opportunity
    """
    # Check if current move is a candidate (BLUNDER, MISTAKE, or INACCURACY)
    if current_classification not in [
        Classification.INACCURACY,
        Classification.MISTAKE,
        Classification.BLUNDER
    ]:
        return False
    
    # Check if opponent's previous move was a MISTAKE or BLUNDER
    if opponent_previous_classification not in [
        Classification.MISTAKE,
        Classification.BLUNDER
    ]:
        return False
    
    return True


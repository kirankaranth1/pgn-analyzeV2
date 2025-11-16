"""
Stage 4: Extract Nodes

Creates simplified, classification-ready structures from state tree nodes.
Produces ExtractedPreviousNode and ExtractedCurrentNode objects.

Matches JavaScript implementation logic from ExtractNode.ts
"""

from typing import Optional, Union
import chess

from ..models.state_tree import StateTreeNode
from ..models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from ..models.enums import PieceColor
from ..utils.evaluation_utils import get_subjective_evaluation
from ..preprocessing.engine_analyzer import get_line_group_sibling


def _safe_move(fen: str, move: Union[str, chess.Move]) -> Optional[chess.Move]:
    """
    Safely parse and apply a move to a position.
    
    Args:
        fen: FEN position string
        move: Move in SAN format or chess.Move object
        
    Returns:
        chess.Move object if successful, None otherwise
    """
    try:
        board = chess.Board(fen)
        if isinstance(move, str):
            return board.parse_san(move)
        else:
            # If already a Move object, validate it's legal in this position
            if move in board.legal_moves:
                return move
            return None
    except (ValueError, chess.IllegalMoveError):
        return None


def _get_top_engine_line(node: StateTreeNode):
    """
    Get the best engine line for a node.
    
    Args:
        node: State tree node
        
    Returns:
        Best EngineLine or None
    """
    if not node.state.engine_lines:
        return None
    
    # Sort by depth (descending) then index (ascending)
    sorted_lines = sorted(
        node.state.engine_lines,
        key=lambda line: (-line.depth, line.index)
    )
    
    return sorted_lines[0] if sorted_lines else None


def _extract_second_top_move(node: StateTreeNode, top_line, player_color: PieceColor):
    """
    Extract second-best engine line and move.
    
    Args:
        node: State tree node
        top_line: Top engine line
        player_color: Color of the player
        
    Returns:
        Tuple of (second_top_line, second_top_move, second_subjective_eval)
    """
    second_top_line = get_line_group_sibling(
        node.state.engine_lines,
        top_line,
        2  # Index 2 = second-best
    )
    
    second_top_move = None
    second_subjective_eval = None
    
    if second_top_line and second_top_line.moves:
        second_move_san = second_top_line.moves[0].san
        second_top_move = _safe_move(node.state.fen, second_move_san)
        
        if second_top_move and second_top_line.evaluation:
            second_subjective_eval = get_subjective_evaluation(
                second_top_line.evaluation,
                player_color
            )
    
    return second_top_line, second_top_move, second_subjective_eval


def extract_previous_state_tree_node(
    node: StateTreeNode
) -> Optional[ExtractedPreviousNode]:
    """
    Extract previous node (position before move was played).
    
    Matches JavaScript implementation: extractPreviousStateTreeNode
    
    Args:
        node: State tree node
        
    Returns:
        ExtractedPreviousNode or None if extraction fails
    """
    # Get top engine line and move in this position
    top_line = _get_top_engine_line(node)
    if not top_line:
        return None
    
    top_move_san = top_line.moves[0].san if top_line.moves else None
    if not top_move_san:
        return None
    
    top_move = _safe_move(node.state.fen, top_move_san)
    if not top_move:
        return None
    
    # Get played move in this position
    played_move = None
    if node.parent and node.state.move:
        played_move = _safe_move(node.parent.state.fen, node.state.move.san)
    
    # Determine player color from played move or default to WHITE
    if played_move:
        # Get color from the move by checking which color moved from parent position
        parent_board = chess.Board(node.parent.state.fen)
        player_color = PieceColor.WHITE if parent_board.turn == chess.WHITE else PieceColor.BLACK
    else:
        # Default to WHITE if no played move (matches JS: playedMove?.color || WHITE)
        player_color = PieceColor.WHITE
    
    # Calculate subjective evaluation
    subjective_evaluation = get_subjective_evaluation(
        top_line.evaluation,
        player_color
    )
    
    # Extract second-best line
    second_top_line, second_top_move, second_subjective_eval = _extract_second_top_move(
        node, top_line, player_color
    )
    
    # Create board instance for the node
    board = chess.Board(node.state.fen)
    
    return ExtractedPreviousNode(
        board=board,
        state=node.state,
        top_line=top_line,
        top_move=top_move,
        evaluation=top_line.evaluation,
        subjective_evaluation=subjective_evaluation,
        second_top_line=second_top_line,
        second_top_move=second_top_move,
        second_subjective_evaluation=second_subjective_eval,
        played_move=played_move
    )


def extract_current_state_tree_node(
    node: StateTreeNode
) -> Optional[ExtractedCurrentNode]:
    """
    Extract current node (position after move was played).
    
    Matches JavaScript implementation: extractCurrentStateTreeNode
    
    Args:
        node: State tree node
        
    Returns:
        ExtractedCurrentNode or None if extraction fails
    """
    # Require parent node
    if not node.parent:
        return None
    
    # Get top engine line and move in this position
    top_line = _get_top_engine_line(node)
    if not top_line:
        return None
    
    # Extract top move (optional for current node)
    top_move_san = top_line.moves[0].san if top_line.moves else None
    top_move = _safe_move(node.state.fen, top_move_san) if top_move_san else None
    
    # Get played move in this position (REQUIRED)
    played_move_san = node.state.move.san if node.state.move else None
    if not played_move_san:
        return None
    
    played_move = _safe_move(node.parent.state.fen, played_move_san)
    if not played_move:
        return None
    
    # Determine player color from the parent board (before move was made)
    parent_board = chess.Board(node.parent.state.fen)
    player_color = PieceColor.WHITE if parent_board.turn == chess.WHITE else PieceColor.BLACK
    
    # Calculate subjective evaluation (REQUIRED for current node)
    subjective_evaluation = get_subjective_evaluation(
        top_line.evaluation,
        player_color
    )
    
    # Extract second-best line
    second_top_line, second_top_move, second_subjective_eval = _extract_second_top_move(
        node, top_line, player_color
    )
    
    # Create board instance for the node
    board = chess.Board(node.state.fen)
    
    return ExtractedCurrentNode(
        board=board,
        state=node.state,
        top_line=top_line,
        evaluation=top_line.evaluation,
        subjective_evaluation=subjective_evaluation,
        played_move=played_move,
        top_move=top_move,
        second_top_line=second_top_line,
        second_top_move=second_top_move,
        second_subjective_evaluation=second_subjective_eval
    )

"""
Stage 4: Extract Nodes

Creates simplified, classification-ready structures from state tree nodes.
Produces ExtractedPreviousNode and ExtractedCurrentNode objects.
"""

from typing import Optional
import chess

from ..models.state_tree import StateTreeNode
from ..models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from ..models.enums import PieceColor
from ..utils.evaluation_utils import get_subjective_evaluation
from ..preprocessing.engine_analyzer import get_line_group_sibling


def extract_previous_state_tree_node(
    node: StateTreeNode
) -> Optional[ExtractedPreviousNode]:
    """
    Extract previous node (position before move was played).
    
    Args:
        node: State tree node
        
    Returns:
        ExtractedPreviousNode or None if extraction fails
    """
    # Get top engine line
    top_line = _get_top_engine_line(node)
    if not top_line:
        return None
    
    # Extract top move
    if not top_line.moves:
        return None
    
    top_move_san = top_line.moves[0].san
    
    # Create board and get top move
    board = chess.Board(node.state.fen)
    try:
        top_move = board.parse_san(top_move_san)
    except (ValueError, chess.IllegalMoveError):
        return None
    
    # Get played move (from child node if available)
    played_move = None
    player_color = None
    
    if node.parent and node.state.move:
        played_board = chess.Board(node.parent.state.fen)
        try:
            played_move = played_board.parse_san(node.state.move.san)
            # Determine color from the board state before move
            player_color_bool = played_board.turn
            player_color = PieceColor.WHITE if player_color_bool == chess.WHITE else PieceColor.BLACK
        except (ValueError, chess.IllegalMoveError):
            played_move = None
    
    # If no played move from parent, use board turn
    if player_color is None:
        player_color_bool = board.turn
        player_color = PieceColor.WHITE if player_color_bool == chess.WHITE else PieceColor.BLACK
    
    # Calculate subjective evaluation
    subjective_evaluation = get_subjective_evaluation(
        top_line.evaluation,
        player_color
    )
    
    # Extract second-best line
    second_top_line = get_line_group_sibling(
        node.state.engine_lines,
        top_line,
        2  # Index 2 = second-best
    )
    
    second_top_move = None
    second_subjective_eval = None
    
    if second_top_line and second_top_line.moves:
        second_move_san = second_top_line.moves[0].san
        board2 = chess.Board(node.state.fen)
        try:
            second_top_move = board2.parse_san(second_move_san)
            # Color is same as top move
            second_subjective_eval = get_subjective_evaluation(
                second_top_line.evaluation,
                player_color
            )
        except (ValueError, chess.IllegalMoveError):
            pass
    
    # Create board instance for the node
    node_board = chess.Board(node.state.fen)
    
    return ExtractedPreviousNode(
        board=node_board,
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
    
    Args:
        node: State tree node
        
    Returns:
        ExtractedCurrentNode or None if extraction fails
    """
    # Require parent node
    if not node.parent:
        return None
    
    # Get top engine line
    top_line = _get_top_engine_line(node)
    if not top_line:
        return None
    
    # Extract top move (optional)
    top_move = None
    if top_line.moves:
        top_move_san = top_line.moves[0].san
        board = chess.Board(node.state.fen)
        try:
            top_move = board.parse_san(top_move_san)
        except (ValueError, chess.IllegalMoveError):
            pass
    
    # Get played move (REQUIRED)
    if not node.state.move:
        return None
    
    played_move_san = node.state.move.san
    played_board = chess.Board(node.parent.state.fen)
    
    try:
        played_move = played_board.parse_san(played_move_san)
    except (ValueError, chess.IllegalMoveError):
        return None
    
    # Determine player color from the parent board (before move was made)
    player_color_bool = played_board.turn
    player_color = PieceColor.WHITE if player_color_bool == chess.WHITE else PieceColor.BLACK
    
    # Calculate subjective evaluation
    subjective_evaluation = get_subjective_evaluation(
        top_line.evaluation,
        player_color
    )
    
    # Extract second-best line
    second_top_line = get_line_group_sibling(
        node.state.engine_lines,
        top_line,
        2
    )
    
    second_top_move = None
    second_subjective_eval = None
    
    if second_top_line and second_top_line.moves:
        second_move_san = second_top_line.moves[0].san
        board2 = chess.Board(node.state.fen)
        try:
            second_top_move = board2.parse_san(second_move_san)
            second_subjective_eval = get_subjective_evaluation(
                second_top_line.evaluation,
                player_color
            )
        except (ValueError, chess.IllegalMoveError):
            pass
    
    # Create board instance for the node
    node_board = chess.Board(node.state.fen)
    
    return ExtractedCurrentNode(
        board=node_board,
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

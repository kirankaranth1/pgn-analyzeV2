"""
Stage 1: Parse Game into State Tree

Converts PGN string into a tree structure representing the game state
at each position, including variations.
"""

from typing import Optional
import chess
import chess.pgn
import io

from ..models.state_tree import StateTreeNode, BoardState, Move
from ..models.enums import PieceColor
from ..utils.chess_utils import generate_unique_id, chess_color_to_piece_color
from ..constants import STARTING_FEN


def parse_pgn_to_state_tree(
    pgn: str,
    initial_position: Optional[str] = None
) -> StateTreeNode:
    """
    Parse PGN string into a state tree.
    
    Args:
        pgn: PGN string (e.g., "1. e4 e5 2. Nf3 Nc6")
        initial_position: FEN string for starting position (default: standard start)
        
    Returns:
        Root node of the state tree
        
    Raises:
        ValueError: If PGN cannot be parsed
    """
    # Set initial position
    initial_fen = initial_position or STARTING_FEN
    
    # Parse PGN using python-chess
    pgn_io = io.StringIO(pgn)
    try:
        game = chess.pgn.read_game(pgn_io)
        if game is None:
            # Empty PGN - just return root node with starting position
            return StateTreeNode(
                id=generate_unique_id(),
                mainline=True,
                parent=None,
                children=[],
                state=BoardState(
                    fen=initial_fen,
                    move=None,
                    move_color=None,
                    engine_lines=[],
                    classification=None,
                    accuracy=None,
                    opening=None
                )
            )
    except Exception as e:
        raise ValueError(f"Failed to parse PGN: {e}")
    
    # Create root node with initial position
    root_node = StateTreeNode(
        id=generate_unique_id(),
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen=initial_fen,
            move=None,
            move_color=None,
            engine_lines=[],
            classification=None,
            accuracy=None,
            opening=None
        )
    )
    
    # Build tree from parsed game
    board = chess.Board(initial_fen)
    _add_moves_to_node(root_node, game, board, is_mainline=True)
    
    return root_node


def _add_moves_to_node(
    current_node: StateTreeNode,
    game_node: chess.pgn.GameNode,
    board: chess.Board,
    is_mainline: bool
) -> None:
    """
    Recursively add moves to the state tree.
    
    Args:
        current_node: Current state tree node
        game_node: Current PGN game node from python-chess
        board: Chess board at current position
        is_mainline: Whether this is the main line
    """
    last_node = current_node
    
    # Iterate through all moves in this variation
    for move_node in game_node.mainline():
        move = move_node.move
        
        # Store current color before making move
        move_color_bool = board.turn
        
        # Get SAN before making the move
        san = board.san(move)
        
        # Make the move
        board.push(move)
        
        # Get FEN after move
        fen_after = board.fen()
        
        # Convert move color
        move_color_str = chess_color_to_piece_color(move_color_bool)
        
        # Create Move object
        move_obj = Move(
            san=san,
            uci=move.uci()
        )
        
        # Create new node
        new_node = StateTreeNode(
            id=generate_unique_id(),
            mainline=is_mainline,
            parent=last_node,
            children=[],
            state=BoardState(
                fen=fen_after,
                move=move_obj,
                move_color=move_color_str,
                engine_lines=[],
                classification=None,
                accuracy=None,
                opening=None
            )
        )
        
        # Link nodes
        last_node.children.append(new_node)
        
        # Process variations (non-mainline alternatives)
        if move_node.variations:
            for variation in list(move_node.variations)[1:]:  # Skip first (mainline)
                # Create a copy of board state before the move
                board_copy = board.copy()
                board_copy.pop()  # Remove the mainline move
                
                # Recursively process variation
                _add_moves_to_node(
                    last_node,  # Variations branch from parent
                    variation,
                    board_copy,
                    is_mainline=False
                )
        
        # Move to next node
        last_node = new_node


def parse_pgn_game(
    pgn: str,
    initial_position: Optional[str] = None
) -> StateTreeNode:
    """
    Parse a PGN game into a state tree.
    
    This is the main entry point for Stage 1 of the preprocessing pipeline.
    
    Args:
        pgn: PGN string
        initial_position: Optional starting FEN (default: standard position)
        
    Returns:
        Root node of the state tree
    """
    return parse_pgn_to_state_tree(pgn, initial_position)

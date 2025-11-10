"""Extract and prepare nodes for classification."""

import chess
from dataclasses import dataclass
from typing import Optional
from ..core.state_tree import StateTreeNode
from ..core.evaluation import Evaluation
from ..core.engine_line import EngineLine
from ..core.move import Move
from ..core.types import PieceColor
from ..analysis.expected_points import get_subjective_evaluation


@dataclass
class ExtractedPreviousNode:
    """Extracted data from position before the move.
    
    Attributes:
        board: Chess board state
        fen: FEN string
        top_line: Best engine line
        top_move: Best move from this position
        evaluation: Top line evaluation
        subjective_evaluation: Evaluation from player's perspective
        second_top_line: Second-best engine line (optional)
        second_top_move: Second-best move (optional)
        second_subjective_eval: Second line subjective evaluation (optional)
        played_move: Move that was actually played (optional)
        player_color: Color of player to move
    """
    board: chess.Board
    fen: str
    top_line: EngineLine
    top_move: Move
    evaluation: Evaluation
    subjective_evaluation: Evaluation
    player_color: PieceColor
    second_top_line: Optional[EngineLine] = None
    second_top_move: Optional[Move] = None
    second_subjective_eval: Optional[Evaluation] = None
    played_move: Optional[Move] = None


@dataclass
class ExtractedCurrentNode:
    """Extracted data from position after the move.
    
    Attributes:
        board: Chess board state
        fen: FEN string
        top_line: Best continuation
        evaluation: Position evaluation
        subjective_evaluation: Player's perspective (required)
        played_move: Move that was played (required)
        player_color: Color of player who moved
        top_move: Best move from here (optional)
        second_top_line: Second-best continuation (optional)
        second_top_move: Second-best move (optional)
        second_subjective_eval: Second line subjective (optional)
    """
    board: chess.Board
    fen: str
    top_line: EngineLine
    evaluation: Evaluation
    subjective_evaluation: Evaluation
    played_move: Move
    player_color: PieceColor
    top_move: Optional[Move] = None
    second_top_line: Optional[EngineLine] = None
    second_top_move: Optional[Move] = None
    second_subjective_eval: Optional[Evaluation] = None


class NodeExtractor:
    """Extract nodes for classification."""
    
    @staticmethod
    def extract_previous_node(node: StateTreeNode) -> Optional[ExtractedPreviousNode]:
        """Extract previous node (before move).
        
        Args:
            node: Current state tree node
            
        Returns:
            ExtractedPreviousNode or None if parent doesn't exist
        """
        parent = node.parent
        if not parent:
            return None
        
        # Get board state
        fen = parent.state.fen
        board = chess.Board(fen)
        
        # Determine player color (who is about to move)
        player_color = PieceColor.WHITE if board.turn == chess.WHITE else PieceColor.BLACK
        
        # Get top line
        top_line = parent.state.get_top_line()
        if not top_line:
            return None
        
        top_move = top_line.get_first_move()
        evaluation = top_line.evaluation
        subjective_eval = get_subjective_evaluation(evaluation, player_color)
        
        # Get second line if available
        second_line = parent.state.get_second_line()
        second_move = None
        second_subjective = None
        
        if second_line:
            try:
                second_move = second_line.get_first_move()
                second_subjective = get_subjective_evaluation(
                    second_line.evaluation, 
                    player_color
                )
            except ValueError:
                pass  # No moves in second line
        
        # Get played move
        played_move = node.state.move
        
        return ExtractedPreviousNode(
            board=board,
            fen=fen,
            top_line=top_line,
            top_move=top_move,
            evaluation=evaluation,
            subjective_evaluation=subjective_eval,
            player_color=player_color,
            second_top_line=second_line,
            second_top_move=second_move,
            second_subjective_eval=second_subjective,
            played_move=played_move
        )
    
    @staticmethod
    def extract_current_node(node: StateTreeNode) -> Optional[ExtractedCurrentNode]:
        """Extract current node (after move).
        
        Args:
            node: Current state tree node
            
        Returns:
            ExtractedCurrentNode or None if data missing
        """
        # Get board state
        fen = node.state.fen
        board = chess.Board(fen)
        
        # Get played move
        played_move = node.state.move
        if not played_move:
            return None  # No move (root node)
        
        # Determine player color (who just moved)
        # After the move, it's the opponent's turn
        player_color = node.state.move_color
        if not player_color:
            # Infer from board turn (opposite of current turn)
            player_color = PieceColor.BLACK if board.turn == chess.WHITE else PieceColor.WHITE
        
        # Get top line
        top_line = node.state.get_top_line()
        if not top_line:
            return None
        
        evaluation = top_line.evaluation
        
        # Subjective evaluation is from the player's perspective who just moved
        subjective_eval = get_subjective_evaluation(evaluation, player_color)
        
        # Get top move if available
        top_move = None
        try:
            top_move = top_line.get_first_move()
        except ValueError:
            pass  # No moves available
        
        # Get second line if available
        second_line = node.state.get_second_line()
        second_move = None
        second_subjective = None
        
        if second_line:
            try:
                second_move = second_line.get_first_move()
                second_subjective = get_subjective_evaluation(
                    second_line.evaluation,
                    player_color
                )
            except ValueError:
                pass
        
        return ExtractedCurrentNode(
            board=board,
            fen=fen,
            top_line=top_line,
            evaluation=evaluation,
            subjective_evaluation=subjective_eval,
            played_move=played_move,
            player_color=player_color,
            top_move=top_move,
            second_top_line=second_line,
            second_top_move=second_move,
            second_subjective_eval=second_subjective
        )


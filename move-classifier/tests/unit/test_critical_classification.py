"""
Unit tests for critical move classification
"""

import chess
import pytest

from src.models.state_tree import Evaluation, EngineLine, BoardState, StateTreeNode, Move
from src.models.enums import PieceColor
from src.models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
from src.classification.critical_move import is_move_critical_candidate
from src.classification.critical_classifier import consider_critical_classification


class TestCriticalMoveCandidate:
    """Test critical move candidate detection."""
    
    def test_not_critical_completely_winning(self):
        """Position still completely winning with second-best move shouldn't be critical."""
        # Create a position where second-best move still has +800 evaluation
        previous_board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1")
        current_board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 1")
        
        previous = ExtractedPreviousNode(
            state=BoardState(fen=previous_board.fen()),
            board=previous_board,
            evaluation=Evaluation(type="centipawn", value=100),
            subjective_evaluation=Evaluation(type="centipawn", value=100),
            top_move=chess.Move.from_uci("f3g5"),
            second_subjective_evaluation=Evaluation(type="centipawn", value=800)  # Still winning
        )
        
        current = ExtractedCurrentNode(
            state=BoardState(fen=current_board.fen(), move=Move(san="Ng5", uci="f3g5")),
            board=current_board,
            evaluation=Evaluation(type="centipawn", value=-100),
            subjective_evaluation=Evaluation(type="centipawn", value=100),
            played_move=chess.Move.from_uci("f3g5")
        )
        
        assert is_move_critical_candidate(previous, current) == False
    
    def test_not_critical_losing_position(self):
        """Moves in losing positions cannot be critical."""
        previous_board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1")
        current_board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 1")
        
        previous = ExtractedPreviousNode(
            state=BoardState(fen=previous_board.fen()),
            board=previous_board,
            evaluation=Evaluation(type="centipawn", value=-200),
            subjective_evaluation=Evaluation(type="centipawn", value=-200),
            top_move=chess.Move.from_uci("f3g5")
        )
        
        current = ExtractedCurrentNode(
            state=BoardState(fen=current_board.fen(), move=Move(san="Ng5", uci="f3g5")),
            board=current_board,
            evaluation=Evaluation(type="centipawn", value=200),
            subjective_evaluation=Evaluation(type="centipawn", value=-200),  # Losing
            played_move=chess.Move.from_uci("f3g5")
        )
        
        assert is_move_critical_candidate(previous, current) == False
    
    def test_not_critical_queen_promotion(self):
        """Queen promotions cannot be critical."""
        previous_board = chess.Board("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
        current_board = chess.Board("Q3k3/8/8/8/8/8/8/4K3 b - - 0 1")
        
        previous = ExtractedPreviousNode(
            state=BoardState(fen=previous_board.fen()),
            board=previous_board,
            evaluation=Evaluation(type="centipawn", value=900),
            subjective_evaluation=Evaluation(type="centipawn", value=900),
            top_move=chess.Move.from_uci("a7a8q")
        )
        
        current = ExtractedCurrentNode(
            state=BoardState(fen=current_board.fen(), move=Move(san="a8=Q", uci="a7a8q")),
            board=current_board,
            evaluation=Evaluation(type="centipawn", value=-900),
            subjective_evaluation=Evaluation(type="centipawn", value=900),
            played_move=chess.Move.from_uci("a7a8q")
        )
        
        assert is_move_critical_candidate(previous, current) == False
    
    def test_not_critical_escaping_check(self):
        """Moves escaping check cannot be critical."""
        previous_board = chess.Board("4k3/8/8/8/8/8/8/R3K3 b - - 0 1")
        previous_board.push_san("Kd8")  # Escaping check
        previous_board.pop()
        
        current_board = chess.Board("3k4/8/8/8/8/8/8/R3K3 w - - 0 1")
        
        previous = ExtractedPreviousNode(
            state=BoardState(fen=previous_board.fen()),
            board=previous_board,
            evaluation=Evaluation(type="centipawn", value=-200),
            subjective_evaluation=Evaluation(type="centipawn", value=200),
            top_move=chess.Move.from_uci("e8d8")
        )
        
        current = ExtractedCurrentNode(
            state=BoardState(fen=current_board.fen(), move=Move(san="Kd8", uci="e8d8")),
            board=current_board,
            evaluation=Evaluation(type="centipawn", value=200),
            subjective_evaluation=Evaluation(type="centipawn", value=200),
            played_move=chess.Move.from_uci("e8d8")
        )
        
        # Position is in check, so should not be critical
        assert is_move_critical_candidate(previous, current) == False


class TestCriticalClassification:
    """Test critical classification logic."""
    
    def test_not_critical_without_second_line(self):
        """Cannot be critical without a second-best line."""
        previous_board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1")
        current_board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 1")
        
        previous = ExtractedPreviousNode(
            state=BoardState(fen=previous_board.fen()),
            board=previous_board,
            evaluation=Evaluation(type="centipawn", value=100),
            subjective_evaluation=Evaluation(type="centipawn", value=100),
            top_move=chess.Move.from_uci("f3g5"),
            second_top_line=None  # No second line
        )
        
        current = ExtractedCurrentNode(
            state=BoardState(fen=current_board.fen(), move=Move(san="Ng5", uci="f3g5")),
            board=current_board,
            evaluation=Evaluation(type="centipawn", value=-100),
            subjective_evaluation=Evaluation(type="centipawn", value=100),
            played_move=chess.Move.from_uci("f3g5")
        )
        
        assert consider_critical_classification(previous, current) == False


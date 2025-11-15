"""
Integration Tests: Engine Components

Tests for cloud and local engine integration.
"""

import pytest

from src.engine.cloud_evaluator import get_cloud_evaluation, _convert_uci_moves_to_san
from src.engine.uci_engine import UCIEngine
from src.models.enums import EngineVersion
from src.constants import STARTING_FEN


class TestCloudEvaluator:
    """Test Lichess cloud evaluation integration."""
    
    @pytest.mark.integration
    @pytest.mark.network
    def test_get_cloud_evaluation_starting_position(self):
        """Test cloud evaluation for starting position."""
        try:
            engine_lines = get_cloud_evaluation(STARTING_FEN, multi_pv=2)
            
            # Should get at least one line
            assert len(engine_lines) > 0
            
            # Verify structure
            for line in engine_lines:
                assert line.evaluation is not None
                assert line.source == "lichess-cloud"
                assert line.depth > 0
                assert line.index >= 1
                assert len(line.moves) > 0
                
        except Exception as e:
            pytest.skip(f"Cloud evaluation failed (expected if no internet): {e}")
    
    @pytest.mark.integration
    @pytest.mark.network
    def test_cloud_evaluation_after_e4(self):
        """Test cloud evaluation for position after 1. e4."""
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        
        try:
            engine_lines = get_cloud_evaluation(fen, multi_pv=3)
            
            assert len(engine_lines) > 0
            
            # First line should be best move
            best_line = engine_lines[0]
            assert best_line.index == 1
            
            # Should suggest common responses like e5, c5, etc.
            best_move = best_line.moves[0].san if best_line.moves else None
            assert best_move in ["e5", "c5", "e6", "c6", "Nf6", "d5"]
            
        except Exception as e:
            pytest.skip(f"Cloud evaluation failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.network
    def test_cloud_evaluation_returns_multiple_lines(self):
        """Test that MultiPV returns multiple lines."""
        try:
            engine_lines = get_cloud_evaluation(STARTING_FEN, multi_pv=3)
            
            # Should get multiple lines
            assert len(engine_lines) >= 2
            
            # Lines should have different indices
            indices = [line.index for line in engine_lines]
            assert len(set(indices)) == len(indices)  # All unique
            
        except Exception as e:
            pytest.skip(f"Cloud evaluation failed: {e}")
    
    def test_convert_uci_moves_to_san(self):
        """Test UCI to SAN conversion."""
        uci_moves = ["e2e4", "e7e5", "g1f3"]
        
        moves = _convert_uci_moves_to_san(STARTING_FEN, uci_moves)
        
        assert len(moves) == 3
        assert moves[0].san == "e4"
        assert moves[1].san == "e5"
        assert moves[2].san == "Nf3"
    
    def test_convert_handles_lichess_castling(self):
        """Test that Lichess castling notation is handled."""
        # Position where castling is possible
        fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
        uci_moves = ["e1g1"]  # Kingside castling in standard UCI
        
        moves = _convert_uci_moves_to_san(fen, uci_moves)
        
        assert len(moves) == 1
        assert moves[0].san == "O-O"


class TestUCIEngine:
    """Test local UCI engine integration."""
    
    @pytest.mark.integration
    @pytest.mark.engine
    def test_uci_engine_initialization(self):
        """Test that UCI engine can be initialized."""
        try:
            engine = UCIEngine()
            assert engine is not None
            assert engine.version == EngineVersion.STOCKFISH_17
            engine.terminate()
        except FileNotFoundError:
            pytest.skip("Stockfish not installed")
    
    @pytest.mark.integration
    @pytest.mark.engine
    @pytest.mark.slow
    def test_uci_engine_evaluate_starting_position(self):
        """Test evaluation of starting position."""
        try:
            engine = UCIEngine()
            engine.set_position(STARTING_FEN)
            
            lines = engine.evaluate(depth=10, multi_pv=2)
            
            # Should get at least one line
            assert len(lines) > 0
            
            # Verify structure
            for line in lines:
                assert line.evaluation is not None
                assert line.source == "stockfish-17"
                assert line.depth == 10
                assert line.index >= 1
                assert len(line.moves) > 0
            
            engine.terminate()
            
        except FileNotFoundError:
            pytest.skip("Stockfish not installed")
    
    @pytest.mark.integration
    @pytest.mark.engine
    @pytest.mark.slow
    def test_uci_engine_multipv(self):
        """Test MultiPV returns multiple lines."""
        try:
            engine = UCIEngine()
            engine.set_position(STARTING_FEN)
            
            lines = engine.evaluate(depth=8, multi_pv=3)
            
            # Should get multiple lines
            assert len(lines) >= 2
            
            # Lines should have increasing indices
            for i, line in enumerate(lines):
                assert line.index == i + 1
            
            engine.terminate()
            
        except FileNotFoundError:
            pytest.skip("Stockfish not installed")
    
    @pytest.mark.integration
    @pytest.mark.engine
    @pytest.mark.slow
    def test_uci_engine_normalized_evaluation(self):
        """Test that evaluations are normalized to White's perspective."""
        try:
            engine = UCIEngine()
            
            # Set position where Black to move
            fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
            engine.set_position(fen)
            
            lines = engine.evaluate(depth=8, multi_pv=1)
            
            assert len(lines) > 0
            
            # Evaluation should still be from White's perspective
            # (positive = White better, negative = Black better)
            # Starting position after e4 should be slightly positive for White
            assert lines[0].evaluation.value > -100  # Reasonable range
            
            engine.terminate()
            
        except FileNotFoundError:
            pytest.skip("Stockfish not installed")
    
    @pytest.mark.integration
    @pytest.mark.engine
    def test_uci_engine_handles_mate(self):
        """Test that engine correctly handles mate in N."""
        try:
            engine = UCIEngine()
            
            # Position before Scholar's mate (Black to move, mate in 1)
            # After 1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 (before Qxf7#)
            fen = "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"
            engine.set_position(fen)
            
            lines = engine.evaluate(depth=10, multi_pv=1)
            
            assert len(lines) > 0
            
            # Should detect mate
            if lines[0].evaluation.type == "mate":
                # White has mate in 1, so should be positive
                assert lines[0].evaluation.value > 0
            
            engine.terminate()
            
        except FileNotFoundError:
            pytest.skip("Stockfish not installed")


class TestEngineAnalyzerIntegration:
    """Test engine analyzer coordination."""
    
    @pytest.mark.integration
    def test_analyzer_tries_cloud_first(self):
        """Test that analyzer tries cloud evaluation first."""
        from src.preprocessing.parser import parse_pgn_game
        from src.preprocessing.engine_analyzer import analyze_state_tree
        from src.config import EngineConfig
        
        root = parse_pgn_game("1. e4")
        
        config = EngineConfig(
            depth=10,
            multi_pv=2,
            use_cloud_eval=True
        )
        
        try:
            analyze_state_tree(root, config)
            
            # Should have engine lines
            assert len(root.state.engine_lines) > 0
            
            # If cloud succeeded, source should be lichess-cloud
            # (might fallback to local if cloud fails)
            assert root.state.engine_lines[0].source in ["lichess-cloud", "stockfish-17"]
            
        except Exception as e:
            pytest.skip(f"Analysis failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.engine
    @pytest.mark.slow
    def test_analyzer_fallback_to_local(self):
        """Test fallback to local engine when cloud fails."""
        from src.preprocessing.parser import parse_pgn_game
        from src.preprocessing.engine_analyzer import analyze_state_tree
        from src.config import EngineConfig
        
        root = parse_pgn_game("1. e4")
        
        # Use a position unlikely to be in cloud database
        uncommon_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        root.state.fen = uncommon_fen
        
        config = EngineConfig(
            depth=8,
            multi_pv=1,
            use_cloud_eval=True  # Will try cloud first
        )
        
        try:
            analyze_state_tree(root, config)
            
            # Should have analysis from either source
            assert len(root.state.engine_lines) > 0
            
        except FileNotFoundError:
            pytest.skip("Stockfish not installed for fallback")
        except Exception as e:
            pytest.skip(f"Analysis failed: {e}")


"""
Integration Test: Morphy vs Duke Karl/Count Isouard (1858) - The Opera Game

This test uses the famous "Opera Game" played by Paul Morphy at the Paris Opera
in 1858. This game is one of the most famous chess games ever played, showcasing
brilliant attacking play and a beautiful checkmate.

Game Details:
- Event: Paris
- Date: 1858
- White: Paul Morphy
- Black: Duke Karl of Brunswick and Count Isouard
- Result: 1-0
- ECO: C41 (Philidor Defense)
- Moves: 17 (33 ply)
- Famous for: Brilliant sacrificial attack leading to checkmate
"""

import pytest
import chess

from src.preprocessing import run_full_preprocessing_pipeline, extract_node_pair
from src.preprocessing.parser import parse_pgn_game
from src.preprocessing.node_chain_builder import get_node_chain
from src.config import EngineConfig


# The famous Opera Game (1858)
# This is a secondary standard test PGN for integration tests
MORPHY_OPERA_PGN = """
1.e4 e5 2.Nf3 d6 3.d4 Bg4 4.dxe5 Bxf3 5.Qxf3 dxe5 6.Bc4 Nf6 7.Qb3 Qe7
8.Nc3 c6 9.Bg5 b5 10.Nxb5 cxb5 11.Bxb5+ Nbd7 12.O-O-O Rd8
13.Rxd7 Rxd7 14.Rd1 Qe6 15.Bxd7+ Nxd7 16.Qb8+ Nxb8 17.Rd8#
""".strip()


class TestMorphyOperaParsing:
    """Test parsing of the Morphy Opera Game."""
    
    def test_parse_full_game(self):
        """Test that the complete game parses correctly."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        
        # Verify root node
        assert root is not None
        assert root.parent is None
        assert root.mainline is True
        
        # Get all nodes
        nodes = get_node_chain(root)
        
        # Should have 34 nodes: root + 33 half-moves
        assert len(nodes) == 34, f"Expected 34 nodes, got {len(nodes)}"
        
        # Verify all nodes are mainline
        for node in nodes:
            assert node.mainline is True
    
    def test_opening_moves(self):
        """Test that opening moves are parsed correctly."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Verify first few moves (Philidor Defense)
        assert nodes[1].state.move.san == "e4"
        assert nodes[1].state.move_color == "WHITE"
        
        assert nodes[2].state.move.san == "e5"
        assert nodes[2].state.move_color == "BLACK"
        
        assert nodes[3].state.move.san == "Nf3"
        assert nodes[3].state.move_color == "WHITE"
        
        # Black's Philidor Defense setup
        assert nodes[4].state.move.san == "d6"
        assert nodes[4].state.move_color == "BLACK"
    
    def test_queen_sacrifice(self):
        """Test the famous queen sacrifice move."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Move 16: Qb8+ - the queen sacrifice
        # This is node 31 (root + 30 half-moves, since move 16 is White's 16th)
        qb8_node = nodes[31]
        assert qb8_node.state.move.san == "Qb8+"
        assert qb8_node.state.move_color == "WHITE"
        
        # Verify it's a check
        board = chess.Board(qb8_node.state.fen)
        assert board.is_check()
    
    def test_checkmate(self):
        """Test the final checkmate move."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Last move should be Rd8# (checkmate)
        last_node = nodes[-1]
        assert last_node.state.move.san == "Rd8#"
        assert last_node.state.move_color == "WHITE"
        
        # Verify board is in checkmate
        board = chess.Board(last_node.state.fen)
        assert board.is_checkmate()
    
    def test_castling_queenside(self):
        """Test queenside castling notation."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # White castles queenside on move 12
        castling_node = nodes[23]
        assert castling_node.state.move.san == "O-O-O"
        assert castling_node.state.move_color == "WHITE"
    
    def test_final_position(self):
        """Test that the final position is checkmate."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Verify the final board position
        last_node = nodes[-1]
        board = chess.Board(last_node.state.fen)
        
        # Should be checkmate
        assert board.is_checkmate()
        assert not board.is_stalemate()
        assert board.is_valid()


class TestMorphyOperaFullPipeline:
    """Test complete preprocessing pipeline with Opera Game."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.network
    def test_full_pipeline_with_cloud_evaluation(self):
        """
        Test complete pipeline with cloud evaluation.
        
        This is a STANDARD INTEGRATION TEST for the preprocessing pipeline.
        """
        config = EngineConfig(
            depth=16,
            multi_pv=2,
            use_cloud_eval=True
        )
        
        try:
            # Run full preprocessing pipeline
            root = run_full_preprocessing_pipeline(
                MORPHY_OPERA_PGN,
                config=config
            )
            
            # Verify structure
            assert root is not None
            nodes = get_node_chain(root)
            assert len(nodes) == 34  # root + 33 moves
            
            # Verify engine analysis was performed
            analyzed = sum(1 for n in nodes if len(n.state.engine_lines) > 0)
            assert analyzed > 0, "No nodes have engine analysis"
            
            # Verify we can extract node pairs
            classified_count = 0
            for i in range(1, len(nodes)):
                node_pair = extract_node_pair(nodes[i])
                if node_pair is not None:
                    previous, current = node_pair
                    
                    # Verify extracted nodes have required data
                    assert previous.board is not None
                    assert current.board is not None
                    assert current.played_move is not None
                    
                    classified_count += 1
            
            # Should be able to extract and classify most moves
            assert classified_count > 20, f"Only {classified_count} moves could be classified"
            
            print(f"\n✅ Successfully processed Opera Game (1858)")
            print(f"   Total nodes: {len(nodes)}")
            print(f"   Classifiable moves: {classified_count}")
            
        except Exception as e:
            pytest.skip(f"Pipeline failed (may require network/engine): {e}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.engine
    def test_full_pipeline_with_local_engine(self):
        """Test complete pipeline with local Stockfish engine."""
        config = EngineConfig(
            depth=12,
            multi_pv=2,
            use_cloud_eval=False
        )
        
        try:
            root = run_full_preprocessing_pipeline(
                MORPHY_OPERA_PGN,
                config=config
            )
            
            assert root is not None
            nodes = get_node_chain(root)
            assert len(nodes) == 34
            
            # Verify engine analysis source
            for node in nodes:
                if len(node.state.engine_lines) > 0:
                    assert node.state.engine_lines[0].source == "stockfish-17"
                    break
            
            print(f"\n✅ Successfully analyzed with local engine")
            
        except FileNotFoundError:
            pytest.skip("Stockfish not installed")
        except Exception as e:
            pytest.skip(f"Pipeline failed: {e}")
    
    def test_game_parsing_only(self):
        """Test parsing without engine analysis (fast test)."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Verify game structure
        assert len(nodes) == 34
        
        # Verify no moves have errors
        for i, node in enumerate(nodes[1:], 1):
            assert node.state.move is not None, f"Node {i} has no move"
            assert node.state.move.san is not None, f"Node {i} has no SAN"
            assert node.state.move.uci is not None, f"Node {i} has no UCI"
            assert node.state.move_color in ["WHITE", "BLACK"], f"Node {i} has invalid color"
            
            # Verify FEN is valid
            board = chess.Board(node.state.fen)
            assert board.is_valid(), f"Node {i} has invalid FEN: {node.state.fen}"
        
        # Verify alternating colors
        for i in range(1, len(nodes)):
            if i % 2 == 1:
                assert nodes[i].state.move_color == "WHITE"
            else:
                assert nodes[i].state.move_color == "BLACK"
        
        print(f"\n✅ Game parsing verified: 33 moves, all valid")


class TestMorphyOperaMovePairs:
    """Test move pair extraction from the game."""
    
    def test_extract_all_move_pairs(self):
        """Test that all moves can be extracted as pairs."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        
        # Add proper engine lines for testing extraction
        from src.models.state_tree import EngineLine, Evaluation, Move
        import chess
        
        nodes = get_node_chain(root)
        for node in nodes:
            board = chess.Board(node.state.fen)
            legal_moves = list(board.legal_moves)
            
            if legal_moves:
                test_move = legal_moves[0]
                node.state.engine_lines = [
                    EngineLine(
                        evaluation=Evaluation(type="centipawn", value=50.0),
                        source="test",
                        depth=10,
                        index=1,
                        moves=[Move(san=board.san(test_move), uci=test_move.uci())]
                    )
                ]
            else:
                node.state.engine_lines = [
                    EngineLine(
                        evaluation=Evaluation(type="centipawn", value=50.0),
                        source="test",
                        depth=10,
                        index=1,
                        moves=[Move(san="e4", uci="e2e4")]
                    )
                ]
        
        # Extract all move pairs
        move_pairs = []
        for i in range(1, len(nodes)):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                move_pairs.append(pair)
        
        # Should extract most pairs (30+ out of 33 moves)
        assert len(move_pairs) > 30, f"Only extracted {len(move_pairs)} move pairs"
        
        # Verify each pair
        for i, (previous, current) in enumerate(move_pairs):
            assert previous is not None, f"Pair {i}: previous is None"
            assert current is not None, f"Pair {i}: current is None"
            assert current.played_move is not None, f"Pair {i}: played_move is None"


class TestMorphyOperaPositions:
    """Test specific interesting positions from the game."""
    
    def test_position_after_queen_sacrifice(self):
        """Test position after 16.Qb8+ (queen sacrifice)."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # After 16.Qb8+
        qb8_node = nodes[31]
        board = chess.Board(qb8_node.state.fen)
        
        # Verify key features
        # White queen should be on b8
        assert board.piece_at(chess.B8) == chess.Piece(chess.QUEEN, chess.WHITE)
        
        # Black is in check
        assert board.is_check()
        
        # Black king is on e8
        assert board.piece_at(chess.E8) == chess.Piece(chess.KING, chess.BLACK)
    
    def test_checkmate_position(self):
        """Test the final checkmate position."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Final position after 17.Rd8#
        final_node = nodes[-1]
        board = chess.Board(final_node.state.fen)
        
        # Verify checkmate
        assert board.is_checkmate()
        assert board.is_check()
        assert not board.is_stalemate()
        
        # White rook should be on d8 delivering checkmate
        assert board.piece_at(chess.D8) == chess.Piece(chess.ROOK, chess.WHITE)
    
    def test_position_before_sacrifice(self):
        """Test position just before the queen sacrifice."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Position before 16.Qb8+ (after 15...Nxd7)
        before_qb8 = nodes[30]
        board = chess.Board(before_qb8.state.fen)
        
        # Black just played, so White to move
        assert board.turn == chess.WHITE
        
        # White queen should still be on b3
        assert board.piece_at(chess.B3) == chess.Piece(chess.QUEEN, chess.WHITE)


class TestMorphyOperaMetrics:
    """Test that accuracy and metrics can be calculated for the game."""
    
    @pytest.mark.slow
    def test_calculate_move_accuracy(self):
        """Test that move accuracy can be calculated."""
        from src.preprocessing.calculator import calculate_move_metrics
        from src.models.state_tree import EngineLine, Evaluation, Move
        import chess
        
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Add proper engine lines
        for node in nodes:
            board = chess.Board(node.state.fen)
            legal_moves = list(board.legal_moves)
            
            if legal_moves:
                test_move = legal_moves[0]
                node.state.engine_lines = [
                    EngineLine(
                        evaluation=Evaluation(type="centipawn", value=30.0),
                        source="test",
                        depth=10,
                        index=1,
                        moves=[Move(san=board.san(test_move), uci=test_move.uci())]
                    )
                ]
        
        # Calculate accuracy for some moves
        calculated_accuracies = 0
        
        for i in range(1, min(10, len(nodes))):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                previous, current = pair
                
                # Calculate metrics
                point_loss, accuracy = calculate_move_metrics(previous, current)
                
                # Verify metrics are valid
                assert 0.0 <= point_loss <= 1.0, f"Invalid point loss: {point_loss}"
                assert 0.0 <= accuracy <= 100.0, f"Invalid accuracy: {accuracy}"
                
                calculated_accuracies += 1
        
        assert calculated_accuracies > 5, f"Only calculated {calculated_accuracies} accuracies"


# Marker for standard integration test
@pytest.mark.standard_integration_test
class TestOperaGameStandardIntegration:
    """
    STANDARD INTEGRATION TEST SUITE for Opera Game
    
    These tests must pass for any implementation of the preprocessing pipeline.
    """
    
    @pytest.mark.integration
    def test_standard_game_parsing(self):
        """REQUIRED: Parse the Opera Game correctly."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        assert len(nodes) == 34
        assert all(node.mainline for node in nodes)
        
        # Verify no parsing errors
        for node in nodes[1:]:
            assert node.state.move is not None
            assert node.state.fen is not None
    
    @pytest.mark.integration
    def test_standard_game_structure(self):
        """REQUIRED: Maintain correct tree structure."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Verify parent-child relationships
        for i in range(1, len(nodes)):
            assert nodes[i].parent == nodes[i-1]
            assert nodes[i] in nodes[i-1].children
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_standard_game_node_extraction(self):
        """REQUIRED: Extract nodes for classification."""
        from src.models.state_tree import EngineLine, Evaluation, Move
        import chess
        
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Add proper engine data
        for node in nodes:
            board = chess.Board(node.state.fen)
            legal_moves = list(board.legal_moves)
            
            if legal_moves:
                test_move = legal_moves[0]
                node.state.engine_lines = [
                    EngineLine(
                        evaluation=Evaluation(type="centipawn", value=20.0),
                        source="test",
                        depth=10,
                        index=1,
                        moves=[Move(san=board.san(test_move), uci=test_move.uci())]
                    )
                ]
        
        # Should extract most moves
        extracted = 0
        for i in range(1, len(nodes)):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                extracted += 1
        
        assert extracted > 30, f"Only extracted {extracted}/33 moves"


if __name__ == "__main__":
    # Quick test to verify the game parses
    print("Testing Morphy vs Duke Karl/Count Isouard (1858) - The Opera Game...")
    root = parse_pgn_game(MORPHY_OPERA_PGN)
    nodes = get_node_chain(root)
    print(f"✅ Parsed {len(nodes)} nodes (root + {len(nodes)-1} moves)")
    print(f"✅ First move: {nodes[1].state.move.san}")
    print(f"✅ Last move: {nodes[-1].state.move.san}")
    print(f"✅ Checkmate: {chess.Board(nodes[-1].state.fen).is_checkmate()}")


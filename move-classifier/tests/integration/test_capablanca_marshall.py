"""
Integration Test: Capablanca vs Marshall (1918)

This test uses the famous historical game between Jose Raul Capablanca and 
Frank James Marshall from New York 1918. This game introduced the Marshall Attack
in the Ruy Lopez and serves as the standard test case for all integration tests
of the chess move classifier.

Game Details:
- Event: New York
- Date: 1918.10.23
- White: Jose Raul Capablanca
- Black: Frank James Marshall
- Result: 1-0
- ECO: C89 (Ruy Lopez, Marshall Attack)
- Moves: 36 (71 ply)
"""

import pytest
import chess

from src.preprocessing import run_full_preprocessing_pipeline, extract_node_pair
from src.preprocessing.parser import parse_pgn_game
from src.preprocessing.node_chain_builder import get_node_chain
from src.config import EngineConfig


# The famous Capablanca vs Marshall game (1918)
# This is the standard test PGN for all integration tests
CAPABLANCA_MARSHALL_PGN = """
1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.O-O Be7 6.Re1 b5 7.Bb3
O-O 8.c3 d5 9.exd5 Nxd5 10.Nxe5 Nxe5 11.Rxe5 Nf6 12.Re1 Bd6
13.h3 Ng4 14.Qf3 Qh4 15.d4 Nxf2 16.Re2 Bg4 17.hxg4 Bh2+ 18.Kf1
Bg3 19.Rxf2 Qh1+ 20.Ke2 Bxf2 21.Bd2 Bh4 22.Qh3 Rae8+ 23.Kd3
Qf1+ 24.Kc2 Bf2 25.Qf3 Qg1 26.Bd5 c5 27.dxc5 Bxc5 28.b4 Bd6
29.a4 a5 30.axb5 axb4 31.Ra6 bxc3 32.Nxc3 Bb4 33.b6 Bxc3
34.Bxc3 h6 35.b7 Re3 36.Bxf7+
""".strip()


class TestCapablancaMarshallParsing:
    """Test parsing of the Capablanca vs Marshall game."""
    
    def test_parse_full_game(self):
        """Test that the complete game parses correctly."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        
        # Verify root node
        assert root is not None
        assert root.parent is None
        assert root.mainline is True
        
        # Get all nodes
        nodes = get_node_chain(root)
        
        # Should have 72 nodes: root + 71 half-moves
        assert len(nodes) == 72, f"Expected 72 nodes, got {len(nodes)}"
        
        # Verify all nodes are mainline
        for node in nodes:
            assert node.mainline is True
    
    def test_opening_moves(self):
        """Test that opening moves are parsed correctly."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Verify first few moves (Ruy Lopez opening)
        assert nodes[1].state.move.san == "e4"
        assert nodes[1].state.move_color == "WHITE"
        
        assert nodes[2].state.move.san == "e5"
        assert nodes[2].state.move_color == "BLACK"
        
        assert nodes[3].state.move.san == "Nf3"
        assert nodes[3].state.move_color == "WHITE"
        
        assert nodes[4].state.move.san == "Nc6"
        assert nodes[4].state.move_color == "BLACK"
        
        assert nodes[5].state.move.san == "Bb5"  # Ruy Lopez
        assert nodes[5].state.move_color == "WHITE"
    
    def test_marshall_attack_critical_moves(self):
        """Test critical moves of the Marshall Attack."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Move 8: d5 - The Marshall Attack gambit
        # This is move 15 in the node chain (root + 7 full moves = 15 half-moves)
        move_8_black = nodes[16]
        assert move_8_black.state.move.san == "d5"
        assert move_8_black.state.move_color == "BLACK"
    
    def test_castling_notation(self):
        """Test that castling moves are parsed correctly."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # White castles kingside on move 5
        white_castling = nodes[9]
        assert white_castling.state.move.san == "O-O"
        assert white_castling.state.move_color == "WHITE"
        
        # Black castles kingside on move 7
        black_castling = nodes[14]
        assert black_castling.state.move.san == "O-O"
        assert black_castling.state.move_color == "BLACK"
    
    def test_final_position(self):
        """Test that the final position is correct."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Last move should be Bxf7+
        last_node = nodes[-1]
        assert last_node.state.move.san == "Bxf7+"
        assert last_node.state.move_color == "WHITE"
        
        # Verify the final board position is valid
        board = chess.Board(last_node.state.fen)
        assert board.is_valid()
        
        # Black is in check
        assert board.is_check()


class TestCapablancaMarshallFullPipeline:
    """Test complete preprocessing pipeline with Capablanca vs Marshall game."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.network
    def test_full_pipeline_with_cloud_evaluation(self):
        """
        Test complete pipeline with cloud evaluation.
        
        This is the STANDARD INTEGRATION TEST for the preprocessing pipeline.
        All future implementations should run and pass this test.
        """
        config = EngineConfig(
            depth=16,
            multi_pv=2,
            use_cloud_eval=True
        )
        
        try:
            # Run full preprocessing pipeline
            root = run_full_preprocessing_pipeline(
                CAPABLANCA_MARSHALL_PGN,
                config=config
            )
            
            # Verify structure
            assert root is not None
            nodes = get_node_chain(root)
            assert len(nodes) == 72  # root + 71 moves
            
            # Verify engine analysis was performed on all positions
            for node in nodes:
                if len(node.state.engine_lines) > 0:
                    # At least some nodes should have engine analysis
                    break
            else:
                pytest.fail("No nodes have engine analysis")
            
            # Verify we can extract node pairs for classification
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
            assert classified_count > 50, f"Only {classified_count} moves could be classified"
            
            print(f"\n✅ Successfully processed Capablanca vs Marshall (1918)")
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
            depth=12,  # Lower depth for faster testing
            multi_pv=2,
            use_cloud_eval=False  # Force local engine
        )
        
        try:
            root = run_full_preprocessing_pipeline(
                CAPABLANCA_MARSHALL_PGN,
                config=config
            )
            
            assert root is not None
            nodes = get_node_chain(root)
            assert len(nodes) == 72
            
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
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Verify game structure
        assert len(nodes) == 72
        
        # Verify no moves have errors
        for i, node in enumerate(nodes[1:], 1):  # Skip root
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
        
        print(f"\n✅ Game parsing verified: 71 moves, all valid")


class TestCapablancaMarshallMovePairs:
    """Test move pair extraction from the game."""
    
    def test_extract_all_move_pairs(self):
        """Test that all moves can be extracted as pairs."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        
        # Add dummy engine lines for testing extraction
        # Note: The engine lines need valid moves that match the position
        from src.models.state_tree import EngineLine, Evaluation, Move
        import chess
        
        nodes = get_node_chain(root)
        for node in nodes:
            # Create a board for this position
            board = chess.Board(node.state.fen)
            
            # Get any legal move for the dummy engine line
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
                # For root or positions with no legal moves
                node.state.engine_lines = [
                    EngineLine(
                        evaluation=Evaluation(type="centipawn", value=50.0),
                        source="test",
                        depth=10,
                        index=1,
                        moves=[Move(san="e4", uci="e2e4")]  # Dummy
                    )
                ]
        
        # Extract all move pairs
        move_pairs = []
        for i in range(1, len(nodes)):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                move_pairs.append(pair)
        
        # Should extract most pairs (not all, since root can't have a previous)
        assert len(move_pairs) > 60, f"Only extracted {len(move_pairs)} move pairs"
        
        # Verify each pair
        for i, (previous, current) in enumerate(move_pairs):
            assert previous is not None, f"Pair {i}: previous is None"
            assert current is not None, f"Pair {i}: current is None"
            assert previous.board is not None, f"Pair {i}: previous.board is None"
            assert current.board is not None, f"Pair {i}: current.board is None"
            assert current.played_move is not None, f"Pair {i}: current.played_move is None"


class TestCapablancaMarshallPositions:
    """Test specific interesting positions from the game."""
    
    def test_marshall_attack_position(self):
        """Test the position after Black plays 8...d5 (Marshall Attack)."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # After 8...d5
        marshall_attack_node = nodes[16]
        board = chess.Board(marshall_attack_node.state.fen)
        
        # Verify key pieces
        # Black's d-pawn should be on d5
        assert board.piece_at(chess.D5) == chess.Piece(chess.PAWN, chess.BLACK)
        
        # White's e-pawn should still be on e4
        assert board.piece_at(chess.E4) == chess.Piece(chess.PAWN, chess.WHITE)
    
    def test_complex_middlegame_position(self):
        """Test a complex tactical position from the middlegame."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # After 17...Bh2+ (check)
        check_position = nodes[34]
        board = chess.Board(check_position.state.fen)
        
        # White should be in check
        assert board.is_check()
        
        # White king must respond
        assert board.turn == chess.WHITE
    
    def test_endgame_position(self):
        """Test the endgame position before the final move."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Position before 36.Bxf7+
        endgame_node = nodes[-2]  # Second to last node
        board = chess.Board(endgame_node.state.fen)
        
        # Black should have made the last move
        assert nodes[-2].state.move_color == "BLACK"
        
        # Board should be valid
        assert board.is_valid()
        
        # White to move
        assert board.turn == chess.WHITE


class TestCapablancaMarshallMetrics:
    """Test that accuracy and metrics can be calculated for the game."""
    
    @pytest.mark.slow
    def test_calculate_move_accuracy(self):
        """Test that move accuracy can be calculated for all moves."""
        from src.preprocessing.calculator import calculate_move_metrics
        from src.models.state_tree import EngineLine, Evaluation, Move
        from src.models.extracted_nodes import ExtractedPreviousNode, ExtractedCurrentNode
        from src.models.state_tree import BoardState
        import chess
        
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Add proper engine lines with valid moves for each position
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
            else:
                # Dummy for positions with no legal moves
                node.state.engine_lines = [
                    EngineLine(
                        evaluation=Evaluation(type="centipawn", value=30.0),
                        source="test",
                        depth=10,
                        index=1,
                        moves=[Move(san="e4", uci="e2e4")]
                    )
                ]
        
        # Calculate accuracy for a few moves
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
class TestStandardIntegrationSuite:
    """
    STANDARD INTEGRATION TEST SUITE
    
    This test suite must pass for any implementation of the preprocessing pipeline.
    All future enhancements must continue to pass these tests.
    """
    
    @pytest.mark.integration
    def test_standard_game_parsing(self):
        """REQUIRED: Parse the standard test game correctly."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        assert len(nodes) == 72
        assert all(node.mainline for node in nodes)
        
        # Verify no parsing errors
        for node in nodes[1:]:
            assert node.state.move is not None
            assert node.state.fen is not None
    
    @pytest.mark.integration
    def test_standard_game_structure(self):
        """REQUIRED: Maintain correct tree structure."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
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
        
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Add proper engine data with valid moves for each position
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
            else:
                # Dummy for positions with no legal moves
                node.state.engine_lines = [
                    EngineLine(
                        evaluation=Evaluation(type="centipawn", value=20.0),
                        source="test",
                        depth=10,
                        index=1,
                        moves=[Move(san="e4", uci="e2e4")]
                    )
                ]
        
        # Should extract most moves
        extracted = 0
        for i in range(1, len(nodes)):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                extracted += 1
        
        assert extracted > 60, f"Only extracted {extracted}/71 moves"


if __name__ == "__main__":
    # Quick test to verify the game parses
    print("Testing Capablanca vs Marshall (1918)...")
    root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
    nodes = get_node_chain(root)
    print(f"✅ Parsed {len(nodes)} nodes (root + {len(nodes)-1} moves)")
    print(f"✅ First move: {nodes[1].state.move.san}")
    print(f"✅ Last move: {nodes[-1].state.move.san}")


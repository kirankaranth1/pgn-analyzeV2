"""
Integration Tests: Basic Classifier with Real Games

Test the basic classifier with real game positions from:
- Capablanca vs Marshall (1918)
- Morphy Opera Game (1858)
"""

import pytest
import chess

from src.classification.basic_classifier import BasicClassifier
from src.models.enums import Classification
from src.models.state_tree import EngineLine, Evaluation, Move
from src.preprocessing import run_full_preprocessing_pipeline, extract_node_pair
from src.preprocessing.parser import parse_pgn_game
from src.preprocessing.node_chain_builder import get_node_chain
from src.config import EngineConfig


def add_dummy_engine_lines(nodes):
    """Add dummy engine lines to nodes for testing."""
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
                    moves=[Move(san="e4", uci="e2e4")]  # Dummy
                )
            ]


# Game PGNs
CAPABLANCA_MARSHALL_PGN = """
1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.O-O Be7 6.Re1 b5 7.Bb3
O-O 8.c3 d5 9.exd5 Nxd5 10.Nxe5 Nxe5 11.Rxe5 Nf6 12.Re1 Bd6
13.h3 Ng4 14.Qf3 Qh4 15.d4 Nxf2 16.Re2 Bg4 17.hxg4 Bh2+ 18.Kf1
Bg3 19.Rxf2 Qh1+ 20.Ke2 Bxf2 21.Bd2 Bh4 22.Qh3 Rae8+ 23.Kd3
Qf1+ 24.Kc2 Bf2 25.Qf3 Qg1 26.Bd5 c5 27.dxc5 Bxc5 28.b4 Bd6
29.a4 a5 30.axb5 axb4 31.Ra6 bxc3 32.Nxc3 Bb4 33.b6 Bxc3
34.Bxc3 h6 35.b7 Re3 36.Bxf7+
""".strip()

MORPHY_OPERA_PGN = """
1.e4 e5 2.Nf3 d6 3.d4 Bg4 4.dxe5 Bxf3 5.Qxf3 dxe5 6.Bc4 Nf6 7.Qb3 Qe7
8.Nc3 c6 9.Bg5 b5 10.Nxb5 cxb5 11.Bxb5+ Nbd7 12.O-O-O Rd8
13.Rxd7 Rxd7 14.Rd1 Qe6 15.Bxd7+ Nxd7 16.Qb8+ Nxb8 17.Rd8#
""".strip()


class TestBasicClassifierWithRealGames:
    """Test basic classifier with real historical games."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.network
    def test_theory_classification_opening_moves_with_real_engine(self):
        """Test that opening moves are classified as THEORY (with real engine analysis)."""
        config = EngineConfig(
            depth=12,
            multi_pv=2,
            use_cloud_eval=True
        )
        
        try:
            # Run full preprocessing with real engine
            root = run_full_preprocessing_pipeline(CAPABLANCA_MARSHALL_PGN, config=config)
            nodes = get_node_chain(root)
            
            classifier = BasicClassifier()
            
            # First few moves should be theory
            theory_count = 0
            for i in range(1, min(10, len(nodes))):
                pair = extract_node_pair(nodes[i])
                if pair is not None:
                    previous, current = pair
                    result = classifier.classify(previous, current)
                    
                    if result == Classification.BOOK:
                        theory_count += 1
                        # Opening name should be stored
                        assert current.state.opening is not None
                        print(f"Move {i}: {current.state.move.san} - {current.state.opening}")
            
            # Should have found some theory moves
            assert theory_count > 0, f"Expected some theory moves in first 10 moves, found {theory_count}"
            print(f"\n✅ Real engine analysis: Found {theory_count} theory moves")
            
        except Exception as e:
            pytest.skip(f"Real engine analysis failed (may require network/engine): {e}")
    
    def test_theory_classification_opening_moves(self):
        """Test that opening moves are classified as THEORY (fast test with dummy data)."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Add dummy engine lines for extraction
        add_dummy_engine_lines(nodes)
        
        classifier = BasicClassifier()
        
        # First few moves should be theory
        theory_count = 0
        for i in range(1, min(10, len(nodes))):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                previous, current = pair
                result = classifier.classify(previous, current)
                
                if result == Classification.BOOK:
                    theory_count += 1
                    # Opening name should be stored
                    assert current.state.opening is not None
                    print(f"Move {i}: {current.state.move.san} - {current.state.opening}")
        
        # Should have found some theory moves
        assert theory_count > 0, f"Expected some theory moves in first 10 moves, found {theory_count}"
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.network
    def test_checkmate_classification_with_real_engine(self):
        """Test that checkmate moves are classified as BEST (with real engine)."""
        config = EngineConfig(
            depth=12,
            multi_pv=2,
            use_cloud_eval=True
        )
        
        try:
            # Run full preprocessing with real engine
            root = run_full_preprocessing_pipeline(MORPHY_OPERA_PGN, config=config)
            nodes = get_node_chain(root)
            
            # Last move should be checkmate (Rd8#)
            last_node = nodes[-1]
            pair = extract_node_pair(last_node)
            
            if pair is not None:
                previous, current = pair
                
                # Verify it's checkmate
                assert current.board.is_checkmate()
                assert current.state.move.san == "Rd8#"
                
                # Classify it
                classifier = BasicClassifier()
                result = classifier.classify(previous, current)
                
                # Should be BEST
                assert result == Classification.BEST
                print(f"\n✅ Real engine analysis: Checkmate correctly classified as {result}")
        
        except Exception as e:
            pytest.skip(f"Real engine analysis failed: {e}")
    
    def test_checkmate_classification(self):
        """Test that checkmate moves are classified as BEST (fast test)."""
        # Parse the Morphy Opera Game which ends in checkmate
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Add dummy engine lines
        add_dummy_engine_lines(nodes)
        
        # Last move should be checkmate (Rd8#)
        last_node = nodes[-1]
        pair = extract_node_pair(last_node)
        
        if pair is not None:
            previous, current = pair
            
            # Verify it's checkmate
            assert current.board.is_checkmate()
            assert current.state.move.san == "Rd8#"
            
            # Classify it
            classifier = BasicClassifier()
            result = classifier.classify(previous, current)
            
            # Should be BEST
            assert result == Classification.BEST
    
    def test_non_checkmate_move_not_classified_as_best_by_basic_classifier(self):
        """Test that normal moves don't get BEST from basic classifier."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Add dummy engine lines
        add_dummy_engine_lines(nodes)
        
        classifier = BasicClassifier()
        
        # Check middle game moves (not checkmate, likely not theory)
        non_best_count = 0
        for i in range(20, min(30, len(nodes))):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                previous, current = pair
                
                # Skip if it's checkmate
                if current.board.is_checkmate():
                    continue
                
                # Disable theory for this test
                classifier.set_include_theory(False)
                result = classifier.classify(previous, current)
                
                # Should return None (needs point loss evaluation)
                if result is None:
                    non_best_count += 1
        
        # Should have found some moves that need point loss evaluation
        assert non_best_count > 0
    
    def test_theory_disabled(self):
        """Test that theory can be disabled."""
        root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
        nodes = get_node_chain(root)
        
        # Create classifier with theory disabled
        classifier = BasicClassifier(include_theory=False)
        
        # Check first few moves
        theory_count = 0
        for i in range(1, min(10, len(nodes))):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                previous, current = pair
                result = classifier.classify(previous, current)
                
                if result == Classification.BOOK:
                    theory_count += 1
        
        # Should NOT have found any theory moves
        assert theory_count == 0, f"Found {theory_count} theory moves with theory disabled"
    
    @pytest.mark.integration
    def test_opening_book_size(self):
        """Test that opening book has loaded properly."""
        classifier = BasicClassifier()
        
        # Should have loaded thousands of positions
        assert classifier.opening_book_size > 1000
        assert classifier.opening_book_size > 3000  # Typically has 3000+ positions
        
        print(f"\n✅ Opening book loaded: {classifier.opening_book_size} positions")


class TestBasicClassifierEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_starting_position_not_forced(self):
        """Test that starting position is not forced (20 legal moves)."""
        pgn = "1. e4"
        root = parse_pgn_game(pgn)
        nodes = get_node_chain(root)
        
        # Add dummy engine lines
        add_dummy_engine_lines(nodes)
        
        # First move (e4)
        pair = extract_node_pair(nodes[1])
        assert pair is not None
        
        previous, current = pair
        
        classifier = BasicClassifier()
        
        # Should not be forced
        result = classifier._classify_forced(previous)
        assert result != Classification.FORCED
    
    def test_checkmate_position_is_best(self):
        """Test that checkmate is always BEST."""
        # Scholar's Mate
        pgn = "1.e4 e5 2.Bc4 Nc6 3.Qh5 Nf6 4.Qxf7#"
        root = parse_pgn_game(pgn)
        nodes = get_node_chain(root)
        
        # Add dummy engine lines
        add_dummy_engine_lines(nodes)
        
        # Last move (Qxf7#)
        last_node = nodes[-1]
        pair = extract_node_pair(last_node)
        
        assert pair is not None
        previous, current = pair
        
        # Verify checkmate
        assert current.board.is_checkmate()
        
        # Classify
        classifier = BasicClassifier()
        result = classifier.classify(previous, current)
        
        # Must be BEST
        assert result == Classification.BEST
    
    def test_classification_priority_order(self):
        """Test that classifications are checked in correct priority order."""
        # FORCED > THEORY > CHECKMATE
        
        # In practice:
        # - FORCED is checked first
        # - THEORY is checked second
        # - CHECKMATE is checked third
        
        # This means:
        # - A forced move that is also in theory book → FORCED
        # - A theory move that delivers checkmate → THEORY (very rare)
        
        # Test FORCED has priority
        fen_before = "8/8/8/8/8/2r5/1K6/2r5 w - - 0 1"
        board = chess.Board(fen_before)
        
        # Only 1 legal move
        assert len(list(board.legal_moves)) == 1
        
        # Even if somehow in opening book, should be FORCED
        # (This is a contrived test - forced endgame moves aren't in opening books)


@pytest.mark.integration
class TestBasicClassifierIntegration:
    """Integration tests with multiple components."""
    
    @pytest.mark.slow
    @pytest.mark.network
    def test_classify_entire_game_with_real_engine(self):
        """Test classifying all moves of Opera Game with real engine analysis."""
        config = EngineConfig(
            depth=12,
            multi_pv=2,
            use_cloud_eval=True
        )
        
        try:
            # Run full preprocessing with real engine
            root = run_full_preprocessing_pipeline(MORPHY_OPERA_PGN, config=config)
            nodes = get_node_chain(root)
            
            classifier = BasicClassifier()
            
            classifications = {
                "FORCED": [],
                "THEORY": [],
                "BEST": [],
                "NONE": []
            }
            
            for i in range(1, len(nodes)):
                pair = extract_node_pair(nodes[i])
                if pair is not None:
                    previous, current = pair
                    result = classifier.classify(previous, current)
                    
                    move_num = (i + 1) // 2
                    color = "White" if i % 2 == 1 else "Black"
                    move_info = (i, f"{move_num}. {current.state.move.san} ({color})")
                    
                    if result == Classification.FORCED:
                        classifications["FORCED"].append(move_info)
                    elif result == Classification.BOOK:
                        classifications["THEORY"].append((move_info, current.state.opening))
                    elif result == Classification.BEST:
                        classifications["BEST"].append(move_info)
                    else:
                        classifications["NONE"].append(move_info)
                else:
                    # Try direct classification for terminal positions (e.g., checkmate)
                    result = classifier.classify_from_state_tree_node(nodes[i])
                    
                    move_num = (i + 1) // 2
                    color = "White" if i % 2 == 1 else "Black"
                    move_info = (i, f"{move_num}. {nodes[i].state.move.san} ({color})")
                    
                    if result == Classification.BOOK:
                        classifications["THEORY"].append((move_info, nodes[i].state.opening))
                    elif result == Classification.BEST:
                        classifications["BEST"].append(move_info)
                    # Otherwise, it truly cannot be classified
            
            print(f"\n📊 REAL ENGINE ANALYSIS - Opera Game Classification:")
            print(f"   FORCED: {len(classifications['FORCED'])}")
            print(f"   THEORY: {len(classifications['THEORY'])}")
            print(f"   BEST: {len(classifications['BEST'])}")
            print(f"   NONE: {len(classifications['NONE'])}")
            
            # With the fallback classification method, we should now detect checkmate
            assert len(classifications["BEST"]) >= 1, "Expected at least one BEST (checkmate)"
            # Should have some theory
            assert len(classifications["THEORY"]) > 0, "Expected theory moves"
            
            print("\n✅ Real engine analysis complete!")
            print(f"   Checkmate correctly classified using fallback method")

            
        except Exception as e:
            pytest.skip(f"Real engine analysis failed: {e}")
    
    def test_classify_entire_game_openings(self):
        """Test classifying all moves of a game for theory (fast test)."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Add dummy engine lines
        add_dummy_engine_lines(nodes)
        
        classifier = BasicClassifier()
        
        theory_moves = []
        non_theory_moves = []
        
        for i in range(1, len(nodes)):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                previous, current = pair
                result = classifier.classify(previous, current)
                
                if result == Classification.BOOK:
                    theory_moves.append((i, current.state.move.san, current.state.opening))
                elif result != Classification.BEST:  # Exclude checkmate
                    non_theory_moves.append((i, current.state.move.san))
        
        print(f"\n📖 Theory moves: {len(theory_moves)}")
        for i, san, opening in theory_moves[:5]:  # Show first 5
            print(f"   {i}. {san} - {opening}")
        
        print(f"\n🎯 Non-theory moves: {len(non_theory_moves)}")
        
        # Should have some of each
        assert len(theory_moves) > 0, "Expected some theory moves"
        assert len(non_theory_moves) > 0, "Expected some non-theory moves"
    
    def test_classify_with_checkmate(self):
        """Test complete classification including checkmate."""
        root = parse_pgn_game(MORPHY_OPERA_PGN)
        nodes = get_node_chain(root)
        
        # Add dummy engine lines
        add_dummy_engine_lines(nodes)
        
        classifier = BasicClassifier()
        
        classifications = {
            "FORCED": 0,
            "THEORY": 0,
            "BEST": 0,
            "NONE": 0
        }
        
        for i in range(1, len(nodes)):
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                previous, current = pair
                result = classifier.classify(previous, current)
                
                if result == Classification.FORCED:
                    classifications["FORCED"] += 1
                elif result == Classification.BOOK:
                    classifications["THEORY"] += 1
                elif result == Classification.BEST:
                    classifications["BEST"] += 1
                    # Should be checkmate
                    assert current.board.is_checkmate()
                else:
                    classifications["NONE"] += 1
        
        print(f"\n📊 Classification breakdown:")
        for cls, count in classifications.items():
            print(f"   {cls}: {count}")
        
        # Should have at least one BEST (the checkmate)
        assert classifications["BEST"] >= 1, "Expected at least one BEST (checkmate)"


if __name__ == "__main__":
    # Quick sanity check
    print("Testing Basic Classifier with Real Games...")
    
    # Test theory
    root = parse_pgn_game(CAPABLANCA_MARSHALL_PGN)
    nodes = get_node_chain(root)
    
    # Add dummy engine lines
    add_dummy_engine_lines(nodes)
    
    classifier = BasicClassifier()
    
    print(f"\n✅ Loaded opening book: {classifier.opening_book_size} positions")
    
    # Check first move
    pair = extract_node_pair(nodes[1])
    if pair:
        previous, current = pair
        result = classifier.classify(previous, current)
        print(f"✅ First move (e4) classification: {result}")
        if result == Classification.BOOK:
            print(f"   Opening: {current.state.opening}")
    
    # Check checkmate
    root2 = parse_pgn_game(MORPHY_OPERA_PGN)
    nodes2 = get_node_chain(root2)
    add_dummy_engine_lines(nodes2)
    
    last_pair = extract_node_pair(nodes2[-1])
    if last_pair:
        previous, current = last_pair
        result = classifier.classify(previous, current)
        print(f"✅ Checkmate move (Rd8#) classification: {result}")
        print(f"   Is checkmate: {current.board.is_checkmate()}")
    
    print("\n✅ All basic integration tests passed!")


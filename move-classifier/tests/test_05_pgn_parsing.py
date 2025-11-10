"""Test 5: PGN parsing - test PGN file parsing and state tree building."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser.pgn_parser import PGNParser
from src.parser.state_tree_builder import StateTreeBuilder


def test_parse_simple_pgn():
    """Test parsing a simple PGN string."""
    pgn_content = """
[Event "Test Game"]
[Site "Test"]
[Date "2024.01.01"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0
"""
    
    game = PGNParser.parse_game(pgn_content)
    assert game is not None
    
    headers = PGNParser.extract_headers(game)
    assert headers["white"] == "Player1"
    assert headers["black"] == "Player2"
    assert headers["result"] == "1-0"
    assert headers["event"] == "Test Game"
    
    print("✓ Simple PGN parsing works")


def test_build_state_tree():
    """Test building state tree from PGN."""
    pgn_content = """
[Event "Test Game"]
[Site "Test"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 1-0
"""
    
    game = PGNParser.parse_game(pgn_content)
    assert game is not None
    
    root = StateTreeBuilder.build_tree(game)
    assert root is not None
    assert root.state.fen is not None
    
    # Check that moves were added
    mainline = root.traverse_mainline()
    # Should have root + moves (at least 4: e4, e5, Nf3, and possibly more)
    assert len(mainline) >= 3
    
    print("✓ State tree building works")


def test_header_extraction():
    """Test extracting various headers."""
    pgn_content = """
[Event "World Championship"]
[Site "Moscow"]
[Date "1985.11.09"]
[Round "24"]
[White "Kasparov"]
[Black "Karpov"]
[Result "1-0"]
[WhiteElo "2700"]
[BlackElo "2720"]

1. e4 1-0
"""
    
    game = PGNParser.parse_game(pgn_content)
    headers = PGNParser.extract_headers(game)
    
    assert headers["event"] == "World Championship"
    assert headers["site"] == "Moscow"
    assert headers["white"] == "Kasparov"
    assert headers["black"] == "Karpov"
    assert headers["white_elo"] == "2700"
    assert headers["black_elo"] == "2720"
    
    print("✓ Header extraction works")


def test_parse_example_pgn():
    """Test parsing the included example.pgn file."""
    example_path = Path(__file__).parent.parent / "example.pgn"
    
    if example_path.exists():
        game = PGNParser.parse_file(str(example_path))
        assert game is not None
        
        headers = PGNParser.extract_headers(game)
        assert headers["white"] == "Player1"
        assert headers["black"] == "Player2"
        
        # Build state tree
        root = StateTreeBuilder.build_tree(game)
        mainline = root.traverse_mainline()
        
        # Example game has many moves
        assert len(mainline) > 10
        
        print(f"✓ Example PGN parsing works ({len(mainline)} positions)")
    else:
        print("⚠ example.pgn not found, test skipped")


def test_move_extraction():
    """Test that moves are correctly extracted."""
    pgn_content = """
[Event "Test"]
[Site "Test"]
[Date "2024.01.01"]
[White "W"]
[Black "B"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 *
"""
    
    game = PGNParser.parse_game(pgn_content)
    root = StateTreeBuilder.build_tree(game)
    mainline = root.traverse_mainline()
    
    # Skip root, check first few moves
    moves = [node.state.move for node in mainline[1:] if node.state.move]
    
    assert len(moves) >= 4
    assert moves[0].san == "e4"
    assert moves[1].san == "e5"
    assert moves[2].san == "Nf3"
    assert moves[3].san == "Nc6"
    
    print("✓ Move extraction works")


def test_fen_in_state_tree():
    """Test that FEN strings are correct in state tree."""
    pgn_content = """
[Event "Test"]
[Site "Test"]
[Date "2024.01.01"]
[White "W"]
[Black "B"]
[Result "*"]

1. e4 *
"""
    
    game = PGNParser.parse_game(pgn_content)
    root = StateTreeBuilder.build_tree(game)
    
    # Check root FEN is starting position
    assert "rnbqkbnr/pppppppp" in root.state.fen
    
    # Check after e4
    mainline = root.traverse_mainline()
    if len(mainline) > 1:
        after_e4 = mainline[1]
        assert "4P3" in after_e4.state.fen  # e4 square occupied
    
    print("✓ FEN strings in state tree correct")


if __name__ == "__main__":
    print("Running PGN parsing tests...\n")
    test_parse_simple_pgn()
    test_build_state_tree()
    test_header_extraction()
    test_parse_example_pgn()
    test_move_extraction()
    test_fen_in_state_tree()
    print("\n✅ All PGN parsing tests passed!")


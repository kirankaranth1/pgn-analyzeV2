#!/usr/bin/env python3
"""
Demo: Checkmate Classification Fallback

Demonstrates how the BasicClassifier now handles terminal positions
(checkmate) even when engine analysis is unavailable.

This solves the problem where checkmate positions couldn't be extracted
because engines don't analyze terminal positions.
"""

import sys
import chess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.classification.basic_classifier import BasicClassifier
from src.models.state_tree import StateTreeNode, BoardState, Move
from src.models.enums import PieceColor, Classification
from src.preprocessing import parse_pgn_game
from src.preprocessing.node_extractor import (
    extract_previous_state_tree_node,
    extract_current_state_tree_node
)


def extract_node_pair(node):
    """Extract (previous, current) node pair or None if extraction fails."""
    if not node.parent:
        return None
    
    previous = extract_previous_state_tree_node(node.parent)
    current = extract_current_state_tree_node(node)
    
    if previous is None or current is None:
        return None
    
    return (previous, current)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print('='*80)


def demo_direct_classification():
    """Demonstrate direct classification from StateTreeNode."""
    print_section("DEMO 1: Direct Classification (No Engine Data)")
    
    # Create a checkmate position without engine lines
    fen = "4R1k1/5ppp/8/8/8/8/5PPP/6K1 b - - 1 1"
    
    node = StateTreeNode(
        id="test-checkmate",
        mainline=True,
        state=BoardState(
            fen=fen,
            move=Move(san="Re8#", uci="e1e8"),
            move_color=PieceColor.WHITE,
            engine_lines=[],  # No engine lines!
            classification=None,
            accuracy=None,
            opening=None
        ),
        parent=None,
        children=[]
    )
    
    print("\nPosition FEN:", fen)
    print("Move played:", node.state.move.san)
    print("Engine lines:", len(node.state.engine_lines))
    
    # Try extraction (will fail)
    pair = extract_node_pair(node)
    print(f"\nExtraction successful: {pair is not None}")
    
    if pair is None:
        print("❌ Cannot use standard classify() method (requires extraction)")
        
        # Use fallback method
        classifier = BasicClassifier()
        result = classifier.classify_from_state_tree_node(node)
        
        print(f"\n✅ Fallback classify_from_state_tree_node() result:")
        print(f"   Classification: {result}")
        print(f"   Explanation: Checkmate detected directly from board state")


def demo_real_game_checkmate():
    """Demonstrate with a real game ending in checkmate."""
    print_section("DEMO 2: Real Game - Morphy Opera Game (1858)")
    
    # Morphy Opera Game
    pgn = """
    1.e4 e5 2.Nf3 d6 3.d4 Bg4 4.dxe5 Bxf3 5.Qxf3 dxe5 6.Bc4 Nf6 7.Qb3 Qe7
    8.Nc3 c6 9.Bg5 b5 10.Nxb5 cxb5 11.Bxb5+ Nbd7 12.O-O-O Rd8
    13.Rxd7 Rxd7 14.Rd1 Qe6 15.Bxd7+ Nxd7 16.Qb8+ Nxb8 17.Rd8#
    """.strip()
    
    print("Game: Paul Morphy vs Duke Karl / Count Isouard")
    print("Result: 1-0 (checkmate)")
    
    # Parse without engine analysis (simulating missing engine data for checkmate)
    print("\n⏳ Parsing game...")
    root = parse_pgn_game(pgn)
    
    # Collect all nodes in mainline
    nodes = []
    current = root
    while current:
        nodes.append(current)
        # Get first child (mainline)
        if current.children:
            current = current.children[0]
        else:
            break
    
    # Get the final move (checkmate)
    final_node = nodes[-1]
    
    print(f"\n📊 Final Move:")
    print(f"   Move: {final_node.state.move.san}")
    print(f"   FEN: {final_node.state.fen}")
    
    # Check if position is actually checkmate
    board = chess.Board(final_node.state.fen)
    print(f"   Is checkmate: {board.is_checkmate()}")
    print(f"   Engine lines: {len(final_node.state.engine_lines)}")
    
    # Try extraction
    pair = extract_node_pair(final_node)
    print(f"\n🔍 Extraction Result:")
    print(f"   Extractable: {pair is not None}")
    
    classifier = BasicClassifier()
    
    if pair is not None:
        # Standard classification
        previous, current = pair
        result = classifier.classify(previous, current)
        print(f"\n✅ Standard Classification:")
        print(f"   Method: classify()")
        print(f"   Result: {result}")
    else:
        # Fallback classification
        result = classifier.classify_from_state_tree_node(final_node)
        print(f"\n✅ Fallback Classification:")
        print(f"   Method: classify_from_state_tree_node()")
        print(f"   Result: {result}")
        print(f"   Note: Works without engine analysis!")


def demo_comparison():
    """Compare standard vs fallback classification."""
    print_section("DEMO 3: Method Comparison")
    
    print("\n📋 Standard classify() Method:")
    print("   • Requires: ExtractedPreviousNode + ExtractedCurrentNode")
    print("   • Needs: Engine analysis for both nodes")
    print("   • Checks: FORCED, THEORY, CHECKMATE")
    print("   • Fails: When extraction returns None")
    
    print("\n📋 Fallback classify_from_state_tree_node() Method:")
    print("   • Requires: Only StateTreeNode")
    print("   • Needs: Just FEN and move")
    print("   • Checks: THEORY, CHECKMATE")
    print("   • Works: Even without engine analysis")
    
    print("\n💡 Use Cases:")
    print("   Standard: Normal positions with engine data")
    print("   Fallback: Terminal positions (checkmate, stalemate)")
    print("            Positions where engine analysis unavailable")
    
    print("\n🎯 Why This Matters:")
    print("   • Engines don't analyze positions that are already over")
    print("   • Without fallback, checkmates would show as 'N/A'")
    print("   • Fallback ensures complete classification coverage")


def main():
    """Run all demonstrations."""
    print("\n" + "🏆" * 40)
    print("CHECKMATE CLASSIFICATION FALLBACK DEMO")
    print("🏆" * 40)
    
    try:
        demo_direct_classification()
        demo_real_game_checkmate()
        demo_comparison()
        
        print_section("SUMMARY")
        print("\n✅ All demonstrations completed successfully!")
        print("\n📚 Key Takeaway:")
        print("   The BasicClassifier now handles terminal positions gracefully")
        print("   by falling back to direct state tree node analysis when")
        print("   extraction fails due to missing engine analysis.")
        print("\n📄 For more details, see: CHECKMATE_CLASSIFICATION_FIX.md")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


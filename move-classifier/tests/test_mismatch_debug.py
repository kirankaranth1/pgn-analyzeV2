#!/usr/bin/env python3
"""
Unit tests for debugging mismatched moves with multi_pv=2, depth=16.

Run with: python -m pytest tests/test_mismatch_debug.py -v -s
Debug mode: python -m pytest tests/test_mismatch_debug.py::test_move_6_bg4 -v -s --pdb
"""

import sys
import os
import chess
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.engine_config import EngineConfig
from src.engine.stockfish_engine import StockfishEngine
from src.core.types import PieceColor
from src.classification.node_extractor import NodeExtractor, ExtractedPreviousNode, ExtractedCurrentNode
from src.classification.point_loss import classify_by_point_loss, calculate_accuracy
from src.analysis.expected_points import get_expected_points, get_subjective_evaluation
from src.core.state_tree import StateTreeNode, BoardState
from src.core.move import Move as CustomMove


def create_test_node_from_fen(fen: str, move_san: str, engine_config: EngineConfig) -> tuple:
    """
    Create test nodes for a position and move.
    
    Returns: (parent_node, current_node, engine_lines_before, engine_lines_after)
    """
    engine = StockfishEngine(engine_config)
    
    # Create parent board (before move)
    parent_board = chess.Board(fen)
    
    # Analyze parent position
    print(f"\n  Analyzing parent position: {fen}")
    engine_lines_before = engine.analyze_position(fen)
    print(f"  Found {len(engine_lines_before)} engine lines")
    for i, line in enumerate(engine_lines_before):
        if line.moves:
            print(f"    Line {i+1}: {line.moves[0].san} eval={line.evaluation.type}:{line.evaluation.value}")
    
    # Make the move
    move = parent_board.parse_san(move_san)
    parent_board.push(move)
    fen_after = parent_board.fen()
    
    # Analyze position after move
    print(f"  Analyzing position after {move_san}: {fen_after}")
    engine_lines_after = engine.analyze_position(fen_after)
    print(f"  Found {len(engine_lines_after)} engine lines")
    for i, line in enumerate(engine_lines_after):
        if line.moves:
            print(f"    Line {i+1}: {line.moves[0].san} eval={line.evaluation.type}:{line.evaluation.value}")
    
    # No need to close - engine handles cleanup automatically
    
    # Convert chess.Move to our CustomMove
    played_move = CustomMove(
        san=move_san,
        uci=move.uci(),
        from_square=chess.square_name(move.from_square),
        to_square=chess.square_name(move.to_square),
        piece=parent_board.piece_type_at(move.to_square),
        color=PieceColor.WHITE if parent_board.turn == chess.BLACK else PieceColor.BLACK,
        captured=parent_board.piece_type_at(move.to_square) if parent_board.is_capture(move) else None,
        promotion=move.promotion
    )
    
    return engine_lines_before, engine_lines_after, played_move


def debug_classification(fen_before: str, move_san: str, expected_class: str, 
                         stockfish_path: str = "/opt/homebrew/bin/stockfish"):
    """
    Debug a single move classification.
    """
    print(f"\n{'='*80}")
    print(f"DEBUGGING: {move_san} (Expected: {expected_class})")
    print(f"{'='*80}")
    print(f"Position before move: {fen_before}")
    
    # Setup
    config = EngineConfig(
        stockfish_path=stockfish_path,
        depth=16,
        multi_pv=2
    )
    
    # Get engine analysis
    engine_lines_before, engine_lines_after, played_move = create_test_node_from_fen(
        fen_before, move_san, config
    )
    
    # Create mock nodes for classification
    parent_board = chess.Board(fen_before)
    parent_board.push(parent_board.parse_san(move_san))
    current_board = chess.Board(parent_board.fen())
    
    # Build state tree nodes
    parent_state = BoardState(
        fen=fen_before,
        move=None,
        engine_lines=engine_lines_before
    )
    parent_node = StateTreeNode(state=parent_state, parent=None, id="parent")
    
    current_state = BoardState(
        fen=current_board.fen(),
        move=played_move,
        engine_lines=engine_lines_after
    )
    current_node = StateTreeNode(state=current_state, parent=parent_node, id="current")
    
    # Extract nodes
    extractor = NodeExtractor()
    previous = extractor.extract_previous_node(current_node)
    current = extractor.extract_current_node(current_node)
    
    if not previous or not current:
        print("ERROR: Failed to extract nodes!")
        return None
    
    # Debug output
    print(f"\n{'='*80}")
    print("EXTRACTED NODE DATA:")
    print(f"{'='*80}")
    
    print(f"\nPREVIOUS NODE (before move):")
    print(f"  Player color: {previous.player_color}")
    print(f"  Top line eval: {previous.evaluation.type}:{previous.evaluation.value}")
    print(f"  Subjective eval: {previous.subjective_evaluation.type}:{previous.subjective_evaluation.value}")
    if previous.top_move:
        print(f"  Top move: {previous.top_move.san}")
    if previous.played_move:
        print(f"  Played move: {previous.played_move.san}")
    if previous.played_move_evaluation:
        print(f"  Played move eval (from multi-PV): {previous.played_move_evaluation.type}:{previous.played_move_evaluation.value}")
    else:
        print(f"  Played move eval: NOT FOUND in multi-PV")
    
    print(f"\nCURRENT NODE (after move):")
    print(f"  Player color: {current.player_color}")
    print(f"  Top line eval: {current.evaluation.type}:{current.evaluation.value}")
    print(f"  Subjective eval: {current.subjective_evaluation.type}:{current.subjective_evaluation.value}")
    print(f"  Played move: {current.played_move.san}")
    
    # Calculate classification
    print(f"\n{'='*80}")
    print("POINT LOSS CALCULATION:")
    print(f"{'='*80}")
    
    # Check if using same-position comparison or fallback
    if previous.played_move_evaluation:
        print("\nUsing SAME-POSITION comparison (move found in multi-PV):")
        eval_before = previous.subjective_evaluation
        eval_after = previous.played_move_evaluation
        print(f"  eval_before (top move): {eval_before.type}:{eval_before.value}")
        print(f"  eval_after (played move): {eval_after.type}:{eval_after.value}")
        
        ep_before = get_expected_points(eval_before)
        ep_after = get_expected_points(eval_after)
        print(f"  EP(top move): {ep_before:.4f}")
        print(f"  EP(played move): {ep_after:.4f}")
        point_loss = max(0.0, ep_before - ep_after)
        print(f"  Point loss: {point_loss:.4f} ({point_loss*100:.2f}%)")
    else:
        print("\nUsing FALLBACK comparison (move NOT in multi-PV):")
        eval_before = previous.evaluation
        eval_after = current.evaluation
        print(f"  eval_before (raw): {eval_before.type}:{eval_before.value}")
        print(f"  eval_after (raw): {eval_after.type}:{eval_after.value}")
        
        ep_before = get_expected_points(eval_before)
        ep_after = get_expected_points(eval_after)
        print(f"  EP(before): {ep_before:.4f}")
        print(f"  EP(after): {ep_after:.4f}")
        
        color_mult = 1 if current.player_color == PieceColor.WHITE else -1
        point_loss = (ep_before - ep_after) * color_mult
        print(f"  (EP_before - EP_after) * {color_mult} = {point_loss:.4f}")
        point_loss = max(0.0, point_loss)
        print(f"  Point loss (after max): {point_loss:.4f} ({point_loss*100:.2f}%)")
    
    # Classify
    classification = classify_by_point_loss(previous, current)
    accuracy = calculate_accuracy(previous, current)
    
    print(f"\n{'='*80}")
    print("RESULT:")
    print(f"{'='*80}")
    print(f"  Classification: {classification.value}")
    print(f"  Accuracy: {accuracy:.2f}%")
    print(f"  Expected: {expected_class}")
    print(f"  Match: {'✓' if expected_class.lower() in classification.value.lower() else '✗'}")
    
    return classification.value


# Test cases for each mismatch
def test_move_6_bg4():
    """Move 6: Bg4 - Expected: excellent/okay, Got: mistake"""
    # Position after 1.e4 e5 2.Nf3 d6 3.d4 (Black to move)
    fen = "rnbqkbnr/ppp2ppp/3p4/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq d3 0 3"
    result = debug_classification(fen, "Bg4", "excellent/okay")
    # Uncomment to assert:
    # assert result in ["excellent", "okay"], f"Expected excellent/okay, got {result}"


def test_move_7_dxe5():
    """Move 7: dxe5 (White) - Expected: best/excellent, Got: mistake"""
    fen = "rn1qkbnr/ppp2ppp/3p4/4p3/3PP1b1/5N2/PPP2PPP/RNBQKB1R w KQkq - 1 4"
    result = debug_classification(fen, "dxe5", "best/excellent")
    # assert result in ["best", "excellent"], f"Expected best/excellent, got {result}"


def test_move_8_bxf3():
    """Move 8: Bxf3 - Expected: best, Got: blunder"""
    fen = "rn1qkbnr/ppp2ppp/3p4/4P3/4P3/5b2/PPP2PPP/RNBQKB1R w KQkq - 0 5"
    result = debug_classification(fen, "Bxf3", "best")
    # assert result == "best", f"Expected best, got {result}"


def test_move_12_nf6():
    """Move 12: Nf6 - Expected: best/excellent, Got: blunder"""
    fen = "rn1qkb1r/ppp2ppp/8/4p3/2B1P3/5Q2/PPP2PPP/RNB1K2R b KQkq - 1 6"
    result = debug_classification(fen, "Nf6", "best/excellent")
    # assert result in ["best", "excellent"], f"Expected best/excellent, got {result}"


def test_move_17_bg5():
    """Move 17: Bg5 - Expected: critical, Got: best"""
    fen = "rn2kb1r/pp2qppp/2p2n2/4p3/2B1P3/1QN5/PPP2PPP/R1B1K2R w KQkq - 0 9"
    result = debug_classification(fen, "Bg5", "critical")
    # assert result == "critical", f"Expected critical, got {result}"


def test_move_18_b5():
    """Move 18: b5 - Expected: inaccuracy, Got: blunder"""
    fen = "rn2kb1r/pp2qppp/2p2n2/4p1B1/2B1P3/1QN5/PPP2PPP/R3K2R b KQkq - 1 9"
    result = debug_classification(fen, "b5", "inaccuracy")
    # assert result == "inaccuracy", f"Expected inaccuracy, got {result}"


def test_move_20_cxb5():
    """Move 20: cxb5 - Expected: okay/inaccuracy, Got: blunder"""
    fen = "rn2kb1r/p3qppp/2p2n2/1p2p1B1/2B1P3/1QN5/PPP2PPP/R3K2R b KQkq - 0 10"
    result = debug_classification(fen, "cxb5", "okay/inaccuracy")
    # assert result in ["okay", "inaccuracy"], f"Expected okay/inaccuracy, got {result}"


def test_move_21_bxb5_check():
    """Move 21: Bxb5+ - Expected: critical, Got: best"""
    fen = "rn2kb1r/p3qppp/5n2/1p2p1B1/2B1P3/1Q6/PPP2PPP/R3K2R w KQkq - 0 11"
    result = debug_classification(fen, "Bxb5+", "critical")
    # assert result == "critical", f"Expected critical, got {result}"


def test_move_28_qe6():
    """Move 28: Qe6 - Expected: inaccuracy/okay, Got: blunder"""
    fen = "4kb1r/p2r1ppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR4 b k - 2 14"
    result = debug_classification(fen, "Qe6", "inaccuracy/okay")
    # assert result in ["inaccuracy", "okay"], f"Expected inaccuracy/okay, got {result}"


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MISMATCH DEBUGGING TESTS")
    print("="*80)
    print("\nRunning all mismatch tests...")
    print("Note: These tests show detailed debug output for each mismatched move.")
    print("="*80)
    
    tests = [
        ("Move 6: Bg4", test_move_6_bg4),
        ("Move 7: dxe5", test_move_7_dxe5),
        ("Move 8: Bxf3", test_move_8_bxf3),
        ("Move 12: Nf6", test_move_12_nf6),
        ("Move 17: Bg5", test_move_17_bg5),
        ("Move 18: b5", test_move_18_b5),
        ("Move 20: cxb5", test_move_20_cxb5),
        ("Move 21: Bxb5+", test_move_21_bxb5_check),
        ("Move 28: Qe6", test_move_28_qe6),
    ]
    
    for name, test_func in tests:
        print(f"\n\n{'#'*80}")
        print(f"# {name}")
        print(f"{'#'*80}")
        try:
            test_func()
        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()


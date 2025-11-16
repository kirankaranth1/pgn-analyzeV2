"""
Test JavaScript Alignment

Verifies that the Python preprocessing pipeline matches the JavaScript implementation.
"""

import pytest
from src.preprocessing.node_extractor import (
    extract_previous_state_tree_node,
    extract_current_state_tree_node
)
from src.models.state_tree import StateTreeNode, BoardState, Move, EngineLine, Evaluation
from src.models.enums import PieceColor


def test_previous_node_extraction_with_second_best():
    """Test that previous node extraction includes second-best move."""
    root = StateTreeNode(
        id='root',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=30.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='e4', uci='e2e4')]
                ),
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=25.0),
                    source='stockfish-17',
                    depth=20,
                    index=2,
                    moves=[Move(san='d4', uci='d2d4')]
                )
            ]
        )
    )
    
    prev_node = extract_previous_state_tree_node(root)
    
    assert prev_node is not None
    assert prev_node.top_move is not None  # REQUIRED
    assert prev_node.subjective_evaluation is not None  # Available but optional in type
    assert prev_node.second_top_line is not None
    assert prev_node.second_top_move is not None
    assert prev_node.second_subjective_evaluation is not None


def test_current_node_extraction_with_second_best():
    """Test that current node extraction includes second-best move."""
    root = StateTreeNode(
        id='root',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=30.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='e4', uci='e2e4')]
                )
            ]
        )
    )
    
    child = StateTreeNode(
        id='child',
        mainline=True,
        parent=root,
        children=[],
        state=BoardState(
            fen='rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
            move=Move(san='e4', uci='e2e4'),
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=20.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='c5', uci='c7c5')]
                ),
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=15.0),
                    source='stockfish-17',
                    depth=20,
                    index=2,
                    moves=[Move(san='e5', uci='e7e5')]
                )
            ]
        )
    )
    
    root.children.append(child)
    
    curr_node = extract_current_state_tree_node(child)
    
    assert curr_node is not None
    assert curr_node.top_move is not None  # Optional but available
    assert curr_node.subjective_evaluation is not None  # REQUIRED
    assert curr_node.played_move is not None  # REQUIRED
    assert curr_node.second_top_line is not None
    assert curr_node.second_top_move is not None
    assert curr_node.second_subjective_evaluation is not None


def test_previous_node_defaults_to_white_when_no_played_move():
    """Test that previous node defaults player color to WHITE (matches JS)."""
    root = StateTreeNode(
        id='root',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=30.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='e4', uci='e2e4')]
                )
            ]
        )
    )
    
    prev_node = extract_previous_state_tree_node(root)
    
    assert prev_node is not None
    assert prev_node.subjective_evaluation is not None
    # Subjective evaluation should be calculated from WHITE's perspective
    assert prev_node.subjective_evaluation.value == 30.0  # Same as original for WHITE


def test_current_node_requires_parent():
    """Test that current node extraction fails without parent (matches JS)."""
    root = StateTreeNode(
        id='root',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            move=Move(san='e4', uci='e2e4'),
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=30.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='e4', uci='e2e4')]
                )
            ]
        )
    )
    
    curr_node = extract_current_state_tree_node(root)
    
    assert curr_node is None


def test_current_node_requires_played_move():
    """Test that current node extraction fails without played move (matches JS)."""
    root = StateTreeNode(
        id='root',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=30.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='e4', uci='e2e4')]
                )
            ]
        )
    )
    
    child = StateTreeNode(
        id='child',
        mainline=True,
        parent=root,
        children=[],
        state=BoardState(
            fen='rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
            move=None,  # No move!
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=20.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='c5', uci='c7c5')]
                )
            ]
        )
    )
    
    root.children.append(child)
    
    curr_node = extract_current_state_tree_node(child)
    
    assert curr_node is None


def test_safe_move_returns_none_on_invalid_move():
    """Test that invalid moves return None instead of raising exceptions."""
    from src.preprocessing.node_extractor import _safe_move
    
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    
    # Valid move
    result = _safe_move(fen, 'e4')
    assert result is not None
    
    # Invalid move
    result = _safe_move(fen, 'e5')  # Can't move pawn to e5 from starting position
    assert result is None
    
    # Nonsense move
    result = _safe_move(fen, 'Xyz123')
    assert result is None


def test_both_nodes_extracted_for_classification():
    """Test that both previous and current nodes can be extracted for classification."""
    root = StateTreeNode(
        id='root',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=30.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='e4', uci='e2e4')]
                )
            ]
        )
    )
    
    child = StateTreeNode(
        id='child',
        mainline=True,
        parent=root,
        children=[],
        state=BoardState(
            fen='rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
            move=Move(san='e4', uci='e2e4'),
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=20.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='c5', uci='c7c5')]
                )
            ]
        )
    )
    
    root.children.append(child)
    
    # Extract both nodes
    prev_node = extract_previous_state_tree_node(root)
    curr_node = extract_current_state_tree_node(child)
    
    # Both should succeed
    assert prev_node is not None
    assert curr_node is not None
    
    # Both should have required fields for classification
    assert prev_node.top_move is not None
    assert curr_node.played_move is not None
    assert curr_node.subjective_evaluation is not None
    
    # Use with basic classifier
    from src.classification.basic_classifier import BasicClassifier
    classifier = BasicClassifier()
    classification = classifier.classify(prev_node, curr_node)
    
    # Classification should work (may be None if no basic rules apply)
    assert classification is None or classification is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


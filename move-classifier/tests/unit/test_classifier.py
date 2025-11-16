"""
Test Main Classifier

Tests the main classification orchestration logic.
"""

import pytest
from src.classification.classifier import Classifier, classify_node
from src.models.state_tree import StateTreeNode, BoardState, Move, EngineLine, Evaluation
from src.models.enums import Classification
from src.config import ClassificationConfig


def test_classifier_initialization():
    """Test that classifier can be initialized."""
    classifier = Classifier()
    assert classifier is not None


def test_classify_forced_move():
    """Test FORCED classification (only one legal move)."""
    # Position where only Kf1 is legal (king trapped by two rooks)
    parent = StateTreeNode(
        id='parent',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='7k/8/8/8/8/8/3rr3/4K3 w - - 0 1',  # Only Kf1 is legal
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=-500.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='Kf1', uci='e1f1')]
                )
            ]
        )
    )
    
    child = StateTreeNode(
        id='child',
        mainline=True,
        parent=parent,
        children=[],
        state=BoardState(
            fen='7k/8/8/8/8/8/3rr3/5K2 b - - 1 1',
            move=Move(san='Kf1', uci='e1f1'),
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=-500.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='Kg7', uci='h8g7')]
                )
            ]
        )
    )
    
    parent.children.append(child)
    
    classifier = Classifier()
    classification = classifier.classify(child)
    
    assert classification == Classification.FORCED


def test_classify_checkmate():
    """Test that checkmate is classified as BEST."""
    parent = StateTreeNode(
        id='parent',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1',
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='mate', value=1),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='Ra8#', uci='a1a8')]
                )
            ]
        )
    )
    
    child = StateTreeNode(
        id='child',
        mainline=True,
        parent=parent,
        children=[],
        state=BoardState(
            fen='R5k1/5ppp/8/8/8/8/5PPP/6K1 b - - 1 1',  # Checkmate position
            move=Move(san='Ra8#', uci='a1a8'),
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='mate', value=0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[]
                )
            ]
        )
    )
    
    parent.children.append(child)
    
    classifier = Classifier()
    classification = classifier.classify(child)
    
    assert classification == Classification.BEST


def test_classify_best_move():
    """Test that playing the top move results in BEST classification."""
    # Use a middlegame position not in opening book
    parent = StateTreeNode(
        id='parent',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5',
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=30.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='O-O', uci='e1g1')]
                ),
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=25.0),
                    source='stockfish-17',
                    depth=20,
                    index=2,
                    moves=[Move(san='Nc3', uci='b1c3')]
                )
            ]
        )
    )
    
    child = StateTreeNode(
        id='child',
        mainline=True,
        parent=parent,
        children=[],
        state=BoardState(
            fen='r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 1 5',
            move=Move(san='O-O', uci='e1g1'),
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=20.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='d6', uci='d7d6')]
                )
            ]
        )
    )
    
    parent.children.append(child)
    
    classifier = Classifier()
    classification = classifier.classify(child)
    
    assert classification == Classification.BEST


def test_classify_non_best_move():
    """Test that not playing the top move uses point loss classification."""
    # Use a middlegame position not in opening book
    parent = StateTreeNode(
        id='parent',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5',
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=50.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='O-O', uci='e1g1')]
                )
            ]
        )
    )
    
    # Play a different move (Nc3 instead of O-O) with evaluation drop
    child = StateTreeNode(
        id='child',
        mainline=True,
        parent=parent,
        children=[],
        state=BoardState(
            fen='r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R b KQkq - 1 5',
            move=Move(san='Nc3', uci='b1c3'),
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=10.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='d6', uci='d7d6')]
                )
            ]
        )
    )
    
    parent.children.append(child)
    
    # Disable theory checking for this test
    config = ClassificationConfig(include_theory=False)
    classifier = Classifier(config=config)
    classification = classifier.classify(child, config=config)
    
    # Point loss from +50 to +10 results in EXCELLENT (point loss < 0.045)
    assert classification == Classification.EXCELLENT


def test_classify_requires_parent():
    """Test that classification fails without parent node."""
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
    
    classifier = Classifier()
    
    with pytest.raises(ValueError, match="no parent node exists"):
        classifier.classify(root)


def test_classify_with_config():
    """Test classification with custom config."""
    parent = StateTreeNode(
        id='parent',
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
        parent=parent,
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
    
    parent.children.append(child)
    
    # Test with theory disabled
    config = ClassificationConfig(include_theory=False)
    classifier = Classifier(config=config)
    classification = classifier.classify(child, config=config)
    
    assert classification == Classification.BEST


def test_classify_node_convenience_function():
    """Test the convenience function classify_node."""
    # Use a middlegame position not in opening book
    parent = StateTreeNode(
        id='parent',
        mainline=True,
        parent=None,
        children=[],
        state=BoardState(
            fen='r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5',
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=30.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='O-O', uci='e1g1')]
                )
            ]
        )
    )
    
    child = StateTreeNode(
        id='child',
        mainline=True,
        parent=parent,
        children=[],
        state=BoardState(
            fen='r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 1 5',
            move=Move(san='O-O', uci='e1g1'),
            engine_lines=[
                EngineLine(
                    evaluation=Evaluation(type='centipawn', value=20.0),
                    source='stockfish-17',
                    depth=20,
                    index=1,
                    moves=[Move(san='d6', uci='d7d6')]
                )
            ]
        )
    )
    
    parent.children.append(child)
    
    classification = classify_node(child)
    
    assert classification == Classification.BEST


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


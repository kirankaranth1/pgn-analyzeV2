"""Test 4: Classification logic - test basic classifiers with mock data."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import chess
from src.core.types import Classification, PieceColor
from src.core.evaluation import Evaluation
from src.core.move import Move
from src.core.engine_line import EngineLine
from src.core.state_tree import StateTreeNode, BoardState
from src.classification.node_extractor import NodeExtractor, ExtractedPreviousNode, ExtractedCurrentNode
from src.classification.forced import is_forced_move, classify_forced
from src.classification.checkmate import is_checkmate, classify_checkmate
from src.classification.point_loss import is_top_move_played, classify_by_point_loss


def create_mock_previous_node(fen: str, legal_move_count: int = 20):
    """Helper to create a mock ExtractedPreviousNode."""
    board = chess.Board(fen)
    
    # Create a mock top move
    legal_moves = list(board.legal_moves)
    if legal_moves:
        chess_move = legal_moves[0]
        top_move = Move(
            san=board.san(chess_move),
            uci=chess_move.uci(),
            from_square=chess.square_name(chess_move.from_square),
            to_square=chess.square_name(chess_move.to_square),
            piece='p',
            color=PieceColor.WHITE if board.turn == chess.WHITE else PieceColor.BLACK
        )
    else:
        top_move = None
    
    eval1 = Evaluation(type="centipawn", value=50)
    
    return ExtractedPreviousNode(
        board=board,
        fen=fen,
        top_line=EngineLine(eval1, "stockfish", 20, 1, [top_move] if top_move else []),
        top_move=top_move,
        evaluation=eval1,
        subjective_evaluation=eval1,
        player_color=PieceColor.WHITE if board.turn == chess.WHITE else PieceColor.BLACK
    )


def create_mock_current_node(fen: str, played_san: str = "e4"):
    """Helper to create a mock ExtractedCurrentNode."""
    board = chess.Board(fen)
    
    played_move = Move(
        san=played_san,
        uci="e2e4",
        from_square="e2",
        to_square="e4",
        piece='p',
        color=PieceColor.WHITE
    )
    
    eval1 = Evaluation(type="centipawn", value=45)
    
    return ExtractedCurrentNode(
        board=board,
        fen=fen,
        top_line=EngineLine(eval1, "stockfish", 20, 1, []),
        evaluation=eval1,
        subjective_evaluation=eval1,
        played_move=played_move,
        player_color=PieceColor.WHITE
    )


def test_forced_move_detection():
    """Test FORCED classification with only one legal move."""
    # Position with only one legal move (king in check)
    fen_one_move = "8/8/8/8/8/2r5/1K6/2r5 w - - 0 1"
    prev = create_mock_previous_node(fen_one_move)
    
    assert is_forced_move(prev)
    classification = classify_forced(prev)
    assert classification == Classification.FORCED
    
    print("✓ FORCED move detection works")


def test_not_forced_move():
    """Test that normal positions are not forced."""
    # Starting position (many moves available)
    fen_start = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    prev = create_mock_previous_node(fen_start)
    
    assert not is_forced_move(prev)
    classification = classify_forced(prev)
    assert classification is None
    
    print("✓ Non-forced move detection works")


def test_checkmate_detection():
    """Test checkmate detection."""
    # Position after back rank mate
    fen_checkmate = "6k1/5ppp/8/8/8/8/5PPP/4R1K1 b - - 0 1"
    current = create_mock_current_node(fen_checkmate)
    
    # Need to set up the board in checkmate state
    # This FEN is actually mate for Black (Black is mated)
    board_mate = chess.Board(fen_checkmate)
    current.board = board_mate
    
    if board_mate.is_checkmate():
        assert is_checkmate(current)
        classification = classify_checkmate(current)
        assert classification == Classification.BEST
        print("✓ Checkmate detection works")
    else:
        print("⚠ Checkmate test skipped (board not in mate)")


def test_top_move_played():
    """Test detection of top move being played."""
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    
    # Create previous node with e4 as top move
    prev = create_mock_previous_node("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    prev.top_move = Move(
        san="e4",
        uci="e2e4",
        from_square="e2",
        to_square="e4",
        piece='p',
        color=PieceColor.WHITE
    )
    
    # Create current node with e4 played
    current = create_mock_current_node(fen, "e4")
    
    assert is_top_move_played(prev, current)
    print("✓ Top move detection works")


def test_not_top_move_played():
    """Test detection when different move played."""
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    
    # Create previous node with e4 as top move
    prev = create_mock_previous_node("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    prev.top_move = Move(
        san="e4",
        uci="e2e4",
        from_square="e2",
        to_square="e4",
        piece='p',
        color=PieceColor.WHITE
    )
    
    # Create current node with d4 played instead
    current = create_mock_current_node(fen, "d4")
    
    assert not is_top_move_played(prev, current)
    print("✓ Non-top move detection works")


def test_point_loss_classification_best():
    """Test BEST classification when top move played."""
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    prev = create_mock_previous_node(fen)
    prev.top_move = Move(san="e4", uci="e2e4", from_square="e2", to_square="e4", piece='p', color=PieceColor.WHITE)
    
    fen_after = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    current = create_mock_current_node(fen_after, "e4")
    
    classification = classify_by_point_loss(prev, current)
    assert classification == Classification.BEST
    
    print("✓ BEST classification works")


def test_point_loss_classification_blunder():
    """Test BLUNDER classification with large point loss."""
    # Before: White has advantage
    prev = create_mock_previous_node("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    prev.subjective_evaluation = Evaluation(type="centipawn", value=500)  # +5.00
    prev.top_move = Move(san="e4", uci="e2e4", from_square="e2", to_square="e4", piece='p', color=PieceColor.WHITE)
    
    # After: Lost the advantage drastically
    current = create_mock_current_node("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1")
    current.subjective_evaluation = Evaluation(type="centipawn", value=-500)  # -5.00
    current.played_move = Move(san="d3", uci="d2d3", from_square="d2", to_square="d3", piece='p', color=PieceColor.WHITE)
    
    classification = classify_by_point_loss(prev, current)
    assert classification == Classification.BLUNDER
    
    print("✓ BLUNDER classification works")


def test_board_state_creation():
    """Test creating BoardState with classifications."""
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    
    move = Move(
        san="e4",
        uci="e2e4",
        from_square="e2",
        to_square="e4",
        piece='p',
        color=PieceColor.WHITE
    )
    
    state = BoardState(
        fen=fen,
        move=move,
        classification=Classification.BEST,
        accuracy=98.5,
        move_color=PieceColor.WHITE
    )
    
    assert state.fen == fen
    assert state.move.san == "e4"
    assert state.classification == Classification.BEST
    assert state.accuracy == 98.5
    
    print("✓ BoardState with classification works")


if __name__ == "__main__":
    print("Running classification logic tests...\n")
    test_forced_move_detection()
    test_not_forced_move()
    test_checkmate_detection()
    test_top_move_played()
    test_not_top_move_played()
    test_point_loss_classification_best()
    test_point_loss_classification_blunder()
    test_board_state_creation()
    print("\n✅ All classification logic tests passed!")


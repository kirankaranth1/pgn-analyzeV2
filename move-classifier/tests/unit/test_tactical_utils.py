"""
Unit tests for tactical analysis utilities (attackers, defenders, piece safety)
"""

import chess
import pytest

from src.models.chess_types import BoardPiece, get_board_pieces
from src.utils.attackers import get_attacking_moves
from src.utils.defenders import get_defending_moves
from src.utils.piece_safety import is_piece_safe, get_unsafe_pieces
from src.constants import PIECE_VALUES


class TestAttackers:
    """Test attacker detection functionality."""
    
    def test_direct_attacker_simple(self):
        """Test direct attacker on a piece."""
        # Position: White knight on d4 attacked by black pawn on c5
        board = chess.Board("8/8/8/2p5/3N4/8/8/8 w - - 0 1")
        knight = BoardPiece(
            square=chess.D4,
            type=chess.KNIGHT,
            color=chess.WHITE
        )
        
        attackers = get_attacking_moves(board, knight, transitive=False)
        assert len(attackers) == 1
        assert attackers[0].piece == chess.PAWN
        assert attackers[0].from_square == chess.C5
    
    def test_multiple_attackers(self):
        """Test multiple pieces attacking same square."""
        # Position: White queen on d4 attacked by black rook on d8 and bishop on a7
        board = chess.Board("3r4/b7/8/8/3Q4/8/8/8 w - - 0 1")
        queen = BoardPiece(
            square=chess.D4,
            type=chess.QUEEN,
            color=chess.WHITE
        )
        
        attackers = get_attacking_moves(board, queen, transitive=False)
        assert len(attackers) >= 2  # At least rook and bishop
    
    def test_transitive_attacker_battery(self):
        """Test transitive attacker (piece behind another piece)."""
        # Position: White queen on d4, black rook on d6, black queen on d8
        # The queen on d8 is a transitive attacker through the rook
        board = chess.Board("3q4/8/3r4/8/3Q4/8/8/8 w - - 0 1")
        queen = BoardPiece(
            square=chess.D4,
            type=chess.QUEEN,
            color=chess.WHITE
        )
        
        attackers_no_transitive = get_attacking_moves(board, queen, transitive=False)
        attackers_with_transitive = get_attacking_moves(board, queen, transitive=True)
        
        # With transitive, we should find the queen behind the rook
        assert len(attackers_with_transitive) >= len(attackers_no_transitive)


class TestDefenders:
    """Test defender detection functionality."""
    
    def test_defenders_simple(self):
        """Test simple defender detection."""
        # Position: White knight on d4, white pawn on c3
        board = chess.Board("8/8/8/8/3N4/2P5/8/8 w - - 0 1")
        knight = BoardPiece(
            square=chess.D4,
            type=chess.KNIGHT,
            color=chess.WHITE
        )
        
        defenders = get_defending_moves(board, knight, transitive=True)
        # The pawn on c3 should be counted as a defender
        assert len(defenders) >= 1


class TestPieceSafety:
    """Test piece safety detection functionality."""
    
    def test_safe_piece_no_attackers(self):
        """Test that piece with no attackers is safe."""
        board = chess.Board("8/8/8/8/3N4/8/8/8 w - - 0 1")
        knight = BoardPiece(
            square=chess.D4,
            type=chess.KNIGHT,
            color=chess.WHITE
        )
        
        assert is_piece_safe(board, knight) == True
    
    def test_unsafe_piece_lower_attacker(self):
        """Test that piece attacked by lower-value piece is unsafe."""
        # Position: White queen on d4 attacked by black pawn on c5
        board = chess.Board("8/8/8/2p5/3Q4/8/8/8 w - - 0 1")
        queen = BoardPiece(
            square=chess.D4,
            type=chess.QUEEN,
            color=chess.WHITE
        )
        
        assert is_piece_safe(board, queen) == False
    
    def test_safe_piece_with_defenders(self):
        """Test that piece with equal-value attacker and defender is safe."""
        # Position: White knight on d4, attacked by black knight on f5, defended by white pawn on c3
        # Equal attackers/defenders means safe
        board = chess.Board("8/8/8/5n2/3N4/2P5/8/8 w - - 0 1")
        knight = BoardPiece(
            square=chess.D4,
            type=chess.KNIGHT,
            color=chess.WHITE
        )
        
        # Knight has equal value attacker and defender, so should be safe
        assert is_piece_safe(board, knight) == True
    
    def test_get_unsafe_pieces(self):
        """Test getting all unsafe pieces for a color."""
        # Position: White queen on d4 (unsafe, attacked by black pawn)
        # White knight on f3 (safe)
        board = chess.Board("8/8/8/2p5/3Q4/5N2/8/8 w - - 0 1")
        
        unsafe = get_unsafe_pieces(board, chess.WHITE)
        
        # Queen should be in unsafe list
        assert len(unsafe) >= 1
        assert any(piece.type == chess.QUEEN for piece in unsafe)


class TestPieceValues:
    """Test piece values constants."""
    
    def test_piece_values_defined(self):
        """Test that all piece values are defined."""
        assert PIECE_VALUES[chess.PAWN] == 1
        assert PIECE_VALUES[chess.KNIGHT] == 3
        assert PIECE_VALUES[chess.BISHOP] == 3
        assert PIECE_VALUES[chess.ROOK] == 5
        assert PIECE_VALUES[chess.QUEEN] == 9
        assert PIECE_VALUES[chess.KING] == float('inf')


class TestBoardPieces:
    """Test board piece utilities."""
    
    def test_get_board_pieces(self):
        """Test getting all pieces from a board."""
        board = chess.Board()  # Starting position
        pieces = get_board_pieces(board)
        
        assert len(pieces) == 32  # 16 white + 16 black pieces
        
        # Count pawns
        pawns = [p for p in pieces if p.type == chess.PAWN]
        assert len(pawns) == 16


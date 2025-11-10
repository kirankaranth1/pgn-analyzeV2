"""Build state tree from parsed PGN game."""

import chess
import chess.pgn
from typing import Optional
from ..core.state_tree import StateTreeNode, BoardState
from ..core.move import Move
from ..core.types import PieceColor


class StateTreeBuilder:
    """Builds a state tree from a chess.pgn.Game."""
    
    @staticmethod
    def build_tree(game: chess.pgn.Game) -> StateTreeNode:
        """Build state tree from PGN game.
        
        Args:
            game: chess.pgn.Game object
            
        Returns:
            Root StateTreeNode
        """
        # Create root node with starting position
        board = game.board()
        root_state = BoardState(fen=board.fen())
        root = StateTreeNode(
            id="root",
            state=root_state,
            mainline=True
        )
        
        # Build tree from game moves
        current_node = root
        node = game
        move_number = 0
        
        while node.variations:
            next_node = node.variation(0)  # Main line
            board = node.board()
            chess_move = next_node.move
            
            # Create Move object
            move = StateTreeBuilder._create_move_from_chess_move(
                chess_move, board
            )
            
            # Create new state
            board.push(chess_move)
            move_number += 1
            
            new_state = BoardState(
                fen=board.fen(),
                move=move,
                move_color=PieceColor.WHITE if board.turn == chess.BLACK else PieceColor.BLACK
            )
            
            # Create new node
            new_node = StateTreeNode(
                id=f"move_{move_number}",
                state=new_state,
                mainline=True
            )
            
            current_node.add_child(new_node)
            current_node = new_node
            node = next_node
        
        return root
    
    @staticmethod
    def _create_move_from_chess_move(
        chess_move: chess.Move, 
        board: chess.Board
    ) -> Move:
        """Convert chess.Move to our Move object.
        
        Args:
            chess_move: chess.Move object
            board: Board before the move
            
        Returns:
            Move object
        """
        from_square = chess.square_name(chess_move.from_square)
        to_square = chess.square_name(chess_move.to_square)
        
        # Get piece being moved
        piece = board.piece_at(chess_move.from_square)
        if not piece:
            raise ValueError("No piece at from_square")
        
        piece_type = piece.symbol().lower()
        color = PieceColor.WHITE if piece.color == chess.WHITE else PieceColor.BLACK
        
        # Get captured piece
        captured_piece = board.piece_at(chess_move.to_square)
        captured_type = captured_piece.symbol().lower() if captured_piece else None
        
        # Handle en passant capture
        if board.is_en_passant(chess_move):
            captured_type = 'p'
        
        # Get promotion
        promotion_type = None
        if chess_move.promotion:
            promotion_type = chess.piece_symbol(chess_move.promotion).lower()
        
        # Get SAN notation
        san = board.san(chess_move)
        
        # Get UCI notation
        uci = chess_move.uci()
        
        return Move(
            san=san,
            uci=uci,
            from_square=from_square,
            to_square=to_square,
            piece=piece_type,
            color=color,
            captured=captured_type,
            promotion=promotion_type,
            flags=""
        )


"""Stockfish UCI engine integration."""

import subprocess
import re
from typing import List, Optional
from .engine_config import EngineConfig
from ..core.evaluation import Evaluation
from ..core.engine_line import EngineLine
from ..core.move import Move
from ..core.types import PieceColor
import chess


class StockfishEngine:
    """Manages communication with Stockfish via UCI protocol."""
    
    def __init__(self, config: EngineConfig):
        """Initialize Stockfish engine.
        
        Args:
            config: Engine configuration
        """
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self._start_engine()
    
    def _start_engine(self) -> None:
        """Start the Stockfish process."""
        try:
            self.process = subprocess.Popen(
                [self.config.stockfish_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Initialize UCI mode
            self._send_command("uci")
            self._wait_for("uciok")
            
            # Set options
            self._send_command(f"setoption name Threads value {self.config.threads}")
            self._send_command(f"setoption name Hash value {self.config.hash_size}")
            self._send_command(f"setoption name MultiPV value {self.config.multi_pv}")
            
            # Ready check
            self._send_command("isready")
            self._wait_for("readyok")
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Stockfish not found at: {self.config.stockfish_path}\n"
                "Please provide a valid path to the Stockfish binary."
            )
    
    def _send_command(self, command: str) -> None:
        """Send command to Stockfish."""
        if self.process and self.process.stdin:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
    
    def _wait_for(self, expected: str) -> List[str]:
        """Wait for expected response from Stockfish."""
        lines = []
        if self.process and self.process.stdout:
            for line in self.process.stdout:
                line = line.strip()
                lines.append(line)
                if expected in line:
                    break
        return lines
    
    def analyze_position(self, fen: str) -> List[EngineLine]:
        """Analyze a chess position.
        
        Args:
            fen: FEN string of the position
            
        Returns:
            List of engine lines (multiple PVs)
        """
        # Set up position
        self._send_command(f"position fen {fen}")
        
        # Start analysis
        self._send_command(f"go depth {self.config.depth}")
        
        # Wait for analysis to complete
        lines = self._wait_for("bestmove")
        
        # Parse engine lines
        return self._parse_engine_output(lines, fen)
    
    def _parse_engine_output(self, lines: List[str], fen: str) -> List[EngineLine]:
        """Parse Stockfish output into EngineLine objects.
        
        Args:
            lines: Output lines from Stockfish
            fen: FEN string of the position being analyzed
            
        Returns:
            List of EngineLine objects
        """
        engine_lines = []
        board = chess.Board(fen)
        
        for line in lines:
            if not line.startswith("info"):
                continue
            
            # Extract multipv index
            multipv_match = re.search(r'multipv (\d+)', line)
            if not multipv_match:
                continue
            multipv = int(multipv_match.group(1))
            
            # Extract depth
            depth_match = re.search(r'depth (\d+)', line)
            if not depth_match:
                continue
            depth = int(depth_match.group(1))
            
            # Only process lines at final depth
            if depth < self.config.depth:
                continue
            
            # Extract evaluation
            evaluation = self._parse_evaluation(line)
            if not evaluation:
                continue
            
            # Extract principal variation (moves)
            pv_match = re.search(r'pv (.+?)(?:$|\s+info)', line)
            if not pv_match:
                continue
            
            pv_uci_moves = pv_match.group(1).strip().split()
            moves = self._convert_uci_moves_to_moves(pv_uci_moves, board)
            
            engine_line = EngineLine(
                evaluation=evaluation,
                source="stockfish",
                depth=depth,
                index=multipv,
                moves=moves
            )
            engine_lines.append(engine_line)
        
        # Sort by index
        engine_lines.sort(key=lambda x: x.index)
        return engine_lines
    
    def _parse_evaluation(self, line: str) -> Optional[Evaluation]:
        """Parse evaluation from info line.
        
        Args:
            line: Info line from Stockfish
            
        Returns:
            Evaluation object or None
        """
        # Check for mate score
        mate_match = re.search(r'score mate (-?\d+)', line)
        if mate_match:
            mate_moves = int(mate_match.group(1))
            return Evaluation(type="mate", value=mate_moves)
        
        # Check for centipawn score
        cp_match = re.search(r'score cp (-?\d+)', line)
        if cp_match:
            centipawns = int(cp_match.group(1))
            return Evaluation(type="centipawn", value=centipawns)
        
        return None
    
    def _convert_uci_moves_to_moves(self, uci_moves: List[str], start_board: chess.Board) -> List[Move]:
        """Convert UCI move strings to Move objects.
        
        Args:
            uci_moves: List of UCI move strings (e.g., ["e2e4", "e7e5"])
            start_board: Starting board position
            
        Returns:
            List of Move objects
        """
        moves = []
        board = start_board.copy()
        
        for uci_str in uci_moves:
            try:
                # Parse UCI move
                chess_move = chess.Move.from_uci(uci_str)
                
                # Get move details
                from_square = chess.square_name(chess_move.from_square)
                to_square = chess.square_name(chess_move.to_square)
                
                # Get piece being moved
                piece = board.piece_at(chess_move.from_square)
                if not piece:
                    break  # Invalid move
                
                # Get captured piece
                captured_piece = board.piece_at(chess_move.to_square)
                captured_type = captured_piece.symbol().lower() if captured_piece else None
                
                # Get promotion
                promotion_type = None
                if chess_move.promotion:
                    promotion_type = chess.piece_symbol(chess_move.promotion).lower()
                
                # Determine color
                color = PieceColor.WHITE if piece.color == chess.WHITE else PieceColor.BLACK
                
                # Make the move to get SAN
                san = board.san(chess_move)
                board.push(chess_move)
                
                # Create Move object
                move = Move(
                    san=san,
                    uci=uci_str,
                    from_square=from_square,
                    to_square=to_square,
                    piece=piece.symbol().lower(),
                    color=color,
                    captured=captured_type,
                    promotion=promotion_type,
                    flags=""
                )
                moves.append(move)
                
            except (ValueError, AssertionError):
                break  # Stop on invalid move
        
        return moves
    
    def quit(self) -> None:
        """Shutdown the engine."""
        if self.process:
            self._send_command("quit")
            self.process.wait(timeout=5)
            self.process = None
    
    def __del__(self):
        """Cleanup on deletion."""
        self.quit()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()


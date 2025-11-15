"""
Local UCI Engine Interface

Provides communication with UCI-compatible chess engines (e.g., Stockfish).
Supports MultiPV analysis and asynchronous evaluation.
"""

from typing import List, Optional, Callable
import subprocess
import re
import chess
import shutil

from ..models.state_tree import EngineLine, Evaluation, Move
from ..models.enums import EngineVersion
from ..utils.chess_utils import is_black_to_move
from ..constants import STARTING_FEN


class UCIEngine:
    """
    UCI chess engine interface.
    
    Supports communication with UCI-compatible engines like Stockfish.
    """
    
    def __init__(
        self,
        engine_path: Optional[str] = None,
        version: EngineVersion = EngineVersion.STOCKFISH_17
    ):
        """
        Initialize UCI engine.
        
        Args:
            engine_path: Path to engine binary (if None, searches PATH)
            version: Engine version identifier
        """
        self.version = version
        self.position = STARTING_FEN
        
        # Find engine binary
        if engine_path is None:
            # Try to find stockfish in PATH
            engine_path = shutil.which("stockfish")
            if engine_path is None:
                raise FileNotFoundError(
                    "Stockfish not found in PATH. Please install Stockfish or provide path."
                )
        
        # Start engine process
        try:
            self.process = subprocess.Popen(
                [engine_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Engine binary not found at: {engine_path}")
        except Exception as e:
            raise Exception(f"Failed to start engine: {e}")
        
        # Initialize engine
        self._send_command("uci")
        self._wait_for_response("uciok")
        self._send_command("ucinewgame")
        self._send_command("isready")
        self._wait_for_response("readyok")
    
    def _send_command(self, command: str) -> None:
        """Send command to engine."""
        if self.process.stdin:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
    
    def _wait_for_response(self, expected: str, timeout: int = 10) -> None:
        """Wait for specific response from engine."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.process.stdout:
                line = self.process.stdout.readline().strip()
                if expected in line:
                    return
        
        raise TimeoutError(f"Engine did not respond with '{expected}' within {timeout}s")
    
    def set_position(self, fen: str) -> None:
        """
        Set current position.
        
        Args:
            fen: Position in FEN notation
        """
        self._send_command(f"position fen {fen}")
        self.position = fen
    
    def evaluate(
        self,
        depth: int = 16,
        multi_pv: int = 2,
        time_limit: Optional[int] = None,
        on_engine_line: Optional[Callable[[EngineLine], None]] = None
    ) -> List[EngineLine]:
        """
        Evaluate current position.
        
        Args:
            depth: Search depth in plies
            multi_pv: Number of principal variations
            time_limit: Time limit in milliseconds (optional)
            on_engine_line: Callback for each engine line (optional)
            
        Returns:
            List of engine lines
        """
        # Configure MultiPV
        self._send_command(f"setoption name MultiPV value {multi_pv}")
        self._send_command("isready")
        self._wait_for_response("readyok")
        
        # Build go command
        if time_limit:
            go_command = f"go depth {depth} movetime {time_limit}"
        else:
            go_command = f"go depth {depth}"
        
        # Start evaluation
        self._send_command(go_command)
        
        # Collect engine lines
        engine_lines = self._parse_engine_output(on_engine_line)
        
        return engine_lines
    
    def _parse_engine_output(
        self,
        on_engine_line: Optional[Callable[[EngineLine], None]] = None
    ) -> List[EngineLine]:
        """
        Parse engine output and extract engine lines.
        
        Args:
            on_engine_line: Optional callback for each line
            
        Returns:
            List of engine lines
        """
        engine_lines: List[EngineLine] = []
        lines_by_depth_index = {}  # Track latest line for each (depth, index)
        
        while True:
            if not self.process.stdout:
                break
            
            line = self.process.stdout.readline().strip()
            
            # Stop on bestmove
            if line.startswith("bestmove") or "depth 0" in line:
                break
            
            # Only process info lines
            if not line.startswith("info depth"):
                continue
            
            # Skip currmove lines
            if "currmove" in line:
                continue
            
            # Parse the line
            parsed_line = self._parse_info_line(line)
            if parsed_line:
                # Track by (depth, index) to get only final lines
                key = (parsed_line.depth, parsed_line.index)
                lines_by_depth_index[key] = parsed_line
                
                if on_engine_line:
                    on_engine_line(parsed_line)
        
        # Get only the lines with maximum depth for each index
        if lines_by_depth_index:
            max_depth = max(line.depth for line in lines_by_depth_index.values())
            engine_lines = [
                line for (depth, _), line in lines_by_depth_index.items()
                if depth == max_depth
            ]
            # Sort by index
            engine_lines.sort(key=lambda x: x.index)
        
        return engine_lines
    
    def _parse_info_line(self, line: str) -> Optional[EngineLine]:
        """
        Parse a single info line from engine output.
        
        Args:
            line: Info line from engine
            
        Returns:
            EngineLine object or None if parsing fails
        """
        # Parse depth
        depth_match = re.search(r'\bdepth (\d+)', line)
        if not depth_match:
            return None
        depth = int(depth_match.group(1))
        
        # Parse MultiPV index
        index_match = re.search(r'\bmultipv (\d+)', line)
        index = int(index_match.group(1)) if index_match else 1
        
        # Parse evaluation
        score_match = re.search(r'\bscore (cp|mate) (-?\d+)', line)
        if not score_match:
            return None
        
        eval_type = "centipawn" if score_match.group(1) == "cp" else "mate"
        eval_value = int(score_match.group(2))
        
        # ⚠️ CRITICAL: Normalize to White's perspective
        # Engine returns evaluation from side-to-move perspective
        if is_black_to_move(self.position):
            eval_value = -eval_value
        
        # Parse principal variation
        pv_match = re.search(r'\bpv (.+)$', line)
        uci_moves = pv_match.group(1).split() if pv_match else []
        
        # Convert UCI moves to SAN
        moves = self._convert_uci_to_san(uci_moves)
        
        # Create engine line
        engine_line = EngineLine(
            evaluation=Evaluation(
                type=eval_type,
                value=float(eval_value)
            ),
            source=self.version.value,
            depth=depth,
            index=index,
            moves=moves
        )
        
        return engine_line
    
    def _convert_uci_to_san(self, uci_moves: List[str]) -> List[Move]:
        """
        Convert UCI moves to SAN notation.
        
        Args:
            uci_moves: List of UCI move strings
            
        Returns:
            List of Move objects
        """
        moves: List[Move] = []
        board = chess.Board(self.position)
        
        for uci_str in uci_moves:
            try:
                move = chess.Move.from_uci(uci_str)
                san = board.san(move)
                board.push(move)
                
                moves.append(Move(
                    san=san,
                    uci=move.uci()
                ))
            except (ValueError, chess.IllegalMoveError):
                break
        
        return moves
    
    def terminate(self) -> None:
        """Terminate the engine process."""
        if self.process:
            self._send_command("quit")
            self.process.terminate()
            self.process.wait(timeout=5)
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.terminate()
        except:
            pass

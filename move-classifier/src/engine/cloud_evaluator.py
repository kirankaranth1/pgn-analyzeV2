"""
Cloud Evaluation Service

Provides position evaluation using Lichess cloud analysis API.
Handles response parsing and castling notation conversion.
"""

from typing import List, Optional
import requests
import chess

from ..models.state_tree import EngineLine, Evaluation, Move
from ..models.enums import EngineVersion
from ..utils.notation_converter import normalize_lichess_castling
from ..utils.chess_utils import is_black_to_move


def get_cloud_evaluation(
    fen: str,
    multi_pv: int = 2,
    timeout: int = 10
) -> List[EngineLine]:
    """
    Get position evaluation from Lichess cloud API.
    
    Args:
        fen: Position in FEN notation
        multi_pv: Number of principal variations to request
        timeout: Request timeout in seconds
        
    Returns:
        List of engine lines from cloud evaluation
        
    Raises:
        Exception: If cloud evaluation fails
    """
    url = f"https://lichess.org/api/cloud-eval?fen={fen}&multiPv={multi_pv}"
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Cloud evaluation failed: {e}")
    
    data = response.json()
    
    # Parse response
    engine_lines = _parse_lichess_response(fen, data)
    
    return engine_lines


def _parse_lichess_response(fen: str, data: dict) -> List[EngineLine]:
    """
    Parse Lichess API response into EngineLine objects.
    
    Args:
        fen: Position FEN
        data: JSON response from Lichess API
        
    Returns:
        List of EngineLine objects
    """
    engine_lines: List[EngineLine] = []
    
    if "pvs" not in data:
        return engine_lines
    
    depth = data.get("depth", 0)
    pvs = data["pvs"]
    
    for idx, pv in enumerate(pvs):
        # Parse moves
        moves_str = pv.get("moves", "")
        if not moves_str:
            continue
        
        uci_moves = moves_str.split()
        moves = _convert_uci_moves_to_san(fen, uci_moves)
        
        # Determine evaluation type and value
        if "mate" in pv:
            eval_type = "mate"
            eval_value = pv["mate"]
        else:
            eval_type = "centipawn"
            eval_value = pv.get("cp", 0)
        
        # Normalize evaluation to White's perspective
        # Lichess already returns from White's perspective
        
        # Create engine line
        engine_line = EngineLine(
            evaluation=Evaluation(
                type=eval_type,
                value=float(eval_value)
            ),
            source=EngineVersion.LICHESS_CLOUD.value,
            depth=depth,
            index=idx + 1,  # 1-indexed
            moves=moves
        )
        
        engine_lines.append(engine_line)
    
    return engine_lines


def _convert_uci_moves_to_san(fen: str, uci_moves: List[str]) -> List[Move]:
    """
    Convert UCI moves to SAN notation.
    
    Args:
        fen: Starting position FEN
        uci_moves: List of UCI move strings
        
    Returns:
        List of Move objects with both SAN and UCI
    """
    moves: List[Move] = []
    board = chess.Board(fen)
    
    for uci_str in uci_moves:
        # Normalize Lichess castling notation
        uci_normalized = normalize_lichess_castling(uci_str)
        
        try:
            # Parse UCI move
            move = chess.Move.from_uci(uci_normalized)
            
            # Get SAN
            san = board.san(move)
            
            # Make move
            board.push(move)
            
            # Create Move object
            moves.append(Move(
                san=san,
                uci=move.uci()
            ))
        except (ValueError, chess.IllegalMoveError):
            # Stop on invalid move
            break
    
    return moves

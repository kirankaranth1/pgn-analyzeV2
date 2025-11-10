"""PGN parsing utilities."""

import chess.pgn
from typing import Dict, Optional, TextIO
from io import StringIO


class PGNParser:
    """Parse PGN files into game data."""
    
    @staticmethod
    def parse_game(pgn_content: str) -> Optional[chess.pgn.Game]:
        """Parse a single game from PGN string.
        
        Args:
            pgn_content: PGN file content as string
            
        Returns:
            chess.pgn.Game object or None if invalid
        """
        pgn_io = StringIO(pgn_content)
        try:
            game = chess.pgn.read_game(pgn_io)
            return game
        except Exception as e:
            print(f"Error parsing PGN: {e}")
            return None
    
    @staticmethod
    def parse_file(file_path: str) -> Optional[chess.pgn.Game]:
        """Parse a game from PGN file.
        
        Args:
            file_path: Path to PGN file
            
        Returns:
            chess.pgn.Game object or None if invalid
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                game = chess.pgn.read_game(f)
                return game
        except Exception as e:
            print(f"Error reading PGN file {file_path}: {e}")
            return None
    
    @staticmethod
    def extract_headers(game: chess.pgn.Game) -> Dict[str, str]:
        """Extract game headers.
        
        Args:
            game: chess.pgn.Game object
            
        Returns:
            Dictionary of header values
        """
        return {
            "white": game.headers.get("White", "Unknown"),
            "black": game.headers.get("Black", "Unknown"),
            "result": game.headers.get("Result", "*"),
            "date": game.headers.get("Date", "????.??.??"),
            "event": game.headers.get("Event", ""),
            "site": game.headers.get("Site", ""),
            "round": game.headers.get("Round", ""),
            "white_elo": game.headers.get("WhiteElo", ""),
            "black_elo": game.headers.get("BlackElo", "")
        }


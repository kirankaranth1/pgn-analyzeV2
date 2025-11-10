"""Opening book lookup utilities."""

import json
from typing import Optional, Dict


class OpeningBook:
    """Handles opening book lookups."""
    
    def __init__(self, openings_file: str):
        """Initialize opening book.
        
        Args:
            openings_file: Path to openings.json file
        """
        self.openings: Dict[str, str] = {}
        self._load_openings(openings_file)
    
    def _load_openings(self, openings_file: str) -> None:
        """Load openings from JSON file.
        
        Args:
            openings_file: Path to openings.json
        """
        try:
            with open(openings_file, 'r', encoding='utf-8') as f:
                self.openings = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load openings file {openings_file}: {e}")
            self.openings = {}
    
    def lookup(self, fen: str) -> Optional[str]:
        """Look up opening name for a position.
        
        Only uses piece placement (first component of FEN).
        
        Args:
            fen: Full FEN string
            
        Returns:
            Opening name or None if not found
        """
        # Extract piece placement (before first space)
        piece_placement = fen.split()[0]
        return self.openings.get(piece_placement)


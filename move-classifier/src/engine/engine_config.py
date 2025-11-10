"""Engine configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EngineConfig:
    """Configuration for chess engine analysis.
    
    Attributes:
        depth: Search depth in plies (default: 20)
        multi_pv: Number of principal variations to analyze (default: 2)
        threads: Number of CPU threads (default: 1)
        hash_size: Hash table size in MB (default: 128)
        stockfish_path: Path to Stockfish binary (required)
    """
    stockfish_path: str
    depth: int = 20
    multi_pv: int = 2
    threads: int = 1
    hash_size: int = 128
    
    def __post_init__(self):
        """Validate configuration."""
        if self.depth < 1:
            raise ValueError("Depth must be at least 1")
        if self.multi_pv < 1:
            raise ValueError("Multi-PV must be at least 1")
        if self.threads < 1:
            raise ValueError("Threads must be at least 1")
        if self.hash_size < 1:
            raise ValueError("Hash size must be at least 1 MB")


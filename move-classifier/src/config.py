"""
Configuration Settings

Configurable parameters for the classification system.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class EngineConfig:
    """Configuration for engine analysis."""
    
    depth: int = 16
    """Search depth in plies."""
    
    time_limit: Optional[int] = None
    """Time limit per position in milliseconds."""
    
    multi_pv: int = 2
    """Number of principal variations to analyze."""
    
    use_cloud_eval: bool = True
    """Try cloud evaluation before local engine."""
    
    stockfish_path: Optional[str] = None
    """Path to Stockfish binary. If None, will search in PATH."""


@dataclass
class ClassificationConfig:
    """Configuration for move classification."""
    
    expand_all_variations: bool = False
    """Include variations in analysis (not just mainline)."""
    
    enable_tactical_analysis: bool = True
    """Enable tactical pattern detection."""
    
    enable_attack_defense: bool = True
    """Enable attack/defense classification."""


@dataclass
class SystemConfig:
    """Overall system configuration."""
    
    engine: EngineConfig
    classification: ClassificationConfig
    
    @classmethod
    def default(cls) -> "SystemConfig":
        """Create default configuration."""
        return cls(
            engine=EngineConfig(),
            classification=ClassificationConfig()
        )


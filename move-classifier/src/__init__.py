"""
Chess Move Classifier

A comprehensive system for analyzing and classifying chess moves based on
engine evaluation and tactical patterns.

Main Components:
    - Preprocessing: 5-stage pipeline from PGN to classification-ready data
    - Classification: Move quality evaluation system
    - Engine: Chess engine interfaces (UCI and cloud)
    - Models: Data structures and enumerations
    - Utils: Helper functions and utilities
"""

from .models import (
    PieceColor,
    Classification,
    EngineVersion,
    GameAnalysis,
)

__version__ = "0.1.0"

__all__ = [
    "PieceColor",
    "Classification",
    "EngineVersion",
    "GameAnalysis",
]

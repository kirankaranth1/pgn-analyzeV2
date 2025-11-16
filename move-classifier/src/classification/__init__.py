"""
Classification Module

Contains the move classification system that evaluates chess moves
based on engine analysis and assigns quality classifications.
"""

from .classifier import Classifier, classify_node
from .basic_classifier import BasicClassifier, OpeningBook
from .critical_classifier import consider_critical_classification
from .critical_move import is_move_critical_candidate
from .brilliant_classifier import consider_brilliant_classification

__all__ = [
    "Classifier",
    "classify_node",
    "BasicClassifier",
    "OpeningBook",
    "consider_critical_classification",
    "is_move_critical_candidate",
    "consider_brilliant_classification",
]


"""
Classification Module

Contains the move classification system that evaluates chess moves
based on engine analysis and assigns quality classifications.
"""

from .classifier import Classifier, classify_node
from .basic_classifier import BasicClassifier, OpeningBook

__all__ = [
    "Classifier",
    "classify_node",
    "BasicClassifier",
    "OpeningBook",
]


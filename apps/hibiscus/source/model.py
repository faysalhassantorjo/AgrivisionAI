"""
Model loader module for Hibiscus leaf disease classifier.
"""

from pathlib import Path
from apps.hibiscus.source.predictor import predictor


def load_model():
    """Load and return the compiled/uncompiled Keras model."""
    return predictor.get_model()

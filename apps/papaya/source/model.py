"""
Model loader module for Papaya leaf disease classifier.
"""

from apps.papaya.source.predictor import predictor


def load_model():
    """Load and return the compiled/uncompiled Keras model."""
    return predictor.get_model()

"""
Model loader module for Zucchini leaf disease classifier.
"""

from apps.zucchini.source.predictor import predictor


def load_model():
    """Load and return the compiled/uncompiled Keras model."""
    return predictor.get_model()

"""
Model loader module for Tea Leaf disease classifier.
"""

from apps.tea_leaf.source.predictor import predictor


def load_model():
    """Load and return the compiled/uncompiled Keras model."""
    return predictor.get_model()

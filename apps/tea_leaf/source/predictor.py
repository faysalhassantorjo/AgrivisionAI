"""
Tea leaf plant disease predictor.
Fixes critical issue where MODEL was previously set to None and never loaded.
"""

from __future__ import annotations

import logging
from typing import Any, Dict
from apps.common.predictor import BasePredictor

logger = logging.getLogger(__name__)

# Standardized predictor instance supporting "Tea leaf.h5" and "tea_leaf_model.h5"
predictor = BasePredictor(
    plant_key="tea_leaf",
    model_filename="Tea leaf.h5",
    candidate_paths=[
        "apps/tea_leaf/source/Tea leaf.h5",
        "apps/tea_leaf/source/tea_leaf_model.h5",
        "apps/tea_leaf/source/model.h5",
    ],
)

CLASSES = predictor.classes


def load_model():
    """Load model dynamically via BasePredictor."""
    return predictor.get_model()


# Module-level MODEL reference for legacy backwards-compatibility
MODEL = predictor.get_model()


def predict(image_file: Any) -> Dict[str, Any]:
    """
    Run inference on uploaded tea leaf image.
    Preserves backwards compatibility with legacy predict() interface.
    """
    return predictor.predict(image_file)

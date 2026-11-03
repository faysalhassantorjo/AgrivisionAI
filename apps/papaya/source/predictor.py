"""
Papaya plant leaf disease predictor.
Standardized BasePredictor implementation for papaya diseases.
"""

from __future__ import annotations

import logging
from typing import Any, Dict
from apps.common.predictor import BasePredictor

logger = logging.getLogger(__name__)

# Standardized predictor instance supporting Papaya.h5 and papaya_model.h5
predictor = BasePredictor(
    plant_key="papaya",
    model_filename="Papaya.h5",
    candidate_paths=[
        "apps/papaya/source/Papaya.h5",
        "apps/papaya/source/papaya_model.h5",
        "apps/papaya/source/model.h5",
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
    Run inference on uploaded papaya leaf image.
    Preserves backwards compatibility with legacy predict() interface.
    """
    return predictor.predict(image_file)

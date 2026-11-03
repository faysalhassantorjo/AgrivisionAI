"""
Zucchini plant leaf disease predictor.
Utilizes the shared BasePredictor with standardized zucchini disease classes.
"""

from __future__ import annotations

import logging
from typing import Any, Dict
from apps.common.predictor import BasePredictor

logger = logging.getLogger(__name__)

# Standardized predictor instance supporting Zucchini.h5 and zucchini_model.h5
# Zucchini.h5 is an EfficientNet architecture with embedded Rescaling(1/255) and Normalization
# layers, requiring raw [0, 255] RGB float32 inputs (not resnet50.preprocess_input).
predictor = BasePredictor(
    plant_key="zucchini",
    model_filename="Zucchini.h5",
    candidate_paths=["apps/zucchini/source/Zucchini.h5", "apps/zucchini/source/zucchini_model.h5"],
    preprocess_mode="raw",
)

CLASSES = predictor.classes


def load_model():
    """Backwards-compatible load_model accessor."""
    return predictor.get_model()


def predict(image_file: Any) -> Dict[str, Any]:
    """
    Run inference on uploaded zucchini leaf image.
    Preserves backwards compatibility with legacy predict() interface.
    """
    return predictor.predict(image_file)

"""
Hibiscus plant leaf disease predictor.
Utilizes the shared BasePredictor with hibiscus-specific class definitions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict
from apps.common.predictor import BasePredictor

logger = logging.getLogger(__name__)

# Standardized predictor instance supporting model.h5 and hibiscus_model.h5.
# Architecture and training ground truth verified from apps/hibiscus/hibiscus.ipynb:
# - Backbone: MobileNetV2 with custom dense head (512 -> Dropout(0.5) -> 8 softmax)
# - Input normalization: [-1, 1] range (inception_v3 / mobilenet_v2 preprocess_input)
# - Ground truth classes (sorted directory indexing):
#   0: Citrus Spot (Citruspot)
#   1: Early Mild Spotting (Early_Mild_Spotting)
#   2: Fungal Infected (Fungal_Infected)
#   3: Healthy (Healthy)
#   4: Mild Edge Damage (Mild_Edge_Damage)
#   5: Senescent (Senescent)
#   6: Slightly Diseased (Slightly_Diseased)
#   7: Wrinkled Leaf (Wrinkled_Leaf)
predictor = BasePredictor(
    plant_key="hibiscus",
    model_filename="model.h5",
    candidate_paths=["apps/hibiscus/source/model.h5", "apps/hibiscus/source/hibiscus_model.h5"],
    preprocess_mode="mobilenet_v2",
)

CLASSES = predictor.classes


def load_model():
    """Backwards-compatible load_model accessor."""
    return predictor.get_model()


def predict(image_file: Any) -> Dict[str, Any]:
    """
    Run inference on uploaded hibiscus leaf image.
    Preserves backwards compatibility with legacy predict() interface.
    """
    return predictor.predict(image_file)

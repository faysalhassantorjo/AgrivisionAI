"""
Base Machine Learning Predictor for AgrivisionAI Plant Disease Detection.
Handles model lifecycle, image preprocessing, softmax normalization,
inference error handling, and structured logging.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from PIL import Image

from apps.common.classes_config import get_class_names, get_disease_details

logger = logging.getLogger(__name__)


def apply_softmax_if_needed(preds: np.ndarray) -> np.ndarray:
    """
    Ensure model outputs are valid probabilities summing to ~1.0.
    If the model outputs raw unnormalized logits, apply numerically stable softmax.
    """
    total_prob = float(np.sum(preds))
    # Probabilities should sum close to 1.0 (between 0.95 and 1.05)
    if not (0.95 <= total_prob <= 1.05):
        logger.debug("Preds sum = %.4f (non-softmax). Applying softmax normalization.", total_prob)
        # Numerically stable softmax
        shifted = preds - np.max(preds, axis=-1, keepdims=True)
        exp_preds = np.exp(shifted)
        preds = exp_preds / np.sum(exp_preds, axis=-1, keepdims=True)
    return preds


class BasePredictor:
    """
    Reusable ML predictor for CNN plant disease classification models.
    Supports standardized model paths, lazy loading, per-architecture
    preprocessing (EfficientNet/raw, MobileNetV2, ResNet), and robust inference.
    """

    def __init__(
        self,
        plant_key: str,
        model_filename: Optional[str] = None,
        candidate_paths: Optional[List[Union[str, Path]]] = None,
        target_size: tuple[int, int] = (224, 224),
        preprocess_mode: str = "auto",
    ) -> None:
        self.plant_key = plant_key
        self.model_filename = model_filename
        self.target_size = target_size
        self.preprocess_mode = preprocess_mode
        self._candidate_paths = candidate_paths or []
        self._model: Any = None
        self._model_path: Optional[Path] = None
        self._load_attempted: bool = False
        self._resolved_preprocess_mode: Optional[str] = None

    @property
    def classes(self) -> List[str]:
        """Fetch current list of class names from configuration."""
        return get_class_names(self.plant_key)

    def resolve_model_path(self) -> Optional[Path]:
        """Find the model weights file across standardized and legacy locations."""
        if self._model_path and self._model_path.exists():
            return self._model_path

        # 1. Explicit candidate paths
        for candidate in self._candidate_paths:
            path = Path(candidate).resolve()
            if path.exists() and path.is_file():
                self._model_path = path
                return self._model_path

        # 2. Check plant app source directory
        base_dir = Path(__file__).resolve().parent.parent.parent
        app_source_dir = base_dir / 'apps' / self.plant_key / 'source'

        candidates = []
        if self.model_filename:
            candidates.append(app_source_dir / self.model_filename)

        # Standardized naming conventions & common legacy names
        candidates.extend([
            app_source_dir / f"{self.plant_key}_model.h5",
            app_source_dir / f"{self.plant_key.capitalize()}.h5",
            app_source_dir / "model.h5",
            app_source_dir / f"{self.plant_key.replace('_', ' ').title()}.h5",
            app_source_dir / f"{self.plant_key.replace('_', ' ')}.h5",
        ])

        for path in candidates:
            if path.exists() and path.is_file():
                self._model_path = path
                return self._model_path

        return None

    def get_model(self) -> Any:
        """Lazy loader for TensorFlow / Keras model."""
        if self._model is not None:
            return self._model

        model_path = self.resolve_model_path()
        if not model_path:
            logger.warning(
                "Model weights file for plant '%s' was not found on disk. Candidate locations checked.",
                self.plant_key
            )
            return None

        try:
            import tensorflow as tf
            logger.info("Loading Keras model for '%s' from %s", self.plant_key, model_path)
            self._model = tf.keras.models.load_model(str(model_path), compile=False)
            logger.info("Successfully loaded model for '%s' (output shape: %s)", self.plant_key, self._model.output_shape)
            return self._model
        except Exception as e:
            logger.error("Failed to load model from %s: %s", model_path, e, exc_info=True)
            self._model = None
            return None

    def is_model_loaded(self) -> bool:
        """Check if model weights exist and can be loaded."""
        return self.get_model() is not None

    def get_preprocess_mode(self) -> str:
        """
        Determine the appropriate image preprocessing strategy for the active model.
        Supports:
          - 'raw' / 'efficientnet': RGB [0, 255] float32 (for models with internal Rescaling/Normalization)
          - 'mobilenet_v2': RGB [-1, 1] float32 via (x / 127.5) - 1.0
          - 'resnet50': BGR with ImageNet mean subtraction
          - 'unit': RGB [0, 1] float32 via x / 255.0
        """
        if self.preprocess_mode != "auto":
            return self.preprocess_mode

        if self._resolved_preprocess_mode:
            return self._resolved_preprocess_mode

        model = self.get_model()
        if model is None:
            self._resolved_preprocess_mode = "raw"
            return "raw"

        # Inspect model architecture to auto-detect model family
        first_layer_names = [l.name.lower() for l in model.layers[:10]]
        first_layer_classes = [l.__class__.__name__.lower() for l in model.layers[:10]]

        # Check if model has built-in Rescaling layer (e.g. EfficientNet)
        has_internal_rescaling = "rescaling" in first_layer_classes or any("rescaling" in n for n in first_layer_names)
        is_efficientnet = has_internal_rescaling or any("stem_" in n or "block1a_" in n for n in first_layer_names)

        # Check if model is MobileNetV2
        is_mobilenet = any("expanded_conv" in n for n in first_layer_names) or "mobilenet" in getattr(model, "name", "").lower()

        # Check if model is ResNet
        is_resnet = any("conv1_conv" in n or "res2" in n for n in first_layer_names) or "resnet" in getattr(model, "name", "").lower()

        if is_efficientnet:
            mode = "raw"
        elif is_mobilenet:
            mode = "mobilenet_v2"
        elif is_resnet:
            mode = "resnet50"
        else:
            mode = "raw"

        logger.info(
            "Auto-detected preprocessing mode '%s' for '%s' (model name: %s)",
            mode, self.plant_key, getattr(model, "name", "unknown")
        )
        self._resolved_preprocess_mode = mode
        return mode

    def preprocess(self, image_file: Any) -> np.ndarray:
        """
        Preprocess uploaded image into batch tensor (1, 224, 224, 3)
        using the preprocessing strategy suitable for the model architecture.
        """
        if hasattr(image_file, 'seek'):
            image_file.seek(0)

        img = Image.open(image_file).convert("RGB")
        img = img.resize(self.target_size, Image.Resampling.BILINEAR)

        arr = np.array(img, dtype=np.float32)
        arr = np.expand_dims(arr, axis=0)

        mode = self.get_preprocess_mode()
        if mode in ("raw", "efficientnet"):
            # EfficientNet models (like Zucchini.h5) have built-in Rescaling(1/255)
            # and Normalization layers. They expect raw RGB float32 values in [0, 255].
            return arr
        elif mode == "mobilenet_v2":
            from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
            return mobilenet_preprocess(arr)
        elif mode == "resnet50":
            from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
            return resnet_preprocess(arr)
        elif mode == "unit":
            return arr / 255.0
        else:
            logger.warning("Unrecognized preprocess_mode '%s', falling back to raw RGB [0, 255]", mode)
            return arr

    def predict(self, image_file: Any) -> Dict[str, Any]:
        """
        Run inference on the uploaded leaf image.
        Returns a rich prediction dictionary or an error dictionary.
        """
        model = self.get_model()
        if model is None:
            return {
                "error": f"The ML model for {self.plant_key.replace('_', ' ').title()} is currently offline or undergoing training.",
                "status": "Unavailable",
            }

        try:
            tensor = self.preprocess(image_file)
            raw_preds = model.predict(tensor, verbose=0)

            # Ensure valid probability distribution
            preds = apply_softmax_if_needed(raw_preds)
            pred_scores = preds[0]

            idx = int(np.argmax(pred_scores))
            confidence = float(np.max(pred_scores) * 100)

            classes = self.classes
            class_name = classes[idx] if idx < len(classes) else f"Class {idx}"

            # Fetch rich treatment and description
            details = get_disease_details(self.plant_key, idx)

            logger.info(
                "Prediction for '%s': class='%s' (idx=%d), confidence=%.2f%%",
                self.plant_key, class_name, idx, confidence
            )

            # Build detailed class breakdown for debugging / transparency
            scores_breakdown = {
                (classes[i] if i < len(classes) else f"Class {i}"): round(float(pred_scores[i] * 100), 2)
                for i in range(len(pred_scores))
            }
            logger.debug("Prediction scores breakdown: %s", scores_breakdown)

            # Sort top 5 candidate probabilities for visualization
            sorted_scores = sorted(scores_breakdown.items(), key=lambda item: item[1], reverse=True)[:5]
            top_scores = [{"class": k, "score": v} for k, v in sorted_scores]

            # Qualitative confidence grading
            if confidence >= 90:
                conf_level = "Very High Confidence"
            elif confidence >= 75:
                conf_level = "High Confidence"
            elif confidence >= 50:
                conf_level = "Moderate Confidence"
            else:
                conf_level = "Low Confidence"

            return {
                "class": details.get('class', class_name),
                "confidence": round(confidence, 2),
                "confidence_level": conf_level,
                "treatment": details.get('treatment', ''),
                "description": details.get('description', ''),
                "status": details.get('status', 'Analyzed'),
                "class_index": idx,
                "scores": scores_breakdown,
                "top_scores": top_scores,
            }

        except Exception as e:
            logger.error("Inference failure for '%s': %s", self.plant_key, e, exc_info=True)
            return {
                "error": "Failed to analyze the leaf image due to an internal processing error. Please try again with another image.",
                "details": str(e),
            }

"""
Service layer for AgrivisionAI Plant Disease Detection.
Decouples business logic, validation, and analytics from the HTTP view layer.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from django.core.files.uploadedfile import UploadedFile

from apps.common.classes_config import get_plant_config
from apps.common.predictor import BasePredictor
from apps.common.validators import validate_uploaded_image

logger = logging.getLogger(__name__)


class PlantDiseaseService:
    """
    Application service managing the plant disease diagnosis workflow.
    """

    def __init__(self, predictor: BasePredictor) -> None:
        self.predictor = predictor
        self.plant_key = predictor.plant_key

    def get_context_metadata(self) -> Dict[str, Any]:
        """Return base metadata about plant, supported diseases, and model status."""
        plant_cfg = get_plant_config(self.plant_key)
        model_ready = self.predictor.is_model_loaded()

        return {
            'plant_key': self.plant_key,
            'plant_name': plant_cfg.get('name', self.plant_key.title()),
            'scientific_name': plant_cfg.get('scientific_name', ''),
            'plant_icon': plant_cfg.get('icon', '🌿'),
            'model_load_status': 'Online' if model_ready else 'Standby / In Training',
            'is_model_ready': model_ready,
            'supported_classes': plant_cfg.get('classes', {}),
        }

    def process_diagnosis_request(self, image_file: Optional[UploadedFile]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate uploaded image and invoke the predictor.

        Returns:
            (result_dict: Optional[Dict], error_message: Optional[str])
        """
        # 1. Validation
        is_valid, validation_error = validate_uploaded_image(image_file)
        if not is_valid:
            logger.warning("Upload validation failed for %s: %s", self.plant_key, validation_error)
            return None, validation_error

        # 2. Prediction
        prediction = self.predictor.predict(image_file)
        if "error" in prediction:
            return None, prediction["error"]

        return prediction, None

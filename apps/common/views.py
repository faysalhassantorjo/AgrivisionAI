"""
Reusable Django view for plant disease detection tools.
Replaces duplicated view logic across individual plant apps.
Supports standard HTTP POST and asynchronous Ajax JSON workflows.
"""

from __future__ import annotations

import base64
import logging
from typing import Any, Dict, Optional

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from apps.common.predictor import BasePredictor
from apps.common.services import PlantDiseaseService

logger = logging.getLogger(__name__)


class PlantDiseaseView(View):
    """
    Standard class-based view for plant leaf diagnosis.
    Handles GET requests by showing the diagnosis form.
    Handles POST requests by validating input, running model prediction,
    and rendering results or error alerts.
    """

    plant_key: str = ""
    template_name: str = "tool_base.html"
    predictor: Optional[BasePredictor] = None

    def get_service(self) -> PlantDiseaseService:
        if self.predictor is None:
            self.predictor = BasePredictor(self.plant_key)
        return PlantDiseaseService(self.predictor)

    def get_base_context(self) -> Dict[str, Any]:
        service = self.get_service()
        ctx = service.get_context_metadata()
        ctx["uploaded_image_url"] = ""
        ctx["result"] = None
        ctx["error"] = None
        return ctx

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = self.get_base_context()
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = self.get_base_context()
        service = self.get_service()

        image = request.FILES.get("image")

        # Encode image to base64 Data URL for immediate display in result view
        image_data_uri = ""
        if image:
            try:
                if hasattr(image, 'seek'):
                    image.seek(0)
                raw_bytes = image.read()
                mime = getattr(image, 'content_type', 'image/jpeg') or 'image/jpeg'
                image_data_uri = f"data:{mime};base64,{base64.b64encode(raw_bytes).decode('utf-8')}"
                if hasattr(image, 'seek'):
                    image.seek(0)
            except Exception as e:
                logger.warning("Could not encode uploaded image to base64 Data URI: %s", e)

        result, error = service.process_diagnosis_request(image)

        if error:
            context["error"] = error
        else:
            if result and image_data_uri:
                result["image_url"] = image_data_uri
            context["result"] = result
            context["uploaded_image_url"] = image_data_uri

        # Check for Ajax / JSON request
        is_ajax = (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or "application/json" in request.headers.get("Accept", "")
            or request.GET.get("format") == "json"
        )

        if is_ajax:
            if error:
                return JsonResponse({"error": error, "status": "error"}, status=400)
            return JsonResponse({"result": result, "status": "success"})

        return render(request, self.template_name, context)


def create_disease_view(plant_key: str, template_name: str, predictor: Optional[BasePredictor] = None):
    """
    Factory helper to generate a functional or class-based view for urls.py or views.py.
    """
    return PlantDiseaseView.as_view(
        plant_key=plant_key,
        template_name=template_name,
        predictor=predictor,
    )

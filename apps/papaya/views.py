"""
Views for Papaya leaf disease detection.
"""

from apps.common.views import PlantDiseaseView
from apps.papaya.source.predictor import predictor


class PapayaDiseaseView(PlantDiseaseView):
    plant_key = "papaya"
    template_name = "papaya/index.html"
    predictor = predictor


index = PapayaDiseaseView.as_view()

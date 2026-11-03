"""
Views for Hibiscus leaf disease detection.
"""

from apps.common.views import PlantDiseaseView
from apps.hibiscus.source.predictor import predictor


class HibiscusDiseaseView(PlantDiseaseView):
    plant_key = "hibiscus"
    template_name = "hibiscus/index.html"
    predictor = predictor


index = HibiscusDiseaseView.as_view()

"""
Views for Tea leaf disease detection.
"""

from apps.common.views import PlantDiseaseView
from apps.tea_leaf.source.predictor import predictor


class TeaLeafDiseaseView(PlantDiseaseView):
    plant_key = "tea_leaf"
    template_name = "tea_leaf/index.html"
    predictor = predictor


index = TeaLeafDiseaseView.as_view()

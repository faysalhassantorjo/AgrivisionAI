"""
Views for Zucchini leaf disease detection.
"""

from apps.common.views import PlantDiseaseView
from apps.zucchini.source.predictor import predictor


class ZucchiniDiseaseView(PlantDiseaseView):
    plant_key = "zucchini"
    template_name = "zucchini/index.html"
    predictor = predictor


index = ZucchiniDiseaseView.as_view()

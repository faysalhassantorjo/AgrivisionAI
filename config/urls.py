"""
URL configuration for AgrivisionAI / PlantMD project.
"""

from datetime import datetime, timezone
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.urls import include, path

from apps.common.classes_config import get_plant_config


def home(request: HttpRequest):
    """Landing homepage displaying all plant disease diagnostic tools."""
    plants = [
        {
            'slug': 'hibiscus',
            'url': '/hibiscus/',
            'name': 'Hibiscus Leaf Disease',
            'icon': '🌺',
            'bg': '#e4f5ec',
            'status': 'Live',
            'badge_class': 'badge-live',
            'desc': 'Detect Healthy, Mild Edge Damage, Citrus Spot, Early Mild Spotting, Fungal Infected, Senescent, and Wrinkled foliage.',
        },
        {
            'slug': 'zucchini',
            'url': '/zucchini/',
            'name': 'Zucchini Leaf Disease',
            'icon': '🍃',
            'bg': '#e4f5ec',
            'status': 'Live',
            'badge_class': 'badge-live',
            'desc': 'Detect Healthy, Yellow Mosaic Virus, Angular Leaf Spot, Anthracnose, Powdery Mildew, and Downy Mildew.',
        },
        {
            'slug': 'tea_leaf',
            'url': '/tea-leaf/',
            'name': 'Tea Leaf Disease',
            'icon': '🍵',
            'bg': '#e4f5ec',
            'status': 'Live',
            'badge_class': 'badge-live',
            'desc': 'Detect Algal Leaf Spot, Anthracnose, Bird\'s Eye Spot, Brown Blight, Gray Blight, and Red Leaf Spot in Camellia sinensis.',
        },
        {
            'slug': 'papaya',
            'url': '/papaya/',
            'name': 'Papaya Leaf Disease',
            'icon': '🍈',
            'bg': '#ffe8d6',
            'status': 'Beta',
            'badge_class': 'badge-soon',
            'desc': 'Identify ringspot virus, anthracnose, leaf curl, and powdery mildew with deep neural networks.',
        },
    ]
    return render(request, 'home.html', {'plants': plants})


def health_check(request: HttpRequest):
    """
    Health check endpoint for Docker container probes, Kubernetes, and monitoring.
    Returns status 200 with service and model status details.
    """
    from apps.common.predictor import BasePredictor

    # Check status of models
    models_status = {
        'hibiscus': 'ready' if BasePredictor('hibiscus').resolve_model_path() else 'missing_weights',
        'zucchini': 'ready' if BasePredictor('zucchini').resolve_model_path() else 'missing_weights',
        'tea_leaf': 'ready' if BasePredictor('tea_leaf').resolve_model_path() else 'missing_weights',
        'papaya': 'ready' if BasePredictor('papaya').resolve_model_path() else 'missing_weights',
    }

    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'debug': settings.DEBUG,
        'models': models_status,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),

    path('tea-leaf/', include('apps.tea_leaf.urls')),
    path('zucchini/', include('apps.zucchini.urls')),
    path('hibiscus/', include('apps.hibiscus.urls')),
    path('papaya/', include('apps.papaya.urls')),

    path('', home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

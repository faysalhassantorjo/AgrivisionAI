"""
Centralized plant disease class configuration loader.
Provides disease names, status, descriptions, and recommended treatments.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / 'config' / 'classes.yaml'

# Default embedded fallback data to ensure system works under all conditions
FALLBACK_CLASSES: Dict[str, Dict[str, Any]] = {
    'hibiscus': {
        'name': 'Hibiscus',
        'scientific_name': 'Hibiscus rosa-sinensis',
        'icon': '🌺',
        'classes': {
            0: {'name': 'Mild Edge Damage', 'status': 'Diseased', 'treatment': 'Prune affected leaves, avoid harsh wind, and inspect for pests.'},
            1: {'name': 'Citrus Spot', 'status': 'Diseased', 'treatment': 'Apply copper-based fungicide spray and avoid overhead watering.'},
            2: {'name': 'Early Mild Spotting', 'status': 'Diseased', 'treatment': 'Isolate plant, sanitize shears, and apply neem oil preventively.'},
            3: {'name': 'Senescent', 'status': 'Aging', 'treatment': 'Gently remove yellowing leaves to encourage new shoot development.'},
            4: {'name': 'Slightly Diseased', 'status': 'Diseased', 'treatment': 'Monitor for 3-5 days. Ensure well-drained soil and mild foliar feed.'},
            5: {'name': 'Fungal Infected', 'status': 'Diseased', 'treatment': 'Remove infected leaves. Spray Mancozeb or Chlorothalonil fungicide.'},
            6: {'name': 'Wrinkled', 'status': 'Physiological / Viral', 'treatment': 'Inspect leaf undersides for aphids or whiteflies; spray insecticidal soap.'},
            7: {'name': 'Healthy', 'status': 'Healthy', 'treatment': 'No treatment required. Maintain current care routine.'},
        },
    },
    'zucchini': {
        'name': 'Zucchini',
        'scientific_name': 'Cucurbita pepo',
        'icon': '🍃',
        'classes': {
            2: {'name': 'Yellow Mosaic Virus', 'status': 'Diseased', 'treatment': 'Remove infected plants promptly to avoid aphid transmission.'},
            1: {'name': 'Powdery Mildew', 'status': 'Diseased', 'treatment': 'Apply potassium bicarbonate, sulfur spray, or systemic fungicide.'},
            0: {'name': 'Angular Leaf Spot', 'status': 'Diseased', 'treatment': 'Apply copper hydroxide bactericide. Do not handle plants when wet.'},
            3: {'name': 'Anthracnose', 'status': 'Diseased', 'treatment': 'Apply Chlorothalonil protectant fungicide and rotate crops.'},
            4: {'name': 'Alternaria Leaf Blight', 'status': 'Diseased', 'treatment': 'Apply preventive fungicide at first signs and use drip irrigation.'},
            5: {'name': 'Gummy Stem Blight', 'status': 'Diseased', 'treatment': 'Apply triazole or strobilurin fungicides and ensure good plant spacing.'},
            6: {'name': 'Healthy', 'status': 'Healthy', 'treatment': 'No treatment needed. Keep soil evenly moist and fertile.'},
            7: {'name': 'Scab', 'status': 'Diseased', 'treatment': 'Use resistant varieties and apply protective fungicides in humid weather.'},
            8: {'name': 'Downy Mildew', 'status': 'Diseased', 'treatment': 'Apply targeted oomycete fungicides (e.g. metalaxyl, cyazofamid).'},
        },
    },
    'tea_leaf': {
        'name': 'Tea Leaf',
        'scientific_name': 'Camellia sinensis',
        'icon': '🍵',
        'classes': {
            0: {'name': 'Algal Leaf Spot', 'status': 'Diseased', 'treatment': 'Prune canopy to increase sunlight; spray copper oxychloride.'},
            1: {'name': 'Anthracnose', 'status': 'Diseased', 'treatment': 'Apply copper fungicide or carbendazim. Clear bush base litter.'},
            2: {'name': "Bird's Eye Spot", 'status': 'Diseased', 'treatment': 'Spray protective dithiocarbamate fungicide; supply potassium.'},
            3: {'name': 'Brown Blight', 'status': 'Diseased', 'treatment': 'Prune affected shoots; apply systemic Hexaconazole or Propiconazole.'},
            4: {'name': 'Gray Blight', 'status': 'Diseased', 'treatment': 'Improve bush sanitation, avoid plucking wounds, and spray copper.'},
            5: {'name': 'Healthy', 'status': 'Healthy', 'treatment': 'No treatment needed. Continue regular plucking and nutrition.'},
            6: {'name': 'Red Leaf Spot', 'status': 'Diseased', 'treatment': 'Apply Mancozeb or systemic triazole fungicides; avoid deep shade.'},
            7: {'name': 'White Spot', 'status': 'Diseased', 'treatment': 'Spray wettable sulfur or copper fungicides; maintain soil pH.'},
        },
    },
    'papaya': {
        'name': 'Papaya',
        'scientific_name': 'Carica papaya',
        'icon': '🍈',
        'classes': {
            0: {'name': 'Anthracnose', 'status': 'Diseased', 'treatment': 'Apply copper hydroxide or azoxystrobin regularly during wet weather.'},
            1: {'name': 'Black Spot', 'status': 'Diseased', 'treatment': 'Remove older spotted leaves and apply Mancozeb sprays.'},
            2: {'name': 'Healthy', 'status': 'Healthy', 'treatment': 'No treatment required. Maintain proper irrigation.'},
            3: {'name': 'Leaf Curl', 'status': 'Diseased', 'treatment': 'Control whitefly vectors; eradicate severely affected plants.'},
            4: {'name': 'Powdery Mildew', 'status': 'Diseased', 'treatment': 'Dust with sulfur or spray potassium bicarbonate.'},
            5: {'name': 'Phytophthora Blight', 'status': 'Diseased', 'treatment': 'Ensure soil drainage; apply phosphonate fungicide drench.'},
            6: {'name': 'Ringspot Virus', 'status': 'Diseased', 'treatment': 'Rogue out infected trees immediately to prevent aphid spread.'},
            7: {'name': 'Yellow Leaf Curl', 'status': 'Diseased', 'treatment': 'Eliminate weed vectors and protect young trees with insect mesh.'},
        },
    },
}

_CONFIG_CACHE: Optional[Dict[str, Any]] = None


def load_classes_config() -> Dict[str, Any]:
    """Load configuration from classes.yaml or fallback to embedded dictionary."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    if CONFIG_PATH.exists():
        try:
            import yaml
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict) and loaded:
                    _CONFIG_CACHE = loaded
                    return _CONFIG_CACHE
        except Exception as e:
            logger.warning("Could not read classes.yaml (%s). Using embedded fallback.", e)

    _CONFIG_CACHE = FALLBACK_CLASSES
    return _CONFIG_CACHE


def get_plant_config(plant_key: str) -> Dict[str, Any]:
    """Retrieve full configuration dictionary for a given plant."""
    cfg = load_classes_config()
    return cfg.get(plant_key, FALLBACK_CLASSES.get(plant_key, {}))


def get_class_names(plant_key: str) -> List[str]:
    """Return ordered list of class names for model index mapping."""
    plant_cfg = get_plant_config(plant_key)
    classes_dict = plant_cfg.get('classes', {})
    sorted_keys = sorted(classes_dict.keys(), key=lambda k: int(k))
    names = []
    for k in sorted_keys:
        val = classes_dict[k]
        if isinstance(val, dict):
            names.append(val.get('name', str(k)))
        else:
            names.append(str(val))
    return names


def get_disease_details(plant_key: str, class_idx: int) -> Dict[str, str]:
    """Get rich metadata (name, description, treatment, status) for a specific disease index."""
    plant_cfg = get_plant_config(plant_key)
    classes_dict = plant_cfg.get('classes', {})

    # Match key as int or string
    info = classes_dict.get(class_idx) or classes_dict.get(str(class_idx))
    if isinstance(info, dict):
        return {
            'class': info.get('name', f'Class {class_idx}'),
            'status': info.get('status', 'Analyzed'),
            'description': info.get('description', ''),
            'treatment': info.get('treatment', 'Consult a local agronomist for customized advice.'),
        }

    return {
        'class': str(info) if info else f'Class {class_idx}',
        'status': 'Analyzed',
        'description': '',
        'treatment': 'Consult a local agricultural extension specialist for treatment options.',
    }

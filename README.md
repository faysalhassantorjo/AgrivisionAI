# AgrivisionAI / PlantMD 🌿

> **Production-grade AI Plant Disease Diagnosis and Agricultural Advisory System built with Django, TensorFlow/Keras, and Docker.**

---

## 📖 Overview

AgrivisionAI is a computer vision platform designed to assist farmers, agronomists, and researchers with automated plant disease detection from leaf imagery. Users can upload leaf photos via an intuitive web interface or REST/JSON endpoints to receive instant condition diagnoses, confidence scores, and actionable agronomic treatments.

### Supported Plant Models
- **🌺 Hibiscus:** 8 classes (Healthy, Mild Edge Damage, Citrus Spot, Early Mild Spotting, Fungal Infected, Senescent, Wrinkled)
- **🍃 Zucchini:** 9 classes (Healthy, Yellow Mosaic Virus, Angular Leaf Spot, Anthracnose, Powdery Mildew, Alternaria Blight, Gummy Stem Blight, Scab, Downy Mildew)
- **🍵 Tea Leaf:** 8 classes (Healthy, Algal Leaf Spot, Anthracnose, Bird's Eye Spot, Brown Blight, Gray Blight, Red Leaf Spot, White Spot)
- **🍈 Papaya:** 8 classes (Healthy, Ringspot Virus, Anthracnose, Leaf Curl, Black Spot, Powdery Mildew, Phytophthora Blight, Yellow Leaf Curl)

---

## 🏗️ Architecture

```
                                  [ User / Client ]
                                          │
                                          ▼
                               [ Nginx Reverse Proxy ]
                               (SSL, Ports 80 / 443)
                                          │
                                          ▼
                                  [ Gunicorn WSGI ]
                               (Django Application)
                                          │
                 ┌────────────────────────┼────────────────────────┐
                 ▼                        ▼                        ▼
         [ Views Layer ]          [ Service Layer ]       [ Health Probes ]
     (PlantDiseaseView CBV)    (PlantDiseaseService)        (/health/)
                 │                        │
                 ▼                        ▼
       [ Templates & Static ]    [ Input Validation ]
      (tool_base.html, CSS/JS)   (Size, MIME, Pillow)
                                          │
                                          ▼
                                 [ BasePredictor ]
                          (Softmax Safeguard & Logging)
                                          │
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
            [ TensorFlow Models ]                     [ config/classes.yaml ]
             (ResNet / DenseNet)                     (Treatments & Metadata)
```

### Key Modules
- **`apps/common/`:** Reusable ML prediction engine (`BasePredictor`), validation utilities, service layer, and class-based views.
- **`config/classes.yaml`:** Centralized disease taxonomy, descriptions, and treatment protocols.
- **`static/css/tool.css` & `static/js/upload.js`:** Shared styling, client-side validation, drag-and-drop file upload, and animations.
- **`templates/tool_base.html`:** Consolidated responsive base template eliminating HTML duplication across tools.

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose **OR** Python 3.11+
- Git

### 1. Environment Configuration
Copy the sample environment file and configure secrets:
```bash
cp .env.example .env
```

Key environment variables in `.env`:
```ini
DJANGO_SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://yourdomain.com
MAX_UPLOAD_SIZE_MB=10
LOG_LEVEL=INFO
```

---

### 2. Running with Docker Compose (Recommended)

#### Production Mode
```bash
docker compose up -d --build
```
This launches:
- `web`: Gunicorn serving Django on port `8000` with automated health checks.
- `nginx`: Reverse proxy with SSL termination on ports `80` and `443`.

#### Development Mode
```bash
docker compose -f docker-compose.dev.yml up --build
```

---

### 3. Running Locally (Without Docker)

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Linux/macOS:
   source venv/bin/activate
   # Windows:
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```
   Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🩺 Health Check & Monitoring

AgrivisionAI includes a dedicated JSON health probe endpoint at `/health/` for Docker, Kubernetes, and uptime monitoring:

```bash
curl http://localhost:8000/health/
```

**Sample Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-11-02T10:30:00Z",
  "debug": false,
  "models": {
    "hibiscus": "ready",
    "zucchini": "ready",
    "tea_leaf": "ready",
    "papaya": "ready"
  }
}
```

---

## ➕ How to Add a New Plant Disease Model

Adding a new crop model takes less than 5 minutes thanks to the shared abstraction layer:

### Step 1: Add Disease Classes in `config/classes.yaml`
```yaml
tomato:
  name: "Tomato"
  scientific_name: "Solanum lycopersicum"
  icon: "🍅"
  classes:
    0:
      name: "Bacterial Spot"
      status: "Diseased"
      description: "Dark water-soaked lesions caused by Xanthomonas."
      treatment: "Apply copper fungicide and avoid overhead watering."
    1:
      name: "Healthy"
      status: "Healthy"
      description: "Vibrant foliage free of lesions."
      treatment: "No treatment required."
```

### Step 2: Create App with Shared BasePredictor & View
In `apps/tomato/source/predictor.py`:
```python
from apps.common.predictor import BasePredictor

predictor = BasePredictor(plant_key="tomato", model_filename="tomato_model.h5")
predict = predictor.predict
```

In `apps/tomato/views.py`:
```python
from apps.common.views import PlantDiseaseView
from .source.predictor import predictor

class TomatoDiseaseView(PlantDiseaseView):
    plant_key = "tomato"
    template_name = "tomato/index.html"
    predictor = predictor

index = TomatoDiseaseView.as_view()
```

### Step 3: Create Template Extending `tool_base.html`
In `apps/tomato/templates/tomato/index.html`:
```html
{% extends 'tool_base.html' %}
{% block tool_title %}Tomato Leaf Disease Detection — PlantMD{% endblock %}
{% block hero_heading %}Tomato Leaf<br><em>Diagnosis</em>{% endblock %}
{% block dropzone_icon %}🍅{% endblock %}
```

### Step 4: Register URL
In `config/urls.py`:
```python
path('tomato/', include('apps.tomato.urls')),
```

---

## 🧪 Testing

Execute the automated test suite:
```bash
python manage.py test
```

Or within Docker:
```bash
docker compose exec web python manage.py test
```

---

## 🛡️ Security Best Practices
- **Never commit `.env` or `db.sqlite3`** to source control (both are protected via `.gitignore`).
- **Always keep `DEBUG=False` in production.** When `DEBUG=False`, Django strictly requires `DJANGO_SECRET_KEY` and rejects fallback development keys.
- **Upload Restrictions:** Files are strictly validated for size ($\le 10\text{MB}$), MIME type, and binary header integrity before model tensor conversion.
- **Nginx Security:** Client request body limit set to `25M` to prevent Denial of Service (DoS) attacks.

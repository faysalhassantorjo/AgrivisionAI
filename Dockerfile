# ---- Base Image ----
FROM python:3.11-slim

# ---- Environment settings (important for ML + Docker speed) ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ---- System dependencies (keep minimal) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# ---- Work directory ----
WORKDIR /app

# ---- Upgrade pip first (avoids reinstall issues) ----
RUN pip install --upgrade pip

# ---- Copy only requirements first (for Docker cache optimization) ----
COPY requirements.txt .

# ---- Install dependencies (layer cached) ----
RUN pip install --no-cache-dir --timeout=1000 -r requirements.txt

# ---- Copy project after dependencies ----
COPY . .

# ---- Expose Django port ----
EXPOSE 8000

# ---- Default command ----
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# Dockerfile Production-Ready
# GGR Crédit Workflow

FROM python:3.12-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer un utilisateur non-root
RUN useradd -m -u 1000 django && \
    mkdir -p /app /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer les dépendances Python
COPY --chown=django:django requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn whitenoise

# Copier le code de l'application
COPY --chown=django:django . .

# S'assurer que les dossiers ont les bonnes permissions
RUN chown -R django:django /app/staticfiles /app/media /app/logs

# Collecter les static files en tant qu'utilisateur django
USER django
RUN python manage.py collectstatic --noinput --settings=core.settings.base
USER root

# Changer vers l'utilisateur non-root
USER django

# Exposer le port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys, urllib.request; \
url='http://127.0.0.1:8000/health/'; \
urllib.request.urlopen(url, timeout=5).read(); \
sys.exit(0)"

# Commande de démarrage
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]

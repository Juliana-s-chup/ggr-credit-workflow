"""
Base settings for ggr_credit_workflow Django project.
Shared by dev and prod.
"""

from pathlib import Path
import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# django-environ
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

# SECURITE: SECRET_KEY obligatoire, pas de valeur par defaut
try:
    SECRET_KEY = env("SECRET_KEY")
    if SECRET_KEY == "insecure-dev-key-change-me":
        raise ImproperlyConfigured(
            "SECRET_KEY must be changed from default value! "
            "Generate a secure key with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
        )
except environ.ImproperlyConfigured:
    raise ImproperlyConfigured(
        "SECRET_KEY environment variable is required! "
        "Set it in your .env file or environment."
    )

# DEBUG: False par defaut (securite production)
DEBUG = env.bool("DEBUG", default=False)

# ALLOWED_HOSTS: Obligatoire en production
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must be set when DEBUG=False! "
        "Set ALLOWED_HOSTS in your .env file (comma-separated list)."
    )

# Core apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "suivi_demande",
    "analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "suivi_demande.middleware_portal.PortalAccessMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "suivi_demande.context_processors.notifications",
            ],
        },
    }
]

# Cache Configuration (en mémoire pour le développement)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "OPTIONS": {
            "MAX_ENTRIES": 1000
        }
    }
}

# Session Configuration (utiliser la base de données)
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS uniquement en production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security Headers (uniquement en production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# CSRF Protection
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# WSGI Application
WSGI_APPLICATION = "core.wsgi.application"

# Configuration PostgreSQL (utilisee par defaut)
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=(
            "postgresql://{user}:{password}@{host}:{port}/{name}".format(
                user=env("DB_USER", default="credit_user"),
                password=env("DB_PASSWORD", default=""),
                host=env("DB_HOST", default="localhost"),
                port=env("DB_PORT", default="5432"),
                name=env("DB_NAME", default="credit_db"),
            )
        ),
    )
}

# Internationalization
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Brazzaville"
USE_I18N = True
USE_TZ = True

# Static/Media
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Auth redirects
LOGIN_REDIRECT_URL = "pro:dashboard"
LOGOUT_REDIRECT_URL = "login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security/hosts (overridden in client.py and pro.py)
# ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
# Commente car defini specifiquement dans client.py et pro.py
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost",
        "https://localhost",
        "http://127.0.0.1",
        "https://127.0.0.1",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://localhost:8000",
        "https://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "https://localhost:8001",
        "https://127.0.0.1:8001",
        "http://localhost:8002",
        "http://127.0.0.1:8002",
        "https://localhost:8002",
        "https://127.0.0.1:8002",
        "http://pro.ggr-credit.local:8002",
        "https://pro.ggr-credit.local:8002",
        "http://client.ggr-credit.local:8001",
        "https://client.ggr-credit.local:8001",
    ],
)

# Email defaults (override in env)
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@ggr-credit.local")

# WhiteNoise storages (enabled in prod)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# Logging configuration professionnelle
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} | {name} | {module}.{funcName}:{lineno} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[{levelname}] {asctime} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "security": {
            "format": "[SECURITY] {asctime} | User: {user} | IP: {ip} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        # Console - Tous les logs en developpement
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        # Fichier general - INFO et superieur
        "file_general": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "general.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        # Fichier debug - Tous les logs DEBUG
        "file_debug": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "debug.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
            "filters": ["require_debug_true"],
        },
        # Fichier erreurs - WARNING et superieur
        "file_error": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "error.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        # Fichier securite - Authentification, permissions, acces
        "file_security": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "security.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 15,
            "formatter": "verbose",
        },
        # Fichier workflow - Actions metier importantes
        "file_workflow": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "workflow.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        # Email admin en cas d'erreur critique (production)
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
            "formatter": "verbose",
        },
    },
    "loggers": {
        # Logger Django par defaut
        "django": {
            "handlers": ["console", "file_general", "file_error"],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        # Logger pour les requetes Django
        "django.request": {
            "handlers": ["console", "file_error", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        # Logger pour la securite Django
        "django.security": {
            "handlers": ["console", "file_security"],
            "level": "INFO",
            "propagate": False,
        },
        # Logger application suivi_demande
        "suivi_demande": {
            "handlers": ["console", "file_general", "file_debug", "file_error"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        # Logger securite application
        "suivi_demande.security": {
            "handlers": ["console", "file_security"],
            "level": "INFO",
            "propagate": False,
        },
        # Logger workflow metier
        "suivi_demande.workflow": {
            "handlers": ["console", "file_workflow", "file_general"],
            "level": "INFO",
            "propagate": False,
        },
        # Logger modeles
        "suivi_demande.models": {
            "handlers": ["console", "file_general", "file_debug"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
    # Logger root (fallback)
    "root": {
        "handlers": ["console", "file_general"],
        "level": "INFO",
    },
}

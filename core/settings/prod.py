"""
Configuration Django pour l'environnement de PRODUCTION
"""

from .base import *
import os

# SÃ‰CURITÃ‰
DEBUG = False

# Charger depuis variables d'environnement
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE-ME-IN-PRODUCTION")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Base de donnÃ©es (depuis .env)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "ggr_credit_workflow"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5434"),
    }
}

# Logging production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR.parent, "logs", "django.log"),
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "security": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR.parent, "logs", "security.log"),
            "maxBytes": 1024 * 1024 * 15,
            "backupCount": 10,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
        "django.security": {
            "handlers": ["security"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# CrÃ©er le dossier logs s'il n'existe pas
LOGS_DIR = os.path.join(BASE_DIR.parent, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

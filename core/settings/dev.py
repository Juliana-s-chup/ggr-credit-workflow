"""
Development settings.
"""

from .base import *  # noqa

DEBUG = True

# Database: PostgreSQL from environment
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="credit_db"),
        "USER": env("DB_USER", default="credit_user"),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default="127.0.0.1"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

# Hosts / CSRF suitable for local dev (can be overridden via .env)
# En mode DEBUG, accepter tous les domaines
ALLOWED_HOSTS = ["*"]  # Accepte tous les domaines en developpement

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# In development, avoid WhiteNoise manifest storage to prevent missing manifest errors
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}

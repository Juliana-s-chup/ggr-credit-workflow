"""
Development settings.
"""

from .base import *  # noqa

DEBUG = True

# Database: prefer DATABASE_URL (Docker-friendly), fallback to DB_*
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=(
            "postgresql://{user}:{password}@{host}:{port}/{name}".format(
                user=env("DB_USER", default="credit_user"),
                password=env("DB_PASSWORD", default=""),
                host=env("DB_HOST", default="127.0.0.1"),
                port=env("DB_PORT", default="5432"),
                name=env("DB_NAME", default="credit_db"),
            )
        ),
    )
}

# Hosts / CSRF suitable for local dev (can be overridden via .env)
# En mode DEBUG, accepter tous les domaines
ALLOWED_HOSTS = ["*"]  # Accepte tous les domaines en developpement

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# In development, avoid WhiteNoise manifest storage to prevent missing manifest errors
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
}

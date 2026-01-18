"""
Settings pour le portail CLIENT
Sous-domaine : client.ggr-credit.cg
"""

from .base import *

# Portail spécifique
PORTAL_TYPE = "CLIENT"

# Restrictions d'accès
ALLOWED_ROLES = ["CLIENT"]

# URLs: utiliser le routeur principal qui inclut déjà le namespace `client`
ROOT_URLCONF = "core.urls"

# Templates spécifiques - Chercher d'abord dans portail_client, puis fallback
TEMPLATES[0]["DIRS"] = [
    BASE_DIR / "templates" / "portail_client",
    BASE_DIR / "templates",  # Fallback
]

# Domaine autorisé - Ne pas utiliser env.list pour éviter les conflits
ALLOWED_HOSTS = [
    "client.ggr-credit.cg",
    "client.ggr-credit.local",  # Pour dev local
    "localhost",
    "127.0.0.1",
]

# Désactiver l'admin Django sur ce portail
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django.contrib.admin"]

# Ajouter le middleware de contrôle d'accès (TEMPORAIREMENT DÉSACTIVÉ POUR DEBUG)
# MIDDLEWARE += [
#     'suivi_demande.middleware_portal.PortalAccessMiddleware',
# ]

# Session cookies (TEMPORAIREMENT SIMPLIFIÉ POUR DEBUG)
SESSION_COOKIE_NAME = "ggr_client_session"
# SESSION_COOKIE_DOMAIN = '.ggr-credit.cg'  # Désactivé temporairement
SESSION_COOKIE_DOMAIN = None  # Utiliser le domaine par défaut

# Redirect après login
LOGIN_REDIRECT_URL = "/dashboard/"
LOGIN_URL = "/accounts/login/"

# Redirect après logout
LOGOUT_REDIRECT_URL = "/accounts/login/"

# Sécurité renforcée (désactivée en dev local)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)

"""
Settings pour le portail CLIENT
Sous-domaine : client.ggr-credit.cg
"""

from .base import *

# Portail specifique
PORTAL_TYPE = "CLIENT"

# Restrictions d'acces
ALLOWED_ROLES = ["CLIENT"]

# URLs: utiliser le routeur principal qui inclut deje  le namespace `client`
ROOT_URLCONF = "core.urls"

# Templates specifiques - Chercher d'abord dans portail_client, puis fallback
TEMPLATES[0]["DIRS"] = [
    BASE_DIR / "templates" / "portail_client",
    BASE_DIR / "templates",  # Fallback
]

# Domaine autorise - Ne pas utiliser env.list pour eviter les conflits
ALLOWED_HOSTS = [
    "client.ggr-credit.cg",
    "client.ggr-credit.local",  # Pour dev local
    "localhost",
    "127.0.0.1",
]

# Desactiver l'admin Django sur ce portail
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django.contrib.admin"]

# Ajouter le middleware de controle d'acces (TEMPORAIREMENT De‰SACTIVe‰ POUR DEBUG)
# MIDDLEWARE += [
#     'suivi_demande.middleware_portal.PortalAccessMiddleware',
# ]

# Session cookies (TEMPORAIREMENT SIMPLIFIe‰ POUR DEBUG)
SESSION_COOKIE_NAME = "ggr_client_session"
# SESSION_COOKIE_DOMAIN = '.ggr-credit.cg'  # Desactive temporairement
SESSION_COOKIE_DOMAIN = None  # Utiliser le domaine par defaut

# Redirect apres login
LOGIN_REDIRECT_URL = "/dashboard/"
LOGIN_URL = "/accounts/login/"

# Redirect apres logout
LOGOUT_REDIRECT_URL = "/accounts/login/"

# Securite renforcee (desactivee en dev local)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)

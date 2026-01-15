"""
Settings pour le portail PROFESSIONNEL
Sous-domaine : pro.ggr-credit.cg
"""
from .base import *

# Portail spécifique
PORTAL_TYPE = 'PROFESSIONAL'

# Restrictions d'accès
ALLOWED_ROLES = ['GESTIONNAIRE', 'ANALYSTE', 'RESPONSABLE_GGR', 'BOE', 'SUPER_ADMIN']

# URLs: utiliser le routeur principal qui inclut déjà le namespace `pro`
ROOT_URLCONF = 'core.urls'

# Templates spécifiques - Chercher d'abord dans portail_pro, puis fallback
TEMPLATES[0]['DIRS'] = [
    BASE_DIR / 'templates' / 'portail_pro',
    BASE_DIR / 'templates',  # Fallback
]

# Domaine autorisé - Ne pas utiliser env.list pour éviter les conflits
ALLOWED_HOSTS = [
    'pro.ggr-credit.cg',
    'pro.ggr-credit.local',  # Pour dev local
    'localhost',
    '127.0.0.1',
]

# Garder l'admin Django sur ce portail
# (déjà dans INSTALLED_APPS de base.py)

# Ajouter le middleware de contrôle d'accès (TEMPORAIREMENT DÉSACTIVÉ POUR DEBUG)
# MIDDLEWARE += [
#     'suivi_demande.middleware_portal.PortalAccessMiddleware',
# ]

# Session cookies (TEMPORAIREMENT SIMPLIFIÉ POUR DEBUG)
SESSION_COOKIE_NAME = 'ggr_pro_session'
# SESSION_COOKIE_DOMAIN = '.ggr-credit.cg'  # Désactivé temporairement
SESSION_COOKIE_DOMAIN = None  # Utiliser le domaine par défaut

# Redirect après login
LOGIN_REDIRECT_URL = '/dashboard/'
LOGIN_URL = '/accounts/login/'

# Redirect après logout
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Sécurité renforcée (désactivée en dev local)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)

# Logging étendu pour auditabilité
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)  # Créer le dossier si nécessaire

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'pro_portal.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'suivi_demande': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Upload constraints (for Demande Étape 4)
# Max size: 20 MB
UPLOAD_MAX_BYTES = 20 * 1024 * 1024
# Allowed extensions
UPLOAD_ALLOWED_EXTS = {"pdf", "jpg", "jpeg", "png", "doc", "docx"}

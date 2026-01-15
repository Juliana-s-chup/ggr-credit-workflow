"""
Module de Sécurité Renforcée
Rate Limiting, Validation, Sanitization
"""
import re
import bleach
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from core.monitoring import log_security_event


# === RATE LIMITING ===

def rate_limit(key_prefix: str, limit: int, period: int):
    """
    Décorateur de rate limiting
    
    Args:
        key_prefix: Préfixe de la clé cache
        limit: Nombre max de requêtes
        period: Période en secondes
    
    Usage:
        @rate_limit('login', limit=5, period=300)  # 5 tentatives / 5min
        def login_view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Identifier l'utilisateur (IP ou user_id)
            if request.user.is_authenticated:
                identifier = f"user_{request.user.id}"
            else:
                identifier = get_client_ip(request)
            
            cache_key = f"rate_limit:{key_prefix}:{identifier}"
            
            # Vérifier le compteur
            count = cache.get(cache_key, 0)
            
            if count >= limit:
                log_security_event(
                    'RATE_LIMIT_EXCEEDED',
                    request.user.id if request.user.is_authenticated else None,
                    get_client_ip(request),
                    {'key_prefix': key_prefix, 'count': count}
                )
                return HttpResponseForbidden(
                    f"Trop de requêtes. Réessayez dans {period} secondes."
                )
            
            # Incrémenter le compteur
            cache.set(cache_key, count + 1, period)
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def get_client_ip(request):
    """Récupère l'IP réelle du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# === SANITIZATION ===

def sanitize_html(text: str) -> str:
    """
    Nettoie le HTML pour éviter XSS
    
    Args:
        text: Texte à nettoyer
    
    Returns:
        Texte nettoyé
    """
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a']
    allowed_attributes = {'a': ['href', 'title']}
    
    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )


def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier
    
    Args:
        filename: Nom du fichier
    
    Returns:
        Nom nettoyé
    """
    # Garder seulement alphanumériques, tirets, underscores et point
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Limiter la longueur
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    name = name[:100]
    
    return f"{name}.{ext}" if ext else name


# === VALIDATION ===

def validate_montant(montant: float) -> tuple[bool, str]:
    """
    Valide un montant de crédit
    
    Args:
        montant: Montant à valider
    
    Returns:
        (is_valid, error_message)
    """
    if montant < 10000:
        return False, "Le montant minimum est de 10 000 FCFA"
    
    if montant > 100000000:  # 100M
        return False, "Le montant maximum est de 100 000 000 FCFA"
    
    return True, ""


def validate_duree(duree_mois: int) -> tuple[bool, str]:
    """
    Valide une durée de crédit
    
    Args:
        duree_mois: Durée en mois
    
    Returns:
        (is_valid, error_message)
    """
    if duree_mois < 1:
        return False, "La durée minimum est de 1 mois"
    
    if duree_mois > 360:  # 30 ans
        return False, "La durée maximum est de 360 mois (30 ans)"
    
    return True, ""


# === PERMISSIONS ===

def require_roles(allowed_roles: list):
    """
    Décorateur pour vérifier les rôles
    
    Usage:
        @require_roles(['GESTIONNAIRE', 'ANALYSTE'])
        def view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentification requise")
            
            user_role = request.user.profile.role
            
            if user_role not in allowed_roles:
                log_security_event(
                    'UNAUTHORIZED_ACCESS',
                    request.user.id,
                    get_client_ip(request),
                    {'required_roles': allowed_roles, 'user_role': user_role}
                )
                return HttpResponseForbidden("Accès non autorisé")
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


# === AUDIT TRAIL ===

class AuditMixin:
    """
    Mixin pour ajouter l'audit trail aux modèles
    
    Usage:
        class MyModel(AuditMixin, models.Model):
            ...
    """
    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        
        if user:
            if not self.pk:  # Création
                self.created_by = user
            self.updated_by = user
        
        super().save(*args, **kwargs)


# === ROLE-BASED ACCESS CONTROL (RBAC) ===

def role_required(*roles):
    """
    Décorateur pour restreindre l'accès selon le rôle utilisateur
    
    Usage:
        @role_required('SUPER_ADMIN', 'RESPONSABLE_GGR')
        def ma_vue(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentification requise")
            
            # Vérifier si l'utilisateur a un profil
            if not hasattr(request.user, 'profile'):
                return HttpResponseForbidden("Profil utilisateur manquant")
            
            # Vérifier si le rôle est autorisé
            user_role = request.user.profile.role
            if user_role not in roles:
                log_security_event(
                    'access_denied',
                    user=request.user,
                    details=f"Rôle {user_role} non autorisé pour {view_func.__name__}"
                )
                return HttpResponseForbidden(
                    f"Accès refusé. Rôle requis: {', '.join(roles)}"
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

"""
Utilitaires pour l'application suivi_demande.
Fonctions de notification, gestion des roles et helpers.
"""

from typing import Iterable, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Notification, DossierCredit, UserRoles

User = get_user_model()


def notify(
    users: Iterable[User],
    *,
    type: str,
    titre: str,
    message: str,
    dossier: Optional[DossierCredit] = None,
    email: bool = False,
) -> int:
    """Create in-app notifications for given users and optionally send emails.
    Returns number of notifications created.
    """
    count = 0
    for u in users:
        Notification.objects.create(
            utilisateur_cible=u,
            type=type,
            titre=titre,
            message=message,
            canal="INTERNE",
        )
        count += 1
        if email and getattr(u, "email", None):
            try:
                send_mail(
                    subject=titre,
                    message=message,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=[u.email],
                    fail_silently=True,
                )
            except Exception:
                # Ignore email failures in MVP
                pass
    return count


def get_current_namespace(request):
    """Determine le namespace actuel base sur la configuration du portail"""
    if hasattr(request, "resolver_match") and request.resolver_match:
        return request.resolver_match.namespace or "pro"
    # Fallback base sur les settings
    portal_type = getattr(settings, "PORTAL_TYPE", "PROFESSIONAL")
    return "client" if portal_type == "CLIENT" else "pro"


# --- Utilitaires de gestion des roles ---


def get_user_role(user) -> Optional[str]:
    """
    Recupere le role d'un utilisateur de maniere robuste.

    Args:
        user: Instance de User Django

    Returns:
        str: Le role de l'utilisateur (CLIENT, GESTIONNAIRE, etc.)
        None: Si l'utilisateur n'a pas de profil
    """
    if not user or not user.is_authenticated:
        return None

    # Essayer profile (OneToOne standard)
    if hasattr(user, "profile"):
        return user.profile.role

    # Essayer userprofile (alternative)
    if hasattr(user, "userprofile"):
        return user.userprofile.role

    return None


def user_has_role(user, role: str) -> bool:
    """Verifie si un utilisateur a un role specifique."""
    user_role = get_user_role(user)
    return user_role == role


def user_has_any_role(user, roles: list) -> bool:
    """Verifie si un utilisateur a l'un des roles specifies."""
    user_role = get_user_role(user)
    return user_role in roles


def is_professional_user(user) -> bool:
    """Verifie si un utilisateur est un professionnel (non-client)."""
    professional_roles = [
        UserRoles.GESTIONNAIRE,
        UserRoles.ANALYSTE,
        UserRoles.RESPONSABLE_GGR,
        UserRoles.BOE,
        UserRoles.SUPER_ADMIN,
    ]
    return user_has_any_role(user, professional_roles)


def is_client_user(user) -> bool:
    """Verifie si un utilisateur est un client."""
    return user_has_role(user, UserRoles.CLIENT)

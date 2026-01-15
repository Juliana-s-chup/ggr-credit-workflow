"""
Utilitaires pour l'application suivi_demande.
Fonctions de notification et helpers.
"""
from typing import Iterable, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Notification, DossierCredit

User = get_user_model()

def notify(users: Iterable[User], *, type: str, titre: str, message: str, dossier: Optional[DossierCredit] = None, email: bool = False) -> int:
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
        if email and getattr(u, 'email', None):
            try:
                send_mail(
                    subject=titre,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    recipient_list=[u.email],
                    fail_silently=True,
                )
            except Exception:
                # Ignore email failures in MVP
                pass
    return count


def get_current_namespace(request):
    """Détermine le namespace actuel basé sur la configuration du portail"""
    if hasattr(request, 'resolver_match') and request.resolver_match:
        return request.resolver_match.namespace or 'pro'
    # Fallback basé sur les settings
    portal_type = getattr(settings, 'PORTAL_TYPE', 'PROFESSIONAL')
    return 'client' if portal_type == 'CLIENT' else 'pro'

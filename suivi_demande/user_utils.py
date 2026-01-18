"""
Utilitaires pour la gestion des utilisateurs.
Centralise la logique de recuperation du role utilisateur.
"""

from typing import Optional
from django.contrib.auth.models import User
from .models import UserRoles


def get_user_role(user: User) -> Optional[str]:
    """
    Recupere le role d'un utilisateur de maniere robuste.

    Args:
        user: Instance de User Django

    Returns:
        str: Le role de l'utilisateur (CLIENT, GESTIONNAIRE, etc.)
        None: Si l'utilisateur n'a pas de profil

    Examples:
        >>> role = get_user_role(request.user)
        >>> if role == UserRoles.GESTIONNAIRE:
        ...     # Logique gestionnaire
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


def user_has_role(user: User, role: str) -> bool:
    """
    Verifie si un utilisateur a un role specifique.

    Args:
        user: Instance de User Django
        role: Role e  verifier (ex: UserRoles.GESTIONNAIRE)

    Returns:
        bool: True si l'utilisateur a ce role

    Examples:
        >>> if user_has_role(request.user, UserRoles.SUPER_ADMIN):
        ...     # Logique admin
    """
    user_role = get_user_role(user)
    return user_role == role


def user_has_any_role(user: User, roles: list) -> bool:
    """
    Verifie si un utilisateur a l'un des roles specifies.

    Args:
        user: Instance de User Django
        roles: Liste de roles acceptes

    Returns:
        bool: True si l'utilisateur a l'un de ces roles

    Examples:
        >>> if user_has_any_role(request.user, [UserRoles.GESTIONNAIRE, UserRoles.ANALYSTE]):
        ...     # Logique professionnelle
    """
    user_role = get_user_role(user)
    return user_role in roles


def is_professional_user(user: User) -> bool:
    """
    Verifie si un utilisateur est un professionnel (non-client).

    Args:
        user: Instance de User Django

    Returns:
        bool: True si professionnel
    """
    professional_roles = [
        UserRoles.GESTIONNAIRE,
        UserRoles.ANALYSTE,
        UserRoles.RESPONSABLE_GGR,
        UserRoles.BOE,
        UserRoles.SUPER_ADMIN,
    ]
    return user_has_any_role(user, professional_roles)


def is_client_user(user: User) -> bool:
    """
    Verifie si un utilisateur est un client.

    Args:
        user: Instance de User Django

    Returns:
        bool: True si client
    """
    return user_has_role(user, UserRoles.CLIENT)

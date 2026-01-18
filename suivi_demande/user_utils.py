"""
Utilitaires pour la gestion des utilisateurs.
Centralise la logique de récupération du rôle utilisateur.
"""

from typing import Optional
from django.contrib.auth.models import User
from .models import UserRoles


def get_user_role(user: User) -> Optional[str]:
    """
    Récupère le rôle d'un utilisateur de manière robuste.

    Args:
        user: Instance de User Django

    Returns:
        str: Le rôle de l'utilisateur (CLIENT, GESTIONNAIRE, etc.)
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
    Vérifie si un utilisateur a un rôle spécifique.

    Args:
        user: Instance de User Django
        role: Rôle à vérifier (ex: UserRoles.GESTIONNAIRE)

    Returns:
        bool: True si l'utilisateur a ce rôle

    Examples:
        >>> if user_has_role(request.user, UserRoles.SUPER_ADMIN):
        ...     # Logique admin
    """
    user_role = get_user_role(user)
    return user_role == role


def user_has_any_role(user: User, roles: list) -> bool:
    """
    Vérifie si un utilisateur a l'un des rôles spécifiés.

    Args:
        user: Instance de User Django
        roles: Liste de rôles acceptés

    Returns:
        bool: True si l'utilisateur a l'un de ces rôles

    Examples:
        >>> if user_has_any_role(request.user, [UserRoles.GESTIONNAIRE, UserRoles.ANALYSTE]):
        ...     # Logique professionnelle
    """
    user_role = get_user_role(user)
    return user_role in roles


def is_professional_user(user: User) -> bool:
    """
    Vérifie si un utilisateur est un professionnel (non-client).

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
    Vérifie si un utilisateur est un client.

    Args:
        user: Instance de User Django

    Returns:
        bool: True si client
    """
    return user_has_role(user, UserRoles.CLIENT)

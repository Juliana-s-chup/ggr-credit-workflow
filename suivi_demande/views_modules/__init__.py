"""
Views modulaires pour l'application suivi_demande.
Structure professionnelle avec séparation des responsabilités.

Ce module centralise tous les imports pour compatibilité avec urls.py.
"""

# Vues de base
from .base import (
    home,
    signup,
    pending_approval,
)

# Vues de gestion des dossiers
from .dossiers import (
    my_applications,
    create_application,
    edit_application,
    delete_application,
    test_dossiers_list,
)

# Vues de notifications
from .notifications import (
    notifications_list,
    notifications_mark_all_read,
    notifications_mark_read,
)

# Vues AJAX
from .ajax import (
    test_notification_api,
)

# Vues dashboard
from .dashboard import (
    dashboard,
    dossier_detail,
)

# Vues workflow
from .workflow import (
    transition_dossier,
    transmettre_analyste_page,
)

# Note : Les autres modules (wizard, etc.)
# seront ajoutés progressivement pour éviter les erreurs.
# Pour l'instant, on importe depuis l'ancien views.py

__all__ = [
    # Base
    "home",
    "signup",
    "pending_approval",
    # Dossiers
    "my_applications",
    "create_application",
    "edit_application",
    "delete_application",
    "test_dossiers_list",
    # Notifications
    "notifications_list",
    "notifications_mark_all_read",
    "notifications_mark_read",
    # AJAX
    "test_notification_api",
    # Dashboard
    "dashboard",
    "dossier_detail",
    # Workflow
    "transition_dossier",
    "transmettre_analyste_page",
]

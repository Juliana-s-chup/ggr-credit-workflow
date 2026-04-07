"""
Package views pour l'application suivi_demande.

Organisation modulaire :
- auth.py          : Inscription, approbation
- dashboard.py     : Dashboard principal (par role)
- dossier.py       : Detail, liste, creation de dossiers
- workflow.py      : Transitions d'etat du workflow
- wizard.py        : Wizard de demande de credit (4 etapes)
- notifications.py : Gestion des notifications
- admin.py         : Administration des utilisateurs
- helpers.py       : Fonctions utilitaires partagees
"""

# Auth
from .auth import signup, pending_approval

# Dashboard
from .dashboard import dashboard

# Dossiers
from .dossier import (
    dossier_detail,
    my_applications,
    create_application,
    test_dossiers_list,
)

# Workflow
from .workflow import transition_dossier, transmettre_analyste_page

# Wizard (demande de credit)
from .wizard import (
    demande_start,
    demande_verification,
    demande_step1,
    demande_step2,
    demande_step3,
    demande_step4,
)

# Notifications
from .notifications import (
    notifications_list,
    notifications_mark_all_read,
    notifications_mark_read,
)

# Administration
from .admin import admin_users, admin_change_role, admin_activate_user

__all__ = [
    # Auth
    "signup",
    "pending_approval",
    # Dashboard
    "dashboard",
    # Dossiers
    "dossier_detail",
    "my_applications",
    "create_application",
    "test_dossiers_list",
    # Workflow
    "transition_dossier",
    "transmettre_analyste_page",
    # Wizard
    "demande_start",
    "demande_verification",
    "demande_step1",
    "demande_step2",
    "demande_step3",
    "demande_step4",
    # Notifications
    "notifications_list",
    "notifications_mark_all_read",
    "notifications_mark_read",
    # Admin
    "admin_users",
    "admin_change_role",
    "admin_activate_user",
]

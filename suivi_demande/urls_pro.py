"""
URLs pour le Portail PROFESSIONNEL
Toutes les fonctionnalites de gestion et administration
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import (
    views,
    views_canevas,
    views_documents,
    views_portals,
    views_admin,
    views_autorisation,
)

app_name = "pro"

urlpatterns = [
    # Page de connexion professionnelle
    path("login/", views_portals.login_pro_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
    # Dashboard professionnel (par role)
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="home"),  # Redirection racine
    # Gestion des dossiers (toutes les fonctions)
    path("dossiers/", views_portals.all_dossiers_view, name="all_dossiers"),
    path("dossier/<int:pk>/", views.dossier_detail, name="dossier_detail"),
    # Creation de dossier (gestionnaire)
    path("nouveau-dossier/", views.create_application, name="create_dossier"),
    path(
        "dossier/<int:pk>/transmettre-analyste/",
        views.transmettre_analyste_page,
        name="transmettre_analyste_page",
    ),
    path(
        "autorisation-ponctuelle/",
        views_autorisation.autorisation_ponctuelle,
        name="autorisation_ponctuelle",
    ),
    # Workflow et transitions
    path(
        "dossier/<int:pk>/<str:action>/transition/",
        views.transition_dossier,
        name="transition_dossier",
    ),
    # Gestion des utilisateurs (admin/gestionnaire)
    path(
        "utilisateur/<int:user_id>/toggle-status/",
        views_admin.admin_toggle_user_status,
        name="admin_toggle_status",
    ),
    path(
        "utilisateur/<int:user_id>/change-role/",
        views_admin.admin_change_user_role,
        name="admin_change_role",
    ),
    path(
        "utilisateur/<int:user_id>/modifier/",
        views_admin.admin_edit_user,
        name="admin_edit_user",
    ),
    path("utilisateur/creer/", views_admin.admin_create_user, name="admin_create_user"),
    # Demandes de credit (wizard - 4 etapes pour gestionnaire)
    path("demande/", views.demande_start, name="demande_start"),
    path(
        "demande/verification/", views.demande_verification, name="demande_verification"
    ),
    path("demande/etape1/", views.demande_step1, name="demande_step1"),
    path("demande/etape2/", views.demande_step2, name="demande_step2"),
    path("demande/etape3/", views.demande_step3, name="demande_step3"),
    path("demande/etape4/", views.demande_step4, name="demande_step4"),
    # Creation de dossier gestionnaire (alias)
    path(
        "gestionnaire/nouveau-dossier/",
        views.create_application,
        name="gestionnaire_create_dossier",
    ),
    # Rapports et analytics
    path("rapports/", views_portals.reports_redirect, name="reports"),
    # Notifications
    path("notifications/", views.notifications_list, name="notifications"),
    path("notifications/marquer-tout-lu/", views.notifications_mark_all_read, name="notifications_mark_all"),
    path("notifications/<int:pk>/marquer-lu/", views.notifications_mark_read, name="notifications_mark_read"),
]

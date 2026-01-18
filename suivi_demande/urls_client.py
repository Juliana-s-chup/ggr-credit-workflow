"""
URLs pour le Portail CLIENT
Fonctionnalites limitees aux besoins client
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_portals

app_name = "client"

urlpatterns = [
    # Page de connexion client
    path("login/", views_portals.login_client_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
    # Dashboard client
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="home"),  # Redirection racine
    # Mes dossiers (consultation uniquement)
    path("mes-dossiers/", views.my_applications, name="my_applications"),
    path("dossier/<int:pk>/", views.dossier_detail, name="dossier_detail"),
    # Nouvelle demande (wizard client)
    path("nouvelle-demande/", views.demande_start, name="demande_start"),
    path(
        "demande/verification/", views.demande_verification, name="demande_verification"
    ),
    path("demande/etape1/", views.demande_step1, name="demande_step1"),
    path("demande/etape2/", views.demande_step2, name="demande_step2"),
    path("demande/etape3/", views.demande_step3, name="demande_step3"),
    path("demande/etape4/", views.demande_step4, name="demande_step4"),
    # Documents (telechargement uniquement, pas d'upload direct)
    path(
        "dossier/<int:dossier_id>/documents/",
        views_portals.view_documents,
        name="view_documents",
    ),
    # Notifications
    path("notifications/", views.notifications_list, name="notifications_list"),
    path(
        "notifications/marquer-tout-lu/",
        views.notifications_mark_all_read,
        name="notifications_mark_all",
    ),
    path(
        "notifications/<int:pk>/marquer-lu/",
        views.notifications_mark_read,
        name="notifications_mark_read",
    ),
]

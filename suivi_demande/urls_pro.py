"""
URLs pour le Portail PROFESSIONNEL
Toutes les fonctionnalités de gestion et administration
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, views_canevas, views_documents, views_portals, views_admin, views_autorisation

# from .pdf_views import dossier_proposition_pdf  # TODO: Vue manquante

app_name = "pro"

urlpatterns = [
    # Page de connexion professionnelle
    path("login/", views_portals.login_pro_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
    # Dashboard professionnel (par rôle)
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="home"),  # Redirection racine
    # Gestion des dossiers (toutes les fonctions)
    path("dossiers/", views_portals.all_dossiers_list, name="all_dossiers"),
    path("dossier/<int:pk>/", views.dossier_detail, name="dossier_detail"),
    # Création de dossier (gestionnaire)
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
    # path('dossier/<int:pk>/archiver/', views.archive_dossier, name='archive_dossier'),  # TODO: Vue manquante
    # path('dossier/<int:pk>/desarchiver/', views.unarchive_dossier, name='unarchive_dossier'),  # TODO: Vue manquante
    # Canevas de proposition (NOKI NOKI)
    # path('dossier/<int:dossier_id>/canevas/', views_canevas.canevas_create_or_edit, name='canevas_form'),  # TODO: Vue manquante
    # path('dossier/<int:dossier_id>/canevas/pdf/', views_canevas.canevas_view_pdf, name='canevas_pdf'),  # TODO: Vue manquante
    # Gestion des documents
    # path('dossier/<int:dossier_id>/documents/', views_documents.upload_documents, name='upload_documents'),  # TODO: Vue manquante
    # path('dossier/<int:dossier_id>/documents/upload/', views_documents.upload_document_ajax, name='upload_document_ajax'),  # TODO: Vue manquante
    # path('dossier/<int:dossier_id>/documents/<int:piece_id>/delete/', views_documents.delete_document_ajax, name='delete_document_ajax'),  # TODO: Vue manquante
    # PDF et exports
    # path('dossier/<int:pk>/proposition.pdf', dossier_proposition_pdf, name='dossier_proposition_pdf'),  # TODO: Vue manquante
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
        "utilisateur/<int:user_id>/modifier/", views_admin.admin_edit_user, name="admin_edit_user"
    ),
    path("utilisateur/creer/", views_admin.admin_create_user, name="admin_create_user"),
    # Notifications
    # path('notifications/', views.notifications_list, name='notifications_list'),  # TODO: Vue manquante
    # path('notifications/marquer-tout-lu/', views.notifications_mark_all_read, name='notifications_mark_all'),  # TODO: Vue manquante
    # path('notifications/<int:pk>/marquer-lu/', views.notifications_mark_read, name='notifications_mark_read'),  # TODO: Vue manquante
    # Demandes de crédit (wizard - 4 étapes pour gestionnaire)
    path("demande/", views.demande_start, name="demande_start"),
    path("demande/verification/", views.demande_verification, name="demande_verification"),
    path("demande/etape1/", views.demande_step1, name="demande_step1"),
    path("demande/etape2/", views.demande_step2, name="demande_step2"),
    path("demande/etape3/", views.demande_step3, name="demande_step3"),
    path("demande/etape4/", views.demande_step4, name="demande_step4"),
    # Création de dossier gestionnaire (alias)
    path(
        "gestionnaire/nouveau-dossier/",
        views.create_application,
        name="gestionnaire_create_dossier",
    ),
]

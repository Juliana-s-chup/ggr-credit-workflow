from django.urls import path
from django.views.generic import RedirectView
from . import views
from .pdf_views import dossier_proposition_pdf
from . import views_canevas
from . import views_autorisation
from . import views_documents

app_name = "suivi"

urlpatterns = [
    # Suppression de la page d'accueil: redirection vers la page de connexion
    path(
        "",
        RedirectView.as_view(url="/accounts/login/", permanent=False),
        name="root_redirect",
    ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("mes-dossiers/", views.my_applications, name="my_applications"),
    path("nouveau-dossier/", views.create_application, name="create_application"),
    path("dashboard/dossier/<int:pk>/", views.dossier_detail, name="dossier_detail"),
    path(
        "dossier/<int:pk>/proposition.pdf",
        dossier_proposition_pdf,
        name="dossier_proposition_pdf",
    ),
    path(
        "dossier/<int:pk>/<str:action>/transition/",
        views.transition_dossier,
        name="transition_dossier",
    ),
    path(
        "dossier/<int:pk>/transmettre-analyste/",
        views.transmettre_analyste_page,
        name="transmettre_analyste_page",
    ),
    # path("dossier/<int:pk>/archiver/", views.archive_dossier, name="archive_dossier"),  # TODO: Vue e  implementer
    # path("dossier/<int:pk>/desarchiver/", views.unarchive_dossier, name="unarchive_dossier"),  # TODO: Vue e  implementer
    # Canevas de proposition
    path(
        "dossier/<int:dossier_id>/canevas/",
        views_canevas.canevas_create_or_edit,
        name="canevas_form",
    ),
    path(
        "dossier/<int:dossier_id>/canevas/pdf/",
        views_canevas.canevas_view_pdf,
        name="canevas_pdf",
    ),
    # Upload documents
    path(
        "dossier/<int:dossier_id>/documents/",
        views_documents.upload_documents,
        name="upload_documents",
    ),
    path(
        "dossier/<int:dossier_id>/documents/upload/",
        views_documents.upload_document_ajax,
        name="upload_document_ajax",
    ),
    path(
        "dossier/<int:dossier_id>/documents/<int:piece_id>/delete/",
        views_documents.delete_document_ajax,
        name="delete_document_ajax",
    ),
    # Demande de credit (wizard)
    path("demande/", views.demande_start, name="demande_start"),
    path(
        "demande/verification/", views.demande_verification, name="demande_verification"
    ),
    path("demande/etape-1/", views.demande_step1, name="demande_step1"),
    path("demande/etape-2/", views.demande_step2, name="demande_step2"),
    path("demande/etape-3/", views.demande_step3, name="demande_step3"),
    path("demande/etape-4/", views.demande_step4, name="demande_step4"),
    # Autorisation Ponctuelle (segment particuliers)
    path(
        "autorisation-ponctuelle/",
        views_autorisation.autorisation_ponctuelle,
        name="autorisation_ponctuelle",
    ),
    # Auth flows Option A
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/pending/", views.pending_approval, name="pending_approval"),
    # Pages de connexion distinctes - TODO: Utiliser views_portals e  la place
    # path("accounts/login_client/", views.login_client, name="login_client"),
    # path("accounts/login_pro/", views.login_pro, name="login_pro"),
    # Pages d'inscription distinctes
    # path("accounts/signup_client/", views.signup_client, name="signup_client"),
    # Notifications
    path("notifications/", views.notifications_list, name="notifications_list"),
    path(
        "notifications/mark-all/",
        views.notifications_mark_all_read,
        name="notifications_mark_all",
    ),
    path(
        "notifications/<int:pk>/mark/",
        views.notifications_mark_read,
        name="notifications_mark_one",
    ),
    # Administration (eviter collision avec Django admin)
    path("suivi-admin/users/", views.admin_users, name="admin_users"),
    # path("suivi-admin/users/create/", views.admin_create_user, name="admin_create_user"),  # TODO: Vue e  implementer
    path(
        "suivi-admin/users/change-role/",
        views.admin_change_role,
        name="admin_change_role",
    ),
    path(
        "suivi-admin/users/<int:user_id>/activate/",
        views.admin_activate_user,
        name="admin_activate_user",
    ),
    # Rapports - TODO: Utiliser views_portals e  la place
    # path("rapports/", views.reports_view, name="reports"),
    # path("rapports/export-xlsx/", views.reports_export_xlsx, name="reports_export_xlsx"),
]

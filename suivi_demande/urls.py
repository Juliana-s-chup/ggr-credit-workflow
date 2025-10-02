from django.urls import path
from . import views
from .pdf_views import dossier_proposition_pdf

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("mes-dossiers/", views.my_applications, name="my_applications"),
    path("nouveau-dossier/", views.create_application, name="create_application"),
    path("dossier/<int:pk>/modifier/", views.edit_application, name="edit_application"),
    path("dossier/<int:pk>/supprimer/", views.delete_application, name="delete_application"),
    path("dashboard/dossier/<int:pk>/", views.dossier_detail, name="dossier_detail"),
    path("dossier/<int:pk>/proposition.pdf", dossier_proposition_pdf, name="dossier_proposition_pdf"),
    path("dossier/<int:pk>/<str:action>/transition/", views.transition_dossier, name="transition_dossier"),
    # Demande de crédit (wizard)
    path("demande/", views.demande_start, name="demande_start"),
    path("demande/verification/", views.demande_verification, name="demande_verification"),
    path("demande/etape-1/", views.demande_step1, name="demande_step1"),
    path("demande/etape-2/", views.demande_step2, name="demande_step2"),
    path("demande/etape-3/", views.demande_step3, name="demande_step3"),
    path("demande/etape-4/", views.demande_step4, name="demande_step4"),
    # Auth flows Option A
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/pending/", views.pending_approval, name="pending_approval"),
    # Notifications
    path("notifications/", views.notifications_list, name="notifications_list"),
    path("notifications/mark-all/", views.notifications_mark_all_read, name="notifications_mark_all"),
    path("notifications/<int:pk>/mark/", views.notifications_mark_read, name="notifications_mark_one"),
    # Administration
    path("admin/users/", views.admin_users, name="admin_users"),
    path("admin/users/change-role/", views.admin_change_role, name="admin_change_role"),
    path("admin/users/<int:user_id>/activate/", views.admin_activate_user, name="admin_activate_user"),
    # Test des notifications
    path("test-notifications/", views.test_notification_view, name="test_notifications"),
    path("test-notifications-api/", views.test_notification_api, name="test_notifications_api"),
    path("test-retour-simple/", views.test_retour_simple, name="test_retour_simple"),
    path("debug-direct/", views.debug_direct, name="debug_direct"),
    path("force-retour/<int:pk>/", views.force_retour_client, name="force_retour_client"),
]
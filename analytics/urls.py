"""
Module Analytics - URLs
"""

from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    # Dashboards
    path("dashboard/", views.dashboard_analytics, name="dashboard_analytics"),
    path("rapport/", views.rapport_statistiques, name="rapport_statistiques"),
    path("predictions/", views.predictions_risque, name="predictions_risque"),
    # Actions
    path("predire/<int:dossier_id>/", views.predire_dossier, name="predire_dossier"),
    path("export/excel/", views.exporter_excel, name="exporter_excel"),
    # API
    path("api/graphiques/", views.api_graphiques_data, name="api_graphiques"),
    path("api/kpis/", views.api_kpis, name="api_kpis"),
]

"""
Module Analytics - Vues pour dashboards et rapports
Auteur: NGUIMBI Juliana
Date: Novembre 2025
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.utils import timezone
import json

from .services import AnalyticsService, MLPredictionService, ExportService
from .models import StatistiquesDossier, PredictionRisque
from suivi_demande.models import DossierCredit
from core.security import role_required


@login_required
@role_required("SUPER_ADMIN", "RESPONSABLE_GGR", "ANALYSTE")
def dashboard_analytics(request):
    """
    Dashboard principal d'analytics avec KPIs et graphiques
    """
    # KPIs
    kpis = AnalyticsService.obtenir_kpis_dashboard()

    # Donnees pour graphiques
    graphiques = AnalyticsService.obtenir_donnees_graphiques()

    # Statistiques recentes
    stats_recentes = StatistiquesDossier.objects.all()[:5]

    context = {
        "kpis": kpis,
        "graphiques": json.dumps(graphiques),  # Serialiser en JSON
        "stats_recentes": stats_recentes,
        "page_title": "Analytics & Reporting",
    }

    return render(request, "analytics/dashboard.html", context)


@login_required
@role_required("SUPER_ADMIN", "RESPONSABLE_GGR")
def rapport_statistiques(request):
    """
    Page de rapport statistiques detaillees
    """
    periode = request.GET.get("periode", "MOIS")

    # Calculer les statistiques
    stats = AnalyticsService.calculer_statistiques_periode(periode)

    # Historique des statistiques
    historique = StatistiquesDossier.objects.filter(periode=periode)[:12]

    context = {
        "stats": stats,
        "historique": historique,
        "periode": periode,
        "page_title": "Rapport Statistiques",
    }

    return render(request, "analytics/rapport_statistiques.html", context)


@login_required
@role_required("ANALYSTE", "RESPONSABLE_GGR")
def predictions_risque(request):
    """
    Page des predictions de risque ML
    """
    # Recuperer les predictions recentes
    predictions = PredictionRisque.objects.select_related("dossier").all()[:20]

    # Statistiques des predictions
    total_predictions = predictions.count()
    risque_faible = predictions.filter(classe_risque="FAIBLE").count()
    risque_moyen = predictions.filter(classe_risque="MOYEN").count()
    risque_eleve = predictions.filter(classe_risque="ELEVE").count()

    context = {
        "predictions": predictions,
        "stats": {
            "total": total_predictions,
            "faible": risque_faible,
            "moyen": risque_moyen,
            "eleve": risque_eleve,
        },
        "page_title": "Predictions de Risque",
    }

    return render(request, "analytics/predictions_risque.html", context)


@login_required
@role_required("ANALYSTE", "RESPONSABLE_GGR")
def predire_dossier(request, dossier_id):
    """
    Genere une prediction de risque pour un dossier specifique
    """
    try:
        dossier = DossierCredit.objects.get(id=dossier_id)
        prediction = MLPredictionService.predire_risque(dossier)

        if prediction:
            messages.success(
                request, f"Prediction generee : Risque {prediction.classe_risque}"
            )
        else:
            messages.warning(
                request, "Pas assez de donnees pour generer une prediction."
            )

    except DossierCredit.DoesNotExist:
        messages.error(request, "Dossier introuvable.")

    return redirect("analytics:predictions_risque")


@login_required
@role_required("SUPER_ADMIN", "RESPONSABLE_GGR")
def exporter_excel(request):
    """
    Exporte les statistiques en Excel
    """
    try:
        filepath = ExportService.exporter_statistiques_excel()

        # Retourner le fichier
        response = FileResponse(
            open(filepath, "rb"),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{filepath.split("/")[-1]}"'
        )

        messages.success(request, "Export Excel genere avec succes.")
        return response

    except Exception as e:
        messages.error(request, f"Erreur lors de l'export : {str(e)}")
        return redirect("analytics:dashboard_analytics")


@login_required
def api_graphiques_data(request):
    """
    API JSON pour les donnees de graphiques (Charts.js)
    """
    graphiques = AnalyticsService.obtenir_donnees_graphiques()
    return JsonResponse(graphiques)


@login_required
def api_kpis(request):
    """
    API JSON pour les KPIs en temps reel
    """
    kpis = AnalyticsService.obtenir_kpis_dashboard()
    return JsonResponse(kpis)

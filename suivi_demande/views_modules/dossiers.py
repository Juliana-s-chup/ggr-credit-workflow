"""
Vues de gestion des dossiers (CRUD).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render

from ..constants import ITEMS_PER_PAGE
from ..models import DossierCredit


@login_required
def my_applications(request):
    """Afficher les dossiers du client avec pagination."""
    dossiers_list = (
        DossierCredit.objects.filter(client=request.user)
        .select_related("acteur_courant")
        .order_by("-date_soumission")
    )

    paginator = Paginator(dossiers_list, ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    dossiers = paginator.get_page(page_number)

    return render(request, "suivi_demande/my_applications.html", {"dossiers": dossiers})


@login_required
def create_application(request):
    """Creer une nouvelle demande."""
    return render(request, "suivi_demande/nouveau_dossier.html")


@login_required
def test_dossiers_list(request):
    """Vue de test pour afficher tous les dossiers."""
    all_dossiers = DossierCredit.objects.all().order_by("-date_soumission")
    total_dossiers = all_dossiers.count()

    statuts_stats = (
        DossierCredit.objects.values("statut_agent").annotate(count=Count("id")).order_by("-count")
    )

    context = {
        "all_dossiers": all_dossiers,
        "total_dossiers": total_dossiers,
        "statuts_stats": statuts_stats,
    }
    return render(request, "suivi_demande/test_dossiers.html", context)

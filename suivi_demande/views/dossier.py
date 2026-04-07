"""
Vues de gestion des dossiers : detail, liste, creation.
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from ..constants import ITEMS_PER_PAGE
from ..models import (
    DossierCredit,
    UserRoles,
    Notification,
    PieceJointe,
    Commentaire,
    JournalAction,
)
from ..permissions import can_upload_piece, get_transition_flags
from ..utils import get_current_namespace

logger = logging.getLogger("suivi_demande")


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
    """Page de creation d'un nouveau dossier."""
    return render(request, "suivi_demande/nouveau_dossier.html")


@login_required
def dossier_detail(request, pk):
    """Detail d'un dossier avec commentaires, pieces jointes et actions."""
    dossier = get_object_or_404(DossierCredit, pk=pk)
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)

    # Acces: le client ne peut voir que ses propres dossiers
    if role == UserRoles.CLIENT and dossier.client_id != request.user.id:
        messages.error(request, "Acces refuse au dossier demande.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    # Marquer les notifications liees au dossier comme lues
    try:
        Notification.objects.filter(
            utilisateur_cible=request.user,
            lu=False,
        ).filter(
            Q(dossier=dossier)
            | Q(titre__icontains=dossier.reference)
            | Q(message__icontains=dossier.reference)
        ).update(lu=True)
    except Exception:
        pass

    # Permissions centralisees
    can_upload = can_upload_piece(dossier, request.user)
    flags = get_transition_flags(dossier, request.user)

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        if action == "add_comment":
            return _handle_add_comment(request, dossier)
        elif action == "upload_piece":
            return _handle_upload_piece(request, dossier, can_upload)

    pieces = PieceJointe.objects.filter(dossier=dossier).order_by("-upload_at")
    commentaires = Commentaire.objects.filter(dossier=dossier).order_by("-created_at")
    journal = JournalAction.objects.filter(dossier=dossier).order_by("-timestamp")

    ctx = {
        "dossier": dossier,
        "pieces": pieces,
        "commentaires": commentaires,
        "journal": journal,
        "role": role,
        "can_upload": can_upload,
        "can_tx_transmettre_analyste": flags["can_tx_transmettre_analyste"],
        "can_tx_transmettre_ggr": flags["can_tx_transmettre_ggr"],
        "can_tx_retour_gestionnaire": flags["can_tx_retour_gestionnaire"],
        "can_tx_approuver": flags["can_tx_approuver"],
        "can_tx_refuser": flags["can_tx_refuser"],
        "can_tx_liberer_fonds": flags["can_tx_liberer_fonds"],
    }
    return render(request, "suivi_demande/dossier_detail.html", ctx)


# ---------------------------------------------------------------------------
# Helpers pour dossier_detail
# ---------------------------------------------------------------------------


def _handle_add_comment(request, dossier):
    """Traite l'ajout d'un commentaire sur un dossier."""
    msg = (request.POST.get("message") or "").strip()
    if msg:
        Commentaire.objects.create(
            dossier=dossier,
            auteur=request.user,
            message=msg,
            cible_role=None,
        )
        messages.success(request, "Commentaire ajoute.")
    namespace = get_current_namespace(request)
    return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)


def _handle_upload_piece(request, dossier, can_upload):
    """Traite l'upload d'une piece jointe sur un dossier."""
    namespace = get_current_namespace(request)

    if not can_upload:
        messages.error(request, "Vous ne pouvez pas deposer de piece a ce stade.")
        return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

    f = request.FILES.get("fichier")
    type_piece = request.POST.get("type_piece") or "AUTRE"

    if not f:
        messages.error(request, "Aucun fichier selectionne.")
        return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

    # Validation taille
    max_bytes = getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024)
    file_size = getattr(f, "size", 0) or 0
    if file_size > max_bytes:
        max_mb = round(max_bytes / (1024 * 1024), 2)
        messages.error(request, f"Fichier trop volumineux. Taille maximale: {max_mb} Mo.")
        return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

    # Validation extension
    filename = getattr(f, "name", "")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    allowed_exts = getattr(settings, "UPLOAD_ALLOWED_EXTS", {"pdf", "jpg", "jpeg", "png"})
    if ext not in allowed_exts:
        messages.error(
            request,
            f"Extension non autorisee ({ext}). Autorisees: {', '.join(sorted(allowed_exts))}.",
        )
        return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

    PieceJointe.objects.create(
        dossier=dossier,
        fichier=f,
        type_piece=type_piece,
        taille=file_size,
        upload_by=request.user,
    )
    messages.success(request, "Piece jointe telechargee.")
    return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)


@login_required
def test_dossiers_list(request):
    """Vue de test pour afficher TOUS les dossiers en base avec pagination."""
    from django.db.models import Count

    dossiers_list = DossierCredit.objects.select_related(
        "client", "acteur_courant"
    ).order_by("-date_soumission")
    total_dossiers = dossiers_list.count()

    statuts_stats = (
        DossierCredit.objects.values("statut_agent")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    paginator = Paginator(dossiers_list, ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    all_dossiers = paginator.get_page(page_number)

    context = {
        "all_dossiers": all_dossiers,
        "total_dossiers": total_dossiers,
        "statuts_stats": statuts_stats,
    }
    return render(request, "suivi_demande/test_dossiers.html", context)

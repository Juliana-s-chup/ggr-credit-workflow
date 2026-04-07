"""
Vues de gestion des notifications utilisateur.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Notification
from ..utils import get_current_namespace

logger = logging.getLogger("suivi_demande")


@login_required
def notifications_list(request):
    """Liste des notifications de l'utilisateur connecte."""
    qs = Notification.objects.filter(utilisateur_cible=request.user).order_by(
        "-created_at"
    )
    return render(request, "suivi_demande/notifications.html", {"notifications": qs})


@login_required
def notifications_mark_all_read(request):
    """Marquer toutes les notifications comme lues."""
    if request.method == "POST":
        Notification.objects.filter(utilisateur_cible=request.user, lu=False).update(
            lu=True
        )
        messages.success(request, "Toutes vos notifications ont ete marquees comme lues.")
    namespace = get_current_namespace(request)
    return redirect(f"{namespace}:notifications")


@login_required
def notifications_mark_read(request, pk: int):
    """Marquer une notification specifique comme lue."""
    if request.method == "POST":
        notif = get_object_or_404(Notification, pk=pk, utilisateur_cible=request.user)
        if not notif.lu:
            notif.lu = True
            notif.save(update_fields=["lu"])
        namespace = get_current_namespace(request)
        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect(f"{namespace}:notifications")
    namespace = get_current_namespace(request)
    return redirect(f"{namespace}:notifications")

"""
Vues de gestion des notifications.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from ..constants import NOTIFICATIONS_PER_PAGE
from ..models import Notification
from ..utils import get_current_namespace


@login_required
def notifications_list(request):
    """Afficher la liste des notifications de l'utilisateur avec pagination."""
    notifications_list = Notification.objects.filter(
        utilisateur_cible=request.user
    ).order_by("-created_at")
    
    paginator = Paginator(notifications_list, NOTIFICATIONS_PER_PAGE)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    return render(request, "suivi_demande/notifications.html", {
        "notifications": notifications
    })


@login_required
def notifications_mark_all_read(request):
    """Marquer toutes les notifications comme lues."""
    if request.method == "POST":
        count = Notification.objects.filter(
            utilisateur_cible=request.user, 
            lu=False
        ).update(lu=True)
        
        if count > 0:
            messages.success(request, f"{count} notification(s) marquée(s) comme lue(s).")
        else:
            messages.info(request, "Aucune notification non lue.")
    
    namespace = get_current_namespace(request)
    return redirect(f"{namespace}:notifications_list")


@login_required
def notifications_mark_read(request, pk: int):
    """Marquer une notification spécifique comme lue."""
    if request.method == "POST":
        notif = get_object_or_404(Notification, pk=pk, utilisateur_cible=request.user)
        if not notif.lu:
            notif.lu = True
            notif.save(update_fields=["lu"])
            messages.success(request, "Notification marquée comme lue.")
        
        # Rediriger vers la page précédente si fournie
        namespace = get_current_namespace(request)
        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect(f"{namespace}:notifications_list")
    
    return redirect("suivi:notifications_list")

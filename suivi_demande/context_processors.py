"""
Context processors pour ajouter des variables globales aux templates.
"""
from .models import Notification


def notifications(request):
    """Expose unread notifications count and latest items for authenticated users."""
    if not request.user.is_authenticated:
        return {"unread_notifications_count": 0, "latest_notifications": []}
    qs = Notification.objects.filter(utilisateur_cible=request.user).order_by("-created_at")
    count = qs.filter(lu=False).count()
    latest = list(qs[:5])
    return {
        "unread_notifications_count": count,
        "latest_notifications": latest,
    }

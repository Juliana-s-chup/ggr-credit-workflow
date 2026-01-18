"""
Vues AJAX et API JSON.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from ..models import Notification


def test_notification_api(request):
    """API pour tester les notifications en AJAX."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Non authentifie"}, status=401)

    # Recuperer les notifications recentes
    notifications = Notification.objects.filter(utilisateur_cible=request.user).order_by(
        "-created_at"
    )[:5]

    data = {
        "notifications": [
            {
                "id": n.id,
                "titre": n.titre,
                "message": n.message,
                "lu": n.lu,
                "created_at": n.created_at.strftime("%d/%m/%Y %H:%M"),
                "type": n.type,
            }
            for n in notifications
        ],
        "count": notifications.count(),
        "unread_count": Notification.objects.filter(
            utilisateur_cible=request.user, lu=False
        ).count(),
    }

    return JsonResponse(data)

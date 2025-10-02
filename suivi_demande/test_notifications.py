"""
Vue de test pour diagnostiquer les notifications
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from suivi_demande.models import Notification, DossierCredit
from django.http import JsonResponse

User = get_user_model()

@login_required
def test_notification_view(request):
    """Vue pour tester les notifications"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_test_notification':
            try:
                # Créer une notification de test
                notification = Notification.objects.create(
                    utilisateur_cible=request.user,
                    type="TEST",
                    titre="Test de notification",
                    message="Ceci est une notification de test créée manuellement.",
                    canal="INTERNE"
                )
                messages.success(request, f"✅ Notification de test créée (ID: {notification.id})")
            except Exception as e:
                messages.error(request, f"❌ Erreur: {e}")
        
        elif action == 'list_notifications':
            # Lister les notifications de l'utilisateur
            notifications = Notification.objects.filter(
                utilisateur_cible=request.user
            ).order_by('-created_at')[:10]
            
            context = {
                'notifications': notifications,
                'count': notifications.count()
            }
            return render(request, 'core/test_notifications.html', context)
    
    # Statistiques
    total_notifications = Notification.objects.filter(utilisateur_cible=request.user).count()
    unread_notifications = Notification.objects.filter(utilisateur_cible=request.user, lu=False).count()
    
    # Derniers dossiers de l'utilisateur (si client)
    dossiers = []
    if hasattr(request.user, 'profile') and request.user.profile.role == 'CLIENT':
        dossiers = DossierCredit.objects.filter(client=request.user).order_by('-date_soumission')[:5]
    
    context = {
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'dossiers': dossiers,
    }
    
    return render(request, 'core/test_notifications.html', context)


def test_notification_api(request):
    """API pour tester les notifications en AJAX"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    # Récupérer les notifications récentes
    notifications = Notification.objects.filter(
        utilisateur_cible=request.user
    ).order_by('-created_at')[:5]
    
    data = {
        'notifications': [
            {
                'id': n.id,
                'titre': n.titre,
                'message': n.message,
                'lu': n.lu,
                'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
                'type': n.type
            }
            for n in notifications
        ],
        'count': notifications.count(),
        'unread_count': Notification.objects.filter(utilisateur_cible=request.user, lu=False).count()
    }
    
    return JsonResponse(data)

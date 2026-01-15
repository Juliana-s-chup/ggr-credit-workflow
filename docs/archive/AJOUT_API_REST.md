# 🚀 AJOUT API REST AVEC DJANGO REST FRAMEWORK

## Installation (5 min)

```bash
pip install djangorestframework
pip install django-filter
pip install drf-spectacular  # Documentation OpenAPI
```

Ajouter dans `requirements.txt` :
```
djangorestframework>=3.14.0
django-filter>=23.0
drf-spectacular>=0.26.0
```

---

## Configuration (10 min)

### 1. Ajouter dans settings.py

```python
# core/settings/base.py

INSTALLED_APPS = [
    ...
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    'suivi_demande',
    'analytics',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'GGR Credit Workflow API',
    'DESCRIPTION': 'API REST pour le système de gestion de workflow de crédit',
    'VERSION': '1.0.0',
}
```

---

## Création de l'API (1h)

### Structure

```
api/
├── __init__.py
├── serializers.py      # Sérialisation des modèles
├── views.py            # ViewSets
├── permissions.py      # Permissions personnalisées
└── urls.py             # Routes API
```

### 1. Serializers

```python
# api/serializers.py
from rest_framework import serializers
from suivi_demande.models import DossierCredit, UserProfile, JournalAction

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'full_name', 'phone', 'role']
        read_only_fields = ['id']


class DossierCreditListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste (moins de détails)."""
    client_name = serializers.CharField(source='client.username', read_only=True)
    
    class Meta:
        model = DossierCredit
        fields = [
            'id', 'reference', 'client_name', 'produit', 
            'montant', 'statut_agent', 'statut_client', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reference', 'created_at', 'updated_at']


class DossierCreditDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail (tous les champs)."""
    client = UserProfileSerializer(source='client.profile', read_only=True)
    acteur_courant = UserProfileSerializer(source='acteur_courant.profile', read_only=True)
    journal = serializers.SerializerMethodField()
    
    class Meta:
        model = DossierCredit
        fields = '__all__'
        read_only_fields = ['id', 'reference', 'created_at', 'updated_at']
    
    def get_journal(self, obj):
        """Retourne les 5 dernières actions."""
        actions = obj.journal_actions.all()[:5]
        return JournalActionSerializer(actions, many=True).data


class JournalActionSerializer(serializers.ModelSerializer):
    acteur_name = serializers.CharField(source='acteur.username', read_only=True)
    
    class Meta:
        model = JournalAction
        fields = ['id', 'action', 'de_statut', 'vers_statut', 
                  'acteur_name', 'timestamp', 'commentaire_systeme']
        read_only_fields = ['id', 'timestamp']
```

### 2. Permissions

```python
# api/permissions.py
from rest_framework import permissions

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permission personnalisée : 
    - Le client peut voir ses propres dossiers
    - Le staff peut voir tous les dossiers
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff a tous les droits
        if request.user.is_staff:
            return True
        
        # Le client peut voir ses propres dossiers
        if hasattr(obj, 'client'):
            return obj.client == request.user
        
        return False


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permission : lecture pour tous, écriture pour staff uniquement.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff
```

### 3. ViewSets

```python
# api/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from suivi_demande.models import DossierCredit
from .serializers import DossierCreditListSerializer, DossierCreditDetailSerializer
from .permissions import IsOwnerOrStaff

class DossierCreditViewSet(viewsets.ModelViewSet):
    """
    API ViewSet pour les dossiers de crédit.
    
    Endpoints:
    - GET /api/dossiers/ - Liste des dossiers
    - POST /api/dossiers/ - Créer un dossier
    - GET /api/dossiers/{id}/ - Détail d'un dossier
    - PUT /api/dossiers/{id}/ - Modifier un dossier
    - DELETE /api/dossiers/{id}/ - Supprimer un dossier
    - GET /api/dossiers/mes_dossiers/ - Mes dossiers (custom action)
    - POST /api/dossiers/{id}/changer_statut/ - Changer le statut
    """
    queryset = DossierCredit.objects.select_related('client', 'acteur_courant').all()
    permission_classes = [IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut_agent', 'statut_client', 'produit']
    search_fields = ['reference', 'client__username']
    ordering_fields = ['created_at', 'updated_at', 'montant']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Utiliser un serializer différent pour la liste et le détail."""
        if self.action == 'list':
            return DossierCreditListSerializer
        return DossierCreditDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle de l'utilisateur."""
        user = self.request.user
        
        # Staff voit tout
        if user.is_staff:
            return self.queryset
        
        # Client voit seulement ses dossiers
        return self.queryset.filter(client=user)
    
    @action(detail=False, methods=['get'])
    def mes_dossiers(self, request):
        """Endpoint personnalisé : /api/dossiers/mes_dossiers/"""
        dossiers = self.queryset.filter(client=request.user)
        serializer = self.get_serializer(dossiers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def changer_statut(self, request, pk=None):
        """
        Endpoint personnalisé : POST /api/dossiers/{id}/changer_statut/
        Body: {"nouveau_statut": "EN_COURS_ANALYSE"}
        """
        dossier = self.get_object()
        nouveau_statut = request.data.get('nouveau_statut')
        
        if not nouveau_statut:
            return Response(
                {'error': 'nouveau_statut requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Valider et changer le statut
        # (Logique métier à implémenter)
        dossier.statut_agent = nouveau_statut
        dossier.save()
        
        serializer = self.get_serializer(dossier)
        return Response(serializer.data)
```

### 4. URLs

```python
# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import DossierCreditViewSet

router = DefaultRouter()
router.register(r'dossiers', DossierCreditViewSet, basename='dossier')

urlpatterns = [
    path('', include(router.urls)),
    
    # Documentation OpenAPI
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

### 5. Intégrer dans core/urls.py

```python
# core/urls.py
urlpatterns = [
    ...
    path('api/', include('api.urls')),
]
```

---

## Résultat

### Endpoints disponibles :

```
GET    /api/dossiers/                    # Liste des dossiers
POST   /api/dossiers/                    # Créer un dossier
GET    /api/dossiers/{id}/               # Détail d'un dossier
PUT    /api/dossiers/{id}/               # Modifier
DELETE /api/dossiers/{id}/               # Supprimer
GET    /api/dossiers/mes_dossiers/       # Mes dossiers
POST   /api/dossiers/{id}/changer_statut/ # Changer statut

GET    /api/schema/                      # Schéma OpenAPI
GET    /api/docs/                        # Documentation Swagger
```

### Documentation automatique :

```
http://localhost:8000/api/docs/
```

---

## Temps estimé : 1h30

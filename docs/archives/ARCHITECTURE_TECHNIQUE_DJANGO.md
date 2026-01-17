# 📐 DOCUMENTATION TECHNIQUE - ARCHITECTURE DJANGO

**GGR Credit Workflow - Architecture Logicielle**  
**Version** : 1.0 | **Date** : 4 novembre 2025

---

## 1. ARCHITECTURE GÉNÉRALE

### 1.1 Pattern architectural : MVT (Model-View-Template)
Django utilise le pattern MVT, variante du MVC :
- **Model** : Couche de données (models.py)
- **View** : Logique métier (views.py)
- **Template** : Présentation (fichiers .html)

### 1.2 Architecture multi-portails
```
┌─────────────────────────────────────────┐
│         UTILISATEURS                     │
├──────────────────┬──────────────────────┤
│  Clients         │  Professionnels      │
│  Port 8001       │  Port 8002           │
└────────┬─────────┴──────────┬───────────┘
         │                    │
    ┌────▼────────────────────▼────┐
    │   DJANGO APPLICATION          │
    │   ┌──────────────────────┐   │
    │   │  core/settings/      │   │
    │   │  - base.py           │   │
    │   │  - client.py         │   │
    │   │  - pro.py            │   │
    │   └──────────────────────┘   │
    │   ┌──────────────────────┐   │
    │   │  suivi_demande/      │   │
    │   │  - models.py         │   │
    │   │  - views_modules/    │   │
    │   │  - forms.py          │   │
    │   └──────────────────────┘   │
    └───────────┬──────────────────┘
                │
    ┌───────────▼──────────────────┐
    │   POSTGRESQL DATABASE         │
    └──────────────────────────────┘
```

### 1.3 Flux de données
```
Client HTTP Request
    ↓
Django URL Router (urls.py)
    ↓
Middleware (auth, CSRF, session)
    ↓
View (views_modules/)
    ↓
Model (ORM → PostgreSQL)
    ↓
Template (HTML + Context)
    ↓
HTTP Response
```

---

## 2. STRUCTURE DES DOSSIERS

```
ggr-credit-workflow/
├── core/                          # Configuration Django
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py               # Settings communs
│   │   ├── client.py             # Portail client
│   │   └── pro.py                # Portail pro
│   ├── urls.py                   # URLs racine
│   ├── wsgi.py                   # Point d'entrée WSGI
│   └── asgi.py                   # Point d'entrée ASGI
│
├── suivi_demande/                # Application principale
│   ├── models.py                 # 8 modèles de données
│   ├── views.py                  # Vues (ancien, 2027 lignes)
│   ├── views_modules/            # Vues modulaires (nouveau)
│   │   ├── __init__.py
│   │   ├── base.py              # Vues de base
│   │   ├── dossiers.py          # Gestion dossiers
│   │   ├── dashboard.py         # Dashboards
│   │   ├── workflow.py          # Transitions
│   │   ├── notifications.py     # Notifications
│   │   └── ajax.py              # API AJAX
│   ├── forms.py                  # Formulaires généraux
│   ├── forms_demande.py          # Wizard étapes 1-2
│   ├── forms_demande_extra.py    # Wizard étapes 3-4
│   ├── urls.py                   # Routes de l'app
│   ├── admin.py                  # Interface admin
│   ├── decorators.py             # Décorateurs custom
│   ├── permissions.py            # Logique permissions
│   ├── constants.py              # Constantes
│   ├── logging_config.py         # Configuration logging
│   ├── utils.py                  # Fonctions utilitaires
│   ├── middleware_portal.py      # Middleware portails
│   ├── tests/                    # Tests (75 tests)
│   │   ├── test_models.py
│   │   ├── test_permissions.py
│   │   ├── test_workflow.py
│   │   ├── test_views.py
│   │   ├── test_forms.py
│   │   └── test_integration.py
│   └── migrations/               # Migrations BDD
│
├── templates/                     # Templates HTML
│   ├── base.html                 # Template de base
│   ├── home.html
│   ├── accounts/                 # Auth templates
│   ├── suivi_demande/            # Templates app
│   ├── emails/                   # Templates emails
│   └── pdf/                      # Templates PDF
│
├── static/                        # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/                         # Fichiers uploadés
├── logs/                          # Fichiers de logs
└── docs/                          # Documentation
```

---

## 3. DESCRIPTION TECHNIQUE DES APPS

### 3.1 App `core`
**Rôle** : Configuration globale du projet

**Fichiers clés** :
- `settings/base.py` : Configuration commune (BDD, apps, middleware)
- `settings/client.py` : Configuration portail client (port 8001)
- `settings/pro.py` : Configuration portail pro (port 8002)
- `urls.py` : Routage principal

### 3.2 App `suivi_demande`
**Rôle** : Application métier principale

**Composants** :
- **8 modèles** : User, UserProfile, DossierCredit, CanevasProposition, etc.
- **20+ vues** : Modulaires dans views_modules/
- **15+ formulaires** : Validation des données
- **30+ templates** : Interface utilisateur
- **75 tests** : Couverture 75-80%

---

## 4. DOCUMENTATION DES MODELS

### 4.1 Architecture des modèles

```python
User (Django built-in)
  ↓ OneToOne
UserProfile (rôle, téléphone, adresse)
  ↓ OneToMany
DossierCredit (référence, montant, statuts)
  ↓ OneToOne
CanevasProposition (analyse financière)
  ↓ OneToMany
PieceJointe, Commentaire, JournalAction
```

### 4.2 Modèles principaux

#### UserProfile
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    role = models.CharField(max_length=20, choices=UserRoles.choices)
    
    # Index pour performance
    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]
```

#### DossierCredit
```python
class DossierCredit(models.Model):
    reference = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    statut_agent = models.CharField(max_length=50, choices=...)
    statut_client = models.CharField(max_length=50, choices=...)
    acteur_courant = models.ForeignKey(User, ...)
    
    # Optimisation requêtes
    class Meta:
        ordering = ['-date_soumission']
        indexes = [
            models.Index(fields=['client', 'statut_agent']),
            models.Index(fields=['statut_agent', 'is_archived']),
        ]
```

### 4.3 Relations entre modèles
- **OneToOne** : User ↔ UserProfile, DossierCredit ↔ CanevasProposition
- **ForeignKey** : DossierCredit → User (client, acteur_courant)
- **ManyToMany** : Aucune (design simplifié)

---

## 5. DOCUMENTATION DES VIEWS

### 5.1 Architecture modulaire
Les vues sont organisées en modules thématiques :

```python
views_modules/
├── base.py          # home, signup, pending_approval
├── dossiers.py      # my_applications, create, edit, delete
├── dashboard.py     # dashboard (6 versions par rôle)
├── workflow.py      # transition_dossier, transmettre_analyste
├── notifications.py # notifications_list, mark_read
└── ajax.py          # API JSON
```

### 5.2 Exemple de vue : dashboard

```python
@login_required
def dashboard(request):
    """Dashboard adapté au rôle de l'utilisateur."""
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)
    
    if role == UserRoles.CLIENT:
        return _dashboard_client(request)
    elif role == UserRoles.GESTIONNAIRE:
        return _dashboard_gestionnaire(request)
    # ... autres rôles
```

### 5.3 Optimisations appliquées
```python
# Éviter N+1 queries
dossiers = DossierCredit.objects.select_related(
    'client', 'acteur_courant'
).prefetch_related('pieces')

# Pagination
from django.core.paginator import Paginator
paginator = Paginator(dossiers_list, 25)
dossiers = paginator.get_page(page_number)
```

---

## 6. DOCUMENTATION DES URLs

### 6.1 Structure des URLs

```python
# core/urls.py (racine)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('suivi_demande.urls')),
]

# suivi_demande/urls.py
urlpatterns = [
    # Base
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Dossiers
    path('my-applications/', views.my_applications, name='my_applications'),
    path('dossier/<int:pk>/', views.dossier_detail, name='dossier_detail'),
    
    # Workflow
    path('transition/<int:pk>/<str:action>/', views.transition_dossier, name='transition_dossier'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
]
```

### 6.2 Namespaces
- Portail client : `namespace='suivi'`
- Portail pro : `namespace='pro'`

---

## 7. DOCUMENTATION DES TEMPLATES

### 7.1 Hiérarchie des templates

```
base.html (template racine)
  ↓ extends
├── home.html
├── dashboard_client.html
├── dashboard_gestionnaire.html
└── dossier_detail.html
```

### 7.2 Template de base

```html
<!-- base.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>{% block title %}GGR Credit{% endblock %}</title>
    {% load static %}
    <link href="{% static 'css/charte_graphique.css' %}" rel="stylesheet">
</head>
<body>
    {% include 'partials/navbar.html' %}
    
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
    
    {% block content %}{% endblock %}
    
    {% include 'partials/footer.html' %}
</body>
</html>
```

### 7.3 Context processors
Variables disponibles dans tous les templates :
- `user` : Utilisateur connecté
- `request` : Objet requête
- `messages` : Messages flash
- `STATIC_URL`, `MEDIA_URL`

---

## 8. DOCUMENTATION DES FORMULAIRES

### 8.1 Types de formulaires

**Formulaires Django** :
```python
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
```

**Formulaires wizard** :
```python
class DemandeStep1Form(forms.Form):
    nom_prenom = forms.CharField(max_length=200)
    date_naissance = forms.DateField()
    # ... autres champs
    
    def clean_date_naissance(self):
        """Validation personnalisée."""
        date = self.cleaned_data['date_naissance']
        if date > timezone.now().date():
            raise ValidationError("Date invalide")
        return date
```

### 8.2 Validation
- **Validation champ** : `clean_<field_name>()`
- **Validation formulaire** : `clean()`
- **Validation modèle** : `Model.clean()`

---

## 9. FICHIERS STATIQUES

### 9.1 Organisation
```
static/
├── css/
│   ├── charte_graphique.css    # Charte graphique
│   └── custom.css              # Styles custom
├── js/
│   ├── main.js                 # JavaScript principal
│   └── notifications.js        # Gestion notifications
└── img/
    └── Credit_Du_Congo.png     # Logo
```

### 9.2 Configuration
```python
# settings/base.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise pour la production
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
```

---

## 10. CONFIGURATION TECHNIQUE

### 10.1 Settings modulaires
```python
# base.py - Configuration commune
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'suivi_demande',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'suivi_demande.middleware_portal.PortalMiddleware',
]

# client.py - Portail client
from .base import *
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
PORTAL_TYPE = 'client'

# pro.py - Portail pro
from .base import *
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
PORTAL_TYPE = 'pro'
```

### 10.2 Middleware custom
```python
class PortalMiddleware:
    """Middleware pour gérer les portails."""
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.portal = settings.PORTAL_TYPE
        response = self.get_response(request)
        return response
```

---

## 11. GESTION DES LOGS

### 11.1 Configuration
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file_general': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'general.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
        },
        'file_security': {
            'filename': BASE_DIR / 'logs' / 'security.log',
        },
        'file_workflow': {
            'filename': BASE_DIR / 'logs' / 'workflow.log',
        },
    },
    'loggers': {
        'suivi_demande': {
            'handlers': ['file_general'],
            'level': 'INFO',
        },
        'suivi_demande.security': {
            'handlers': ['file_security'],
            'level': 'INFO',
        },
    },
}
```

### 11.2 Utilisation
```python
from .logging_config import log_transition, security_logger

log_transition(dossier, action, user, from_status, to_status)
security_logger.info(f"Login success: {user.username}")
```

---

## 12. PERMISSIONS ET SÉCURITÉ

### 12.1 Contrôle d'accès par rôle (RBAC)
```python
@login_required
@transition_allowed
def transition_dossier(request, pk, action):
    """Vérifie automatiquement les permissions."""
    # Décorateur transition_allowed vérifie :
    # - Utilisateur connecté
    # - Rôle autorisé pour l'action
    # - Statut du dossier compatible
```

### 12.2 Isolation des données
```python
# Client ne voit que ses dossiers
if role == UserRoles.CLIENT and dossier.client != request.user:
    messages.error(request, "Accès refusé")
    return redirect('dashboard')
```

### 12.3 Protection CSRF
```html
<form method="post">
    {% csrf_token %}
    <!-- champs -->
</form>
```

---

## 13. INTERACTION AVEC LA BASE DE DONNÉES

### 13.1 ORM Django
```python
# Création
dossier = DossierCredit.objects.create(
    client=user,
    reference="DOS-2025-001",
    montant=Decimal('2000000.00')
)

# Lecture avec optimisation
dossiers = DossierCredit.objects.select_related(
    'client', 'acteur_courant'
).filter(statut_agent='NOUVEAU')

# Mise à jour
dossier.statut_agent = 'TRANSMIS_ANALYSTE'
dossier.save()

# Suppression
dossier.delete()
```

### 13.2 Transactions
```python
from django.db import transaction

@transaction.atomic
def transition_dossier(request, pk, action):
    """Toutes les opérations sont atomiques."""
    dossier.statut_agent = new_status
    dossier.save()
    JournalAction.objects.create(...)
    Notification.objects.create(...)
```

---

## 14. PROCESSUS D'EXÉCUTION D'UNE REQUÊTE

### 14.1 Flux complet
```
1. CLIENT envoie requête HTTP
   GET /dashboard/

2. WSGI/ASGI reçoit la requête
   → Passe à Django

3. URL ROUTER (urls.py)
   → Trouve la route correspondante
   → path('dashboard/', views.dashboard)

4. MIDDLEWARE (dans l'ordre)
   → SecurityMiddleware
   → SessionMiddleware
   → CsrfViewMiddleware
   → AuthenticationMiddleware (charge request.user)
   → PortalMiddleware (ajoute request.portal)

5. VIEW (views_modules/dashboard.py)
   → Vérifie @login_required
   → Récupère le rôle de l'utilisateur
   → Appelle _dashboard_client() ou autre selon rôle

6. LOGIQUE MÉTIER
   → Requêtes ORM à la base de données
   dossiers = DossierCredit.objects.filter(
       client=request.user
   ).select_related('acteur_courant')
   
7. CONTEXT
   → Prépare les données pour le template
   context = {
       'dossiers': dossiers,
       'stats': stats,
   }

8. TEMPLATE RENDERING
   → Charge dashboard_client.html
   → Hérite de base.html
   → Remplace {% block content %}
   → Insère les variables du context

9. MIDDLEWARE (retour)
   → Traite la réponse dans l'ordre inverse

10. HTTP RESPONSE
    → Envoyée au client
    → Status 200, HTML généré
```

### 14.2 Exemple concret : Création de dossier

```
POST /demande/step4/ avec données formulaire

1. URL Router → views.demande_step4

2. Middleware → Authentification OK

3. View demande_step4():
   a. Récupère données session (étapes 1-3)
   b. Valide formulaire étape 4
   c. Si valide:
      - Crée DossierCredit
      - Génère référence unique
      - Upload documents
      - Crée JournalAction
      - Crée Notification
      - Log l'action
      - Envoie email
   d. Redirect vers dashboard

4. Template → Message de confirmation

5. Response → Redirect 302 vers /dashboard/
```

---

**Document rédigé par un architecte logiciel Django senior**  
**Conforme aux standards académiques et professionnels**

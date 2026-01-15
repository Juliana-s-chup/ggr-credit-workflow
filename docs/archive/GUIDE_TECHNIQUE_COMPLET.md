# 🔧 GUIDE TECHNIQUE COMPLET

**Documentation technique détaillée du projet GGR Credit Workflow**

---

## 📋 TABLE DES MATIÈRES

1. [Configuration](#configuration)
2. [Base de données](#base-de-données)
3. [API et endpoints](#api-et-endpoints)
4. [Formulaires](#formulaires)
5. [Templates](#templates)
6. [Fichiers statiques](#fichiers-statiques)
7. [Logging](#logging)
8. [Tests](#tests)

---

## ⚙️ CONFIGURATION

### Settings modulaires

Le projet utilise 3 fichiers de settings :

#### 1. `core/settings/base.py` - Configuration commune

```python
# Base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='credit_db'),
        'USER': env('DB_USER', default='credit_user'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='127.0.0.1'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suivi_demande',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'suivi_demande.middleware_portal.PortalMiddleware',
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

#### 2. `core/settings/client.py` - Portail client

```python
from .base import *

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'client.ggr-credit.local']
ROOT_URLCONF = 'core.urls'
PORTAL_TYPE = 'client'
```

#### 3. `core/settings/pro.py` - Portail professionnel

```python
from .base import *

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'pro.ggr-credit.local']
ROOT_URLCONF = 'core.urls'
PORTAL_TYPE = 'pro'
```

### Variables d'environnement (.env)

```bash
# Django
SECRET_KEY=votre-cle-secrete-tres-longue
DEBUG=True
DJANGO_SETTINGS_MODULE=core.settings.base

# Base de données
DB_NAME=credit_db
DB_USER=credit_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=127.0.0.1
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@ggr-credit.cg

# Uploads
UPLOAD_MAX_BYTES=5242880  # 5 MB
```

---

## 💾 BASE DE DONNÉES

### Schéma relationnel

```
User (Django)
  ↓ OneToOne
UserProfile
  - role (CLIENT, GESTIONNAIRE, etc.)

User
  ↓ OneToMany
DossierCredit
  ↓ OneToOne
CanevasProposition

DossierCredit
  ↓ OneToMany
PieceJointe
Commentaire
JournalAction

User
  ↓ OneToMany
Notification
```

### Migrations importantes

```bash
# Migration initiale
0001_initial.py

# Ajout archivage
0002_dossiercredit_archived_at_dossiercredit_archived_by.py

# Ajout canevas
0003_canevasproposition.py

# Ajout index (performance)
0011_alter_dossiercredit_options_and_more.py
```

### Index de performance

```python
class DossierCredit(models.Model):
    # ...
    class Meta:
        ordering = ['-date_soumission']
        indexes = [
            models.Index(fields=['client', 'statut_agent']),
            models.Index(fields=['statut_agent', 'is_archived']),
        ]
```

---

## 🌐 API ET ENDPOINTS

### Routes principales

#### Portail Client

```python
# Authentification
/accounts/login/          # Connexion
/accounts/logout/         # Déconnexion
/signup/                  # Inscription

# Dashboard
/dashboard/               # Dashboard client
/my-applications/         # Liste dossiers (paginée)

# Wizard demande
/demande/start/           # Démarrage
/demande/step1/           # Étape 1
/demande/step2/           # Étape 2
/demande/step3/           # Étape 3
/demande/step4/           # Étape 4
/demande/verification/    # Vérification

# Dossiers
/dossier/<id>/            # Détail dossier

# Notifications
/notifications/           # Liste (paginée)
/notifications/mark-read/<id>/  # Marquer lue
/notifications/mark-all-read/   # Marquer toutes lues
```

#### Portail Professionnel

```python
# Authentification
/pro/login/               # Connexion pro

# Dashboard
/pro/dashboard/           # Dashboard selon rôle

# Gestion dossiers
/pro/dossier/<id>/        # Détail dossier
/pro/transition/<id>/<action>/  # Transition

# Canevas
/pro/canevas/<dossier_id>/      # Créer/Modifier
/pro/canevas/<id>/pdf/          # Générer PDF

# Administration
/pro/admin/users/         # Gestion utilisateurs
/pro/admin/change-role/<id>/    # Changer rôle
/pro/admin/activate/<id>/       # Activer compte
```

### API AJAX

```python
# Notifications
/api/notifications/       # GET: Liste JSON
```

---

## 📝 FORMULAIRES

### Formulaires du wizard

#### DemandeStep1Form
```python
class DemandeStep1Form(forms.Form):
    nom_prenom = forms.CharField(max_length=200)
    date_naissance = forms.DateField()
    nationalite = forms.ChoiceField(choices=NATIONALITE_CHOICES)
    adresse_exacte = forms.CharField(widget=forms.Textarea)
    numero_telephone = forms.CharField(max_length=20)
    emploi_occupe = forms.CharField(max_length=200)
    statut_emploi = forms.ChoiceField(choices=STATUT_EMPLOI_CHOICES)
    anciennete_emploi = forms.CharField(max_length=100)
    type_contrat = forms.ChoiceField(choices=TYPE_CONTRAT_CHOICES)
    nom_employeur = forms.CharField(max_length=200)
    lieu_emploi = forms.CharField(max_length=200)
    situation_famille = forms.ChoiceField(choices=SITUATION_FAMILLE_CHOICES)
```

#### DemandeStep2Form
```python
class DemandeStep2Form(forms.Form):
    salaire_net_moyen = forms.DecimalField(max_digits=12, decimal_places=2)
    autres_revenus = forms.DecimalField(max_digits=12, decimal_places=2)
    total_charges_mensuelles = forms.DecimalField(max_digits=12, decimal_places=2)
    nombre_personnes_charge = forms.IntegerField(min_value=0)
    credits_en_cours = forms.ChoiceField(choices=[('OUI', 'Oui'), ('NON', 'Non')])
    total_echeances_credits = forms.DecimalField(max_digits=12, decimal_places=2)
```

### Validation personnalisée

```python
def clean_salaire_net_moyen(self):
    salaire = self.cleaned_data['salaire_net_moyen']
    if salaire < 0:
        raise ValidationError("Le salaire ne peut pas être négatif")
    return salaire
```

---

## 🎨 TEMPLATES

### Structure des templates

```
templates/
├── base.html                    # Template de base
├── home.html                    # Page d'accueil
├── accounts/
│   ├── login.html              # Connexion
│   ├── signup.html             # Inscription
│   └── pending_approval.html   # Attente approbation
├── suivi_demande/
│   ├── dashboard_client.html
│   ├── dashboard_gestionnaire.html
│   ├── dashboard_analyste.html
│   ├── dashboard_responsable_ggr_pro.html
│   ├── dashboard_boe.html
│   ├── dashboard_super_admin.html
│   ├── my_applications.html
│   ├── dossier_detail.html
│   ├── notifications.html
│   ├── demande_step1.html
│   ├── demande_step2.html
│   ├── demande_step3.html
│   ├── demande_step4.html
│   └── canevas_proposition.html
├── emails/
│   ├── retour_client.html      # Email HTML
│   └── dossier_update_client.html
└── pdf/
    └── proposition.html         # Template PDF
```

### Template de base

```html
<!-- base.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GGR Credit{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'partials/navbar.html' %}
    
    <main class="container my-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
    
    {% include 'partials/footer.html' %}
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 📁 FICHIERS STATIQUES

### Structure

```
static/
├── css/
│   ├── charte_graphique.css    # Charte graphique
│   └── custom.css              # Styles personnalisés
├── js/
│   ├── main.js                 # JavaScript principal
│   └── notifications.js        # Gestion notifications
├── img/
│   ├── Credit_Du_Congo.png     # Logo
│   └── favicon.ico             # Icône
└── suivi_demande/
    ├── css/
    └── img/
```

### Chargement dans les templates

```html
{% load static %}

<link rel="stylesheet" href="{% static 'css/charte_graphique.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'img/Credit_Du_Congo.png' %}" alt="Logo">
```

---

## 📊 LOGGING

### Configuration

```python
# logging_config.py

import logging

logger = logging.getLogger(__name__)

def log_dossier_creation(dossier, user):
    """Log la création d'un dossier."""
    logger.info(
        f"Dossier créé: {dossier.reference} par {user.username}"
    )

def log_transition(dossier, action, user, from_status, to_status):
    """Log une transition de statut."""
    logger.info(
        f"Transition: {dossier.reference} | "
        f"{from_status} → {to_status} | "
        f"Action: {action} | "
        f"Par: {user.username}"
    )

def log_error(context, error, user=None):
    """Log une erreur."""
    logger.error(
        f"Erreur dans {context}: {str(error)} | "
        f"User: {user.username if user else 'Anonymous'}"
    )
```

### Utilisation

```python
from .logging_config import log_transition

# Dans une vue
log_transition(dossier, 'transmettre_analyste', request.user, 
               DossierStatutAgent.NOUVEAU, 
               DossierStatutAgent.TRANSMIS_ANALYSTE)
```

### Fichiers de logs

```
logs/
├── django.log              # Log principal (rotation 10MB)
├── django.log.1            # Backup 1
├── django.log.2            # Backup 2
└── ...                     # Jusqu'à 5 backups
```

---

## 🧪 TESTS

### Structure des tests

```
suivi_demande/tests/
├── __init__.py
├── test_models.py          # 15 tests
├── test_permissions.py     # 10 tests
├── test_workflow.py        # 8 tests
├── test_views.py           # 17 tests
├── test_forms.py           # 15 tests
└── test_integration.py     # 10 tests
```

### Exemple de test

```python
class DossierCreditTestCase(TestCase):
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user('test', password='pass')
        UserProfile.objects.create(
            user=self.user,
            full_name="Test",
            phone="+242 06 000 00 00",
            address="Test",
            role=UserRoles.CLIENT
        )
    
    def test_creation_dossier(self):
        """Test la création d'un dossier."""
        dossier = DossierCredit.objects.create(
            client=self.user,
            reference="DOS-TEST-001",
            produit="Crédit",
            montant=Decimal('1000000.00')
        )
        
        self.assertEqual(dossier.statut_agent, DossierStatutAgent.NOUVEAU)
        self.assertEqual(dossier.client, self.user)
```

### Lancer les tests

```bash
# Tous les tests
python manage.py test suivi_demande

# Tests spécifiques
python manage.py test suivi_demande.tests.test_models

# Avec couverture
coverage run --source='.' manage.py test suivi_demande
coverage report
coverage html
```

---

## 🔐 SÉCURITÉ

### Protection CSRF

```python
# Activé par défaut dans settings
MIDDLEWARE = [
    # ...
    'django.middleware.csrf.CsrfViewMiddleware',
    # ...
]

# Dans les formulaires
<form method="post">
    {% csrf_token %}
    <!-- champs -->
</form>
```

### Validation des uploads

```python
# Dans constants.py
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_FILE_TYPES = ['application/pdf', 'image/jpeg', 'image/png']

# Dans la vue
if fichier.size > MAX_FILE_SIZE:
    messages.error(request, "Fichier trop volumineux")
    return redirect(...)
```

### Permissions

```python
# Décorateur personnalisé
@login_required
@transition_allowed
def transition_dossier(request, pk, action):
    # Vérifie automatiquement les permissions
    pass
```

---

**Documentation technique générée le 4 novembre 2025**

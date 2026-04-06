# 📚 DOCUMENTATION SOUTENANCE - PARTIE 2
## Structure des Dossiers et Fichiers

---

# 3. STRUCTURE DES DOSSIERS (TRÈS IMPORTANT)

## 3.1 Vue d'ensemble

```
ggr-credit-workflow/
├── 📁 core/                    # Configuration Django
├── 📁 suivi_demande/           # Application métier principale
├── 📁 analytics/               # Module d'analyse
├── 📁 templates/               # Templates HTML
├── 📁 static/                  # Fichiers statiques
├── 📁 media/                   # Fichiers uploadés
├── 📁 docs/                    # Documentation
├── 📁 scripts/                 # Scripts utilitaires
├── 📁 nginx/                   # Configuration Nginx
├── 📄 manage.py                # Script Django
├── 📄 requirements.txt         # Dépendances Python
├── 📄 Dockerfile               # Configuration Docker
└── 📄 docker-compose.yml       # Orchestration Docker
```

## 3.2 Dossier `core/` - Le cerveau de l'application

### Rôle :
C'est le **centre de configuration** de Django. Tout ce qui concerne la configuration globale est ici.

### Pourquoi il existe :
Django a besoin d'un endroit centralisé pour :
- Configurer les paramètres (base de données, sécurité, etc.)
- Définir les URLs principales
- Gérer les settings par environnement (dev, prod)

### Contenu :
```
core/
├── settings/
│   ├── base.py          # Settings communs à tous les environnements
│   ├── client.py        # Settings spécifiques au portail client
│   ├── pro.py           # Settings spécifiques au portail pro
│   └── prod.py          # Settings de production
├── urls.py              # URLs principales de l'application
├── wsgi.py              # Point d'entrée WSGI (serveur web)
├── asgi.py              # Point d'entrée ASGI (websockets)
├── security.py          # Utilitaires de sécurité
└── monitoring.py        # Monitoring et logs
```

### Interaction avec les autres dossiers :
- `core/settings/` → Lit les variables de `suivi_demande/`, `analytics/`
- `core/urls.py` → Inclut les URLs de `suivi_demande/urls.py`
- Tous les autres dossiers dépendent de `core/` pour la configuration

### Exemple concret :
Quand vous lancez `python manage.py runserver`, Django :
1. Lit `core/settings/base.py` pour la configuration
2. Charge `core/urls.py` pour savoir quelles URLs existent
3. Démarre le serveur avec ces paramètres

## 3.3 Dossier `suivi_demande/` - Le cœur métier

### Rôle :
C'est l'**application principale** qui gère TOUT le métier des dossiers de crédit.

### Pourquoi il existe :
Dans Django, on organise le code en "applications". Chaque application a une responsabilité.
`suivi_demande` = Tout ce qui concerne les dossiers de crédit.

### Contenu détaillé :

```
suivi_demande/
├── 📄 models.py                 # Définition des tables (DossierCredit, UserProfile, etc.)
├── 📄 views.py                  # Logique des pages (81 KB ! Très gros fichier)
├── 📄 views_portals.py          # Vues spécifiques aux portails
├── 📄 views_admin.py            # Vues d'administration
├── 📄 views_documents.py        # Gestion des documents
├── 📄 views_canevas.py          # Gestion du canevas de proposition
├── 📄 forms.py                  # Formulaires (inscription, etc.)
├── 📄 forms_demande.py          # Formulaires de demande de crédit
├── 📄 forms_canevas.py          # Formulaire du canevas
├── 📄 urls.py                   # URLs générales
├── 📄 urls_client.py            # URLs du portail client
├── 📄 urls_pro.py               # URLs du portail professionnel
├── 📄 decorators.py             # Décorateurs personnalisés (@role_required, etc.)
├── 📄 permissions.py            # Gestion des permissions
├── 📄 validators.py             # Validation des données
├── 📄 constants.py              # Constantes (montants min/max, etc.)
├── 📄 middleware_portal.py      # Middleware de contrôle d'accès
├── 📁 services/                 # Couche service (logique métier)
│   ├── dossier_service.py       # Service de gestion des dossiers
│   └── __init__.py
├── 📁 ml/                       # Machine Learning
│   ├── credit_scoring.py        # Modèle de scoring crédit
│   └── __init__.py
├── 📁 tests/                    # Tests unitaires et d'intégration
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_security.py
│   └── ... (7 fichiers de tests)
├── 📁 migrations/               # Migrations de base de données
│   ├── 0001_initial.py
│   ├── 0002_...py
│   └── ... (14 migrations)
├── 📁 management/               # Commandes Django personnalisées
│   └── commands/
│       └── train_scoring_model.py
└── 📁 templatetags/             # Tags de template personnalisés
    └── custom_filters.py
```

### Fichiers clés expliqués :

#### `models.py` - La structure des données
**Rôle** : Définit toutes les tables de la base de données

**Modèles principaux** :
- `UserProfile` → Profil utilisateur étendu (rôle, téléphone, etc.)
- `DossierCredit` → Le dossier de crédit (montant, statut, etc.)
- `PieceJointe` → Les documents uploadés
- `CanevasProposition` → Formulaire détaillé de proposition
- `JournalAction` → Historique des actions (audit trail)
- `Notification` → Notifications aux utilisateurs
- `Commentaire` → Commentaires sur les dossiers

#### `views.py` - La logique des pages
**Rôle** : Contient toute la logique pour afficher les pages et traiter les actions

**Fonctions importantes** :
- `dashboard()` → Affiche le tableau de bord selon le rôle
- `demande_step1/2/3/4()` → Wizard de création de dossier
- `transition_dossier()` → Gère les transitions du workflow
- `dossier_detail()` → Affiche le détail d'un dossier
- `upload_piece()` → Upload de documents

#### `forms.py` - Les formulaires
**Rôle** : Définit les formulaires HTML et leur validation

**Formulaires** :
- `SignupForm` → Inscription
- `DemandeStep1Form` → Étape 1 de la demande
- `CanevasForm` → Formulaire du canevas

#### `decorators.py` - Les décorateurs
**Rôle** : Fonctions qui "décorent" d'autres fonctions pour ajouter des fonctionnalités

**Décorateurs** :
- `@role_required("GESTIONNAIRE")` → Vérifie que l'utilisateur a le bon rôle
- `@transition_allowed` → Vérifie si l'utilisateur peut faire une transition

**Exemple d'utilisation** :
```python
@login_required
@role_required("GESTIONNAIRE")
def dashboard_gestionnaire(request):
    # Seuls les gestionnaires peuvent accéder à cette vue
    ...
```

#### `services/dossier_service.py` - La couche service
**Rôle** : Logique métier réutilisable, séparée des vues

**Avantages** :
- Code réutilisable
- Plus facile à tester
- Séparation des responsabilités

**Exemple** :
```python
class DossierService:
    @staticmethod
    def get_dossiers_for_user(user, page=1, per_page=25):
        """Récupère les dossiers selon le rôle de l'utilisateur"""
        role = user.profile.role
        
        if role == UserRoles.CLIENT:
            # Le client voit ses propres dossiers
            queryset = DossierCredit.objects.filter(client=user)
        elif role == UserRoles.GESTIONNAIRE:
            # Le gestionnaire voit les nouveaux dossiers
            queryset = DossierCredit.objects.filter(statut_agent='NOUVEAU')
        # ... etc
        
        return paginate(queryset, page, per_page)
```

### Interaction avec les autres dossiers :
- Utilise `core/settings/` pour la configuration
- Lit/écrit dans la base de données PostgreSQL
- Utilise les templates de `templates/suivi_demande/`
- Sert les fichiers statiques de `static/`
- Stocke les uploads dans `media/`

## 3.4 Dossier `analytics/` - Les statistiques

### Rôle :
Module **indépendant** pour les tableaux de bord et les rapports.

### Pourquoi il existe :
Séparation des responsabilités :
- `suivi_demande/` → Gestion des dossiers
- `analytics/` → Analyse et reporting

### Contenu :
```
analytics/
├── models.py            # Tables pour les statistiques
├── views.py             # Vues des dashboards
├── services.py          # Logique d'analyse
├── urls.py              # URLs du module analytics
└── templates/           # Templates des dashboards
```

### Ce qu'il fait :
- Calcule des statistiques (taux d'approbation, montants moyens, etc.)
- Génère des graphiques
- Produit des rapports Excel/PDF

### Interaction :
- Lit les données de `suivi_demande.models.DossierCredit`
- Utilise des requêtes SQL optimisées (agrégations)
- Affiche les résultats dans des dashboards

## 3.5 Dossier `templates/` - L'interface utilisateur

### Rôle :
Contient tous les **fichiers HTML** que l'utilisateur voit.

### Structure :
```
templates/
├── base.html                    # Template de base (header, footer)
├── base-clean.html              # Template sans navigation
├── home.html                    # Page d'accueil
├── suivi_demande/               # Templates de l'app suivi_demande
│   ├── dashboard_client.html    # Dashboard client
│   ├── dashboard_gestionnaire.html
│   ├── dossier_detail.html      # Détail d'un dossier
│   ├── demande_step1.html       # Formulaire étape 1
│   └── ...
├── analytics/                   # Templates analytics
│   └── dashboard.html
├── accounts/                    # Templates d'authentification
│   ├── login.html
│   └── signup.html
└── components/                  # Composants réutilisables
    ├── alert.html
    ├── button.html
    └── ...
```

### Principe d'héritage :
```
base.html (structure générale : header, footer, menu)
    ↓ extends
dashboard_client.html (contenu spécifique au dashboard)
```

**Exemple** :
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}GGR Credit{% endblock %}</title>
</head>
<body>
    <nav><!-- Menu --></nav>
    
    {% block content %}
    <!-- Le contenu sera inséré ici -->
    {% endblock %}
    
    <footer><!-- Footer --></footer>
</body>
</html>

<!-- dashboard_client.html -->
{% extends "base.html" %}

{% block title %}Mon Dashboard{% endblock %}

{% block content %}
    <h1>Mes dossiers</h1>
    {% for dossier in dossiers %}
        <div>{{ dossier.reference }}</div>
    {% endfor %}
{% endblock %}
```

## 3.6 Dossier `static/` - Les ressources

### Rôle :
Fichiers **statiques** (CSS, JavaScript, images) qui ne changent pas.

### Structure :
```
static/
├── css/
│   ├── charte_graphique.css     # Styles de la charte
│   ├── design-system.css        # Design system
│   └── modern-dashboard.css     # Styles des dashboards
├── js/
│   ├── main.js                  # JavaScript principal
│   └── src/                     # Code source JS
└── core/
    └── css/                     # Styles du core
```

### Pourquoi séparer static/ et media/ :
- `static/` → Fichiers du développeur (CSS, JS, logos) - versionnés dans Git
- `media/` → Fichiers uploadés par les utilisateurs (documents, photos) - PAS dans Git

## 3.7 Dossier `media/` - Les uploads

### Rôle :
Stocke les **fichiers uploadés** par les utilisateurs.

### Structure :
```
media/
└── dossiers/
    ├── CRED-2025-001/           # Dossier par référence
    │   ├── CNI_client.pdf
    │   ├── fiche_paie.pdf
    │   └── releve_bancaire.pdf
    └── CRED-2025-002/
        └── ...
```

### Sécurité :
- Validation du type de fichier (PDF, JPG, PNG uniquement)
- Limite de taille (5 MB max)
- Nom de fichier sanitizé (pas de caractères dangereux)
- Stockage organisé par dossier

## 3.8 Fichiers à la racine

### `manage.py` - Le couteau suisse Django
**Rôle** : Script principal pour toutes les commandes Django

**Exemples d'utilisation** :
```bash
python manage.py migrate          # Applique les migrations
python manage.py createsuperuser  # Crée un admin
python manage.py runserver        # Lance le serveur
python manage.py test             # Lance les tests
python manage.py collectstatic    # Collecte les fichiers statiques
```

### `requirements.txt` - Les dépendances
**Rôle** : Liste toutes les bibliothèques Python nécessaires

**Contenu** :
```
Django==5.2.6              # Framework web
psycopg2-binary==2.9.10    # Driver PostgreSQL
django-environ==0.11.2     # Variables d'environnement
gunicorn==23.0.0           # Serveur WSGI
whitenoise==6.8.2          # Fichiers statiques
django-redis==5.4.0        # Cache Redis
xhtml2pdf==0.2.16          # Génération PDF
scikit-learn==1.6.1        # Machine Learning
...
```

### `Dockerfile` - L'image Docker
**Rôle** : Instructions pour construire l'image Docker de l'application

**Ce qu'il fait** :
1. Part d'une image Python 3.12
2. Installe les dépendances système (PostgreSQL client, etc.)
3. Copie le code de l'application
4. Installe les dépendances Python
5. Configure l'utilisateur non-root (sécurité)
6. Définit la commande de démarrage (Gunicorn)

### `docker-compose.yml` - L'orchestration
**Rôle** : Définit et orchestre tous les services Docker

**Services définis** :
- `db` → PostgreSQL (base de données)
- `redis` → Redis (cache et sessions)
- `web` → Django + Gunicorn (application)
- `nginx` → Nginx (serveur web)

**Avantage** : Un seul `docker-compose up` lance tout !

---

**Suite dans DOCUMENTATION_SOUTENANCE_PARTIE3.md**

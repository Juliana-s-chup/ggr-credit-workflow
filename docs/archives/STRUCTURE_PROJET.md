# 📁 STRUCTURE DU PROJET GGR CREDIT WORKFLOW

**Application Django de Gestion des Demandes de Crédit Bancaire**

---

## 🏗️ STRUCTURE GLOBALE

```
ggr-credit-workflow/
├── 📂 core/                    # Configuration Django
├── 📂 suivi_demande/          # Application principale
├── 📂 templates/              # Templates HTML
├── 📂 static/                 # Fichiers statiques (CSS, JS, images)
├── 📂 staticfiles/            # Fichiers statiques collectés (production)
├── 📂 media/                  # Fichiers uploadés (documents clients)
├── 📂 logs/                   # Fichiers de logs
├── 📂 docs/                   # Documentation complète
├── 📂 venv/                   # Environnement virtuel Python
├── 📄 manage.py               # Script de gestion Django
├── 📄 requirements.txt        # Dépendances Python
├── 📄 .env                    # Variables d'environnement
└── 📄 README_PROFESSIONNEL.md # Documentation principale
```

---

## 📂 DÉTAIL PAR DOSSIER

### 1. core/ - Configuration Django

```
core/
├── settings/
│   ├── __init__.py
│   ├── base.py              # Settings communs
│   ├── client.py            # Portail client (port 8001)
│   └── pro.py               # Portail professionnel (port 8002)
├── __init__.py
├── asgi.py                  # Configuration ASGI
├── urls.py                  # URLs racine
└── wsgi.py                  # Configuration WSGI
```

**Rôle** : Configuration centrale de Django (settings, URLs racine, WSGI/ASGI)

**Fichiers clés** :
- `settings/base.py` : Configuration commune (BDD, apps, middleware, templates)
- `settings/client.py` : Configuration portail client (port 8001)
- `settings/pro.py` : Configuration portail professionnel (port 8002)
- `urls.py` : Routage principal vers l'app suivi_demande

---

### 2. suivi_demande/ - Application Principale

```
suivi_demande/
├── migrations/              # Migrations de base de données
│   ├── 0001_initial.py
│   ├── 0002_dossiercredit_archived_at_dossiercredit_archived_by.py
│   ├── 0003_canevasproposition.py
│   └── ...
│
├── views_modules/           # Vues modulaires (refactoring)
│   ├── __init__.py
│   ├── base.py             # Vues de base (home, login, signup)
│   ├── dossiers.py         # Gestion des dossiers
│   ├── dashboard.py        # Dashboards par rôle
│   ├── workflow.py         # Transitions de statut
│   ├── notifications.py    # Gestion des notifications
│   └── ajax.py             # Endpoints AJAX
│
├── app_tests/              # Tests automatisés
│   ├── test_negative_cases.py
│   └── test_transitions_notifications.py
│
├── management/             # Commandes Django custom
│   └── commands/
│
├── __init__.py
├── admin.py                # Interface d'administration Django
├── apps.py                 # Configuration de l'app
├── constants.py            # Constantes du projet
├── decorators.py           # Décorateurs personnalisés
├── forms.py                # Formulaires généraux
├── forms_demande.py        # Formulaires wizard (étapes 1-2)
├── forms_demande_extra.py  # Formulaires wizard (étapes 3-4)
├── logging_config.py       # Configuration du logging
├── models.py               # Modèles de données (8 modèles)
├── permissions.py          # Logique de permissions
├── urls.py                 # Routes de l'application
├── utils.py                # Fonctions utilitaires
└── views.py                # Vues (legacy, avant refactoring)
```

**Rôle** : Cœur de l'application (logique métier, modèles, vues, formulaires)

**Fichiers clés** :
- `models.py` : 8 modèles (User, UserProfile, DossierCredit, CanevasProposition, etc.)
- `views_modules/` : Vues organisées par thématique
- `forms*.py` : Formulaires de saisie et validation
- `constants.py` : Constantes métier (rôles, statuts, limites)
- `decorators.py` : Décorateurs de sécurité (@login_required, @transition_allowed)

---

### 3. templates/ - Templates HTML

```
templates/
├── base.html                # Template de base (héritage)
│
├── accounts/               # Authentification
│   ├── login.html
│   ├── signup.html
│   ├── signup_client.html
│   └── pending_approval.html
│
├── suivi_demande/          # Pages principales
│   ├── home.html
│   ├── dashboard_client.html
│   ├── dashboard_gestionnaire.html
│   ├── dashboard_analyste.html
│   ├── dashboard_responsable_ggr.html
│   ├── dashboard_boe.html
│   ├── dashboard_admin.html
│   ├── my_applications.html
│   ├── dossier_detail.html
│   ├── notifications.html
│   ├── demande_step1.html
│   ├── demande_step2.html
│   ├── demande_step3.html
│   ├── demande_step4.html
│   └── ...
│
├── emails/                 # Templates d'emails
│   ├── dossier_a_traiter.html
│   ├── dossier_update_client.html
│   └── retour_client.html
│
├── pdf/                    # Templates PDF
│   └── proposition.html
│
└── portail_client/         # Portail client spécifique
    └── login.html
```

**Rôle** : Présentation (HTML, structure des pages)

**Organisation** :
- Héritage de `base.html` pour cohérence
- Séparation par fonctionnalité (accounts, suivi_demande, emails, pdf)
- Templates responsive (Bootstrap 5)

---

### 4. static/ - Fichiers Statiques

```
static/
├── core/
│   └── css/
│
├── css/
│   └── charte_graphique.css    # Styles personnalisés
│
└── suivi_demande/
    └── img/                     # Images de l'application
```

**Rôle** : CSS, JavaScript, images (avant collecte)

**Note** : En production, ces fichiers sont collectés dans `staticfiles/` via `collectstatic`

---

### 5. staticfiles/ - Fichiers Statiques Collectés

```
staticfiles/
├── admin/                   # Fichiers admin Django
├── css/                     # CSS collectés
├── js/                      # JavaScript collectés
└── img/                     # Images collectées
```

**Rôle** : Fichiers statiques optimisés pour la production (WhiteNoise)

**Génération** : `python manage.py collectstatic`

---

### 6. media/ - Fichiers Uploadés

```
media/
└── documents/              # Documents clients (CNI, fiches de paie, etc.)
    ├── DOS-2024-001_CNI.pdf
    ├── DOS-2024-001_Fiche_Paie_1.pdf
    └── ...
```

**Rôle** : Stockage des fichiers uploadés par les utilisateurs

**Sécurité** :
- Validation du type (PDF, JPG, PNG)
- Taille max : 5 MB
- Accès contrôlé par permissions

---

### 7. logs/ - Fichiers de Logs

```
logs/
├── general.log             # Logs généraux
├── debug.log               # Logs de débogage
├── error.log               # Logs d'erreurs
├── security.log            # Logs de sécurité
└── workflow.log            # Logs du workflow
```

**Rôle** : Traçabilité et débogage

**Configuration** : Rotation automatique (10 fichiers de 10 MB)

---

### 8. docs/ - Documentation

```
docs/
├── 📄 README_DOCUMENTATION.md
├── 📄 INDEX_DOCUMENTATION.md
│
├── 📋 Cahier des charges (3 parties)
│   ├── CDC_PARTIE1_PRESENTATION.md
│   ├── CDC_PARTIE2_EXIGENCES.md
│   └── CDC_PARTIE3_PLANIFICATION.md
│
├── 📚 Documentation fonctionnelle
│   ├── DOCUMENTATION_FONCTIONNELLE_COMPLETE.md
│   ├── CONTEXTE_PROJET_MEMOIRE.md
│   └── 01_AUTHENTIFICATION_GESTION_UTILISATEURS.md
│
├── 🏗️ Documentation technique
│   ├── ARCHITECTURE_TECHNIQUE_DJANGO.md
│   ├── MODELE_DONNEES_BDD.md
│   ├── QUALITE_CODE_BONNES_PRATIQUES.md
│   └── TESTS_QUALITE_LOGICIELLE.md
│
├── 📖 Guides utilisateurs
│   ├── GUIDE_UTILISATEUR.md
│   ├── GUIDE_DEPLOIEMENT.md
│   └── DEMARRAGE_RAPIDE.md
│
└── 📦 Archives
    └── archives/
```

**Rôle** : Documentation complète du projet (60+ pages)

**Contenu** :
- Cahier des charges (60 pages)
- Documentation fonctionnelle (50 pages)
- Documentation technique (50 pages)
- Guides utilisateurs (30 pages)

---

## 📄 FICHIERS RACINE

### Fichiers de configuration

| Fichier | Description |
|---------|-------------|
| `manage.py` | Script de gestion Django (runserver, migrate, etc.) |
| `requirements.txt` | Dépendances Python (Django, PostgreSQL, etc.) |
| `.env` | Variables d'environnement (SECRET_KEY, DB_PASSWORD) |
| `.env.example` | Exemple de fichier .env |
| `.gitignore` | Fichiers ignorés par Git |

### Scripts PowerShell

| Fichier | Description |
|---------|-------------|
| `start_portals.ps1` | Démarrage des 2 portails (client + pro) |
| `start_portals_simple.ps1` | Version simplifiée |
| `start_server.bat` | Démarrage serveur (Windows) |
| `nettoyer_projet.ps1` | Nettoyage du projet |
| `organiser_docs.ps1` | Organisation de la documentation |

### Documentation principale

| Fichier | Description |
|---------|-------------|
| `README_PROFESSIONNEL.md` | README principal du projet |
| `DEMARRAGE_RAPIDE.md` | Guide de démarrage rapide |
| `INDEX_DOCUMENTATION.md` | Index de toute la documentation |

---

## 🗂️ MODÈLES DE DONNÉES (8 modèles)

### Dans suivi_demande/models.py

```python
1. User (Django built-in)           # Utilisateurs
2. UserProfile                      # Profils utilisateurs (rôle, téléphone, etc.)
3. DossierCredit                    # Dossiers de crédit
4. CanevasProposition               # Propositions d'analyste
5. PieceJointe                      # Documents uploadés
6. JournalAction                    # Historique des actions
7. Notification                     # Notifications utilisateurs
8. Commentaire                      # Commentaires sur dossiers
```

**Relations** :
- User (1) ↔ (1) UserProfile
- User (1) ↔ (N) DossierCredit [client]
- DossierCredit (1) ↔ (1) CanevasProposition
- DossierCredit (1) ↔ (N) PieceJointe
- DossierCredit (1) ↔ (N) JournalAction
- DossierCredit (1) ↔ (N) Commentaire
- User (1) ↔ (N) Notification

---

## 🔧 TECHNOLOGIES UTILISÉES

### Backend

| Technologie | Version | Utilisation |
|-------------|---------|-------------|
| Python | 3.12 | Langage principal |
| Django | 5.2.6 | Framework web |
| PostgreSQL | 14+ | Base de données |
| Gunicorn | 20.1+ | Serveur WSGI |
| WhiteNoise | 6.11.0 | Fichiers statiques |
| xhtml2pdf | 0.2.17 | Génération PDF |

### Frontend

| Technologie | Version | Utilisation |
|-------------|---------|-------------|
| HTML5 | - | Structure |
| CSS3 | - | Styles |
| JavaScript | ES6+ | Interactivité |
| Bootstrap | 5.3 | Framework CSS |

---

## 📊 STATISTIQUES DU PROJET

### Code source

| Métrique | Valeur |
|----------|--------|
| Applications Django | 1 (suivi_demande) |
| Modèles | 8 |
| Vues | 30+ |
| Templates | 40+ |
| Formulaires | 10+ |
| Migrations | 6 |
| Tests | 75 |
| Lignes de code Python | ~8000 |

### Documentation

| Type | Pages |
|------|-------|
| Cahier des charges | 60 |
| Documentation fonctionnelle | 50 |
| Documentation technique | 50 |
| Guides utilisateurs | 30 |
| **TOTAL** | **190+** |

### Fichiers

| Type | Nombre |
|------|--------|
| Fichiers Python (.py) | 50+ |
| Templates HTML | 40+ |
| Fichiers CSS | 5+ |
| Fichiers JavaScript | 3+ |
| Fichiers Markdown (.md) | 25+ |
| **TOTAL** | **120+** |

---

## 🚀 COMMANDES PRINCIPALES

### Développement

```bash
# Activer l'environnement virtuel
.\venv\Scripts\activate

# Lancer le serveur de développement
python manage.py runserver

# Lancer les 2 portails
.\start_portals_simple.ps1

# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic
```

### Tests

```bash
# Lancer tous les tests
python manage.py test suivi_demande

# Lancer les tests avec couverture
coverage run --source='.' manage.py test suivi_demande
coverage report
coverage html
```

### Production

```bash
# Collecter les statiques
python manage.py collectstatic --noinput

# Lancer avec Gunicorn
gunicorn core.wsgi:application
```

---

## 🔐 SÉCURITÉ

### Mesures implémentées

- ✅ Protection CSRF (Django)
- ✅ Protection XSS (échappement automatique)
- ✅ Protection SQL Injection (ORM)
- ✅ Mots de passe hashés (PBKDF2)
- ✅ RBAC (Role-Based Access Control)
- ✅ Isolation des données par client
- ✅ Validation des uploads (type, taille)
- ✅ Logging de sécurité complet
- ✅ HTTPS en production
- ✅ Sessions sécurisées (30 min timeout)

---

## 📈 WORKFLOW DE DÉVELOPPEMENT

### 1. Développement local
```
Développement → Tests → Commit → Push
```

### 2. Déploiement
```
Pull → Migrations → Collectstatic → Restart Gunicorn
```

### 3. Maintenance
```
Logs → Monitoring → Backups → Updates
```

---

## 📞 CONTACTS ET SUPPORT

**Développeur** : Juliana  
**Projet** : GGR Credit Workflow  
**Type** : Application Django de gestion de crédit bancaire  
**Statut** : En production  
**Version** : 1.0

---

**Structure du projet générée le 4 novembre 2025**

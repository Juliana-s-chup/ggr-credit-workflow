# 🏦 GGR Credit Workflow - Système de Gestion de Crédits

[![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)

Système professionnel de gestion des demandes de crédit avec workflow complet, portails séparés (client/professionnel), et traçabilité complète.

---

## 📋 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Documentation](#documentation)

---

## ✨ Fonctionnalités

### Portail Client
- ✅ Inscription et authentification
- ✅ Wizard de demande de crédit (4 étapes)
- ✅ Suivi en temps réel du dossier
- ✅ Notifications automatiques
- ✅ Historique des demandes

### Portail Professionnel
- ✅ Dashboards par rôle (Gestionnaire, Analyste, Responsable GGR, BOE)
- ✅ Workflow complet de traitement
- ✅ Gestion des documents
- ✅ Canevas de proposition NOKI NOKI
- ✅ Journal des actions (audit trail)
- ✅ Génération de PDF
- ✅ Statistiques et rapports

### Sécurité
- ✅ Contrôle d'accès par rôle (RBAC)
- ✅ Authentification sécurisée
- ✅ Protection CSRF
- ✅ Validation des données
- ✅ Logging complet

---

## 🏗️ Architecture

### Stack Technique

```
Backend:
- Django 5.2.6 (Framework web Python)
- PostgreSQL 14+ (Base de données)
- WhiteNoise (Fichiers statiques)
- xhtml2pdf (Génération PDF)

Frontend:
- HTML5 / CSS3
- JavaScript vanilla
- Bootstrap (UI Framework)

Déploiement:
- Gunicorn (WSGI server)
- Nginx (Reverse proxy)
```

### Structure du Projet

```
ggr-credit-workflow/
├── core/                          # Configuration Django
│   ├── settings/
│   │   ├── base.py               # Settings communs
│   │   ├── client.py             # Portail client
│   │   └── pro.py                # Portail professionnel
│   ├── urls.py
│   └── wsgi.py
│
├── suivi_demande/                # Application principale
│   ├── models.py                 # Modèles de données
│   ├── views.py                  # Vues (à diviser)
│   ├── forms.py                  # Formulaires
│   ├── urls.py                   # Routes
│   ├── admin.py                  # Interface admin
│   ├── decorators.py             # Contrôle d'accès
│   ├── permissions.py            # Permissions
│   ├── constants.py              # Constantes
│   ├── logging_config.py         # Configuration logging
│   ├── tests/                    # Tests unitaires
│   │   ├── test_models.py
│   │   ├── test_permissions.py
│   │   └── test_workflow.py
│   └── templates/                # Templates HTML
│
├── templates/                     # Templates globaux
├── static/                        # Fichiers statiques
├── media/                         # Fichiers uploadés
├── logs/                          # Logs applicatifs
├── requirements.txt               # Dépendances Python
└── manage.py                      # CLI Django
```

### Modèle de Données

**Entités principales** :
- `User` : Utilisateurs du système
- `UserProfile` : Profils avec rôles
- `DossierCredit` : Dossiers de demande
- `CanevasProposition` : Propositions de crédit
- `PieceJointe` : Documents attachés
- `JournalAction` : Historique des actions
- `Notification` : Notifications utilisateurs

---

## 🚀 Installation

### Prérequis

- Python 3.10+
- PostgreSQL 14+
- pip
- virtualenv (recommandé)

### Installation locale

```bash
# 1. Cloner le projet
git clone https://github.com/votre-repo/ggr-credit-workflow.git
cd ggr-credit-workflow

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer la base de données PostgreSQL
createdb credit_db

# 5. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# 6. Appliquer les migrations
python manage.py migrate

# 7. Créer un superutilisateur
python manage.py createsuperuser

# 8. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 9. Lancer le serveur de développement
python manage.py runserver
```

### Accès

- **Portail Client** : http://localhost:8001
- **Portail Professionnel** : http://localhost:8002
- **Admin Django** : http://localhost:8000/admin

---

## ⚙️ Configuration

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

# Sécurité (Production)
ALLOWED_HOSTS=localhost,127.0.0.1,votre-domaine.com
CSRF_TRUSTED_ORIGINS=https://votre-domaine.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Logging

Les logs sont configurés dans `core/settings/base.py` :
- **Console** : Affichage temps réel
- **Fichier** : `logs/django.log` (rotation automatique, max 10MB)

---

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
python manage.py test suivi_demande

# Tests spécifiques
python manage.py test suivi_demande.tests.test_models
python manage.py test suivi_demande.tests.test_permissions
python manage.py test suivi_demande.tests.test_workflow

# Avec couverture
coverage run --source='.' manage.py test suivi_demande
coverage report
coverage html  # Rapport HTML dans htmlcov/
```

### Tests existants

- ✅ **test_models.py** : Tests des modèles (UserProfile, DossierCredit, Canevas, etc.)
- ✅ **test_permissions.py** : Tests des permissions et contrôle d'accès
- ✅ **test_workflow.py** : Tests des transitions de workflow

**Couverture actuelle** : ~40% (objectif : 80%+)

---

## 📦 Déploiement

### Production avec Gunicorn + Nginx

```bash
# 1. Installer Gunicorn
pip install gunicorn

# 2. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 3. Lancer Gunicorn
gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

### Configuration Nginx

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Checklist de production

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` sécurisée (variable d'environnement)
- [ ] `ALLOWED_HOSTS` configuré
- [ ] HTTPS activé
- [ ] Base de données PostgreSQL
- [ ] Fichiers statiques collectés
- [ ] Logs configurés
- [ ] Backups automatiques
- [ ] Monitoring activé

---

## 📚 Documentation

### Pour les développeurs

- [Guide des bonnes pratiques](GUIDE_BONNES_PRATIQUES_DJANGO.md)
- [Rapport d'améliorations](RAPPORT_AMELIORATIONS_PROJET.md)
- [Documentation API](docs/API.md) (à créer)

### Pour les utilisateurs

- [Manuel utilisateur Client](docs/MANUEL_CLIENT.md) (à créer)
- [Manuel utilisateur Professionnel](docs/MANUEL_PRO.md) (à créer)

---

## 🤝 Contribution

### Workflow Git

```bash
# 1. Créer une branche
git checkout -b feature/ma-fonctionnalite

# 2. Faire vos modifications
git add .
git commit -m "feat: ajout de ma fonctionnalité"

# 3. Pousser et créer une PR
git push origin feature/ma-fonctionnalite
```

### Standards de code

- **PEP 8** pour Python
- **Docstrings** obligatoires
- **Tests** pour chaque nouvelle fonctionnalité
- **Commits** en anglais, format conventionnel

---

## 📝 Licence

Ce projet est sous licence propriétaire. Tous droits réservés.

---

## 👥 Équipe

- **Développeur Principal** : [Votre Nom]
- **Directeur de Mémoire** : [Nom du directeur]
- **Institution** : [Nom de l'université]

---

## 📞 Support

Pour toute question ou problème :
- **Email** : support@ggr-credit.cg
- **Issues** : [GitHub Issues](https://github.com/votre-repo/issues)

---

**Version** : 1.0.0  
**Dernière mise à jour** : 4 novembre 2025

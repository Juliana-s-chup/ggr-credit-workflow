# GGR Credit Workflow

**Systeme de gestion des dossiers de credit bancaire**
*Projet de fin d'etude - NGUIMBI Juliana*

---

## Description

Application web Django pour la gestion complete du cycle de vie des dossiers de credit bancaire. Le systeme propose **deux portails distincts** (Client et Professionnel) avec un workflow de validation multi-niveaux, une gestion des roles (RBAC), un module d'analytics et de prediction de risque par Machine Learning.

### Fonctionnalites principales

- **Portail Client** : consultation et suivi de l'avancement des dossiers, notifications
- **Portail Professionnel** : creation et traitement des dossiers, validation hierarchique, dashboards par role
- **Workflow** : circuit de validation BPMN a 9 statuts avec transitions controlees
- **Canevas de proposition** : formulaire complet aligne sur les standards bancaires
- **Securite** : RBAC, journalisation des actions, middleware portail, validation des fichiers
- **Analytics** : dashboards KPI, rapports statistiques, export Excel contextuel par role
- **ML** : prediction de risque credit (RandomForest, scikit-learn)

---

## Roles utilisateurs

| Role | Description | Portail |
|------|-------------|---------|
| **Client** | Consulte et suit l'avancement de son dossier de credit | Client |
| **Gestionnaire** | Cree les dossiers pour les clients, verifie et transmet a l'analyste | Pro |
| **Analyste credit** | Evalue le risque et prepare l'avis technique | Pro |
| **Responsable GGR** | Valide les dossiers, acces aux rapports et analytics | Pro |
| **BOE** | Back Office Engagement, gere la liberation des fonds | Pro |
| **Super Admin** | Administration complete (utilisateurs, roles, systeme) | Pro |

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| **Backend** | Django 5.2, Python 3.12+ |
| **Base de donnees** | PostgreSQL 16 |
| **Frontend** | HTML5, CSS3 (design system custom), JavaScript, Bootstrap 5 |
| **Analytics** | Pandas, NumPy, Openpyxl, Chart.js |
| **ML** | scikit-learn, joblib |
| **PDF** | xhtml2pdf, ReportLab |
| **Serveur** | Nginx (reverse proxy) + Gunicorn |
| **Conteneurisation** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Tests** | pytest, pytest-django, coverage, factory-boy |

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │    Nginx    │     │   Django    │
│  (Browser)  │────>│   (Proxy)   │────>│    App      │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
              ┌─────▼─────┐            ┌───────▼───────┐          ┌───────▼───────┐
              │   core    │            │ suivi_demande │          │   analytics   │
              │ (config)  │            │   (metier)    │          │  (reporting)  │
              └───────────┘            └───────────────┘          └───────────────┘
                                               │
                                        ┌──────▼──────┐
                                        │ PostgreSQL  │
                                        │    (DB)     │
                                        └─────────────┘
```

Le projet suit le pattern **MVT (Model-View-Template)** de Django avec une **couche service** pour la logique metier.

---

## Workflow de traitement

```
[NOUVEAU] ──> [TRANSMIS_RESP_GEST] ──> [TRANSMIS_ANALYSTE] ──> [EN_COURS_ANALYSE]
                                                                       │
                                                                       ▼
                                                            [EN_COURS_VALIDATION_GGR]
                                                                       │
                                                            [EN_ATTENTE_DECISION_DG]
                                                                       │
                                                    ┌──────────────────┼──────────────────┐
                                                    ▼                                     ▼
                                          [APPROUVE_ATTENTE_FONDS]                    [REFUSE]
                                                    │
                                                    ▼
                                              [FONDS_LIBERE]
```

---

## Structure du projet

```
ggr-credit-workflow/
├── core/                        # Configuration Django
│   ├── settings/                # Settings par environnement
│   │   ├── base.py              #   Settings communs
│   │   ├── dev.py               #   Developpement
│   │   ├── prod.py              #   Production
│   │   ├── client.py            #   Portail client (port 8001)
│   │   └── pro.py               #   Portail pro (port 8002)
│   ├── urls.py                  # Routage principal
│   ├── security.py              # Decorateurs et RBAC
│   ├── monitoring.py            # Monitoring applicatif
│   └── middleware/               # Middlewares custom
│
├── suivi_demande/               # Application metier principale
│   ├── models.py                # Modeles (DossierCredit, UserProfile, etc.)
│   ├── views.py                 # Vues principales
│   ├── views_portals.py         # Vues specifiques aux portails
│   ├── views_admin.py           # Vues administration utilisateurs
│   ├── views_canevas.py         # Vues canevas de proposition
│   ├── views_documents.py       # Upload/gestion des documents
│   ├── views_modules/           # Vues modulaires (dashboard, workflow, etc.)
│   ├── services/                # Couche service (logique metier)
│   │   └── dossier_service.py   #   Filtrage et gestion des dossiers
│   ├── forms.py                 # Formulaire inscription
│   ├── forms_demande.py         # Formulaires wizard (etapes 1 a 4)
│   ├── forms_canevas.py         # Formulaire canevas de proposition
│   ├── forms_autorisation.py    # Formulaire autorisation ponctuelle
│   ├── urls.py                  # URLs communes
│   ├── urls_client.py           # URLs portail client
│   ├── urls_pro.py              # URLs portail professionnel
│   ├── permissions.py           # Permissions et transitions
│   ├── validators.py            # Validation fichiers et donnees
│   ├── decorators.py            # Decorateurs metier
│   ├── constants.py             # Constantes (montants, delais)
│   ├── utils.py                 # Utilitaires (notifications, roles, helpers)
│   ├── logging_config.py        # Helpers de logging metier
│   ├── ml/                      # Machine Learning (credit scoring)
│   ├── tests/                   # Tests (7 fichiers)
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_forms.py
│   │   ├── test_workflow.py
│   │   ├── test_permissions.py
│   │   ├── test_security.py
│   │   └── test_integration.py
│   └── management/commands/     # Commandes Django
│       ├── create_superadmin.py
│       ├── seed_demo.py
│       └── train_scoring_model.py
│
├── analytics/                   # Module analytics et reporting
│   ├── models.py                # StatistiquesDossier, PredictionRisque
│   ├── views.py                 # Dashboard, rapports, predictions
│   ├── services.py              # Calculs stats, ML, export Excel
│   └── urls.py
│
├── templates/                   # Templates HTML
│   ├── base.html                # Template de base
│   ├── includes/                # Partials (_navbar, _sidebar, _footer)
│   ├── suivi_demande/           # Templates metier (dashboards, wizard, etc.)
│   ├── analytics/               # Templates analytics
│   ├── portail_pro/             # Templates specifiques portail pro
│   ├── portail_client/          # Templates specifiques portail client
│   ├── accounts/                # Templates authentification
│   └── emails/                  # Templates emails
│
├── static/                      # Fichiers statiques
│   ├── css/                     # Design system, charte graphique
│   └── js/src/modules/          # Modules JS (navbar, sidebar, alerts)
│
├── docs/                        # Documentation
│   ├── architecture/            # Schemas techniques
│   ├── diagrammes/              # BPMN, ERD, UML
│   ├── guides/                  # Guides demarrage et utilisation
│   ├── memoire/                 # Documents du memoire
│   └── soutenance/              # Documentation de soutenance
│
├── scripts/                     # Scripts utilitaires
├── nginx/                       # Configuration Nginx
├── Dockerfile                   # Image Docker production
├── docker-compose.yml           # Orchestration Docker
├── requirements.txt             # Dependances Python
├── pytest.ini                   # Configuration tests
├── Makefile                     # Commandes make
└── manage.py
```

---

## Installation rapide

### 1. Cloner le projet
```bash
git clone https://github.com/<votre-compte>/ggr-credit-workflow.git
cd ggr-credit-workflow
```

### 2. Environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 3. Dependances
```bash
pip install -r requirements.txt
```

### 4. Configuration
```bash
copy env.example .env        # Windows
# cp env.example .env        # Linux/Mac
```
Editer `.env` avec vos parametres : `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`.

### 5. Base de donnees
```bash
python manage.py migrate
python manage.py create_superadmin
python manage.py seed_demo              # Optionnel : donnees de demonstration
```

### 6. Lancer les portails
```bash
# Portail Client (port 8001)
python manage.py runserver 8001 --settings=core.settings.client

# Portail Professionnel (port 8002)
python manage.py runserver 8002 --settings=core.settings.pro
```

### Acces aux portails
- **Portail Client** : http://client.ggr-credit.local:8001/client/login/
- **Portail Pro** : http://pro.ggr-credit.local:8002/pro/login/

---

## Docker

```bash
docker-compose up -d        # Production
docker-compose -f docker-compose.dev.yml up -d   # Developpement
```

---

## Tests

```bash
pytest                       # Tous les tests
pytest --cov=suivi_demande   # Avec couverture
python manage.py test        # Alternative Django
```

Le projet contient **7 fichiers de tests** couvrant : models, forms, views, permissions, security, integration, workflow.

---

## Documentation

Voir le dossier `docs/` pour la documentation complete :
- `docs/guides/` - Guides de demarrage et d'utilisation
- `docs/architecture/` - Schemas et diagrammes techniques
- `docs/diagrammes/` - BPMN, ERD, UML
- `docs/memoire/` - Documents du memoire
- `docs/soutenance/` - Documentation de soutenance

---

## Licence

MIT - Voir le fichier `LICENSE`

---

**Auteur** : NGUIMBI Juliana | **Projet academique** - 2025

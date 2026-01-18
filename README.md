# GGR Credit Workflow

**Application de gestion des dossiers de credit - Projet de fin d'etude**

---

## Description

Application web Django pour la gestion complete des dossiers de credit bancaire. Elle propose deux portails distincts (Client et Professionnel) avec un workflow de validation multi-niveaux et une gestion des roles (RBAC).

### Fonctionnalites principales

- **Portail Client** : depot de demande, suivi en temps reel, upload de documents
- **Portail Professionnel** : traitement des dossiers, validation hierarchique, tableau de bord
- **Workflow** : circuit de validation a 6 etapes avec notifications
- **Securite** : authentification, autorisation par role, journalisation des actions
- **Analytics** : tableaux de bord et indicateurs de performance

---

## Roles utilisateurs

| Role | Description |
|------|-------------|
| **Client** | Depose une demande de credit et suit son avancement |
| **Gestionnaire** | Recoit et verifie les dossiers, transmet a l'analyste |
| **Analyste credit** | Evalue le risque et prepare l'avis technique |
| **Responsable GGR** | Valide les dossiers avant decision finale |
| **BOE** | Back Office Engagement, gere la liberation des fonds |
| **Super Admin** | Administration complete du systeme |

---

## Stack technique

- **Backend** : Django 5, Python 3.12
- **Base de donnees** : PostgreSQL 16
- **Frontend** : HTML/CSS, JavaScript, Bootstrap
- **Serveur** : Nginx (reverse proxy) + Gunicorn
- **Conteneurisation** : Docker, Docker Compose

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │    Nginx    │     │   Django    │
│  (Browser)  │────▶│   (Proxy)   │────▶│    App      │
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

---

## Workflow de traitement

```
[NOUVEAU] ──▶ [GESTIONNAIRE] ──▶ [ANALYSTE] ──▶ [RESPONSABLE GGR] ──▶ [DECISION DG]
                                                                            │
                                                        ┌───────────────────┼───────────────────┐
                                                        ▼                                       ▼
                                                   [APPROUVE]                              [REFUSE]
                                                        │
                                                        ▼
                                                 [FONDS LIBERE]
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
Editer `.env` avec vos parametres (DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY).

### 5. Base de donnees
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Lancer le serveur
```bash
python manage.py runserver
```

### Acces aux portails
- **Portail Client** : http://localhost:8000/client/login/
- **Portail Pro** : http://localhost:8000/pro/login/

---

## Docker (optionnel)

```bash
docker-compose up -d
```

---

## Tests

```bash
pytest
# ou
python manage.py test
```

Le projet contient 7 fichiers de tests couvrant : models, forms, views, permissions, security, integration, workflow.

---

## Structure du projet

```
ggr-credit-workflow/
├── core/                 # Configuration Django (settings, urls)
├── suivi_demande/        # Application metier principale
│   ├── models.py         # Modeles de donnees
│   ├── views.py          # Logique de presentation
│   ├── forms.py          # Formulaires
│   └── tests/            # Tests unitaires et integration
├── analytics/            # Module d'analyse et reporting
├── templates/            # Templates HTML
├── static/               # CSS, JS, images
├── docs/                 # Documentation complete
│   ├── guides/           # Guides utilisateur
│   ├── architecture/     # Schemas techniques
│   └── memoire/          # Documents du memoire
├── scripts/              # Scripts utilitaires
└── nginx/                # Configuration Nginx
```

---

## Documentation

Voir le dossier `docs/` pour la documentation complete :
- `docs/README.md` - Index de la documentation
- `docs/guides/` - Guides de demarrage et d'utilisation
- `docs/architecture/` - Schemas et diagrammes

---

## Licence

MIT - Voir le fichier `LICENSE`

---

**Projet academique - 2025**

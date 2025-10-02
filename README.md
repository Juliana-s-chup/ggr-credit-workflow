# GGR Credit Workflow

Application Django de gestion de dossiers de crédit (Crédit du Congo) avec rôles, transitions de workflow, notifications internes et envoi d’emails (console en dev).

## Prérequis
- Python 3.12+
- PostgreSQL 14+
- pip, venv

## Installation
```bash
# Cloner le dépôt
# git clone <repo-url>
# cd ggr-credit-workflow

# Créer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration
Le projet utilise `django-environ` et un fichier `.env` à la racine.

Exemple de `.env` (un `.env.example` est fourni):
```
SECRET_KEY=django-insecure-dev-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données PostgreSQL
db_name=credit_db
DB_USER=credit_user
DB_PASSWORD=<votre_mot_de_passe>
DB_HOST=127.0.0.1
DB_PORT=5434

# Emails (dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@ggr-credit.local
```

Créer la base PostgreSQL et l’utilisateur si besoin:
```sql
-- Exemple
CREATE USER credit_user WITH PASSWORD '***';
CREATE DATABASE credit_db OWNER credit_user;
```

Appliquer les migrations:
```bash
python manage.py migrate
```

## Démarrage
```bash
python manage.py runserver
```
Accès: http://127.0.0.1:8000/

## Authentification & Rôles
- Rôles supportés: `CLIENT`, `GESTIONNAIRE`, `ANALYSTE`, `RESPONSABLE_GGR`, `BOE`, `SUPER_ADMIN`.
- Un `UserProfile` relie l’utilisateur à un rôle.

## Dashboards
- `CLIENT`: ses propres dossiers.
- `GESTIONNAIRE`: dossiers au statut `NOUVEAU`.
- `ANALYSTE`: `TRANSMIS_ANALYSTE`, `EN_COURS_ANALYSE`.
- `RESPONSABLE_GGR`: `EN_COURS_VALIDATION_GGR`, `EN_ATTENTE_DECISION_DG`.
- `BOE`: `APPROUVE_ATTENTE_FONDS`.

## Transitions de workflow
- Gestionnaire: `transmettre_analyste`
- Analyste: `transmettre_ggr`, `retour_gestionnaire`
- Responsable GGR: `approuver`, `refuser`
- BOE: `liberer_fonds`

Les transitions sont validées par le décorateur `@transition_allowed`. Les actions sont accessibles via les dashboards et la page de détail du dossier.

## Notifications
- À chaque transition:
  - Notification au client (type `DOSSIER_MAJ`) + email console.
  - Notification aux prochains acteurs (type `DOSSIER_A_TRAITER`) + email console.
- Navbar: cloche avec badge, dropdown (5 dernières) et actions “Lu”/“Tout lire”.
- Pages:
  - `/notifications/` (liste)
  - `/notifications/mark-all/` (POST)
  - `/notifications/<pk>/mark/` (POST)

## Pièces jointes
- Upload sur la page détail (selon rôle/état). Validation côté serveur:
  - Extensions autorisées: `pdf`, `jpg`, `jpeg`, `png` (configurable via `.env`)
  - Taille max: 5 Mo par défaut (`UPLOAD_MAX_BYTES`)

## Données de démo (fixtures)
Une commande management permet de créer des comptes par rôle et des dossiers répartis sur plusieurs statuts.

```bash
# Créer les données de démo
python manage.py seed_demo

# Réinitialiser puis recréer la démo
python manage.py seed_demo --reset
```
Comptes créés:
- admin / admin (superuser)
- client1 / demo1234
- client2 / demo1234
- gest1 / demo1234
- an1 / demo1234
- resp1 / demo1234
- boe1 / demo1234

## Tests
```bash
python manage.py test core
```

## Structure clés
- `core/models.py`: modèles `DossierCredit`, `JournalAction`, `Notification`, `UserProfile`, enums des statuts et rôles.
- `core/views.py`: dashboards, transitions (`transition_dossier`), notifications et page détail.
- `core/permissions.py`: helpers d’autorisations (upload, flags de transitions).
- `core/decorators.py`: `role_required`, `transition_allowed`.
- `core/context_processors.py`: `unread_notifications_count`, `latest_notifications`.
- `templates/`: dashboards, page détail, notifications, base layout.

## Déploiement
- Changer `DEBUG=False` et définir `ALLOWED_HOSTS`.
- Configurer un backend email réel (SMTP) via `.env`.
- Utiliser un serveur d’app (gunicorn/uvicorn) + proxy (nginx). 
- Migrations automatiques et collectstatic si nécessaire.

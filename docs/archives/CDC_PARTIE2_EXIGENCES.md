# 📋 CAHIER DES CHARGES - PARTIE 2
## EXIGENCES TECHNIQUES ET NON FONCTIONNELLES

**Projet** : GGR Credit Workflow  
**Version** : 1.0 | **Date** : 4 novembre 2025

---

## 3. EXIGENCES TECHNIQUES

### 3.1 Architecture Django

#### Structure des applications

```
ggr-credit-workflow/
├── core/                          # Configuration Django
│   ├── settings/
│   │   ├── base.py               # Settings communs
│   │   ├── client.py             # Portail client (port 8001)
│   │   └── pro.py                # Portail pro (port 8002)
│   ├── urls.py                   # URLs racine
│   ├── wsgi.py                   # WSGI
│   └── asgi.py                   # ASGI
│
├── suivi_demande/                # Application principale
│   ├── models.py                 # 8 modèles
│   ├── views_modules/            # Vues modulaires
│   │   ├── base.py
│   │   ├── dossiers.py
│   │   ├── dashboard.py
│   │   ├── workflow.py
│   │   └── notifications.py
│   ├── forms.py                  # Formulaires
│   ├── urls.py                   # Routes
│   ├── admin.py                  # Interface admin
│   ├── decorators.py             # Décorateurs custom
│   ├── permissions.py            # Logique permissions
│   ├── constants.py              # Constantes
│   ├── logging_config.py         # Configuration logging
│   └── utils.py                  # Utilitaires
│
├── templates/                     # Templates HTML
│   ├── base.html
│   ├── suivi_demande/
│   ├── emails/
│   └── pdf/
│
├── static/                        # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/                         # Fichiers uploadés
└── logs/                          # Logs
```

#### Pattern MVT (Model-View-Template)

**Models** : Couche de données
- 8 modèles Django
- ORM pour abstraction SQL
- Relations OneToOne, ForeignKey
- Validation au niveau modèle

**Views** : Logique métier
- Vues basées sur fonctions
- Décorateurs pour permissions
- Gestion des formulaires
- Redirection selon le rôle

**Templates** : Présentation
- Héritage de templates
- Template tags Django
- Inclusion de partials
- Responsive design

### 3.2 Technologies utilisées

#### Backend

| Technologie | Version | Utilisation |
|-------------|---------|-------------|
| **Python** | 3.10+ | Langage principal |
| **Django** | 5.2.6 | Framework web |
| **PostgreSQL** | 14+ | Base de données |
| **Gunicorn** | 20.1+ | Serveur WSGI |
| **WhiteNoise** | 6.5+ | Fichiers statiques |

#### Frontend

| Technologie | Version | Utilisation |
|-------------|---------|-------------|
| **HTML5** | - | Structure |
| **CSS3** | - | Styles |
| **JavaScript** | ES6+ | Interactivité |
| **Bootstrap** | 5.3 | Framework CSS |

#### Outils de développement

| Outil | Utilisation |
|-------|-------------|
| **Git** | Contrôle de version |
| **pip** | Gestion dépendances Python |
| **virtualenv** | Environnement virtuel |
| **coverage** | Couverture de tests |

### 3.3 Choix techniques et justifications

#### Django Framework

**Justification** :
- Sécurité native (CSRF, XSS, SQL injection)
- Batteries included (ORM, auth, admin)
- Architecture MVT claire
- Communauté active
- Documentation exhaustive
- Scalabilité prouvée (Instagram, Pinterest)

#### PostgreSQL

**Justification** :
- Production-ready
- Support JSONB pour métadonnées
- Transactions robustes
- Performances sur gros volumes
- Concurrent access
- Open source

#### Architecture multi-portails

**Justification** :
- Séparation client/professionnel
- Configuration spécifique par portail
- Sécurité renforcée
- Évolutivité (ajout de portails)

#### Settings modulaires

**Justification** :
- Environnements séparés (dev, prod)
- Configuration par portail
- Facilite le déploiement
- Évite les erreurs

### 3.4 Contraintes techniques

**Hébergement** :
- Serveur local (interne à la banque)
- Ubuntu 20.04 LTS
- RAM : 8 GB
- CPU : 4 cœurs
- Disque : 50 GB SSD

**Réseau** :
- Intranet uniquement (sécurité)
- Accès VPN pour télétravail
- Bande passante : 1 Gbps

**Base de données** :
- PostgreSQL 14
- Backups quotidiens automatiques
- Réplication (optionnel)

**Navigateurs supportés** :
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

---

## 4. EXIGENCES NON FONCTIONNELLES

### 4.1 Sécurité

#### Authentification

**Exigences** :
- Mot de passe haché (PBKDF2 avec Django)
- Minimum 8 caractères
- Session sécurisée (30 min timeout)
- Logout automatique après inactivité
- Logging des connexions/déconnexions

**Implémentation** :
```python
# Django auth intégré
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # Vue protégée
```

#### Autorisation (RBAC)

**Exigences** :
- Contrôle d'accès par rôle
- Permissions granulaires
- Isolation des données (client ne voit que ses dossiers)
- Vérification à chaque action

**Implémentation** :
```python
# Décorateur custom
@transition_allowed
def transition_dossier(request, pk, action):
    # Vérifie automatiquement les permissions
```

#### Protection des données

**Exigences** :
- Protection CSRF activée
- Protection XSS (échappement automatique)
- Protection SQL injection (ORM)
- Validation des uploads (type, taille)
- HTTPS en production

**Validation uploads** :
- Types autorisés : PDF, JPG, PNG
- Taille max : 5 MB
- Vérification type MIME
- Stockage sécurisé

#### Gestion des erreurs

**Exigences** :
- Messages d'erreur clairs (pas de détails techniques)
- Logging de toutes les erreurs
- Page 404 personnalisée
- Page 500 personnalisée
- Pas de stack trace en production

### 4.2 Performance

#### Temps de réponse

| Type de page | Objectif |
|--------------|----------|
| Pages simples | < 1 seconde |
| Pages avec requêtes | < 2 secondes |
| Génération PDF | < 5 secondes |
| Upload fichier | < 10 secondes |

#### Optimisations appliquées

**Requêtes BDD** :
```python
# Éviter N+1 queries
dossiers = DossierCredit.objects.select_related(
    'client', 'acteur_courant'
).prefetch_related('pieces')
```

**Pagination** :
```python
# 25 items par page
from django.core.paginator import Paginator
paginator = Paginator(dossiers_list, 25)
```

**Index BDD** :
```python
class Meta:
    indexes = [
        models.Index(fields=['client', 'statut_agent']),
        models.Index(fields=['statut_agent', 'is_archived']),
    ]
```

**Cache** :
- WhiteNoise pour fichiers statiques
- Cache headers optimisés
- Compression automatique

#### Capacité

**Objectifs** :
- 500 utilisateurs simultanés
- 10 000 dossiers
- 50 000 documents
- 100 000 actions loggées

### 4.3 Ergonomie et UX

#### Principes UX

**Simplicité** :
- Maximum 3 clics pour toute action
- Navigation intuitive
- Wizard guidé pour la demande
- Messages clairs et explicites

**Cohérence** :
- Charte graphique uniforme
- Terminologie cohérente
- Comportements prévisibles
- Icônes standardisées

**Feedback** :
- Messages de confirmation
- Messages d'erreur explicites
- Indicateurs de progression
- Notifications en temps réel

#### Responsive Design

**Exigences** :
- Compatible desktop (1920×1080)
- Compatible tablette (768×1024)
- Compatible mobile (375×667)
- Adaptation automatique

**Implémentation** :
- Bootstrap 5.3 (grid system)
- Media queries CSS
- Images responsive
- Menu burger mobile

#### Accessibilité

**Exigences** :
- Contraste suffisant (WCAG AA)
- Taille de police lisible (16px min)
- Labels sur tous les champs
- Navigation au clavier possible

### 4.4 Disponibilité

**Objectif** : 99% de disponibilité

**Calcul** :
- 99% = 7,2 heures d'indisponibilité par mois
- Maintenance planifiée : Week-end
- Sauvegarde quotidienne : 2h du matin

**Mesures** :
- Monitoring du serveur
- Alertes automatiques
- Plan de reprise d'activité
- Backups automatiques

### 4.5 Maintenabilité du code

#### Structure modulaire

**Exigences** :
- Fichiers < 500 lignes
- Fonctions < 50 lignes
- Séparation des responsabilités
- Réutilisabilité du code

**Résultat** :
- views.py (2027 lignes) → 6 modules (< 600 lignes chacun)
- Code DRY (Don't Repeat Yourself)
- Fonctions helper réutilisables

#### Documentation

**Exigences** :
- Docstrings sur toutes les fonctions
- Commentaires sur le code complexe
- README complet
- Documentation technique
- Guide utilisateur

**Exemple** :
```python
def log_transition(dossier, action, user, from_status, to_status):
    """
    Log une transition de statut dans le workflow.
    
    Args:
        dossier (DossierCredit): Instance du dossier
        action (str): Action effectuée
        user (User): Utilisateur
        from_status (str): Statut de départ
        to_status (str): Statut d'arrivée
    """
```

#### Tests

**Exigences** :
- Couverture > 75%
- Tests unitaires
- Tests d'intégration
- Tests de sécurité

**Résultat** :
- 75 tests créés
- Couverture 75-80%
- 0 test échoué

### 4.6 Qualité du code

#### Conventions

**PEP 8** (Python) :
- Indentation : 4 espaces
- Longueur ligne : max 100 caractères
- Nommage : snake_case pour variables/fonctions

**Django Coding Style** :
- Imports ordonnés (stdlib, Django, tiers, locaux)
- Vues retournent toujours HttpResponse
- Templates héritent de base.html

#### Outils de qualité

**Linting** :
```bash
# Vérification du code
flake8 suivi_demande/
pylint suivi_demande/
```

**Formatage** :
```bash
# Formatage automatique
black suivi_demande/
```

#### Métriques

| Métrique | Objectif | Résultat |
|----------|----------|----------|
| Couverture tests | > 75% | 75-80% |
| Complexité cyclomatique | < 10 | < 8 |
| Duplication code | < 5% | < 3% |
| Lignes par fichier | < 500 | ✅ |

---

## 5. MODÈLE DE DONNÉES

### 5.1 Liste des tables et colonnes

#### Table `auth_user` (Django built-in)

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Clé primaire |
| username | VARCHAR(150) | UNIQUE, NOT NULL | Nom d'utilisateur |
| email | VARCHAR(254) | NULL | Email |
| password | VARCHAR(128) | NOT NULL | Hash mot de passe |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Compte actif |
| date_joined | TIMESTAMP | NOT NULL | Date inscription |

#### Table `suivi_demande_userprofile`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Clé primaire |
| user_id | INTEGER | FK, UNIQUE, NOT NULL | Lien vers user |
| full_name | VARCHAR(200) | NOT NULL | Nom complet |
| phone | VARCHAR(20) | NOT NULL | Téléphone |
| address | TEXT | NOT NULL | Adresse |
| role | VARCHAR(20) | NOT NULL | Rôle utilisateur |

**Rôles possibles** : CLIENT, GESTIONNAIRE, ANALYSTE, RESPONSABLE_GGR, BOE, SUPER_ADMIN

#### Table `suivi_demande_dossiercredit`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Clé primaire |
| reference | VARCHAR(50) | UNIQUE, NOT NULL | Référence unique |
| client_id | INTEGER | FK, NOT NULL | Client demandeur |
| produit | VARCHAR(100) | NOT NULL | Type de crédit |
| montant | DECIMAL(12,2) | NOT NULL, CHECK > 0 | Montant demandé |
| statut_agent | VARCHAR(50) | NOT NULL | Statut interne |
| statut_client | VARCHAR(50) | NOT NULL | Statut visible client |
| acteur_courant_id | INTEGER | FK, NULL | Acteur en charge |
| is_archived | BOOLEAN | NOT NULL, DEFAULT FALSE | Archivé |
| date_soumission | TIMESTAMP | NOT NULL | Date soumission |

#### Table `suivi_demande_canevasproposition`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Clé primaire |
| dossier_id | INTEGER | FK, UNIQUE, NOT NULL | Lien vers dossier |
| salaire_net_moyen_fcfa | DECIMAL(12,2) | NOT NULL | Salaire net |
| capacite_endettement_brute_fcfa | DECIMAL(12,2) | NULL | 40% salaire |
| capacite_endettement_nette_fcfa | DECIMAL(12,2) | NULL | Brute - crédits |
| proposition_montant_fcfa | DECIMAL(12,2) | NULL | Montant proposé |
| proposition_duree_mois | INTEGER | NULL | Durée proposée |
| proposition_taux_pourcent | DECIMAL(5,2) | NULL | Taux proposé |

#### Table `suivi_demande_piecejointe`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Clé primaire |
| dossier_id | INTEGER | FK, NOT NULL | Lien vers dossier |
| fichier | VARCHAR(100) | NOT NULL | Chemin fichier |
| type_piece | VARCHAR(50) | NOT NULL | Type document |
| taille | INTEGER | NOT NULL | Taille en octets |
| upload_at | TIMESTAMP | NOT NULL | Date upload |

#### Table `suivi_demande_journalaction`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Clé primaire |
| dossier_id | INTEGER | FK, NOT NULL | Lien vers dossier |
| action | VARCHAR(50) | NOT NULL | Type d'action |
| acteur_id | INTEGER | FK, NULL | Utilisateur |
| timestamp | TIMESTAMP | NOT NULL | Date/heure |
| de_statut | VARCHAR(50) | NULL | Statut départ |
| vers_statut | VARCHAR(50) | NULL | Statut arrivée |

#### Table `suivi_demande_notification`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Clé primaire |
| utilisateur_cible_id | INTEGER | FK, NOT NULL | Destinataire |
| type | VARCHAR(50) | NOT NULL | Type notification |
| titre | VARCHAR(200) | NOT NULL | Titre |
| message | TEXT | NOT NULL | Message |
| lu | BOOLEAN | NOT NULL, DEFAULT FALSE | Notification lue |
| created_at | TIMESTAMP | NOT NULL | Date création |

#### Table `suivi_demande_commentaire`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Clé primaire |
| dossier_id | INTEGER | FK, NOT NULL | Lien vers dossier |
| auteur_id | INTEGER | FK, NOT NULL | Auteur |
| message | TEXT | NOT NULL | Contenu |
| created_at | TIMESTAMP | NOT NULL | Date création |

### 5.2 Relations entre les entités

```
auth_user (1) ──── (1) userprofile
auth_user (1) ──── (N) dossiercredit [client]
auth_user (1) ──── (N) dossiercredit [acteur_courant]
dossiercredit (1) ──── (1) canevasproposition
dossiercredit (1) ──── (N) piecejointe
dossiercredit (1) ──── (N) journalaction
dossiercredit (1) ──── (N) commentaire
auth_user (1) ──── (N) notification
```

### 5.3 Schéma relationnel (ERD)

```
┌─────────────┐
│  auth_user  │
│  (Users)    │
├─────────────┤
│ PK id       │
│    username │
│    email    │
│    password │
└──────┬──────┘
       │ 1:1
       ▼
┌─────────────┐
│ userprofile │
├─────────────┤
│ PK id       │
│ FK user_id  │
│    role     │
└──────┬──────┘
       │ 1:N
       ▼
┌──────────────┐
│dossiercredit │◄────┐
├──────────────┤     │ 1:1
│ PK id        │     │
│    reference │     │
│ FK client_id │     │
│    montant   │     │
│    statut    │     │
└┬─┬─┬─┬───────┘     │
 │ │ │ │             │
 │ │ │ └─────────────┤
 │ │ │        ┌──────▼──────┐
 │ │ │        │ canevas     │
 │ │ │        │ proposition │
 │ │ │        ├─────────────┤
 │ │ │        │ PK id       │
 │ │ │        │ FK dossier  │
 │ │ │        │    salaire  │
 │ │ │        └─────────────┘
 │ │ │
 │ │ └─────────┐
 │ │    ┌──────▼──────┐
 │ │    │ piecejointe │
 │ │    ├─────────────┤
 │ │    │ PK id       │
 │ │    │ FK dossier  │
 │ │    │    fichier  │
 │ │    └─────────────┘
 │ │
 │ └──────────┐
 │     ┌──────▼──────┐
 │     │journalaction│
 │     ├─────────────┤
 │     │ PK id       │
 │     │ FK dossier  │
 │     │    action   │
 │     └─────────────┘
 │
 └──────────┐
      ┌─────▼──────┐
      │commentaire │
      ├────────────┤
      │ PK id      │
      │ FK dossier │
      │    message │
      └────────────┘
```

### 5.4 Contraintes et règles d'intégrité

**Contraintes de clés** :
- PRIMARY KEY sur toutes les tables (id)
- FOREIGN KEY avec ON DELETE CASCADE ou SET NULL
- UNIQUE sur username, reference, user_id (userprofile)

**Contraintes de domaine** :
- CHECK montant > 0
- CHECK taille fichier <= 5242880 (5 MB)
- CHECK role IN (liste des rôles)
- CHECK duree_mois > 0 AND <= 120

**Contraintes d'intégrité** :
- NOT NULL sur champs obligatoires
- DEFAULT sur champs avec valeur par défaut
- Index sur colonnes fréquemment filtrées

---

**FIN DE LA PARTIE 2**  
**Voir CAHIER_CHARGES_PARTIE3.md pour la suite**

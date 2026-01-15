# 📚 DOCUMENTATION COMPLÈTE - GGR CREDIT WORKFLOW

**Système de Gestion des Demandes de Crédit**  
**Version** : 1.1.0  
**Date** : 4 novembre 2025

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du système](#architecture-du-système)
3. [Portails et utilisateurs](#portails-et-utilisateurs)
4. [Pages et fonctionnalités](#pages-et-fonctionnalités)
5. [Workflow métier](#workflow-métier)
6. [Modèles de données](#modèles-de-données)
7. [Sécurité et permissions](#sécurité-et-permissions)
8. [Installation et déploiement](#installation-et-déploiement)

---

## 🎯 VUE D'ENSEMBLE

### Qu'est-ce que GGR Credit Workflow ?

**GGR Credit Workflow** est un système web professionnel de gestion des demandes de crédit bancaire développé avec Django. Il permet de gérer l'intégralité du processus de demande de crédit, depuis la soumission par le client jusqu'à la libération des fonds.

### Objectifs du système

- ✅ **Digitaliser** le processus de demande de crédit
- ✅ **Automatiser** le workflow de traitement
- ✅ **Tracer** toutes les actions et décisions
- ✅ **Sécuriser** les données sensibles
- ✅ **Optimiser** les délais de traitement

### Utilisateurs cibles

1. **Clients** : Demandeurs de crédit
2. **Gestionnaires** : Premiers traitants des dossiers
3. **Analystes** : Analysent la solvabilité
4. **Responsables GGR** : Valident ou refusent
5. **BOE** : Libèrent les fonds
6. **Super Admins** : Administrent le système

---

## 🏗️ ARCHITECTURE DU SYSTÈME

### Stack technique

```
Frontend:
- HTML5 / CSS3 / JavaScript
- Bootstrap 5
- Templates Django

Backend:
- Python 3.10+
- Django 5.2.6
- PostgreSQL 14+

Outils:
- WhiteNoise (fichiers statiques)
- xhtml2pdf (génération PDF)
- Coverage (tests)
```

### Structure des fichiers

```
ggr-credit-workflow/
├── core/                          # Configuration Django
│   ├── settings/
│   │   ├── base.py               # Settings communs
│   │   ├── client.py             # Portail client (port 8001)
│   │   └── pro.py                # Portail pro (port 8002)
│   ├── urls.py                   # Routes principales
│   └── wsgi.py                   # Point d'entrée WSGI
│
├── suivi_demande/                # Application principale
│   ├── models.py                 # Modèles de données
│   ├── views.py                  # Vues (2027 lignes)
│   ├── views_modules/            # Vues modulaires (nouveau)
│   │   ├── base.py              # Vues de base
│   │   ├── dossiers.py          # Gestion dossiers
│   │   ├── dashboard.py         # Dashboards
│   │   ├── workflow.py          # Transitions
│   │   ├── notifications.py     # Notifications
│   │   └── ajax.py              # API AJAX
│   ├── forms.py                  # Formulaires
│   ├── forms_demande.py          # Wizard étapes 1-2
│   ├── forms_demande_extra.py    # Wizard étapes 3-4
│   ├── urls.py                   # Routes app
│   ├── admin.py                  # Interface admin
│   ├── decorators.py             # Contrôle d'accès
│   ├── permissions.py            # Permissions
│   ├── constants.py              # Constantes
│   ├── logging_config.py         # Configuration logging
│   ├── tests/                    # Tests (75 tests)
│   │   ├── test_models.py
│   │   ├── test_permissions.py
│   │   ├── test_workflow.py
│   │   ├── test_views.py
│   │   ├── test_forms.py
│   │   └── test_integration.py
│   └── templates/                # Templates HTML
│
├── templates/                     # Templates globaux
├── static/                        # CSS, JS, images
├── media/                         # Fichiers uploadés
├── logs/                          # Logs applicatifs
├── requirements.txt               # Dépendances Python
└── manage.py                      # CLI Django
```

---

## 👥 PORTAILS ET UTILISATEURS

### 1. Portail Client (Port 8001)

**URL** : `http://127.0.0.1:8001`

**Pour qui ?** Les demandeurs de crédit

**Fonctionnalités** :
- Inscription et création de compte
- Wizard de demande de crédit (4 étapes)
- Suivi en temps réel du dossier
- Consultation de l'historique
- Réception de notifications
- Téléchargement de documents (pas d’upload après soumission)

#### Rôle du Client
- Peut créer un compte et soumettre une demande via le wizard en 4 étapes.
- Peut consulter uniquement ses propres dossiers (lecture seule après soumission).
- Peut lire les commentaires/retours du gestionnaire dans l’historique.
- Peut télécharger ses documents déposés dans le cadre du dossier.
- Ne peut pas modifier le statut du dossier ni voir les dossiers d’autres utilisateurs.
- Ne peut pas téléverser de nouvelles pièces après soumission; tout complément passe par le gestionnaire.

### 2. Portail Professionnel (Port 8002)

**URL** : `http://127.0.0.1:8002/pro/`

**Pour qui ?** Le personnel de la banque

**Rôles disponibles** :
- **Gestionnaire** : Traite les nouveaux dossiers
- **Analyste** : Analyse la solvabilité
- **Responsable GGR** : Valide ou refuse
- **BOE** : Libère les fonds
- **Super Admin** : Gère les utilisateurs

---

## 📄 PAGES ET FONCTIONNALITÉS

### PORTAIL CLIENT

#### 1. Page d'accueil `/`
- **Fichier** : `templates/home.html`
- **Vue** : `views_modules/base.py::home()`
- **Contenu** :
  - Présentation du service
  - Boutons "Se connecter" et "S'inscrire"
  - Informations sur les produits de crédit

#### 2. Inscription `/signup/`
- **Fichier** : `templates/accounts/signup.html`
- **Vue** : `views_modules/base.py::signup()`
- **Formulaire** : `forms.py::SignupForm`
- **Champs** :
  - Nom d'utilisateur
  - Email
  - Mot de passe (avec confirmation)
- **Processus** :
  1. Client remplit le formulaire
  2. Compte créé mais inactif
  3. Redirection vers page "En attente d'approbation"
  4. Admin doit activer le compte

#### 3. Connexion `/accounts/login/`
- **Fichier** : Django auth (built-in)
- **Redirection après connexion** : Dashboard

#### 4. Dashboard Client `/dashboard/`
- **Fichier** : `templates/suivi_demande/dashboard_client.html`
- **Vue** : `views_modules/dashboard.py::dashboard()`
- **Sections** :
  - **Mes dossiers en cours** : Liste des dossiers actifs
  - **Dossiers traités** : Historique des dossiers terminés
  - **Statistiques** :
    - Nombre de dossiers approuvés
    - Montant total demandé
  - **Historique des actions** : Journal des événements
- **Actions disponibles** :
  - Créer nouvelle demande
  - Voir détails d'un dossier
  - Consulter notifications

#### 5. Mes demandes `/my-applications/`
- **Fichier** : `templates/suivi_demande/my_applications.html`
- **Vue** : `views_modules/dossiers.py::my_applications()`
- **Fonctionnalités** :
  - Liste paginée (25 par page)
  - Filtrage par statut
  - Tri par date
  - Badges de statut colorés
- **Colonnes affichées** :
  - Référence
  - Produit
  - Montant
  - Statut client
  - Date de soumission
  - Dernière mise à jour
  - Actions (Voir détail)

#### 6. Wizard de demande (4 étapes)

##### Étape 1 : Informations personnelles `/demande/step1/`
- **Vue** : `views.py::demande_step1()`
- **Formulaire** : `forms_demande.py::DemandeStep1Form`
- **Champs** :
  - Nom et prénom
  - Date de naissance
  - Nationalité
  - Adresse exacte
  - Numéro de téléphone
  - Emploi occupé
  - Statut emploi (Public/Privé)
  - Ancienneté emploi
  - Type de contrat (CDI/CDD/Autre)
  - Nom employeur
  - Lieu emploi
  - Situation familiale

##### Étape 2 : Informations financières `/demande/step2/`
- **Vue** : `views.py::demande_step2()`
- **Formulaire** : `forms_demande.py::DemandeStep2Form`
- **Champs** :
  - Salaire net moyen
  - Autres revenus
  - Total charges mensuelles
  - Nombre de personnes à charge
  - Crédits en cours (Oui/Non)
  - Total échéances crédits en cours

##### Étape 3 : Demande de crédit `/demande/step3/`
- **Vue** : `views.py::demande_step3()`
- **Formulaire** : `forms_demande_extra.py::DemandeStep3Form`
- **Champs** :
  - Type de crédit
  - Montant demandé
  - Durée (en mois)
  - Objet du financement
  - Garanties proposées

##### Étape 4 : Documents et validation `/demande/step4/`
- **Vue** : `views.py::demande_step4()`
- **Formulaire** : `forms_demande_extra.py::DemandeStep4Form`
- **Contenu** :
  - Upload de documents (CNI, fiches de paie, etc.)
  - Consentements :
    - Traitement des données personnelles
    - Vérification des informations
    - Conditions générales
  - Récapitulatif de la demande
  - Bouton de soumission finale

#### 7. Détail d'un dossier `/dossier/<id>/`
- **Fichier** : `templates/suivi_demande/dossier_detail.html`
- **Vue** : `views_modules/dashboard.py::dossier_detail()`
- **Onglets** :
  1. **Informations** : Détails du dossier
  2. **Documents** : Pièces jointes
  3. **Commentaires** : Échanges avec la banque
  4. **Historique** : Journal des actions
- **Actions** :
  - Ajouter un commentaire
  - Télécharger des documents
  - Voir le statut en temps réel

#### 8. Notifications `/notifications/`
- **Fichier** : `templates/suivi_demande/notifications.html`
- **Vue** : `views_modules/notifications.py::notifications_list()`
- **Fonctionnalités** :
  - Liste paginée (20 par page)
  - Badge "Non lu" / "Lu"
  - Marquer comme lu
  - Marquer toutes comme lues
  - Filtrage par type
- **Types de notifications** :
  - Nouveau message
  - Mise à jour du dossier
  - Demande de compléments
  - Décision finale

---

### PORTAIL PROFESSIONNEL

#### 1. Connexion Pro `/pro/login/`
- **Fichier** : Django auth
- **Redirection** : Dashboard selon le rôle

#### 2. Dashboard Gestionnaire `/pro/dashboard/`
- **Fichier** : `templates/suivi_demande/dashboard_gestionnaire.html`
- **Vue** : `views_modules/dashboard.py::_dashboard_gestionnaire()`
- **Sections** :
  - **KPI** :
    - Nouveaux dossiers (total + aujourd'hui)
    - Dossiers complets (total + aujourd'hui)
    - Dossiers retournés (total + aujourd'hui)
    - En attente décision (total + aujourd'hui)
    - Délai moyen de traitement
  - **Dossiers en attente** : À traiter en priorité
  - **Dossiers récents** : 10 derniers
  - **Dossiers en cours** : Tous les actifs
  - **Dossiers traités** : Historique
  - **Actions récentes** : Journal global
- **Actions disponibles** :
  - Transmettre à l'analyste
  - Retourner au client (avec commentaire)
  - Voir détails
  - Archiver

#### 3. Dashboard Analyste `/pro/dashboard/`
- **Fichier** : `templates/suivi_demande/dashboard_analyste.html`
- **Vue** : `views_modules/dashboard.py::_dashboard_analyste()`
- **Sections** :
  - **Dossiers à analyser** : Transmis par gestionnaire
  - **Dossiers prioritaires** : 5 plus anciens
  - **Statistiques** :
    - Total à analyser
    - Dossiers ce mois
  - **Dossiers traités** : Historique
- **Actions disponibles** :
  - Transmettre au GGR
  - Retourner au gestionnaire
  - Analyser (créer canevas)

#### 4. Dashboard Responsable GGR `/pro/dashboard/`
- **Fichier** : `templates/suivi_demande/dashboard_responsable_ggr_pro.html`
- **Vue** : `views_modules/dashboard.py::_dashboard_responsable_ggr()`
- **Sections** :
  - **Dossiers en validation** : À décider
  - **Dossiers traités** : Historique décisions
  - **Historique actions** : Journal
- **Actions disponibles** :
  - Approuver
  - Refuser (avec motif)
  - Demander complément d'analyse

#### 5. Dashboard BOE `/pro/dashboard/`
- **Fichier** : `templates/suivi_demande/dashboard_boe.html`
- **Vue** : `views_modules/dashboard.py::_dashboard_boe()`
- **Sections** :
  - **Dossiers approuvés** : En attente libération
  - **Fonds libérés aujourd'hui** : Compteur
  - **Dossiers traités** : Historique
- **Actions disponibles** :
  - Libérer les fonds
  - Voir détails

#### 6. Dashboard Super Admin `/pro/dashboard/`
- **Fichier** : `templates/suivi_demande/dashboard_super_admin.html`
- **Vue** : `views_modules/dashboard.py::_dashboard_super_admin()`
- **Sections** :
  - **Gestion utilisateurs** :
    - Liste tous les utilisateurs
    - Statistiques par rôle
    - Utilisateurs actifs/inactifs
  - **Actions récentes** : Log admin Django
  - **Utilisateurs récents** : 10 derniers inscrits
- **Actions disponibles** :
  - Activer/Désactiver utilisateur
  - Changer le rôle
  - Voir profil détaillé

#### 7. Gestion des utilisateurs `/pro/admin/users/`
- **Fichier** : `templates/suivi_demande/admin_users.html`
- **Vue** : `views_admin.py::admin_users()`
- **Fonctionnalités** :
  - Liste tous les utilisateurs
  - Filtrage par rôle
  - Filtrage par statut (actif/inactif)
  - Recherche par nom
- **Actions** :
  - Activer compte
  - Désactiver compte
  - Changer rôle
  - Voir détails

#### 8. Canevas de proposition `/pro/canevas/<dossier_id>/`
- **Fichier** : `templates/suivi_demande/canevas_proposition.html`
- **Vue** : `views_canevas.py::canevas_proposition()`
- **Contenu** :
  - **Informations client** (pré-remplies)
  - **Situation financière** :
    - Salaire net moyen
    - Autres revenus
    - Charges mensuelles
    - Crédits en cours
  - **Calculs automatiques** :
    - Capacité d'endettement brute (40% salaire)
    - Capacité d'endettement nette
    - Salaire net avant endettement
    - Taux d'endettement
  - **Proposition de crédit** :
    - Montant proposé
    - Durée
    - Taux d'intérêt
    - Mensualité
    - Coût total du crédit
  - **Documents requis** (checklist)
  - **Validation** : Boutons Valider/Refuser

#### 9. Génération PDF `/pro/canevas/<id>/pdf/`
- **Vue** : `pdf_views.py::generer_pdf_canevas()`
- **Contenu** :
  - Logo de la banque
  - Informations complètes du canevas
  - Calculs financiers
  - Proposition détaillée
  - Signature électronique

---

## 🔄 WORKFLOW MÉTIER

### Statuts Agent (côté banque)

```
NOUVEAU
  ↓ (Gestionnaire transmet)
TRANSMIS_ANALYSTE
  ↓ (Analyste analyse)
EN_COURS_ANALYSE
  ↓ (Analyste transmet)
EN_COURS_VALIDATION_GGR
  ↓ (GGR décide)
APPROUVE_ATTENTE_FONDS ou REFUSE
  ↓ (BOE libère)
FONDS_LIBERE
```

### Statuts Client (côté client)

- **EN_ATTENTE** : Dossier soumis, en attente de traitement
- **EN_COURS_TRAITEMENT** : Dossier en cours d'analyse
- **SE_RAPPROCHER_GEST** : Compléments requis ou refusé
- **TERMINE** : Fonds libérés

### Transitions possibles

| De | Vers | Acteur | Action |
|----|------|--------|--------|
| NOUVEAU | TRANSMIS_ANALYSTE | Gestionnaire | Transmettre |
| NOUVEAU | NOUVEAU | Gestionnaire | Retour client |
| TRANSMIS_ANALYSTE | EN_COURS_VALIDATION_GGR | Analyste | Transmettre GGR |
| TRANSMIS_ANALYSTE | TRANSMIS_RESP_GEST | Analyste | Retour gestionnaire |
| EN_COURS_VALIDATION_GGR | APPROUVE_ATTENTE_FONDS | Resp. GGR | Approuver |
| EN_COURS_VALIDATION_GGR | REFUSE | Resp. GGR | Refuser |
| APPROUVE_ATTENTE_FONDS | FONDS_LIBERE | BOE | Libérer fonds |

---

## 💾 MODÈLES DE DONNÉES

### 1. User (Django built-in)
- username
- email
- password
- is_active
- is_staff
- date_joined

### 2. UserProfile
- user (OneToOne → User)
- full_name
- phone
- address
- role (CLIENT, GESTIONNAIRE, ANALYSTE, etc.)
- created_at
- updated_at

### 3. DossierCredit
- client (FK → User)
- reference (unique)
- produit
- montant
- statut_agent
- statut_client
- acteur_courant (FK → User)
- is_archived
- archived_at
- archived_by
- date_soumission
- date_maj
- wizard_current_step
- wizard_completed
- consent_accepted

### 4. CanevasProposition
- dossier (OneToOne → DossierCredit)
- nom_prenom
- date_naissance
- adresse_exacte
- numero_telephone
- emploi_occupe
- nom_employeur
- salaire_net_moyen_fcfa
- autres_revenus_fcfa
- total_charges_mensuelles_fcfa
- total_echeances_credits_cours
- capacite_endettement_brute_fcfa
- capacite_endettement_nette_fcfa
- demande_montant_fcfa
- demande_duree_mois
- demande_taux_pourcent
- proposition_montant_fcfa
- proposition_duree_mois
- proposition_taux_pourcent
- proposition_mensualite_fcfa
- Documents requis (booleans)

### 5. PieceJointe
- dossier (FK → DossierCredit)
- fichier (FileField)
- type_piece (CNI, FICHE_PAIE, etc.)
- taille
- upload_by (FK → User)
- upload_at

### 6. JournalAction
- dossier (FK → DossierCredit)
- action (TRANSITION, APPROBATION, etc.)
- de_statut
- vers_statut
- acteur (FK → User)
- timestamp
- commentaire_systeme
- meta (JSONField)

### 7. Notification
- utilisateur_cible (FK → User)
- type
- titre
- message
- canal (INTERNE, EMAIL, SMS)
- lu
- created_at

### 8. Commentaire
- dossier (FK → DossierCredit)
- auteur (FK → User)
- message
- cible_role
- created_at

---

## 🔒 SÉCURITÉ ET PERMISSIONS

### Contrôle d'accès par rôle

**Fichier** : `decorators.py` et `permissions.py`

#### Permissions par rôle

| Action | CLIENT | GEST | ANALYSTE | GGR | BOE | ADMIN |
|--------|--------|------|----------|-----|-----|-------|
| Créer demande | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Voir ses dossiers | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Voir tous dossiers | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Transmettre analyste | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Retour client | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Transmettre GGR | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Approuver/Refuser | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Libérer fonds | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Gérer utilisateurs | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### Isolation des données

- **Clients** : Ne voient que leurs propres dossiers
- **Professionnels** : Voient tous les dossiers selon leur rôle
- **Filtrage automatique** dans les requêtes

### Validation des uploads

- **Taille max** : 5 MB
- **Types autorisés** : PDF, JPG, JPEG, PNG
- **Validation** : Extension + type MIME

---

## 🚀 INSTALLATION ET DÉPLOIEMENT

Voir `README_PROFESSIONNEL.md` pour les instructions complètes.

---

**Documentation générée le 4 novembre 2025**  
**Version du projet : 1.1.0**

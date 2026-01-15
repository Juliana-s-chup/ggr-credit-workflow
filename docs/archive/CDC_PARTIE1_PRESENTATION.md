# 📋 CAHIER DES CHARGES - PARTIE 1
## PRÉSENTATION GÉNÉRALE ET DESCRIPTION FONCTIONNELLE

**Projet** : GGR Credit Workflow  
**Version** : 1.0 | **Date** : 4 novembre 2025

---

## 1. PRÉSENTATION GÉNÉRALE

### 1.1 Contexte du projet

Le secteur bancaire congolais fait face à un impératif de modernisation de ses processus. Le traitement des demandes de crédit, activité centrale des institutions financières, repose encore largement sur des procédures manuelles et des documents papier.

L'institution GGR (Gestion des Garanties et Risques) a identifié la nécessité de digitaliser son processus d'octroi de crédit pour améliorer l'efficacité opérationnelle, réduire les délais de traitement et offrir une meilleure expérience client.

**Chiffres clés** :
- Délai moyen actuel : 15 jours
- Taux d'erreur : 15%
- Déplacements clients : 3-4 par dossier
- Temps de recherche d'un dossier : 30 minutes

### 1.2 Problématique initiale

**Pour les clients** :
- Processus long nécessitant plusieurs déplacements physiques
- Absence de visibilité sur l'état d'avancement
- Horaires d'ouverture limités (8h-17h)
- Communication difficile avec la banque

**Pour la banque** :
- Gestion manuelle chronophage et source d'erreurs
- Absence de traçabilité des actions
- Coordination difficile entre services
- Impossibilité de générer des statistiques fiables
- Stockage physique volumineux

**Pour le management** :
- Manque de visibilité sur l'activité
- Difficultés à mesurer les performances
- Impossibilité de pilotage en temps réel

### 1.3 Objectifs métier

#### Objectifs généraux
1. Digitaliser le processus de bout en bout
2. Réduire les délais de traitement de 50%
3. Améliorer l'expérience client
4. Assurer la traçabilité complète
5. Optimiser la productivité des équipes

#### Objectifs quantifiables
| Indicateur | Avant | Objectif |
|------------|-------|----------|
| Délai moyen | 15 jours | 7 jours |
| Déplacements client | 3-4 | 0-1 |
| Taux d'erreur | 15% | 5% |
| Satisfaction client | 60% | 85% |
| Temps recherche dossier | 30 min | 30 sec |

### 1.4 Public cible et utilisateurs

**Clients** (100-500 utilisateurs) :
- Particuliers demandeurs de crédit
- Âge : 25-60 ans
- Niveau digital : Moyen à élevé
- Besoin : Simplicité et rapidité

**Professionnels** (20-50 utilisateurs) :
- Gestionnaires (5-10)
- Analystes crédit (3-5)
- Responsables GGR (2-3)
- BOE (2-3)
- Administrateurs (1-2)

### 1.5 Contraintes générales

**Contraintes techniques** :
- Développement en Django 5.2.6
- Base de données PostgreSQL
- Hébergement local (serveur interne)
- Compatible navigateurs modernes

**Contraintes métier** :
- Conformité réglementaire bancaire
- Traçabilité obligatoire
- Sécurité des données sensibles
- Disponibilité 99%

**Contraintes temporelles** :
- Développement : 6 mois
- Formation : 2 semaines
- Mise en production : 1 mois

---

## 2. DESCRIPTION FONCTIONNELLE DÉTAILLÉE

### 2.1 Acteurs du système

| Acteur | Rôle | Nombre |
|--------|------|--------|
| **Client** | Demandeur de crédit | 100-500 |
| **Gestionnaire** | Vérification complétude | 5-10 |
| **Analyste** | Analyse solvabilité | 3-5 |
| **Responsable GGR** | Décision finale | 2-3 |
| **BOE** | Libération fonds | 2-3 |
| **Super Admin** | Administration système | 1-2 |

### 2.2 Rôles et permissions

#### Matrice des permissions

| Action | Client | Gestionnaire | Analyste | Resp. GGR | BOE | Admin |
|--------|--------|--------------|----------|-----------|-----|-------|
| Créer demande | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Voir ses dossiers | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Voir tous dossiers | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Télécharger documents | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ajouter documents | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| Ajouter commentaires | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Transmettre analyste | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Créer canevas | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Approuver/Refuser | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Libérer fonds | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Gérer utilisateurs | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### 2.3 Description détaillée des fonctionnalités

#### F1 : Authentification et gestion des comptes

**F1.1 Inscription**
- Formulaire : username, email, mot de passe
- Validation : email unique, mot de passe fort (8+ caractères)
- Statut initial : Inactif (attente validation admin)
- Notification : Email de confirmation après activation

**F1.2 Connexion**
- Authentification par username/password
- Session sécurisée (30 min d'inactivité)
- Redirection selon le rôle
- Logging des connexions/déconnexions

**F1.3 Gestion du profil**
- Consultation des informations
- Modification : email, téléphone, adresse
- Changement de mot de passe
- Historique des actions

#### F2 : Gestion des demandes de crédit (CRUD)

**F2.1 Création (Wizard 4 étapes)**

**Étape 1 : Informations personnelles**
- Nom, prénom, date de naissance
- Nationalité, adresse, téléphone
- Emploi, employeur, ancienneté
- Situation familiale

**Étape 2 : Informations financières**
- Salaire net moyen
- Autres revenus
- Charges mensuelles
- Crédits en cours

**Étape 3 : Demande de crédit**
- Type de crédit
- Montant (min 100 000 FCFA)
- Durée (max 120 mois)
- Objet du financement
- Garanties proposées

**Étape 4 : Documents et validation**
- Upload CNI (PDF/JPG, max 5 MB)
- Upload 3 fiches de paie
- Upload justificatif domicile
- Acceptation conditions générales
- Consentements RGPD

**F2.2 Consultation (Read)**
- Liste des demandes avec filtres
- Détail d'une demande
- Historique des actions
- Documents associés
- Commentaires

**F2.3 Modification (Update)**
- Ajout de documents complémentaires
- Ajout de commentaires
- Modification par les professionnels (statut, acteur)

**F2.4 Suppression (Delete)**
- Archivage logique (soft delete)
- Conservation de l'historique
- Accès restreint aux admins

#### F3 : Gestion des documents

**F3.1 Upload**
- Types autorisés : PDF, JPG, PNG
- Taille max : 5 MB
- Validation du type MIME
- Stockage sécurisé dans media/

**F3.2 Consultation**
- Téléchargement des documents
- Prévisualisation (si possible)
- Liste des documents par dossier

**F3.3 Gestion**
- Ajout de documents complémentaires
- Suppression (admin uniquement)
- Traçabilité (qui, quand)

#### F4 : Workflow des demandes

**Statuts du workflow** :
1. NOUVEAU (soumission)
2. TRANSMIS_ANALYSTE (gestionnaire)
3. EN_COURS_VALIDATION_GGR (analyste)
4. APPROUVE_ATTENTE_FONDS (responsable GGR)
5. FONDS_LIBERE (BOE)
6. REFUSE (responsable GGR)
7. TRANSMIS_RESP_GEST (retour analyste)
8. RETOUR_CLIENT (gestionnaire)

**Transitions autorisées** :
```
NOUVEAU → TRANSMIS_ANALYSTE (Gestionnaire)
NOUVEAU → RETOUR_CLIENT (Gestionnaire)
TRANSMIS_ANALYSTE → EN_COURS_VALIDATION_GGR (Analyste)
TRANSMIS_ANALYSTE → TRANSMIS_RESP_GEST (Analyste)
EN_COURS_VALIDATION_GGR → APPROUVE_ATTENTE_FONDS (Resp. GGR)
EN_COURS_VALIDATION_GGR → REFUSE (Resp. GGR)
APPROUVE_ATTENTE_FONDS → FONDS_LIBERE (BOE)
```

#### F5 : Canevas de proposition (Analyste)

**Données saisies** :
- Informations personnelles (pré-remplies)
- Données financières (salaire, charges, crédits)
- Demande client (montant, durée, taux)

**Calculs automatiques** :
- Capacité endettement brute = Salaire × 40%
- Capacité nette = Brute - Crédits en cours
- Taux d'endettement = Mensualité / Salaire

**Proposition** :
- Montant accordé (≤ capacité nette)
- Durée proposée
- Taux d'intérêt
- Mensualité calculée

**Génération PDF** :
- Document formaté professionnel
- Signature électronique (optionnel)

#### F6 : Tableau de bord avec statistiques

**Dashboard Client** :
- Nombre de demandes (en cours, approuvées, refusées)
- Montant total demandé
- Dernières actions
- Notifications non lues

**Dashboard Gestionnaire** :
- Dossiers en attente (NOUVEAU)
- Dossiers retournés (TRANSMIS_RESP_GEST)
- Statistiques personnelles
- Délai moyen de traitement

**Dashboard Analyste** :
- Dossiers à analyser (TRANSMIS_ANALYSTE)
- Dossiers en cours (EN_COURS_ANALYSE)
- Statistiques d'analyse
- Taux d'approbation

**Dashboard Responsable GGR** :
- Dossiers en validation (EN_COURS_VALIDATION_GGR)
- Montant total en attente
- Taux d'approbation global
- Statistiques par analyste

**Dashboard BOE** :
- Dossiers approuvés (APPROUVE_ATTENTE_FONDS)
- Montant à libérer
- Fonds libérés (mois en cours)
- Historique

**Dashboard Admin** :
- Vue globale de tous les dossiers
- Statistiques par statut
- Statistiques par acteur
- Logs système

#### F7 : Notifications

**Types de notifications** :
- Interne (dans l'application)
- Email (SMTP)
- SMS (optionnel, futur)

**Événements notifiés** :
- Création de dossier
- Changement de statut
- Commentaire ajouté
- Compléments requis
- Décision finale
- Libération des fonds

**Gestion** :
- Badge de notification (nombre non lues)
- Liste des notifications
- Marquer comme lu
- Historique complet

#### F8 : Commentaires et communication

**Fonctionnalités** :
- Ajout de commentaire sur un dossier
- Destinataire : rôle spécifique ou tous
- Notification automatique
- Historique des échanges

**Cas d'usage** :
- Gestionnaire demande compléments au client
- Analyste demande précisions au gestionnaire
- Responsable GGR justifie un refus

#### F9 : Journal des actions (Audit Trail)

**Traçabilité complète** :
- Qui a fait quoi et quand
- Transitions de statut
- Modifications de données
- Connexions/déconnexions
- Accès aux dossiers

**Utilisation** :
- Audit interne/externe
- Résolution de litiges
- Analyse des processus
- Conformité réglementaire

### 2.4 Scénarios d'utilisation (User Stories)

**US1 : En tant que gestionnaire, je veux créer une demande de crédit pour un client**
```
GIVEN je suis connecté en tant que gestionnaire
WHEN je clique sur "Nouvelle demande"
AND je remplis le wizard 4 étapes avec les informations du client
AND j'uploade les documents requis
AND je soumets la demande
THEN un dossier est créé avec statut NOUVEAU
AND le client reçoit une notification
AND je peux consulter le dossier créé
```

**US2 : En tant que gestionnaire, je veux transmettre un dossier à l'analyste**
```
GIVEN je suis connecté en tant que gestionnaire
WHEN je consulte un dossier NOUVEAU
AND je vérifie la complétude
AND le dossier est complet
AND je clique sur "Transmettre à l'analyste"
THEN le statut passe à TRANSMIS_ANALYSTE
AND l'analyste reçoit une notification
AND le client est informé
```

**US3 : En tant qu'analyste, je veux créer un canevas de proposition**
```
GIVEN je suis connecté en tant qu'analyste
WHEN je consulte un dossier TRANSMIS_ANALYSTE
AND je clique sur "Créer canevas"
AND je saisis les données financières
THEN le système calcule automatiquement la capacité d'endettement
AND je propose montant/durée/taux
AND je sauvegarde le canevas
AND je peux transmettre au GGR
```

**US4 : En tant que responsable GGR, je veux approuver un dossier**
```
GIVEN je suis connecté en tant que responsable GGR
WHEN je consulte un dossier EN_COURS_VALIDATION_GGR
AND j'examine le canevas de l'analyste
AND je décide d'approuver
AND je clique sur "Approuver"
THEN le statut passe à APPROUVE_ATTENTE_FONDS
AND le BOE est notifié
AND le client reçoit la bonne nouvelle
```

**US5 : En tant que BOE, je veux libérer les fonds**
```
GIVEN je suis connecté en tant que BOE
WHEN je consulte un dossier APPROUVE_ATTENTE_FONDS
AND je vérifie les conditions d'engagement
AND je clique sur "Libérer les fonds"
THEN le statut passe à FONDS_LIBERE
AND le client est notifié
AND le dossier est clôturé
```

### 2.5 Diagramme textuel des cas d'utilisation

```
┌─────────────────────────────────────────────────────────────┐
│                  SYSTÈME GGR CREDIT WORKFLOW                 │
└─────────────────────────────────────────────────────────────┘

ACTEUR: Client
├── UC01: S'inscrire
├── UC02: Se connecter
├── UC03: Consulter mes demandes
├── UC04: Consulter le détail d'une demande
├── UC05: Télécharger un document
├── UC06: Lire les commentaires
└── UC07: Consulter les notifications

ACTEUR: Gestionnaire
├── UC10: Créer une demande de crédit pour un client (wizard 4 étapes)
├── UC11: Consulter le dashboard gestionnaire
├── UC12: Consulter la liste des dossiers (NOUVEAU, TRANSMIS_RESP_GEST)
├── UC13: Consulter le détail d'un dossier
├── UC14: Transmettre un dossier à l'analyste
├── UC15: Retourner un dossier au client (avec commentaire)
└── UC16: Ajouter un commentaire

ACTEUR: Analyste
├── UC17: Consulter le dashboard analyste
├── UC18: Consulter les dossiers à analyser (TRANSMIS_ANALYSTE)
├── UC19: Créer un canevas de proposition
│   ├── UC19.1: Saisir les données financières
│   ├── UC19.2: Calculer la capacité d'endettement (auto)
│   └── UC19.3: Proposer les conditions du crédit
├── UC20: Transmettre un dossier au GGR
├── UC21: Retourner un dossier au gestionnaire
└── UC22: Générer le PDF du canevas

ACTEUR: Responsable GGR
├── UC23: Consulter le dashboard GGR
├── UC24: Consulter les dossiers en validation
├── UC25: Examiner le canevas de proposition
├── UC26: Approuver un dossier
├── UC27: Refuser un dossier (avec motif)
└── UC28: Ajuster les conditions du crédit

ACTEUR: BOE
├── UC29: Consulter le dashboard BOE
├── UC30: Consulter les dossiers approuvés
├── UC31: Vérifier les conditions d'engagement
├── UC32: Libérer les fonds
└── UC33: Clôturer un dossier

ACTEUR: Super Admin
├── UC34: Consulter le dashboard admin
├── UC35: Gérer les utilisateurs
│   ├── UC35.1: Activer un compte
│   ├── UC35.2: Désactiver un compte
│   └── UC35.3: Changer le rôle d'un utilisateur
├── UC36: Consulter les statistiques globales
├── UC37: Consulter les logs système
└── UC38: Archiver/Désarchiver un dossier

ACTEUR: Système (automatique)
├── UC39: Envoyer une notification
├── UC40: Envoyer un email
├── UC41: Logger une action
├── UC42: Calculer automatiquement les indicateurs
└── UC43: Générer les rapports automatiques
```

---

**FIN DE LA PARTIE 1**  
**Voir CAHIER_CHARGES_PARTIE2.md pour la suite**

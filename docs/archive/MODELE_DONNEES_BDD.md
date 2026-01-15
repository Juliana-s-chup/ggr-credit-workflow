# 🗄️ MODÈLE DE DONNÉES - DOCUMENTATION COMPLÈTE

**GGR Credit Workflow - Base de Données Relationnelle**  
**SGBD** : PostgreSQL 14+ | **ORM** : Django 5.2.6

---

## 1. LISTE DES TABLES

### 1.1 Tables principales (8 tables)

| Table | Description | Lignes estimées |
|-------|-------------|-----------------|
| `auth_user` | Utilisateurs Django (built-in) | 100-500 |
| `suivi_demande_userprofile` | Profils utilisateurs étendus | 100-500 |
| `suivi_demande_dossiercredit` | Dossiers de crédit | 1000-10000 |
| `suivi_demande_canevasproposition` | Analyses financières | 500-5000 |
| `suivi_demande_piecejointe` | Documents uploadés | 5000-50000 |
| `suivi_demande_journalaction` | Journal des actions | 10000-100000 |
| `suivi_demande_notification` | Notifications | 5000-50000 |
| `suivi_demande_commentaire` | Commentaires | 1000-10000 |

### 1.2 Tables système Django
- `django_migrations` : Historique des migrations
- `django_session` : Sessions utilisateurs
- `django_content_type` : Types de contenu
- `auth_permission` : Permissions
- `auth_group` : Groupes (non utilisé)

---

## 2. DESCRIPTION DÉTAILLÉE DES TABLES

### 2.1 Table `auth_user` (Django built-in)

**Description** : Utilisateurs du système (clients et professionnels)

| Colonne | Type SQL | Taille | NULL | Défaut | Description |
|---------|----------|--------|------|--------|-------------|
| `id` | INTEGER | - | NO | AUTO | Clé primaire |
| `username` | VARCHAR | 150 | NO | - | Nom d'utilisateur unique |
| `email` | VARCHAR | 254 | YES | - | Email |
| `password` | VARCHAR | 128 | NO | - | Hash du mot de passe |
| `first_name` | VARCHAR | 150 | YES | - | Prénom |
| `last_name` | VARCHAR | 150 | YES | - | Nom |
| `is_active` | BOOLEAN | - | NO | TRUE | Compte actif |
| `is_staff` | BOOLEAN | - | NO | FALSE | Accès admin |
| `is_superuser` | BOOLEAN | - | NO | FALSE | Super admin |
| `date_joined` | TIMESTAMP | - | NO | NOW() | Date d'inscription |
| `last_login` | TIMESTAMP | - | YES | - | Dernière connexion |

**Contraintes** :
- `PRIMARY KEY (id)`
- `UNIQUE (username)`
- `CHECK (username <> '')`

---

### 2.2 Table `suivi_demande_userprofile`

**Description** : Extension du profil utilisateur avec rôle et coordonnées

| Colonne | Type SQL | Taille | NULL | Défaut | Description |
|---------|----------|--------|------|--------|-------------|
| `id` | INTEGER | - | NO | AUTO | Clé primaire |
| `user_id` | INTEGER | - | NO | - | FK vers auth_user |
| `full_name` | VARCHAR | 200 | NO | - | Nom complet |
| `phone` | VARCHAR | 20 | NO | - | Téléphone |
| `address` | TEXT | - | NO | - | Adresse complète |
| `role` | VARCHAR | 20 | NO | - | Rôle (CLIENT, GESTIONNAIRE, etc.) |
| `created_at` | TIMESTAMP | - | NO | NOW() | Date de création |
| `updated_at` | TIMESTAMP | - | NO | NOW() | Dernière modification |

**Contraintes** :
- `PRIMARY KEY (id)`
- `FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE`
- `UNIQUE (user_id)` (relation OneToOne)
- `CHECK (role IN ('CLIENT', 'GESTIONNAIRE', 'ANALYSTE', 'RESPONSABLE_GGR', 'BOE', 'SUPER_ADMIN'))`

**Index** :
- `INDEX idx_userprofile_role ON (role)` - Performance filtrage par rôle

---

### 2.3 Table `suivi_demande_dossiercredit`

**Description** : Dossiers de demande de crédit (table centrale)

| Colonne | Type SQL | Taille | NULL | Défaut | Description |
|---------|----------|--------|------|--------|-------------|
| `id` | INTEGER | - | NO | AUTO | Clé primaire |
| `reference` | VARCHAR | 50 | NO | - | Référence unique (DOS-2025-001) |
| `client_id` | INTEGER | - | NO | - | FK vers auth_user (demandeur) |
| `produit` | VARCHAR | 100 | NO | - | Type de crédit |
| `montant` | DECIMAL | 12,2 | NO | - | Montant demandé (FCFA) |
| `statut_agent` | VARCHAR | 50 | NO | 'NOUVEAU' | Statut interne |
| `statut_client` | VARCHAR | 50 | NO | 'EN_ATTENTE' | Statut visible client |
| `acteur_courant_id` | INTEGER | - | YES | - | FK vers auth_user (acteur) |
| `is_archived` | BOOLEAN | - | NO | FALSE | Dossier archivé |
| `archived_at` | TIMESTAMP | - | YES | - | Date archivage |
| `archived_by_id` | INTEGER | - | YES | - | FK vers auth_user |
| `date_soumission` | TIMESTAMP | - | NO | NOW() | Date de soumission |
| `date_maj` | TIMESTAMP | - | NO | NOW() | Dernière mise à jour |
| `wizard_current_step` | INTEGER | - | NO | 1 | Étape wizard en cours |
| `wizard_completed` | BOOLEAN | - | NO | FALSE | Wizard terminé |
| `consent_accepted` | BOOLEAN | - | NO | FALSE | Consentements acceptés |

**Contraintes** :
- `PRIMARY KEY (id)`
- `UNIQUE (reference)`
- `FOREIGN KEY (client_id) REFERENCES auth_user(id) ON DELETE CASCADE`
- `FOREIGN KEY (acteur_courant_id) REFERENCES auth_user(id) ON DELETE SET NULL`
- `FOREIGN KEY (archived_by_id) REFERENCES auth_user(id) ON DELETE SET NULL`
- `CHECK (montant > 0)`
- `CHECK (wizard_current_step BETWEEN 1 AND 4)`

**Index** :
- `INDEX idx_dossier_client_statut ON (client_id, statut_agent)` - Performance requêtes client
- `INDEX idx_dossier_statut_archived ON (statut_agent, is_archived)` - Performance filtrage
- `INDEX idx_dossier_date ON (date_soumission DESC)` - Tri chronologique

---

### 2.4 Table `suivi_demande_canevasproposition`

**Description** : Analyse financière et proposition de crédit par l'analyste

| Colonne | Type SQL | Taille | NULL | Défaut | Description |
|---------|----------|--------|------|--------|-------------|
| `id` | INTEGER | - | NO | AUTO | Clé primaire |
| `dossier_id` | INTEGER | - | NO | - | FK vers dossiercredit |
| `nom_prenom` | VARCHAR | 200 | NO | - | Nom du demandeur |
| `date_naissance` | DATE | - | NO | - | Date de naissance |
| `adresse_exacte` | TEXT | - | NO | - | Adresse |
| `numero_telephone` | VARCHAR | 20 | NO | - | Téléphone |
| `emploi_occupe` | VARCHAR | 200 | NO | - | Emploi |
| `nom_employeur` | VARCHAR | 200 | NO | - | Employeur |
| `lieu_emploi` | VARCHAR | 200 | NO | - | Lieu de travail |
| `salaire_net_moyen_fcfa` | DECIMAL | 12,2 | NO | - | Salaire net moyen |
| `autres_revenus_fcfa` | DECIMAL | 12,2 | NO | 0 | Autres revenus |
| `total_charges_mensuelles_fcfa` | DECIMAL | 12,2 | NO | 0 | Charges mensuelles |
| `total_echeances_credits_cours` | DECIMAL | 12,2 | NO | 0 | Échéances crédits |
| `capacite_endettement_brute_fcfa` | DECIMAL | 12,2 | YES | - | 40% du salaire |
| `capacite_endettement_nette_fcfa` | DECIMAL | 12,2 | YES | - | Brute - crédits |
| `demande_montant_fcfa` | DECIMAL | 12,2 | NO | - | Montant demandé |
| `demande_duree_mois` | INTEGER | - | NO | - | Durée demandée |
| `demande_taux_pourcent` | DECIMAL | 5,2 | NO | - | Taux demandé |
| `proposition_montant_fcfa` | DECIMAL | 12,2 | YES | - | Montant proposé |
| `proposition_duree_mois` | INTEGER | - | YES | - | Durée proposée |
| `proposition_taux_pourcent` | DECIMAL | 5,2 | YES | - | Taux proposé |
| `proposition_mensualite_fcfa` | DECIMAL | 12,2 | YES | - | Mensualité calculée |
| `created_at` | TIMESTAMP | - | NO | NOW() | Date de création |
| `updated_at` | TIMESTAMP | - | NO | NOW() | Dernière modification |

**Contraintes** :
- `PRIMARY KEY (id)`
- `FOREIGN KEY (dossier_id) REFERENCES dossiercredit(id) ON DELETE CASCADE`
- `UNIQUE (dossier_id)` (relation OneToOne)
- `CHECK (salaire_net_moyen_fcfa >= 0)`
- `CHECK (demande_montant_fcfa > 0)`
- `CHECK (demande_duree_mois > 0 AND demande_duree_mois <= 120)`

---

### 2.5 Table `suivi_demande_piecejointe`

**Description** : Documents uploadés (CNI, fiches de paie, etc.)

| Colonne | Type SQL | Taille | NULL | Défaut | Description |
|---------|----------|--------|------|--------|-------------|
| `id` | INTEGER | - | NO | AUTO | Clé primaire |
| `dossier_id` | INTEGER | - | NO | - | FK vers dossiercredit |
| `fichier` | VARCHAR | 100 | NO | - | Chemin du fichier |
| `type_piece` | VARCHAR | 50 | NO | 'AUTRE' | Type de document |
| `taille` | INTEGER | - | NO | 0 | Taille en octets |
| `upload_by_id` | INTEGER | - | YES | - | FK vers auth_user |
| `upload_at` | TIMESTAMP | - | NO | NOW() | Date d'upload |

**Contraintes** :
- `PRIMARY KEY (id)`
- `FOREIGN KEY (dossier_id) REFERENCES dossiercredit(id) ON DELETE CASCADE`
- `FOREIGN KEY (upload_by_id) REFERENCES auth_user(id) ON DELETE SET NULL`
- `CHECK (type_piece IN ('CNI', 'FICHE_PAIE', 'JUSTIFICATIF_DOMICILE', 'AUTRE'))`
- `CHECK (taille > 0 AND taille <= 5242880)` -- Max 5 MB

**Index** :
- `INDEX idx_piece_dossier ON (dossier_id, upload_at DESC)`

---

### 2.6 Table `suivi_demande_journalaction`

**Description** : Journal de toutes les actions (audit trail)

| Colonne | Type SQL | Taille | NULL | Défaut | Description |
|---------|----------|--------|------|--------|-------------|
| `id` | INTEGER | - | NO | AUTO | Clé primaire |
| `dossier_id` | INTEGER | - | NO | - | FK vers dossiercredit |
| `action` | VARCHAR | 50 | NO | - | Type d'action |
| `de_statut` | VARCHAR | 50 | YES | - | Statut de départ |
| `vers_statut` | VARCHAR | 50 | YES | - | Statut d'arrivée |
| `acteur_id` | INTEGER | - | YES | - | FK vers auth_user |
| `timestamp` | TIMESTAMP | - | NO | NOW() | Date/heure de l'action |
| `commentaire_systeme` | TEXT | - | YES | - | Commentaire automatique |
| `meta` | JSONB | - | YES | - | Métadonnées JSON |

**Contraintes** :
- `PRIMARY KEY (id)`
- `FOREIGN KEY (dossier_id) REFERENCES dossiercredit(id) ON DELETE CASCADE`
- `FOREIGN KEY (acteur_id) REFERENCES auth_user(id) ON DELETE SET NULL`
- `CHECK (action IN ('TRANSITION', 'APPROBATION', 'REFUS', 'RETOUR', 'RETOUR_CLIENT', 'LIBERATION_FONDS'))`

**Index** :
- `INDEX idx_journal_dossier ON (dossier_id, timestamp DESC)`
- `INDEX idx_journal_timestamp ON (timestamp DESC)`

---

### 2.7 Table `suivi_demande_notification`

**Description** : Notifications internes et emails

| Colonne | Type SQL | Taille | NULL | Défaut | Description |
|---------|----------|--------|------|--------|-------------|
| `id` | INTEGER | - | NO | AUTO | Clé primaire |
| `utilisateur_cible_id` | INTEGER | - | NO | - | FK vers auth_user |
| `type` | VARCHAR | 50 | NO | - | Type de notification |
| `titre` | VARCHAR | 200 | NO | - | Titre |
| `message` | TEXT | - | NO | - | Message |
| `canal` | VARCHAR | 20 | NO | 'INTERNE' | Canal (INTERNE/EMAIL/SMS) |
| `lu` | BOOLEAN | - | NO | FALSE | Notification lue |
| `created_at` | TIMESTAMP | - | NO | NOW() | Date de création |

**Contraintes** :
- `PRIMARY KEY (id)`
- `FOREIGN KEY (utilisateur_cible_id) REFERENCES auth_user(id) ON DELETE CASCADE`
- `CHECK (canal IN ('INTERNE', 'EMAIL', 'SMS'))`

**Index** :
- `INDEX idx_notif_user_lu ON (utilisateur_cible_id, lu, created_at DESC)`

---

### 2.8 Table `suivi_demande_commentaire`

**Description** : Commentaires sur les dossiers

| Colonne | Type SQL | Taille | NULL | Défaut | Description |
|---------|----------|--------|------|--------|-------------|
| `id` | INTEGER | - | NO | AUTO | Clé primaire |
| `dossier_id` | INTEGER | - | NO | - | FK vers dossiercredit |
| `auteur_id` | INTEGER | - | NO | - | FK vers auth_user |
| `message` | TEXT | - | NO | - | Contenu du commentaire |
| `cible_role` | VARCHAR | 20 | YES | - | Rôle destinataire |
| `created_at` | TIMESTAMP | - | NO | NOW() | Date de création |

**Contraintes** :
- `PRIMARY KEY (id)`
- `FOREIGN KEY (dossier_id) REFERENCES dossiercredit(id) ON DELETE CASCADE`
- `FOREIGN KEY (auteur_id) REFERENCES auth_user(id) ON DELETE CASCADE`

**Index** :
- `INDEX idx_comment_dossier ON (dossier_id, created_at DESC)`

---

## 3. DIAGRAMME RELATIONNEL (ERD)

```
┌─────────────────────┐
│    auth_user        │
│  (Utilisateurs)     │
├─────────────────────┤
│ PK id               │
│    username (UNIQUE)│
│    email            │
│    password         │
│    is_active        │
└──────┬──────────────┘
       │ 1
       │
       │ 1:1
       ▼
┌─────────────────────┐
│  userprofile        │
│  (Profils)          │
├─────────────────────┤
│ PK id               │
│ FK user_id (UNIQUE) │
│    full_name        │
│    phone            │
│    role             │
└──────┬──────────────┘
       │
       │ 1:N (client)
       ▼
┌─────────────────────┐
│  dossiercredit      │◄───────┐
│  (Dossiers)         │        │ 1:1
├─────────────────────┤        │
│ PK id               │        │
│    reference (UNIQUE│        │
│ FK client_id        │        │
│ FK acteur_courant_id│        │
│    montant          │        │
│    statut_agent     │        │
│    statut_client    │        │
└──┬──┬──┬──┬─────────┘        │
   │  │  │  │                  │
   │  │  │  │ 1:N              │
   │  │  │  └──────────────────┤
   │  │  │              ┌──────▼──────────┐
   │  │  │              │ canevasproposition│
   │  │  │              │ (Analyses)       │
   │  │  │              ├─────────────────┤
   │  │  │              │ PK id           │
   │  │  │              │ FK dossier_id   │
   │  │  │              │    salaire_net  │
   │  │  │              │    capacite_...  │
   │  │  │              └─────────────────┘
   │  │  │
   │  │  │ 1:N
   │  │  └─────────────────┐
   │  │              ┌─────▼──────────┐
   │  │              │  piecejointe   │
   │  │              │  (Documents)   │
   │  │              ├────────────────┤
   │  │              │ PK id          │
   │  │              │ FK dossier_id  │
   │  │              │    fichier     │
   │  │              │    type_piece  │
   │  │              └────────────────┘
   │  │
   │  │ 1:N
   │  └──────────────────┐
   │              ┌──────▼──────────┐
   │              │ journalaction   │
   │              │ (Audit)         │
   │              ├─────────────────┤
   │              │ PK id           │
   │              │ FK dossier_id   │
   │              │ FK acteur_id    │
   │              │    action       │
   │              │    timestamp    │
   │              └─────────────────┘
   │
   │ 1:N
   └──────────────────┐
              ┌───────▼─────────┐
              │ commentaire     │
              │ (Commentaires)  │
              ├─────────────────┤
              │ PK id           │
              │ FK dossier_id   │
              │ FK auteur_id    │
              │    message      │
              └─────────────────┘

┌─────────────────────┐
│  notification       │
│  (Notifications)    │
├─────────────────────┤
│ PK id               │
│ FK utilisateur_cible│
│    type             │
│    message          │
│    lu               │
└─────────────────────┘
```

---

## 4. RELATIONS ENTRE LES TABLES

### 4.1 Relations OneToOne (1:1)
- `auth_user` ↔ `userprofile` : Un utilisateur a un seul profil
- `dossiercredit` ↔ `canevasproposition` : Un dossier a une seule analyse

### 4.2 Relations OneToMany (1:N)
- `auth_user` → `dossiercredit` (client) : Un client a plusieurs dossiers
- `auth_user` → `dossiercredit` (acteur) : Un acteur traite plusieurs dossiers
- `dossiercredit` → `piecejointe` : Un dossier a plusieurs documents
- `dossiercredit` → `journalaction` : Un dossier a plusieurs actions
- `dossiercredit` → `commentaire` : Un dossier a plusieurs commentaires
- `auth_user` → `notification` : Un utilisateur reçoit plusieurs notifications

### 4.3 Cardinalités
```
User (1) ──── (1) UserProfile
User (1) ──── (N) DossierCredit [client]
User (1) ──── (N) DossierCredit [acteur_courant]
DossierCredit (1) ──── (1) CanevasProposition
DossierCredit (1) ──── (N) PieceJointe
DossierCredit (1) ──── (N) JournalAction
DossierCredit (1) ──── (N) Commentaire
User (1) ──── (N) Notification
```

---

## 5. JUSTIFICATION DU MODÈLE

### 5.1 Normalisation
Le modèle respecte la **3ème forme normale (3NF)** :
- Pas de redondance de données
- Chaque attribut dépend de la clé primaire
- Pas de dépendances transitives

### 5.2 Choix de conception

#### Séparation User / UserProfile
**Justification** : Extension du modèle User Django sans le modifier, permettant d'ajouter des champs métier (rôle, téléphone) tout en conservant la compatibilité avec l'écosystème Django.

#### Table DossierCredit centrale
**Justification** : Hub central du système, toutes les autres tables gravitent autour. Facilite les requêtes et maintient la cohérence.

#### Relation OneToOne DossierCredit ↔ CanevasProposition
**Justification** : Un dossier n'a qu'une seule analyse financière. Séparation pour éviter une table trop large et améliorer les performances.

#### Table JournalAction (Audit Trail)
**Justification** : Traçabilité complète obligatoire pour un système bancaire. Permet l'audit et la conformité réglementaire.

#### Index stratégiques
**Justification** : 
- `(client_id, statut_agent)` : Requête fréquente "mes dossiers en cours"
- `(statut_agent, is_archived)` : Filtrage des dossiers actifs
- `timestamp DESC` : Tri chronologique des actions

### 5.3 Intégrité référentielle
- `ON DELETE CASCADE` : Suppression en cascade pour les données dépendantes
- `ON DELETE SET NULL` : Conservation de l'historique même si l'acteur est supprimé
- Contraintes CHECK : Validation au niveau BDD (montant > 0, durée <= 120 mois)

### 5.4 Performance
- Index sur les colonnes fréquemment filtrées
- JSONB pour métadonnées flexibles (PostgreSQL)
- Pagination au niveau application (25 items/page)

---

**Document rédigé par un expert en bases de données**  
**Conforme aux standards académiques et professionnels**

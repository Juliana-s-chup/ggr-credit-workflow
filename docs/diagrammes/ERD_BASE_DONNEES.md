# 🗄️ DIAGRAMME ERD - BASE DE DONNÉES

## Diagramme Entité-Relation (ERD)

```mermaid
erDiagram
    auth_user ||--o{ suivi_demande_userprofile : "1:1"
    auth_user ||--o{ suivi_demande_dossiercredit : "client"
    auth_user ||--o{ suivi_demande_dossiercredit : "acteur_courant"
    auth_user ||--o{ suivi_demande_journalaction : "acteur"
    auth_user ||--o{ suivi_demande_notification : "utilisateur_cible"
    auth_user ||--o{ suivi_demande_commentaire : "auteur"
    auth_user ||--o{ suivi_demande_piecejointe : "upload_by"
    
    suivi_demande_dossiercredit ||--|| suivi_demande_canevasproposition : "1:1"
    suivi_demande_dossiercredit ||--o{ suivi_demande_piecejointe : "dossier"
    suivi_demande_dossiercredit ||--o{ suivi_demande_journalaction : "dossier"
    suivi_demande_dossiercredit ||--o{ suivi_demande_notification : "dossier"
    suivi_demande_dossiercredit ||--o{ suivi_demande_commentaire : "dossier"
    
    auth_user {
        int id PK
        string username UK
        string email
        string password
        boolean is_active
        boolean is_staff
        datetime date_joined
    }
    
    suivi_demande_userprofile {
        int id PK
        int user_id FK,UK
        string full_name
        string phone
        string address
        string role
        datetime created_at
    }
    
    suivi_demande_dossiercredit {
        int id PK
        string reference UK
        int client_id FK
        string produit
        decimal montant
        string statut_agent
        string statut_client
        int acteur_courant_id FK
        boolean is_archived
        datetime date_soumission
        datetime date_maj
    }
    
    suivi_demande_canevasproposition {
        int id PK
        int dossier_id FK,UK
        string nom_prenom
        date date_naissance
        string adresse_exacte
        string numero_telephone
        string emploi_occupe
        decimal salaire_net_moyen_fcfa
        decimal demande_montant_fcfa
        int demande_duree_mois
        decimal capacite_endettement_nette_fcfa
    }
    
    suivi_demande_piecejointe {
        int id PK
        int dossier_id FK
        string fichier
        string type_piece
        int taille
        int upload_by_id FK
        datetime upload_at
    }
    
    suivi_demande_journalaction {
        int id PK
        int dossier_id FK
        string action
        string de_statut
        string vers_statut
        int acteur_id FK
        text commentaire_systeme
        datetime timestamp
        json meta
    }
    
    suivi_demande_notification {
        int id PK
        int utilisateur_cible_id FK
        string type
        string titre
        text message
        boolean lu
        string canal
        datetime created_at
    }
    
    suivi_demande_commentaire {
        int id PK
        int dossier_id FK
        int auteur_id FK
        text message
        string cible_role
        datetime created_at
    }
```

## Légende

- **PK**: Primary Key (Clé primaire)
- **FK**: Foreign Key (Clé étrangère)
- **UK**: Unique Key (Contrainte d'unicité)
- **||--||**: Relation 1:1
- **||--o{**: Relation 1:N

## Contraintes d'Intégrité

### Contraintes CHECK
```sql
ALTER TABLE suivi_demande_dossiercredit 
ADD CONSTRAINT montant_positif CHECK (montant > 0);

ALTER TABLE suivi_demande_canevasproposition 
ADD CONSTRAINT salaire_positif CHECK (salaire_net_moyen_fcfa > 0);

ALTER TABLE suivi_demande_canevasproposition 
ADD CONSTRAINT duree_positive CHECK (demande_duree_mois > 0);
```

### Index pour Performances
```sql
CREATE INDEX idx_dossier_statut_agent ON suivi_demande_dossiercredit(statut_agent);
CREATE INDEX idx_dossier_client ON suivi_demande_dossiercredit(client_id);
CREATE INDEX idx_dossier_date ON suivi_demande_dossiercredit(date_soumission);
CREATE INDEX idx_journal_dossier ON suivi_demande_journalaction(dossier_id);
CREATE INDEX idx_journal_timestamp ON suivi_demande_journalaction(timestamp);
```

## Normalisation

### Forme Normale 3 (3NF)

Le schéma respecte la 3NF:
- **1NF**: Toutes les colonnes contiennent des valeurs atomiques
- **2NF**: Pas de dépendances partielles (toutes les clés sont simples)
- **3NF**: Pas de dépendances transitives

**Exemple**: 
- `capacite_endettement_nette_fcfa` dépend de `salaire_net_moyen_fcfa` et `total_echeances_credits_cours`
- Ces champs sont dans la même table `canevasproposition` (pas de dépendance transitive)

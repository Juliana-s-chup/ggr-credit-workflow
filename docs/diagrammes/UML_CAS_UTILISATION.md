# 📊 DIAGRAMME UML - CAS D'UTILISATION

## Diagramme de Cas d'Utilisation

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor Client as C
actor Gestionnaire as G
actor Analyste as A
actor "Responsable GGR" as R
actor BOE as B
actor "Super Admin" as SA

rectangle "Système GGR Credit Workflow" {
  
  package "Portail Client" {
    usecase (S'inscrire) as UC1
    usecase (Se connecter) as UC2
    usecase (Soumettre demande crédit) as UC3
    usecase (Remplir canevas) as UC4
    usecase (Uploader pièces jointes) as UC5
    usecase (Consulter statut dossier) as UC6
    usecase (Recevoir notifications) as UC7
    usecase (Modifier dossier brouillon) as UC8
  }
  
  package "Portail Professionnel" {
    usecase (Créer dossier client) as UC9
    usecase (Transmettre à analyste) as UC10
    usecase (Analyser dossier) as UC11
    usecase (Proposer décision) as UC12
    usecase (Valider/Refuser dossier) as UC13
    usecase (Libérer fonds) as UC14
    usecase (Consulter rapports) as UC15
    usecase (Archiver dossier) as UC16
    usecase (Ajouter commentaire) as UC17
    usecase (Retourner au client) as UC18
  }
  
  package "Administration" {
    usecase (Gérer utilisateurs) as UC19
    usecase (Configurer système) as UC20
    usecase (Consulter logs) as UC21
    usecase (Exporter données) as UC22
  }
}

' Relations Client
C --> UC1
C --> UC2
C --> UC3
C --> UC4
C --> UC5
C --> UC6
C --> UC7
C --> UC8

' Relations Gestionnaire
G --> UC2
G --> UC9
G --> UC10
G --> UC6
G --> UC15
G --> UC16
G --> UC17
G --> UC18

' Relations Analyste
A --> UC2
A --> UC11
A --> UC12
A --> UC6
A --> UC15
A --> UC17

' Relations Responsable GGR
R --> UC2
R --> UC13
R --> UC6
R --> UC15
R --> UC17

' Relations BOE
B --> UC2
B --> UC14
B --> UC6
B --> UC15

' Relations Super Admin
SA --> UC2
SA --> UC19
SA --> UC20
SA --> UC21
SA --> UC22
SA --> UC15

' Extensions et inclusions
UC3 ..> UC4 : <<include>>
UC3 ..> UC5 : <<include>>
UC9 ..> UC4 : <<include>>
UC10 ..> UC17 : <<extend>>
UC11 ..> UC17 : <<extend>>
UC13 ..> UC17 : <<extend>>

@enduml
```

## Description des Cas d'Utilisation

### Portail Client

| ID | Cas d'Utilisation | Acteur | Description |
|----|-------------------|--------|-------------|
| UC1 | S'inscrire | Client | Créer un compte avec email, téléphone, adresse |
| UC2 | Se connecter | Tous | Authentification username/password |
| UC3 | Soumettre demande crédit | Client | Créer une nouvelle demande de crédit |
| UC4 | Remplir canevas | Client, Gestionnaire | Compléter le formulaire de proposition (4 étapes) |
| UC5 | Uploader pièces jointes | Client | Télécharger CNI, fiches de paie, etc. |
| UC6 | Consulter statut dossier | Tous | Voir l'état d'avancement du dossier |
| UC7 | Recevoir notifications | Client | Notifications email/internes sur changements |
| UC8 | Modifier dossier brouillon | Client | Modifier avant soumission finale |

### Portail Professionnel

| ID | Cas d'Utilisation | Acteur | Description |
|----|-------------------|--------|-------------|
| UC9 | Créer dossier client | Gestionnaire | Créer un dossier pour un client (guichet) |
| UC10 | Transmettre à analyste | Gestionnaire | Envoyer le dossier à l'analyste crédit |
| UC11 | Analyser dossier | Analyste | Étudier la solvabilité, risques |
| UC12 | Proposer décision | Analyste | Recommander approbation/refus |
| UC13 | Valider/Refuser dossier | Responsable GGR | Décision finale sur le crédit |
| UC14 | Libérer fonds | BOE | Débloquer les fonds approuvés |
| UC15 | Consulter rapports | Tous pros | Voir KPI, statistiques, graphiques |
| UC16 | Archiver dossier | Gestionnaire | Archiver dossiers terminés |
| UC17 | Ajouter commentaire | Tous pros | Commenter un dossier |
| UC18 | Retourner au client | Gestionnaire, Analyste | Demander complément d'information |

### Administration

| ID | Cas d'Utilisation | Acteur | Description |
|----|-------------------|--------|-------------|
| UC19 | Gérer utilisateurs | Super Admin | CRUD utilisateurs, rôles |
| UC20 | Configurer système | Super Admin | Paramètres, constantes métier |
| UC21 | Consulter logs | Super Admin | Audit trail, sécurité |
| UC22 | Exporter données | Super Admin | Export CSV, Excel, rapports |

## Relations

- **<<include>>**: Relation obligatoire (UC3 inclut toujours UC4 et UC5)
- **<<extend>>**: Relation optionnelle (UC10 peut étendre UC17 si commentaire ajouté)

## Préconditions et Postconditions

### UC3: Soumettre demande crédit

**Préconditions:**
- Client authentifié
- Profil client complet

**Postconditions:**
- Dossier créé avec statut NOUVEAU
- Entrée JournalAction créée
- Notification envoyée au gestionnaire

### UC13: Valider/Refuser dossier

**Préconditions:**
- Dossier au statut EN_COURS_VALIDATION_GGR
- Analyste a proposé une décision
- Responsable GGR authentifié

**Postconditions:**
- Statut changé vers APPROUVE_ATTENTE_FONDS ou REFUSE
- Entrée JournalAction créée
- Notification envoyée au client
- Si approuvé: dossier transmis au BOE

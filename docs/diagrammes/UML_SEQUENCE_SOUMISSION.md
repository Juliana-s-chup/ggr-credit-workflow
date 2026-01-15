# 🔄 DIAGRAMME UML - SÉQUENCE

## Diagramme de Séquence: Soumission Dossier de Crédit

```plantuml
@startuml
actor Client
participant "Portail Web" as Web
participant "Django View" as View
participant "DossierCredit" as Dossier
participant "CanevasProposition" as Canevas
participant "PieceJointe" as Piece
participant "JournalAction" as Journal
participant "Notification" as Notif
database PostgreSQL as DB

Client -> Web: Accéder à /client/demande/nouvelle/
activate Web
Web -> View: nouvelle_demande_view(request)
activate View
View -> View: Vérifier authentification
View -> View: Vérifier rôle CLIENT
View --> Web: Formulaire étape 1
deactivate View
Web --> Client: Afficher formulaire
deactivate Web

== Étape 1: Informations de base ==

Client -> Web: Soumettre étape 1 (produit, montant, durée)
activate Web
Web -> View: POST /client/demande/etape/1/
activate View
View -> View: Valider formulaire
View -> Dossier: create(client, produit, montant)
activate Dossier
Dossier -> DB: INSERT INTO suivi_demande_dossiercredit
activate DB
DB --> Dossier: id=123
deactivate DB
Dossier --> View: dossier_123
deactivate Dossier

View -> Journal: create(dossier, action=CREATION)
activate Journal
Journal -> DB: INSERT INTO suivi_demande_journalaction
Journal --> View: journal_entry
deactivate Journal

View --> Web: Redirection étape 2
deactivate View
Web --> Client: Formulaire étape 2
deactivate Web

== Étape 2: Informations personnelles ==

Client -> Web: Soumettre étape 2 (nom, adresse, emploi)
activate Web
Web -> View: POST /client/demande/etape/2/
activate View
View -> Canevas: create(dossier, nom_prenom, emploi...)
activate Canevas
Canevas -> DB: INSERT INTO suivi_demande_canevasproposition
Canevas --> View: canevas
deactivate Canevas
View --> Web: Redirection étape 3
deactivate View
Web --> Client: Formulaire étape 3
deactivate Web

== Étape 3: Capacité d'endettement ==

Client -> Web: Soumettre étape 3 (salaire, échéances)
activate Web
Web -> View: POST /client/demande/etape/3/
activate View
View -> Canevas: update(salaire_net_moyen_fcfa, ...)
activate Canevas
Canevas -> Canevas: calculer_capacite_endettement()
Canevas -> DB: UPDATE suivi_demande_canevasproposition
Canevas --> View: canevas_updated
deactivate Canevas
View --> Web: Redirection étape 4
deactivate View
Web --> Client: Formulaire étape 4 (upload)
deactivate Web

== Étape 4: Pièces jointes ==

Client -> Web: Uploader CNI
activate Web
Web -> View: POST /client/demande/upload/
activate View
View -> Piece: create(dossier, fichier, type=CNI)
activate Piece
Piece -> DB: INSERT INTO suivi_demande_piecejointe
Piece --> View: piece_jointe
deactivate Piece
View -> Canevas: update_doc_flags_from_pieces()
activate Canevas
Canevas -> DB: UPDATE doc_cni_ok=True
deactivate Canevas
View --> Web: Success
deactivate View
Web --> Client: Pièce uploadée
deactivate Web

Client -> Web: Uploader Fiche de paie
activate Web
Web -> View: POST /client/demande/upload/
activate View
View -> Piece: create(dossier, fichier, type=FICHE_PAIE)
activate Piece
Piece -> DB: INSERT INTO suivi_demande_piecejointe
Piece --> View: piece_jointe
deactivate Piece
View -> Canevas: update_doc_flags_from_pieces()
activate Canevas
Canevas -> DB: UPDATE doc_fiche_paie_ok=True
deactivate Canevas
View --> Web: Success
deactivate View
Web --> Client: Pièce uploadée
deactivate Web

== Soumission finale ==

Client -> Web: Cliquer "Soumettre définitivement"
activate Web
Web -> View: POST /client/demande/soumettre/
activate View
View -> View: Vérifier toutes pièces présentes
View -> Dossier: update(wizard_completed=True, statut_agent=TRANSMIS_ANALYSTE)
activate Dossier
Dossier -> DB: UPDATE suivi_demande_dossiercredit
Dossier --> View: dossier_updated
deactivate Dossier

View -> Journal: create(dossier, action=TRANSITION, vers_statut=TRANSMIS_ANALYSTE)
activate Journal
Journal -> DB: INSERT INTO suivi_demande_journalaction
Journal --> View: journal_entry
deactivate Journal

View -> Notif: create(utilisateur=gestionnaire, type=NOUVEAU_DOSSIER)
activate Notif
Notif -> DB: INSERT INTO suivi_demande_notification
Notif --> View: notification
deactivate Notif

View -> Notif: create(utilisateur=client, type=CONFIRMATION_SOUMISSION)
activate Notif
Notif -> DB: INSERT INTO suivi_demande_notification
Notif --> View: notification
deactivate Notif

View --> Web: Redirection dashboard + message succès
deactivate View
Web --> Client: "Dossier soumis avec succès"
deactivate Web

@enduml
```

## Description du Flux

### Phase 1: Initialisation (Étape 1)
1. Client accède au formulaire de nouvelle demande
2. Django vérifie l'authentification et le rôle
3. Client remplit produit, montant, durée
4. Django crée le `DossierCredit` avec statut NOUVEAU
5. Entrée `JournalAction` créée (action=CREATION)

### Phase 2: Informations Personnelles (Étape 2)
1. Client remplit nom, adresse, emploi, situation familiale
2. Django crée le `CanevasProposition` lié au dossier

### Phase 3: Capacité d'Endettement (Étape 3)
1. Client saisit salaire, échéances en cours
2. Django calcule automatiquement:
   - Capacité brute = 40% du salaire
   - Capacité nette = Capacité brute - échéances
3. Mise à jour du `CanevasProposition`

### Phase 4: Pièces Jointes (Étape 4)
1. Client uploade CNI, fiches de paie, etc.
2. Django crée des `PieceJointe` pour chaque fichier
3. Mise à jour automatique des flags documents (doc_cni_ok, etc.)

### Phase 5: Soumission Finale
1. Client valide la soumission
2. Django vérifie que toutes les pièces obligatoires sont présentes
3. Mise à jour du dossier:
   - `wizard_completed = True`
   - `statut_agent = TRANSMIS_ANALYSTE`
4. Création d'une entrée `JournalAction` (TRANSITION)
5. Notifications envoyées:
   - Au gestionnaire (nouveau dossier à traiter)
   - Au client (confirmation de soumission)

## Temps de Réponse Estimés

| Étape | Temps moyen | Requêtes DB |
|-------|-------------|-------------|
| Étape 1 | 200ms | 2 (INSERT dossier + journal) |
| Étape 2 | 150ms | 1 (INSERT canevas) |
| Étape 3 | 180ms | 1 (UPDATE canevas) |
| Étape 4 (par pièce) | 300ms | 2 (INSERT piece + UPDATE canevas) |
| Soumission finale | 250ms | 4 (UPDATE dossier + INSERT journal + 2 notifications) |

**Total pour un dossier complet**: ~1.5-2 secondes (4 pièces jointes)

# ✅ RÔLE CLIENT DÉFINITIF - ACCÈS EN LECTURE SEULE

**Date** : 5 novembre 2025  
**Statut** : VALIDÉ ET CORRIGÉ

---

## 🔒 CLIENT = ACCÈS EN LECTURE SEULE

Le client a un **accès limité en consultation uniquement**. Il ne peut effectuer **AUCUNE modification** sur son dossier.

---

## ✅ CE QUE LE CLIENT PEUT FAIRE

### 1. Consulter l'état d'avancement de sa demande
- Voir le statut actuel de son dossier
- Suivre la progression dans le workflow
- Connaître l'acteur en charge

### 2. Suivre le statut en temps réel
- Dashboard avec statistiques personnelles
- Liste de ses demandes
- Historique des actions

### 3. Recevoir des notifications
- **Email** : Notifications importantes (création, changement statut, décision)
- **Portail** : Badge de notifications non lues
- Consultation de l'historique des notifications

### 4. Télécharger ses documents
- Accès à tous les documents uploadés
- Téléchargement en PDF/JPG/PNG
- Visualisation de la liste complète

### 5. Lire les commentaires du gestionnaire
- Consultation des échanges
- Lecture des demandes de compléments
- Historique complet des communications

### 6. Gérer son profil
- Modifier : email, téléphone, adresse
- Changer son mot de passe
- Consulter ses informations

---

## ❌ CE QUE LE CLIENT NE PEUT PAS FAIRE

### 1. Créer une demande de crédit
→ **Seul le gestionnaire** crée les demandes en agence

### 2. Modifier une demande existante
→ **Seul le gestionnaire** peut modifier les informations

### 3. Ajouter des documents
→ **Seul le gestionnaire** peut ajouter des documents au dossier

### 4. Ajouter des commentaires
→ **Seul le gestionnaire** peut communiquer via le système

### 5. Changer le statut d'un dossier
→ Réservé aux professionnels (gestionnaire, analyste, GGR, BOE)

### 6. Voir les dossiers d'autres clients
→ Isolation stricte des données

---

## 📋 MATRICE DES PERMISSIONS

| Action | Client | Gestionnaire | Analyste | Resp. GGR | BOE | Admin |
|--------|--------|--------------|----------|-----------|-----|-------|
| **CONSULTATION** |
| Voir ses dossiers | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Voir tous dossiers | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Télécharger documents | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Lire commentaires | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **MODIFICATION** |
| Créer demande | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Ajouter documents | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| Ajouter commentaires | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Transmettre analyste | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Créer canevas | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Approuver/Refuser | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Libérer fonds | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **ADMINISTRATION** |
| Gérer utilisateurs | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🔄 WORKFLOW COMPLET

```
┌─────────────────────────────────────────────────────────────┐
│                    PROCESSUS DE DEMANDE                      │
└─────────────────────────────────────────────────────────────┘

1. CLIENT (EN AGENCE)
   ├─> Prend rendez-vous avec le gestionnaire
   ├─> Apporte ses documents physiques
   │   ├─> CNI
   │   ├─> 3 fiches de paie
   │   └─> Justificatif de domicile
   └─> Fournit ses informations au gestionnaire

2. GESTIONNAIRE (EN AGENCE)
   ├─> Reçoit le client
   ├─> Collecte les informations
   ├─> Se connecte au portail PRO (port 8002)
   ├─> Crée la demande (wizard 4 étapes)
   │   ├─> Étape 1 : Infos personnelles
   │   ├─> Étape 2 : Infos financières
   │   ├─> Étape 3 : Demande de crédit
   │   └─> Étape 4 : Upload documents
   └─> Soumet la demande

3. SYSTÈME
   ├─> Crée le dossier (statut NOUVEAU)
   ├─> Génère référence unique (DOS-2025-XXX)
   ├─> Envoie email au client
   └─> Notifie le gestionnaire

4. CLIENT (DEPUIS CHEZ LUI - PORTAIL CLIENT)
   ├─> Reçoit email de notification
   ├─> Se connecte au portail CLIENT (port 8001)
   ├─> Consulte sa demande (LECTURE SEULE)
   │   ├─> Référence du dossier
   │   ├─> Montant demandé
   │   ├─> Statut actuel
   │   ├─> Documents uploadés
   │   └─> Commentaires du gestionnaire
   ├─> Suit l'avancement en temps réel
   ├─> Télécharge ses documents si besoin
   └─> Lit les commentaires

5. GESTIONNAIRE (WORKFLOW)
   ├─> Vérifie la complétude du dossier
   ├─> Transmet à l'analyste (si complet)
   └─> Retourne au client (si incomplet)
       └─> Ajoute commentaire : "Documents manquants"

6. CLIENT (NOTIFICATION)
   ├─> Reçoit notification de changement de statut
   ├─> Se connecte au portail
   ├─> Lit le commentaire du gestionnaire
   └─> Contacte le gestionnaire pour fournir les compléments

7. GESTIONNAIRE (AJOUT COMPLÉMENTS)
   ├─> Reçoit les documents du client (en agence ou email)
   ├─> Ajoute les documents au dossier
   └─> Retransmet à l'analyste

8. WORKFLOW CONTINUE...
   └─> Analyste → GGR → BOE → FONDS_LIBERE
```

---

## 💡 POUR TOUTE MODIFICATION

### Le client doit contacter son gestionnaire

**Cas d'usage** :
- ❓ Documents manquants → Apporter en agence ou envoyer par email au gestionnaire
- ❓ Informations incorrectes → Contacter le gestionnaire pour correction
- ❓ Ajout d'informations → Informer le gestionnaire
- ❓ Questions sur le dossier → Appeler ou visiter l'agence

**Coordonnées** :
- 📧 Email : gestionnaire@ggr-credit.cg
- ☎️ Téléphone : +242 XX XXX XX XX
- 🏢 Agence : Lundi-Vendredi 8h-17h

---

## 📊 STATUTS VISIBLES PAR LE CLIENT

Le client voit des **statuts simplifiés** :

| Statut interne (système) | Statut visible client | Signification |
|---------------------------|----------------------|---------------|
| NOUVEAU | EN ATTENTE | Dossier soumis, en attente de traitement |
| TRANSMIS_ANALYSTE | EN COURS DE TRAITEMENT | Analyse en cours |
| EN_COURS_VALIDATION_GGR | EN COURS DE TRAITEMENT | Validation en cours |
| TRANSMIS_RESP_GEST | SE RAPPROCHER DU GESTIONNAIRE | Documents ou infos manquants |
| RETOUR_CLIENT | SE RAPPROCHER DU GESTIONNAIRE | Action requise |
| APPROUVE_ATTENTE_FONDS | TERMINÉ - APPROUVÉ | Crédit approuvé |
| FONDS_LIBERE | TERMINÉ - APPROUVÉ | Fonds libérés |
| REFUSE | TERMINÉ - REFUSÉ | Crédit refusé |

---

## 🎯 AVANTAGES DE CE MODÈLE

### Pour le client
- ✅ Transparence totale (suivi en temps réel)
- ✅ Disponibilité 24/7 (consultation)
- ✅ Moins de déplacements en agence
- ✅ Notifications automatiques

### Pour la banque
- ✅ Contrôle total sur les données
- ✅ Traçabilité complète
- ✅ Réduction des erreurs
- ✅ Conformité réglementaire

### Pour le gestionnaire
- ✅ Saisie unique en agence
- ✅ Validation des informations
- ✅ Communication centralisée
- ✅ Historique complet

---

## 🔐 SÉCURITÉ

### Isolation des données
- Chaque client voit **uniquement ses propres dossiers**
- Aucun accès aux dossiers d'autres clients
- Vérification à chaque requête

### Permissions strictes
- Décorateurs Django : `@login_required`, `@role_required`
- Vérification au niveau de la base de données
- Logging de toutes les tentatives d'accès

### Traçabilité
- Journal complet des actions
- Qui a consulté quoi et quand
- Audit trail pour conformité

---

## 📄 DOCUMENTS CORRIGÉS

Les documents suivants reflètent maintenant le **rôle correct du client** :

1. ✅ **CDC_PARTIE1_PRESENTATION.md**
   - Matrice des permissions mise à jour
   - Diagramme UC corrigé (UC01-UC07 pour client)
   
2. ✅ **GUIDE_UTILISATEUR.md**
   - Note "Accès en lecture seule" ajoutée
   - Sections "Ajouter document" et "Ajouter commentaire" supprimées
   - FAQ mise à jour
   
3. ✅ **CORRECTIONS_ROLE_CLIENT.md**
   - Workflow corrigé
   - Rôles clarifiés

---

## ✅ VALIDATION FINALE

**Le rôle du client est maintenant clairement défini** :

```
CLIENT = CONSULTATION UNIQUEMENT
GESTIONNAIRE = CRÉATION ET MODIFICATION
```

**Aucune ambiguïté possible** ✓

---

**Document validé le 5 novembre 2025**  
**Toutes les documentations sont cohérentes**

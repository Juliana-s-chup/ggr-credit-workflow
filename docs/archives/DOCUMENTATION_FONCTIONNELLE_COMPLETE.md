# 📋 DOCUMENTATION FONCTIONNELLE COMPLÈTE
## Système de Gestion des Demandes de Crédit Bancaire

**Version** : 1.0 | **Date** : 4 novembre 2025

---

## 1. DESCRIPTION GÉNÉRALE

### 1.1 Présentation
**GGR Credit Workflow** est une application web de gestion des demandes de crédit bancaire qui digitalise et automatise le processus d'octroi de crédit dans une institution financière congolaise.

### 1.2 Périmètre
Le système couvre l'intégralité du cycle de vie d'une demande de crédit :
- Création de la demande par le gestionnaire pour le client
- Consultation et suivi par le client (lecture seule)
- Vérification par le gestionnaire
- Analyse de solvabilité par l'analyste
- Validation par le responsable GGR
- Libération des fonds par le BOE

---

## 2. BESOIN MÉTIER

### 2.1 Problématiques
**Pour les clients** :
- Déplacements multiples à l'agence
- Manque de visibilité sur l'état d'avancement
- Délais d'attente importants

**Pour la banque** :
- Gestion manuelle chronophage
- Absence de traçabilité
- Difficultés de coordination entre services
- Impossibilité de générer des statistiques

### 2.2 Solution apportée
Plateforme web permettant :
- Création des demandes par le gestionnaire et suivi en ligne 24h/24 par le client
- Workflow automatisé entre services
- Traçabilité complète des actions
- Notifications automatiques
- Tableaux de bord en temps réel

---

## 3. OBJECTIFS DU SYSTÈME

### 3.1 Objectifs quantifiables
- Réduire les délais de traitement de 15 à 7 jours (-50%)
- Réduire les déplacements clients de 3-4 à 0-1
- Augmenter la satisfaction client de 60% à 85%
- Réduire les erreurs de saisie de 15% à 5%

### 3.2 Objectifs qualitatifs
- Améliorer l'expérience client
- Optimiser la productivité des équipes
- Assurer la traçabilité complète
- Faciliter le pilotage par les indicateurs

---

## 4. ACTEURS DU SYSTÈME

### 4.1 Client
**Rôle** : Bénéficiaire (consultation uniquement)  
**Actions** : Consulter le statut, télécharger ses documents, lire les commentaires du gestionnaire, recevoir des notifications  
**Accès** : Portail Client (port 8001)

### 4.2 Gestionnaire
**Rôle** : Vérification complétude  
**Actions** : Transmettre à l'analyste, retourner au client  
**Workflow** : NOUVEAU → TRANSMIS_ANALYSTE

### 4.3 Analyste
**Rôle** : Analyse de solvabilité  
**Actions** : Créer canevas, calculer capacité endettement, transmettre au GGR  
**Workflow** : TRANSMIS_ANALYSTE → EN_COURS_VALIDATION_GGR

### 4.4 Responsable GGR
**Rôle** : Décision finale  
**Actions** : Approuver ou refuser  
**Workflow** : EN_COURS_VALIDATION_GGR → APPROUVE ou REFUSE

### 4.5 BOE
**Rôle** : Libération des fonds  
**Actions** : Libérer les fonds  
**Workflow** : APPROUVE_ATTENTE_FONDS → FONDS_LIBERE

### 4.6 Super Admin
**Rôle** : Administration système  
**Actions** : Gérer utilisateurs, attribuer rôles, consulter logs

---

## 5. PARCOURS UTILISATEURS

### 5.1 Parcours Client
```
1. Inscription → Attente activation admin
2. Connexion → Dashboard
3. Consultation de "Mes demandes" (lecture seule)
4. Ouverture du détail d'un dossier → Informations, Pièces (téléchargement), Commentaires (lecture)
5. Suivi des statuts en temps réel et notifications à chaque étape
6. Pour toute modification → contact avec le gestionnaire (en agence / canal interne)
```

### 5.2 Parcours Gestionnaire
```
1. Connexion portail pro
2. Dashboard → Dossiers en attente
3. Vérification complétude
4. Si complet → Transmettre analyste
5. Si incomplet → Retour client (avec commentaire)
```

### 5.3 Parcours Analyste
```
1. Dashboard → Dossiers à analyser
2. Consultation dossier + documents
3. Création canevas proposition :
   - Calcul automatique capacité endettement
   - Proposition montant/durée/taux
4. Transmission au GGR
```

### 5.4 Parcours Responsable GGR
```
1. Dashboard → Dossiers en validation
2. Examen canevas + avis analyste
3. Décision : Approuver ou Refuser
4. Notification client + BOE
```

### 5.5 Parcours BOE
```
1. Dashboard → Dossiers approuvés
2. Vérification conditions engagement
3. Libération des fonds
4. Clôture dossier
```

---

## 6. CAS D'UTILISATION

### UC01 : Créer une demande de crédit pour un client
**Acteur** : Gestionnaire  
**Précondition** : Connecté en tant que gestionnaire  
**Flux** : Wizard 4 étapes (saisie des infos client) → Soumission → Dossier créé → Client notifié  
**Postcondition** : Dossier NOUVEAU, notifications envoyées

### UC02 : Transmettre à l'analyste
**Acteur** : Gestionnaire  
**Précondition** : Dossier NOUVEAU  
**Flux** : Vérification → Transmission  
**Postcondition** : Dossier TRANSMIS_ANALYSTE

### UC03 : Créer canevas de proposition
**Acteur** : Analyste  
**Flux** : Saisie données → Calculs automatiques → Proposition  
**Calculs** : Capacité = Salaire × 40% - Crédits en cours

### UC04 : Approuver un dossier
**Acteur** : Responsable GGR  
**Flux** : Examen → Décision → Approbation  
**Postcondition** : Dossier APPROUVE_ATTENTE_FONDS

### UC05 : Libérer les fonds
**Acteur** : BOE  
**Flux** : Vérification → Libération  
**Postcondition** : Dossier FONDS_LIBERE (clôturé)

---

## 7. MODULES FONCTIONNELS

### 7.1 Module Authentification
- Inscription avec validation admin
- Connexion sécurisée
- Gestion des sessions
- Récupération mot de passe

### 7.2 Module Gestion des Demandes
- Wizard guidé 4 étapes
- Validation des données
- Upload de documents (max 5 MB, PDF/JPG/PNG)
- Génération référence unique

### 7.3 Module Workflow
- Transitions automatisées entre statuts
- Contrôle des permissions par rôle
- Journal des actions (traçabilité)
- Notifications automatiques

### 7.4 Module Canevas de Proposition
- Saisie données financières
- Calculs automatiques :
  - Capacité endettement = Salaire × 40%
  - Capacité nette = Brute - Crédits en cours
  - Mensualité = Montant × Taux / (1 - (1 + Taux)^-Durée)
- Génération PDF

### 7.5 Module Notifications
- Notifications internes (dans l'application)
- Emails automatiques
- Historique des notifications

### 7.6 Module Dashboards
- Dashboard par rôle (6 dashboards différents)
- KPI en temps réel
- Graphiques et statistiques
- Historique des actions

### 7.7 Module Administration
- Gestion des utilisateurs
- Attribution des rôles
- Activation/désactivation comptes
- Consultation logs système

---

## 8. CONTRAINTES FONCTIONNELLES

### 8.1 Règles métier
1. **Capacité d'endettement** : Maximum 40% du salaire net
2. **Montant minimum** : 100 000 FCFA
3. **Durée maximum** : 120 mois (10 ans)
4. **Documents obligatoires** : CNI + 3 fiches de paie
5. **Âge minimum** : 18 ans

### 8.2 Workflow obligatoire
- Ordre des statuts non modifiable
- Impossible de sauter une étape
- Retour en arrière possible (retour client, retour gestionnaire)
- Traçabilité obligatoire de toutes les actions

### 8.3 Permissions strictes
- Client : accès uniquement à ses propres dossiers
- Séparation des rôles : un utilisateur = un rôle
- Actions limitées selon le rôle et le statut du dossier

---

## 9. CONTRAINTES NON FONCTIONNELLES

### 9.1 Sécurité
- **Authentification** : Obligatoire pour toutes les pages (sauf accueil)
- **Autorisation** : Contrôle d'accès par rôle (RBAC)
- **Protection CSRF** : Activée sur tous les formulaires
- **Validation uploads** : Taille max 5 MB, types autorisés (PDF, JPG, PNG)
- **Logs de sécurité** : Toutes les connexions/déconnexions tracées
- **Isolation des données** : Client ne voit que ses dossiers

### 9.2 Performance
- **Temps de réponse** : < 2 secondes pour les pages standards
- **Pagination** : 25 éléments par page
- **Optimisation requêtes** : select_related() pour éviter N+1
- **Rotation logs** : Automatique (10 MB, 10 backups)

### 9.3 Disponibilité
- **Objectif** : 99% de disponibilité
- **Sauvegarde BDD** : Quotidienne automatique
- **Gestion erreurs** : Messages utilisateur clairs

### 9.4 Ergonomie
- **Responsive** : Compatible mobile/tablette/desktop
- **Navigation intuitive** : Maximum 3 clics pour toute action
- **Messages clairs** : Confirmations et erreurs explicites
- **Aide contextuelle** : Tooltips sur champs complexes

### 9.5 Maintenabilité
- **Code modulaire** : Views séparées par domaine
- **Logging complet** : 5 fichiers de logs spécialisés
- **Tests** : 75 tests (75-80% couverture)
- **Documentation** : 300+ pages

### 9.6 Conformité
- **RGPD** : Consentements explicites
- **Audit** : Traçabilité complète (journal des actions)
- **Standards** : Django best practices, PEP 8

---

## ANNEXES

### Workflow complet
```
NOUVEAU 
  → TRANSMIS_ANALYSTE 
  → EN_COURS_VALIDATION_GGR 
  → APPROUVE_ATTENTE_FONDS 
  → FONDS_LIBERE

Retours possibles :
- NOUVEAU ← Retour client (gestionnaire)
- TRANSMIS_RESP_GEST ← Retour gestionnaire (analyste)
- REFUSE ← Refus (responsable GGR)
```

### Statuts client
- EN_ATTENTE : Dossier soumis
- EN_COURS_TRAITEMENT : En cours d'analyse
- SE_RAPPROCHER_GEST : Compléments requis
- TERMINE : Fonds libérés ou refusé

---

**Document rédigé par un analyste fonctionnel senior**  
**Conforme aux standards de documentation académique et professionnelle**

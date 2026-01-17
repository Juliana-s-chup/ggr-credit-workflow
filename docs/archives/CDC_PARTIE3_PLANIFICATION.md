# 📋 CAHIER DES CHARGES - PARTIE 3
## INTERFACE, PLANIFICATION ET VALIDATION

**Projet** : GGR Credit Workflow  
**Version** : 1.0 | **Date** : 4 novembre 2025

---

## 6. MAQUETTES ET DESCRIPTION INTERFACE UTILISATEUR

### 6.1 Pages principales

#### Page Login

**URL** : `/accounts/login/`

**Éléments** :
- Logo de la banque (centré en haut)
- Formulaire de connexion :
  - Champ "Nom d'utilisateur"
  - Champ "Mot de passe" (masqué)
  - Case "Se souvenir de moi"
  - Bouton "Connexion" (bleu, pleine largeur)
- Lien "Mot de passe oublié ?"
- Lien "Créer un compte"
- Footer avec mentions légales

**Comportements** :
- Validation côté client (champs requis)
- Message d'erreur si identifiants incorrects
- Redirection vers dashboard après connexion
- Désactivation du bouton pendant la soumission

#### Dashboard Client

**URL** : `/dashboard/`

**Sections** :
1. **Header** :
   - Logo + nom de l'application
   - Nom de l'utilisateur
   - Icône notifications (badge si non lues)
   - Bouton "Déconnexion"

2. **Résumé (Cards)** :
   - Demandes en cours (nombre + icône)
   - Demandes approuvées (nombre + icône vert)
   - Demandes refusées (nombre + icône rouge)
   - Montant total demandé (FCFA)

3. **Mes dossiers en cours** :
   - Tableau avec colonnes :
     - Référence
     - Montant
     - Statut (badge coloré)
     - Date
     - Actions (bouton "Voir")
   - Pagination (25 par page)

4. **Actions rapides** :
   - Bouton "Nouvelle demande" (vert, prominent)
   - Bouton "Mes demandes"
   - Bouton "Notifications"

5. **Historique récent** :
   - 5 dernières actions
   - Format : "Date - Action - Dossier"

**Comportements** :
- Actualisation automatique des stats
- Filtres sur le tableau (statut, date)
- Tri des colonnes
- Responsive (collapse sur mobile)

#### Page Gestion des Demandes (Wizard)

**URL** : `/demande/step1/`, `/demande/step2/`, etc.

**Étape 1 : Informations personnelles**

**Éléments** :
- Indicateur de progression (1/4)
- Formulaire avec sections :
  - Identité (nom, prénom, date naissance)
  - Contact (adresse, téléphone)
  - Emploi (poste, employeur, ancienneté)
  - Situation familiale
- Boutons :
  - "Suivant" (bleu, à droite)
  - "Annuler" (gris, à gauche)

**Validation** :
- Tous les champs obligatoires
- Date de naissance valide (18+ ans)
- Format téléphone (+242...)
- Messages d'erreur sous chaque champ

**Étape 2 : Informations financières**

**Éléments** :
- Indicateur de progression (2/4)
- Formulaire :
  - Salaire net moyen (FCFA)
  - Autres revenus (FCFA)
  - Charges mensuelles (FCFA)
  - Personnes à charge (nombre)
  - Crédits en cours (Oui/Non)
  - Si oui : Total échéances (FCFA)
- Boutons :
  - "Précédent"
  - "Suivant"

**Validation** :
- Montants > 0
- Calcul automatique du reste à vivre

**Étape 3 : Demande de crédit**

**Éléments** :
- Indicateur de progression (3/4)
- Formulaire :
  - Type de crédit (select)
  - Montant demandé (FCFA, min 100 000)
  - Durée souhaitée (mois, max 120)
  - Objet du financement (textarea)
  - Garanties proposées (checkboxes)
- Boutons :
  - "Précédent"
  - "Suivant"

**Validation** :
- Montant >= 100 000 FCFA
- Durée entre 1 et 120 mois
- Objet min 50 caractères

**Étape 4 : Documents et validation**

**Éléments** :
- Indicateur de progression (4/4)
- Upload de documents :
  - CNI (obligatoire)
  - 3 fiches de paie (obligatoire)
  - Justificatif domicile (obligatoire)
  - Autres documents (optionnel)
- Checkboxes :
  - Acceptation traitement données
  - Acceptation vérification informations
  - Acceptation conditions générales
- Récapitulatif :
  - Résumé des informations saisies
  - Liste des documents uploadés
- Boutons :
  - "Précédent"
  - "Soumettre ma demande" (vert, large)

**Validation** :
- 3 documents minimum
- Taille < 5 MB chacun
- Format PDF/JPG/PNG
- Toutes les cases cochées

**Comportements** :
- Sauvegarde automatique à chaque étape
- Possibilité de reprendre plus tard
- Barre de progression visuelle
- Confirmation avant soumission

#### Dashboard Gestionnaire

**URL** : `/dashboard/`

**Sections** :
1. **Statistiques** :
   - Dossiers en attente (NOUVEAU)
   - Dossiers retournés (TRANSMIS_RESP_GEST)
   - Dossiers traités aujourd'hui
   - Délai moyen de traitement

2. **Dossiers à traiter** :
   - Tableau avec filtres
   - Colonnes : Référence, Client, Montant, Date, Actions
   - Actions : "Voir", "Transmettre", "Retour client"

3. **Activité récente** :
   - Dernières actions effectuées
   - Graphique des dossiers traités (7 derniers jours)

**Comportements** :
- Actualisation en temps réel
- Notifications sonores (optionnel)
- Filtres avancés (date, montant, statut)

#### Page Détail Dossier

**URL** : `/dossier/<id>/`

**Onglets** :

**1. Informations**
- Référence, statut, dates
- Informations client
- Informations demande
- Acteur en charge

**2. Documents**
- Liste des documents
- Bouton "Télécharger" pour chaque
- Bouton "Ajouter un document" (si autorisé)
- Prévisualisation PDF (iframe)

**3. Commentaires**
- Fil de discussion
- Formulaire d'ajout de commentaire
- Historique complet

**4. Historique**
- Journal des actions
- Timeline visuelle
- Filtres par type d'action

**5. Canevas** (si existe)
- Affichage du canevas de proposition
- Données financières
- Calculs automatiques
- Bouton "Télécharger PDF"

**Actions selon le rôle** :
- Client : Ajouter document, commenter
- Gestionnaire : Transmettre, retour client
- Analyste : Créer canevas, transmettre GGR
- Resp. GGR : Approuver, refuser
- BOE : Libérer fonds

#### Page Statistiques (Admin)

**URL** : `/statistics/`

**Sections** :
1. **Vue d'ensemble** :
   - KPI principaux (cards)
   - Graphique évolution (line chart)

2. **Par statut** :
   - Répartition des dossiers (pie chart)
   - Tableau détaillé

3. **Par acteur** :
   - Performances individuelles (bar chart)
   - Délai moyen par acteur

4. **Temporel** :
   - Évolution mensuelle (line chart)
   - Saisonnalité

5. **Exports** :
   - Bouton "Exporter en CSV"
   - Bouton "Exporter en PDF"
   - Filtres de date

**Comportements** :
- Graphiques interactifs (hover pour détails)
- Filtres dynamiques
- Actualisation automatique

### 6.2 Comportements UX/UI attendus

#### Feedback utilisateur

**Messages de succès** :
- Toast vert en haut à droite
- Icône ✓
- Disparition automatique après 3 secondes

**Messages d'erreur** :
- Toast rouge en haut à droite
- Icône ✗
- Reste affiché jusqu'à fermeture manuelle

**Messages d'information** :
- Toast bleu
- Icône ℹ
- Disparition après 5 secondes

#### États de chargement

**Boutons** :
- Spinner + texte "Chargement..."
- Désactivation pendant le traitement
- Retour à l'état normal après

**Pages** :
- Skeleton screens pour les tableaux
- Spinner centré pour les pages complètes
- Barre de progression pour les uploads

#### Responsive

**Desktop (> 1200px)** :
- Layout 3 colonnes
- Sidebar fixe
- Tableaux complets

**Tablette (768-1200px)** :
- Layout 2 colonnes
- Sidebar collapsible
- Tableaux avec scroll horizontal

**Mobile (< 768px)** :
- Layout 1 colonne
- Menu burger
- Cards au lieu de tableaux

---

## 7. PLANIFICATION ET DÉCOUPAGE DU PROJET

### 7.1 Tâches principales

#### Phase 1 : Analyse et conception (4 semaines)

| Tâche | Durée | Livrables |
|-------|-------|-----------|
| Analyse des besoins | 1 sem | Cahier des charges |
| Modélisation UML | 1 sem | Diagrammes (use case, séquence, classes) |
| Conception BDD | 1 sem | MCD, MLD, dictionnaire de données |
| Maquettage | 1 sem | Wireframes, maquettes |

#### Phase 2 : Développement backend (8 semaines)

| Tâche | Durée | Livrables |
|-------|-------|-----------|
| Setup projet Django | 1 sem | Structure projet, settings |
| Modèles et migrations | 2 sem | 8 modèles, migrations |
| Authentification | 1 sem | Login, logout, permissions |
| Workflow et transitions | 2 sem | Logique métier, décorateurs |
| Canevas et calculs | 1 sem | Calculs automatiques |
| Notifications et emails | 1 sem | Système de notifications |

#### Phase 3 : Développement frontend (6 semaines)

| Tâche | Durée | Livrables |
|-------|-------|-----------|
| Templates de base | 1 sem | base.html, partials |
| Pages authentification | 1 sem | Login, signup |
| Wizard demande | 2 sem | 4 étapes, validation |
| Dashboards | 1 sem | 6 dashboards par rôle |
| Pages détail et listes | 1 sem | Dossiers, notifications |

#### Phase 4 : Tests et qualité (4 semaines)

| Tâche | Durée | Livrables |
|-------|-------|-----------|
| Tests unitaires | 2 sem | 50+ tests |
| Tests d'intégration | 1 sem | 20+ tests |
| Tests de sécurité | 1 sem | Tests permissions, CSRF |

#### Phase 5 : Déploiement et formation (4 semaines)

| Tâche | Durée | Livrables |
|-------|-------|-----------|
| Préparation production | 1 sem | Configuration serveur |
| Déploiement | 1 sem | Application en production |
| Documentation | 1 sem | Guides utilisateur et technique |
| Formation utilisateurs | 1 sem | Sessions de formation |

**Durée totale** : 26 semaines (6 mois)

### 7.2 Étapes de développement

#### Sprint 1-2 : Foundation (4 semaines)
- Setup projet
- Modèles de base
- Authentification
- Templates de base

#### Sprint 3-4 : Core Features (4 semaines)
- Création de demande (wizard)
- Workflow de base
- Dashboards clients

#### Sprint 5-6 : Professional Features (4 semaines)
- Dashboards professionnels
- Canevas de proposition
- Transitions workflow

#### Sprint 7-8 : Advanced Features (4 semaines)
- Notifications
- Statistiques
- Génération PDF

#### Sprint 9-10 : Polish & Testing (4 semaines)
- Tests complets
- Corrections bugs
- Optimisations

#### Sprint 11-12 : Deployment (4 semaines)
- Déploiement
- Documentation
- Formation

### 7.3 Priorités (MoSCoW)

#### Must Have (Indispensable)
- ✅ Authentification et gestion des comptes
- ✅ Création de demande (wizard 4 étapes)
- ✅ Workflow complet (7 statuts)
- ✅ Dashboards par rôle
- ✅ Gestion des documents (upload, download)
- ✅ Permissions par rôle (RBAC)
- ✅ Notifications internes
- ✅ Journal des actions (audit trail)

#### Should Have (Important)
- ✅ Canevas de proposition avec calculs
- ✅ Génération PDF
- ✅ Statistiques de base
- ✅ Commentaires sur dossiers
- ✅ Emails automatiques
- ✅ Système de logging

#### Could Have (Souhaitable)
- ⚠️ Statistiques avancées (graphiques)
- ⚠️ Export CSV/Excel
- ⚠️ Recherche avancée
- ⚠️ Filtres multiples
- ⚠️ Archivage automatique

#### Won't Have (Hors périmètre v1)
- ❌ Signature électronique
- ❌ Notifications SMS
- ❌ Application mobile native
- ❌ Intégration avec core banking
- ❌ Chat en temps réel

### 7.4 Livrables

#### Livrables de conception
- Cahier des charges complet
- Diagrammes UML (use case, séquence, classes)
- Modèle de données (MCD, MLD)
- Maquettes UI/UX
- Spécifications techniques

#### Livrables de développement
- Code source (GitHub)
- Base de données (scripts SQL)
- Fichiers de configuration
- Tests automatisés (75 tests)
- Documentation du code (docstrings)

#### Livrables de déploiement
- Application déployée et fonctionnelle
- Guide d'installation
- Guide de déploiement
- Scripts de backup

#### Livrables de documentation
- Documentation fonctionnelle (50+ pages)
- Documentation technique (50+ pages)
- Guide utilisateur (30+ pages)
- Guide administrateur (20+ pages)
- FAQ (10+ questions)

---

## 8. CRITÈRES DE VALIDATION

### 8.1 Critères par fonctionnalité

#### F1 : Authentification

**Critères** :
- [ ] Un utilisateur peut s'inscrire avec username/email/password
- [ ] Le compte est inactif par défaut
- [ ] Un admin peut activer le compte
- [ ] L'utilisateur reçoit un email de confirmation
- [ ] Un utilisateur peut se connecter avec ses identifiants
- [ ] La session expire après 30 min d'inactivité
- [ ] Un utilisateur peut se déconnecter
- [ ] Les connexions sont loggées

**Tests** :
- Test unitaire : création d'utilisateur
- Test d'intégration : workflow complet inscription → activation → connexion
- Test de sécurité : tentative de connexion avec mauvais identifiants

#### F2 : Création de demande

**Critères** :
- [ ] Le wizard affiche 4 étapes
- [ ] Chaque étape valide les données
- [ ] Les données sont sauvegardées à chaque étape
- [ ] L'utilisateur peut revenir en arrière
- [ ] Les documents sont uploadés (max 5 MB, PDF/JPG/PNG)
- [ ] Un dossier est créé avec statut NOUVEAU
- [ ] Une référence unique est générée (DOS-YYYY-NNN)
- [ ] Le client et le gestionnaire reçoivent une notification

**Tests** :
- Test unitaire : validation de chaque formulaire
- Test d'intégration : soumission complète du wizard
- Test de sécurité : upload de fichier malveillant (rejeté)

#### F3 : Workflow

**Critères** :
- [ ] Seuls les rôles autorisés peuvent effectuer une transition
- [ ] Les transitions respectent le workflow défini
- [ ] Chaque transition est loggée dans le journal
- [ ] Les acteurs concernés reçoivent une notification
- [ ] Le statut client est mis à jour
- [ ] L'acteur courant est mis à jour

**Tests** :
- Test unitaire : vérification des permissions par rôle
- Test d'intégration : workflow complet NOUVEAU → FONDS_LIBERE
- Test de sécurité : tentative de transition non autorisée (refusée)

#### F4 : Canevas de proposition

**Critères** :
- [ ] L'analyste peut créer un canevas
- [ ] Les données du dossier sont pré-remplies
- [ ] La capacité d'endettement est calculée automatiquement (40%)
- [ ] La capacité nette = brute - crédits en cours
- [ ] La mensualité est calculée selon la formule
- [ ] Un PDF peut être généré
- [ ] Le canevas est sauvegardé

**Tests** :
- Test unitaire : calculs financiers (capacité, mensualité)
- Test d'intégration : création et sauvegarde du canevas
- Test fonctionnel : génération du PDF

#### F5 : Dashboards

**Critères** :
- [ ] Chaque rôle a son dashboard spécifique
- [ ] Les statistiques sont correctes
- [ ] Les dossiers affichés correspondent au rôle
- [ ] La pagination fonctionne (25 par page)
- [ ] Les filtres fonctionnent
- [ ] Le dashboard est responsive

**Tests** :
- Test unitaire : calcul des statistiques
- Test d'intégration : affichage du dashboard par rôle
- Test fonctionnel : navigation et filtres

### 8.2 Tests prévus

#### Tests unitaires (50 tests)

**Modèles** (15 tests) :
- Création d'objets
- Validation des contraintes
- Relations entre modèles
- Méthodes custom

**Formulaires** (15 tests) :
- Validation des champs
- Messages d'erreur
- Données valides/invalides
- Nettoyage des données

**Permissions** (10 tests) :
- Vérification des rôles
- Isolation des données
- Décorateurs custom
- Accès refusé

**Calculs** (10 tests) :
- Capacité d'endettement
- Mensualité
- Taux d'endettement
- Reste à vivre

#### Tests d'intégration (20 tests)

**Workflow** (8 tests) :
- Workflow complet (NOUVEAU → FONDS_LIBERE)
- Retours (RETOUR_CLIENT, TRANSMIS_RESP_GEST)
- Refus
- Notifications à chaque étape

**Parcours utilisateur** (7 tests) :
- Inscription → Activation → Connexion
- Création demande complète (wizard)
- Consultation et modification
- Déconnexion

**Sécurité** (5 tests) :
- Protection CSRF
- Isolation des données
- Permissions par rôle
- Upload de fichiers

#### Tests fonctionnels (5 tests)

**End-to-end** :
- Parcours client complet
- Parcours gestionnaire
- Parcours analyste
- Parcours responsable GGR
- Parcours BOE

**Couverture cible** : 75-80%

---

## 9. RISQUES ET LIMITES

### 9.1 Risques techniques

#### Risque 1 : Performance avec gros volumes

**Description** : Ralentissement avec 10 000+ dossiers

**Probabilité** : Moyenne  
**Impact** : Élevé

**Mitigation** :
- Pagination (25 items/page)
- Index sur colonnes fréquentes
- Optimisation requêtes (select_related)
- Cache pour les statistiques

#### Risque 2 : Sécurité des données

**Description** : Accès non autorisé ou fuite de données

**Probabilité** : Faible  
**Impact** : Critique

**Mitigation** :
- RBAC strict
- Isolation des données
- Logging complet
- HTTPS obligatoire
- Backups quotidiens

#### Risque 3 : Disponibilité du serveur

**Description** : Panne du serveur ou de la BDD

**Probabilité** : Faible  
**Impact** : Élevé

**Mitigation** :
- Monitoring 24/7
- Backups automatiques
- Plan de reprise d'activité
- Serveur de secours (optionnel)

### 9.2 Risques fonctionnels

#### Risque 1 : Adoption par les utilisateurs

**Description** : Résistance au changement

**Probabilité** : Moyenne  
**Impact** : Élevé

**Mitigation** :
- Formation complète
- Support dédié
- Interface intuitive
- Communication sur les bénéfices

#### Risque 2 : Évolution des règles métier

**Description** : Changement des règles de crédit

**Probabilité** : Moyenne  
**Impact** : Moyen

**Mitigation** :
- Code modulaire
- Constantes paramétrables
- Documentation complète
- Architecture évolutive

### 9.3 Contraintes de temps

**Délai initial** : 6 mois

**Risques de dépassement** :
- Complexité sous-estimée : +2 semaines
- Bugs critiques : +1 semaine
- Changements de périmètre : +2 semaines

**Buffer** : 1 mois supplémentaire prévu

**Livraison finale** : 7 mois maximum

### 9.4 Limites actuelles de la solution

#### Limites fonctionnelles

**Pas d'intégration core banking** :
- Pas de vérification automatique du compte client
- Pas de libération automatique des fonds
- Saisie manuelle de certaines données

**Pas de signature électronique** :
- Signature physique requise
- Déplacement client pour signature

**Pas d'application mobile native** :
- Version web responsive uniquement
- Expérience mobile limitée

#### Limites techniques

**Hébergement local uniquement** :
- Pas d'accès depuis l'extérieur (sauf VPN)
- Pas de haute disponibilité
- Scalabilité limitée

**Pas de temps réel** :
- Actualisation manuelle requise
- Pas de WebSocket
- Notifications différées

**Exports limités** :
- PDF uniquement
- Pas de CSV/Excel natif
- Pas d'API publique

### 9.5 Évolutions futures (v2)

**Court terme (6 mois)** :
- Signature électronique
- Notifications SMS
- Export CSV/Excel
- Statistiques avancées

**Moyen terme (1 an)** :
- Application mobile native
- Intégration core banking
- Chat en temps réel
- API REST publique

**Long terme (2 ans)** :
- Intelligence artificielle (scoring automatique)
- Blockchain (traçabilité)
- Biométrie (authentification)
- Open Banking

---

## CONCLUSION

Ce cahier des charges définit de manière exhaustive les besoins, les spécifications et les contraintes du projet GGR Credit Workflow. Il constitue le document de référence pour le développement, les tests et la validation de l'application.

**Points clés** :
- Digitalisation complète du processus de crédit
- Workflow automatisé avec 7 statuts
- 6 rôles utilisateurs avec permissions granulaires
- Architecture Django modulaire et scalable
- Sécurité renforcée (RBAC, CSRF, logging)
- Tests complets (75 tests, 75-80% couverture)
- Déploiement en 6 mois

**Succès mesurable** :
- Réduction délais : -50% (15j → 7j)
- Réduction erreurs : -67% (15% → 5%)
- Satisfaction client : +42% (60% → 85%)
- Déplacements client : -75% (3-4 → 0-1)

---

**FIN DU CAHIER DES CHARGES**  
**Document complet en 3 parties**

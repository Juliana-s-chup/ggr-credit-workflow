# 📖 GUIDE UTILISATEUR - GGR CREDIT WORKFLOW

**Manuel d'utilisation pour les clients**  
**Version** : 1.0 | **Date** : 4 novembre 2025

---

## TABLE DES MATIÈRES

1. [Premiers pas](#1-premiers-pas)
2. [Créer un compte](#2-créer-un-compte)
3. [Se connecter](#3-se-connecter)
4. [Consulter le tableau de bord](#4-consulter-le-tableau-de-bord)
5. [Suivre mes demandes](#5-suivre-mes-demandes)
6. [Gérer mon profil](#6-gérer-mon-profil)
7. [Consulter les notifications](#7-consulter-les-notifications)
8. [Se déconnecter](#8-se-déconnecter)
9. [Questions fréquentes](#9-questions-fréquentes)

---

## 1. PREMIERS PAS

### 1.1 Accéder à l'application

1. Ouvrez votre navigateur web (Chrome, Firefox, Edge, Safari)
2. Saisissez l'adresse fournie par votre banque (ex: **http://127.0.0.1:8001**)
3. Vous êtes automatiquement redirigé vers la **page de connexion**

### 1.2 Page de connexion (nouveau)

La page de connexion est **l’unique point d’entrée** de l’application. Elle contient :
- **Deux onglets** :
  - Onglet **Client** (lecture seule)
  - Onglet **Professionnel** (gestionnaire, analyste, GGR, BOE, admin)
- **Formulaire de connexion** commun (identifiant + mot de passe)
- **Lien "Pas de compte ? S’inscrire"** : ouvre la page d’inscription (`/accounts/signup/`)

Remarque : Il n’y a pas de page d’accueil. Toute visite de l’adresse principale redirige vers la page de connexion.
- **Bouton "S'inscrire"** : Pour créer un nouveau compte
- **Informations** sur les services de crédit

---

## 2. CRÉER UN COMPTE

### 2.1 Étapes d'inscription

**Étape 1 : Accéder au formulaire**
1. Cliquez sur le bouton **"S'inscrire"** en haut à droite
2. Le formulaire d'inscription s'affiche

**Étape 2 : Remplir le formulaire**

Remplissez les champs suivants :

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Nom d'utilisateur** | Votre identifiant unique | jean.dupont |
| **Email** | Votre adresse email | jean.dupont@email.com |
| **Mot de passe** | Minimum 8 caractères | ••••••••• |
| **Confirmer mot de passe** | Retapez le même mot de passe | ••••••••• |

**Étape 3 : Valider**
1. Cliquez sur le bouton **"S'inscrire"**
2. Un message de confirmation s'affiche

### 2.2 Activation du compte

⚠️ **Important** : Votre compte doit être activé par un administrateur.

**Après l'inscription** :
1. Vous êtes redirigé vers une page "En attente d'approbation"
2. Un administrateur de la banque va activer votre compte (délai : 24-48h)
3. Vous recevrez un email de confirmation une fois votre compte activé
4. Vous pourrez alors vous connecter

### 2.3 Conseils pour le mot de passe

✅ **Bon mot de passe** :
- Au moins 8 caractères
- Mélange de lettres et chiffres
- Au moins une majuscule
- Exemple : `MonMotDePasse2025!`

❌ **Mauvais mot de passe** :
- Trop court : `123456`
- Trop simple : `password`
- Informations personnelles : `jeandupont`

---

## 3. SE CONNECTER

### 3.1 Connexion standard

**Étape 1 : Accéder à la page de connexion**
1. Cliquez sur **"Se connecter"** en haut à droite
2. Ou allez directement sur : http://127.0.0.1:8001/accounts/login/

**Étape 2 : Saisir vos identifiants**
1. **Nom d'utilisateur** : Tapez votre nom d'utilisateur
2. **Mot de passe** : Tapez votre mot de passe
3. Cochez **"Se souvenir de moi"** si vous êtes sur votre ordinateur personnel

**Étape 3 : Valider**
1. Cliquez sur **"Connexion"**
2. Vous êtes redirigé vers votre tableau de bord

### 3.2 Problèmes de connexion

**❌ "Nom d'utilisateur ou mot de passe incorrect"**
- Vérifiez que vous avez bien tapé votre nom d'utilisateur
- Vérifiez que la touche Majuscule n'est pas activée
- Essayez de copier-coller votre mot de passe

**❌ "Votre compte n'est pas encore activé"**
- Votre compte est en attente d'activation par un administrateur
- Contactez votre agence bancaire

**❌ "Mot de passe oublié"**
- Cliquez sur "Mot de passe oublié ?"
- Suivez les instructions pour réinitialiser votre mot de passe

---

## 4. CONSULTER LE TABLEAU DE BORD

⚠️ **IMPORTANT** : En tant que client, vous avez un **accès en lecture seule**. C'est votre **gestionnaire de compte** à la banque qui crée et gère votre demande de crédit.

**Votre rôle (CONSULTATION uniquement)** :
- ✅ Consulter l'état d'avancement de votre demande
- ✅ Suivre le statut en temps réel
- ✅ Recevoir des notifications (email + portail)
- ✅ Télécharger vos documents
- ✅ Lire les commentaires du gestionnaire

**Vous ne pouvez PAS** :
- ❌ Créer une demande
- ❌ Modifier une demande
- ❌ Ajouter des documents
- ❌ Ajouter des commentaires

💡 **Pour toute modification**, contactez votre gestionnaire de compte en agence.

---

### 4.1 Accéder au tableau de bord

Après connexion, vous êtes automatiquement redirigé vers votre tableau de bord.

Pour y revenir à tout moment :
1. Cliquez sur **"Tableau de bord"** dans le menu
2. Ou sur le logo en haut à gauche

### 4.2 Contenu du tableau de bord

**Section 1 : Résumé**
- Nombre de demandes en cours
- Nombre de demandes approuvées
- Montant total demandé

**Section 2 : Mes dossiers en cours**
- Liste de vos demandes actives
- Statut de chaque demande
- Date de soumission
- Bouton "Voir détail"

**Section 3 : Dossiers traités**
- Historique de vos demandes terminées
- Statut final (Approuvé / Refusé)

**Section 4 : Actions rapides**
- Bouton **"Nouvelle demande"**
- Bouton **"Mes demandes"**
- Bouton **"Notifications"**

**Section 5 : Historique des actions**
- Dernières actions sur vos dossiers
- Date et heure
- Type d'action

---

## 5. SUIVRE MES DEMANDES

### 5.1 Accéder à la liste de mes demandes

1. Cliquez sur **"Mes demandes"** dans le menu
2. La liste de toutes vos demandes s'affiche

### 5.2 Comprendre les statuts

**Statuts visibles pour vous (client) :**

| Statut | Signification | Action requise |
|--------|---------------|----------------|
| **EN ATTENTE** | Dossier soumis, en attente de traitement | Aucune |
| **EN COURS DE TRAITEMENT** | Votre dossier est en cours d'analyse | Aucune |
| **SE RAPPROCHER DU GESTIONNAIRE** | Documents manquants ou informations à compléter | ⚠️ Action requise |
| **TERMINÉ** | Décision finale prise (approuvé ou refusé) | Consulter le résultat |

### 5.3 Consulter le détail d'une demande

**Étape 1 : Ouvrir le détail**
1. Dans "Mes demandes", cliquez sur une ligne
2. Ou cliquez sur le bouton **"Voir détail"**

**Étape 2 : Onglets disponibles**

**Onglet "Informations"**
- Référence du dossier
- Montant demandé
- Statut actuel
- Date de soumission
- Acteur en charge

**Onglet "Documents"**
- Liste des documents uploadés
- Bouton **"Télécharger"** pour chaque document
- Visualisation uniquement (pas d'ajout possible)

**Onglet "Commentaires"**
- Lecture des échanges avec la banque
- Commentaires du gestionnaire
- Visualisation uniquement (pas d'ajout possible)

**Onglet "Historique"**
- Journal de toutes les actions
- Date et heure
- Acteur
- Action effectuée

💡 **Besoin d'ajouter un document ou un commentaire ?**  
Contactez votre gestionnaire de compte en agence. Seul le gestionnaire peut modifier votre dossier.

---

## 6. GÉRER MON PROFIL

### 6.1 Accéder à mon profil

1. Cliquez sur votre nom en haut à droite
2. Sélectionnez **"Mon profil"**

### 6.2 Informations affichées

**Informations personnelles**
- Nom d'utilisateur
- Email
- Nom complet
- Téléphone
- Adresse
- Rôle (CLIENT)
- Date d'inscription

### 6.3 Modifier mes informations

**Informations modifiables :**
- Email
- Téléphone
- Adresse

**Comment modifier ?**
1. Cliquez sur **"Modifier"**
2. Changez les informations souhaitées
3. Cliquez sur **"Enregistrer"**
4. Un message de confirmation s'affiche

**Informations non modifiables :**
- Nom d'utilisateur
- Nom complet
- Rôle

💡 **Pour modifier ces informations**, contactez votre agence bancaire.

### 6.4 Changer mon mot de passe

1. Dans votre profil, cliquez sur **"Changer le mot de passe"**
2. Remplissez le formulaire :
   - Mot de passe actuel
   - Nouveau mot de passe
   - Confirmer le nouveau mot de passe
3. Cliquez sur **"Modifier"**
4. Vous êtes déconnecté automatiquement
5. Reconnectez-vous avec votre nouveau mot de passe

---

## 7. CONSULTER LES NOTIFICATIONS

### 7.1 Accéder aux notifications

**Méthode 1 : Icône de notification**
1. Cliquez sur l'icône 🔔 en haut à droite
2. Le nombre de notifications non lues s'affiche
3. Un menu déroulant s'ouvre avec les dernières notifications

**Méthode 2 : Page complète**
1. Cliquez sur **"Notifications"** dans le menu
2. La liste complète s'affiche (20 par page)

### 7.2 Types de notifications

**Notifications que vous recevez :**
- ✉️ **Nouveau message** : Commentaire d'un gestionnaire
- 📝 **Mise à jour du dossier** : Changement de statut
- ⚠️ **Compléments requis** : Documents manquants
- ✅ **Décision finale** : Approbation ou refus

### 7.3 Marquer comme lu

**Une seule notification :**
1. Cliquez sur la notification
2. Elle passe automatiquement en "Lu"
3. Le badge de couleur disparaît

**Toutes les notifications :**
1. Cliquez sur **"Marquer toutes comme lues"**
2. Toutes passent en "Lu"

### 7.4 Notifications par email

Vous recevez également des emails pour :
- Création de votre dossier
- Changement de statut important
- Décision finale

💡 **Vérifiez votre boîte email** régulièrement.

---

## 8. SE DÉCONNECTER

### 8.1 Déconnexion standard

**Méthode 1 : Menu utilisateur**
1. Cliquez sur votre nom en haut à droite
2. Sélectionnez **"Se déconnecter"**
3. Vous êtes redirigé vers la page d'accueil

**Méthode 2 : Bouton direct**
1. Cliquez sur le bouton **"Déconnexion"** dans le menu
2. Confirmation immédiate

### 8.2 Déconnexion automatique

⚠️ **Important** : Pour votre sécurité, vous êtes automatiquement déconnecté après :
- **30 minutes d'inactivité** sur ordinateur personnel
- **15 minutes d'inactivité** sur ordinateur public

### 8.3 Bonnes pratiques de sécurité

✅ **À faire** :
- Toujours se déconnecter sur un ordinateur public
- Fermer le navigateur après déconnexion
- Ne jamais partager votre mot de passe

❌ **À ne pas faire** :
- Laisser votre session ouverte sur un ordinateur partagé
- Cocher "Se souvenir de moi" sur un ordinateur public
- Enregistrer votre mot de passe dans le navigateur sur un ordinateur public

---

## 9. QUESTIONS FRÉQUENTES

### 9.1 Compte et connexion

**Q : Combien de temps faut-il pour activer mon compte ?**  
R : Généralement 24 à 48 heures ouvrées. Vous recevrez un email de confirmation.

**Q : J'ai oublié mon mot de passe, que faire ?**  
R : Cliquez sur "Mot de passe oublié ?" sur la page de connexion et suivez les instructions.

**Q : Puis-je changer mon nom d'utilisateur ?**  
R : Non, le nom d'utilisateur est définitif. Contactez votre agence pour créer un nouveau compte.

### 9.2 Demande de crédit

**Q : Comment faire une demande de crédit ?**  
R : Prenez rendez-vous avec votre gestionnaire de compte en agence. Il créera la demande pour vous après avoir collecté vos informations et documents.

**Q : Combien de temps pour traiter ma demande ?**  
R : En moyenne 7 à 15 jours ouvrés selon la complexité du dossier.

**Q : Quels documents sont obligatoires ?**  
R : CNI, 3 dernières fiches de paie, justificatif de domicile. Apportez-les lors de votre rendez-vous avec le gestionnaire.

**Q : Puis-je modifier ma demande après création ?**  
R : Non, mais vous pouvez ajouter des documents complémentaires si le gestionnaire vous le demande.

**Q : Quel est le montant minimum de crédit ?**  
R : 100 000 FCFA.

**Q : Quelle est la durée maximum ?**  
R : 120 mois (10 ans).

### 9.3 Suivi et notifications

**Q : Comment savoir où en est mon dossier ?**  
R : Consultez "Mes demandes" ou votre tableau de bord. Le statut est mis à jour en temps réel.

**Q : Je n'ai pas reçu de notification, est-ce normal ?**  
R : Vérifiez vos spams. Assurez-vous que votre email est correct dans votre profil.

**Q : Que signifie "SE RAPPROCHER DU GESTIONNAIRE" ?**  
R : Des documents ou informations complémentaires sont requis. Consultez les commentaires.

### 9.4 Problèmes techniques

**Q : Le site ne s'affiche pas correctement**  
R : 
- Videz le cache de votre navigateur
- Essayez un autre navigateur (Chrome, Firefox)
- Vérifiez votre connexion internet

**Q : Je ne peux pas télécharger un document**  
R :
- Vérifiez que le fichier fait moins de 5 MB
- Vérifiez le format (PDF, JPG, PNG uniquement)
- Essayez de compresser le fichier

**Q : Le site est lent**  
R :
- Vérifiez votre connexion internet
- Fermez les autres onglets
- Essayez plus tard (moins d'affluence)

### 9.5 Contact et support

**Q : Comment contacter le support ?**  
R : 
- Email : support@ggr-credit.cg
- Téléphone : +242 XX XXX XX XX
- Agence : Visitez votre agence bancaire

**Q : Horaires du support**  
R : Lundi à Vendredi, 8h00 - 17h00 (heure locale)

---

## ANNEXE : RACCOURCIS CLAVIER

| Raccourci | Action |
|-----------|--------|
| `Ctrl + D` | Aller au tableau de bord |
| `Ctrl + N` | Nouvelle demande |
| `Ctrl + M` | Mes demandes |
| `Ctrl + L` | Se déconnecter |

---

## GLOSSAIRE

**CNI** : Carte Nationale d'Identité  
**FCFA** : Franc de la Communauté Financière Africaine  
**CDI** : Contrat à Durée Indéterminée  
**CDD** : Contrat à Durée Déterminée  
**BOE** : Back Office Engagement (service qui libère les fonds)  
**GGR** : Gestion des Garanties et Risques  
**Canevas** : Document d'analyse financière créé par l'analyste  

---

**Guide utilisateur rédigé par un rédacteur technique**  
**Pour toute question : support@ggr-credit.cg**  
**Version 1.0 - Novembre 2025**

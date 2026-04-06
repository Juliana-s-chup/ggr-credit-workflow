# 📚 DOCUMENTATION SOUTENANCE - PARTIE 1
## Vue d'ensemble et Architecture

**Projet** : GGR Credit Workflow  
**Auteur** : NGUIMBI Juliana  
**Date** : 2026

---

# 1. VUE D'ENSEMBLE DU PROJET

## 1.1 Objectif du projet

**GGR Credit Workflow** est une application web de gestion des dossiers de crédit bancaire.

### En termes simples :
Imaginez une banque qui reçoit des demandes de prêt. Avant, tout se faisait sur papier :
- Le client remplit des formulaires papier
- Les documents circulent de bureau en bureau
- Difficile de savoir où en est le dossier
- Risque de perte de documents
- Processus lent et inefficace

**Votre application résout ce problème** en numérisant tout le processus !

## 1.2 Problème résolu

### Problèmes identifiés :
1. **Manque de traçabilité** : Impossible de savoir où est un dossier
2. **Lenteur du processus** : Les documents circulent physiquement
3. **Risque d'erreur** : Saisie manuelle, documents perdus
4. **Manque de transparence** : Le client ne sait pas où en est sa demande
5. **Difficulté de reporting** : Pas de statistiques en temps réel

### Solutions apportées :
1. ✅ **Traçabilité totale** : Chaque action est enregistrée (qui, quand, quoi)
2. ✅ **Rapidité** : Workflow numérique, notifications automatiques
3. ✅ **Fiabilité** : Validation automatique, pas de perte de données
4. ✅ **Transparence** : Le client suit son dossier en temps réel
5. ✅ **Analytics** : Tableaux de bord et statistiques instantanées

## 1.3 Type d'application

### C'est une **application web full-stack** :

**Frontend** (ce que l'utilisateur voit) :
- Pages HTML avec CSS moderne
- JavaScript pour l'interactivité
- Interface responsive (fonctionne sur mobile/tablette/PC)

**Backend** (la logique métier) :
- Django (framework Python)
- Gestion des utilisateurs, des dossiers, du workflow
- API pour les communications

**Base de données** :
- PostgreSQL (stockage des données)
- Relations complexes entre les tables

**Déploiement** :
- Docker (conteneurisation)
- Nginx (serveur web)
- Gunicorn (serveur d'application)

## 1.4 Public cible

### Utilisateurs de l'application :

1. **Clients** (grand public)
   - Déposent une demande de crédit
   - Uploadent leurs documents
   - Suivent l'avancement de leur dossier

2. **Gestionnaires** (employés banque)
   - Reçoivent les nouvelles demandes
   - Vérifient les documents
   - Transmettent aux analystes

3. **Analystes crédit** (experts risque)
   - Évaluent le risque du crédit
   - Calculent la capacité de remboursement
   - Donnent un avis technique

4. **Responsable GGR** (manager)
   - Valident les dossiers importants
   - Prennent les décisions finales

5. **BOE** (Back Office Engagement)
   - Gèrent la libération des fonds
   - Finalisent les dossiers approuvés

6. **Super Admin** (IT)
   - Gèrent les utilisateurs
   - Administrent le système

---

# 2. ARCHITECTURE GLOBALE

## 2.1 Type d'architecture : MVT (Model-View-Template)

Django utilise le pattern **MVT**, qui est une variante du célèbre **MVC**.

### Explication simple :

Imaginez un restaurant :

**Model (Modèle)** = La cuisine
- C'est là où les données sont préparées
- Les "recettes" (règles métier)
- La base de données

**View (Vue)** = Le serveur
- Reçoit les commandes (requêtes HTTP)
- Va chercher les plats en cuisine (interroge les modèles)
- Apporte les plats au client (renvoie la réponse)

**Template (Gabarit)** = La présentation du plat
- Comment le plat est présenté dans l'assiette
- Le HTML que l'utilisateur voit
- La mise en forme

### Dans votre projet :

```
UTILISATEUR (Client ou Professionnel)
    ↓
    │ 1. Requête HTTP (ex: "Je veux voir mes dossiers")
    ▼
NGINX (Serveur web / Proxy)
    ↓
    │ 2. Transmet à Django
    ▼
DJANGO (MVT)
    │
    ├─→ URLS (urls.py) → Analyse l'URL, détermine quelle View appeler
    │
    ├─→ VIEW (views.py) → Logique métier, vérifie permissions
    │       ↓
    │       │ 3. Demande les données
    │       ▼
    ├─→ MODEL (models.py) → Communique avec PostgreSQL
    │       ↓
    │       │ 4. Retourne les données
    │       ▼
    ├─→ VIEW (suite) → Prépare le contexte
    │       ↓
    │       │ 5. Passe au Template
    │       ▼
    └─→ TEMPLATE (HTML) → Génère le HTML final
            ↓
            │ 6. Renvoie au navigateur
            ▼
UTILISATEUR (Voit la page)
```

## 2.2 Organisation générale

### Architecture en couches :

```
┌────────────────────────────────────┐
│    COUCHE PRÉSENTATION             │
│    - Templates HTML                │
│    - CSS, JavaScript               │
└────────────────┬───────────────────┘
                 │
┌────────────────▼───────────────────┐
│    COUCHE CONTRÔLEUR               │
│    - Views (views.py, etc.)        │
│    - Gestion des requêtes HTTP     │
└────────────────┬───────────────────┘
                 │
┌────────────────▼───────────────────┐
│    COUCHE MÉTIER                   │
│    - Services (DossierService)     │
│    - Règles de gestion             │
└────────────────┬───────────────────┘
                 │
┌────────────────▼───────────────────┐
│    COUCHE DONNÉES                  │
│    - Models (models.py)            │
│    - ORM Django                    │
└────────────────┬───────────────────┘
                 │
┌────────────────▼───────────────────┐
│    BASE DE DONNÉES                 │
│    - PostgreSQL                    │
└────────────────────────────────────┘
```

## 2.3 Séparation des responsabilités

### Principe SOLID appliqué :

**1. Single Responsibility (Responsabilité unique)**
- Chaque fichier a UN rôle précis
- `models.py` → Définit les données
- `views.py` → Gère les requêtes
- `forms.py` → Gère les formulaires

**2. Séparation Frontend / Backend**
- Frontend : `templates/`, `static/`
- Backend : `views.py`, `models.py`, `services/`

**3. Modularité**
- Application `suivi_demande` → Gestion des dossiers
- Application `analytics` → Statistiques et rapports
- Application `core` → Configuration globale

**4. Réutilisabilité**
- `services/` → Logique métier réutilisable
- `decorators.py` → Décorateurs réutilisables
- `validators.py` → Validations réutilisables

---

**Suite dans DOCUMENTATION_SOUTENANCE_PARTIE2.md**

# DOCUMENTATION TECHNIQUE COMPLÈTE
## Système de Gestion de Workflow de Crédit - Crédit du Congo

---

## 📚 STRUCTURE DE LA DOCUMENTATION

Cette documentation est organisée en **8 modules fonctionnels** détaillés :

### **Module 1 : Authentification et Gestion des Utilisateurs**
📄 Fichier : `01_AUTHENTIFICATION_GESTION_UTILISATEURS.md`

**Fonctionnalités couvertes :**
- 1.1. Inscription (Signup)
- 1.2. Connexion (Login)
- 1.3. Gestion des rôles (RBAC)
- 1.4. Activation des comptes (Admin)
- 1.5. Modification des rôles (Admin)

---

### **Module 2 : Gestion des Demandes de Crédit**
📄 Fichier : `02_GESTION_DEMANDES_CREDIT.md`

**Fonctionnalités couvertes :**
- 2.1. Formulaire multi-étapes (Wizard)
- 2.2. Validation des données
- 2.3. Génération de référence unique
- 2.4. Création de dossier par le gestionnaire
- 2.5. Upload de pièces justificatives
- 2.6. Capture photo via webcam

---

### **Module 3 : Workflow et Machine à États**
📄 Fichier : `03_WORKFLOW_MACHINE_ETATS.md`

**Fonctionnalités couvertes :**
- 3.1. États des dossiers (DossierStatutAgent, DossierStatutClient)
- 3.2. Transitions autorisées par rôle
- 3.3. Validation des transitions (@transition_allowed)
- 3.4. Actions de workflow (transmettre_analyste, retour_client, etc.)
- 3.5. Journalisation des actions (JournalAction)

---

### **Module 4 : Système de Notifications**
📄 Fichier : `04_SYSTEME_NOTIFICATIONS.md`

**Fonctionnalités couvertes :**
- 4.1. Notifications in-app
- 4.2. Notifications par email
- 4.3. Utilitaire centralisé (notify())
- 4.4. Notifications multi-acteurs
- 4.5. Badge de compteurs non lus
- 4.6. Marquer comme lu

---

### **Module 5 : Tableaux de Bord (Dashboards)**
📄 Fichier : `05_TABLEAUX_DE_BORD.md`

**Fonctionnalités couvertes :**
- 5.1. Dashboard Client
- 5.2. Dashboard Gestionnaire
- 5.3. Dashboard Analyste
- 5.4. Dashboard Responsable GGR
- 5.5. Dashboard BOE
- 5.6. Dashboard Super Admin
- 5.7. KPI et statistiques
- 5.8. Visualisations graphiques (Chart.js)

---

### **Module 6 : Reporting et Export**
📄 Fichier : `06_REPORTING_EXPORT.md`

**Fonctionnalités couvertes :**
- 6.1. Génération de rapports PDF (xhtml2pdf)
- 6.2. Export Excel XLSX (openpyxl)
- 6.3. Filtres de rapports (période, statut, montant)
- 6.4. Statistiques agrégées
- 6.5. Proposition de crédit PDF

---

### **Module 7 : Archivage et Gestion Documentaire**
📄 Fichier : `07_ARCHIVAGE_GESTION_DOCUMENTAIRE.md`

**Fonctionnalités couvertes :**
- 7.1. Archivage des dossiers terminés
- 7.2. Désarchivage (rôles autorisés)
- 7.3. Consultation des archives
- 7.4. Gestion des pièces jointes
- 7.5. Stockage et organisation des fichiers

---

### **Module 8 : Commentaires et Communication**
📄 Fichier : `08_COMMENTAIRES_COMMUNICATION.md`

**Fonctionnalités couvertes :**
- 8.1. Ajout de commentaires sur dossiers
- 8.2. Commentaires ciblés par rôle
- 8.3. Historique des commentaires
- 8.4. Retours avec motifs (retour_client, retour_gestionnaire)

---

## 📊 SCHÉMA D'ARCHITECTURE GLOBALE



---

## 🗄️ MODÈLE DE DONNÉES GLOBAL

### **Tables principales**

1. **auth_user** (Django built-in)
   - Authentification de base

2. **suivi_demande_userprofile**
   - Extension du profil utilisateur
   - Gestion des rôles

3. **suivi_demande_dossiercredit**
   - Dossiers de crédit
   - Machine à états

4. **suivi_demande_piecejointe**
   - Pièces justificatives uploadées

5. **suivi_demande_commentaire**
   - Commentaires sur dossiers

6. **suivi_demande_journalaction**
   - Historique et audit trail

7. **suivi_demande_notification**
   - Notifications in-app

8. **django_session**
   - Sessions utilisateurs

---

## 🔐 SÉCURITÉ

### **Mécanismes implémentés**
- ✅ CSRF Protection (Django middleware)
- ✅ Password Hashing (PBKDF2, 260k iterations)
- ✅ SQL Injection Protection (Django ORM)
- ✅ XSS Protection (Template auto-escaping)
- ✅ RBAC (Role-Based Access Control)
- ✅ Session Security (HttpOnly, Secure, SameSite)
- ✅ File Upload Validation
- ✅ HTTPS/SSL Support (production)

---

## 📈 MÉTRIQUES ET PERFORMANCES

### **Paramètres de configuration**

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **Session Cookie Age** | 1 209 600 s | 14 jours |
| **Password Min Length** | 8 caractères | Validation |
| **PBKDF2 Iterations** | 260 000 | Hashage |
| **Max Upload Size** | 10 MB | Fichiers |
| **Database Connection Pool** | 20 | PostgreSQL |
| **Static Files Cache** | 31 536 000 s | 1 an |

### **Temps de réponse cibles**
- Page de connexion : < 500 ms
- Dashboard : < 1 s
- Liste dossiers : < 1.5 s
- Détail dossier : < 1 s
- Génération PDF : < 3 s
- Export Excel : < 5 s

---

## 🔄 FLUX DE DONNÉES PRINCIPAUX

### **Flux 1 : Création de demande de crédit**
```
Client → Formulaire multi-étapes → Validation → Création DossierCredit
→ Upload pièces → Notification Gestionnaire → Dashboard Gestionnaire
```

### **Flux 2 : Workflow de validation**
```
Gestionnaire → Transmettre Analyste → Notification Analyste
→ Analyste → Analyse → Transmettre GGR → Notification Resp GGR
→ Resp GGR → Approuver/Refuser → Notification Gestionnaire + Client
→ Si Approuvé → BOE → Libérer Fonds → Notification Client
```

### **Flux 3 : Retour pour corrections**
```
Analyste/Gestionnaire → Retour Client (avec motif) → Notification Client
→ Client → Compléter dossier → Notification Gestionnaire
→ Reprise du workflow
```

---

## 🛠️ TECHNOLOGIES PAR COUCHE

### **Frontend**
- HTML5, CSS3, JavaScript (ES6+)
- Bootstrap 5.3
- Font Awesome 6
- Chart.js 3.x
- Fetch API, Canvas API, MediaDevices API

### **Backend**
- Python 3.10+
- Django 4.2+
- Django ORM
- Django Authentication
- Django Forms & Validators

### **Base de données**
- SQLite (développement)
- PostgreSQL 14+ (production recommandée)

### **Génération de documents**
- xhtml2pdf (PDF)
- openpyxl (Excel)

### **Déploiement**
- Gunicorn / uWSGI
- Nginx / Apache
- Systemd
- Git

---

## 📝 COMMENT UTILISER CETTE DOCUMENTATION

### **Pour votre mémoire**

1. **Chapitre 4 (Analyse et spécification)** :
   - Utilisez les sections "Modèles de données" et "Algorithme et logique"

2. **Chapitre 5 (Conception)** :
   - Utilisez les diagrammes et schémas d'architecture
   - Référencez les matrices de permissions

3. **Chapitre 6 (Implémentation)** :
   - Copiez les extraits de code commentés
   - Expliquez les choix techniques

4. **Chapitre 7 (Tests)** :
   - Utilisez les flux de données pour créer des scénarios de test

5. **Annexes** :
   - Ajoutez les captures d'écran
   - Incluez les extraits de code significatifs

### **Structure recommandée par fonctionnalité**

Pour chaque fonctionnalité dans votre mémoire :

```markdown
#### X.X. [Nom de la fonctionnalité]

**Description** : [Brève description]

**Technologies utilisées** :
- Backend : [liste]
- Frontend : [liste]
- Base de données : [tables]

**Algorithme** :
[Pseudo-code ou description étape par étape]

**Modèle de données** :
[Schéma de table ou diagramme de classes]

**Interface utilisateur** :
[Capture d'écran + description]

**Code significatif** :
```python
[Extrait de code commenté]
```

**Interactions** :
[Avec quels autres modules cette fonctionnalité interagit]
```

---

## 📞 SUPPORT

Pour toute question sur cette documentation :
- Consultez les fichiers détaillés par module
- Référez-vous au code source dans `suivi_demande/`
- Consultez la documentation Django officielle

---

**Bonne rédaction de votre mémoire ! 🎓**

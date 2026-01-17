# 🚀 DÉMARRAGE RAPIDE DES PORTAILS

## ✅ STATUT ACTUEL

Les deux portails fonctionnent correctement !

---

## 📋 COMMANDES DE DÉMARRAGE

### Option 1 : Script automatique (RECOMMANDÉ)

```powershell
.\start_portals_simple.ps1
```

### Option 2 : Démarrage manuel

**Terminal 1 - Portail CLIENT** :
```powershell
python manage.py runserver 8001 --settings=core.settings.client
```

**Terminal 2 - Portail PROFESSIONNEL** :
```powershell
python manage.py runserver 8002 --settings=core.settings.pro
```

---

## 🌐 ACCÈS AUX PORTAILS

| Portail | URL | Port |
|---------|-----|------|
| **Client** | http://127.0.0.1:8001 | 8001 |
| **Professionnel** | http://127.0.0.1:8002 | 8002 |

---

## 🔍 VÉRIFICATION QUE TOUT FONCTIONNE

### 1. Vérifier la configuration

```powershell
# Portail Client
python manage.py check --settings=core.settings.client

# Portail Professionnel
python manage.py check --settings=core.settings.pro
```

**Résultat attendu** : `System check identified no issues (0 silenced).`

### 2. Vérifier les migrations

```powershell
python manage.py showmigrations --settings=core.settings.base
```

**Résultat attendu** : Toutes les migrations doivent avoir un `[X]`

### 3. Lancer les tests

```powershell
python manage.py test suivi_demande --settings=core.settings.base
```

**Résultat attendu** : `Ran 33 tests in X.XXXs` avec `OK`

---

## ⚠️ PROBLÈMES COURANTS ET SOLUTIONS

### Problème 1 : "Port already in use"

**Erreur** : `Error: That port is already in use.`

**Solution** :
```powershell
# Trouver le processus qui utilise le port
netstat -ano | findstr :8001
netstat -ano | findstr :8002

# Tuer le processus (remplacer PID par le numéro trouvé)
taskkill /PID <PID> /F
```

### Problème 2 : "ModuleNotFoundError"

**Erreur** : `ModuleNotFoundError: No module named 'suivi_demande.views.base'`

**Solution** : Le dossier `suivi_demande/views/` ne doit PAS exister
```powershell
# Vérifier
dir suivi_demande

# Si le dossier views/ existe, le supprimer
rmdir /s suivi_demande\views
```

### Problème 3 : "No such table"

**Erreur** : `django.db.utils.OperationalError: no such table`

**Solution** : Appliquer les migrations
```powershell
python manage.py migrate --settings=core.settings.base
```

### Problème 4 : Erreur 404 sur fichiers CSS

**Symptôme** : `[04/Nov/2025 15:49:45] "GET /static/css/charte_graphique.css HTTP/1.1" 404`

**Solution** : Collecter les fichiers statiques
```powershell
python manage.py collectstatic --noinput --settings=core.settings.base
```

**Note** : Cette erreur n'empêche PAS le portail de fonctionner.

---

## 🔐 CONNEXION AUX PORTAILS

### Portail CLIENT (8001)

**Pour les clients** :
- URL : http://127.0.0.1:8001
- Créer un compte via "S'inscrire"
- Attendre l'approbation d'un admin

### Portail PROFESSIONNEL (8002)

**Pour le personnel** :
- URL : http://127.0.0.1:8002/pro/login/
- Utiliser un compte avec rôle professionnel :
  - Gestionnaire
  - Analyste
  - Responsable GGR
  - BOE
  - Super Admin

**Créer un superutilisateur** :
```powershell
python manage.py createsuperuser --settings=core.settings.base
```

---

## 📊 VÉRIFIER LES LOGS

Les logs sont enregistrés dans :
- **Console** : Affichage en temps réel
- **Fichier** : `logs/django.log` (rotation automatique à 10MB)

**Voir les dernières lignes** :
```powershell
Get-Content logs\django.log -Tail 50
```

---

## 🧪 LANCER LES TESTS

### Tous les tests
```powershell
python manage.py test suivi_demande
```

### Tests spécifiques
```powershell
# Tests des modèles
python manage.py test suivi_demande.tests.test_models

# Tests des permissions
python manage.py test suivi_demande.tests.test_permissions

# Tests du workflow
python manage.py test suivi_demande.tests.test_workflow
```

### Avec couverture
```powershell
coverage run --source='.' manage.py test suivi_demande
coverage report
coverage html
```

---

## 🎯 CHECKLIST DE DÉMARRAGE

Avant de commencer à travailler :

- [ ] Activer l'environnement virtuel : `venv\Scripts\Activate.ps1`
- [ ] Vérifier les migrations : `python manage.py showmigrations`
- [ ] Lancer les tests : `python manage.py test suivi_demande`
- [ ] Démarrer le portail CLIENT : Port 8001
- [ ] Démarrer le portail PRO : Port 8002
- [ ] Ouvrir le navigateur sur les deux URLs

---

## 📚 DOCUMENTATION COMPLÈTE

Pour plus de détails, consultez :
- `README_PROFESSIONNEL.md` : Documentation complète
- `GUIDE_BONNES_PRATIQUES_DJANGO.md` : Bonnes pratiques
- `CORRECTIONS_APPLIQUEES.md` : Liste des améliorations

---

## 🆘 SUPPORT

Si vous rencontrez un problème :

1. **Vérifier les logs** : `logs/django.log`
2. **Vérifier la console** : Messages d'erreur
3. **Tester la configuration** : `python manage.py check`

---

**Dernière mise à jour** : 4 novembre 2025  
**Version** : 1.0.0

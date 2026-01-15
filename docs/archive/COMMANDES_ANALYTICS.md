# 🚀 COMMANDES POUR INSTALLER LE MODULE ANALYTICS

## ✅ CORRECTIONS EFFECTUÉES

1. ✅ `analytics` ajouté dans `INSTALLED_APPS` (`core/settings/base.py`)
2. ✅ URLs analytics ajoutées dans `core/urls.py`
3. ✅ Décorateur `role_required` créé dans `core/security.py`

---

## 📋 COMMANDES À EXÉCUTER (DANS L'ORDRE)

### 1. Créer le dossier ML models
```bash
mkdir analytics\ml_models
```

### 2. Créer les migrations
```bash
python manage.py makemigrations analytics
```

**Résultat attendu** :
```
Migrations for 'analytics':
  analytics\migrations\0001_initial.py
    - Create model StatistiquesDossier
    - Create model PerformanceActeur
    - Create model PredictionRisque
```

### 3. Appliquer les migrations
```bash
python manage.py migrate analytics
```

**Résultat attendu** :
```
Running migrations:
  Applying analytics.0001_initial... OK
```

### 4. (Optionnel) Tester le module
```bash
python manage.py test analytics
```

**Résultat attendu** :
```
Creating test database...
...........
----------------------------------------------------------------------
Ran 11 tests in 2.345s

OK
```

### 5. Lancer le serveur
```bash
python manage.py runserver
```

### 6. Accéder au dashboard
Ouvrir dans le navigateur :
```
http://localhost:8000/analytics/dashboard/
```

---

## 🔧 EN CAS D'ERREUR DE BASE DE DONNÉES

Si vous voyez l'erreur :
```
django.db.utils.OperationalError: [Errno 11001] getaddrinfo failed
```

**Cause** : PostgreSQL n'est pas accessible (Docker non démarré ou mauvaise configuration).

**Solutions** :

### Option A : Utiliser SQLite (pour tester rapidement)

Modifier temporairement `core/settings/base.py` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Puis relancer les migrations :
```bash
python manage.py migrate
```

### Option B : Démarrer Docker PostgreSQL

```bash
docker-compose -f docker-compose.dev.yml up -d
```

Attendre 30 secondes, puis :
```bash
python manage.py migrate
```

---

## ✅ VÉRIFICATION FINALE

### Vérifier que le module est installé
```bash
python manage.py shell
```

```python
from django.conf import settings
print('analytics' in settings.INSTALLED_APPS)
# Doit afficher: True

from analytics.models import StatistiquesDossier
print(StatistiquesDossier)
# Doit afficher: <class 'analytics.models.StatistiquesDossier'>

exit()
```

### Vérifier les URLs
```bash
python manage.py show_urls | findstr analytics
```

**Résultat attendu** :
```
/analytics/dashboard/                  analytics:dashboard_analytics
/analytics/rapport/                    analytics:rapport_statistiques
/analytics/predictions/                analytics:predictions_risque
/analytics/export/excel/               analytics:exporter_excel
/analytics/api/graphiques/             analytics:api_graphiques
/analytics/api/kpis/                   analytics:api_kpis
```

---

## 🎯 RÉSUMÉ DES COMMANDES (COPIER-COLLER)

```bash
# 1. Créer dossier ML
mkdir analytics\ml_models

# 2. Migrations
python manage.py makemigrations analytics
python manage.py migrate analytics

# 3. Tester (optionnel)
python manage.py test analytics

# 4. Lancer serveur
python manage.py runserver
```

Puis ouvrir : **http://localhost:8000/analytics/dashboard/**

---

## 📞 AIDE

Si vous rencontrez des problèmes :
1. Vérifier que `analytics` est dans `INSTALLED_APPS`
2. Vérifier que PostgreSQL/Docker est démarré
3. Consulter `docs/CORRECTIONS_ANALYTICS.md`
4. Vérifier les logs d'erreur

---

**Le module Analytics est maintenant prêt à être utilisé !** 🎉

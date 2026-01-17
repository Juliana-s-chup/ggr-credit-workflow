# 🐘 DÉMARRER POSTGRESQL AVEC DOCKER

## ✅ SQLite SUPPRIMÉ - PostgreSQL RESTAURÉ

---

## 🚀 COMMANDES POUR DÉMARRER

### OPTION 1 : Docker Compose (RECOMMANDÉ)

```bash
# 1. Démarrer PostgreSQL avec Docker
docker-compose -f docker-compose.dev.yml up -d

# 2. Attendre 30 secondes que PostgreSQL démarre

# 3. Créer les migrations analytics
python manage.py makemigrations analytics

# 4. Appliquer toutes les migrations
python manage.py migrate

# 5. Créer un superuser
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

---

### OPTION 2 : PostgreSQL Local (sans Docker)

Si vous avez PostgreSQL installé localement :

1. **Modifier `.env`** :
```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=credit_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
```

2. **Créer la base de données** :
```bash
psql -U postgres
CREATE DATABASE credit_db;
\q
```

3. **Appliquer les migrations** :
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 📋 VÉRIFICATIONS

### Vérifier que Docker fonctionne

```bash
docker ps
```

**Résultat attendu** :
```
CONTAINER ID   IMAGE         PORTS                    STATUS
abc123...      postgres:16   0.0.0.0:5432->5432/tcp   Up
```

### Vérifier la connexion PostgreSQL

```bash
docker exec -it ggr-credit-workflow-db-1 psql -U credit_user -d credit_db
```

**Si ça fonctionne**, vous verrez :
```
credit_db=#
```

Tapez `\q` pour quitter.

---

## ⚠️ RÉSOLUTION DES PROBLÈMES

### Erreur : "getaddrinfo failed"

**Cause** : Docker n'est pas démarré

**Solution** :
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Erreur : "password authentication failed"

**Cause** : Mauvais mot de passe dans `.env`

**Solution** :
```bash
# 1. Supprimer les volumes Docker
docker-compose -f docker-compose.dev.yml down -v

# 2. Vérifier le .env
DB_PASSWORD=votre_mot_de_passe

# 3. Redémarrer
docker-compose -f docker-compose.dev.yml up -d
```

### Erreur : "port 5432 already in use"

**Cause** : PostgreSQL déjà installé localement

**Solution** :
```bash
# Option A : Arrêter PostgreSQL local
net stop postgresql-x64-16

# Option B : Changer le port dans docker-compose.dev.yml
ports:
  - "5433:5432"  # Utiliser 5433 au lieu de 5432
```

---

## 📊 CONFIGURATION ACTUELLE

| Paramètre | Valeur |
|-----------|--------|
| **Base de données** | PostgreSQL 16 |
| **Host** | `db` (Docker) ou `127.0.0.1` (local) |
| **Port** | `5432` |
| **Database** | `credit_db` |
| **User** | `credit_user` |
| **Password** | Défini dans `.env` |

---

## ✅ RÉSUMÉ

1. ✅ SQLite supprimé
2. ✅ PostgreSQL restauré dans `settings.py`
3. ✅ Migration 0006 corrigée (CASCADE restauré)
4. ✅ Configuration Docker prête

---

## 🎯 PROCHAINES ÉTAPES

```bash
# 1. Démarrer Docker
docker-compose -f docker-compose.dev.yml up -d

# 2. Attendre 30 secondes

# 3. Appliquer les migrations
python manage.py migrate

# 4. Créer superuser
python manage.py createsuperuser

# 5. Lancer le serveur
python manage.py runserver
```

---

**PostgreSQL est maintenant configuré ! 🐘**

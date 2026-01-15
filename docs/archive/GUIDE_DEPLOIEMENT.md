# 🚀 GUIDE DE DÉPLOIEMENT

**GGR Credit Workflow - Déploiement en Production**

---

## 1. PRÉ-REQUIS

### 1.1 Serveur

**Configuration minimale** :
- **OS** : Ubuntu 20.04 LTS ou supérieur
- **RAM** : 2 GB minimum, 4 GB recommandé
- **CPU** : 2 cœurs minimum
- **Disque** : 20 GB minimum
- **Bande passante** : 100 Mbps

**Configuration recommandée (production)** :
- **RAM** : 8 GB
- **CPU** : 4 cœurs
- **Disque** : 50 GB SSD
- **Bande passante** : 1 Gbps

### 1.2 Logiciels requis

```bash
# Python
Python 3.10 ou supérieur

# Base de données
PostgreSQL 14 ou supérieur

# Serveur web (optionnel)
Nginx 1.18 ou supérieur

# Gestionnaire de processus
Gunicorn 20.1 ou supérieur
```

### 1.3 Accès requis

- Accès SSH au serveur
- Droits sudo
- Accès à la base de données PostgreSQL
- Nom de domaine configuré (optionnel)

---

## 2. INSTALLATION

### 2.1 Mise à jour du système

```bash
# Connexion SSH
ssh user@votre-serveur.com

# Mise à jour
sudo apt update
sudo apt upgrade -y
```

### 2.2 Installation de Python et dépendances

```bash
# Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Vérification
python3 --version  # Doit afficher 3.10 ou supérieur
```

### 2.3 Installation de PostgreSQL

```bash
# Installation
sudo apt install postgresql postgresql-contrib -y

# Démarrage
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Vérification
sudo systemctl status postgresql
```

### 2.4 Installation de Nginx (optionnel)

```bash
# Installation
sudo apt install nginx -y

# Démarrage
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2.5 Création de l'utilisateur système

```bash
# Créer un utilisateur dédié
sudo adduser ggr-credit --disabled-password --gecos ""

# Se connecter
sudo su - ggr-credit
```

### 2.6 Clonage du projet

```bash
# Depuis le répertoire home de l'utilisateur
cd /home/ggr-credit

# Cloner le projet (Git)
git clone https://github.com/votre-repo/ggr-credit-workflow.git

# Ou copier les fichiers (SCP)
# Sur votre machine locale :
# scp -r ggr-credit-workflow/ user@serveur:/home/ggr-credit/

cd ggr-credit-workflow
```

### 2.7 Création de l'environnement virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer
source venv/bin/activate

# Vérification
which python  # Doit pointer vers venv/bin/python
```

### 2.8 Installation des dépendances Python

```bash
# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Vérification
pip list
```

---

## 3. CONFIGURATION DE LA BASE DE DONNÉES

### 3.1 Création de la base de données

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Dans psql :
CREATE DATABASE credit_db;
CREATE USER credit_user WITH PASSWORD 'VotreMotDePasseSecurise123!';
ALTER ROLE credit_user SET client_encoding TO 'utf8';
ALTER ROLE credit_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE credit_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE credit_db TO credit_user;

# Quitter
\q
```

### 3.2 Test de connexion

```bash
# Tester la connexion
psql -h localhost -U credit_user -d credit_db

# Si succès, vous êtes connecté
# Quitter avec \q
```

### 3.3 Configuration PostgreSQL (optionnel)

```bash
# Éditer pg_hba.conf pour autoriser les connexions
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Ajouter (si nécessaire) :
# local   all             credit_user                             md5

# Redémarrer PostgreSQL
sudo systemctl restart postgresql
```

---

## 4. MIGRATION DES DONNÉES

### 4.1 Configuration de la connexion BDD

```bash
# Créer le fichier .env
nano .env

# Ajouter :
DEBUG=False
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire-123456789
DJANGO_SETTINGS_MODULE=core.settings.base

DB_NAME=credit_db
DB_USER=credit_user
DB_PASSWORD=VotreMotDePasseSecurise123!
DB_HOST=localhost
DB_PORT=5432

ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,IP-du-serveur

# Sauvegarder : Ctrl+O, Enter, Ctrl+X
```

### 4.2 Test de la configuration

```bash
# Activer l'environnement virtuel (si pas déjà fait)
source venv/bin/activate

# Tester la configuration
python manage.py check --settings=core.settings.base

# Résultat attendu : System check identified no issues (0 silenced).
```

### 4.3 Exécution des migrations

```bash
# Créer les tables
python manage.py migrate --settings=core.settings.base

# Vérification
python manage.py showmigrations --settings=core.settings.base
# Toutes les migrations doivent avoir un [X]
```

### 4.4 Création du superutilisateur

```bash
# Créer un compte admin
python manage.py createsuperuser --settings=core.settings.base

# Suivre les instructions :
# Username: admin
# Email: admin@ggr-credit.cg
# Password: ********
```

### 4.5 Chargement des données initiales (optionnel)

```bash
# Si vous avez des fixtures
python manage.py loaddata initial_data.json --settings=core.settings.base
```

---

## 5. GESTION DES FICHIERS STATIQUES

### 5.1 Configuration

```python
# Dans settings/base.py (déjà configuré)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise pour servir les statiques
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Juste après Security
    # ...
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
```

### 5.2 Collecte des fichiers statiques

```bash
# Collecter tous les fichiers statiques
python manage.py collectstatic --settings=core.settings.base --noinput

# Vérification
ls -la staticfiles/
# Doit contenir : admin/, css/, js/, img/
```

### 5.3 Configuration des médias

```bash
# Créer le dossier media
mkdir -p media/documents

# Permissions
chmod 755 media
chmod 755 media/documents
```

---

## 6. LANCEMENT DU SERVEUR

### 6.1 Test avec le serveur de développement

```bash
# Test rapide (NE PAS utiliser en production)
python manage.py runserver 0.0.0.0:8000 --settings=core.settings.base

# Accéder depuis un navigateur : http://IP-serveur:8000
# Ctrl+C pour arrêter
```

### 6.2 Installation de Gunicorn

```bash
# Déjà installé via requirements.txt
# Vérification
gunicorn --version
```

### 6.3 Configuration de Gunicorn

```bash
# Créer le fichier de configuration
nano gunicorn_config.py

# Contenu :
bind = "0.0.0.0:8000"
workers = 4  # (2 × CPU cores) + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "/home/ggr-credit/ggr-credit-workflow/logs/gunicorn-error.log"
accesslog = "/home/ggr-credit/ggr-credit-workflow/logs/gunicorn-access.log"
loglevel = "info"
```

### 6.4 Lancement avec Gunicorn

```bash
# Créer le dossier logs
mkdir -p logs

# Lancer Gunicorn
gunicorn core.wsgi:application -c gunicorn_config.py

# Test : http://IP-serveur:8000
```

### 6.5 Configuration systemd (démarrage automatique)

```bash
# Créer le service
sudo nano /etc/systemd/system/ggr-credit.service

# Contenu :
[Unit]
Description=GGR Credit Workflow
After=network.target

[Service]
Type=notify
User=ggr-credit
Group=ggr-credit
WorkingDirectory=/home/ggr-credit/ggr-credit-workflow
Environment="PATH=/home/ggr-credit/ggr-credit-workflow/venv/bin"
ExecStart=/home/ggr-credit/ggr-credit-workflow/venv/bin/gunicorn \
          core.wsgi:application \
          -c /home/ggr-credit/ggr-credit-workflow/gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Sauvegarder et quitter
```

```bash
# Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable ggr-credit
sudo systemctl start ggr-credit

# Vérification
sudo systemctl status ggr-credit

# Logs
sudo journalctl -u ggr-credit -f
```

### 6.6 Configuration Nginx (reverse proxy)

```bash
# Créer la configuration
sudo nano /etc/nginx/sites-available/ggr-credit

# Contenu :
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    client_max_body_size 5M;

    location /static/ {
        alias /home/ggr-credit/ggr-credit-workflow/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /home/ggr-credit/ggr-credit-workflow/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Sauvegarder
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/ggr-credit /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx

# Vérification
sudo systemctl status nginx
```

---

## 7. VARIABLES D'ENVIRONNEMENT

### 7.1 Fichier .env (déjà créé)

```bash
# Éditer si nécessaire
nano .env
```

### 7.2 Variables importantes

```bash
# Django
DEBUG=False  # IMPORTANT : False en production
SECRET_KEY=votre-cle-secrete-unique-et-aleatoire
DJANGO_SETTINGS_MODULE=core.settings.base
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,IP

# Base de données
DB_NAME=credit_db
DB_USER=credit_user
DB_PASSWORD=VotreMotDePasseSecurise123!
DB_HOST=localhost
DB_PORT=5432

# Email (optionnel)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Uploads
UPLOAD_MAX_BYTES=5242880  # 5 MB
```

### 7.3 Génération d'une SECRET_KEY sécurisée

```python
# Dans le shell Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copier la clé générée dans .env
```

---

## 8. SÉCURISATION POUR LA PRODUCTION

### 8.1 Settings de sécurité Django

```python
# Dans settings/base.py (à ajouter)

# HTTPS
SECURE_SSL_REDIRECT = True  # Rediriger HTTP vers HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Autres
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### 8.2 Configuration du pare-feu

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Vérification
sudo ufw status
```

### 8.3 Installation de Let's Encrypt (HTTPS)

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtenir un certificat
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Renouvellement automatique (déjà configuré)
sudo certbot renew --dry-run
```

### 8.4 Permissions des fichiers

```bash
# Propriétaire
sudo chown -R ggr-credit:ggr-credit /home/ggr-credit/ggr-credit-workflow

# Permissions
chmod 755 /home/ggr-credit/ggr-credit-workflow
chmod 644 /home/ggr-credit/ggr-credit-workflow/.env
chmod 755 /home/ggr-credit/ggr-credit-workflow/media
```

### 8.5 Sauvegarde automatique

```bash
# Créer le script de sauvegarde
nano /home/ggr-credit/backup.sh

# Contenu :
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ggr-credit/backups"
mkdir -p $BACKUP_DIR

# Backup BDD
pg_dump -U credit_user credit_db > $BACKUP_DIR/db_$DATE.sql

# Backup media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/ggr-credit/ggr-credit-workflow/media

# Garder seulement les 7 derniers backups
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete

# Rendre exécutable
chmod +x /home/ggr-credit/backup.sh

# Ajouter au crontab (tous les jours à 2h du matin)
crontab -e
# Ajouter :
0 2 * * * /home/ggr-credit/backup.sh
```

### 8.6 Monitoring des logs

```bash
# Logs Django
tail -f /home/ggr-credit/ggr-credit-workflow/logs/general.log

# Logs Gunicorn
tail -f /home/ggr-credit/ggr-credit-workflow/logs/gunicorn-error.log

# Logs Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## 9. VÉRIFICATION FINALE

### 9.1 Checklist de déploiement

- [ ] Base de données créée et accessible
- [ ] Migrations exécutées
- [ ] Superutilisateur créé
- [ ] Fichiers statiques collectés
- [ ] DEBUG=False dans .env
- [ ] SECRET_KEY sécurisée
- [ ] ALLOWED_HOSTS configuré
- [ ] Gunicorn démarre correctement
- [ ] Service systemd actif
- [ ] Nginx configuré et actif
- [ ] HTTPS activé (Let's Encrypt)
- [ ] Pare-feu configuré
- [ ] Sauvegardes automatiques configurées

### 9.2 Tests de fonctionnement

```bash
# 1. Test de connexion BDD
python manage.py dbshell --settings=core.settings.base

# 2. Test des migrations
python manage.py showmigrations --settings=core.settings.base

# 3. Test de l'admin
# Accéder à : https://votre-domaine.com/admin/

# 4. Test d'une page
# Accéder à : https://votre-domaine.com/

# 5. Test de création de compte
# S'inscrire via l'interface
```

---

## 10. MAINTENANCE

### 10.1 Mise à jour du code

```bash
# Se connecter au serveur
ssh ggr-credit@serveur

# Aller dans le projet
cd /home/ggr-credit/ggr-credit-workflow

# Activer venv
source venv/bin/activate

# Récupérer les modifications
git pull origin main

# Installer nouvelles dépendances
pip install -r requirements.txt

# Migrations
python manage.py migrate --settings=core.settings.base

# Collecter statiques
python manage.py collectstatic --noinput --settings=core.settings.base

# Redémarrer Gunicorn
sudo systemctl restart ggr-credit
```

### 10.2 Redémarrage des services

```bash
# Gunicorn
sudo systemctl restart ggr-credit

# Nginx
sudo systemctl restart nginx

# PostgreSQL
sudo systemctl restart postgresql
```

---

**Guide de déploiement professionnel**  
**Pour toute question : support@ggr-credit.cg**

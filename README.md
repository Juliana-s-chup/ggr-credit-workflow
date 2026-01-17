# GGR Credit Workflow (Projet de fin dâ€™Ã©tude)

## ðŸŽ¯ Description
Application Django de gestion des dossiers de crÃ©dit avec deux portails (Client et Professionnel), workflow, rÃ´les (RBAC) et journalisation.

## ðŸ§± Stack
- Django 5 + Python 3.12
- PostgreSQL 16
- Nginx (reverse proxy local) + Gunicorn (prod)

## ðŸš€ DÃ©marrage rapide (local)
1. Cloner et entrer dans le dossier
   ```bash
   git clone https://github.com/<votre-compte>/ggr-credit-workflow.git
   cd ggr-credit-workflow
   ```
2. Environnement virtuel
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   # source venv/bin/activate  # Linux/Mac
   ```
3. DÃ©pendances
   ```bash
   pip install -r requirements.txt
   ```
4. Variables dâ€™environnement
   ```bash
   copy env.example .env   # Windows
   # cp env.example .env   # Linux/Mac
   # Ouvrir .env et renseigner DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, SECRET_KEY
   ```
5. Base de donnÃ©es et migrations
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
6. Lancer
   ```bash
   python manage.py runserver
   ```
   AccÃ¨s:
   - Portail Client: http://localhost:8000/client/login/
   - Portail Pro:    http://localhost:8000/pro/login/

## ðŸ³ Docker (optionnel)
```bash
docker-compose up -d
```
Nginx est configurÃ© en HTTP local simple.

## ðŸ”’ Bonnes pratiques de sÃ©curitÃ©
- Les secrets restent dans `.env` (non versionnÃ©)
- `env.example` fournit un gabarit sans secrets

## ðŸ§ª Tests
```bash
python manage.py test
```

## ðŸ“„ Licence
Projet acadÃ©mique pour dÃ©monstration.


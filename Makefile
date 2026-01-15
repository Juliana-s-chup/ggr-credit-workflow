.PHONY: help test coverage install lint format clean

help:
	@echo "🚀 GGR Credit Workflow - Commandes disponibles"
	@echo ""
	@echo "  make install    - Installer les dépendances"
	@echo "  make test       - Lancer tous les tests"
	@echo "  make coverage   - Générer le rapport de couverture"
	@echo "  make lint       - Vérifier la qualité du code"
	@echo "  make format     - Formater le code avec Black"
	@echo "  make clean      - Nettoyer les fichiers temporaires"
	@echo "  make run        - Lancer le serveur de développement"
	@echo "  make migrate    - Appliquer les migrations"
	@echo ""

install:
	@echo "📦 Installation des dépendances..."
	pip install -r requirements.txt

test:
	@echo "🧪 Lancement des tests..."
	python manage.py test --verbosity=2

pytest:
	@echo "🧪 Lancement des tests avec pytest..."
	pytest --cov=suivi_demande --cov=analytics --cov-report=html --cov-report=term-missing

coverage:
	@echo "📊 Génération du rapport de couverture..."
	coverage run --source='suivi_demande,analytics' manage.py test
	coverage report
	coverage html
	@echo "✅ Rapport disponible dans htmlcov/index.html"

lint:
	@echo "🔍 Vérification de la qualité du code..."
	flake8 suivi_demande analytics core --max-line-length=120 --exclude=migrations

format:
	@echo "✨ Formatage du code avec Black..."
	black suivi_demande analytics core --line-length=120

clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage .pytest_cache
	@echo "✅ Nettoyage terminé"

run:
	@echo "🚀 Démarrage du serveur de développement..."
	python manage.py runserver

migrate:
	@echo "🔄 Application des migrations..."
	python manage.py makemigrations
	python manage.py migrate

superuser:
	@echo "👤 Création d'un superutilisateur..."
	python manage.py createsuperuser

shell:
	@echo "🐚 Ouverture du shell Django..."
	python manage.py shell

collectstatic:
	@echo "📁 Collecte des fichiers statiques..."
	python manage.py collectstatic --noinput

all: clean install migrate test coverage
	@echo "✅ Toutes les étapes terminées avec succès!"

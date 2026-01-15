# 📊 Module Analytics - Documentation Technique

## Vue d'ensemble

Le module `analytics` fournit des fonctionnalités d'analyse de données, de reporting et de prédiction ML pour le système de gestion de workflow de crédit bancaire.

## Fonctionnalités

### 1. Dashboards Analytiques
- KPIs en temps réel (total dossiers, taux d'approbation, etc.)
- Graphiques interactifs avec Charts.js
- Évolution mensuelle des dossiers
- Répartition par statut et type de crédit

### 2. Statistiques Agrégées
- Calcul automatique par période (jour, semaine, mois, année)
- Métriques : compteurs, montants, délais, taux
- Historique des performances

### 3. Export Excel
- Export complet des dossiers
- Statistiques agrégées
- Format compatible Excel/LibreOffice

### 4. Prédiction ML
- Modèle Random Forest pour risque crédit
- Score de risque (0-100)
- Classification : FAIBLE, MOYEN, ÉLEVÉ
- Recommandations automatiques

## Installation

### Dépendances

```bash
pip install pandas numpy scikit-learn matplotlib seaborn openpyxl joblib
```

### Configuration Django

Ajouter dans `settings.py` :

```python
INSTALLED_APPS = [
    ...
    'analytics',
]
```

Ajouter dans `urls.py` principal :

```python
urlpatterns = [
    ...
    path('analytics/', include('analytics.urls')),
]
```

### Migrations

```bash
python manage.py makemigrations analytics
python manage.py migrate analytics
```

## Utilisation

### 1. Calculer les Statistiques

```python
from analytics.services import AnalyticsService

# Calculer les stats mensuelles
stats = AnalyticsService.calculer_statistiques_periode('MOIS')
print(f"Total dossiers: {stats.total_dossiers}")
print(f"Taux approbation: {stats.taux_approbation}%")
```

### 2. Obtenir les KPIs

```python
kpis = AnalyticsService.obtenir_kpis_dashboard()
# {'total_dossiers': 150, 'taux_approbation': 75.5, ...}
```

### 3. Prédire le Risque

```python
from analytics.services import MLPredictionService
from suivi_demande.models import DossierCredit

dossier = DossierCredit.objects.get(id=42)
prediction = MLPredictionService.predire_risque(dossier)

print(f"Score risque: {prediction.score_risque}")
print(f"Classe: {prediction.classe_risque}")
print(f"Recommandation: {prediction.recommandation}")
```

### 4. Exporter en Excel

```python
from analytics.services import ExportService

filepath = ExportService.exporter_statistiques_excel()
# Retourne: 'media/exports/statistiques_credit_20251111.xlsx'
```

## API Endpoints

### Dashboards

- `GET /analytics/dashboard/` - Dashboard principal
- `GET /analytics/rapport/` - Rapport statistiques
- `GET /analytics/predictions/` - Prédictions ML

### Actions

- `POST /analytics/predire/<dossier_id>/` - Générer prédiction
- `GET /analytics/export/excel/` - Télécharger Excel

### API JSON

- `GET /analytics/api/graphiques/` - Données pour Charts.js
- `GET /analytics/api/kpis/` - KPIs en temps réel

## Modèles de Données

### StatistiquesDossier

Statistiques agrégées par période.

**Champs principaux** :
- `periode` : JOUR, SEMAINE, MOIS, ANNEE
- `total_dossiers` : Nombre total
- `taux_approbation` : Pourcentage d'approbation
- `montant_total_demande` : Montant total demandé
- `delai_moyen_traitement` : Délai moyen en jours

### PredictionRisque

Prédictions ML pour les dossiers.

**Champs principaux** :
- `dossier` : Lien vers DossierCredit
- `score_risque` : Score 0-100
- `probabilite_defaut` : Probabilité 0-1
- `classe_risque` : FAIBLE, MOYEN, ELEVE
- `recommandation` : Texte de recommandation

## Machine Learning

### Entraînement du Modèle

```python
from analytics.services import MLPredictionService

# Entraîner le modèle (nécessite au moins 10 dossiers terminés)
model = MLPredictionService.entrainer_modele()
```

### Features Utilisées

1. Montant demandé
2. Durée en mois
3. Revenu mensuel
4. Type de crédit (encodage one-hot)

### Algorithme

- **Random Forest Classifier** (scikit-learn)
- 100 arbres de décision
- Normalisation StandardScaler

### Fichiers Modèles

- `analytics/ml_models/credit_risk_model.pkl` - Modèle entraîné
- `analytics/ml_models/scaler.pkl` - Scaler pour normalisation

## Tests

```bash
# Tests unitaires
python manage.py test analytics

# Tests spécifiques
python manage.py test analytics.tests.test_services
python manage.py test analytics.tests.test_ml
```

## Permissions

- **SUPER_ADMIN** : Accès complet
- **RESPONSABLE_GGR** : Dashboards + Rapports + Export
- **ANALYSTE** : Prédictions ML
- **GESTIONNAIRE** : KPIs basiques
- **CLIENT** : Aucun accès

## Performance

### Optimisations

- Statistiques pré-calculées (évite requêtes lourdes)
- Cache Redis pour KPIs (TTL 5 minutes)
- Pagination des listes (50 éléments/page)
- Index PostgreSQL sur champs de filtrage

### Monitoring

```python
# Temps de calcul des stats
import time
start = time.time()
stats = AnalyticsService.calculer_statistiques_periode('MOIS')
print(f"Durée: {time.time() - start:.2f}s")
```

## Troubleshooting

### Erreur : "Pas assez de données pour entraîner"

**Cause** : Moins de 10 dossiers terminés (APPROUVE ou REJETE)

**Solution** : Créer plus de dossiers de test ou utiliser des fixtures

### Erreur : "Module 'sklearn' not found"

**Cause** : scikit-learn non installé

**Solution** :
```bash
pip install scikit-learn
```

### Graphiques ne s'affichent pas

**Cause** : Charts.js non chargé

**Solution** : Vérifier la connexion internet (CDN Charts.js)

## Maintenance

### Tâches Périodiques

```bash
# Calculer les stats quotidiennes (cron)
0 1 * * * cd /app && python manage.py shell -c "from analytics.services import AnalyticsService; AnalyticsService.calculer_statistiques_periode('JOUR')"

# Ré-entraîner le modèle ML (hebdomadaire)
0 2 * * 0 cd /app && python manage.py shell -c "from analytics.services import MLPredictionService; MLPredictionService.entrainer_modele()"
```

## Roadmap

- [ ] Ajout de features ML (historique client, scoring externe)
- [ ] Validation croisée du modèle
- [ ] Dashboards interactifs (filtres dynamiques)
- [ ] Alertes automatiques (seuils)
- [ ] Intégration Power BI
- [ ] Export PDF des rapports

## Auteur

**NGUIMBI Juliana**  
Bachelor Full Stack & Data Analyst  
Crédit du Congo - GGR  
Novembre 2025

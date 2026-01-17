# CHAPITRE 6.5 : MODULE D'ANALYSE DE DONNÉES ET REPORTING

## Introduction

Dans le cadre de la formation **Bachelor Full Stack & Data Analyst**, l'aspect analyse de données constitue un pilier essentiel du projet. Ce chapitre présente le module d'analytics développé pour transformer les données brutes des dossiers de crédit en informations exploitables, facilitant ainsi la prise de décision stratégique au sein de la GGR du Crédit du Congo.

Le module d'analytics répond à trois objectifs principaux :
1. **Visualisation des KPIs** : Tableaux de bord interactifs avec indicateurs clés de performance
2. **Analyse statistique** : Rapports détaillés sur les tendances et performances
3. **Prédiction ML** : Modèle de machine learning pour l'évaluation du risque crédit

---

## 6.5.1. Architecture du Module Analytics

### A. Structure Modulaire

Le module `analytics` est organisé selon une architecture en couches :

```
analytics/
├── models.py           # Modèles de données statistiques
├── services.py         # Logique métier et calculs
├── views.py            # Contrôleurs et API
├── urls.py             # Routage
├── admin.py            # Interface d'administration
└── ml_models/          # Modèles ML sauvegardés
    ├── credit_risk_model.pkl
    └── scaler.pkl
```

### B. Modèles de Données

Trois modèles principaux ont été créés pour stocker les analyses :

#### 1. **StatistiquesDossier**
Agrège les métriques globales par période (jour, semaine, mois, année) :
- Compteurs : total, en cours, approuvés, rejetés, archivés
- Montants : total demandé, total approuvé, montant moyen
- Délais : temps moyen de traitement par étape
- Taux : approbation, rejet

#### 2. **PerformanceActeur**
Évalue la performance individuelle des gestionnaires et analystes :
- Dossiers traités par période
- Taux d'approbation personnel
- Délai moyen de traitement
- Score de performance calculé

#### 3. **PredictionRisque**
Stocke les prédictions du modèle ML :
- Score de risque (0-100)
- Probabilité de défaut (0-1)
- Classification : FAIBLE, MOYEN, ÉLEVÉ
- Facteurs de risque identifiés
- Recommandation automatique

---

## 6.5.2. Dashboards Analytiques avec Charts.js

### A. Dashboard Principal

Le dashboard principal offre une vue d'ensemble avec :

**KPIs en temps réel** :
- 📁 Total dossiers
- ⏳ Dossiers en cours
- ✅ Taux d'approbation
- 📅 Nouveaux dossiers du mois

**Graphiques interactifs** (Charts.js 4.4.0) :
1. **Graphique linéaire** : Évolution mensuelle des dossiers (12 derniers mois)
2. **Graphique en donut** : Répartition par statut
3. **Graphique en barres** : Répartition par type de crédit

### B. Implémentation Technique

```javascript
// Exemple : Graphique d'évolution mensuelle
const ctxEvolution = document.getElementById('chartEvolution').getContext('2d');
new Chart(ctxEvolution, {
    type: 'line',
    data: {
        labels: ['Jan', 'Fév', 'Mar', ...],
        datasets: [{
            label: 'Nombre de dossiers',
            data: [12, 19, 15, ...],
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            tooltip: { mode: 'index' }
        }
    }
});
```

### C. Service de Calcul Statistique

La classe `AnalyticsService` centralise tous les calculs :

```python
class AnalyticsService:
    @staticmethod
    def calculer_statistiques_periode(periode='MOIS'):
        # Récupération des dossiers de la période
        dossiers = DossierCredit.objects.filter(created_at__gte=date_debut)
        
        # Calculs agrégés
        total = dossiers.count()
        approuves = dossiers.filter(statut_agent='APPROUVE').count()
        taux_approbation = (approuves / total * 100) if total > 0 else 0
        
        # Sauvegarde des statistiques
        stats = StatistiquesDossier.objects.create(...)
        return stats
```

---

## 6.5.3. Export Excel avec Statistiques (pandas)

### A. Fonctionnalité d'Export

Le module permet d'exporter les données en Excel avec deux feuilles :
1. **Feuille "Dossiers"** : Liste complète des dossiers avec détails
2. **Feuille "Statistiques"** : Métriques agrégées

### B. Implémentation avec pandas

```python
class ExportService:
    @staticmethod
    def exporter_statistiques_excel():
        # Récupération des données
        dossiers = DossierCredit.objects.all().values(
            'reference', 'client__username', 'type_credit', 
            'montant_demande', 'statut_agent', 'created_at'
        )
        
        # Création DataFrame pandas
        df = pd.DataFrame(list(dossiers))
        df.columns = ['Référence', 'Client', 'Type', 'Montant', 'Statut', 'Date']
        
        # Statistiques agrégées
        stats = {
            'Total dossiers': [len(df)],
            'Montant total': [df['Montant'].sum()],
            'Montant moyen': [df['Montant'].mean()],
            'Taux approbation': [calcul_taux_approbation(df)]
        }
        df_stats = pd.DataFrame(stats)
        
        # Export Excel multi-feuilles
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Dossiers', index=False)
            df_stats.to_excel(writer, sheet_name='Statistiques', index=False)
        
        return filepath
```

### C. Avantages de l'Export Excel

- **Analyse hors ligne** : Les décideurs peuvent analyser les données dans Excel
- **Pivot tables** : Création de tableaux croisés dynamiques
- **Graphiques personnalisés** : Visualisations supplémentaires
- **Archivage** : Conservation des rapports mensuels

---

## 6.5.4. Analyse Prédictive avec Machine Learning

### A. Objectif du Modèle ML

Le modèle de machine learning prédit le **risque de défaut de paiement** d'un dossier de crédit avant sa validation finale, permettant aux analystes de :
- Identifier les dossiers à risque élevé
- Prioriser l'analyse approfondie
- Réduire le taux de défaut

### B. Algorithme Utilisé : Random Forest

**Choix de l'algorithme** :
- **Random Forest Classifier** (scikit-learn)
- Robuste aux données déséquilibrées
- Interprétable (importance des features)
- Performant sur des datasets de taille moyenne

### C. Features (Variables Prédictives)

Le modèle utilise 6 features principales :
1. **Montant demandé** : Montant du crédit
2. **Durée** : Durée du prêt en mois
3. **Revenu mensuel** : Revenu du client
4. **Type de crédit** : Immobilier, Consommation, Professionnel (encodage one-hot)

### D. Implémentation

```python
class MLPredictionService:
    @staticmethod
    def entrainer_modele():
        # Récupération des dossiers historiques
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=['APPROUVE', 'REJETE']
        )
        
        # Préparation des features
        X = []
        y = []
        for dossier in dossiers:
            features = [
                float(dossier.montant_demande),
                float(dossier.duree_mois),
                float(dossier.revenu_mensuel),
                1 if dossier.type_credit == 'IMMOBILIER' else 0,
                1 if dossier.type_credit == 'CONSOMMATION' else 0,
                1 if dossier.type_credit == 'PROFESSIONNEL' else 0,
            ]
            X.append(features)
            y.append(1 if dossier.statut_agent == 'REJETE' else 0)
        
        X = np.array(X)
        y = np.array(y)
        
        # Normalisation
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Entraînement Random Forest
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        # Sauvegarde
        joblib.dump(model, 'analytics/ml_models/credit_risk_model.pkl')
        joblib.dump(scaler, 'analytics/ml_models/scaler.pkl')
        
        return model
    
    @staticmethod
    def predire_risque(dossier):
        # Chargement du modèle
        model = joblib.load('analytics/ml_models/credit_risk_model.pkl')
        scaler = joblib.load('analytics/ml_models/scaler.pkl')
        
        # Extraction features
        features = np.array([extraire_features(dossier)])
        features_scaled = scaler.transform(features)
        
        # Prédiction
        probabilite_defaut = model.predict_proba(features_scaled)[0][1]
        score_risque = probabilite_defaut * 100
        
        # Classification
        if score_risque < 30:
            classe_risque = 'FAIBLE'
            recommandation = "Approbation recommandée."
        elif score_risque < 60:
            classe_risque = 'MOYEN'
            recommandation = "Analyse approfondie recommandée."
        else:
            classe_risque = 'ELEVE'
            recommandation = "Prudence recommandée."
        
        # Sauvegarde de la prédiction
        prediction = PredictionRisque.objects.create(
            dossier=dossier,
            score_risque=score_risque,
            probabilite_defaut=probabilite_defaut,
            classe_risque=classe_risque,
            recommandation=recommandation,
        )
        
        return prediction
```

### E. Interprétation des Résultats

**Score de risque** :
- **0-30** : Risque FAIBLE → Approbation recommandée
- **30-60** : Risque MOYEN → Analyse approfondie
- **60-100** : Risque ÉLEVÉ → Prudence requise

**Facteurs de risque** :
Le modèle identifie les variables ayant le plus contribué au score (feature importance).

---

## 6.5.5. Interface Utilisateur Analytics

### A. Pages Développées

1. **`/analytics/dashboard/`** : Dashboard principal avec KPIs et graphiques
2. **`/analytics/rapport/`** : Rapport statistiques détaillé par période
3. **`/analytics/predictions/`** : Liste des prédictions ML
4. **`/analytics/export/excel/`** : Téléchargement Excel

### B. Permissions d'Accès

- **SUPER_ADMIN** : Accès complet
- **RESPONSABLE_GGR** : Dashboards et rapports
- **ANALYSTE** : Prédictions ML uniquement
- **GESTIONNAIRE** : KPIs basiques
- **CLIENT** : Aucun accès (données sensibles)

---

## 6.5.6. Apports du Module Data Analyst

### A. Pour la Banque

1. **Prise de décision éclairée** :
   - Visualisation temps réel des performances
   - Identification des tendances
   - Détection des anomalies

2. **Optimisation opérationnelle** :
   - Réduction du taux de défaut grâce au ML
   - Priorisation des dossiers à risque
   - Amélioration des délais de traitement

3. **Reporting automatisé** :
   - Génération automatique de rapports mensuels
   - Export Excel pour la direction
   - Traçabilité des performances

### B. Pour le Projet Académique

1. **Compétences Data Science** :
   - Manipulation de données avec pandas
   - Visualisation avec Charts.js
   - Machine Learning avec scikit-learn

2. **Conformité au diplôme** :
   - Justification du titre "Full Stack & Data Analyst"
   - Démonstration de compétences analytiques
   - Application concrète du ML

---

## 6.5.7. Limites et Perspectives

### A. Limites Actuelles

1. **Modèle ML basique** :
   - Features limitées (6 variables)
   - Pas de validation croisée
   - Pas de tuning des hyperparamètres

2. **Données d'entraînement** :
   - Dataset limité (projet académique)
   - Pas de données réelles sensibles

3. **Visualisations** :
   - Graphiques statiques (pas de drill-down)
   - Pas de filtres dynamiques avancés

### B. Améliorations Futures

1. **Modèle ML avancé** :
   - Ajout de features (historique client, scoring externe)
   - Validation croisée et GridSearchCV
   - Comparaison d'algorithmes (XGBoost, LightGBM)
   - Explainability (SHAP values)

2. **Dashboards interactifs** :
   - Filtres dynamiques par période/acteur
   - Drill-down sur les graphiques
   - Alertes automatiques (seuils dépassés)

3. **Big Data** :
   - Intégration Apache Spark pour volumes importants
   - Data warehouse (PostgreSQL → Redshift/BigQuery)
   - ETL automatisé

4. **BI avancé** :
   - Intégration Power BI / Tableau
   - Rapports automatisés par email
   - Prédictions en temps réel

---

## Conclusion du Chapitre 6.5

Le module d'analyse de données et reporting constitue une **valeur ajoutée majeure** au projet Workflow GGR. Il transforme le système de gestion de dossiers en un **outil d'aide à la décision stratégique**, combinant :
- **Visualisation intuitive** (Charts.js)
- **Analyse statistique rigoureuse** (pandas)
- **Intelligence artificielle** (scikit-learn)

Ce module démontre la **double compétence Full Stack & Data Analyst** de l'étudiante, en intégrant harmonieusement le développement web (Django) et l'analyse de données (Python Data Science stack).

Pour la banque, il représente un **levier d'optimisation** permettant de réduire les risques, d'améliorer les performances et de prendre des décisions éclairées basées sur les données.

---

**Prochaine étape** : Chapitre 7 - Tests et Validation (incluant tests du module analytics)

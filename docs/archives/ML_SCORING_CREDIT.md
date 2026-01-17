# 🤖 MODULE MACHINE LEARNING - SCORING CRÉDIT

## Vue d'ensemble

Le système intègre un modèle de Machine Learning pour prédire automatiquement la probabilité d'approbation d'un dossier de crédit basé sur l'historique des décisions.

## Algorithme Utilisé

**Random Forest Classifier** (scikit-learn)
- 100 arbres de décision
- Profondeur maximale: 10
- Équilibrage des classes (class_weight='balanced')

## Features (Variables Prédictives)

| Feature | Description | Importance |
|---------|-------------|------------|
| `montant` | Montant du crédit demandé (FCFA) | Élevée |
| `duree_mois` | Durée du crédit (mois) | Moyenne |
| `salaire_net` | Salaire net moyen (FCFA) | Élevée |
| `capacite_nette` | Capacité d'endettement nette (FCFA) | Très élevée |
| `ratio_endettement` | montant / capacité_nette | Critique |

## Entraînement du Modèle

### Commande
```bash
python manage.py train_scoring_model
```

### Données Requises
- Minimum 10 dossiers avec statuts finaux
- Statuts: APPROUVE_ATTENTE_FONDS, FONDS_LIBERE, REFUSE

### Métriques
- **Accuracy**: Précision globale du modèle
- **Precision/Recall**: Par classe (approuvé/refusé)
- **F1-Score**: Moyenne harmonique

## Utilisation

### Dans le Code
```python
from suivi_demande.ml.credit_scoring import predict_approval_probability

# Prédire pour un dossier
dossier = DossierCredit.objects.get(id=123)
proba = predict_approval_probability(dossier)

if proba:
    print(f"Probabilité d'approbation: {proba}%")
```

### Dans les Templates
```html
{% if dossier.score_ia %}
<div class="alert alert-info">
    🤖 Score IA: {{ dossier.score_ia }}% de probabilité d'approbation
</div>
{% endif %}
```

## Interprétation des Scores

| Score | Interprétation | Action Recommandée |
|-------|----------------|-------------------|
| 0-30% | Risque élevé | Refus probable |
| 31-60% | Risque moyen | Analyse approfondie |
| 61-85% | Risque faible | Approbation probable |
| 86-100% | Très faible risque | Approbation recommandée |

## Limitations

1. **Données d'entraînement**: Nécessite un historique suffisant (>50 dossiers recommandés)
2. **Biais**: Le modèle reproduit les décisions passées (biais humains inclus)
3. **Évolution**: À réentraîner régulièrement (mensuel recommandé)
4. **Aide à la décision**: Ne remplace PAS l'analyse humaine

## Amélioration Continue

### Réentraînement Automatique
```python
# Planifier avec cron (mensuel)
0 2 1 * * cd /path/to/project && python manage.py train_scoring_model
```

### Ajout de Features
Futures améliorations possibles:
- Historique bancaire du client
- Secteur d'activité de l'employeur
- Ancienneté dans l'emploi
- Nombre de crédits antérieurs

## Conformité RGPD

- ✅ Pas de données sensibles (race, religion, etc.)
- ✅ Explicabilité via importance des features
- ✅ Droit à l'intervention humaine (décision finale = humain)
- ✅ Transparence: score affiché au gestionnaire

## Performance

- **Temps de prédiction**: <50ms par dossier
- **Mémoire**: ~5MB (modèle chargé)
- **Précision attendue**: 75-85% (selon qualité données)

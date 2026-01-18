"""
Modèle de Machine Learning pour le scoring crédit.
Prédit la probabilité d'approbation d'un dossier de crédit.
"""

import os
import logging
from decimal import Decimal
from pathlib import Path

logger = logging.getLogger(__name__)

# Vérifier si scikit-learn est disponible
try:
    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("scikit-learn non installé. Fonctionnalités ML désactivées.")


class CreditScoringModel:
    """Modèle de scoring crédit basé sur Random Forest."""

    def __init__(self, model_path=None):
        """
        Initialise le modèle de scoring.

        Args:
            model_path: Chemin vers le modèle sauvegardé (optionnel)
        """
        if not ML_AVAILABLE:
            raise ImportError("scikit-learn requis pour le scoring ML")

        self.model = None
        self.model_path = model_path or self._get_default_model_path()
        self.feature_names = [
            "montant",
            "duree_mois",
            "salaire_net",
            "capacite_nette",
            "ratio_endettement",
        ]

    def _get_default_model_path(self):
        """Retourne le chemin par défaut du modèle."""
        base_dir = Path(__file__).resolve().parent.parent.parent
        models_dir = base_dir / "ml_models"
        models_dir.mkdir(exist_ok=True)
        return models_dir / "credit_scoring.pkl"

    def prepare_features(self, dossier):
        """
        Prépare les features pour la prédiction.

        Args:
            dossier: Instance de DossierCredit

        Returns:
            Liste de features [montant, duree, salaire, capacite, ratio]
        """
        try:
            canevas = dossier.canevas
            montant = float(dossier.montant)
            duree = canevas.demande_duree_mois
            salaire = float(canevas.salaire_net_moyen_fcfa)
            capacite = float(canevas.capacite_endettement_nette_fcfa)

            # Ratio d'endettement = montant demandé / capacité nette
            ratio = (montant / capacite) if capacite > 0 else 999

            return [montant, duree, salaire, capacite, ratio]
        except Exception as e:
            logger.error(f"Erreur préparation features: {e}")
            return None

    def train(self, dossiers_queryset):
        """
        Entraîne le modèle sur l'historique des dossiers.

        Args:
            dossiers_queryset: QuerySet de DossierCredit avec statuts finaux

        Returns:
            dict: Métriques d'entraînement (accuracy, report)
        """
        if not ML_AVAILABLE:
            return None

        # Préparer les données
        X = []
        y = []

        for dossier in dossiers_queryset:
            if not hasattr(dossier, "canevas"):
                continue

            features = self.prepare_features(dossier)
            if features is None:
                continue

            # Label: 1 = approuvé, 0 = refusé
            label = 1 if dossier.statut_agent in ["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE"] else 0

            X.append(features)
            y.append(label)

        if len(X) < 10:
            logger.warning(f"Pas assez de données pour entraîner (seulement {len(X)} dossiers)")
            return None

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Entraîner Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight="balanced",  # Gérer déséquilibre classes
        )

        self.model.fit(X_train, y_train)

        # Évaluer
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        # Sauvegarder
        joblib.dump(self.model, self.model_path)
        logger.info(f"Modèle entraîné et sauvegardé: accuracy={accuracy:.2%}")

        return {
            "accuracy": accuracy,
            "report": report,
            "n_train": len(X_train),
            "n_test": len(X_test),
        }

    def load(self):
        """Charge le modèle depuis le disque."""
        if not ML_AVAILABLE:
            return False

        if not os.path.exists(self.model_path):
            logger.warning(f"Modèle non trouvé: {self.model_path}")
            return False

        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Modèle chargé depuis {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur chargement modèle: {e}")
            return False

    def predict_probability(self, dossier):
        """
        Prédit la probabilité d'approbation d'un dossier.

        Args:
            dossier: Instance de DossierCredit

        Returns:
            float: Probabilité d'approbation (0-100%)
        """
        if not ML_AVAILABLE or self.model is None:
            return None

        features = self.prepare_features(dossier)
        if features is None:
            return None

        try:
            # Prédire probabilité classe 1 (approuvé)
            proba = self.model.predict_proba([features])[0][1]
            return round(proba * 100, 2)
        except Exception as e:
            logger.error(f"Erreur prédiction: {e}")
            return None

    def get_feature_importance(self):
        """Retourne l'importance des features."""
        if self.model is None:
            return None

        importances = self.model.feature_importances_
        return dict(zip(self.feature_names, importances))


# Instance globale du modèle
_scoring_model = None


def get_scoring_model():
    """Retourne l'instance globale du modèle de scoring."""
    global _scoring_model
    if _scoring_model is None and ML_AVAILABLE:
        _scoring_model = CreditScoringModel()
        _scoring_model.load()
    return _scoring_model


def predict_approval_probability(dossier):
    """
    Fonction helper pour prédire la probabilité d'approbation.

    Args:
        dossier: Instance de DossierCredit

    Returns:
        float: Probabilité d'approbation (0-100%) ou None si erreur
    """
    model = get_scoring_model()
    if model is None:
        return None
    return model.predict_probability(dossier)

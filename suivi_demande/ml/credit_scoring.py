"""
Modele de Machine Learning pour le scoring credit.
Predit la probabilite d'approbation d'un dossier de credit.
"""

import os
import logging
from decimal import Decimal
from pathlib import Path

logger = logging.getLogger(__name__)

# Verifier si scikit-learn est disponible
try:
    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("scikit-learn non installe. Fonctionnalites ML desactivees.")


class CreditScoringModel:
    """Modele de scoring credit base sur Random Forest."""

    def __init__(self, model_path=None):
        """
        Initialise le modele de scoring.

        Args:
            model_path: Chemin vers le modele sauvegarde (optionnel)
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
        """Retourne le chemin par defaut du modele."""
        base_dir = Path(__file__).resolve().parent.parent.parent
        models_dir = base_dir / "ml_models"
        models_dir.mkdir(exist_ok=True)
        return models_dir / "credit_scoring.pkl"

    def prepare_features(self, dossier):
        """
        Prepare les features pour la prediction.

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

            # Ratio d'endettement = montant demande / capacite nette
            ratio = (montant / capacite) if capacite > 0 else 999

            return [montant, duree, salaire, capacite, ratio]
        except Exception as e:
            logger.error(f"Erreur preparation features: {e}")
            return None

    def train(self, dossiers_queryset):
        """
        Entraine le modele sur l'historique des dossiers.

        Args:
            dossiers_queryset: QuerySet de DossierCredit avec statuts finaux

        Returns:
            dict: Metriques d'entrainement (accuracy, report)
        """
        if not ML_AVAILABLE:
            return None

        # Preparer les donnees
        X = []
        y = []

        for dossier in dossiers_queryset:
            if not hasattr(dossier, "canevas"):
                continue

            features = self.prepare_features(dossier)
            if features is None:
                continue

            # Label: 1 = approuve, 0 = refuse
            label = (
                1
                if dossier.statut_agent in ["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE"]
                else 0
            )

            X.append(features)
            y.append(label)

        if len(X) < 10:
            logger.warning(
                f"Pas assez de donnees pour entrainer (seulement {len(X)} dossiers)"
            )
            return None

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Entrainer Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight="balanced",  # Gerer desequilibre classes
        )

        self.model.fit(X_train, y_train)

        # e‰valuer
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        # Sauvegarder
        joblib.dump(self.model, self.model_path)
        logger.info(f"Modele entraine et sauvegarde: accuracy={accuracy:.2%}")

        return {
            "accuracy": accuracy,
            "report": report,
            "n_train": len(X_train),
            "n_test": len(X_test),
        }

    def load(self):
        """Charge le modele depuis le disque."""
        if not ML_AVAILABLE:
            return False

        if not os.path.exists(self.model_path):
            logger.warning(f"Modele non trouve: {self.model_path}")
            return False

        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Modele charge depuis {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur chargement modele: {e}")
            return False

    def predict_probability(self, dossier):
        """
        Predit la probabilite d'approbation d'un dossier.

        Args:
            dossier: Instance de DossierCredit

        Returns:
            float: Probabilite d'approbation (0-100%)
        """
        if not ML_AVAILABLE or self.model is None:
            return None

        features = self.prepare_features(dossier)
        if features is None:
            return None

        try:
            # Predire probabilite classe 1 (approuve)
            proba = self.model.predict_proba([features])[0][1]
            return round(proba * 100, 2)
        except Exception as e:
            logger.error(f"Erreur prediction: {e}")
            return None

    def get_feature_importance(self):
        """Retourne l'importance des features."""
        if self.model is None:
            return None

        importances = self.model.feature_importances_
        return dict(zip(self.feature_names, importances))


# Instance globale du modele
_scoring_model = None


def get_scoring_model():
    """Retourne l'instance globale du modele de scoring."""
    global _scoring_model
    if _scoring_model is None and ML_AVAILABLE:
        _scoring_model = CreditScoringModel()
        _scoring_model.load()
    return _scoring_model


def predict_approval_probability(dossier):
    """
    Fonction helper pour predire la probabilite d'approbation.

    Args:
        dossier: Instance de DossierCredit

    Returns:
        float: Probabilite d'approbation (0-100%) ou None si erreur
    """
    model = get_scoring_model()
    if model is None:
        return None
    return model.predict_probability(dossier)

"""
Module Analytics - Services de calcul et analyse
Auteur: NGUIMBI Juliana
Date: Novembre 2025
"""

from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

from suivi_demande.models import DossierCredit, JournalAction
from .models import StatistiquesDossier, PerformanceActeur, PredictionRisque


class AnalyticsService:
    """
    Service principal pour les calculs statistiques et analyses
    """

    @staticmethod
    def calculer_statistiques_periode(periode="MOIS"):
        """
        Calcule les statistiques pour une periode donnee
        """
        # Determiner la date de debut selon la periode
        now = timezone.now()
        if periode == "JOUR":
            date_debut = now - timedelta(days=1)
        elif periode == "SEMAINE":
            date_debut = now - timedelta(weeks=1)
        elif periode == "MOIS":
            date_debut = now - timedelta(days=30)
        else:  # ANNEE
            date_debut = now - timedelta(days=365)

        # Recuperer les dossiers de la periode
        dossiers = DossierCredit.objects.filter(created_at__gte=date_debut)

        # Compteurs
        total = dossiers.count()
        en_cours = dossiers.filter(
            statut_agent__in=[
                "NOUVEAU",
                "TRANSMIS_ANALYSTE",
                "EN_COURS_ANALYSE",
                "EN_COURS_VALIDATION_GGR",
            ]
        ).count()
        approuves = dossiers.filter(
            statut_agent__in=["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE"]
        ).count()
        rejetes = dossiers.filter(statut_agent="REJETE").count()
        archives = dossiers.filter(is_archived=True).count()

        # Montants
        montant_total = dossiers.aggregate(Sum("montant_demande"))["montant_demande__sum"] or 0
        montant_approuve = (
            dossiers.filter(statut_agent__in=["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE"]).aggregate(
                Sum("montant_demande")
            )["montant_demande__sum"]
            or 0
        )
        montant_moyen = dossiers.aggregate(Avg("montant_demande"))["montant_demande__avg"] or 0

        # Delais (calcul simplifie)
        delai_moyen = AnalyticsService._calculer_delai_moyen(dossiers)

        # Taux
        taux_approbation = (approuves / total * 100) if total > 0 else 0
        taux_rejet = (rejetes / total * 100) if total > 0 else 0

        # Creer l'enregistrement statistique
        stats = StatistiquesDossier.objects.create(
            periode=periode,
            total_dossiers=total,
            dossiers_en_cours=en_cours,
            dossiers_approuves=approuves,
            dossiers_rejetes=rejetes,
            dossiers_archives=archives,
            montant_total_demande=montant_total,
            montant_total_approuve=montant_approuve,
            montant_moyen_demande=montant_moyen,
            delai_moyen_traitement=delai_moyen,
            taux_approbation=taux_approbation,
            taux_rejet=taux_rejet,
        )

        return stats

    @staticmethod
    def _calculer_delai_moyen(dossiers):
        """
        Calcule le delai moyen de traitement en jours
        """
        delais = []
        for dossier in dossiers:
            if dossier.statut_agent in ["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE", "REJETE"]:
                # Calculer le delai entre creation et decision finale
                derniere_action = (
                    JournalAction.objects.filter(dossier=dossier).order_by("-created_at").first()
                )

                if derniere_action:
                    delai = (derniere_action.created_at - dossier.created_at).days
                    delais.append(delai)

        return sum(delais) / len(delais) if delais else 0

    @staticmethod
    def obtenir_kpis_dashboard():
        """
        Retourne les KPIs pour le dashboard principal
        """
        # Statistiques globales
        total_dossiers = DossierCredit.objects.count()
        dossiers_en_cours = DossierCredit.objects.filter(
            statut_agent__in=[
                "NOUVEAU",
                "TRANSMIS_ANALYSTE",
                "EN_COURS_ANALYSE",
                "EN_COURS_VALIDATION_GGR",
            ]
        ).count()
        dossiers_ce_mois = DossierCredit.objects.filter(
            created_at__month=timezone.now().month, created_at__year=timezone.now().year
        ).count()

        # Taux d'approbation
        dossiers_termines = DossierCredit.objects.filter(
            statut_agent__in=["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE", "REJETE"]
        )
        total_termines = dossiers_termines.count()
        approuves = dossiers_termines.filter(
            statut_agent__in=["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE"]
        ).count()
        taux_approbation = (approuves / total_termines * 100) if total_termines > 0 else 0

        # Montant total
        montant_total = (
            DossierCredit.objects.aggregate(Sum("montant_demande"))["montant_demande__sum"] or 0
        )

        return {
            "total_dossiers": total_dossiers,
            "dossiers_en_cours": dossiers_en_cours,
            "dossiers_ce_mois": dossiers_ce_mois,
            "taux_approbation": round(taux_approbation, 2),
            "montant_total": montant_total,
        }

    @staticmethod
    def obtenir_donnees_graphiques():
        """
        Retourne les donnees pour les graphiques Charts.js
        """
        # e‰volution mensuelle des dossiers (12 derniers mois)
        mois_labels = []
        mois_data = []

        for i in range(11, -1, -1):
            date = timezone.now() - timedelta(days=30 * i)
            mois_labels.append(date.strftime("%b %Y"))
            count = DossierCredit.objects.filter(
                created_at__month=date.month, created_at__year=date.year
            ).count()
            mois_data.append(count)

        # Repartition par statut
        statuts = DossierCredit.objects.values("statut_agent").annotate(count=Count("id"))
        statuts_labels = [s["statut_agent"] for s in statuts]
        statuts_data = [s["count"] for s in statuts]

        # Repartition par type de credit
        types = DossierCredit.objects.values("type_credit").annotate(count=Count("id"))
        types_labels = [t["type_credit"] for t in types]
        types_data = [t["count"] for t in types]

        return {
            "evolution_mensuelle": {
                "labels": mois_labels,
                "data": mois_data,
            },
            "repartition_statuts": {
                "labels": statuts_labels,
                "data": statuts_data,
            },
            "repartition_types": {
                "labels": types_labels,
                "data": types_data,
            },
        }


class MLPredictionService:
    """
    Service de prediction de risque credit avec Machine Learning
    """

    MODEL_PATH = "analytics/ml_models/credit_risk_model.pkl"
    SCALER_PATH = "analytics/ml_models/scaler.pkl"

    @staticmethod
    def entrainer_modele():
        """
        Entraine le modele de prediction de risque
        Note: Version simplifiee pour demonstration
        """
        # Recuperer les dossiers termines (approuves ou rejetes)
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE", "REJETE"]
        )

        if dossiers.count() < 10:
            return None  # Pas assez de donnees

        # Preparer les features
        X = []
        y = []

        for dossier in dossiers:
            features = MLPredictionService._extraire_features(dossier)
            X.append(features)
            # Label: 1 si rejete, 0 si approuve
            y.append(1 if dossier.statut_agent == "REJETE" else 0)

        X = np.array(X)
        y = np.array(y)

        # Normalisation
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Entrainement
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)

        # Sauvegarder le modele
        os.makedirs("analytics/ml_models", exist_ok=True)
        joblib.dump(model, MLPredictionService.MODEL_PATH)
        joblib.dump(scaler, MLPredictionService.SCALER_PATH)

        return model

    @staticmethod
    def _extraire_features(dossier):
        """
        Extrait les features d'un dossier pour le ML
        """
        return [
            float(dossier.montant_demande or 0),
            float(dossier.duree_mois or 0),
            float(dossier.revenu_mensuel or 0) if hasattr(dossier, "revenu_mensuel") else 0,
            1 if dossier.type_credit == "IMMOBILIER" else 0,
            1 if dossier.type_credit == "CONSOMMATION" else 0,
            1 if dossier.type_credit == "PROFESSIONNEL" else 0,
        ]

    @staticmethod
    def predire_risque(dossier):
        """
        Predit le risque pour un dossier donne
        """
        # Verifier si le modele existe
        if not os.path.exists(MLPredictionService.MODEL_PATH):
            MLPredictionService.entrainer_modele()

        if not os.path.exists(MLPredictionService.MODEL_PATH):
            return None  # Pas assez de donnees pour entrainer

        # Charger le modele
        model = joblib.load(MLPredictionService.MODEL_PATH)
        scaler = joblib.load(MLPredictionService.SCALER_PATH)

        # Extraire features
        features = np.array([MLPredictionService._extraire_features(dossier)])
        features_scaled = scaler.transform(features)

        # Prediction
        probabilite_defaut = model.predict_proba(features_scaled)[0][1]
        score_risque = probabilite_defaut * 100

        # Classification
        if score_risque < 30:
            classe_risque = "FAIBLE"
            recommandation = "Dossier e  faible risque. Approbation recommandee."
        elif score_risque < 60:
            classe_risque = "MOYEN"
            recommandation = "Dossier e  risque modere. Analyse approfondie recommandee."
        else:
            classe_risque = "ELEVE"
            recommandation = "Dossier e  risque eleve. Prudence recommandee."

        # Creer ou mettre e  jour la prediction
        prediction, created = PredictionRisque.objects.update_or_create(
            dossier=dossier,
            defaults={
                "score_risque": score_risque,
                "probabilite_defaut": probabilite_defaut,
                "classe_risque": classe_risque,
                "recommandation": recommandation,
                "confiance": 0.75,  # Simplifie
                "facteurs_risque": {
                    "montant": float(dossier.montant_demande),
                    "duree": dossier.duree_mois,
                    "type": dossier.type_credit,
                },
            },
        )

        return prediction


class ExportService:
    """
    Service d'export de donnees (Excel, PDF)
    """

    @staticmethod
    def exporter_statistiques_excel():
        """
        Exporte les statistiques en Excel avec pandas
        """
        # Recuperer les dossiers
        dossiers = DossierCredit.objects.all().values(
            "reference",
            "client__username",
            "type_credit",
            "montant_demande",
            "statut_agent",
            "created_at",
            "updated_at",
        )

        # Creer DataFrame
        df = pd.DataFrame(list(dossiers))

        # Renommer les colonnes
        df.columns = [
            "Reference",
            "Client",
            "Type",
            "Montant",
            "Statut",
            "Cree le",
            "Modifie le",
        ]

        # Statistiques agregees
        stats = {
            "Total dossiers": [len(df)],
            "Montant total": [df["Montant"].sum()],
            "Montant moyen": [df["Montant"].mean()],
            "Taux approbation": [
                len(df[df["Statut"].isin(["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE"])])
                / len(df)
                * 100
            ],
        }
        df_stats = pd.DataFrame(stats)

        # Creer le fichier Excel
        filename = f'statistiques_credit_{timezone.now().strftime("%Y%m%d")}.xlsx'
        filepath = f"media/exports/{filename}"

        os.makedirs("media/exports", exist_ok=True)

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Dossiers", index=False)
            df_stats.to_excel(writer, sheet_name="Statistiques", index=False)

        return filepath

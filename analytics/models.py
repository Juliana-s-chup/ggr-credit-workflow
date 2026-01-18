"""
Module Analytics - Modeles de donnees pour statistiques et KPIs
Auteur: NGUIMBI Juliana
Date: Novembre 2025
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from suivi_demande.models import DossierCredit


class StatistiquesDossier(models.Model):
    """
    Statistiques agregees des dossiers de credit
    Calculees periodiquement pour optimiser les dashboards
    """

    date_calcul = models.DateTimeField(auto_now_add=True)
    periode = models.CharField(
        max_length=20,
        choices=[
            ("JOUR", "Journalier"),
            ("SEMAINE", "Hebdomadaire"),
            ("MOIS", "Mensuel"),
            ("ANNEE", "Annuel"),
        ],
    )

    # Compteurs globaux
    total_dossiers = models.IntegerField(default=0)
    dossiers_en_cours = models.IntegerField(default=0)
    dossiers_approuves = models.IntegerField(default=0)
    dossiers_rejetes = models.IntegerField(default=0)
    dossiers_archives = models.IntegerField(default=0)

    # Montants
    montant_total_demande = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_total_approuve = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_moyen_demande = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Delais (en jours)
    delai_moyen_traitement = models.FloatField(default=0)
    delai_moyen_analyse = models.FloatField(default=0)
    delai_moyen_validation = models.FloatField(default=0)

    # Taux
    taux_approbation = models.FloatField(default=0)  # Pourcentage
    taux_rejet = models.FloatField(default=0)

    class Meta:
        verbose_name = "Statistique Dossier"
        verbose_name_plural = "Statistiques Dossiers"
        ordering = ["-date_calcul"]

    def __str__(self):
        return f"Stats {self.periode} - {self.date_calcul.strftime('%Y-%m-%d')}"


class PerformanceActeur(models.Model):
    """
    Performance individuelle des acteurs (gestionnaires, analystes, etc.)
    """

    acteur = models.ForeignKey(User, on_delete=models.CASCADE)
    periode_debut = models.DateField()
    periode_fin = models.DateField()

    # Compteurs
    dossiers_traites = models.IntegerField(default=0)
    dossiers_approuves = models.IntegerField(default=0)
    dossiers_rejetes = models.IntegerField(default=0)

    # Delais
    delai_moyen_traitement = models.FloatField(default=0)

    # Performance
    taux_approbation = models.FloatField(default=0)
    score_performance = models.FloatField(default=0)  # Score calcule

    date_calcul = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Performance Acteur"
        verbose_name_plural = "Performances Acteurs"
        ordering = ["-date_calcul"]

    def __str__(self):
        return f"{self.acteur.get_full_name()} - {self.periode_debut} e  {self.periode_fin}"


class PredictionRisque(models.Model):
    """
    Predictions de risque credit basees sur ML
    """

    dossier = models.OneToOneField(
        DossierCredit, on_delete=models.CASCADE, related_name="prediction"
    )

    # Scores predits
    score_risque = models.FloatField(help_text="Score de 0 (faible risque) e  100 (risque eleve)")
    probabilite_defaut = models.FloatField(help_text="Probabilite de defaut de paiement (0-1)")

    # Classification
    classe_risque = models.CharField(
        max_length=20,
        choices=[
            ("FAIBLE", "Risque Faible"),
            ("MOYEN", "Risque Moyen"),
            ("ELEVE", "Risque e‰leve"),
        ],
    )

    # Facteurs de risque
    facteurs_risque = models.JSONField(default=dict, help_text="Facteurs contribuant au risque")

    # Recommandation
    recommandation = models.TextField(blank=True)

    # Metadonnees
    modele_version = models.CharField(max_length=50, default="v1.0")
    date_prediction = models.DateTimeField(auto_now_add=True)
    confiance = models.FloatField(default=0, help_text="Niveau de confiance de la prediction (0-1)")

    class Meta:
        verbose_name = "Prediction Risque"
        verbose_name_plural = "Predictions Risques"
        ordering = ["-date_prediction"]

    def __str__(self):
        return f"Prediction {self.dossier.reference} - {self.classe_risque}"

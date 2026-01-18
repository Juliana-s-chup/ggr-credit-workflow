"""
Module Analytics - Tests Unitaires
Auteur: NGUIMBI Juliana
Date: Novembre 2025
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from suivi_demande.models import DossierCredit, UserProfile
from .models import StatistiquesDossier, PredictionRisque
from .services import AnalyticsService, MLPredictionService


class StatistiquesServiceTest(TestCase):
    """
    Tests pour le service de calcul de statistiques
    """

    def setUp(self):
        # Creer un utilisateur client
        self.user = User.objects.create_user(
            username="client_test", password="test123", email="client@test.com"
        )
        self.profile = UserProfile.objects.create(
            user=self.user, role="CLIENT", full_name="Client Test"
        )

        # Creer des dossiers de test
        for i in range(5):
            DossierCredit.objects.create(
                reference=f"TEST-2025-{i:03d}",
                client=self.user,
                type_credit="CONSOMMATION",
                montant_demande=Decimal("1000000"),
                duree_mois=12,
                statut_agent="NOUVEAU" if i < 3 else "APPROUVE_ATTENTE_FONDS",
            )

    def test_calcul_statistiques_mois(self):
        """
        Test du calcul des statistiques mensuelles
        """
        stats = AnalyticsService.calculer_statistiques_periode("MOIS")

        self.assertIsNotNone(stats)
        self.assertEqual(stats.periode, "MOIS")
        self.assertEqual(stats.total_dossiers, 5)
        self.assertEqual(stats.dossiers_en_cours, 3)
        self.assertEqual(stats.dossiers_approuves, 2)

    def test_obtenir_kpis_dashboard(self):
        """
        Test de recuperation des KPIs
        """
        kpis = AnalyticsService.obtenir_kpis_dashboard()

        self.assertIn("total_dossiers", kpis)
        self.assertIn("taux_approbation", kpis)
        self.assertGreaterEqual(kpis["total_dossiers"], 5)

    def test_obtenir_donnees_graphiques(self):
        """
        Test de recuperation des donnees pour graphiques
        """
        graphiques = AnalyticsService.obtenir_donnees_graphiques()

        self.assertIn("evolution_mensuelle", graphiques)
        self.assertIn("repartition_statuts", graphiques)
        self.assertIn("repartition_types", graphiques)

        # Verifier la structure
        self.assertIn("labels", graphiques["evolution_mensuelle"])
        self.assertIn("data", graphiques["evolution_mensuelle"])


class MLPredictionServiceTest(TestCase):
    """
    Tests pour le service de prediction ML
    """

    def setUp(self):
        # Creer un utilisateur
        self.user = User.objects.create_user(username="client_ml", password="test123")
        UserProfile.objects.create(user=self.user, role="CLIENT", full_name="Client ML")

        # Creer des dossiers pour entrainement (minimum 10)
        for i in range(15):
            DossierCredit.objects.create(
                reference=f"ML-TEST-{i:03d}",
                client=self.user,
                type_credit="CONSOMMATION",
                montant_demande=Decimal("500000") * (i + 1),
                duree_mois=12 + i,
                statut_agent="APPROUVE_ATTENTE_FONDS" if i % 2 == 0 else "REJETE",
            )

    def test_entrainement_modele(self):
        """
        Test de l'entrainement du modele ML
        """
        model = MLPredictionService.entrainer_modele()

        # Verifier que le modele est cree
        self.assertIsNotNone(model)

    def test_prediction_risque(self):
        """
        Test de prediction de risque sur un dossier
        """
        # Entrainer le modele d'abord
        MLPredictionService.entrainer_modele()

        # Creer un nouveau dossier pour prediction
        dossier = DossierCredit.objects.create(
            reference="PRED-TEST-001",
            client=self.user,
            type_credit="IMMOBILIER",
            montant_demande=Decimal("5000000"),
            duree_mois=24,
            statut_agent="NOUVEAU",
        )

        # Predire le risque
        prediction = MLPredictionService.predire_risque(dossier)

        # Verifications
        self.assertIsNotNone(prediction)
        self.assertIn(prediction.classe_risque, ["FAIBLE", "MOYEN", "ELEVE"])
        self.assertGreaterEqual(prediction.score_risque, 0)
        self.assertLessEqual(prediction.score_risque, 100)
        self.assertGreaterEqual(prediction.probabilite_defaut, 0)
        self.assertLessEqual(prediction.probabilite_defaut, 1)


class AnalyticsDashboardViewTest(TestCase):
    """
    Tests pour les vues du dashboard analytics
    """

    def setUp(self):
        # Creer un utilisateur admin
        self.user = User.objects.create_user(
            username="admin_test", password="test123", is_staff=True
        )
        self.profile = UserProfile.objects.create(
            user=self.user, role="SUPER_ADMIN", full_name="Admin Test"
        )

        self.client = Client()
        self.client.login(username="admin_test", password="test123")

    def test_dashboard_analytics_access(self):
        """
        Test d'acces au dashboard analytics
        """
        response = self.client.get("/analytics/dashboard/")

        # Verifier que la page est accessible
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analytics")

    def test_api_kpis(self):
        """
        Test de l'API KPIs JSON
        """
        response = self.client.get("/analytics/api/kpis/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Verifier la structure JSON
        data = response.json()
        self.assertIn("total_dossiers", data)
        self.assertIn("taux_approbation", data)


class StatistiquesDossierModelTest(TestCase):
    """
    Tests pour le modele StatistiquesDossier
    """

    def test_creation_statistiques(self):
        """
        Test de creation d'une entree statistique
        """
        stats = StatistiquesDossier.objects.create(
            periode="MOIS",
            total_dossiers=100,
            dossiers_approuves=75,
            taux_approbation=75.0,
            montant_total_demande=Decimal("50000000"),
        )

        self.assertEqual(stats.periode, "MOIS")
        self.assertEqual(stats.total_dossiers, 100)
        self.assertEqual(stats.taux_approbation, 75.0)

        # Verifier le __str__
        self.assertIn("MOIS", str(stats))


class PredictionRisqueModelTest(TestCase):
    """
    Tests pour le modele PredictionRisque
    """

    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test123")
        UserProfile.objects.create(user=self.user, role="CLIENT", full_name="Test")

        self.dossier = DossierCredit.objects.create(
            reference="PRED-001",
            client=self.user,
            type_credit="CONSOMMATION",
            montant_demande=Decimal("1000000"),
            duree_mois=12,
        )

    def test_creation_prediction(self):
        """
        Test de creation d'une prediction
        """
        prediction = PredictionRisque.objects.create(
            dossier=self.dossier,
            score_risque=45.5,
            probabilite_defaut=0.455,
            classe_risque="MOYEN",
            recommandation="Analyse approfondie recommandee.",
            confiance=0.85,
        )

        self.assertEqual(prediction.classe_risque, "MOYEN")
        self.assertEqual(prediction.score_risque, 45.5)
        self.assertIn("PRED-001", str(prediction))

"""
Tests pour le workflow des dossiers de credit.
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import (
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    UserProfile,
    UserRoles,
    JournalAction,
)

User = get_user_model()


class WorkflowTestCase(TestCase):
    """Tests pour les transitions de workflow."""

    def setUp(self):
        """Preparation des donnees de test."""
        # Creer les utilisateurs
        self.client_user = User.objects.create_user(username="client", password="pass123")
        UserProfile.objects.create(
            user=self.client_user,
            full_name="Client Test",
            phone="+242 06 111 11 11",
            address="Test",
            role=UserRoles.CLIENT,
        )

        self.gest_user = User.objects.create_user(username="gestionnaire", password="pass123")
        UserProfile.objects.create(
            user=self.gest_user,
            full_name="Gestionnaire Test",
            phone="+242 06 222 22 22",
            address="Test",
            role=UserRoles.GESTIONNAIRE,
        )

        self.analyste_user = User.objects.create_user(username="analyste", password="pass123")
        UserProfile.objects.create(
            user=self.analyste_user,
            full_name="Analyste Test",
            phone="+242 06 333 33 33",
            address="Test",
            role=UserRoles.ANALYSTE,
        )

        # Creer un dossier
        self.dossier = DossierCredit.objects.create(
            client=self.client_user,
            reference="DOS-WF-001",
            produit="Credit",
            montant=Decimal("1000000.00"),
            statut_agent=DossierStatutAgent.NOUVEAU,
        )

        self.client = Client()

    def test_dossier_initial_status(self):
        """Test que le statut initial est correct."""
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.NOUVEAU)
        self.assertEqual(self.dossier.statut_client, DossierStatutClient.EN_ATTENTE)

    def test_journal_creation_on_dossier_create(self):
        """Test qu'une entree de journal est creee e  la creation du dossier."""
        # Creer un nouveau dossier avec journal
        dossier = DossierCredit.objects.create(
            client=self.client_user,
            reference="DOS-WF-002",
            produit="Credit",
            montant=Decimal("500000.00"),
        )

        # Creer l'entree de journal manuellement (normalement fait dans la vue)
        JournalAction.objects.create(
            dossier=dossier,
            action="CREATION",
            de_statut=None,
            vers_statut=DossierStatutAgent.NOUVEAU,
            acteur=self.client_user,
            commentaire_systeme="Dossier cree",
        )

        # Verifier qu'une entree existe
        self.assertEqual(dossier.journal.count(), 1)
        journal = dossier.journal.first()
        self.assertEqual(journal.action, "CREATION")
        self.assertEqual(journal.vers_statut, DossierStatutAgent.NOUVEAU)

    def test_transition_nouveau_vers_transmis_analyste(self):
        """Test transition de NOUVEAU vers TRANSMIS_ANALYSTE."""
        ancien_statut = self.dossier.statut_agent

        # Simuler la transition
        self.dossier.statut_agent = DossierStatutAgent.TRANSMIS_ANALYSTE
        self.dossier.acteur_courant = self.analyste_user
        self.dossier.save()

        # Creer l'entree de journal
        JournalAction.objects.create(
            dossier=self.dossier,
            action="TRANSITION",
            de_statut=ancien_statut,
            vers_statut=DossierStatutAgent.TRANSMIS_ANALYSTE,
            acteur=self.gest_user,
            commentaire_systeme="Transmis e  l'analyste",
        )

        # Verifier
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.TRANSMIS_ANALYSTE)
        self.assertEqual(self.dossier.acteur_courant, self.analyste_user)
        self.assertEqual(self.dossier.journal.count(), 1)

    def test_multiple_transitions(self):
        """Test d'un workflow complet avec plusieurs transitions."""
        # 1. NOUVEAU -> TRANSMIS_ANALYSTE
        self.dossier.statut_agent = DossierStatutAgent.TRANSMIS_ANALYSTE
        self.dossier.save()
        JournalAction.objects.create(
            dossier=self.dossier,
            action="TRANSITION",
            de_statut=DossierStatutAgent.NOUVEAU,
            vers_statut=DossierStatutAgent.TRANSMIS_ANALYSTE,
            acteur=self.gest_user,
        )

        # 2. TRANSMIS_ANALYSTE -> EN_COURS_ANALYSE
        self.dossier.statut_agent = DossierStatutAgent.EN_COURS_ANALYSE
        self.dossier.save()
        JournalAction.objects.create(
            dossier=self.dossier,
            action="TRANSITION",
            de_statut=DossierStatutAgent.TRANSMIS_ANALYSTE,
            vers_statut=DossierStatutAgent.EN_COURS_ANALYSE,
            acteur=self.analyste_user,
        )

        # 3. EN_COURS_ANALYSE -> EN_COURS_VALIDATION_GGR
        self.dossier.statut_agent = DossierStatutAgent.EN_COURS_VALIDATION_GGR
        self.dossier.save()
        JournalAction.objects.create(
            dossier=self.dossier,
            action="TRANSITION",
            de_statut=DossierStatutAgent.EN_COURS_ANALYSE,
            vers_statut=DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            acteur=self.analyste_user,
        )

        # Verifier l'historique
        self.assertEqual(self.dossier.journal.count(), 3)
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.EN_COURS_VALIDATION_GGR)

        # Verifier l'ordre chronologique
        actions = list(self.dossier.journal.order_by("timestamp"))
        self.assertEqual(actions[0].vers_statut, DossierStatutAgent.TRANSMIS_ANALYSTE)
        self.assertEqual(actions[1].vers_statut, DossierStatutAgent.EN_COURS_ANALYSE)
        self.assertEqual(actions[2].vers_statut, DossierStatutAgent.EN_COURS_VALIDATION_GGR)

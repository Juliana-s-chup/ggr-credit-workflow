"""
Tests unitaires pour les modeles de l'application suivi_demande.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import (
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    UserProfile,
    UserRoles,
    CanevasProposition,
    JournalAction,
    Notification,
    PieceJointe,
)

User = get_user_model()


class UserProfileTestCase(TestCase):
    """Tests pour le modele UserProfile."""

    def setUp(self):
        """Preparation des donnees de test."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_profile(self):
        """Test creation d'un profil utilisateur."""
        profile = UserProfile.objects.create(
            user=self.user,
            full_name="Test User",
            phone="+242 06 123 45 67",
            address="123 Test Street",
            role=UserRoles.CLIENT,
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, UserRoles.CLIENT)
        self.assertEqual(str(profile), f"Profil de {self.user.username}")

    def test_profile_roles(self):
        """Test des differents roles."""
        roles = [
            UserRoles.CLIENT,
            UserRoles.GESTIONNAIRE,
            UserRoles.ANALYSTE,
            UserRoles.RESPONSABLE_GGR,
            UserRoles.BOE,
        ]

        for role in roles:
            profile = UserProfile.objects.create(
                user=User.objects.create_user(username=f"user_{role}", password="pass"),
                full_name=f"User {role}",
                phone="+242 06 000 00 00",
                address="Test",
                role=role,
            )
            self.assertEqual(profile.role, role)


class DossierCreditTestCase(TestCase):
    """Tests pour le modele DossierCredit."""

    def setUp(self):
        """Preparation des donnees de test."""
        self.client_user = User.objects.create_user(
            username="client", email="client@example.com", password="pass123"
        )
        UserProfile.objects.create(
            user=self.client_user,
            full_name="Client Test",
            phone="+242 06 111 11 11",
            address="Test Address",
            role=UserRoles.CLIENT,
        )

    def test_create_dossier(self):
        """Test creation d'un dossier de credit."""
        dossier = DossierCredit.objects.create(
            client=self.client_user,
            reference="DOS-TEST-001",
            produit="Credit Personnel",
            montant=Decimal("1000000.00"),
        )

        self.assertEqual(dossier.client, self.client_user)
        self.assertEqual(dossier.reference, "DOS-TEST-001")
        self.assertEqual(dossier.statut_agent, DossierStatutAgent.NOUVEAU)
        self.assertEqual(dossier.statut_client, DossierStatutClient.EN_ATTENTE)
        self.assertFalse(dossier.is_archived)
        self.assertFalse(dossier.wizard_completed)

    def test_dossier_str(self):
        """Test de la representation string."""
        dossier = DossierCredit.objects.create(
            client=self.client_user,
            reference="DOS-TEST-002",
            produit="Credit",
            montant=Decimal("500000.00"),
        )

        self.assertEqual(str(dossier), f"DOS-TEST-002 - {self.client_user}")

    def test_dossier_montant_positif(self):
        """Test que le montant doit etre positif."""
        dossier = DossierCredit(
            client=self.client_user,
            reference="DOS-TEST-003",
            produit="Credit",
            montant=Decimal("-1000.00"),  # Montant negatif
        )

        # Le validator devrait empecher cela
        with self.assertRaises(ValidationError):
            dossier.full_clean()


class CanevasPropositionTestCase(TestCase):
    """Tests pour le modele CanevasProposition."""

    def setUp(self):
        """Preparation des donnees de test."""
        self.user = User.objects.create_user(username="testclient", password="pass123")
        self.dossier = DossierCredit.objects.create(
            client=self.user,
            reference="DOS-CAN-001",
            produit="Credit",
            montant=Decimal("2000000.00"),
        )

    def test_create_canevas(self):
        """Test creation d'un canevas."""
        canevas = CanevasProposition.objects.create(
            dossier=self.dossier,
            nom_prenom="Test User",
            date_naissance=timezone.now().date(),
            adresse_exacte="123 Test St",
            numero_telephone="+242 06 000 00 00",
            emploi_occupe="Developpeur",
            nom_employeur="Test Corp",
            lieu_emploi="Brazzaville",
            salaire_net_moyen_fcfa=Decimal("500000.00"),
            demande_montant_fcfa=Decimal("2000000.00"),
            demande_duree_mois=24,
            demande_taux_pourcent=Decimal("12.00"),
        )

        self.assertEqual(canevas.dossier, self.dossier)
        self.assertEqual(canevas.nom_prenom, "Test User")

    def test_calcul_capacite_endettement(self):
        """Test du calcul de capacite d'endettement."""
        canevas = CanevasProposition.objects.create(
            dossier=self.dossier,
            nom_prenom="Test User",
            date_naissance=timezone.now().date(),
            adresse_exacte="Test",
            numero_telephone="+242 06 000 00 00",
            emploi_occupe="Test",
            nom_employeur="Test",
            lieu_emploi="Test",
            salaire_net_moyen_fcfa=Decimal("1000000.00"),
            total_echeances_credits_cours=Decimal("100000.00"),
            demande_montant_fcfa=Decimal("1000000.00"),
            demande_duree_mois=12,
            demande_taux_pourcent=Decimal("10.00"),
        )

        canevas.calculer_capacite_endettement()

        # 40% de 1000000 = 400000
        self.assertEqual(canevas.capacite_endettement_brute_fcfa, Decimal("400000.00"))
        # 400000 - 100000 = 300000
        self.assertEqual(canevas.capacite_endettement_nette_fcfa, Decimal("300000.00"))
        # 1000000 - 100000 = 900000
        self.assertEqual(
            canevas.salaire_net_avant_endettement_fcfa, Decimal("900000.00")
        )


class JournalActionTestCase(TestCase):
    """Tests pour le modele JournalAction."""

    def setUp(self):
        """Preparation des donnees de test."""
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.dossier = DossierCredit.objects.create(
            client=self.user,
            reference="DOS-JOUR-001",
            produit="Credit",
            montant=Decimal("1000000.00"),
        )

    def test_create_journal_entry(self):
        """Test creation d'une entree de journal."""
        journal = JournalAction.objects.create(
            dossier=self.dossier,
            action="CREATION",
            de_statut=None,
            vers_statut=DossierStatutAgent.NOUVEAU,
            acteur=self.user,
            commentaire_systeme="Dossier cree",
        )

        self.assertEqual(journal.dossier, self.dossier)
        self.assertEqual(journal.action, "CREATION")
        self.assertEqual(journal.acteur, self.user)
        self.assertIsNotNone(journal.timestamp)


class NotificationTestCase(TestCase):
    """Tests pour le modele Notification."""

    def setUp(self):
        """Preparation des donnees de test."""
        self.user = User.objects.create_user(username="testuser", password="pass")

    def test_create_notification(self):
        """Test creation d'une notification."""
        notif = Notification.objects.create(
            utilisateur_cible=self.user,
            type="TEST",
            titre="Test Notification",
            message="Ceci est un test",
            canal="INTERNE",
        )

        self.assertEqual(notif.utilisateur_cible, self.user)
        self.assertFalse(notif.lu)
        self.assertEqual(notif.canal, "INTERNE")

    def test_notification_str(self):
        """Test de la representation string."""
        notif = Notification.objects.create(
            utilisateur_cible=self.user,
            type="INFO",
            titre="Info",
            message="Message",
            canal="INTERNE",
        )

        self.assertEqual(str(notif), f"Notif INFO -> {self.user}")

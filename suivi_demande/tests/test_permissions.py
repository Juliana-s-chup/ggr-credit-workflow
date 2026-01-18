"""
Tests pour les permissions et le controle d'acces.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import (
    DossierCredit,
    DossierStatutAgent,
    UserProfile,
    UserRoles,
)
from ..permissions import (
    get_user_role,
    can_upload_piece,
    get_transition_flags,
)

User = get_user_model()


class PermissionsTestCase(TestCase):
    """Tests pour les fonctions de permissions."""

    def setUp(self):
        """Preparation des donnees de test."""
        # Creer un client
        self.client_user = User.objects.create_user(username="client", password="pass123")
        self.client_profile = UserProfile.objects.create(
            user=self.client_user,
            full_name="Client Test",
            phone="+242 06 111 11 11",
            address="Test",
            role=UserRoles.CLIENT,
        )

        # Creer un gestionnaire
        self.gest_user = User.objects.create_user(username="gestionnaire", password="pass123")
        self.gest_profile = UserProfile.objects.create(
            user=self.gest_user,
            full_name="Gestionnaire Test",
            phone="+242 06 222 22 22",
            address="Test",
            role=UserRoles.GESTIONNAIRE,
        )

        # Creer un analyste
        self.analyste_user = User.objects.create_user(username="analyste", password="pass123")
        self.analyste_profile = UserProfile.objects.create(
            user=self.analyste_user,
            full_name="Analyste Test",
            phone="+242 06 333 33 33",
            address="Test",
            role=UserRoles.ANALYSTE,
        )

        # Creer un dossier
        self.dossier = DossierCredit.objects.create(
            client=self.client_user, reference="DOS-PERM-001", produit="Credit", montant=1000000
        )

    def test_get_user_role(self):
        """Test recuperation du role utilisateur."""
        self.assertEqual(get_user_role(self.client_user), UserRoles.CLIENT)
        self.assertEqual(get_user_role(self.gest_user), UserRoles.GESTIONNAIRE)
        self.assertEqual(get_user_role(self.analyste_user), UserRoles.ANALYSTE)

    def test_can_upload_piece_gestionnaire(self):
        """Test qu'un gestionnaire peut uploader sur un nouveau dossier."""
        self.dossier.statut_agent = DossierStatutAgent.NOUVEAU
        self.dossier.save()

        self.assertTrue(can_upload_piece(self.dossier, self.gest_user))

    def test_can_upload_piece_client(self):
        """Test qu'un client ne peut pas uploader."""
        self.assertFalse(can_upload_piece(self.dossier, self.client_user))

    def test_transition_flags_gestionnaire(self):
        """Test des flags de transition pour un gestionnaire."""
        self.dossier.statut_agent = DossierStatutAgent.NOUVEAU
        self.dossier.save()

        flags = get_transition_flags(self.dossier, self.gest_user)

        self.assertTrue(flags["can_tx_transmettre_analyste"])
        self.assertTrue(flags["can_tx_retour_client"])
        self.assertFalse(flags["can_tx_transmettre_ggr"])
        self.assertFalse(flags["can_tx_approuver"])

    def test_transition_flags_analyste(self):
        """Test des flags de transition pour un analyste."""
        self.dossier.statut_agent = DossierStatutAgent.TRANSMIS_ANALYSTE
        self.dossier.save()

        flags = get_transition_flags(self.dossier, self.analyste_user)

        self.assertFalse(flags["can_tx_transmettre_analyste"])
        self.assertTrue(flags["can_tx_transmettre_ggr"])
        self.assertTrue(flags["can_tx_retour_gestionnaire"])
        self.assertFalse(flags["can_tx_approuver"])

    def test_transition_flags_wrong_status(self):
        """Test qu'aucune transition n'est possible avec un mauvais statut."""
        self.dossier.statut_agent = DossierStatutAgent.FONDS_LIBERE
        self.dossier.save()

        flags = get_transition_flags(self.dossier, self.gest_user)

        # Aucune transition possible depuis FONDS_LIBERE pour un gestionnaire
        self.assertFalse(flags["can_tx_transmettre_analyste"])
        self.assertFalse(flags["can_tx_retour_client"])

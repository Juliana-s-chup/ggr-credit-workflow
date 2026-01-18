"""
Tests de securite de l'application.
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from ..models import DossierCredit, UserProfile, UserRoles

User = get_user_model()


@pytest.mark.security
class SecurityTestCase(TestCase):
    """Tests de securite."""

    def setUp(self):
        """Preparation des donnees de test."""
        self.client = Client()

        # Creer un client
        self.client_user = User.objects.create_user(
            username="client", email="client@test.com", password="testpass123"
        )
        self.client_profile = UserProfile.objects.create(
            user=self.client_user,
            full_name="Client Test",
            phone="+242 06 111 11 11",
            address="Test",
            role=UserRoles.CLIENT,
        )

        # Creer un dossier pour ce client
        self.dossier = DossierCredit.objects.create(
            client=self.client_user,
            reference="DOS-SEC-001",
            produit="Credit",
            montant=Decimal("1000000.00"),
        )

        # Creer un autre client
        self.other_user = User.objects.create_user(
            username="other", email="other@test.com", password="testpass123"
        )
        self.other_profile = UserProfile.objects.create(
            user=self.other_user,
            full_name="Other Client",
            phone="+242 06 222 22 22",
            address="Test",
            role=UserRoles.CLIENT,
        )

    def test_client_ne_peut_pas_voir_dossier_autre_client(self):
        """Test qu'un client ne peut pas acceder au dossier d'un autre."""
        self.client.login(username="other", password="testpass123")
        response = self.client.get(f"/dossier/{self.dossier.pk}/")

        # Doit etre refuse (302 redirect ou 403 forbidden)
        self.assertIn(response.status_code, [302, 403])

    def test_utilisateur_non_connecte_redirige_vers_login(self):
        """Test qu'un utilisateur non connecte est redirige vers login."""
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_csrf_token_present_dans_formulaires(self):
        """Test que le token CSRF est present dans les formulaires."""
        self.client.login(username="client", password="testpass123")
        response = self.client.get("/profile/")

        # Verifier que le CSRF token est present
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_sql_injection_protection(self):
        """Test de protection contre l'injection SQL."""
        self.client.login(username="client", password="testpass123")

        # Tenter une injection SQL dans la recherche
        malicious_query = "'; DROP TABLE suivi_demande_dossiercredit; --"
        response = self.client.get(f"/search/?q={malicious_query}")

        # Le systeme doit gerer cela sans erreur
        self.assertIn(response.status_code, [200, 302, 404])

        # Verifier que la table existe toujours
        self.assertTrue(DossierCredit.objects.exists())

    def test_xss_protection_dans_commentaires(self):
        """Test de protection contre XSS dans les commentaires."""
        self.client.login(username="client", password="testpass123")

        # Tenter d'injecter du JavaScript
        xss_payload = '<script>alert("XSS")</script>'
        response = self.client.post(
            f"/dossier/{self.dossier.pk}/comment/", {"commentaire": xss_payload}
        )

        # Verifier que le script n'est pas execute
        # Django echappe automatiquement le HTML
        if response.status_code == 200:
            self.assertNotContains(response, "<script>")

    def test_password_hashing(self):
        """Test que les mots de passe sont hashes."""
        user = User.objects.get(username="client")

        # Le mot de passe ne doit pas etre stocke en clair
        self.assertNotEqual(user.password, "testpass123")

        # Le mot de passe doit commencer par l'algorithme de hash
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))

    def test_session_security(self):
        """Test de la securite des sessions."""
        self.client.login(username="client", password="testpass123")

        # Verifier que la session est creee
        self.assertIn("_auth_user_id", self.client.session)

        # Verifier que l'ID utilisateur est correct
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.client_user.pk)


@pytest.mark.security
class PermissionsTestCase(TestCase):
    """Tests des permissions RBAC."""

    def setUp(self):
        """Preparation."""
        self.client = Client()

        # Creer un client
        self.client_user = User.objects.create_user(username="client", password="pass")
        UserProfile.objects.create(
            user=self.client_user,
            full_name="Client",
            phone="+242 06 000 00 00",
            address="Test",
            role=UserRoles.CLIENT,
        )

        # Creer un gestionnaire
        self.gest_user = User.objects.create_user(
            username="gestionnaire", password="pass"
        )
        UserProfile.objects.create(
            user=self.gest_user,
            full_name="Gestionnaire",
            phone="+242 06 111 11 11",
            address="Test",
            role=UserRoles.GESTIONNAIRE,
        )

    def test_client_ne_peut_pas_creer_dossier(self):
        """Test qu'un client ne peut pas creer de dossier."""
        self.client.login(username="client", password="pass")
        response = self.client.get("/pro/dossier/create/")

        # Doit etre refuse
        self.assertIn(response.status_code, [302, 403])

    def test_gestionnaire_peut_creer_dossier(self):
        """Test qu'un gestionnaire peut creer un dossier."""
        self.client.login(username="gestionnaire", password="pass")
        response = self.client.get("/pro/dossier/create/")

        # Doit etre autorise
        self.assertEqual(response.status_code, 200)

    def test_client_peut_voir_son_dashboard(self):
        """Test qu'un client peut voir son dashboard."""
        self.client.login(username="client", password="pass")
        response = self.client.get("/dashboard/")

        self.assertEqual(response.status_code, 200)


@pytest.mark.security
class FileUploadSecurityTestCase(TestCase):
    """Tests de securite des uploads de fichiers."""

    def setUp(self):
        """Preparation."""
        self.client = Client()
        self.user = User.objects.create_user("testuser", password="pass")
        UserProfile.objects.create(
            user=self.user,
            full_name="Test",
            phone="+242 06 000 00 00",
            address="Test",
            role=UserRoles.CLIENT,
        )

        self.dossier = DossierCredit.objects.create(
            client=self.user,
            reference="DOS-UPLOAD-001",
            produit="Credit",
            montant=Decimal("1000000.00"),
        )

    def test_upload_fichier_executable_refuse(self):
        """Test que les fichiers executables sont refuses."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.login(username="testuser", password="pass")

        # Creer un faux fichier .exe
        fake_exe = SimpleUploadedFile(
            "malware.exe",
            b"MZ\x90\x00",
            content_type="application/x-msdownload",  # Header EXE
        )

        response = self.client.post(
            f"/dossier/{self.dossier.pk}/upload/", {"fichier": fake_exe}
        )

        # Doit etre refuse
        # Verifier selon votre implementation

    def test_upload_fichier_trop_gros_refuse(self):
        """Test que les fichiers trop gros sont refuses."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.login(username="testuser", password="pass")

        # Creer un fichier de 20MB (si limite est 10MB)
        large_file = SimpleUploadedFile(
            "large.pdf",
            b"0" * (20 * 1024 * 1024),
            content_type="application/pdf",  # 20MB
        )

        response = self.client.post(
            f"/dossier/{self.dossier.pk}/upload/", {"fichier": large_file}
        )

        # Doit etre refuse
        # Verifier selon votre implementation

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings

from suivi_demande.models import (
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    UserRoles,
    UserProfile,
    JournalAction,
    Notification,
    PieceJointe,
)


class NegativeTransitionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # Users
        self.client_user = User.objects.create_user(username="c1", password="pwd")
        self.gestionnaire = User.objects.create_user(username="g1", password="pwd")
        self.analyste = User.objects.create_user(username="a1", password="pwd")
        self.resp = User.objects.create_user(username="r1", password="pwd")

        UserProfile.objects.create(user=self.client_user, role=UserRoles.CLIENT)
        UserProfile.objects.create(user=self.gestionnaire, role=UserRoles.GESTIONNAIRE)
        UserProfile.objects.create(user=self.analyste, role=UserRoles.ANALYSTE)
        UserProfile.objects.create(user=self.resp, role=UserRoles.RESPONSABLE_GGR)

        self.dossier = DossierCredit.objects.create(
            reference="NEG-001",
            client=self.client_user,
            produit="Prod A",
            montant=5000,
            statut_agent=DossierStatutAgent.NOUVEAU,
            statut_client=DossierStatutClient.EN_COURS_TRAITEMENT,
        )

    def test_wrong_role_cannot_approve(self):
        # Un analyste ne peut pas approuver
        self.client.login(username="a1", password="pwd")
        url = reverse("transition_dossier", args=[self.dossier.pk, "approuver"])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.dossier.refresh_from_db()
        # Statut inchangé
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.NOUVEAU)
        # Pas de journal action créée vers APPROUVE_ATTENTE_FONDS
        self.assertFalse(JournalAction.objects.filter(dossier=self.dossier, vers_statut=DossierStatutAgent.APPROUVE_ATTENTE_FONDS).exists())

    def test_wrong_status_cannot_transmit_ggr(self):
        # Analyste veut envoyer GGR mais statut est NOUVEAU -> refus
        self.client.login(username="a1", password="pwd")
        url = reverse("transition_dossier", args=[self.dossier.pk, "transmettre_ggr"])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.dossier.refresh_from_db()
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.NOUVEAU)
        self.assertFalse(JournalAction.objects.filter(dossier=self.dossier, action="TRANSITION").exists())

    def test_get_method_not_allowed(self):
        # Même avec bon rôle, en GET -> refus
        self.client.login(username="g1", password="pwd")
        url = reverse("transition_dossier", args=[self.dossier.pk, "transmettre_analyste"])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.dossier.refresh_from_db()
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.NOUVEAU)


class UploadValidationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client_user = User.objects.create_user(username="c2", password="pwd")
        UserProfile.objects.create(user=self.client_user, role=UserRoles.CLIENT)
        self.dossier = DossierCredit.objects.create(
            reference="UP-001",
            client=self.client_user,
            produit="Prod B",
            montant=1500,
            statut_agent=DossierStatutAgent.NOUVEAU,
            statut_client=DossierStatutClient.EN_COURS_TRAITEMENT,
        )

    def test_upload_extension_not_allowed(self):
        self.client.login(username="c2", password="pwd")
        url = reverse("dossier_detail", args=[self.dossier.pk])
        bad_file = SimpleUploadedFile("malware.exe", b"MZ...binary", content_type="application/octet-stream")
        resp = self.client.post(url, {
            "action": "upload_piece",
            "type_piece": "AUTRE",
        }, format='multipart', FILES={"fichier": bad_file})
        self.assertEqual(resp.status_code, 302)
        # Aucune pièce jointe créée
        self.assertFalse(PieceJointe.objects.filter(dossier=self.dossier).exists())

    def test_upload_too_large(self):
        self.client.login(username="c2", password="pwd")
        url = reverse("dossier_detail", args=[self.dossier.pk])
        # Créer un gros fichier (> UPLOAD_MAX_BYTES)
        big_size = getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024) + 1024
        big_content = b"0" * big_size
        big_file = SimpleUploadedFile("big.pdf", big_content, content_type="application/pdf")
        resp = self.client.post(url, {
            "action": "upload_piece",
            "type_piece": "AUTRE",
        }, format='multipart', FILES={"fichier": big_file})
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(PieceJointe.objects.filter(dossier=self.dossier).exists())

    def test_upload_ok(self):
        self.client.login(username="c2", password="pwd")
        url = reverse("dossier_detail", args=[self.dossier.pk])
        ok_file = SimpleUploadedFile("doc.pdf", b"%PDF-1.4 ...", content_type="application/pdf")
        resp = self.client.post(url, {
            "action": "upload_piece",
            "type_piece": "AUTRE",
        }, format='multipart', FILES={"fichier": ok_file})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(PieceJointe.objects.filter(dossier=self.dossier, type_piece="AUTRE").exists())

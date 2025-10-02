from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from suivi_demande.models import (
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    UserRoles,
    UserProfile,
    JournalAction,
    Notification,
)


class WorkflowTransitionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # Users
        self.user_client = User.objects.create_user(username="client", password="pwd", email="client@example.com")
        self.user_gest = User.objects.create_user(username="gest", password="pwd", email="gest@example.com")
        self.user_an = User.objects.create_user(username="an", password="pwd", email="an@example.com")
        self.user_resp = User.objects.create_user(username="resp", password="pwd", email="resp@example.com")
        self.user_boe = User.objects.create_user(username="boe", password="pwd", email="boe@example.com")

        UserProfile.objects.create(user=self.user_client, role=UserRoles.CLIENT)
        UserProfile.objects.create(user=self.user_gest, role=UserRoles.GESTIONNAIRE)
        UserProfile.objects.create(user=self.user_an, role=UserRoles.ANALYSTE)
        UserProfile.objects.create(user=self.user_resp, role=UserRoles.RESPONSABLE_GGR)
        UserProfile.objects.create(user=self.user_boe, role=UserRoles.BOE)

        # Dossier initial
        self.dossier = DossierCredit.objects.create(
            reference="REF-001",
            client=self.user_client,
            produit="Produit X",
            montant=1000,
            statut_agent=DossierStatutAgent.NOUVEAU,
            statut_client=DossierStatutClient.BROUILLON if hasattr(DossierStatutClient, 'BROUILLON') else DossierStatutClient.EN_COURS_TRAITEMENT,
        )

    def test_gestionnaire_transmet_analyste(self):
        self.client.login(username="gest", password="pwd")
        url = reverse("transition_dossier", args=[self.dossier.pk, "transmettre_analyste"])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.dossier.refresh_from_db()
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.TRANSMIS_ANALYSTE)
        # JournalAction créé
        self.assertTrue(JournalAction.objects.filter(dossier=self.dossier, vers_statut=DossierStatutAgent.TRANSMIS_ANALYSTE).exists())
        # Notifications: client + analyste(s)
        self.assertTrue(Notification.objects.filter(utilisateur_cible=self.user_client, type="DOSSIER_MAJ").exists())
        self.assertTrue(Notification.objects.filter(type="DOSSIER_A_TRAITER").exists())

    def test_analyste_transmet_ggr(self):
        # Prérequis
        self.dossier.statut_agent = DossierStatutAgent.TRANSMIS_ANALYSTE
        self.dossier.save()
        self.client.login(username="an", password="pwd")
        url = reverse("transition_dossier", args=[self.dossier.pk, "transmettre_ggr"])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.dossier.refresh_from_db()
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.EN_COURS_VALIDATION_GGR)

    def test_responsable_approuve(self):
        self.dossier.statut_agent = DossierStatutAgent.EN_COURS_VALIDATION_GGR
        self.dossier.save()
        self.client.login(username="resp", password="pwd")
        url = reverse("transition_dossier", args=[self.dossier.pk, "approuver"])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.dossier.refresh_from_db()
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.APPROUVE_ATTENTE_FONDS)

    def test_boe_liberer_fonds(self):
        self.dossier.statut_agent = DossierStatutAgent.APPROUVE_ATTENTE_FONDS
        self.dossier.save()
        self.client.login(username="boe", password="pwd")
        url = reverse("transition_dossier", args=[self.dossier.pk, "liberer_fonds"])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.dossier.refresh_from_db()
        self.assertEqual(self.dossier.statut_agent, DossierStatutAgent.FONDS_LIBERE)


class NotificationViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u1", password="pwd", email="u1@example.com")
        UserProfile.objects.create(user=self.user, role=UserRoles.CLIENT)
        self.notif = Notification.objects.create(
            utilisateur_cible=self.user,
            type="TEST",
            titre="Titre",
            message="Message",
            canal="INTERNE",
            lu=False,
        )

    def test_mark_one_notification_read(self):
        self.client.login(username="u1", password="pwd")
        url = reverse("notifications_mark_one", args=[self.notif.pk])
        resp = self.client.post(url, data={"next": reverse("notifications_list")})
        self.assertEqual(resp.status_code, 302)
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.lu)

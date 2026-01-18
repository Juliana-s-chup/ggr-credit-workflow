"""
Tests d'integration du workflow complet.
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import (
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    UserProfile,
    UserRoles,
    JournalAction,
    Notification,
    CanevasProposition,
)

User = get_user_model()


class WorkflowCompletTestCase(TestCase):
    """Tests du workflow complet d'un dossier."""

    def setUp(self):
        """Preparation des utilisateurs."""
        # Client
        self.client_user = User.objects.create_user("client", password="pass")
        UserProfile.objects.create(
            user=self.client_user,
            full_name="Client Test",
            phone="+242 06 111 11 11",
            address="Test",
            role=UserRoles.CLIENT,
        )

        # Gestionnaire
        self.gest_user = User.objects.create_user("gest", password="pass")
        UserProfile.objects.create(
            user=self.gest_user,
            full_name="Gestionnaire",
            phone="+242 06 222 22 22",
            address="Test",
            role=UserRoles.GESTIONNAIRE,
        )

        # Analyste
        self.analyste_user = User.objects.create_user("analyste", password="pass")
        UserProfile.objects.create(
            user=self.analyste_user,
            full_name="Analyste",
            phone="+242 06 333 33 33",
            address="Test",
            role=UserRoles.ANALYSTE,
        )

        # Responsable GGR
        self.resp_ggr_user = User.objects.create_user("resp_ggr", password="pass")
        UserProfile.objects.create(
            user=self.resp_ggr_user,
            full_name="Responsable GGR",
            phone="+242 06 444 44 44",
            address="Test",
            role=UserRoles.RESPONSABLE_GGR,
        )

        # BOE
        self.boe_user = User.objects.create_user("boe", password="pass")
        UserProfile.objects.create(
            user=self.boe_user,
            full_name="BOE",
            phone="+242 06 555 55 55",
            address="Test",
            role=UserRoles.BOE,
        )

        self.client = Client()

    def test_workflow_complet_nouveau_to_fonds_libere(self):
        """Test du workflow complet : NOUVEAU â†’ FONDS_LIBERE."""
        # 1. Creer un dossier
        dossier = DossierCredit.objects.create(
            client=self.client_user,
            reference="DOS-INT-001",
            produit="Credit Personnel",
            montant=Decimal("2000000.00"),
        )
        self.assertEqual(dossier.statut_agent, DossierStatutAgent.NOUVEAU)
        self.assertEqual(dossier.statut_client, DossierStatutClient.EN_ATTENTE)

        # 2. Gestionnaire transmet e  l'analyste
        dossier.statut_agent = DossierStatutAgent.TRANSMIS_ANALYSTE
        dossier.statut_client = DossierStatutClient.EN_COURS_TRAITEMENT
        dossier.acteur_courant = self.analyste_user
        dossier.save()

        JournalAction.objects.create(
            dossier=dossier,
            action="TRANSITION",
            de_statut=DossierStatutAgent.NOUVEAU,
            vers_statut=DossierStatutAgent.TRANSMIS_ANALYSTE,
            acteur=self.gest_user,
        )

        self.assertEqual(dossier.statut_agent, DossierStatutAgent.TRANSMIS_ANALYSTE)
        self.assertEqual(dossier.journal.count(), 1)

        # 3. Analyste transmet au GGR
        dossier.statut_agent = DossierStatutAgent.EN_COURS_VALIDATION_GGR
        dossier.acteur_courant = self.resp_ggr_user
        dossier.save()

        JournalAction.objects.create(
            dossier=dossier,
            action="TRANSITION",
            de_statut=DossierStatutAgent.TRANSMIS_ANALYSTE,
            vers_statut=DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            acteur=self.analyste_user,
        )

        self.assertEqual(dossier.statut_agent, DossierStatutAgent.EN_COURS_VALIDATION_GGR)
        self.assertEqual(dossier.journal.count(), 2)

        # 4. GGR approuve
        dossier.statut_agent = DossierStatutAgent.APPROUVE_ATTENTE_FONDS
        dossier.acteur_courant = self.boe_user
        dossier.save()

        JournalAction.objects.create(
            dossier=dossier,
            action="APPROBATION",
            de_statut=DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            vers_statut=DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
            acteur=self.resp_ggr_user,
        )

        self.assertEqual(dossier.statut_agent, DossierStatutAgent.APPROUVE_ATTENTE_FONDS)
        self.assertEqual(dossier.journal.count(), 3)

        # 5. BOE libere les fonds
        dossier.statut_agent = DossierStatutAgent.FONDS_LIBERE
        dossier.statut_client = DossierStatutClient.TERMINE
        dossier.save()

        JournalAction.objects.create(
            dossier=dossier,
            action="LIBERATION_FONDS",
            de_statut=DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
            vers_statut=DossierStatutAgent.FONDS_LIBERE,
            acteur=self.boe_user,
        )

        # Verifications finales
        self.assertEqual(dossier.statut_agent, DossierStatutAgent.FONDS_LIBERE)
        self.assertEqual(dossier.statut_client, DossierStatutClient.TERMINE)
        self.assertEqual(dossier.journal.count(), 4)

    def test_workflow_avec_retour_client(self):
        """Test du workflow avec retour au client."""
        # 1. Creer un dossier
        dossier = DossierCredit.objects.create(
            client=self.client_user,
            reference="DOS-INT-002",
            produit="Credit",
            montant=Decimal("1000000.00"),
        )

        # 2. Gestionnaire retourne au client
        dossier.statut_agent = DossierStatutAgent.NOUVEAU
        dossier.statut_client = DossierStatutClient.SE_RAPPROCHER_GEST
        dossier.save()

        JournalAction.objects.create(
            dossier=dossier,
            action="RETOUR_CLIENT",
            de_statut=DossierStatutAgent.NOUVEAU,
            vers_statut=DossierStatutAgent.NOUVEAU,
            acteur=self.gest_user,
            commentaire_systeme="Documents incomplets",
        )

        # Verifications
        self.assertEqual(dossier.statut_client, DossierStatutClient.SE_RAPPROCHER_GEST)
        self.assertEqual(dossier.journal.count(), 1)

        # 3. Client complete et gestionnaire transmet
        dossier.statut_agent = DossierStatutAgent.TRANSMIS_ANALYSTE
        dossier.statut_client = DossierStatutClient.EN_COURS_TRAITEMENT
        dossier.save()

        self.assertEqual(dossier.statut_agent, DossierStatutAgent.TRANSMIS_ANALYSTE)

    def test_workflow_avec_refus(self):
        """Test du workflow avec refus."""
        # 1. Creer un dossier
        dossier = DossierCredit.objects.create(
            client=self.client_user,
            reference="DOS-INT-003",
            produit="Credit",
            montant=Decimal("5000000.00"),
        )

        # 2. Passer par les etapes jusqu'au GGR
        dossier.statut_agent = DossierStatutAgent.EN_COURS_VALIDATION_GGR
        dossier.save()

        # 3. GGR refuse
        dossier.statut_agent = DossierStatutAgent.REFUSE
        dossier.statut_client = DossierStatutClient.SE_RAPPROCHER_GEST
        dossier.save()

        JournalAction.objects.create(
            dossier=dossier,
            action="REFUS",
            de_statut=DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            vers_statut=DossierStatutAgent.REFUSE,
            acteur=self.resp_ggr_user,
            commentaire_systeme="Capacite d'endettement insuffisante",
        )

        # Verifications
        self.assertEqual(dossier.statut_agent, DossierStatutAgent.REFUSE)
        self.assertEqual(dossier.statut_client, DossierStatutClient.SE_RAPPROCHER_GEST)


class NotificationIntegrationTestCase(TestCase):
    """Tests d'integration des notifications."""

    def setUp(self):
        """Preparation."""
        self.user = User.objects.create_user("testuser", password="pass")
        UserProfile.objects.create(
            user=self.user,
            full_name="Test",
            phone="+242 06 000 00 00",
            address="Test",
            role=UserRoles.CLIENT,
        )

    def test_notification_creee_lors_transition(self):
        """Test qu'une notification est creee lors d'une transition."""
        # Creer un dossier
        dossier = DossierCredit.objects.create(
            client=self.user,
            reference="DOS-NOTIF-001",
            produit="Credit",
            montant=Decimal("1000000.00"),
        )

        # Creer une notification
        notif = Notification.objects.create(
            utilisateur_cible=self.user,
            type="NOUVEAU_MESSAGE",
            titre=f"Dossier {dossier.reference} mis e  jour",
            message="Votre dossier a ete transmis e  l'analyste",
            canal="INTERNE",
        )

        # Verifier que la notification existe
        self.assertEqual(Notification.objects.filter(utilisateur_cible=self.user).count(), 1)
        self.assertFalse(notif.lu)

    def test_notification_marquee_lue_lors_acces_dossier(self):
        """Test que les notifications sont marquees lues."""
        # Creer un dossier
        dossier = DossierCredit.objects.create(
            client=self.user,
            reference="DOS-NOTIF-002",
            produit="Credit",
            montant=Decimal("1000000.00"),
        )

        # Creer une notification
        notif = Notification.objects.create(
            utilisateur_cible=self.user,
            type="NOUVEAU_MESSAGE",
            titre=f"Dossier {dossier.reference}",
            message="Message",
            canal="INTERNE",
            lu=False,
        )

        # Marquer comme lue
        notif.lu = True
        notif.save()

        # Verifier
        notif.refresh_from_db()
        self.assertTrue(notif.lu)


class CanevasIntegrationTestCase(TestCase):
    """Tests d'integration du canevas."""

    def setUp(self):
        """Preparation."""
        self.user = User.objects.create_user("testuser", password="pass")
        self.dossier = DossierCredit.objects.create(
            client=self.user,
            reference="DOS-CAN-001",
            produit="Credit",
            montant=Decimal("2000000.00"),
        )

    def test_creation_canevas_avec_calculs(self):
        """Test de creation d'un canevas avec calculs automatiques."""
        # Creer un canevas
        canevas = CanevasProposition.objects.create(
            dossier=self.dossier,
            nom_prenom="Test User",
            date_naissance="1990-01-01",
            adresse_exacte="Test",
            numero_telephone="+242 06 000 00 00",
            emploi_occupe="Test",
            nom_employeur="Test",
            lieu_emploi="Test",
            salaire_net_moyen_fcfa=Decimal("1000000.00"),
            total_echeances_credits_cours=Decimal("100000.00"),
            demande_montant_fcfa=Decimal("2000000.00"),
            demande_duree_mois=24,
            demande_taux_pourcent=Decimal("12.00"),
        )

        # Calculer la capacite d'endettement
        canevas.calculer_capacite_endettement()

        # Verifications
        # 40% de 1000000 = 400000
        self.assertEqual(canevas.capacite_endettement_brute_fcfa, Decimal("400000.00"))
        # 400000 - 100000 = 300000
        self.assertEqual(canevas.capacite_endettement_nette_fcfa, Decimal("300000.00"))


class DashboardIntegrationTestCase(TestCase):
    """Tests d'integration des dashboards."""

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

    def test_dashboard_affiche_statistiques_correctes(self):
        """Test que le dashboard affiche les bonnes statistiques."""
        # Creer 5 dossiers
        for i in range(5):
            DossierCredit.objects.create(
                client=self.user,
                reference=f"DOS-STAT-{i:03d}",
                produit="Credit",
                montant=Decimal("1000000.00"),
            )

        # Se connecter et acceder au dashboard
        self.client.login(username="testuser", password="pass")
        response = self.client.get("/dashboard/")

        # Verifier que les 5 dossiers sont affiches
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["dossiers_en_cours"].count(), 5)


class PermissionsIntegrationTestCase(TestCase):
    """Tests d'integration des permissions."""

    def setUp(self):
        """Preparation."""
        self.client = Client()

        # Client 1
        self.client1 = User.objects.create_user("client1", password="pass")
        UserProfile.objects.create(
            user=self.client1,
            full_name="Client 1",
            phone="+242 06 111 11 11",
            address="Test",
            role=UserRoles.CLIENT,
        )

        # Client 2
        self.client2 = User.objects.create_user("client2", password="pass")
        UserProfile.objects.create(
            user=self.client2,
            full_name="Client 2",
            phone="+242 06 222 22 22",
            address="Test",
            role=UserRoles.CLIENT,
        )

    def test_isolation_donnees_entre_clients(self):
        """Test que les clients ne voient pas les donnees des autres."""
        # Client 1 cree un dossier
        dossier1 = DossierCredit.objects.create(
            client=self.client1,
            reference="DOS-ISOL-001",
            produit="Credit",
            montant=Decimal("1000000.00"),
        )

        # Client 2 cree un dossier
        dossier2 = DossierCredit.objects.create(
            client=self.client2,
            reference="DOS-ISOL-002",
            produit="Credit",
            montant=Decimal("2000000.00"),
        )

        # Client 1 se connecte
        self.client.login(username="client1", password="pass")
        response = self.client.get("/dashboard/")

        # Verifier qu'il ne voit que son dossier
        dossiers = response.context["dossiers_en_cours"]
        self.assertEqual(dossiers.count(), 1)
        self.assertEqual(dossiers.first().reference, "DOS-ISOL-001")

        # Client 1 ne peut pas acceder au dossier de Client 2
        response = self.client.get(f"/dossier/{dossier2.pk}/")
        self.assertEqual(response.status_code, 302)  # Redirect

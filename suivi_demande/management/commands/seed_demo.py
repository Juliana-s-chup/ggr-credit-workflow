from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from suivi_demande.models import (
    UserProfile,
    UserRoles,
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
)


class Command(BaseCommand):
    help = "Seed de donnees de demonstration: utilisateurs par role et dossiers e  differents statuts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprimer les donnees demo avant de recreer",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        if options.get("reset"):
            self.stdout.write("Suppression des dossiers demo'¦")
            DossierCredit.objects.all().delete()
            self.stdout.write("Suppression des profils demo'¦")
            UserProfile.objects.all().delete()
            self.stdout.write("Suppression des users demo'¦")
            User.objects.filter(
                username__in=[
                    "client1",
                    "client2",
                    "gest1",
                    "an1",
                    "resp1",
                    "boe1",
                    "admin",
                ]
            ).delete()

        # Superuser
        admin, _ = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@example.com"}
        )
        if not admin.is_superuser:
            admin.set_password("admin")
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
        self.stdout.write("Admin: admin / admin")

        # Users + profiles
        users_spec = [
            ("client1", UserRoles.CLIENT, "client1@example.com"),
            ("client2", UserRoles.CLIENT, "client2@example.com"),
            ("gest1", UserRoles.GESTIONNAIRE, "gest1@example.com"),
            ("an1", UserRoles.ANALYSTE, "an1@example.com"),
            ("resp1", UserRoles.RESPONSABLE_GGR, "resp1@example.com"),
            ("boe1", UserRoles.BOE, "boe1@example.com"),
        ]

        created_users = {}
        for username, role, email in users_spec:
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": email}
            )
            if created:
                user.set_password("demo1234")
                user.is_active = True
                user.save()
            UserProfile.objects.get_or_create(user=user, defaults={"role": role})
            created_users[username] = user

        self.stdout.write("Utilisateurs demo: mot de passe = demo1234")

        # Dossiers par statut
        client1 = created_users["client1"]
        client2 = created_users["client2"]

        data = [
            (
                "REF-NEW-1",
                client1,
                DossierStatutAgent.NOUVEAU,
                (
                    DossierStatutClient.BROUILLON
                    if hasattr(DossierStatutClient, "BROUILLON")
                    else DossierStatutClient.EN_COURS_TRAITEMENT
                ),
                5000,
            ),
            (
                "REF-AN-1",
                client1,
                DossierStatutAgent.TRANSMIS_ANALYSTE,
                DossierStatutClient.EN_COURS_TRAITEMENT,
                7000,
            ),
            (
                "REF-AN-2",
                client2,
                DossierStatutAgent.EN_COURS_ANALYSE,
                DossierStatutClient.EN_COURS_TRAITEMENT,
                9000,
            ),
            (
                "REF-GGR-1",
                client2,
                DossierStatutAgent.EN_COURS_VALIDATION_GGR,
                DossierStatutClient.EN_COURS_TRAITEMENT,
                15000,
            ),
            (
                "REF-DG-1",
                client1,
                DossierStatutAgent.EN_ATTENTE_DECISION_DG,
                DossierStatutClient.EN_COURS_TRAITEMENT,
                20000,
            ),
            (
                "REF-APP-1",
                client1,
                DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
                DossierStatutClient.EN_COURS_TRAITEMENT,
                12000,
            ),
            (
                "REF-DONE-1",
                client2,
                DossierStatutAgent.FONDS_LIBERE,
                DossierStatutClient.TERMINE,
                3000,
            ),
            (
                "REF-REF-1",
                client2,
                DossierStatutAgent.REFUSE,
                DossierStatutClient.SE_RAPPROCHER_GEST,
                2500,
            ),
        ]

        for ref, client, s_agent, s_client, montant in data:
            DossierCredit.objects.get_or_create(
                reference=ref,
                defaults={
                    "client": client,
                    "produit": "Credit conso",
                    "montant": montant,
                    "statut_agent": s_agent,
                    "statut_client": s_client,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed de demo termine."))

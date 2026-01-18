from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from suivi_demande.models import UserProfile, UserRoles

User = get_user_model()


class Command(BaseCommand):
    help = "Vérifie et corrige les profils utilisateur manquants"

    def add_arguments(self, parser):
        parser.add_argument(
            "--create-missing",
            action="store_true",
            help="Créer les profils manquants avec le rôle CLIENT par défaut",
        )
        parser.add_argument(
            "--set-role",
            type=str,
            help="Définir le rôle pour un utilisateur spécifique (format: username:role)",
        )

    def handle(self, *args, **options):
        self.stdout.write("=== Vérification des profils utilisateur ===")

        # Lister tous les utilisateurs
        users = User.objects.all()
        users_without_profile = []

        for user in users:
            try:
                profile = user.profile
                self.stdout.write(f"✓ {user.username} -> Rôle: {profile.role}")
            except UserProfile.DoesNotExist:
                users_without_profile.append(user)
                self.stdout.write(f"✗ {user.username} -> AUCUN PROFIL")

        if users_without_profile:
            self.stdout.write(
                f"\n{len(users_without_profile)} utilisateur(s) sans profil trouvé(s)"
            )

            if options["create_missing"]:
                for user in users_without_profile:
                    profile = UserProfile.objects.create(
                        user=user,
                        full_name=user.get_full_name() or user.username,
                        phone="",
                        address="",
                        role=UserRoles.CLIENT,
                    )
                    self.stdout.write(f"✓ Profil créé pour {user.username} avec le rôle CLIENT")
            else:
                self.stdout.write("Utilisez --create-missing pour créer les profils manquants")

        # Définir un rôle spécifique
        if options["set_role"]:
            try:
                username, role = options["set_role"].split(":")
                user = User.objects.get(username=username)
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "full_name": user.get_full_name() or user.username,
                        "phone": "",
                        "address": "",
                        "role": role,
                    },
                )
                if not created:
                    profile.role = role
                    profile.save()

                self.stdout.write(f"✓ Rôle {role} défini pour {username}")
            except ValueError:
                self.stdout.write("Format incorrect. Utilisez: username:role")
            except User.DoesNotExist:
                self.stdout.write(f"Utilisateur {username} introuvable")
            except Exception as e:
                self.stdout.write(f"Erreur: {e}")

        self.stdout.write("\n=== Rôles disponibles ===")
        for role_code, role_name in UserRoles.choices:
            self.stdout.write(f"- {role_code}: {role_name}")

        self.stdout.write("\n=== Exemples d'utilisation ===")
        self.stdout.write("python manage.py fix_user_profiles --create-missing")
        self.stdout.write("python manage.py fix_user_profiles --set-role admin:SUPER_ADMIN")
        self.stdout.write(
            "python manage.py fix_user_profiles --set-role gestionnaire1:GESTIONNAIRE"
        )

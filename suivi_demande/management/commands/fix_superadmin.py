from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from suivi_demande.models import UserProfile, UserRoles

User = get_user_model()


class Command(BaseCommand):
    help = "Fix super admin access by ensuring superuser accounts have SUPER_ADMIN role"

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            nargs="?",
            type=str,
            help="Username to fix (optional, will fix all superusers if not provided)",
        )

    def handle(self, *args, **options):
        username = options.get("username")

        if username:
            try:
                user = User.objects.get(username=username)
                users = [user]
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
                return
        else:
            users = User.objects.filter(is_superuser=True)

        if not users:
            self.stdout.write(self.style.WARNING("No superuser accounts found"))
            return

        for user in users:
            self.stdout.write(f"\nProcessing user: {user.username}")
            self.stdout.write(f"  - is_superuser: {user.is_superuser}")
            self.stdout.write(f"  - is_active: {user.is_active}")

            # Ensure user is active
            if not user.is_active:
                user.is_active = True
                user.save()
                self.stdout.write(self.style.SUCCESS("  Ã¢Å“â€œ Activated user"))

            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "full_name": user.get_full_name() or user.username,
                    "phone": "",
                    "address": "",
                    "role": UserRoles.SUPER_ADMIN,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Ã¢Å“â€œ Created profile with role SUPER_ADMIN"
                    )
                )
            else:
                self.stdout.write(f"  - Current role: {profile.role}")
                if profile.role != UserRoles.SUPER_ADMIN:
                    profile.role = UserRoles.SUPER_ADMIN
                    profile.save(update_fields=["role"])
                    self.stdout.write(
                        self.style.SUCCESS(f"  Ã¢Å“â€œ Updated role to SUPER_ADMIN")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"  Ã¢Å“â€œ Role already SUPER_ADMIN")
                    )

        self.stdout.write(
            self.style.SUCCESS(f"\nÃ¢Å“â€œ Fixed {len(users)} superuser account(s)")
        )
        self.stdout.write("\nYou can now log in with these credentials.")

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from suivi_demande.models import UserProfile, UserRoles

User = get_user_model()


class Command(BaseCommand):
    help = "Create or reset a super admin account"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", type=str, default="admin", help="Username (default: admin)"
        )
        parser.add_argument(
            "--password", type=str, default="admin123", help="Password (default: admin123)"
        )
        parser.add_argument("--email", type=str, default="admin@creditducongo.com", help="Email")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email = options["email"]

        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(f"Creating/Updating Super Admin Account")
        self.stdout.write(f'{"="*60}\n')

        # Create or get user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Created new user: {username}"))
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠ User "{username}" already exists, updating...')
            )
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            if email:
                user.email = email

        # Set password
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"✓ Password set"))

        # Create or update profile
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "full_name": "Super Administrateur",
                "phone": "+242 00 000 00 00",
                "address": "Brazzaville, Congo",
                "role": UserRoles.SUPER_ADMIN,
            },
        )

        if not profile_created and profile.role != UserRoles.SUPER_ADMIN:
            profile.role = UserRoles.SUPER_ADMIN
            profile.full_name = "Super Administrateur"
            profile.save()
            self.stdout.write(self.style.SUCCESS(f"✓ Profile updated to SUPER_ADMIN"))
        elif profile_created:
            self.stdout.write(self.style.SUCCESS(f"✓ Profile created with SUPER_ADMIN role"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ Profile already configured"))

        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(self.style.SUCCESS("✓ SUPER ADMIN ACCOUNT READY"))
        self.stdout.write(f'{"="*60}\n')
        self.stdout.write(f"Username: {self.style.SUCCESS(username)}")
        self.stdout.write(f"Password: {self.style.SUCCESS(password)}")
        self.stdout.write(f"Email:    {email}")
        self.stdout.write(f'Role:     {self.style.SUCCESS("SUPER_ADMIN")}')
        self.stdout.write(f"\nYou can now log in at: http://localhost:8000/accounts/login/")
        self.stdout.write(f'{"="*60}\n')

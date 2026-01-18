"""
Commande de Backup de la Base de DonnÃ©es
Usage: python manage.py backup_db
"""

import os
import gzip
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command


class Command(BaseCommand):
    help = "CrÃ©e un backup de la base de donnÃ©es"

    def add_arguments(self, parser):
        parser.add_argument(
            "--compress",
            action="store_true",
            help="Compresser le backup avec gzip",
        )
        parser.add_argument(
            "--upload-s3",
            action="store_true",
            help="Uploader sur S3",
        )

    def handle(self, *args, **options):
        # CrÃ©er le dossier backups
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # Nom du fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.json"
        filepath = os.path.join(backup_dir, filename)

        self.stdout.write(self.style.SUCCESS(f"ðŸ”„ CrÃ©ation du backup..."))

        # CrÃ©er le backup avec dumpdata
        with open(filepath, "w") as f:
            call_command(
                "dumpdata",
                "--natural-foreign",
                "--natural-primary",
                "--indent=2",
                "--exclude=contenttypes",
                "--exclude=auth.permission",
                stdout=f,
            )

        self.stdout.write(self.style.SUCCESS(f"âœ… Backup crÃ©Ã©: {filepath}"))

        # Compresser si demandÃ©
        if options["compress"]:
            compressed_path = f"{filepath}.gz"
            with open(filepath, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Supprimer le fichier non compressÃ©
            os.remove(filepath)
            filepath = compressed_path

            self.stdout.write(self.style.SUCCESS(f"âœ… Backup compressÃ©: {compressed_path}"))

        # Upload S3 si demandÃ©
        if options["upload_s3"]:
            self.upload_to_s3(filepath)

        # Nettoyer les vieux backups (garder 30 jours)
        self.cleanup_old_backups(backup_dir, days=30)

        self.stdout.write(self.style.SUCCESS(f"âœ… Backup terminÃ© avec succÃ¨s"))

    def upload_to_s3(self, filepath):
        """Upload le backup sur S3"""
        try:
            import boto3
            from botocore.exceptions import ClientError

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

            bucket_name = settings.AWS_BACKUP_BUCKET
            s3_key = f"backups/{os.path.basename(filepath)}"

            s3_client.upload_file(filepath, bucket_name, s3_key)

            self.stdout.write(self.style.SUCCESS(f"âœ… Backup uploadÃ© sur S3: {s3_key}"))

        except (ImportError, ClientError, AttributeError) as e:
            self.stdout.write(self.style.ERROR(f"âŒ Erreur upload S3: {e}"))

    def cleanup_old_backups(self, backup_dir, days=30):
        """Supprime les backups de plus de X jours"""
        import time

        now = time.time()
        cutoff = now - (days * 86400)  # X jours en secondes

        for filename in os.listdir(backup_dir):
            filepath = os.path.join(backup_dir, filename)

            if os.path.isfile(filepath):
                file_time = os.path.getmtime(filepath)

                if file_time < cutoff:
                    os.remove(filepath)
                    self.stdout.write(self.style.WARNING(f"ðŸ—‘ï¸  Backup supprimÃ©: {filename}"))

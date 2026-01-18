"""
Commande de Restauration de la Base de Données
Usage: python manage.py restore_db <backup_file>
"""

import os
import gzip
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = "Restaure la base de données depuis un backup"

    def add_arguments(self, parser):
        parser.add_argument(
            "backup_file",
            type=str,
            help="Chemin vers le fichier de backup",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Vider la base avant restauration",
        )

    def handle(self, *args, **options):
        backup_file = options["backup_file"]

        # Vérifier que le fichier existe
        if not os.path.exists(backup_file):
            raise CommandError(f"❌ Fichier non trouvé: {backup_file}")

        self.stdout.write(
            self.style.WARNING("⚠️  ATTENTION: Cette opération va modifier la base de données")
        )

        # Confirmation
        confirm = input("Voulez-vous continuer? (oui/non): ")
        if confirm.lower() not in ["oui", "yes", "y"]:
            self.stdout.write(self.style.ERROR("❌ Restauration annulée"))
            return

        # Flush si demandé
        if options["flush"]:
            self.stdout.write(self.style.WARNING("🗑️  Vidage de la base de données..."))
            call_command("flush", "--no-input")

        # Décompresser si nécessaire
        if backup_file.endswith(".gz"):
            self.stdout.write(self.style.SUCCESS("📦 Décompression du backup..."))
            temp_file = backup_file.replace(".gz", "")

            with gzip.open(backup_file, "rb") as f_in:
                with open(temp_file, "wb") as f_out:
                    f_out.write(f_in.read())

            backup_file = temp_file

        # Restaurer
        self.stdout.write(self.style.SUCCESS("🔄 Restauration en cours..."))

        with open(backup_file, "r") as f:
            call_command("loaddata", backup_file)

        self.stdout.write(self.style.SUCCESS("✅ Restauration terminée avec succès"))

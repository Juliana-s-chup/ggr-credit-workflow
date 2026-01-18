"""
Commande de Restauration de la Base de DonnÃ©es
Usage: python manage.py restore_db <backup_file>
"""

import os
import gzip
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = "Restaure la base de donnÃ©es depuis un backup"

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

        # VÃ©rifier que le fichier existe
        if not os.path.exists(backup_file):
            raise CommandError(f"âŒ Fichier non trouvÃ©: {backup_file}")

        self.stdout.write(
            self.style.WARNING("âš ï¸  ATTENTION: Cette opÃ©ration va modifier la base de donnÃ©es")
        )

        # Confirmation
        confirm = input("Voulez-vous continuer? (oui/non): ")
        if confirm.lower() not in ["oui", "yes", "y"]:
            self.stdout.write(self.style.ERROR("âŒ Restauration annulÃ©e"))
            return

        # Flush si demandÃ©
        if options["flush"]:
            self.stdout.write(self.style.WARNING("ðŸ—‘ï¸  Vidage de la base de donnÃ©es..."))
            call_command("flush", "--no-input")

        # DÃ©compresser si nÃ©cessaire
        if backup_file.endswith(".gz"):
            self.stdout.write(self.style.SUCCESS("ðŸ“¦ DÃ©compression du backup..."))
            temp_file = backup_file.replace(".gz", "")

            with gzip.open(backup_file, "rb") as f_in:
                with open(temp_file, "wb") as f_out:
                    f_out.write(f_in.read())

            backup_file = temp_file

        # Restaurer
        self.stdout.write(self.style.SUCCESS("ðŸ”„ Restauration en cours..."))

        with open(backup_file, "r") as f:
            call_command("loaddata", backup_file)

        self.stdout.write(self.style.SUCCESS("âœ… Restauration terminÃ©e avec succÃ¨s"))

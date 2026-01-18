"""
Commande Django pour entrainer le modele de scoring credit.
Usage: python manage.py train_scoring_model
"""

from django.core.management.base import BaseCommand
from suivi_demande.models import DossierCredit, DossierStatutAgent
from suivi_demande.ml.credit_scoring import CreditScoringModel


class Command(BaseCommand):
    help = "Entraine le modele de scoring credit sur l'historique des dossiers"

    def handle(self, *args, **options):
        self.stdout.write("ðŸ¤– Entrainement du modele de scoring credit...")

        # Recuperer les dossiers avec statuts finaux
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
                DossierStatutAgent.FONDS_LIBERE,
                DossierStatutAgent.REFUSE,
            ]
        ).select_related("canevas")

        count = dossiers.count()
        self.stdout.write(f"ðŸ“Š {count} dossiers trouves pour l'entrainement")

        if count < 10:
            self.stdout.write(
                self.style.WARNING(f"âš ï¸  Pas assez de donnees (minimum 10, trouves {count})")
            )
            return

        # Entrainer le modele
        model = CreditScoringModel()
        metrics = model.train(dossiers)

        if metrics is None:
            self.stdout.write(self.style.ERROR("âŒ e‰chec de l'entrainement"))
            return

        # Afficher les resultats
        self.stdout.write(self.style.SUCCESS(f"âœ… Modele entraine avec succes!"))
        self.stdout.write(f"   Precision: {metrics['accuracy']:.2%}")
        self.stdout.write(f"   Donnees d'entrainement: {metrics['n_train']}")
        self.stdout.write(f"   Donnees de test: {metrics['n_test']}")

        # Importance des features
        importance = model.get_feature_importance()
        if importance:
            self.stdout.write("\nðŸ“ˆ Importance des features:")
            for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                self.stdout.write(f"   {feature}: {score:.3f}")

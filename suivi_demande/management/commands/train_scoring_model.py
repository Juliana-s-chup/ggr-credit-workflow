"""
Commande Django pour entraÃ®ner le modÃ¨le de scoring crÃ©dit.
Usage: python manage.py train_scoring_model
"""

from django.core.management.base import BaseCommand
from suivi_demande.models import DossierCredit, DossierStatutAgent
from suivi_demande.ml.credit_scoring import CreditScoringModel


class Command(BaseCommand):
    help = "EntraÃ®ne le modÃ¨le de scoring crÃ©dit sur l'historique des dossiers"

    def handle(self, *args, **options):
        self.stdout.write("ðŸ¤– EntraÃ®nement du modÃ¨le de scoring crÃ©dit...")

        # RÃ©cupÃ©rer les dossiers avec statuts finaux
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
                DossierStatutAgent.FONDS_LIBERE,
                DossierStatutAgent.REFUSE,
            ]
        ).select_related("canevas")

        count = dossiers.count()
        self.stdout.write(f"ðŸ“Š {count} dossiers trouvÃ©s pour l'entraÃ®nement")

        if count < 10:
            self.stdout.write(
                self.style.WARNING(f"âš ï¸  Pas assez de donnÃ©es (minimum 10, trouvÃ©s {count})")
            )
            return

        # EntraÃ®ner le modÃ¨le
        model = CreditScoringModel()
        metrics = model.train(dossiers)

        if metrics is None:
            self.stdout.write(self.style.ERROR("âŒ Ã‰chec de l'entraÃ®nement"))
            return

        # Afficher les rÃ©sultats
        self.stdout.write(self.style.SUCCESS(f"âœ… ModÃ¨le entraÃ®nÃ© avec succÃ¨s!"))
        self.stdout.write(f"   PrÃ©cision: {metrics['accuracy']:.2%}")
        self.stdout.write(f"   DonnÃ©es d'entraÃ®nement: {metrics['n_train']}")
        self.stdout.write(f"   DonnÃ©es de test: {metrics['n_test']}")

        # Importance des features
        importance = model.get_feature_importance()
        if importance:
            self.stdout.write("\nðŸ“ˆ Importance des features:")
            for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                self.stdout.write(f"   {feature}: {score:.3f}")

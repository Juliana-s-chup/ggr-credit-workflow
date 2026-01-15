"""
Commande Django pour entraîner le modèle de scoring crédit.
Usage: python manage.py train_scoring_model
"""
from django.core.management.base import BaseCommand
from suivi_demande.models import DossierCredit, DossierStatutAgent
from suivi_demande.ml.credit_scoring import CreditScoringModel


class Command(BaseCommand):
    help = 'Entraîne le modèle de scoring crédit sur l\'historique des dossiers'

    def handle(self, *args, **options):
        self.stdout.write("🤖 Entraînement du modèle de scoring crédit...")
        
        # Récupérer les dossiers avec statuts finaux
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
                DossierStatutAgent.FONDS_LIBERE,
                DossierStatutAgent.REFUSE
            ]
        ).select_related('canevas')
        
        count = dossiers.count()
        self.stdout.write(f"📊 {count} dossiers trouvés pour l'entraînement")
        
        if count < 10:
            self.stdout.write(self.style.WARNING(
                f"⚠️  Pas assez de données (minimum 10, trouvés {count})"
            ))
            return
        
        # Entraîner le modèle
        model = CreditScoringModel()
        metrics = model.train(dossiers)
        
        if metrics is None:
            self.stdout.write(self.style.ERROR("❌ Échec de l'entraînement"))
            return
        
        # Afficher les résultats
        self.stdout.write(self.style.SUCCESS(
            f"✅ Modèle entraîné avec succès!"
        ))
        self.stdout.write(f"   Précision: {metrics['accuracy']:.2%}")
        self.stdout.write(f"   Données d'entraînement: {metrics['n_train']}")
        self.stdout.write(f"   Données de test: {metrics['n_test']}")
        
        # Importance des features
        importance = model.get_feature_importance()
        if importance:
            self.stdout.write("\n📈 Importance des features:")
            for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                self.stdout.write(f"   {feature}: {score:.3f}")

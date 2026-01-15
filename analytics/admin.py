"""
Module Analytics - Configuration Admin Django
"""

from django.contrib import admin
from .models import StatistiquesDossier, PerformanceActeur, PredictionRisque


@admin.register(StatistiquesDossier)
class StatistiquesDossierAdmin(admin.ModelAdmin):
    list_display = ('periode', 'date_calcul', 'total_dossiers', 'taux_approbation', 'montant_total_demande')
    list_filter = ('periode', 'date_calcul')
    search_fields = ('periode',)
    readonly_fields = ('date_calcul',)
    
    fieldsets = (
        ('Période', {
            'fields': ('periode', 'date_calcul')
        }),
        ('Compteurs', {
            'fields': ('total_dossiers', 'dossiers_en_cours', 'dossiers_approuves', 'dossiers_rejetes', 'dossiers_archives')
        }),
        ('Montants', {
            'fields': ('montant_total_demande', 'montant_total_approuve', 'montant_moyen_demande')
        }),
        ('Délais et Taux', {
            'fields': ('delai_moyen_traitement', 'taux_approbation', 'taux_rejet')
        }),
    )


@admin.register(PerformanceActeur)
class PerformanceActeurAdmin(admin.ModelAdmin):
    list_display = ('acteur', 'periode_debut', 'periode_fin', 'dossiers_traites', 'taux_approbation', 'score_performance')
    list_filter = ('periode_debut', 'periode_fin')
    search_fields = ('acteur__username', 'acteur__first_name', 'acteur__last_name')
    readonly_fields = ('date_calcul',)


@admin.register(PredictionRisque)
class PredictionRisqueAdmin(admin.ModelAdmin):
    list_display = ('dossier', 'classe_risque', 'score_risque', 'probabilite_defaut', 'date_prediction')
    list_filter = ('classe_risque', 'date_prediction')
    search_fields = ('dossier__reference',)
    readonly_fields = ('date_prediction',)
    
    fieldsets = (
        ('Dossier', {
            'fields': ('dossier',)
        }),
        ('Prédiction', {
            'fields': ('score_risque', 'probabilite_defaut', 'classe_risque', 'confiance')
        }),
        ('Détails', {
            'fields': ('facteurs_risque', 'recommandation', 'modele_version', 'date_prediction')
        }),
    )

"""
Module Analytics - Configuration de l'application Django
"""

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "analytics"
    verbose_name = "Analytics & Reporting"

    def ready(self):
        """
        Code execute au demarrage de l'application
        """
        # Import des signaux si necessaire
        # import analytics.signals
        pass

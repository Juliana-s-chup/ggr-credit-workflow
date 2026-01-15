"""
Configuration de l'interface d'administration Django.
"""
from django.contrib import admin

from .models import (
    UserProfile,
    DossierCredit,
    PieceJointe,
    Commentaire,
    JournalAction,
    Notification,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone", "birth_date")
    search_fields = ("user__username", "user__email", "full_name", "phone")


@admin.register(DossierCredit)
class DossierCreditAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reference",
        "client",
        "produit",
        "montant",
        "statut_agent",
        "statut_client",
        "acteur_courant",
        "is_archived",
        "date_soumission",
    )
    list_filter = ("statut_agent", "statut_client", "is_archived", "date_soumission")
    search_fields = ("reference", "client__username", "client__email")


@admin.register(PieceJointe)
class PieceJointeAdmin(admin.ModelAdmin):
    list_display = ("id", "dossier", "type_piece", "taille", "upload_by", "upload_at")
    list_filter = ("type_piece", "upload_at")
    search_fields = ("dossier__reference",)


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ("id", "dossier", "auteur", "cible_role", "created_at")
    list_filter = ("cible_role", "created_at")
    search_fields = ("dossier__reference", "auteur__username")


@admin.register(JournalAction)
class JournalActionAdmin(admin.ModelAdmin):
    list_display = ("id", "dossier", "action", "de_statut", "vers_statut", "acteur", "timestamp")
    list_filter = ("action", "de_statut", "vers_statut", "timestamp")
    search_fields = ("dossier__reference", "acteur__username")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "utilisateur_cible", "type", "titre", "lu", "canal", "created_at")
    list_filter = ("lu", "canal", "created_at")
    search_fields = ("titre", "utilisateur_cible__username")
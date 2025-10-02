from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class UserRoles(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    GESTIONNAIRE = "GESTIONNAIRE", "Gestionnaire"
    ANALYSTE = "ANALYSTE", "Analyste crédit"
    RESPONSABLE_GGR = "RESPONSABLE_GGR", "Responsable GGR"
    BOE = "BOE", "Back Office Engagement"
    SUPER_ADMIN = "SUPER_ADMIN", "Super administrateur"

class CreditApplication(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Brouillon"),
        ("SUBMITTED", "Soumis"),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_applications")
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.client} ({self.status})"


class UserProfile(models.Model):
    """Informations supplémentaires pour l'utilisateur (inscription)."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    role = models.CharField(max_length=32, choices=UserRoles.choices, default=UserRoles.CLIENT)

    def __str__(self):
        return f"Profil de {self.user.username}"


# --- Workflow & Dossiers ---


class DossierStatutAgent(models.TextChoices):
    NOUVEAU = "NOUVEAU", "Nouveau dossier crédit"
    TRANSMIS_RESP_GEST = "TRANSMIS_RESP_GEST", "Transmis au responsable Gestionnaire"
    TRANSMIS_ANALYSTE = "TRANSMIS_ANALYSTE", "Transmis à l’analyste crédit"
    EN_COURS_ANALYSE = "EN_COURS_ANALYSE", "En cours d’analyse risqué"
    EN_COURS_VALIDATION_GGR = "EN_COURS_VALIDATION_GGR", "En cours validation GGR"
    EN_ATTENTE_DECISION_DG = "EN_ATTENTE_DECISION_DG", "En attente décision DG"
    APPROUVE_ATTENTE_FONDS = "APPROUVE_ATTENTE_FONDS", "Approuvé, en attente de libération de fonds"
    FONDS_LIBERE = "FONDS_LIBERE", "Fonds libéré"
    REFUSE = "REFUSE", "Refusé / Non approuvé"


class DossierStatutClient(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", "En attente"
    EN_COURS_TRAITEMENT = "EN_COURS_TRAITEMENT", "En cours de traitement"
    TERMINE = "TERMINE", "Traitement terminé"
    SE_RAPPROCHER_GEST = "SE_RAPPROCHER_GEST", "Se rapprocher du gestionnaire"


def piece_upload_to(instance, filename: str) -> str:
    ref = instance.dossier.reference if instance.dossier_id else "no-ref"
    return f"dossiers/{ref}/{filename}"


class DossierCredit(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dossiers")
    reference = models.CharField(max_length=30, unique=True)
    produit = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    statut_agent = models.CharField(max_length=40, choices=DossierStatutAgent.choices, default=DossierStatutAgent.NOUVEAU)
    statut_client = models.CharField(max_length=40, choices=DossierStatutClient.choices, default=DossierStatutClient.EN_ATTENTE)
    acteur_courant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="dossiers_en_cours")
    is_archived = models.BooleanField(default=False)
    date_soumission = models.DateTimeField(default=timezone.now)
    date_maj = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} - {self.client}"


class PieceJointe(models.Model):
    TYPE_PIECE_CHOICES = [
        ("CNI", "Carte Nationale d'Identité"),
        ("FICHE_PAIE", "Fiche de paie"),
        ("RELEVE_BANCAIRE", "Relevé bancaire"),
        ("AUTRE", "Autre"),
    ]
    dossier = models.ForeignKey(DossierCredit, on_delete=models.CASCADE, related_name="pieces")
    fichier = models.FileField(upload_to=piece_upload_to)
    type_piece = models.CharField(max_length=30, choices=TYPE_PIECE_CHOICES)
    taille = models.PositiveIntegerField(default=0)
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    upload_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_piece} - {self.dossier.reference}"


class Commentaire(models.Model):
    dossier = models.ForeignKey(DossierCredit, on_delete=models.CASCADE, related_name="commentaires")
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    cible_role = models.CharField(max_length=32, choices=UserRoles.choices, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire {self.id} sur {self.dossier.reference}"


class JournalAction(models.Model):
    ACTIONS = [
        ("CREATION", "Création du dossier"),
        ("MISE_A_JOUR", "Mise à jour"),
        ("TRANSITION", "Transition d'état"),
        ("RETROU", "Retour étape précédente"),
        ("APPROBATION", "Approbation"),
        ("REFUS", "Refus"),
        ("LIBERATION_FONDS", "Libération des fonds"),
    ]
    dossier = models.ForeignKey(DossierCredit, on_delete=models.CASCADE, related_name="journal")
    action = models.CharField(max_length=30, choices=ACTIONS)
    de_statut = models.CharField(max_length=40, choices=DossierStatutAgent.choices, null=True, blank=True)
    vers_statut = models.CharField(max_length=40, choices=DossierStatutAgent.choices, null=True, blank=True)
    acteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    commentaire_systeme = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.action} - {self.dossier.reference}"


class Notification(models.Model):
    CANAUX = [
        ("INTERNE", "Interne"),
        ("EMAIL", "Email"),
    ]
    utilisateur_cible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=50)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    canal = models.CharField(max_length=20, choices=CANAUX, default="INTERNE")

    def __str__(self):
        return f"Notif {self.type} -> {self.utilisateur_cible}"

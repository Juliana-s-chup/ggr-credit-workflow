# core/models_refactored.py
"""
MODÈLES REFACTORISÉS - CRÉDIT DU CONGO
Élimination des incohérences et unification des concepts métier
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class UserRoles(models.TextChoices):
    """Rôles utilisateurs standardisés"""
    CLIENT = "CLIENT", "Client"
    GESTIONNAIRE = "GESTIONNAIRE", "Gestionnaire de clientèle"
    ANALYSTE = "ANALYSTE", "Analyste crédit"
    RESPONSABLE_GGR = "RESPONSABLE_GGR", "Responsable GGR"
    BOE = "BOE", "Back Office Engagement"
    SUPER_ADMIN = "SUPER_ADMIN", "Super administrateur"


class ProduitCredit(models.Model):
    """Catalogue des produits de crédit"""
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    description = models.TextField()
    taux_min = models.DecimalField(max_digits=5, decimal_places=2)
    taux_max = models.DecimalField(max_digits=5, decimal_places=2)
    montant_min = models.DecimalField(max_digits=12, decimal_places=2)
    montant_max = models.DecimalField(max_digits=12, decimal_places=2)
    duree_min_mois = models.PositiveIntegerField()
    duree_max_mois = models.PositiveIntegerField()
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Produit de crédit"
        verbose_name_plural = "Produits de crédit"
    
    def __str__(self):
        return f"{self.code} - {self.nom}"


class StatutDossier(models.TextChoices):
    """États unifiés du workflow de crédit"""
    # États client
    BROUILLON = "BROUILLON", "Brouillon"
    SOUMIS = "SOUMIS", "Soumis pour traitement"
    
    # États gestionnaire
    RECU_GESTIONNAIRE = "RECU_GESTIONNAIRE", "Reçu par le gestionnaire"
    DOCUMENTS_INCOMPLETS = "DOCUMENTS_INCOMPLETS", "Documents incomplets"
    
    # États analyste
    EN_ANALYSE = "EN_ANALYSE", "En cours d'analyse"
    ANALYSE_TERMINEE = "ANALYSE_TERMINEE", "Analyse terminée"
    
    # États responsable GGR
    EN_VALIDATION_GGR = "EN_VALIDATION_GGR", "En validation GGR"
    VALIDE_GGR = "VALIDE_GGR", "Validé par GGR"
    
    # États BOE
    EN_ENGAGEMENT = "EN_ENGAGEMENT", "En cours d'engagement"
    FONDS_LIBERES = "FONDS_LIBERES", "Fonds libérés"
    
    # États finaux
    APPROUVE = "APPROUVE", "Approuvé"
    REJETE = "REJETE", "Rejeté"
    ANNULE = "ANNULE", "Annulé"


class PrioriteTraitement(models.TextChoices):
    """Niveaux de priorité"""
    BASSE = "BASSE", "Basse"
    NORMALE = "NORMALE", "Normale"
    HAUTE = "HAUTE", "Haute"
    URGENTE = "URGENTE", "Urgente"


class DossierCredit(models.Model):
    """
    MODÈLE UNIFIÉ - Fusion de CreditApplication et DossierCredit
    Représente une demande de crédit complète du début à la fin
    """
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=30, unique=True, db_index=True)
    
    # Parties prenantes
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="dossiers_credit"
    )
    gestionnaire_assigne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="dossiers_geres",
        limit_choices_to={'profile__role': UserRoles.GESTIONNAIRE}
    )
    analyste_assigne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="dossiers_analyses",
        limit_choices_to={'profile__role': UserRoles.ANALYSTE}
    )
    
    # Détails du crédit
    produit = models.ForeignKey(ProduitCredit, on_delete=models.PROTECT)
    montant_demande = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('100000'))]  # 100k FCFA minimum
    )
    duree_mois = models.PositiveIntegerField(
        validators=[MinValueValidator(6), MaxValueValidator(360)]
    )
    objet_financement = models.TextField()
    
    # Workflow et statuts
    statut = models.CharField(
        max_length=30, 
        choices=StatutDossier.choices, 
        default=StatutDossier.BROUILLON,
        db_index=True
    )
    priorite = models.CharField(
        max_length=20,
        choices=PrioriteTraitement.choices,
        default=PrioriteTraitement.NORMALE
    )
    
    # Métadonnées temporelles
    date_creation = models.DateTimeField(auto_now_add=True)
    date_soumission = models.DateTimeField(null=True, blank=True)
    date_derniere_maj = models.DateTimeField(auto_now=True)
    date_echeance_traitement = models.DateTimeField(null=True, blank=True)
    
    # Résultat de l'analyse
    score_risque = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    montant_approuve = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    taux_approuve = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True
    )
    
    # Flags de gestion
    is_archived = models.BooleanField(default=False)
    requires_documents = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Dossier de crédit"
        verbose_name_plural = "Dossiers de crédit"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['statut', 'priorite']),
            models.Index(fields=['client', 'statut']),
            models.Index(fields=['date_creation']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.client.get_full_name()} ({self.get_statut_display()})"
    
    @property
    def peut_etre_soumis(self):
        """Vérifie si le dossier peut être soumis"""
        return (
            self.statut == StatutDossier.BROUILLON and
            self.pieces_jointes.filter(obligatoire=True).count() >= 3
        )
    
    @property
    def delai_traitement_jours(self):
        """Calcule le délai de traitement en jours"""
        if not self.date_soumission:
            return 0
        fin = self.date_derniere_maj if self.statut in [StatutDossier.APPROUVE, StatutDossier.REJETE] else timezone.now()
        return (fin - self.date_soumission).days
    
    def generer_reference(self):
        """Génère une référence unique"""
        if not self.reference:
            year = timezone.now().year
            count = DossierCredit.objects.filter(
                date_creation__year=year
            ).count() + 1
            self.reference = f"CR-{year}-{count:06d}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.generer_reference()
        super().save(*args, **kwargs)


class TypePieceJointe(models.Model):
    """Types de pièces jointes standardisés"""
    code = models.CharField(max_length=30, unique=True)
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    obligatoire_par_defaut = models.BooleanField(default=False)
    formats_acceptes = models.JSONField(default=list)  # ['pdf', 'jpg', 'png']
    taille_max_mb = models.PositiveIntegerField(default=5)
    
    def __str__(self):
        return self.libelle


def piece_upload_path(instance, filename):
    """Chemin de stockage des pièces jointes"""
    return f"dossiers/{instance.dossier.reference}/pieces/{filename}"


class PieceJointe(models.Model):
    """Pièces jointes du dossier"""
    dossier = models.ForeignKey(
        DossierCredit, 
        on_delete=models.CASCADE, 
        related_name="pieces_jointes"
    )
    type_piece = models.ForeignKey(TypePieceJointe, on_delete=models.PROTECT)
    fichier = models.FileField(upload_to=piece_upload_path)
    nom_original = models.CharField(max_length=255)
    taille_octets = models.PositiveIntegerField()
    obligatoire = models.BooleanField(default=False)
    
    # Métadonnées
    upload_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    date_upload = models.DateTimeField(auto_now_add=True)
    verifie = models.BooleanField(default=False)
    verifie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="pieces_verifiees"
    )
    date_verification = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['dossier', 'type_piece']
    
    def __str__(self):
        return f"{self.type_piece.libelle} - {self.dossier.reference}"


class ActionDossier(models.Model):
    """Journal des actions sur le dossier"""
    TYPES_ACTION = [
        ("CREATION", "Création du dossier"),
        ("SOUMISSION", "Soumission"),
        ("ASSIGNATION", "Assignation"),
        ("TRANSITION_STATUT", "Changement de statut"),
        ("AJOUT_PIECE", "Ajout de pièce jointe"),
        ("COMMENTAIRE", "Ajout de commentaire"),
        ("ANALYSE", "Analyse effectuée"),
        ("DECISION", "Décision prise"),
        ("LIBERATION_FONDS", "Libération des fonds"),
    ]
    
    dossier = models.ForeignKey(
        DossierCredit, 
        on_delete=models.CASCADE, 
        related_name="actions"
    )
    type_action = models.CharField(max_length=30, choices=TYPES_ACTION)
    acteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    
    # Détails de l'action
    ancien_statut = models.CharField(
        max_length=30, 
        choices=StatutDossier.choices, 
        null=True, blank=True
    )
    nouveau_statut = models.CharField(
        max_length=30, 
        choices=StatutDossier.choices, 
        null=True, blank=True
    )
    
    description = models.TextField()
    metadonnees = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_type_action_display()} - {self.dossier.reference}"


class CommentaireDossier(models.Model):
    """Commentaires et communications sur le dossier"""
    dossier = models.ForeignKey(
        DossierCredit, 
        on_delete=models.CASCADE, 
        related_name="commentaires"
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    
    contenu = models.TextField()
    visible_client = models.BooleanField(default=False)
    destinataire_role = models.CharField(
        max_length=32, 
        choices=UserRoles.choices, 
        null=True, blank=True
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Commentaire {self.id} - {self.dossier.reference}"


class UserProfile(models.Model):
    """Profil utilisateur étendu"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="profile"
    )
    
    # Informations personnelles
    telephone = models.CharField(max_length=20, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    adresse = models.TextField(blank=True)
    
    # Informations professionnelles
    role = models.CharField(
        max_length=32, 
        choices=UserRoles.choices, 
        default=UserRoles.CLIENT
    )
    departement = models.CharField(max_length=100, blank=True)
    date_embauche = models.DateField(null=True, blank=True)
    
    # Préférences
    notifications_email = models.BooleanField(default=True)
    notifications_sms = models.BooleanField(default=False)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"


class Notification(models.Model):
    """Système de notifications unifié"""
    TYPES_NOTIFICATION = [
        ("NOUVEAU_DOSSIER", "Nouveau dossier"),
        ("CHANGEMENT_STATUT", "Changement de statut"),
        ("DOCUMENT_REQUIS", "Document requis"),
        ("DECISION_PRISE", "Décision prise"),
        ("ECHEANCE_PROCHE", "Échéance proche"),
        ("SYSTEME", "Notification système"),
    ]
    
    CANAUX = [
        ("INTERNE", "Notification interne"),
        ("EMAIL", "Email"),
        ("SMS", "SMS"),
    ]
    
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="notifications"
    )
    dossier = models.ForeignKey(
        DossierCredit, 
        on_delete=models.CASCADE, 
        null=True, blank=True,
        related_name="notifications"
    )
    
    type_notification = models.CharField(max_length=30, choices=TYPES_NOTIFICATION)
    canal = models.CharField(max_length=20, choices=CANAUX, default="INTERNE")
    
    titre = models.CharField(max_length=200)
    message = models.TextField()
    
    # État
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées pour l'envoi
    envoyee = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(null=True, blank=True)
    erreur_envoi = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['destinataire', 'lue']),
            models.Index(fields=['date_creation']),
        ]
    
    def __str__(self):
        return f"{self.get_type_notification_display()} -> {self.destinataire.username}"

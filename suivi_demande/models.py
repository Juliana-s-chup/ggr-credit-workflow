"""
Modeles pour l'application suivi_demande.
Gere les dossiers de credit, les utilisateurs, les notifications et le workflow.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class UserRoles(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    GESTIONNAIRE = "GESTIONNAIRE", "Gestionnaire"
    ANALYSTE = "ANALYSTE", "Analyste credit"
    RESPONSABLE_GGR = "RESPONSABLE_GGR", "Responsable GGR"
    BOE = "BOE", "Back Office Engagement"
    SUPER_ADMIN = "SUPER_ADMIN", "Super administrateur"


class UserProfile(models.Model):
    """Informations supplementaires pour l'utilisateur (inscription)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    role = models.CharField(
        max_length=32, choices=UserRoles.choices, default=UserRoles.CLIENT
    )

    def __str__(self):
        return f"Profil de {self.user.username}"


# --- Workflow & Dossiers ---


class DossierStatutAgent(models.TextChoices):
    NOUVEAU = "NOUVEAU", "Nouveau dossier credit"
    TRANSMIS_RESP_GEST = "TRANSMIS_RESP_GEST", "Transmis au responsable Gestionnaire"
    TRANSMIS_ANALYSTE = "TRANSMIS_ANALYSTE", "Transmis e  l'analyste credit"
    EN_COURS_ANALYSE = "EN_COURS_ANALYSE", "En cours d'analyse risque"
    EN_COURS_VALIDATION_GGR = "EN_COURS_VALIDATION_GGR", "En cours validation GGR"
    EN_ATTENTE_DECISION_DG = "EN_ATTENTE_DECISION_DG", "En attente decision DG"
    APPROUVE_ATTENTE_FONDS = (
        "APPROUVE_ATTENTE_FONDS",
        "Approuve, en attente de liberation de fonds",
    )
    FONDS_LIBERE = "FONDS_LIBERE", "Fonds libere"
    REFUSE = "REFUSE", "Refuse / Non approuve"


class DossierStatutClient(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", "En attente"
    EN_COURS_TRAITEMENT = "EN_COURS_TRAITEMENT", "En cours de traitement"
    TERMINE = "TERMINE", "Traitement termine"
    SE_RAPPROCHER_GEST = "SE_RAPPROCHER_GEST", "Se rapprocher du gestionnaire"


def piece_upload_to(instance, filename: str) -> str:
    ref = instance.dossier.reference if instance.dossier_id else "no-ref"
    return f"dossiers/{ref}/{filename}"


class DossierCredit(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dossiers"
    )
    reference = models.CharField(max_length=30, unique=True, db_index=True)
    produit = models.CharField(max_length=100)
    montant = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    statut_agent = models.CharField(
        max_length=40,
        choices=DossierStatutAgent.choices,
        default=DossierStatutAgent.NOUVEAU,
        db_index=True,
    )
    statut_client = models.CharField(
        max_length=40,
        choices=DossierStatutClient.choices,
        default=DossierStatutClient.EN_ATTENTE,
    )
    acteur_courant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dossiers_en_cours",
    )
    is_archived = models.BooleanField(default=False, db_index=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dossiers_archives",
    )
    date_soumission = models.DateTimeField(default=timezone.now, db_index=True)
    date_maj = models.DateTimeField(auto_now=True)
    # Suivi du wizard (etapes)
    wizard_current_step = models.PositiveSmallIntegerField(
        default=1,
        choices=[
            (1, "e‰tape 1"),
            (2, "e‰tape 2"),
            (3, "e‰tape 3"),
            (4, "e‰tape 4"),
        ],
    )
    wizard_completed = models.BooleanField(default=False)
    consent_accepted = models.BooleanField(default=False)
    consent_accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date_soumission"]
        verbose_name = "Dossier de credit"
        verbose_name_plural = "Dossiers de credit"
        indexes = [
            models.Index(fields=["client", "statut_agent"]),
            models.Index(fields=["statut_agent", "is_archived"]),
        ]

    def __str__(self):
        return f"{self.reference} - {self.client}"

    def clean(self):
        """Validation metier du dossier."""
        from django.core.exceptions import ValidationError
        from .constants import MONTANT_MINIMUM_CREDIT, MONTANT_MAXIMUM_CREDIT

        if self.montant < MONTANT_MINIMUM_CREDIT:
            raise ValidationError(
                f"Le montant minimum est de {MONTANT_MINIMUM_CREDIT} FCFA"
            )

        if self.montant > MONTANT_MAXIMUM_CREDIT:
            raise ValidationError(
                f"Le montant maximum est de {MONTANT_MAXIMUM_CREDIT} FCFA"
            )


class PieceJointe(models.Model):
    TYPE_PIECE_CHOICES = [
        ("CNI", "Carte Nationale d'Identite"),
        ("FICHE_PAIE", "Fiche de paie"),
        ("RELEVE_BANCAIRE", "Releve bancaire"),
        ("BILLET_ORDRE", "Billet e  ordre"),
        ("ATTESTATION_EMPLOYEUR", "Attestation de l'employeur"),
        ("ATTESTATION_DOMICILIATION", "Attestation de domiciliation irrevocable"),
        ("ASSURANCE_DECES_INVALIDITE", "Assurance deces-invalidite"),
        ("AUTRE", "Autre"),
    ]
    dossier = models.ForeignKey(
        DossierCredit, on_delete=models.CASCADE, related_name="pieces"
    )
    fichier = models.FileField(upload_to=piece_upload_to)
    type_piece = models.CharField(max_length=30, choices=TYPE_PIECE_CHOICES)
    taille = models.PositiveIntegerField(default=0)
    upload_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    upload_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_piece} - {self.dossier.reference}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            if hasattr(self.dossier, "canevas"):
                self.dossier.canevas.update_doc_flags_from_pieces()
        except Exception:
            pass

    def delete(self, *args, **kwargs):
        dossier = self.dossier
        super().delete(*args, **kwargs)
        try:
            if hasattr(dossier, "canevas"):
                dossier.canevas.update_doc_flags_from_pieces()
        except Exception:
            pass


class CanevasProposition(models.Model):
    """Canevas de proposition de credit NOKI NOKI."""

    # Relation avec le dossier
    dossier = models.OneToOneField(
        DossierCredit, on_delete=models.CASCADE, related_name="canevas"
    )

    # === EN-TeŠTE ===
    agence = models.CharField(max_length=100, default="PNBR")
    code_agence = models.CharField(max_length=10, default="10")
    nom_exploitant = models.CharField(max_length=200, default="YOBA")
    matricule_exploitant = models.CharField(max_length=50, default="101")
    date_proposition = models.DateField(default=timezone.now)

    # === SECTION 1: RENSEIGNEMENTS SUR LE DEMANDEUR ===
    # Identite
    nom_prenom = models.CharField(max_length=200)
    date_naissance = models.DateField()
    nationalite = models.CharField(max_length=100, default="CONGOLAISE")

    # Adresse
    adresse_exacte = models.CharField(max_length=255)
    numero_telephone = models.CharField(max_length=30)
    telephone_travail = models.CharField(max_length=30, blank=True)
    telephone_domicile = models.CharField(max_length=30, blank=True)

    # Emploi
    radical = models.CharField(max_length=50, blank=True)
    date_ouverture_compte = models.DateField(null=True, blank=True)
    date_domiciliation_salaire = models.DateField(null=True, blank=True)
    emploi_occupe = models.CharField(max_length=200)
    statut_emploi = models.CharField(
        max_length=50,
        default="PRIVE",
        choices=[
            ("PRIVE", "Prive"),
            ("PUBLIC", "Public"),
        ],
    )
    anciennete_emploi = models.CharField(max_length=100)  # Ex: "16 ans et 06 mois"
    type_contrat = models.CharField(
        max_length=20,
        default="CDI",
        choices=[
            ("CDI", "CDI"),
            ("CDD", "CDD"),
            ("STAGE", "Stage"),
            ("AUTRE", "Autre"),
        ],
    )

    # Employeur
    nom_employeur = models.CharField(max_length=200)
    lieu_emploi = models.CharField(max_length=200)
    employeur_client_banque = models.BooleanField(default=False)
    radical_employeur = models.CharField(max_length=50, blank=True)

    # Situation familiale
    situation_famille = models.CharField(
        max_length=20,
        default="MARIE",
        choices=[
            ("CELIBATAIRE", "Celibataire"),
            ("MARIE", "Marie(e)"),
            ("DIVORCE", "Divorce(e)"),
            ("VEUF", "Veuf/Veuve"),
        ],
    )
    nombre_personnes_charge = models.IntegerField(default=0)
    regime_matrimonial = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ("COMMUNAUTE", "Communaute des biens"),
            ("SEPARATION", "Separation des biens"),
            ("PARTICIPATION", "Participation aux acquets"),
            ("AUTRE", "Autres"),
        ],
    )  # Si marie
    participation_enquetes = models.CharField(max_length=200, blank=True)

    # Logement
    salaire_conjoint = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    emploi_conjoint = models.CharField(max_length=200, blank=True)
    statut_logement = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ("LOCATAIRE", "Locataire"),
            ("PROPRIETAIRE", "Proprietaire"),
            ("AUTRES", "Autres (e  preciser)"),
        ],
    )
    numero_tf = models.CharField(max_length=100, blank=True)  # Si proprietaire
    logement_autres_precision = models.CharField(max_length=200, blank=True)

    # Nature du pret en cours
    nature_pret_cours = models.CharField(
        max_length=20,
        default="NOKI",
        choices=[
            ("NOKI", "NOKI"),
            ("AUTRE", "Autre"),
        ],
    )
    montant_origine_fcfa = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    date_derniere_echeance = models.DateField(null=True, blank=True)
    montant_echeance_fcfa = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    k_restant_du_fcfa = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # === SECTION 2: CAPACITe‰ D'ENDETTEMENT ===
    salaire_net_moyen_fcfa = models.DecimalField(max_digits=12, decimal_places=2)
    echeances_prets_relevees = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    total_echeances_credits_cours = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    salaire_net_avant_endettement_fcfa = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    capacite_endettement_brute_fcfa = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    capacite_endettement_nette_fcfa = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )

    # === SECTION 3: De‰TAILS DU CRe‰DIT ===
    nature_pret = models.CharField(
        max_length=20,
        default="PRET",
        choices=[
            ("CAUTION", "Caution"),
            ("PRET", "Pret"),
            ("DECOUVERT", "Decouvert"),
        ],
    )
    motif_credit = models.CharField(max_length=200, blank=True)

    # Demande du client
    demande_montant_fcfa = models.DecimalField(max_digits=12, decimal_places=2)
    demande_duree_mois = models.IntegerField()
    demande_taux_pourcent = models.DecimalField(max_digits=5, decimal_places=2)
    demande_periodicite = models.CharField(
        max_length=1,
        default="M",
        choices=[
            ("M", "Mensuelle"),
            ("T", "Trimestrielle"),
            ("S", "Semestrielle"),
            ("A", "Annuelle"),
        ],
    )
    demande_montant_echeance_fcfa = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    demande_date_1ere_echeance = models.DateField(null=True, blank=True)

    # Proposition
    proposition_montant_fcfa = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    proposition_duree_mois = models.IntegerField(null=True, blank=True)
    proposition_taux_pourcent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    proposition_periodicite = models.CharField(
        max_length=1,
        default="M",
        choices=[
            ("M", "Mensuelle"),
            ("T", "Trimestrielle"),
            ("S", "Semestrielle"),
            ("A", "Annuelle"),
        ],
    )
    proposition_montant_echeance_fcfa = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    proposition_date_1ere_echeance = models.DateField(null=True, blank=True)

    # === SECTION 4: DOCUMENTS & VALIDATIONS ===
    doc_cni_ok = models.BooleanField(default=False)
    doc_fiche_paie_ok = models.BooleanField(default=False)
    doc_releve_ok = models.BooleanField(default=False)
    doc_billet_ordre_ok = models.BooleanField(default=False)
    doc_attestation_employeur_ok = models.BooleanField(default=False)
    doc_attestation_domiciliation_ok = models.BooleanField(default=False)
    doc_assurance_deces_invalidite_ok = models.BooleanField(default=False)
    validation_consentement = models.BooleanField(default=False)

    def __str__(self):
        return f"Canevas {self.dossier.reference} - {self.nom_prenom}"

    def calculer_capacite_endettement(self):
        """
        Calcule automatiquement la capacite d'endettement.

        Regle metier : La capacite d'endettement brute est de 40% du salaire net moyen.
        La capacite nette est la capacite brute moins les echeances en cours.

        Raises:
            ValueError: Si le salaire est negatif ou nul.
        """
        from decimal import Decimal
        from .constants import TAUX_ENDETTEMENT_MAX

        if self.salaire_net_moyen_fcfa <= 0:
            raise ValueError("Le salaire net moyen doit etre positif")

        # Capacite brute = 40% du salaire net moyen
        self.capacite_endettement_brute_fcfa = (
            self.salaire_net_moyen_fcfa * TAUX_ENDETTEMENT_MAX
        )

        # Capacite nette = Capacite brute - echeances en cours
        self.capacite_endettement_nette_fcfa = max(
            Decimal("0"),
            self.capacite_endettement_brute_fcfa - self.total_echeances_credits_cours,
        )

        # Salaire net avant endettement
        self.salaire_net_avant_endettement_fcfa = (
            self.salaire_net_moyen_fcfa - self.total_echeances_credits_cours
        )

    def update_doc_flags_from_pieces(self):
        """Met e  jour les drapeaux documents (etape 4) en fonction des pieces du dossier."""
        types = set(self.dossier.pieces.values_list("type_piece", flat=True))
        mapping = {
            "CNI": "doc_cni_ok",
            "FICHE_PAIE": "doc_fiche_paie_ok",
            "RELEVE_BANCAIRE": "doc_releve_ok",
            "BILLET_ORDRE": "doc_billet_ordre_ok",
            "ATTESTATION_EMPLOYEUR": "doc_attestation_employeur_ok",
            "ATTESTATION_DOMICILIATION": "doc_attestation_domiciliation_ok",
            "ASSURANCE_DECES_INVALIDITE": "doc_assurance_deces_invalidite_ok",
        }
        for code, field in mapping.items():
            setattr(self, field, code in types)
        self.save(update_fields=list(mapping.values()))

    class Meta:
        verbose_name = "Canevas de proposition"
        verbose_name_plural = "Canevas de propositions"


class Commentaire(models.Model):
    dossier = models.ForeignKey(
        DossierCredit, on_delete=models.CASCADE, related_name="commentaires"
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    message = models.TextField()
    cible_role = models.CharField(
        max_length=32, choices=UserRoles.choices, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire {self.id} sur {self.dossier.reference}"


class JournalAction(models.Model):
    ACTIONS = [
        ("CREATION", "Creation du dossier"),
        ("MISE_A_JOUR", "Mise e  jour"),
        ("TRANSITION", "Transition d'etat"),
        ("RETOUR_CLIENT", "Retour au client"),
        ("RETOUR_GESTIONNAIRE", "Retour au gestionnaire"),
        ("APPROBATION", "Approbation"),
        ("REFUS", "Refus"),
        ("LIBERATION_FONDS", "Liberation des fonds"),
    ]
    dossier = models.ForeignKey(
        DossierCredit, on_delete=models.CASCADE, related_name="journal"
    )
    action = models.CharField(max_length=30, choices=ACTIONS)
    de_statut = models.CharField(
        max_length=40, choices=DossierStatutAgent.choices, null=True, blank=True
    )
    vers_statut = models.CharField(
        max_length=40, choices=DossierStatutAgent.choices, null=True, blank=True
    )
    acteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
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
    utilisateur_cible = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=50)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    canal = models.CharField(max_length=20, choices=CANAUX, default="INTERNE")

    def __str__(self):
        return f"Notif {self.type} -> {self.utilisateur_cible}"

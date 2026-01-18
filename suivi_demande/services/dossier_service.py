"""
Service layer pour la gestion des dossiers de credit.
Centralise la logique metier et evite la duplication dans les views.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import QuerySet, Prefetch, Q, Sum
from django.core.paginator import Paginator, Page
from django.utils import timezone
from django.db import models

from ..models import (
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    JournalAction,
    Notification,
    CanevasProposition,
    PieceJointe,
)
from ..user_utils import get_user_role
from ..models import UserRoles


class DossierService:
    """Service pour la gestion des dossiers de credit."""

    @staticmethod
    def get_dossiers_for_user(
        user: User,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Page:
        """
        Recupere les dossiers accessibles par un utilisateur avec pagination.
        Optimise avec select_related et prefetch_related.

        Args:
            user: Utilisateur connecte
            page: Numero de page
            per_page: Nombre d'elements par page
            filters: Filtres optionnels (statut, date, etc.)

        Returns:
            Page: Page Django avec les dossiers
        """
        role = get_user_role(user)

        # Base queryset optimise
        queryset = DossierCredit.objects.select_related(
            "client", "client__profile", "acteur_courant", "canevas"
        ).prefetch_related(
            Prefetch("pieces", queryset=PieceJointe.objects.order_by("-upload_at")),
            Prefetch("journal", queryset=JournalAction.objects.order_by("-timestamp")),
        )

        # Filtrage par role
        if role == UserRoles.CLIENT:
            queryset = queryset.filter(client=user)
        elif role == UserRoles.GESTIONNAIRE:
            # Gestionnaire voit tous les dossiers non archives
            queryset = queryset.filter(is_archived=False)
        elif role == UserRoles.ANALYSTE:
            # Analyste voit les dossiers en analyse
            queryset = queryset.filter(
                statut_agent__in=[
                    DossierStatutAgent.TRANSMIS_ANALYSTE,
                    DossierStatutAgent.EN_COURS_ANALYSE,
                ]
            )
        elif role == UserRoles.RESPONSABLE_GGR:
            # Responsable GGR voit les dossiers en validation
            queryset = queryset.filter(
                statut_agent__in=[
                    DossierStatutAgent.EN_COURS_VALIDATION_GGR,
                    DossierStatutAgent.EN_ATTENTE_DECISION_DG,
                ]
            )
        elif role == UserRoles.BOE:
            # BOE voit les dossiers approuves
            queryset = queryset.filter(
                statut_agent__in=[
                    DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
                ]
            )
        elif role == UserRoles.SUPER_ADMIN:
            # Super admin voit tout
            pass
        else:
            # Role inconnu: aucun dossier
            queryset = queryset.none()

        # Appliquer les filtres additionnels
        if filters:
            if "statut" in filters:
                queryset = queryset.filter(statut_agent=filters["statut"])
            if "date_debut" in filters:
                queryset = queryset.filter(date_soumission__gte=filters["date_debut"])
            if "date_fin" in filters:
                queryset = queryset.filter(date_soumission__lte=filters["date_fin"])
            if "search" in filters:
                search = filters["search"]
                queryset = queryset.filter(
                    Q(reference__icontains=search)
                    | Q(client__username__icontains=search)
                    | Q(produit__icontains=search)
                )

        # Tri par defaut
        queryset = queryset.order_by("-date_soumission")

        # Pagination
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page)

    @staticmethod
    def get_dossier_detail(dossier_id: int, user: User) -> Optional[DossierCredit]:
        """
        Recupere un dossier avec toutes ses relations (optimise).
        Verifie les permissions d'acces.

        Args:
            dossier_id: ID du dossier
            user: Utilisateur connecte

        Returns:
            DossierCredit ou None si non trouve/non autorise
        """
        try:
            dossier = (
                DossierCredit.objects.select_related(
                    "client", "client__profile", "acteur_courant", "canevas"
                )
                .prefetch_related(
                    "pieces",
                    "journal",
                    "commentaires",
                    "commentaires__auteur",
                )
                .get(pk=dossier_id)
            )

            # Verifier les permissions
            role = get_user_role(user)
            if role == UserRoles.CLIENT and dossier.client != user:
                return None

            return dossier
        except DossierCredit.DoesNotExist:
            return None

    @staticmethod
    def create_dossier(
        client: User, produit: str, montant: Decimal, created_by: User
    ) -> DossierCredit:
        """
        Cree un nouveau dossier de credit.

        Args:
            client: Client demandeur
            produit: Type de credit
            montant: Montant demande
            created_by: Utilisateur createur

        Returns:
            DossierCredit: Nouveau dossier cree
        """
        # Generer la reference
        year = timezone.now().year
        count = DossierCredit.objects.filter(date_soumission__year=year).count() + 1
        reference = f"DOS-{year}-{count:05d}"

        # Creer le dossier
        dossier = DossierCredit.objects.create(
            client=client,
            reference=reference,
            produit=produit,
            montant=montant,
            statut_agent=DossierStatutAgent.NOUVEAU,
            statut_client=DossierStatutClient.EN_ATTENTE,
        )

        # Creer l'entree journal
        JournalAction.objects.create(
            dossier=dossier,
            action="CREATION",
            vers_statut=DossierStatutAgent.NOUVEAU,
            acteur=created_by,
            commentaire_systeme=f"Dossier cree par {created_by.username}",
        )

        return dossier

    @staticmethod
    def transition_statut(
        dossier: DossierCredit,
        nouveau_statut: str,
        acteur: User,
        commentaire: Optional[str] = None,
    ) -> bool:
        """
        Effectue une transition de statut avec validation.

        Args:
            dossier: Dossier concerne
            nouveau_statut: Nouveau statut agent
            acteur: Utilisateur effectuant la transition
            commentaire: Commentaire optionnel

        Returns:
            bool: True si transition reussie
        """
        ancien_statut = dossier.statut_agent

        # Mettre e  jour le dossier
        dossier.statut_agent = nouveau_statut
        dossier.acteur_courant = acteur
        dossier.save()

        # Creer l'entree journal
        JournalAction.objects.create(
            dossier=dossier,
            action="TRANSITION",
            de_statut=ancien_statut,
            vers_statut=nouveau_statut,
            acteur=acteur,
            commentaire_systeme=commentaire
            or f"Transition {ancien_statut} â†’ {nouveau_statut}",
        )

        # Creer notification pour le client
        Notification.objects.create(
            utilisateur_cible=dossier.client,
            type="CHANGEMENT_STATUT",
            titre=f"Dossier {dossier.reference} - Mise e  jour",
            message=f"Votre dossier est passe au statut: {dossier.get_statut_agent_display()}",
            canal="INTERNE",
        )

        return True

    @staticmethod
    def get_statistics_for_role(user: User) -> Dict[str, Any]:
        """
        Calcule les statistiques pour un utilisateur selon son role.

        Args:
            user: Utilisateur connecte

        Returns:
            Dict: Statistiques (total, en_cours, approuves, refuses, etc.)
        """
        role = get_user_role(user)

        # Base queryset selon le role
        if role == UserRoles.CLIENT:
            queryset = DossierCredit.objects.filter(client=user)
        elif role == UserRoles.GESTIONNAIRE:
            queryset = DossierCredit.objects.filter(is_archived=False)
        elif role == UserRoles.SUPER_ADMIN:
            queryset = DossierCredit.objects.all()
        else:
            queryset = DossierCredit.objects.none()

        # Calculer les stats
        stats = {
            "total": queryset.count(),
            "en_cours": queryset.exclude(
                statut_agent__in=[
                    DossierStatutAgent.FONDS_LIBERE,
                    DossierStatutAgent.REFUSE,
                ]
            ).count(),
            "approuves": queryset.filter(
                statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS
            ).count(),
            "refuses": queryset.filter(statut_agent=DossierStatutAgent.REFUSE).count(),
            "montant_total": queryset.aggregate(total=Sum("montant"))["total"]
            or Decimal("0"),
        }

        return stats

"""
Service layer pour la gestion des dossiers de crÃ©dit.
Centralise la logique mÃ©tier et Ã©vite la duplication dans les views.
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
    """Service pour la gestion des dossiers de crÃ©dit."""

    @staticmethod
    def get_dossiers_for_user(
        user: User, page: int = 1, per_page: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> Page:
        """
        RÃ©cupÃ¨re les dossiers accessibles par un utilisateur avec pagination.
        OptimisÃ© avec select_related et prefetch_related.

        Args:
            user: Utilisateur connectÃ©
            page: NumÃ©ro de page
            per_page: Nombre d'Ã©lÃ©ments par page
            filters: Filtres optionnels (statut, date, etc.)

        Returns:
            Page: Page Django avec les dossiers
        """
        role = get_user_role(user)

        # Base queryset optimisÃ©
        queryset = DossierCredit.objects.select_related(
            "client", "client__profile", "acteur_courant", "canevas"
        ).prefetch_related(
            Prefetch("pieces", queryset=PieceJointe.objects.order_by("-upload_at")),
            Prefetch("journal", queryset=JournalAction.objects.order_by("-timestamp")),
        )

        # Filtrage par rÃ´le
        if role == UserRoles.CLIENT:
            queryset = queryset.filter(client=user)
        elif role == UserRoles.GESTIONNAIRE:
            # Gestionnaire voit tous les dossiers non archivÃ©s
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
            # BOE voit les dossiers approuvÃ©s
            queryset = queryset.filter(
                statut_agent__in=[
                    DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
                ]
            )
        elif role == UserRoles.SUPER_ADMIN:
            # Super admin voit tout
            pass
        else:
            # RÃ´le inconnu: aucun dossier
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

        # Tri par dÃ©faut
        queryset = queryset.order_by("-date_soumission")

        # Pagination
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page)

    @staticmethod
    def get_dossier_detail(dossier_id: int, user: User) -> Optional[DossierCredit]:
        """
        RÃ©cupÃ¨re un dossier avec toutes ses relations (optimisÃ©).
        VÃ©rifie les permissions d'accÃ¨s.

        Args:
            dossier_id: ID du dossier
            user: Utilisateur connectÃ©

        Returns:
            DossierCredit ou None si non trouvÃ©/non autorisÃ©
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

            # VÃ©rifier les permissions
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
        CrÃ©e un nouveau dossier de crÃ©dit.

        Args:
            client: Client demandeur
            produit: Type de crÃ©dit
            montant: Montant demandÃ©
            created_by: Utilisateur crÃ©ateur

        Returns:
            DossierCredit: Nouveau dossier crÃ©Ã©
        """
        # GÃ©nÃ©rer la rÃ©fÃ©rence
        year = timezone.now().year
        count = DossierCredit.objects.filter(date_soumission__year=year).count() + 1
        reference = f"DOS-{year}-{count:05d}"

        # CrÃ©er le dossier
        dossier = DossierCredit.objects.create(
            client=client,
            reference=reference,
            produit=produit,
            montant=montant,
            statut_agent=DossierStatutAgent.NOUVEAU,
            statut_client=DossierStatutClient.EN_ATTENTE,
        )

        # CrÃ©er l'entrÃ©e journal
        JournalAction.objects.create(
            dossier=dossier,
            action="CREATION",
            vers_statut=DossierStatutAgent.NOUVEAU,
            acteur=created_by,
            commentaire_systeme=f"Dossier crÃ©Ã© par {created_by.username}",
        )

        return dossier

    @staticmethod
    def transition_statut(
        dossier: DossierCredit, nouveau_statut: str, acteur: User, commentaire: Optional[str] = None
    ) -> bool:
        """
        Effectue une transition de statut avec validation.

        Args:
            dossier: Dossier concernÃ©
            nouveau_statut: Nouveau statut agent
            acteur: Utilisateur effectuant la transition
            commentaire: Commentaire optionnel

        Returns:
            bool: True si transition rÃ©ussie
        """
        ancien_statut = dossier.statut_agent

        # Mettre Ã  jour le dossier
        dossier.statut_agent = nouveau_statut
        dossier.acteur_courant = acteur
        dossier.save()

        # CrÃ©er l'entrÃ©e journal
        JournalAction.objects.create(
            dossier=dossier,
            action="TRANSITION",
            de_statut=ancien_statut,
            vers_statut=nouveau_statut,
            acteur=acteur,
            commentaire_systeme=commentaire or f"Transition {ancien_statut} â†’ {nouveau_statut}",
        )

        # CrÃ©er notification pour le client
        Notification.objects.create(
            utilisateur_cible=dossier.client,
            type="CHANGEMENT_STATUT",
            titre=f"Dossier {dossier.reference} - Mise Ã  jour",
            message=f"Votre dossier est passÃ© au statut: {dossier.get_statut_agent_display()}",
            canal="INTERNE",
        )

        return True

    @staticmethod
    def get_statistics_for_role(user: User) -> Dict[str, Any]:
        """
        Calcule les statistiques pour un utilisateur selon son rÃ´le.

        Args:
            user: Utilisateur connectÃ©

        Returns:
            Dict: Statistiques (total, en_cours, approuves, refuses, etc.)
        """
        role = get_user_role(user)

        # Base queryset selon le rÃ´le
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
                statut_agent__in=[DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
            ).count(),
            "approuves": queryset.filter(
                statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS
            ).count(),
            "refuses": queryset.filter(statut_agent=DossierStatutAgent.REFUSE).count(),
            "montant_total": queryset.aggregate(total=Sum("montant"))["total"] or Decimal("0"),
        }

        return stats

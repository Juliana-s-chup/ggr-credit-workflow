"""
Service layer pour la gestion des dossiers de crédit.
Centralise la logique métier et évite la duplication dans les views.
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
    """Service pour la gestion des dossiers de crédit."""

    @staticmethod
    def get_dossiers_for_user(
        user: User, page: int = 1, per_page: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> Page:
        """
        Récupère les dossiers accessibles par un utilisateur avec pagination.
        Optimisé avec select_related et prefetch_related.

        Args:
            user: Utilisateur connecté
            page: Numéro de page
            per_page: Nombre d'éléments par page
            filters: Filtres optionnels (statut, date, etc.)

        Returns:
            Page: Page Django avec les dossiers
        """
        role = get_user_role(user)

        # Base queryset optimisé
        queryset = DossierCredit.objects.select_related(
            "client", "client__profile", "acteur_courant", "canevas"
        ).prefetch_related(
            Prefetch("pieces", queryset=PieceJointe.objects.order_by("-upload_at")),
            Prefetch("journal", queryset=JournalAction.objects.order_by("-timestamp")),
        )

        # Filtrage par rôle
        if role == UserRoles.CLIENT:
            queryset = queryset.filter(client=user)
        elif role == UserRoles.GESTIONNAIRE:
            # Gestionnaire voit tous les dossiers non archivés
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
            # BOE voit les dossiers approuvés
            queryset = queryset.filter(
                statut_agent__in=[
                    DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
                ]
            )
        elif role == UserRoles.SUPER_ADMIN:
            # Super admin voit tout
            pass
        else:
            # Rôle inconnu: aucun dossier
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

        # Tri par défaut
        queryset = queryset.order_by("-date_soumission")

        # Pagination
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page)

    @staticmethod
    def get_dossier_detail(dossier_id: int, user: User) -> Optional[DossierCredit]:
        """
        Récupère un dossier avec toutes ses relations (optimisé).
        Vérifie les permissions d'accès.

        Args:
            dossier_id: ID du dossier
            user: Utilisateur connecté

        Returns:
            DossierCredit ou None si non trouvé/non autorisé
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

            # Vérifier les permissions
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
        Crée un nouveau dossier de crédit.

        Args:
            client: Client demandeur
            produit: Type de crédit
            montant: Montant demandé
            created_by: Utilisateur créateur

        Returns:
            DossierCredit: Nouveau dossier créé
        """
        # Générer la référence
        year = timezone.now().year
        count = DossierCredit.objects.filter(date_soumission__year=year).count() + 1
        reference = f"DOS-{year}-{count:05d}"

        # Créer le dossier
        dossier = DossierCredit.objects.create(
            client=client,
            reference=reference,
            produit=produit,
            montant=montant,
            statut_agent=DossierStatutAgent.NOUVEAU,
            statut_client=DossierStatutClient.EN_ATTENTE,
        )

        # Créer l'entrée journal
        JournalAction.objects.create(
            dossier=dossier,
            action="CREATION",
            vers_statut=DossierStatutAgent.NOUVEAU,
            acteur=created_by,
            commentaire_systeme=f"Dossier créé par {created_by.username}",
        )

        return dossier

    @staticmethod
    def transition_statut(
        dossier: DossierCredit, nouveau_statut: str, acteur: User, commentaire: Optional[str] = None
    ) -> bool:
        """
        Effectue une transition de statut avec validation.

        Args:
            dossier: Dossier concerné
            nouveau_statut: Nouveau statut agent
            acteur: Utilisateur effectuant la transition
            commentaire: Commentaire optionnel

        Returns:
            bool: True si transition réussie
        """
        ancien_statut = dossier.statut_agent

        # Mettre à jour le dossier
        dossier.statut_agent = nouveau_statut
        dossier.acteur_courant = acteur
        dossier.save()

        # Créer l'entrée journal
        JournalAction.objects.create(
            dossier=dossier,
            action="TRANSITION",
            de_statut=ancien_statut,
            vers_statut=nouveau_statut,
            acteur=acteur,
            commentaire_systeme=commentaire or f"Transition {ancien_statut} → {nouveau_statut}",
        )

        # Créer notification pour le client
        Notification.objects.create(
            utilisateur_cible=dossier.client,
            type="CHANGEMENT_STATUT",
            titre=f"Dossier {dossier.reference} - Mise à jour",
            message=f"Votre dossier est passé au statut: {dossier.get_statut_agent_display()}",
            canal="INTERNE",
        )

        return True

    @staticmethod
    def get_statistics_for_role(user: User) -> Dict[str, Any]:
        """
        Calcule les statistiques pour un utilisateur selon son rôle.

        Args:
            user: Utilisateur connecté

        Returns:
            Dict: Statistiques (total, en_cours, approuves, refuses, etc.)
        """
        role = get_user_role(user)

        # Base queryset selon le rôle
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

"""
Gestion des permissions pour les dossiers de crÃ©dit.
"""

from __future__ import annotations

from django.contrib.auth.models import AnonymousUser

from .models import DossierCredit, DossierStatutAgent, UserRoles


def get_user_role(user) -> str:
    if isinstance(user, AnonymousUser):
        return None
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", UserRoles.CLIENT)


def can_upload_piece(dossier: DossierCredit, user) -> bool:
    """RÃ¨gles (MVP) pour l'upload de piÃ¨ces jointes.
    - Client: dÃ©sactivÃ© (les clients n'uploadent plus de documents)
    - Gestionnaire: si statut_agent in {NOUVEAU, TRANSMIS_RESP_GEST}
    """
    role = get_user_role(user)
    if role == UserRoles.GESTIONNAIRE and dossier.statut_agent in (
        DossierStatutAgent.NOUVEAU,
        DossierStatutAgent.TRANSMIS_RESP_GEST,
    ):
        return True
    return False


def get_transition_flags(dossier: DossierCredit, user) -> dict:
    """Calcule les flags d'actions de transition autorisÃ©es pour l'utilisateur donnÃ©.
    Retourne un dict de boolÃ©ens:
      - can_tx_transmettre_analyste
      - can_tx_transmettre_ggr
      - can_tx_retour_gestionnaire
      - can_tx_approuver
      - can_tx_refuser
      - can_tx_liberer_fonds
    """
    role = get_user_role(user)
    statut = dossier.statut_agent

    return {
        "can_tx_transmettre_analyste": role == UserRoles.GESTIONNAIRE
        and statut
        in (
            DossierStatutAgent.NOUVEAU,
            DossierStatutAgent.TRANSMIS_RESP_GEST,
        ),
        "can_tx_retour_client": role == UserRoles.GESTIONNAIRE
        and statut
        in (
            DossierStatutAgent.NOUVEAU,
            DossierStatutAgent.TRANSMIS_RESP_GEST,
        ),
        "can_tx_transmettre_ggr": role == UserRoles.ANALYSTE
        and statut
        in (
            DossierStatutAgent.TRANSMIS_ANALYSTE,
            DossierStatutAgent.EN_COURS_ANALYSE,
        ),
        "can_tx_retour_gestionnaire": role == UserRoles.ANALYSTE
        and statut
        in (
            DossierStatutAgent.TRANSMIS_ANALYSTE,
            DossierStatutAgent.EN_COURS_ANALYSE,
        ),
        "can_tx_approuver": role == UserRoles.RESPONSABLE_GGR
        and statut
        in (
            DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            DossierStatutAgent.EN_ATTENTE_DECISION_DG,
        ),
        "can_tx_refuser": role == UserRoles.RESPONSABLE_GGR
        and statut
        in (
            DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            DossierStatutAgent.EN_ATTENTE_DECISION_DG,
            DossierStatutAgent.TRANSMIS_ANALYSTE,
            DossierStatutAgent.EN_COURS_ANALYSE,
        ),
        "can_tx_liberer_fonds": role == UserRoles.BOE
        and statut == DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
    }

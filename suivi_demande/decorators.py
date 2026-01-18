"""
Decorateurs pour la gestion des permissions et des transitions.
"""

from functools import wraps
from typing import Iterable

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404

from .models import DossierCredit, DossierStatutAgent, UserRoles


def role_required(roles: Iterable[str]):
    """Decorator to require that request.user has one of the given roles.
    roles: iterable of UserRoles values.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            profile = getattr(request.user, "profile", None)
            role = getattr(profile, "role", None)
            if role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "Acces non autorise pour votre role.")
            return redirect("suivi:dashboard")

        return _wrapped

    return decorator


def transition_allowed(view_func):
    """Decorator to validate that the current user can perform the transition specified by 'action' on the dossier 'pk'.
    If not allowed, redirect to dashboard with an error message.
    """

    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        pk = kwargs.get("pk")
        action = kwargs.get("action")
        if pk is None or action is None:
            messages.error(request, "Parametres de transition manquants.")
            return redirect("suivi:dashboard")

        dossier = get_object_or_404(DossierCredit, pk=pk)
        profile = getattr(request.user, "profile", None)
        role = getattr(profile, "role", None)

        allowed = False
        try:
            if role == UserRoles.GESTIONNAIRE and action == "transmettre_analyste":
                allowed = dossier.statut_agent in [
                    DossierStatutAgent.NOUVEAU,
                    DossierStatutAgent.TRANSMIS_RESP_GEST,
                ]
            elif role == UserRoles.GESTIONNAIRE and action == "retour_client":
                # Autoriser le retour au client par un gestionnaire
                allowed = dossier.statut_agent in [
                    DossierStatutAgent.NOUVEAU,
                    DossierStatutAgent.TRANSMIS_RESP_GEST,
                ]
            elif role == UserRoles.ANALYSTE and action == "transmettre_ggr":
                allowed = dossier.statut_agent in [
                    DossierStatutAgent.TRANSMIS_ANALYSTE,
                    DossierStatutAgent.EN_COURS_ANALYSE,
                ]
            elif role == UserRoles.ANALYSTE and action == "retour_gestionnaire":
                allowed = dossier.statut_agent in [
                    DossierStatutAgent.TRANSMIS_ANALYSTE,
                    DossierStatutAgent.EN_COURS_ANALYSE,
                ]
            elif role == UserRoles.RESPONSABLE_GGR and action == "approuver":
                allowed = dossier.statut_agent in [
                    DossierStatutAgent.EN_COURS_VALIDATION_GGR,
                    DossierStatutAgent.EN_ATTENTE_DECISION_DG,
                ]
            elif role == UserRoles.RESPONSABLE_GGR and action == "refuser":
                allowed = dossier.statut_agent in [
                    DossierStatutAgent.EN_COURS_VALIDATION_GGR,
                    DossierStatutAgent.EN_ATTENTE_DECISION_DG,
                    DossierStatutAgent.TRANSMIS_ANALYSTE,
                    DossierStatutAgent.EN_COURS_ANALYSE,
                ]
            elif role == UserRoles.BOE and action == "liberer_fonds":
                allowed = dossier.statut_agent == DossierStatutAgent.APPROUVE_ATTENTE_FONDS
        except Exception:
            allowed = False

        if not allowed:
            messages.error(request, "Action non autorisee pour votre role ou l'etat du dossier.")
            return redirect("suivi:dashboard")

        return view_func(request, *args, **kwargs)

    return _wrapped

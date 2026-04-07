"""
Vues de gestion du workflow : transitions d'etat des dossiers.
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.templatetags.static import static

from ..decorators import transition_allowed
from ..models import (
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    JournalAction,
    Notification,
    UserRoles,
)
from ..utils import get_current_namespace

User = get_user_model()
logger = logging.getLogger("suivi_demande")


@login_required
@transition_allowed
def transition_dossier(request, pk, action: str):
    """Effectue une transition d'etat sur un dossier en fonction du role et de l'action."""
    if request.method != "POST":
        messages.error(request, "Methode non autorisee.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    dossier = get_object_or_404(DossierCredit, pk=pk)
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", None)

    commentaire_retour = request.POST.get("commentaire_retour", "").strip()

    allowed = False
    de_statut = dossier.statut_agent
    vers_statut = None
    nouveau_statut_client = None
    action_log = None

    try:
        allowed, vers_statut, nouveau_statut_client, action_log = _resolve_transition(
            role, action, dossier, commentaire_retour, request
        )
    except _RetourClientRedirect as exc:
        return exc.response

    if not allowed:
        messages.error(
            request,
            "Action non autorisee pour votre role ou l'etat actuel du dossier.",
        )
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    # Appliquer la transition
    ancien_statut_client = dossier.statut_client
    dossier.statut_agent = vers_statut
    if nouveau_statut_client:
        dossier.statut_client = nouveau_statut_client
    dossier.acteur_courant = request.user
    dossier.save()

    # Journaliser
    commentaire_systeme = f"Action: {action}"
    if action == "retour_client" and commentaire_retour:
        commentaire_systeme += f" - Motif: {commentaire_retour}"

    JournalAction.objects.create(
        dossier=dossier,
        action=action_log or "TRANSITION",
        de_statut=de_statut,
        vers_statut=vers_statut,
        acteur=request.user,
        commentaire_systeme=commentaire_systeme,
        meta={
            "ancien_statut_client": ancien_statut_client,
            "nouveau_statut_client": dossier.statut_client,
            "role": role,
            "commentaire_retour": commentaire_retour if action == "retour_client" else None,
        },
    )

    # Notifications
    _send_transition_notifications(request, dossier, action, commentaire_retour)

    # Message de succes
    if action == "retour_client":
        messages.success(
            request,
            f"Le dossier {dossier.reference} a ete retourne au client avec vos commentaires.",
        )
    else:
        messages.success(request, "Transition effectuee avec succes.")

    namespace = get_current_namespace(request)
    return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)


@login_required
def transmettre_analyste_page(request, pk: int):
    """Page de confirmation de transmission a l'analyste."""
    dossier = get_object_or_404(DossierCredit, pk=pk)
    return render(request, "suivi_demande/transmettre_analyste.html", {"dossier": dossier})


# ---------------------------------------------------------------------------
# Helpers internes
# ---------------------------------------------------------------------------


class _RetourClientRedirect(Exception):
    """Exception interne pour gerer le redirect dans retour_client."""
    def __init__(self, response):
        self.response = response


def _resolve_transition(role, action, dossier, commentaire_retour, request):
    """Determine la transition a appliquer selon le role et l'action."""
    allowed = False
    vers_statut = None
    nouveau_statut_client = None
    action_log = None

    if role == UserRoles.GESTIONNAIRE and action == "transmettre_analyste":
        if dossier.statut_agent in [
            DossierStatutAgent.NOUVEAU,
            DossierStatutAgent.TRANSMIS_RESP_GEST,
        ]:
            vers_statut = DossierStatutAgent.TRANSMIS_ANALYSTE
            nouveau_statut_client = DossierStatutClient.EN_COURS_TRAITEMENT
            action_log = "TRANSITION"
            allowed = True

    elif role == UserRoles.GESTIONNAIRE and action == "retour_client":
        if dossier.statut_agent in [
            DossierStatutAgent.NOUVEAU,
            DossierStatutAgent.TRANSMIS_RESP_GEST,
        ]:
            if not commentaire_retour:
                messages.error(
                    request,
                    "Un commentaire expliquant pourquoi le dossier est incomplet est requis.",
                )
                namespace = get_current_namespace(request)
                raise _RetourClientRedirect(
                    redirect(f"{namespace}:dossier_detail", pk=dossier.pk)
                )
            vers_statut = DossierStatutAgent.NOUVEAU
            nouveau_statut_client = DossierStatutClient.SE_RAPPROCHER_GEST
            action_log = "RETOUR_CLIENT"
            allowed = True

    elif role == UserRoles.ANALYSTE and action == "transmettre_ggr":
        if dossier.statut_agent in [
            DossierStatutAgent.TRANSMIS_ANALYSTE,
            DossierStatutAgent.EN_COURS_ANALYSE,
        ]:
            vers_statut = DossierStatutAgent.EN_COURS_VALIDATION_GGR
            nouveau_statut_client = DossierStatutClient.EN_COURS_TRAITEMENT
            action_log = "TRANSITION"
            allowed = True

    elif role == UserRoles.ANALYSTE and action == "retour_gestionnaire":
        if dossier.statut_agent in [
            DossierStatutAgent.TRANSMIS_ANALYSTE,
            DossierStatutAgent.EN_COURS_ANALYSE,
        ]:
            vers_statut = DossierStatutAgent.TRANSMIS_RESP_GEST
            nouveau_statut_client = DossierStatutClient.EN_COURS_TRAITEMENT
            action_log = "RETOUR_GESTIONNAIRE"
            allowed = True

    elif role == UserRoles.RESPONSABLE_GGR and action == "approuver":
        if dossier.statut_agent in [
            DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            DossierStatutAgent.EN_ATTENTE_DECISION_DG,
        ]:
            vers_statut = DossierStatutAgent.APPROUVE_ATTENTE_FONDS
            nouveau_statut_client = DossierStatutClient.EN_COURS_TRAITEMENT
            action_log = "APPROBATION"
            allowed = True

    elif role == UserRoles.RESPONSABLE_GGR and action == "refuser":
        if dossier.statut_agent in [
            DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            DossierStatutAgent.EN_ATTENTE_DECISION_DG,
            DossierStatutAgent.TRANSMIS_ANALYSTE,
            DossierStatutAgent.EN_COURS_ANALYSE,
        ]:
            vers_statut = DossierStatutAgent.REFUSE
            nouveau_statut_client = DossierStatutClient.REFUSE
            action_log = "REFUS"
            allowed = True

    elif role == UserRoles.BOE and action == "liberer_fonds":
        if dossier.statut_agent == DossierStatutAgent.APPROUVE_ATTENTE_FONDS:
            vers_statut = DossierStatutAgent.FONDS_LIBERE
            nouveau_statut_client = DossierStatutClient.TERMINE
            action_log = "LIBERATION_FONDS"
            allowed = True

    return allowed, vers_statut, nouveau_statut_client, action_log


def _send_transition_notifications(request, dossier, action, commentaire_retour):
    """Envoie les notifications internes et emails apres une transition."""
    try:
        # Notification pour le client
        if action == "retour_client":
            titre = f"Dossier {dossier.reference} - Complements requis"
            message_notif = (
                f"Votre dossier necessite des complements. Motif: {commentaire_retour}"
            )
        else:
            titre = f"Dossier {dossier.reference} - Mise a jour"
            message_notif = (
                f"Statut cote client: {dossier.get_statut_client_display()}"
            )

        Notification.objects.create(
            utilisateur_cible=dossier.client,
            type="NOUVEAU_MESSAGE",
            titre=titre,
            message=message_notif,
            canal="INTERNE",
        )

        # Notifier le role cible selon l'action
        role_cible_map = {
            "transmettre_analyste": UserRoles.ANALYSTE,
            "transmettre_ggr": UserRoles.RESPONSABLE_GGR,
            "approuver": UserRoles.BOE,
            "retour_gestionnaire": UserRoles.GESTIONNAIRE,
        }

        role_cible = role_cible_map.get(action)
        if role_cible:
            utilisateurs = User.objects.filter(profile__role=role_cible, is_active=True)
            expediteur = request.user.get_full_name() or request.user.username
            client_name = dossier.client.get_full_name() or dossier.client.username

            for user in utilisateurs:
                Notification.objects.create(
                    utilisateur_cible=user,
                    type="NOUVEAU_MESSAGE",
                    titre=f"Dossier {action.replace('_', ' ')} - {dossier.reference}",
                    message=(
                        f"Reference: {dossier.reference}\n"
                        f"Client: {client_name}\n"
                        f"Montant: {dossier.montant} FCFA\n"
                        f"Par: {expediteur}"
                    ),
                    canal="INTERNE",
                )

                # Email
                if user.email:
                    try:
                        send_mail(
                            subject=f"[Credit du Congo] Dossier {dossier.reference}",
                            message=(
                                f"Reference: {dossier.reference}\n"
                                f"Client: {client_name}\n"
                                f"Montant: {dossier.montant} FCFA\n"
                                f"Par: {expediteur}"
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=True,
                        )
                    except Exception:
                        logger.exception(f"Erreur envoi email a {user.username}")

        # Email au client
        if dossier.client.email:
            _send_client_email(request, dossier, action, commentaire_retour)

    except Exception:
        logger.exception("Erreur lors de l'envoi des notifications de transition")


def _send_client_email(request, dossier, action, commentaire_retour):
    """Envoie un email au client apres une transition."""
    if action == "retour_client":
        subject = f"[Credit du Congo] Dossier {dossier.reference} - Complements requis"
        text_message = (
            f"Bonjour,\n\n"
            f"Votre dossier de credit {dossier.reference} necessite des complements.\n\n"
            f"Motif du retour:\n{commentaire_retour}\n\n"
            f"Veuillez vous rapprocher de votre gestionnaire pour completer votre dossier.\n\n"
            f"Cordialement,\nL'equipe Credit du Congo"
        )
        html_message = None
        try:
            html_message = render_to_string(
                "emails/retour_client.html",
                {
                    "dossier": dossier,
                    "commentaire_retour": commentaire_retour,
                    "logo_url": request.build_absolute_uri(
                        static("suivi_demande/img/Credit_Du_Congo.png")
                    ),
                    "site_url": request.build_absolute_uri("/"),
                },
            )
        except Exception:
            logger.warning("Template email retour_client.html non disponible")
    else:
        subject = f"[Credit du Congo] Dossier {dossier.reference} mis a jour"
        text_message = (
            f"Bonjour,\n\nVotre dossier {dossier.reference} a ete mis a jour. "
            f"Nouveau statut: {dossier.get_statut_client_display()}.\n\n"
            f"Ceci est un message automatique."
        )
        html_message = None

    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[dossier.client.email],
            fail_silently=True,
            html_message=html_message,
        )
    except Exception:
        logger.exception(f"Erreur envoi email au client {dossier.client.email}")

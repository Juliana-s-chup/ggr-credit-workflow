"""
Vues de gestion du workflow et des transitions de statut.
"""

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
    UserRoles,
    JournalAction,
    Notification,
)
from ..utils import get_current_namespace
from ..logging_config import log_transition, log_error

User = get_user_model()


@login_required
@transition_allowed
def transition_dossier(request, pk, action: str):
    """
    Effectue une transition d'état sur un dossier en fonction du rôle et de l'action.

    Actions possibles :
    - GESTIONNAIRE : transmettre_analyste, retour_client
    - ANALYSTE : transmettre_ggr, retour_gestionnaire
    - RESPONSABLE_GGR : approuver, refuser
    - BOE : liberer_fonds
    """
    if request.method != "POST":
        messages.error(request, "Méthode non autorisée.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    dossier = get_object_or_404(DossierCredit, pk=pk)
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", None)

    # Récupérer le commentaire de retour s'il existe
    commentaire_retour = request.POST.get("commentaire_retour", "").strip()

    allowed = False
    de_statut = dossier.statut_agent
    vers_statut = None
    nouveau_statut_client = None
    action_log = None

    try:
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
                    return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)
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
                action_log = "RETOUR"
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
                nouveau_statut_client = DossierStatutClient.SE_RAPPROCHER_GEST
                action_log = "REFUS"
                allowed = True

        elif role == UserRoles.BOE and action == "liberer_fonds":
            if dossier.statut_agent == DossierStatutAgent.APPROUVE_ATTENTE_FONDS:
                vers_statut = DossierStatutAgent.FONDS_LIBERE
                nouveau_statut_client = DossierStatutClient.TERMINE
                action_log = "LIBERATION_FONDS"
                allowed = True
    except Exception as e:
        log_error("transition_dossier", e, request.user)
        allowed = False

    if not allowed:
        messages.error(request, "Action non autorisée pour votre rôle ou l'état actuel du dossier.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    # Effectuer la transition
    ancien_statut_client = dossier.statut_client
    dossier.statut_agent = vers_statut
    if nouveau_statut_client:
        dossier.statut_client = nouveau_statut_client
    dossier.acteur_courant = request.user
    dossier.save()

    # Logger la transition
    log_transition(dossier, action, request.user, de_statut, vers_statut)

    # Préparer le commentaire système
    commentaire_systeme = f"Action: {action}"
    if action == "retour_client" and commentaire_retour:
        commentaire_systeme += f" - Motif: {commentaire_retour}"

    # Créer l'entrée dans le journal
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

    # Notifications et emails
    try:
        _handle_notifications(request, dossier, action, commentaire_retour)
    except Exception as e:
        log_error("notifications_transition", e, request.user)
        messages.warning(
            request, "Transition effectuée mais erreur lors de l'envoi des notifications."
        )

    # Message de succès
    if action == "retour_client":
        messages.success(
            request,
            f"Le dossier {dossier.reference} a été retourné au client avec vos commentaires.",
        )
    else:
        messages.success(request, "Transition effectuée avec succès.")

    namespace = get_current_namespace(request)
    return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)


def _handle_notifications(request, dossier, action, commentaire_retour):
    """Gère les notifications et emails après une transition."""
    # Notification pour le client
    if action == "retour_client":
        message_notification = (
            f"🔔 Nouveau message • Dossier {dossier.reference}\n"
            f"Votre dossier nécessite des compléments. Motif: {commentaire_retour}"
        )
        titre_notification = f"🔔 Dossier {dossier.reference} • Compléments requis"
    else:
        message_notification = (
            f"🔔 Mise à jour • Dossier {dossier.reference}\n"
            f"Statut côté client: {dossier.get_statut_client_display()}"
        )
        titre_notification = f"🔔 Dossier {dossier.reference} • Mise à jour"

    # Créer la notification pour le client
    Notification.objects.create(
        utilisateur_cible=dossier.client,
        type="NOUVEAU_MESSAGE",
        titre=titre_notification,
        message=message_notification,
        canal="INTERNE",
    )

    # Notifier les groupes selon l'action
    if action == "transmettre_analyste":
        _notifier_groupe(
            request,
            dossier,
            UserRoles.ANALYSTE,
            f"🔔 Nouveau dossier à analyser • {dossier.reference}",
            "🔔 Nouveau message\nRéférence: {dossier_ref}\nClient: {client_name}\nMontant: {montant} FCFA\nProduit: {produit}\nTransmis par: {expediteur}",
        )

    elif action == "transmettre_ggr":
        _notifier_groupe(
            request,
            dossier,
            UserRoles.RESPONSABLE_GGR,
            f"🔔 Dossier à valider • {dossier.reference}",
            "🔔 Nouveau message\nRéférence: {dossier_ref}\nClient: {client_name}\nMontant: {montant} FCFA\nProduit: {produit}\nTransmis par: {expediteur}",
        )

    elif action == "approuver":
        _notifier_groupe(
            request,
            dossier,
            UserRoles.BOE,
            f"🔔 Dossier approuvé • {dossier.reference}",
            "🔔 Nouveau message\nRéférence: {dossier_ref}\nClient: {client_name}\nMontant: {montant} FCFA\nProduit: {produit}\nApprouvé par: {expediteur}",
        )

    elif action == "retour_gestionnaire":
        _notifier_groupe(
            request,
            dossier,
            UserRoles.GESTIONNAIRE,
            f"🔔 Dossier retourné • {dossier.reference}",
            "🔔 Nouveau message\nRéférence: {dossier_ref}\nClient: {client_name}\nMontant: {montant} FCFA\nRetourné par: {expediteur}",
        )

    # Email au client
    if dossier.client.email:
        _send_email_to_client(request, dossier, action, commentaire_retour)


def _notifier_groupe(request, dossier, role_cible, titre, message_template):
    """Notifie tous les utilisateurs d'un rôle donné."""
    utilisateurs = User.objects.filter(profile__role=role_cible, is_active=True)

    count = 0
    for user in utilisateurs:
        Notification.objects.create(
            utilisateur_cible=user,
            type="NOUVEAU_MESSAGE",
            titre=titre,
            message=message_template.format(
                user_name=user.get_full_name() or user.username,
                dossier_ref=dossier.reference,
                client_name=dossier.client.get_full_name() or dossier.client.username,
                montant=dossier.montant,
                produit=dossier.produit,
                expediteur=request.user.get_full_name() or request.user.username,
            ),
            canal="INTERNE",
        )

        # Email
        if user.email:
            try:
                send_mail(
                    subject=f"[Crédit du Congo] {titre}",
                    message=message_template.format(
                        user_name=user.get_full_name() or user.username,
                        dossier_ref=dossier.reference,
                        client_name=dossier.client.get_full_name() or dossier.client.username,
                        montant=dossier.montant,
                        produit=dossier.produit,
                        expediteur=request.user.get_full_name() or request.user.username,
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                count += 1
            except Exception:
                pass

    if count > 0:
        messages.success(request, f"✓ {count} utilisateur(s) notifié(s).")


def _send_email_to_client(request, dossier, action, commentaire_retour):
    """Envoie un email au client."""
    if action == "retour_client":
        subject = f"[Crédit du Congo] Dossier {dossier.reference} - Compléments requis"
        text_message = (
            f"Bonjour,\n\n"
            f"Votre dossier de crédit {dossier.reference} nécessite des compléments.\n\n"
            f"Motif du retour:\n{commentaire_retour}\n\n"
            f"Veuillez vous rapprocher de votre gestionnaire pour compléter votre dossier.\n\n"
            f"Cordialement,\nL'équipe Crédit du Congo"
        )
    else:
        subject = f"[Crédit du Congo] Dossier {dossier.reference} mis à jour"
        text_message = (
            f"Bonjour,\n\nVotre dossier {dossier.reference} a été mis à jour. "
            f"Nouveau statut côté client: {dossier.get_statut_client_display()}.\n\nCeci est un message automatique."
        )

    # Template HTML pour retour client
    html_message = None
    if action == "retour_client":
        try:
            logo_url = request.build_absolute_uri(static("suivi_demande/img/Credit_Du_Congo.png"))
            site_url = request.build_absolute_uri("/")

            html_message = render_to_string(
                "emails/retour_client.html",
                {
                    "dossier": dossier,
                    "commentaire_retour": commentaire_retour,
                    "logo_url": logo_url,
                    "site_url": site_url,
                },
            )
        except Exception:
            html_message = None

    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[dossier.client.email],
            fail_silently=False,
            html_message=html_message,
        )
    except Exception as e:
        log_error("email_client", e, request.user)


@login_required
def transmettre_analyste_page(request, pk: int):
    """Page de transmission d'un dossier à l'analyste."""
    dossier = get_object_or_404(DossierCredit, pk=pk)
    ctx = {
        "dossier": dossier,
    }
    return render(request, "suivi_demande/transmettre_analyste.html", ctx)

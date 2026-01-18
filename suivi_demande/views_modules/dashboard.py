"""
Vues des dashboards par role et detail des dossiers.
"""

import statistics

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings

from ..models import (
    DossierCredit,
    DossierStatutAgent,
    UserRoles,
    UserProfile,
    JournalAction,
    Notification,
    PieceJointe,
    Commentaire,
)
from ..permissions import can_upload_piece, get_transition_flags
from ..utils import get_current_namespace


@login_required
def dashboard(request):
    """
    Dashboard principal adapte au role de l'utilisateur.

    Affiche des vues differentes selon le role :
    - CLIENT : Ses dossiers
    - GESTIONNAIRE : Dossiers e  traiter
    - ANALYSTE : Dossiers e  analyser
    - RESPONSABLE_GGR : Dossiers en validation
    - BOE : Dossiers approuves
    - SUPER_ADMIN : Gestion utilisateurs
    """
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)

    # Si pas de profil, creer un profil CLIENT par defaut
    if profile is None:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "full_name": request.user.get_full_name() or request.user.username,
                "phone": "",
                "address": "",
                "role": UserRoles.CLIENT,
            },
        )
        role = profile.role

    # Debug info
    debug_info = {
        "user": request.user.username,
        "profile_exists": profile is not None,
        "role": role,
        "template_to_use": None,
    }

    if role == UserRoles.CLIENT:
        return _dashboard_client(request, debug_info)
    elif role == UserRoles.GESTIONNAIRE:
        return _dashboard_gestionnaire(request, debug_info)
    elif role == UserRoles.ANALYSTE:
        return _dashboard_analyste(request, debug_info)
    elif role == UserRoles.RESPONSABLE_GGR:
        return _dashboard_responsable_ggr(request, debug_info)
    elif role == UserRoles.BOE:
        return _dashboard_boe(request, debug_info)
    else:
        return _dashboard_super_admin(request, debug_info)


def _dashboard_client(request, debug_info):
    """Dashboard pour les clients."""
    debug_info["template_to_use"] = "dashboard_client.html"

    # Dossiers en cours (non termines)
    dossiers_en_cours = (
        DossierCredit.objects.filter(client=request.user)
        .exclude(statut_agent__in=[DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE])
        .select_related("acteur_courant")
        .order_by("-date_soumission")
    )

    # Dossiers traites (termines)
    dossiers_traites = (
        DossierCredit.objects.filter(
            client=request.user,
            statut_agent__in=[DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE],
        )
        .select_related("acteur_courant")
        .order_by("-date_maj")[:20]
    )

    # Tous les dossiers (pour compatibilite)
    dossiers = (
        DossierCredit.objects.filter(client=request.user)
        .select_related("acteur_courant")
        .order_by("-date_soumission")
    )

    dossiers_approuves = dossiers.filter(
        statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS
    ).count()
    montant_total = dossiers.aggregate(total=Sum("montant"))["total"] or 0

    # Historique des actions sur les dossiers du client
    historique_actions = (
        JournalAction.objects.filter(dossier__client=request.user)
        .select_related("dossier", "acteur")
        .order_by("-timestamp")[:20]
    )

    context = {
        "mes_dossiers": dossiers,
        "dossiers": dossiers_en_cours,
        "dossiers_en_cours": dossiers_en_cours,
        "dossiers_traites": dossiers_traites,
        "historique_actions": historique_actions,
        "dossiers_approuves": dossiers_approuves,
        "montant_total": montant_total,
        "historique_dossiers": dossiers_traites,
        "debug_info": debug_info,
    }
    return render(request, "suivi_demande/dashboard_client.html", context)


def _dashboard_gestionnaire(request, debug_info):
    """Dashboard pour les gestionnaires."""
    # Dossiers en attente
    dossiers_pending = (
        DossierCredit.objects.filter(
            statut_agent__in=[DossierStatutAgent.NOUVEAU, DossierStatutAgent.TRANSMIS_RESP_GEST]
        )
        .select_related("client", "acteur_courant")
        .order_by("-date_soumission")
    )

    # Dossiers recents
    recents = (
        DossierCredit.objects.select_related("client", "acteur_courant")
        .all()
        .order_by("-date_soumission")[:10]
    )

    # KPI
    today = timezone.now().date()

    nouveaux_qs = DossierCredit.objects.filter(statut_agent=DossierStatutAgent.NOUVEAU)
    nouveaux_total = nouveaux_qs.count()
    nouveaux_today = nouveaux_qs.filter(date_soumission__date=today).count()

    complets_qs = DossierCredit.objects.filter(
        statut_agent__in=[DossierStatutAgent.TRANSMIS_ANALYSTE, DossierStatutAgent.EN_COURS_ANALYSE]
    )
    complets_total = complets_qs.count()
    complets_today = complets_qs.filter(date_soumission__date=today).count()

    retournes_qs = DossierCredit.objects.filter(statut_agent=DossierStatutAgent.TRANSMIS_RESP_GEST)
    retournes_total = retournes_qs.count()
    retournes_today = retournes_qs.filter(date_soumission__date=today).count()

    en_attente_qs = DossierCredit.objects.filter(
        statut_agent__in=[
            DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            DossierStatutAgent.EN_ATTENTE_DECISION_DG,
        ]
    )
    en_attente_total = en_attente_qs.count()
    en_attente_today = en_attente_qs.filter(date_soumission__date=today).count()

    # Calcul delai moyen
    try:
        delais = []
        now = timezone.now()
        for d in DossierCredit.objects.order_by("-date_soumission")[:20]:
            if d.date_soumission:
                delta = now - d.date_soumission
                delais.append(delta.total_seconds() / 86400.0)
        delai_moyen_jours = round(statistics.mean(delais), 1) if delais else "'”"
        variation_semaine = 0
    except Exception:
        delai_moyen_jours = "'”"
        variation_semaine = 0

    kpi = {
        "nouveaux_total": nouveaux_total,
        "nouveaux_today": nouveaux_today,
        "complets_total": complets_total,
        "complets_today": complets_today,
        "retournes_total": retournes_total,
        "retournes_today": retournes_today,
        "en_attente_total": en_attente_total,
        "en_attente_today": en_attente_today,
        "delai_moyen_jours": delai_moyen_jours,
        "variation_semaine": variation_semaine,
    }

    # Dossiers en cours
    dossiers_en_cours = (
        DossierCredit.objects.exclude(
            statut_agent__in=[
                DossierStatutAgent.FONDS_LIBERE,
                DossierStatutAgent.REFUSE,
            ]
        )
        .select_related("client", "acteur_courant")
        .order_by("-date_soumission")
    )

    # Dossiers traites
    dossiers_traites = (
        DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.FONDS_LIBERE,
                DossierStatutAgent.REFUSE,
            ]
        )
        .select_related("client")
        .order_by("-date_maj")[:20]
    )

    # Historique
    historique_actions = JournalAction.objects.select_related("dossier", "acteur").order_by(
        "-timestamp"
    )[:20]

    # Statistiques supplementaires
    total_dossiers = DossierCredit.objects.count()
    today_date = timezone.now().date()
    dossiers_ce_mois = DossierCredit.objects.filter(
        date_soumission__year=today_date.year,
        date_soumission__month=today_date.month,
    ).count()

    approuves = DossierCredit.objects.filter(
        statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS
    ).count()
    refuses = DossierCredit.objects.filter(statut_agent=DossierStatutAgent.REFUSE).count()
    total_decides = approuves + refuses
    taux_validation = round((approuves / total_decides) * 100, 1) if total_decides else 0

    portefeuille_total = DossierCredit.objects.aggregate(total=Sum("montant"))["total"] or 0

    dossiers_urgents = list(dossiers_pending[:5])
    mes_clients = []

    mes_dossiers_crees = (
        DossierCredit.objects.filter(acteur_courant=request.user)
        .select_related("client")
        .order_by("-date_soumission")[:20]
    )

    debug_info["template_to_use"] = "dashboard_gestionnaire.html"
    debug_info["total_dossiers_base"] = total_dossiers
    debug_info["dossiers_affiches"] = dossiers_en_cours.count()

    # Messages d'information
    if total_dossiers == 0:
        messages.warning(request, "ðŸ” Aucun dossier n'existe en base de donnees.")
    elif dossiers_en_cours.count() == 0:
        messages.info(request, f"ðŸ” {total_dossiers} dossier(s) en base, mais aucun actif.")
    else:
        messages.success(request, f"âœ“ {dossiers_en_cours.count()} dossier(s) en cours.")

    ctx = {
        "dossiers_pending": dossiers_pending,
        "recents": recents,
        "kpi": kpi,
        "dossiers": dossiers_en_cours,
        "dossiers_en_cours": dossiers_en_cours,
        "dossiers_traites": dossiers_traites,
        "historique_actions": historique_actions,
        "dossiers_urgents": dossiers_urgents,
        "dossiers_ce_mois": dossiers_ce_mois,
        "taux_validation": taux_validation,
        "portefeuille_total": portefeuille_total,
        "mes_clients": mes_clients,
        "mes_dossiers_crees": mes_dossiers_crees,
        "debug_info": debug_info,
    }
    return render(request, "suivi_demande/dashboard_gestionnaire.html", ctx)


def _dashboard_analyste(request, debug_info):
    """Dashboard pour les analystes."""
    dossiers = (
        DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.TRANSMIS_ANALYSTE,
                DossierStatutAgent.EN_COURS_ANALYSE,
            ]
        )
        .select_related("client", "acteur_courant")
        .order_by("-date_soumission")
    )

    dossiers_en_attente = dossiers.filter(statut_agent=DossierStatutAgent.TRANSMIS_ANALYSTE)
    dossiers_a_analyser = dossiers
    dossiers_prioritaires = dossiers[:5]

    total_dossiers = dossiers.count()
    dossiers_ce_mois = dossiers.filter(
        date_soumission__year=timezone.now().year, date_soumission__month=timezone.now().month
    ).count()

    dossiers_traites = (
        DossierCredit.objects.filter(
            statut_agent__in=[DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        )
        .select_related("client")
        .order_by("-date_maj")[:20]
    )

    historique_actions = JournalAction.objects.select_related("dossier", "acteur").order_by(
        "-timestamp"
    )[:20]

    context = {
        "dossiers": dossiers,
        "dossiers_en_attente": dossiers_en_attente,
        "dossiers_a_analyser": dossiers_a_analyser,
        "dossiers_prioritaires": dossiers_prioritaires,
        "dossiers_traites": dossiers_traites,
        "historique_actions": historique_actions,
        "total_dossiers": total_dossiers,
        "dossiers_ce_mois": dossiers_ce_mois,
    }
    return render(request, "suivi_demande/dashboard_analyste.html", context)


def _dashboard_responsable_ggr(request, debug_info):
    """Dashboard pour le responsable GGR."""
    dossiers = (
        DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.EN_COURS_VALIDATION_GGR,
                DossierStatutAgent.EN_ATTENTE_DECISION_DG,
            ]
        )
        .select_related("client", "acteur_courant")
        .order_by("-date_soumission")
    )

    dossiers_traites = (
        DossierCredit.objects.filter(
            statut_agent__in=[DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        )
        .select_related("client")
        .order_by("-date_maj")[:20]
    )

    historique_actions = JournalAction.objects.select_related("dossier", "acteur").order_by(
        "-timestamp"
    )[:20]

    return render(
        request,
        "suivi_demande/dashboard_responsable_ggr_pro.html",
        {
            "dossiers": dossiers,
            "dossiers_traites": dossiers_traites,
            "historique_actions": historique_actions,
        },
    )


def _dashboard_boe(request, debug_info):
    """Dashboard pour le BOE (Back Office Engagement)."""
    dossiers = (
        DossierCredit.objects.filter(statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS)
        .select_related("client", "acteur_courant")
        .order_by("-date_soumission")
    )

    today = timezone.now().date()
    fonds_liberes_today = DossierCredit.objects.filter(
        statut_agent=DossierStatutAgent.FONDS_LIBERE, date_maj__date=today
    ).count()

    dossiers_traites = (
        DossierCredit.objects.filter(
            statut_agent__in=[DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        )
        .select_related("client")
        .order_by("-date_maj")[:20]
    )

    historique_actions = JournalAction.objects.select_related("dossier", "acteur").order_by(
        "-timestamp"
    )[:20]

    context = {
        "dossiers": dossiers,
        "dossiers_traites": dossiers_traites,
        "historique_actions": historique_actions,
        "fonds_liberes_today": fonds_liberes_today,
        "total_dossiers": dossiers.count(),
    }
    return render(request, "suivi_demande/dashboard_boe.html", context)


def _dashboard_super_admin(request, debug_info):
    """Dashboard pour le super administrateur."""
    from django.contrib.auth import get_user_model
    from django.contrib.admin.models import LogEntry

    User = get_user_model()

    all_users = User.objects.select_related("profile").all().order_by("-date_joined")

    stats_total_users = all_users.count()
    stats_users_active = all_users.filter(is_active=True).count()
    stats_users_inactive = all_users.filter(is_active=False).count()

    stats_roles = {}
    for role_value, role_label in UserRoles.choices:
        count = UserProfile.objects.filter(role=role_value).count()
        stats_roles[role_label] = count

    historique_utilisateurs = (
        LogEntry.objects.select_related("user", "content_type")
        .filter(content_type__model__in=["user", "userprofile"])
        .order_by("-action_time")[:50]
    )

    users_recent = all_users[:10]

    context = {
        "all_users": all_users,
        "users_recent": users_recent,
        "stats_total_users": stats_total_users,
        "stats_users_active": stats_users_active,
        "stats_users_inactive": stats_users_inactive,
        "stats_roles": stats_roles,
        "historique_utilisateurs": historique_utilisateurs,
    }
    return render(request, "suivi_demande/dashboard_super_admin.html", context)


@login_required
def dossier_detail(request, pk):
    """
    Affiche le detail complet d'un dossier.

    Gere :
    - Affichage des informations du dossier
    - Ajout de commentaires
    - Upload de pieces jointes
    - Permissions selon le role
    """
    dossier = get_object_or_404(
        DossierCredit.objects.select_related("client", "acteur_courant"), pk=pk
    )
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)

    # Controle d'acces : le client ne peut voir que ses propres dossiers
    if role == UserRoles.CLIENT and dossier.client_id != request.user.id:
        messages.error(request, "Acces refuse au dossier demande.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    # Marquer les notifications liees au dossier comme lues
    try:
        Notification.objects.filter(
            utilisateur_cible=request.user,
            lu=False,
        ).filter(
            Q(titre__icontains=dossier.reference) | Q(message__icontains=dossier.reference)
        ).update(lu=True)
    except Exception:
        pass

    # Permissions
    can_upload = can_upload_piece(dossier, request.user)
    _flags = get_transition_flags(dossier, request.user)
    can_tx_transmettre_analyste = _flags["can_tx_transmettre_analyste"]
    can_tx_transmettre_ggr = _flags["can_tx_transmettre_ggr"]
    can_tx_retour_gestionnaire = _flags["can_tx_retour_gestionnaire"]
    can_tx_approuver = _flags["can_tx_approuver"]
    can_tx_refuser = _flags["can_tx_refuser"]
    can_tx_liberer_fonds = _flags["can_tx_liberer_fonds"]

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()

        if action == "add_comment":
            msg = (request.POST.get("message") or "").strip()
            if msg:
                Commentaire.objects.create(
                    dossier=dossier,
                    auteur=request.user,
                    message=msg,
                    cible_role=None,
                )
                messages.success(request, "Commentaire ajoute.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

        elif action == "upload_piece":
            if not can_upload:
                messages.error(request, "Vous ne pouvez pas deposer de piece e  ce stade.")
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

            f = request.FILES.get("fichier")
            type_piece = request.POST.get("type_piece") or "AUTRE"
            if not f:
                messages.error(request, "Aucun fichier selectionne.")
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

            # Validation taille
            file_size = getattr(f, "size", 0) or 0
            max_size = getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024)
            if file_size > max_size:
                max_mb = round(max_size / (1024 * 1024), 2)
                messages.error(request, f"Fichier trop volumineux. Taille max: {max_mb} Mo.")
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

            # Validation extension
            filename = getattr(f, "name", "")
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            allowed_exts = getattr(settings, "UPLOAD_ALLOWED_EXTS", {"pdf", "jpg", "jpeg", "png"})
            if ext not in allowed_exts:
                messages.error(
                    request,
                    f"Extension non autorisee ({ext}). Autorisees: {', '.join(sorted(allowed_exts))}.",
                )
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

            # Creer la piece jointe
            pj = PieceJointe.objects.create(
                dossier=dossier,
                fichier=f,
                type_piece=type_piece,
                taille=file_size,
                upload_by=request.user,
            )
            messages.success(request, "Piece jointe telechargee.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

    # Recuperer les donnees
    pieces = (
        PieceJointe.objects.filter(dossier=dossier)
        .select_related("upload_by")
        .order_by("-upload_at")
    )
    commentaires = (
        Commentaire.objects.filter(dossier=dossier).select_related("auteur").order_by("-created_at")
    )
    journal = (
        JournalAction.objects.filter(dossier=dossier)
        .select_related("acteur")
        .order_by("-timestamp")
    )

    ctx = {
        "dossier": dossier,
        "pieces": pieces,
        "commentaires": commentaires,
        "journal": journal,
        "role": role,
        "can_upload": can_upload,
        "can_tx_transmettre_analyste": can_tx_transmettre_analyste,
        "can_tx_transmettre_ggr": can_tx_transmettre_ggr,
        "can_tx_retour_gestionnaire": can_tx_retour_gestionnaire,
        "can_tx_approuver": can_tx_approuver,
        "can_tx_refuser": can_tx_refuser,
        "can_tx_liberer_fonds": can_tx_liberer_fonds,
    }
    return render(request, "suivi_demande/dossier_detail.html", ctx)

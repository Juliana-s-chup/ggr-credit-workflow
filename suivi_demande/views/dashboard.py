"""
Vue du dashboard principal, adapte au role de l'utilisateur.

Chaque role (CLIENT, GESTIONNAIRE, ANALYSTE, RESPONSABLE_GGR, BOE, SUPER_ADMIN)
dispose d'un dashboard personnalise avec ses KPI et dossiers pertinents.
"""

import logging
import statistics

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from ..models import (
    DossierCredit,
    DossierStatutAgent,
    UserRoles,
    UserProfile,
    JournalAction,
)
from ..services.dossier_service import DossierService
from ..utils import get_user_role

User = get_user_model()
logger = logging.getLogger("suivi_demande")


@login_required
def dashboard(request):
    """
    Dashboard principal avec optimisations Service Layer.
    Route vers le template adapte au role de l'utilisateur.
    """
    role = get_user_role(request.user)

    # Si pas de profil, creer un profil CLIENT par defaut
    if role is None:
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

    if role == UserRoles.CLIENT:
        return _dashboard_client(request)
    elif role == UserRoles.GESTIONNAIRE:
        return _dashboard_gestionnaire(request)
    elif role == UserRoles.ANALYSTE:
        return _dashboard_analyste(request)
    elif role == UserRoles.RESPONSABLE_GGR:
        return _dashboard_responsable_ggr(request)
    elif role == UserRoles.BOE:
        return _dashboard_boe(request)
    else:
        return _dashboard_super_admin(request)


# ---------------------------------------------------------------------------
# Dashboards par role (fonctions privees)
# ---------------------------------------------------------------------------


def _dashboard_client(request):
    """Dashboard pour le role CLIENT."""
    page = DossierService.get_dossiers_for_user(
        user=request.user,
        page=request.GET.get("page", 1),
        per_page=50,
    )

    all_dossiers = list(page.object_list)
    dossiers_en_cours = [
        d for d in all_dossiers
        if d.statut_agent not in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
    ]
    dossiers_traites = [
        d for d in all_dossiers
        if d.statut_agent in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
    ][:20]

    stats = DossierService.get_statistics_for_role(request.user)

    historique_actions = (
        JournalAction.objects.filter(dossier__client=request.user)
        .select_related("dossier", "acteur")
        .order_by("-timestamp")[:20]
    )

    context = {
        "mes_dossiers": all_dossiers,
        "dossiers": dossiers_en_cours,
        "dossiers_en_cours": dossiers_en_cours,
        "dossiers_traites": dossiers_traites,
        "historique_actions": historique_actions,
        "dossiers_approuves": stats["approuves"],
        "montant_total": stats["montant_total"],
        "historique_dossiers": dossiers_traites,
        "page": page,
    }
    return render(request, "suivi_demande/dashboard_client.html", context)


def _dashboard_gestionnaire(request):
    """Dashboard pour le role GESTIONNAIRE."""
    page = DossierService.get_dossiers_for_user(
        user=request.user, page=request.GET.get("page", 1), per_page=50
    )
    stats = DossierService.get_statistics_for_role(request.user)

    all_dossiers = list(page.object_list)
    dossiers_en_cours = [
        d for d in all_dossiers
        if d.statut_agent not in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
    ]
    dossiers_traites = [
        d for d in all_dossiers
        if d.statut_agent in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
    ][:20]

    dossiers_pending = [
        d for d in dossiers_en_cours
        if d.statut_agent in [DossierStatutAgent.NOUVEAU, DossierStatutAgent.TRANSMIS_RESP_GEST]
    ]

    recents = all_dossiers[:10]

    nouveaux_total = sum(
        1 for d in all_dossiers if d.statut_agent == DossierStatutAgent.NOUVEAU
    )
    complets_total = sum(
        1 for d in all_dossiers
        if d.statut_agent in [DossierStatutAgent.TRANSMIS_ANALYSTE, DossierStatutAgent.EN_COURS_ANALYSE]
    )
    retournes_total = sum(
        1 for d in all_dossiers
        if d.statut_agent == DossierStatutAgent.TRANSMIS_RESP_GEST
    )

    kpi = {
        "nouveaux_total": nouveaux_total,
        "nouveaux_today": 0,
        "complets_total": complets_total,
        "complets_today": 0,
        "retournes_total": retournes_total,
        "retournes_today": 0,
        "en_attente_total": stats["en_cours"],
        "en_attente_today": 0,
        "delai_moyen_jours": "-",
        "variation_semaine": 0,
    }

    historique_actions = JournalAction.objects.select_related(
        "dossier", "acteur"
    ).order_by("-timestamp")[:20]

    total_decides = stats["approuves"] + stats["refuses"]
    taux_validation = (
        round((stats["approuves"] / total_decides) * 100, 1) if total_decides else 0
    )

    ctx = {
        "dossiers_pending": dossiers_pending,
        "recents": recents,
        "kpi": kpi,
        "dossiers": dossiers_en_cours,
        "dossiers_en_cours": dossiers_en_cours,
        "dossiers_traites": dossiers_traites,
        "historique_actions": historique_actions,
        "dossiers_urgents": dossiers_pending[:5],
        "dossiers_ce_mois": stats["total"],
        "taux_validation": taux_validation,
        "portefeuille_total": stats["montant_total"],
        "mes_clients": [],
        "mes_dossiers_crees": recents[:20],
        "page": page,
    }
    return render(request, "suivi_demande/dashboard_gestionnaire.html", ctx)


def _dashboard_analyste(request):
    """Dashboard pour le role ANALYSTE."""
    page = DossierService.get_dossiers_for_user(
        user=request.user, page=request.GET.get("page", 1), per_page=30
    )

    dossiers = list(page.object_list)
    dossiers_en_attente = [
        d for d in dossiers
        if d.statut_agent == DossierStatutAgent.TRANSMIS_ANALYSTE
    ]
    dossiers_prioritaires = dossiers[:5]

    stats = DossierService.get_statistics_for_role(request.user)

    dossiers_traites = DossierCredit.objects.select_related(
        "client", "client__profile", "acteur_courant"
    ).filter(
        statut_agent__in=[
            DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            DossierStatutAgent.EN_ATTENTE_DECISION_DG,
            DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
            DossierStatutAgent.FONDS_LIBERE,
            DossierStatutAgent.REFUSE,
        ]
    ).order_by("-date_soumission")[:20]

    historique_actions = JournalAction.objects.select_related(
        "dossier", "acteur"
    ).order_by("-timestamp")[:20]

    context = {
        "dossiers": dossiers,
        "dossiers_en_attente": dossiers_en_attente,
        "dossiers_a_analyser": dossiers,
        "dossiers_prioritaires": dossiers_prioritaires,
        "dossiers_traites": dossiers_traites,
        "historique_actions": historique_actions,
        "total_dossiers": stats["total"],
        "dossiers_ce_mois": stats["total"],
        "page": page,
    }
    return render(request, "suivi_demande/dashboard_analyste.html", context)


def _dashboard_responsable_ggr(request):
    """Dashboard pour le role RESPONSABLE_GGR."""
    page = DossierService.get_dossiers_for_user(
        user=request.user, page=request.GET.get("page", 1), per_page=30
    )
    dossiers = list(page.object_list)

    dossiers_traites = DossierCredit.objects.select_related(
        "client", "client__profile", "acteur_courant"
    ).filter(
        statut_agent__in=[
            DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
            DossierStatutAgent.FONDS_LIBERE,
            DossierStatutAgent.REFUSE,
        ]
    ).order_by("-date_soumission")[:20]

    historique_actions = JournalAction.objects.select_related(
        "dossier", "acteur"
    ).order_by("-timestamp")[:20]

    return render(
        request,
        "suivi_demande/dashboard_responsable_ggr_pro.html",
        {
            "dossiers": dossiers,
            "dossiers_traites": dossiers_traites,
            "historique_actions": historique_actions,
            "page": page,
        },
    )


def _dashboard_boe(request):
    """Dashboard pour le role BOE."""
    page = DossierService.get_dossiers_for_user(
        user=request.user, page=request.GET.get("page", 1), per_page=30
    )
    dossiers = list(page.object_list)
    stats = DossierService.get_statistics_for_role(request.user)

    dossiers_traites = DossierCredit.objects.select_related(
        "client", "client__profile", "acteur_courant"
    ).filter(
        statut_agent=DossierStatutAgent.FONDS_LIBERE
    ).order_by("-date_soumission")[:20]

    historique_actions = JournalAction.objects.select_related(
        "dossier", "acteur"
    ).order_by("-timestamp")[:20]

    context = {
        "dossiers": dossiers,
        "dossiers_traites": dossiers_traites,
        "historique_actions": historique_actions,
        "fonds_liberes_today": 0,
        "total_dossiers": stats["total"],
        "page": page,
    }
    return render(request, "suivi_demande/dashboard_boe.html", context)


def _dashboard_super_admin(request):
    """Dashboard pour le role SUPER_ADMIN."""
    from django.contrib.admin.models import LogEntry

    all_users = (
        User.objects.select_related("profile").all().order_by("-date_joined")
    )

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

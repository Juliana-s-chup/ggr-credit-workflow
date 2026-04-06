"""
Vues specifiques aux portails Client et Professionnel
"""

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.conf import settings
from django.db import models
from django.views.decorators.http import require_GET
from datetime import datetime

from .models import UserRoles
from core.security import rate_limit


@rate_limit('login_client', limit=5, period=300)  # 5 tentatives par 5 minutes
def login_client_view(request):
    """
    Vue de connexion pour le portail CLIENT
    Restreint uniquement aux utilisateurs avec role CLIENT
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Verifier que l'utilisateur a le role CLIENT
            profile = getattr(user, "profile", None)
            role = getattr(profile, "role", None)

            if role != UserRoles.CLIENT:
                messages.error(
                    request,
                    "Acces refuse. Cet espace est reserve aux clients. "
                    "Les professionnels doivent utiliser le portail pro.ggr-credit.cg",
                )
                return render(request, "portail_client/login.html", {"form": form})

            # Connexion reussie
            auth_login(request, user)
            messages.success(
                request, f"Bienvenue {user.get_full_name() or user.username} !"
            )

            # Redirection vers le dashboard client
            next_url = request.GET.get("next", "/dashboard/")
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(
        request,
        "portail_client/login.html",
        {
            "form": form,
            "portal_type": "client",
        },
    )


@rate_limit('login_pro', limit=5, period=300)  # 5 tentatives par 5 minutes
def login_pro_view(request):
    """
    Vue de connexion pour le portail PROFESSIONNEL
    Restreint aux utilisateurs avec roles professionnels
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Verifier que l'utilisateur a un role professionnel
            profile = getattr(user, "profile", None)
            role = getattr(profile, "role", None)

            allowed_roles = [
                UserRoles.GESTIONNAIRE,
                UserRoles.ANALYSTE,
                UserRoles.RESPONSABLE_GGR,
                UserRoles.BOE,
                UserRoles.SUPER_ADMIN,
            ]

            if role not in allowed_roles:
                messages.error(
                    request,
                    "Acces refuse. Cet espace est reserve aux professionnels. "
                    "Les clients doivent utiliser le portail client.ggr-credit.cg",
                )
                return render(request, "portail_pro/login.html", {"form": form})

            # Connexion reussie
            auth_login(request, user)
            messages.success(
                request, f"Bienvenue {user.get_full_name() or user.username} !"
            )

            # Redirection vers le dashboard pro
            next_url = request.GET.get("next", "/dashboard/")
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(
        request,
        "portail_pro/login.html",
        {
            "form": form,
            "portal_type": "professional",
        },
    )


from django.contrib.auth.decorators import login_required


@login_required
def view_documents(request, dossier_id):
    """
    Vue de consultation des documents pour les clients
    (lecture seule, pas d'upload)
    """
    from django.shortcuts import get_object_or_404
    from .models import DossierCredit

    dossier = get_object_or_404(DossierCredit, pk=dossier_id)

    # Verifier que le client accede e  son propre dossier
    if dossier.client != request.user:
        messages.error(request, "Vous ne pouvez consulter que vos propres dossiers.")
        return redirect("client:my_applications")

    documents = dossier.pieces.all().order_by("-date_upload")

    return render(
        request,
        "portail_client/view_documents.html",
        {
            "dossier": dossier,
            "documents": documents,
        },
    )


@login_required
def all_dossiers_view(request):
    """Vue de tous les dossiers pour les professionnels avec pagination"""
    from .models import DossierCredit, UserRoles
    from django.core.paginator import Paginator
    from .constants import ITEMS_PER_PAGE

    # Determiner le role de l'utilisateur
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", None)

    # Filtrer selon le role
    if role == UserRoles.GESTIONNAIRE:
        dossiers_list = DossierCredit.objects.filter(
            statut_agent__in=["NOUVEAU", "INCOMPLET"]
        )
    elif role == UserRoles.ANALYSTE:
        dossiers_list = DossierCredit.objects.filter(
            statut_agent__in=["TRANSMIS_ANALYSTE", "EN_COURS_ANALYSE"]
        )
    elif role == UserRoles.RESPONSABLE_GGR:
        dossiers_list = DossierCredit.objects.filter(
            statut_agent__in=["EN_COURS_VALIDATION_GGR", "EN_ATTENTE_DECISION_DG"]
        )
    elif role == UserRoles.BOE:
        dossiers_list = DossierCredit.objects.filter(statut_agent="APPROUVE_ATTENTE_FONDS")
    else:  # SUPER_ADMIN
        dossiers_list = DossierCredit.objects.all()

    dossiers_list = dossiers_list.select_related('client', 'acteur_courant').order_by("-date_soumission")

    # Pagination
    paginator = Paginator(dossiers_list, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    dossiers = paginator.get_page(page_number)

    return render(
        request,
        "portail_pro/all_dossiers.html",
        {
            "dossiers": dossiers,
            "user_role": role,
        },
    )


@login_required
@require_GET
def reports_view(request):
    """Vue des rapports pour les professionnels (filtres par utilisateur connecte)"""
    from .models import DossierCredit, UserRoles, JournalAction
    from django.db.models import Count, Sum

    # Determiner le perimetre de l'utilisateur selon son role
    def _scope_queryset_par_role(user):
        profile = getattr(user, "profile", None)
        role = getattr(profile, "role", None)

        if role == UserRoles.CLIENT:
            # Interdit cote portail pro
            return DossierCredit.objects.none()

        if role == UserRoles.GESTIONNAIRE:
            # Gestionnaire: vue globale (pilotage)
            return DossierCredit.objects.all()

        if role == UserRoles.ANALYSTE:
            dossier_ids = (
                JournalAction.objects.filter(acteur=user)
                .values_list("dossier_id", flat=True)
                .distinct()
            )
            return DossierCredit.objects.filter(
                (models.Q(id__in=dossier_ids)) | (models.Q(acteur_courant=user))
            )

        # RESPONSABLE_GGR / BOE / SUPER_ADMIN -> tout le perimetre
        return DossierCredit.objects.all()

    # Controle d'acces: roles autorises (detection robuste du role)
    def get_user_role(user):
        role = getattr(getattr(user, "profile", None), "role", None)
        if not role:
            role = getattr(getattr(user, "userprofile", None), "role", None)
        return role

    user_role = get_user_role(request.user)
    
    # Router chaque rôle vers sa vue de rapports spécifique
    if user_role == UserRoles.SUPER_ADMIN:
        return reports_users_view(request)
    elif user_role == UserRoles.GESTIONNAIRE:
        return reports_gestionnaire_view(request)
    elif user_role == UserRoles.ANALYSTE:
        return reports_analyste_view(request)
    elif user_role == UserRoles.RESPONSABLE_GGR:
        return reports_responsable_ggr_view(request)
    elif user_role == UserRoles.BOE:
        return reports_boe_view(request)
    else:
        messages.error(request, "Acces non autorise e  la page Rapports.")
        return redirect("pro:dashboard")

    qs = _scope_queryset_par_role(request.user)

    # Ajustement de perimetre specifique au role BOE: dossiers pertinents pour la liberation des fonds
    if user_role == UserRoles.BOE:
        qs = qs.filter(statut_agent__in=["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE"])

    # Filtrage periode (date_debut, date_fin) sur la date de soumission du dossier
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    try:
        if date_debut:
            dt_start = datetime.fromisoformat(date_debut)
            qs = qs.filter(date_soumission__gte=dt_start)
        if date_fin:
            # inclure fin de journee
            dt_end = datetime.fromisoformat(date_fin)
            qs = qs.filter(date_soumission__lte=dt_end)
    except Exception:
        # ignore filtre si format invalide
        pass

    # Statistiques dans le perimetre (role-aware)
    if user_role == UserRoles.BOE:
        # Pour BOE, en_cours = en attente de liberation; approuves = fonds liberes
        stats = {
            "total_dossiers": qs.count(),
            "en_cours": qs.filter(statut_agent="APPROUVE_ATTENTE_FONDS").count(),
            "approuves": qs.filter(statut_agent="FONDS_LIBERE").count(),
            "refuses": 0,
            "montant_total": qs.aggregate(total=Sum("montant"))["total"] or 0,
        }
    else:
        stats = {
            "total_dossiers": qs.count(),
            "en_cours": qs.exclude(
                statut_agent__in=["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE", "REFUSE"]
            ).count(),
            "approuves": qs.filter(statut_agent="APPROUVE_ATTENTE_FONDS").count(),
            "refuses": qs.filter(statut_agent="REFUSE").count(),
            "montant_total": qs.aggregate(total=Sum("montant"))["total"] or 0,
        }

    # Par statut dans le perimetre
    par_statut = (
        qs.values("statut_agent").annotate(count=Count("id")).order_by("-count")
    )

    # KPIs additionnels
    finals = ["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE", "REFUSE"]
    processed_count = qs.filter(statut_agent__in=finals).count()
    approved_count = qs.filter(
        statut_agent__in=["APPROUVE_ATTENTE_FONDS", "FONDS_LIBERE"]
    ).count()
    refused_count = qs.filter(statut_agent="REFUSE").count()
    denom = processed_count or 1
    acceptance_rate = round((approved_count / denom) * 100, 2)
    reject_rate = round((refused_count / denom) * 100, 2)

    # Rework: dossiers avec retour
    rework_count = 0
    try:
        rework_count = (
            JournalAction.objects.filter(
                dossier_id__in=qs.values_list("id", flat=True),
                action__in=["RETOUR_CLIENT", "RETOUR_GESTIONNAIRE"],
            )
            .values("dossier_id")
            .distinct()
            .count()
        )
    except Exception:
        rework_count = 0

    # Lead time moyen (jours): soumission -> 1er statut final
    lead_time_sum = 0.0
    lead_time_n = 0
    try:
        dossier_ids = list(qs.values_list("id", "date_soumission"))
        if dossier_ids:
            # map id -> date_soumission
            submit_map = {did: ds for did, ds in dossier_ids}
            finals_qs = (
                JournalAction.objects.filter(
                    dossier_id__in=submit_map.keys(), vers_statut__in=finals
                )
                .order_by("dossier_id", "timestamp")
                .values("dossier_id", "timestamp")
            )
            seen = set()
            for row in finals_qs:
                did = row["dossier_id"]
                if did in seen:
                    continue
                seen.add(did)
                ts_final = row["timestamp"]
                dt_submit = submit_map.get(did)
                if dt_submit and ts_final and ts_final > dt_submit:
                    delta = ts_final - dt_submit
                    lead_time_sum += delta.total_seconds() / 86400.0
                    lead_time_n += 1
    except Exception:
        pass
    lead_time_avg_days = round(lead_time_sum / lead_time_n, 2) if lead_time_n else 0.0

    kpis = {
        "processed_count": processed_count,
        "acceptance_rate": acceptance_rate,
        "reject_rate": reject_rate,
        "rework_count": rework_count,
        "lead_time_avg_days": lead_time_avg_days,
    }

    # Donnees pour graphiques Chart.js
    import json
    from collections import defaultdict
    from django.db.models.functions import TruncMonth

    # 1. e‰volution mensuelle (courbe)
    monthly_data = (
        qs.filter(statut_agent__in=finals)
        .annotate(mois=TruncMonth("date_soumission"))
        .values("mois")
        .annotate(count=Count("id"))
        .order_by("mois")
    )
    chart_monthly = {
        "labels": [
            d["mois"].strftime("%b %Y") if d["mois"] else "" for d in monthly_data
        ],
        "data": [d["count"] for d in monthly_data],
    }

    # 2. Repartition par statut (camembert)
    chart_statuts = {
        "labels": [row["statut_agent"] for row in par_statut],
        "data": [row["count"] for row in par_statut],
    }

    # 3. Lead time par gestionnaire (histogramme) - top 10
    try:
        from django.db.models import Avg

        lead_by_manager = []
        # Recuperer les gestionnaires avec dossiers
        managers_qs = (
            qs.exclude(acteur_courant__isnull=True)
            .values("acteur_courant__username")
            .annotate(nb=Count("id"))
            .filter(nb__gt=0)
            .order_by("-nb")[:10]
        )
        manager_names = [m["acteur_courant__username"] for m in managers_qs]

        # Calculer lead time moyen par gestionnaire (approximation simple)
        for mgr in manager_names:
            mgr_dossiers = qs.filter(
                acteur_courant__username=mgr, statut_agent__in=finals
            )
            if mgr_dossiers.exists():
                # Approximation: utiliser date_maj - date_soumission
                avg_days = 0
                count = 0
                for d in mgr_dossiers:
                    if d.date_maj and d.date_soumission:
                        delta = (d.date_maj - d.date_soumission).total_seconds() / 86400
                        avg_days += delta
                        count += 1
                if count > 0:
                    lead_by_manager.append(
                        {"manager": mgr, "avg_days": round(avg_days / count, 1)}
                    )

        chart_lead_time = {
            "labels": [m["manager"] for m in lead_by_manager],
            "data": [m["avg_days"] for m in lead_by_manager],
        }
    except Exception:
        chart_lead_time = {"labels": [], "data": []}

    charts_data = {
        "monthly": chart_monthly,
        "statuts": chart_statuts,
        "lead_time": chart_lead_time,
    }

    return render(
        request,
        "portail_pro/reports.html",
        {
            "stats": stats,
            "par_statut": par_statut,
            "kpis": kpis,
            "charts_json": json.dumps(charts_data),
        },
    )


@login_required
def rapports_export_csv(request):
    """Export CSV des dossiers selon le perimetre et les filtres de periode."""
    from .models import DossierCredit, UserRoles, JournalAction
    import csv
    from django.http import HttpResponse

    # meme perimetre que reports_view
    def _scope_queryset_par_role(user):
        profile = getattr(user, "profile", None)
        role = getattr(profile, "role", None)
        if role == UserRoles.CLIENT:
            return DossierCredit.objects.none()
        if role == UserRoles.GESTIONNAIRE:
            return DossierCredit.objects.all()
        if role == UserRoles.ANALYSTE:
            dossier_ids = (
                JournalAction.objects.filter(acteur=user)
                .values_list("dossier_id", flat=True)
                .distinct()
            )
            return DossierCredit.objects.filter(
                (models.Q(id__in=dossier_ids)) | (models.Q(acteur_courant=user))
            )
        return DossierCredit.objects.all()

    qs = _scope_queryset_par_role(request.user).select_related("client")

    # filtres periode
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    try:
        if date_debut:
            dt_start = datetime.fromisoformat(date_debut)
            qs = qs.filter(date_soumission__gte=dt_start)
        if date_fin:
            dt_end = datetime.fromisoformat(date_fin)
            qs = qs.filter(date_soumission__lte=dt_end)
    except Exception:
        pass

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="dossiers_rapports.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "reference",
            "client",
            "produit",
            "montant",
            "statut_agent",
            "statut_client",
            "date_soumission",
            "date_maj",
        ]
    )
    for d in qs.order_by("-date_soumission"):
        writer.writerow(
            [
                d.reference,
                getattr(d.client, "username", ""),
                d.produit,
                d.montant,
                d.statut_agent,
                d.statut_client,
                d.date_soumission,
                d.date_maj,
            ]
        )
    return response


@login_required
def stats_view(request):
    """Vue des statistiques detaillees"""
    # e€ implementer selon vos besoins
    return render(request, "portail_pro/stats.html", {})


@login_required
def reports_redirect(request):
    """Redirection vers la vue des rapports"""
    return reports_view(request)


@login_required
@require_GET
def reports_users_view(request):
    """Vue des rapports utilisateurs pour le super administrateur"""
    from django.contrib.auth import get_user_model
    from django.db.models import Count
    from django.db.models.functions import TruncMonth
    from .models import UserProfile, UserRoles
    import json
    
    User = get_user_model()
    
    # Vérifier que l'utilisateur est bien super admin
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", None)
    if role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Accès non autorisé à cette page.")
        return redirect("pro:dashboard")
    
    # Filtrage par période
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    
    users_qs = User.objects.select_related("profile").all()
    
    try:
        if date_debut:
            dt_start = datetime.fromisoformat(date_debut)
            users_qs = users_qs.filter(date_joined__gte=dt_start)
        if date_fin:
            dt_end = datetime.fromisoformat(date_fin)
            users_qs = users_qs.filter(date_joined__lte=dt_end)
    except Exception:
        pass
    
    # Statistiques générales
    stats = {
        "total_users": users_qs.count(),
        "active_users": users_qs.filter(is_active=True).count(),
        "inactive_users": users_qs.filter(is_active=False).count(),
        "users_this_period": users_qs.count(),
    }
    
    # Répartition par rôle
    par_role = []
    for role_value, role_label in UserRoles.choices:
        count = UserProfile.objects.filter(
            user__in=users_qs, role=role_value
        ).count()
        if count > 0:
            par_role.append({"role": role_label, "count": count})
    
    # KPIs
    total_profiles = UserProfile.objects.filter(user__in=users_qs).count()
    users_with_profile = users_qs.filter(profile__isnull=False).count()
    profile_completion_rate = round((users_with_profile / stats["total_users"] * 100), 2) if stats["total_users"] > 0 else 0
    
    kpis = {
        "total_profiles": total_profiles,
        "profile_completion_rate": profile_completion_rate,
        "active_rate": round((stats["active_users"] / stats["total_users"] * 100), 2) if stats["total_users"] > 0 else 0,
    }
    
    # Données pour graphiques
    # 1. Évolution mensuelle des inscriptions
    monthly_data = (
        users_qs.annotate(mois=TruncMonth("date_joined"))
        .values("mois")
        .annotate(count=Count("id"))
        .order_by("mois")
    )
    chart_monthly = {
        "labels": [
            d["mois"].strftime("%b %Y") if d["mois"] else "" for d in monthly_data
        ],
        "data": [d["count"] for d in monthly_data],
    }
    
    # 2. Répartition par rôle (camembert)
    chart_roles = {
        "labels": [r["role"] for r in par_role],
        "data": [r["count"] for r in par_role],
    }
    
    # 3. Actifs vs Inactifs
    chart_status = {
        "labels": ["Actifs", "Inactifs"],
        "data": [stats["active_users"], stats["inactive_users"]],
    }
    
    charts_data = {
        "monthly": chart_monthly,
        "roles": chart_roles,
        "status": chart_status,
    }
    
    return render(
        request,
        "portail_pro/reports_users.html",
        {
            "stats": stats,
            "par_role": par_role,
            "kpis": kpis,
            "charts_json": json.dumps(charts_data),
        },
    )


@login_required
@require_GET
def reports_gestionnaire_view(request):
    """Vue des rapports pour le Gestionnaire - Pilotage global des dossiers"""
    from .models import DossierCredit, JournalAction, DossierStatutAgent
    from django.db.models import Count, Sum, Avg, Q
    from django.db.models.functions import TruncMonth
    import json
    
    # Tous les dossiers (vue globale du gestionnaire)
    qs = DossierCredit.objects.all()
    
    # Filtrage par période
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    
    try:
        if date_debut:
            dt_start = datetime.fromisoformat(date_debut)
            qs = qs.filter(date_soumission__gte=dt_start)
        if date_fin:
            dt_end = datetime.fromisoformat(date_fin)
            qs = qs.filter(date_soumission__lte=dt_end)
    except Exception:
        pass
    
    # Statistiques générales
    stats = {
        "total_dossiers": qs.count(),
        "dossiers_nouveaux": qs.filter(statut_agent=DossierStatutAgent.NOUVEAU).count(),
        "dossiers_en_cours": qs.exclude(
            statut_agent__in=[DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        ).count(),
        "dossiers_approuves": qs.filter(statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS).count(),
        "dossiers_refuses": qs.filter(statut_agent=DossierStatutAgent.REFUSE).count(),
        "dossiers_liberes": qs.filter(statut_agent=DossierStatutAgent.FONDS_LIBERE).count(),
        "montant_total": qs.aggregate(total=Sum("montant"))["total"] or 0,
    }
    
    # Répartition par statut
    par_statut = (
        qs.values("statut_agent")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    
    # KPIs spécifiques au gestionnaire
    finals = [DossierStatutAgent.APPROUVE_ATTENTE_FONDS, DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
    processed_count = qs.filter(statut_agent__in=finals).count()
    approved_count = qs.filter(statut_agent__in=[DossierStatutAgent.APPROUVE_ATTENTE_FONDS, DossierStatutAgent.FONDS_LIBERE]).count()
    refused_count = qs.filter(statut_agent=DossierStatutAgent.REFUSE).count()
    
    denom = processed_count or 1
    acceptance_rate = round((approved_count / denom) * 100, 2)
    reject_rate = round((refused_count / denom) * 100, 2)
    
    # Dossiers avec retour client
    rework_count = JournalAction.objects.filter(
        dossier_id__in=qs.values_list("id", flat=True),
        action__in=["RETOUR_CLIENT", "RETOUR_GESTIONNAIRE"]
    ).values("dossier_id").distinct().count()
    
    kpis = {
        "processed_count": processed_count,
        "acceptance_rate": acceptance_rate,
        "reject_rate": reject_rate,
        "rework_count": rework_count,
        "montant_approuve": qs.filter(
            statut_agent__in=[DossierStatutAgent.APPROUVE_ATTENTE_FONDS, DossierStatutAgent.FONDS_LIBERE]
        ).aggregate(total=Sum("montant"))["total"] or 0,
    }
    
    # Graphiques
    # 1. Évolution mensuelle des dossiers créés
    monthly_data = (
        qs.annotate(mois=TruncMonth("date_soumission"))
        .values("mois")
        .annotate(count=Count("id"))
        .order_by("mois")
    )
    chart_monthly = {
        "labels": [d["mois"].strftime("%b %Y") if d["mois"] else "" for d in monthly_data],
        "data": [d["count"] for d in monthly_data],
    }
    
    # 2. Répartition par statut
    chart_statuts = {
        "labels": [row["statut_agent"] for row in par_statut],
        "data": [row["count"] for row in par_statut],
    }
    
    # 3. Performance par analyste (top 5)
    analyst_performance = []
    try:
        analysts = qs.filter(
            statut_agent__in=finals
        ).values("acteur_courant__username").annotate(
            total=Count("id"),
            approuves=Count("id", filter=Q(statut_agent__in=[DossierStatutAgent.APPROUVE_ATTENTE_FONDS, DossierStatutAgent.FONDS_LIBERE]))
        ).order_by("-total")[:5]
        
        for analyst in analysts:
            if analyst["acteur_courant__username"]:
                analyst_performance.append({
                    "name": analyst["acteur_courant__username"],
                    "total": analyst["total"],
                    "approuves": analyst["approuves"]
                })
    except Exception:
        pass
    
    chart_analysts = {
        "labels": [a["name"] for a in analyst_performance],
        "data": [a["approuves"] for a in analyst_performance],
    }
    
    charts_data = {
        "monthly": chart_monthly,
        "statuts": chart_statuts,
        "analysts": chart_analysts,
    }
    
    return render(
        request,
        "portail_pro/reports_gestionnaire.html",
        {
            "stats": stats,
            "par_statut": par_statut,
            "kpis": kpis,
            "charts_json": json.dumps(charts_data),
        },
    )


@login_required
@require_GET
def reports_analyste_view(request):
    """Vue des rapports pour l'Analyste - Analyses et scoring de crédit"""
    from .models import DossierCredit, JournalAction, DossierStatutAgent
    from django.db.models import Count, Sum, Avg, Q
    from django.db.models.functions import TruncMonth
    import json
    
    # Dossiers assignés à l'analyste ou qu'il a traités
    dossier_ids = (
        JournalAction.objects.filter(acteur=request.user)
        .values_list("dossier_id", flat=True)
        .distinct()
    )
    qs = DossierCredit.objects.filter(
        Q(id__in=dossier_ids) | Q(acteur_courant=request.user)
    )
    
    # Filtrage par période
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    
    try:
        if date_debut:
            dt_start = datetime.fromisoformat(date_debut)
            qs = qs.filter(date_soumission__gte=dt_start)
        if date_fin:
            dt_end = datetime.fromisoformat(date_fin)
            qs = qs.filter(date_soumission__lte=dt_end)
    except Exception:
        pass
    
    # Statistiques générales
    stats = {
        "total_dossiers": qs.count(),
        "dossiers_en_analyse": qs.filter(
            statut_agent__in=[DossierStatutAgent.TRANSMIS_ANALYSTE, DossierStatutAgent.EN_COURS_ANALYSE]
        ).count(),
        "dossiers_analyses": qs.filter(
            statut_agent__in=[
                DossierStatutAgent.EN_COURS_VALIDATION_GGR,
                DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
                DossierStatutAgent.FONDS_LIBERE,
                DossierStatutAgent.REFUSE
            ]
        ).count(),
        "dossiers_approuves": qs.filter(
            statut_agent__in=[DossierStatutAgent.APPROUVE_ATTENTE_FONDS, DossierStatutAgent.FONDS_LIBERE]
        ).count(),
        "dossiers_refuses": qs.filter(statut_agent=DossierStatutAgent.REFUSE).count(),
        "montant_total": qs.aggregate(total=Sum("montant"))["total"] or 0,
    }
    
    # Répartition par statut
    par_statut = (
        qs.values("statut_agent")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    
    # KPIs spécifiques à l'analyste
    analyses_terminees = stats["dossiers_analyses"]
    approuves = stats["dossiers_approuves"]
    refuses = stats["dossiers_refuses"]
    
    denom = analyses_terminees or 1
    taux_approbation = round((approuves / denom) * 100, 2)
    taux_refus = round((refuses / denom) * 100, 2)
    
    # Délai moyen d'analyse
    delai_moyen = 0.0
    try:
        analyses_avec_delai = []
        for dossier in qs.filter(statut_agent__in=[
            DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
            DossierStatutAgent.FONDS_LIBERE,
            DossierStatutAgent.REFUSE
        ]):
            # Chercher la première action de l'analyste
            premiere_action = JournalAction.objects.filter(
                dossier=dossier,
                acteur=request.user
            ).order_by("timestamp").first()
            
            if premiere_action and dossier.date_maj:
                delta = (dossier.date_maj - premiere_action.timestamp).total_seconds() / 86400
                if delta >= 0:
                    analyses_avec_delai.append(delta)
        
        if analyses_avec_delai:
            delai_moyen = round(sum(analyses_avec_delai) / len(analyses_avec_delai), 2)
    except Exception:
        pass
    
    kpis = {
        "analyses_terminees": analyses_terminees,
        "taux_approbation": taux_approbation,
        "taux_refus": taux_refus,
        "delai_moyen": delai_moyen,
        "montant_analyse": qs.filter(
            statut_agent__in=[
                DossierStatutAgent.EN_COURS_VALIDATION_GGR,
                DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
                DossierStatutAgent.FONDS_LIBERE
            ]
        ).aggregate(total=Sum("montant"))["total"] or 0,
    }
    
    # Graphiques
    # 1. Évolution mensuelle des analyses
    monthly_data = (
        qs.filter(statut_agent__in=[
            DossierStatutAgent.EN_COURS_VALIDATION_GGR,
            DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
            DossierStatutAgent.FONDS_LIBERE,
            DossierStatutAgent.REFUSE
        ])
        .annotate(mois=TruncMonth("date_maj"))
        .values("mois")
        .annotate(count=Count("id"))
        .order_by("mois")
    )
    chart_monthly = {
        "labels": [d["mois"].strftime("%b %Y") if d["mois"] else "" for d in monthly_data],
        "data": [d["count"] for d in monthly_data],
    }
    
    # 2. Répartition par statut
    chart_statuts = {
        "labels": [row["statut_agent"] for row in par_statut],
        "data": [row["count"] for row in par_statut],
    }
    
    # 3. Décisions (Approuvé vs Refusé)
    chart_decisions = {
        "labels": ["Approuvés", "Refusés", "En cours"],
        "data": [approuves, refuses, stats["dossiers_en_analyse"]],
    }
    
    charts_data = {
        "monthly": chart_monthly,
        "statuts": chart_statuts,
        "decisions": chart_decisions,
    }
    
    return render(
        request,
        "portail_pro/reports_analyste.html",
        {
            "stats": stats,
            "par_statut": par_statut,
            "kpis": kpis,
            "charts_json": json.dumps(charts_data),
        },
    )


@login_required
@require_GET
def reports_responsable_ggr_view(request):
    """Vue des rapports pour le Responsable GGR - Validations et décisions"""
    from .models import DossierCredit, JournalAction, DossierStatutAgent
    from django.db.models import Count, Sum, Q
    from django.db.models.functions import TruncMonth
    import json
    
    # Tous les dossiers (vue globale pour validation)
    qs = DossierCredit.objects.all()
    
    # Filtrage par période
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    
    try:
        if date_debut:
            dt_start = datetime.fromisoformat(date_debut)
            qs = qs.filter(date_soumission__gte=dt_start)
        if date_fin:
            dt_end = datetime.fromisoformat(date_fin)
            qs = qs.filter(date_soumission__lte=dt_end)
    except Exception:
        pass
    
    # Statistiques générales
    stats = {
        "total_dossiers": qs.count(),
        "en_attente_validation": qs.filter(
            statut_agent=DossierStatutAgent.EN_COURS_VALIDATION_GGR
        ).count(),
        "valides_approuves": qs.filter(
            statut_agent__in=[DossierStatutAgent.APPROUVE_ATTENTE_FONDS, DossierStatutAgent.FONDS_LIBERE]
        ).count(),
        "refuses": qs.filter(statut_agent=DossierStatutAgent.REFUSE).count(),
        "en_attente_dg": qs.filter(statut_agent=DossierStatutAgent.EN_ATTENTE_DECISION_DG).count(),
        "montant_total": qs.aggregate(total=Sum("montant"))["total"] or 0,
    }
    
    # Répartition par statut
    par_statut = (
        qs.values("statut_agent")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    
    # KPIs spécifiques au Responsable GGR
    decisions_prises = stats["valides_approuves"] + stats["refuses"]
    approuves = stats["valides_approuves"]
    refuses = stats["refuses"]
    
    denom = decisions_prises or 1
    taux_approbation = round((approuves / denom) * 100, 2)
    taux_refus = round((refuses / denom) * 100, 2)
    
    # Montants validés
    montant_valide = qs.filter(
        statut_agent__in=[DossierStatutAgent.APPROUVE_ATTENTE_FONDS, DossierStatutAgent.FONDS_LIBERE]
    ).aggregate(total=Sum("montant"))["total"] or 0
    
    montant_refuse = qs.filter(
        statut_agent=DossierStatutAgent.REFUSE
    ).aggregate(total=Sum("montant"))["total"] or 0
    
    kpis = {
        "decisions_prises": decisions_prises,
        "taux_approbation": taux_approbation,
        "taux_refus": taux_refus,
        "montant_valide": montant_valide,
        "montant_refuse": montant_refuse,
    }
    
    # Graphiques
    # 1. Évolution mensuelle des validations
    monthly_data = (
        qs.filter(statut_agent__in=[
            DossierStatutAgent.APPROUVE_ATTENTE_FONDS,
            DossierStatutAgent.FONDS_LIBERE,
            DossierStatutAgent.REFUSE
        ])
        .annotate(mois=TruncMonth("date_maj"))
        .values("mois")
        .annotate(count=Count("id"))
        .order_by("mois")
    )
    chart_monthly = {
        "labels": [d["mois"].strftime("%b %Y") if d["mois"] else "" for d in monthly_data],
        "data": [d["count"] for d in monthly_data],
    }
    
    # 2. Répartition par statut
    chart_statuts = {
        "labels": [row["statut_agent"] for row in par_statut],
        "data": [row["count"] for row in par_statut],
    }
    
    # 3. Décisions (Approuvés vs Refusés vs En attente)
    chart_decisions = {
        "labels": ["Approuvés", "Refusés", "En attente validation"],
        "data": [approuves, refuses, stats["en_attente_validation"]],
    }
    
    charts_data = {
        "monthly": chart_monthly,
        "statuts": chart_statuts,
        "decisions": chart_decisions,
    }
    
    return render(
        request,
        "portail_pro/reports_responsable_ggr.html",
        {
            "stats": stats,
            "par_statut": par_statut,
            "kpis": kpis,
            "charts_json": json.dumps(charts_data),
        },
    )


@login_required
@require_GET
def reports_boe_view(request):
    """Vue des rapports pour le BOE - Libération de fonds"""
    from .models import DossierCredit, JournalAction, DossierStatutAgent
    from django.db.models import Count, Sum
    from django.db.models.functions import TruncMonth
    import json
    
    # Dossiers pertinents pour le BOE (approuvés et fonds libérés)
    qs = DossierCredit.objects.filter(
        statut_agent__in=[DossierStatutAgent.APPROUVE_ATTENTE_FONDS, DossierStatutAgent.FONDS_LIBERE]
    )
    
    # Filtrage par période
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    
    try:
        if date_debut:
            dt_start = datetime.fromisoformat(date_debut)
            qs = qs.filter(date_soumission__gte=dt_start)
        if date_fin:
            dt_end = datetime.fromisoformat(date_fin)
            qs = qs.filter(date_soumission__lte=dt_end)
    except Exception:
        pass
    
    # Statistiques générales
    stats = {
        "total_dossiers": qs.count(),
        "en_attente_liberation": qs.filter(
            statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS
        ).count(),
        "fonds_liberes": qs.filter(
            statut_agent=DossierStatutAgent.FONDS_LIBERE
        ).count(),
        "montant_total": qs.aggregate(total=Sum("montant"))["total"] or 0,
        "montant_en_attente": qs.filter(
            statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS
        ).aggregate(total=Sum("montant"))["total"] or 0,
        "montant_libere": qs.filter(
            statut_agent=DossierStatutAgent.FONDS_LIBERE
        ).aggregate(total=Sum("montant"))["total"] or 0,
    }
    
    # Répartition par statut
    par_statut = (
        qs.values("statut_agent")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    
    # KPIs spécifiques au BOE
    total = stats["total_dossiers"]
    liberes = stats["fonds_liberes"]
    en_attente = stats["en_attente_liberation"]
    
    denom = total or 1
    taux_liberation = round((liberes / denom) * 100, 2)
    taux_en_attente = round((en_attente / denom) * 100, 2)
    
    kpis = {
        "taux_liberation": taux_liberation,
        "taux_en_attente": taux_en_attente,
        "montant_moyen_libere": round(stats["montant_libere"] / liberes, 2) if liberes > 0 else 0,
    }
    
    # Graphiques
    # 1. Évolution mensuelle des libérations
    monthly_data = (
        qs.filter(statut_agent=DossierStatutAgent.FONDS_LIBERE)
        .annotate(mois=TruncMonth("date_maj"))
        .values("mois")
        .annotate(count=Count("id"))
        .order_by("mois")
    )
    chart_monthly = {
        "labels": [d["mois"].strftime("%b %Y") if d["mois"] else "" for d in monthly_data],
        "data": [d["count"] for d in monthly_data],
    }
    
    # 2. Montants par mois
    monthly_montants = (
        qs.filter(statut_agent=DossierStatutAgent.FONDS_LIBERE)
        .annotate(mois=TruncMonth("date_maj"))
        .values("mois")
        .annotate(montant=Sum("montant"))
        .order_by("mois")
    )
    chart_montants = {
        "labels": [d["mois"].strftime("%b %Y") if d["mois"] else "" for d in monthly_montants],
        "data": [float(d["montant"]) for d in monthly_montants],
    }
    
    # 3. Statut (En attente vs Libéré)
    chart_statut = {
        "labels": ["En attente libération", "Fonds libérés"],
        "data": [en_attente, liberes],
    }
    
    charts_data = {
        "monthly": chart_monthly,
        "montants": chart_montants,
        "statut": chart_statut,
    }
    
    return render(
        request,
        "portail_pro/reports_boe.html",
        {
            "stats": stats,
            "par_statut": par_statut,
            "kpis": kpis,
            "charts_json": json.dumps(charts_data),
        },
    )

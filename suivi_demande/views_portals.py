"""
Vues spécifiques aux portails Client et Professionnel
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



def login_client_view(request):
    """
    Vue de connexion pour le portail CLIENT
    Restreint uniquement aux utilisateurs avec rôle CLIENT
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Vérifier que l'utilisateur a le rôle CLIENT
            profile = getattr(user, 'profile', None)
            role = getattr(profile, 'role', None)
            
            if role != UserRoles.CLIENT:
                messages.error(
                    request,
                    "Accès refusé. Cet espace est réservé aux clients. "
                    "Les professionnels doivent utiliser le portail pro.ggr-credit.cg"
                )
                return render(request, 'portail_client/login.html', {'form': form})
            
            # Connexion réussie
            auth_login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")
            
            # Redirection vers le dashboard client
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'portail_client/login.html', {
        'form': form,
        'portal_type': 'client',
    })


def login_pro_view(request):
    """
    Vue de connexion pour le portail PROFESSIONNEL
    Restreint aux utilisateurs avec rôles professionnels
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Vérifier que l'utilisateur a un rôle professionnel
            profile = getattr(user, 'profile', None)
            role = getattr(profile, 'role', None)
            
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
                    "Accès refusé. Cet espace est réservé aux professionnels. "
                    "Les clients doivent utiliser le portail client.ggr-credit.cg"
                )
                return render(request, 'portail_pro/login.html', {'form': form})
            
            # Connexion réussie
            auth_login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")
            
            # Redirection vers le dashboard pro
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'portail_pro/login.html', {
        'form': form,
        'portal_type': 'professional',
    })


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
    
    # Vérifier que le client accède à son propre dossier
    if dossier.client != request.user:
        messages.error(request, "Vous ne pouvez consulter que vos propres dossiers.")
        return redirect('client:my_applications')
    
    documents = dossier.pieces.all().order_by('-date_upload')
    
    return render(request, 'portail_client/view_documents.html', {
        'dossier': dossier,
        'documents': documents,
    })


@login_required
def all_dossiers_list(request):
    """
    Liste de tous les dossiers pour les professionnels
    Avec filtres et recherche
    """
    from .models import DossierCredit, UserRoles
    
    # Vérifier le rôle professionnel
    profile = getattr(request.user, 'profile', None)
    role = getattr(profile, 'role', None)
    
    # Filtrer selon le rôle
    if role == UserRoles.GESTIONNAIRE:
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=['NOUVEAU', 'INCOMPLET']
        )
    elif role == UserRoles.ANALYSTE:
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=['TRANSMIS_ANALYSTE', 'EN_COURS_ANALYSE']
        )
    elif role == UserRoles.RESPONSABLE_GGR:
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=['EN_COURS_VALIDATION_GGR', 'EN_ATTENTE_DECISION_DG']
        )
    elif role == UserRoles.BOE:
        dossiers = DossierCredit.objects.filter(
            statut_agent='APPROUVE_ATTENTE_FONDS'
        )
    else:  # SUPER_ADMIN
        dossiers = DossierCredit.objects.all()
    
    dossiers = dossiers.order_by('-date_soumission')
    
    return render(request, 'portail_pro/all_dossiers.html', {
        'dossiers': dossiers,
        'user_role': role,
    })


@login_required
@require_GET
def reports_view(request):
    """Vue des rapports pour les professionnels (filtrés par utilisateur connecté)"""
    from .models import DossierCredit, UserRoles, JournalAction
    from django.db.models import Count, Sum

    # Déterminer le périmètre de l'utilisateur selon son rôle
    def _scope_queryset_par_role(user):
        profile = getattr(user, 'profile', None)
        role = getattr(profile, 'role', None)

        if role == UserRoles.CLIENT:
            # Interdit côté portail pro
            return DossierCredit.objects.none()

        if role == UserRoles.GESTIONNAIRE:
            # Gestionnaire: vue globale (pilotage)
            return DossierCredit.objects.all()

        if role == UserRoles.ANALYSTE:
            dossier_ids = (JournalAction.objects
                           .filter(acteur=user)
                           .values_list('dossier_id', flat=True)
                           .distinct())
            return DossierCredit.objects.filter(
                (models.Q(id__in=dossier_ids)) | (models.Q(acteur_courant=user))
            )

        # RESPONSABLE_GGR / BOE / SUPER_ADMIN -> tout le périmètre
        return DossierCredit.objects.all()

    # Contrôle d'accès: rôles autorisés (détection robuste du rôle)
    def get_user_role(user):
        role = getattr(getattr(user, 'profile', None), 'role', None)
        if not role:
            role = getattr(getattr(user, 'userprofile', None), 'role', None)
        return role

    user_role = get_user_role(request.user)
    allowed_roles = [
        UserRoles.GESTIONNAIRE,
        UserRoles.ANALYSTE,
        UserRoles.RESPONSABLE_GGR,
        UserRoles.BOE,
        UserRoles.SUPER_ADMIN,
    ]
    if user_role not in allowed_roles:
        messages.error(request, "Accès non autorisé à la page Rapports.")
        return redirect('pro:dashboard')

    qs = _scope_queryset_par_role(request.user)

    # Ajustement de périmètre spécifique au rôle BOE: dossiers pertinents pour la libération des fonds
    if user_role == UserRoles.BOE:
        qs = qs.filter(statut_agent__in=['APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE'])

    # Filtrage période (date_debut, date_fin) sur la date de soumission du dossier
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    try:
        if date_debut:
            dt_start = datetime.fromisoformat(date_debut)
            qs = qs.filter(date_soumission__gte=dt_start)
        if date_fin:
            # inclure fin de journée
            dt_end = datetime.fromisoformat(date_fin)
            qs = qs.filter(date_soumission__lte=dt_end)
    except Exception:
        # ignore filtre si format invalide
        pass

    # Statistiques dans le périmètre (role-aware)
    if user_role == UserRoles.BOE:
        # Pour BOE, en_cours = en attente de libération; approuves = fonds libérés
        stats = {
            'total_dossiers': qs.count(),
            'en_cours': qs.filter(statut_agent='APPROUVE_ATTENTE_FONDS').count(),
            'approuves': qs.filter(statut_agent='FONDS_LIBERE').count(),
            'refuses': 0,
            'montant_total': qs.aggregate(total=Sum('montant'))['total'] or 0,
        }
    else:
        stats = {
            'total_dossiers': qs.count(),
            'en_cours': qs.exclude(
                statut_agent__in=['APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE', 'REFUSE']
            ).count(),
            'approuves': qs.filter(
                statut_agent='APPROUVE_ATTENTE_FONDS'
            ).count(),
            'refuses': qs.filter(
                statut_agent='REFUSE'
            ).count(),
            'montant_total': qs.aggregate(
                total=Sum('montant')
            )['total'] or 0,
        }

    # Par statut dans le périmètre
    par_statut = qs.values('statut_agent').annotate(
        count=Count('id')
    ).order_by('-count')

    # KPIs additionnels
    finals = ['APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE', 'REFUSE']
    processed_count = qs.filter(statut_agent__in=finals).count()
    approved_count = qs.filter(statut_agent__in=['APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE']).count()
    refused_count = qs.filter(statut_agent='REFUSE').count()
    denom = processed_count or 1
    acceptance_rate = round((approved_count / denom) * 100, 2)
    reject_rate = round((refused_count / denom) * 100, 2)

    # Rework: dossiers avec retour
    rework_count = 0
    try:
        rework_count = (JournalAction.objects
                        .filter(dossier_id__in=qs.values_list('id', flat=True),
                                action__in=['RETOUR_CLIENT', 'RETOUR_GESTIONNAIRE'])
                        .values('dossier_id')
                        .distinct()
                        .count())
    except Exception:
        rework_count = 0

    # Lead time moyen (jours): soumission -> 1er statut final
    lead_time_sum = 0.0
    lead_time_n = 0
    try:
        dossier_ids = list(qs.values_list('id', 'date_soumission'))
        if dossier_ids:
            # map id -> date_soumission
            submit_map = {did: ds for did, ds in dossier_ids}
            finals_qs = (JournalAction.objects
                         .filter(dossier_id__in=submit_map.keys(), vers_statut__in=finals)
                         .order_by('dossier_id', 'timestamp')
                         .values('dossier_id', 'timestamp'))
            seen = set()
            for row in finals_qs:
                did = row['dossier_id']
                if did in seen:
                    continue
                seen.add(did)
                ts_final = row['timestamp']
                dt_submit = submit_map.get(did)
                if dt_submit and ts_final and ts_final > dt_submit:
                    delta = ts_final - dt_submit
                    lead_time_sum += (delta.total_seconds() / 86400.0)
                    lead_time_n += 1
    except Exception:
        pass
    lead_time_avg_days = round(lead_time_sum / lead_time_n, 2) if lead_time_n else 0.0

    kpis = {
        'processed_count': processed_count,
        'acceptance_rate': acceptance_rate,
        'reject_rate': reject_rate,
        'rework_count': rework_count,
        'lead_time_avg_days': lead_time_avg_days,
    }

    # Données pour graphiques Chart.js
    import json
    from collections import defaultdict
    from django.db.models.functions import TruncMonth

    # 1. Évolution mensuelle (courbe)
    monthly_data = (qs.filter(statut_agent__in=finals)
                    .annotate(mois=TruncMonth('date_soumission'))
                    .values('mois')
                    .annotate(count=Count('id'))
                    .order_by('mois'))
    chart_monthly = {
        'labels': [d['mois'].strftime('%b %Y') if d['mois'] else '' for d in monthly_data],
        'data': [d['count'] for d in monthly_data]
    }

    # 2. Répartition par statut (camembert)
    chart_statuts = {
        'labels': [row['statut_agent'] for row in par_statut],
        'data': [row['count'] for row in par_statut]
    }

    # 3. Lead time par gestionnaire (histogramme) - top 10
    try:
        from django.db.models import Avg
        lead_by_manager = []
        # Récupérer les gestionnaires avec dossiers
        managers_qs = (qs.exclude(acteur_courant__isnull=True)
                       .values('acteur_courant__username')
                       .annotate(nb=Count('id'))
                       .filter(nb__gt=0)
                       .order_by('-nb')[:10])
        manager_names = [m['acteur_courant__username'] for m in managers_qs]
        
        # Calculer lead time moyen par gestionnaire (approximation simple)
        for mgr in manager_names:
            mgr_dossiers = qs.filter(acteur_courant__username=mgr, statut_agent__in=finals)
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
                    lead_by_manager.append({'manager': mgr, 'avg_days': round(avg_days / count, 1)})
        
        chart_lead_time = {
            'labels': [m['manager'] for m in lead_by_manager],
            'data': [m['avg_days'] for m in lead_by_manager]
        }
    except Exception:
        chart_lead_time = {'labels': [], 'data': []}

    charts_data = {
        'monthly': chart_monthly,
        'statuts': chart_statuts,
        'lead_time': chart_lead_time
    }

    return render(request, 'portail_pro/reports.html', {
        'stats': stats,
        'par_statut': par_statut,
        'kpis': kpis,
        'charts_json': json.dumps(charts_data),
    })


@login_required
def rapports_export_csv(request):
    """Export CSV des dossiers selon le périmètre et les filtres de période."""
    from .models import DossierCredit, UserRoles, JournalAction
    import csv
    from django.http import HttpResponse

    # même périmètre que reports_view
    def _scope_queryset_par_role(user):
        profile = getattr(user, 'profile', None)
        role = getattr(profile, 'role', None)
        if role == UserRoles.CLIENT:
            return DossierCredit.objects.none()
        if role == UserRoles.GESTIONNAIRE:
            return DossierCredit.objects.all()
        if role == UserRoles.ANALYSTE:
            dossier_ids = (JournalAction.objects
                           .filter(acteur=user)
                           .values_list('dossier_id', flat=True)
                           .distinct())
            return DossierCredit.objects.filter(
                (models.Q(id__in=dossier_ids)) | (models.Q(acteur_courant=user))
            )
        return DossierCredit.objects.all()

    qs = _scope_queryset_par_role(request.user).select_related('client')

    # filtres période
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    try:
        if date_debut:
            dt_start = datetime.fromisoformat(date_debut)
            qs = qs.filter(date_soumission__gte=dt_start)
        if date_fin:
            dt_end = datetime.fromisoformat(date_fin)
            qs = qs.filter(date_soumission__lte=dt_end)
    except Exception:
        pass

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dossiers_rapports.csv"'
    writer = csv.writer(response)
    writer.writerow(['reference','client','produit','montant','statut_agent','statut_client','date_soumission','date_maj'])
    for d in qs.order_by('-date_soumission'):
        writer.writerow([
            d.reference,
            getattr(d.client, 'username', ''),
            d.produit,
            d.montant,
            d.statut_agent,
            d.statut_client,
            d.date_soumission,
            d.date_maj,
        ])
    return response


@login_required
def stats_view(request):
    """Vue des statistiques détaillées"""
    # À implémenter selon vos besoins
    return render(request, 'portail_pro/stats.html', {})



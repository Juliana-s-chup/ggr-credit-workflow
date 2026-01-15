"""
Views pour l'application suivi_demande.
Gère les demandes de crédit, le workflow et les dashboards.
"""
# Imports Django standard
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
import statistics
import traceback

# Imports Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.core.mail import send_mail
from django.db.models import Q, Sum, Count, Avg
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

# Imports xhtml2pdf
from xhtml2pdf import pisa

# Imports locaux
from .decorators import transition_allowed
from .forms import SignupForm
from .forms_demande import DemandeStep1Form, DemandeStep2Form
from .forms_demande_extra import DemandeStep3Form, DemandeStep4Form
from .models import (
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    JournalAction,
    Notification,
    UserRoles,
    UserProfile,
    Commentaire,
    PieceJointe,
    CanevasProposition,
)
from .permissions import can_upload_piece, get_transition_flags
from .utils import get_current_namespace

# Nouveaux imports - Service Layer et Utilitaires
from .services.dossier_service import DossierService
from .user_utils import get_user_role, user_has_role, is_professional_user
from .validators import validate_file_upload, sanitize_filename

User = get_user_model()


def serialize_form_data(data):
    """Convertit les objets Decimal, date et datetime en strings pour la sérialisation JSON."""
    serialized = {}
    for key, value in data.items():
        if isinstance(value, Decimal):
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif isinstance(value, date):
            serialized[key] = value.isoformat()
        elif isinstance(value, float):
            serialized[key] = str(value)
        else:
            serialized[key] = value
    return serialized


@login_required
def test_dossiers_list(request):
    """Vue de test pour afficher TOUS les dossiers en base"""
    all_dossiers = DossierCredit.objects.all().order_by('-date_soumission')
    total_dossiers = all_dossiers.count()
    
    # Statistiques par statut
    statuts_stats = DossierCredit.objects.values('statut_agent').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'all_dossiers': all_dossiers,
        'total_dossiers': total_dossiers,
        'statuts_stats': statuts_stats,
    }
    return render(request, 'suivi_demande/test_dossiers.html', context)


@login_required
def my_applications(request):
    """Afficher les dossiers du client avec pagination."""
    from django.core.paginator import Paginator
    from .constants import ITEMS_PER_PAGE
    
    dossiers_list = DossierCredit.objects.filter(
        client=request.user
    ).select_related('acteur_courant').order_by("-date_soumission")
    
    paginator = Paginator(dossiers_list, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    dossiers = paginator.get_page(page_number)
    
    return render(request, "suivi_demande/my_applications.html", {"dossiers": dossiers})


@login_required
def create_application(request):
    return render(request, "suivi_demande/nouveau_dossier.html")


def signup(request):
    portal = (request.GET.get('as') or request.POST.get('as') or 'client').lower()
    portal = 'pro' if portal in ['pro', 'professionnel', 'prof'] else 'client'

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                profile = getattr(user, 'profile', None)
                if profile is None:
                    profile = UserProfile.objects.create(
                        user=user,
                        full_name=user.get_full_name() or user.username,
                        phone='', address='',
                        role=UserRoles.CLIENT
                    )
                # Affectation du rôle selon le portail d'origine
                if portal == 'pro':
                    selected_role = form.cleaned_data.get('role')
                    allowed_roles = {r for r, _ in UserRoles.choices if r != UserRoles.CLIENT}
                    if selected_role in allowed_roles:
                        profile.role = selected_role
                    else:
                        profile.role = UserRoles.GESTIONNAIRE
                else:
                    profile.role = UserRoles.CLIENT
                profile.save(update_fields=['role'])
            except Exception:
                pass

            messages.success(
                request,
                "Votre compte a été créé. Il sera activé après approbation par un administrateur.",
            )
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form, "portal": portal})


@login_required
def pending_approval(request):

    if request.user.is_active:
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")
    return render(request, "accounts/pending_approval.html")


@login_required
def dashboard(request):
    """
    Dashboard principal avec optimisations Service Layer.
    Utilise get_user_role() et DossierService pour les performances.
    """
    # Utiliser user_utils pour récupérer le rôle (plus robuste)
    role = get_user_role(request.user)
    
    # Si pas de profil, créer un profil CLIENT par défaut
    if role is None:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'full_name': request.user.get_full_name() or request.user.username,
                'phone': '',
                'address': '',
                'role': UserRoles.CLIENT
            }
        )
        role = profile.role
    
    # Debug visible dans l'interface
    debug_info = {
        'user': request.user.username,
        'profile_exists': hasattr(request.user, 'profile'),
        'role': role,
        'template_to_use': None
    }

    if role == UserRoles.CLIENT:
        debug_info['template_to_use'] = 'dashboard_client.html'
        
        # ✅ OPTIMISÉ: Utiliser le Service Layer avec pagination
        page = DossierService.get_dossiers_for_user(
            user=request.user,
            page=request.GET.get('page', 1),
            per_page=50  # Charger plus pour séparer en cours/traités
        )
        
        # Séparer en cours et traités (en mémoire, pas de nouvelle query)
        all_dossiers = list(page.object_list)
        dossiers_en_cours = [
            d for d in all_dossiers 
            if d.statut_agent not in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        ]
        dossiers_traites = [
            d for d in all_dossiers
            if d.statut_agent in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        ][:20]
        
        # ✅ OPTIMISÉ: Statistiques via Service Layer (1 query au lieu de 3)
        stats = DossierService.get_statistics_for_role(request.user)
        
        # Historique des actions (déjà optimisé avec select_related)
        historique_actions = JournalAction.objects.filter(
            dossier__client=request.user
        ).select_related('dossier', 'acteur').order_by("-timestamp")[:20]
        
        context = {
            "mes_dossiers": all_dossiers,  # Tous les dossiers
            "dossiers": dossiers_en_cours,  # En cours
            "dossiers_en_cours": dossiers_en_cours,
            "dossiers_traites": dossiers_traites,  # Terminés
            "historique_actions": historique_actions,
            "dossiers_approuves": stats['approuves'],  # ✅ Depuis stats
            "montant_total": stats['montant_total'],  # ✅ Depuis stats
            "historique_dossiers": dossiers_traites,  # compat
            "debug_info": debug_info,
            "page": page,  # Pour pagination future
        }
        return render(request, "suivi_demande/dashboard_client.html", context)

    elif role == UserRoles.GESTIONNAIRE:
        # ✅ OPTIMISÉ: Utiliser Service Layer
        page = DossierService.get_dossiers_for_user(
            user=request.user,
            page=request.GET.get('page', 1),
            per_page=50
        )
        
        # ✅ OPTIMISÉ: Statistiques en 1 query
        stats = DossierService.get_statistics_for_role(request.user)
        
        # Séparer dossiers en cours et traités (en mémoire)
        all_dossiers = list(page.object_list)
        dossiers_en_cours = [
            d for d in all_dossiers
            if d.statut_agent not in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        ]
        dossiers_traites = [
            d for d in all_dossiers
            if d.statut_agent in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        ][:20]
        
        # Dossiers en attente (nouveaux + retournés)
        dossiers_pending = [
            d for d in dossiers_en_cours
            if d.statut_agent in [DossierStatutAgent.NOUVEAU, DossierStatutAgent.TRANSMIS_RESP_GEST]
        ]
        
        # Dossiers récents (10 premiers)
        recents = all_dossiers[:10]
        
        # KPI détaillés (pour compatibilité template)
        today = timezone.now().date()
        nouveaux_total = sum(1 for d in all_dossiers if d.statut_agent == DossierStatutAgent.NOUVEAU)
        complets_total = sum(1 for d in all_dossiers if d.statut_agent in [
            DossierStatutAgent.TRANSMIS_ANALYSTE, DossierStatutAgent.EN_COURS_ANALYSE
        ])
        retournes_total = sum(1 for d in all_dossiers if d.statut_agent == DossierStatutAgent.TRANSMIS_RESP_GEST)
        
        kpi = {
            "nouveaux_total": nouveaux_total,
            "nouveaux_today": 0,  # Nécessiterait une query supplémentaire
            "complets_total": complets_total,
            "complets_today": 0,
            "retournes_total": retournes_total,
            "retournes_today": 0,
            "en_attente_total": stats['en_cours'],
            "en_attente_today": 0,
            "delai_moyen_jours": "—",
            "variation_semaine": 0,
        }
        
        # Historique actions (optimisé)
        historique_actions = JournalAction.objects.select_related(
            'dossier', 'acteur'
        ).order_by("-timestamp")[:20]
        
        # Taux de validation
        total_decides = stats['approuves'] + stats['refuses']
        taux_validation = round((stats['approuves'] / total_decides) * 100, 1) if total_decides else 0
        
        debug_info['template_to_use'] = 'dashboard_gestionnaire.html'
        debug_info['total_dossiers_base'] = stats['total']
        debug_info['dossiers_affiches'] = len(dossiers_en_cours)
        
        ctx = {
            "dossiers_pending": dossiers_pending,
            "recents": recents,
            "kpi": kpi,
            "dossiers": dossiers_en_cours,
            "dossiers_en_cours": dossiers_en_cours,
            "dossiers_traites": dossiers_traites,
            "historique_actions": historique_actions,
            "dossiers_urgents": dossiers_pending[:5],
            "dossiers_ce_mois": stats['total'],  # Approximation
            "taux_validation": taux_validation,
            "portefeuille_total": stats['montant_total'],
            "mes_clients": [],
            "mes_dossiers_crees": recents[:20],
            "debug_info": debug_info,
            "page": page,
        }
        return render(request, "suivi_demande/dashboard_gestionnaire.html", ctx)

    elif role == UserRoles.ANALYSTE:
        # ✅ OPTIMISÉ: Service Layer filtre automatiquement par rôle
        page = DossierService.get_dossiers_for_user(
            user=request.user,
            page=request.GET.get('page', 1),
            per_page=30
        )
        
        dossiers = list(page.object_list)
        dossiers_en_attente = [d for d in dossiers if d.statut_agent == DossierStatutAgent.TRANSMIS_ANALYSTE]
        dossiers_prioritaires = dossiers[:5]
        
        # ✅ OPTIMISÉ: Stats via Service Layer
        stats = DossierService.get_statistics_for_role(request.user)
        
        # Dossiers traités (séparés)
        dossiers_traites = [
            d for d in dossiers
            if d.statut_agent in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        ][:20]
        
        # Historique (optimisé)
        historique_actions = JournalAction.objects.select_related(
            'dossier', 'acteur'
        ).order_by("-timestamp")[:20]
        
        context = {
            "dossiers": dossiers,
            "dossiers_en_attente": dossiers_en_attente,
            "dossiers_a_analyser": dossiers,
            "dossiers_prioritaires": dossiers_prioritaires,
            "dossiers_traites": dossiers_traites,
            "historique_actions": historique_actions,
            "total_dossiers": stats['total'],
            "dossiers_ce_mois": stats['total'],
            "page": page,
        }
        return render(request, "suivi_demande/dashboard_analyste.html", context)

    elif role == UserRoles.RESPONSABLE_GGR:
        # ✅ OPTIMISÉ: Service Layer filtre automatiquement
        page = DossierService.get_dossiers_for_user(
            user=request.user,
            page=request.GET.get('page', 1),
            per_page=30
        )
        
        dossiers = list(page.object_list)
        dossiers_traites = [
            d for d in dossiers
            if d.statut_agent in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        ][:20]
        
        # Historique (optimisé)
        historique_actions = JournalAction.objects.select_related(
            'dossier', 'acteur'
        ).order_by("-timestamp")[:20]
        
        return render(request, "suivi_demande/dashboard_responsable_ggr_pro.html", {
            "dossiers": dossiers,
            "dossiers_traites": dossiers_traites,
            "historique_actions": historique_actions,
            "page": page,
        })

    elif role == UserRoles.BOE:
        # ✅ OPTIMISÉ: Service Layer filtre automatiquement (APPROUVE_ATTENTE_FONDS)
        page = DossierService.get_dossiers_for_user(
            user=request.user,
            page=request.GET.get('page', 1),
            per_page=30
        )
        
        dossiers = list(page.object_list)
        
        # ✅ OPTIMISÉ: Stats via Service Layer
        stats = DossierService.get_statistics_for_role(request.user)
        
        # Dossiers traités
        dossiers_traites = [
            d for d in dossiers
            if d.statut_agent in [DossierStatutAgent.FONDS_LIBERE, DossierStatutAgent.REFUSE]
        ][:20]
        
        # Historique (optimisé)
        historique_actions = JournalAction.objects.select_related(
            'dossier', 'acteur'
        ).order_by("-timestamp")[:20]
        
        context = {
            "dossiers": dossiers,
            "dossiers_traites": dossiers_traites,
            "historique_actions": historique_actions,
            "fonds_liberes_today": 0,  # Nécessiterait query supplémentaire
            "total_dossiers": stats['total'],
            "page": page,
        }
        return render(request, "suivi_demande/dashboard_boe.html", context)

    else:
        # Dashboard Super Admin - Gestion des utilisateurs uniquement
        from django.contrib.admin.models import LogEntry
        
        # Tous les utilisateurs
        all_users = User.objects.select_related('profile').all().order_by('-date_joined')
        
        # Statistiques
        stats_total_users = all_users.count()
        stats_users_active = all_users.filter(is_active=True).count()
        stats_users_inactive = all_users.filter(is_active=False).count()
        
        # Statistiques par rôle
        stats_roles = {}
        for role_value, role_label in UserRoles.choices:
            count = UserProfile.objects.filter(role=role_value).count()
            stats_roles[role_label] = count
        
        # Historique des actions sur les utilisateurs (créations, modifications, désactivations)
        # Utiliser LogEntry de Django Admin pour tracer les actions
        historique_utilisateurs = LogEntry.objects.select_related('user', 'content_type').filter(
            content_type__model__in=['user', 'userprofile']
        ).order_by('-action_time')[:50]
        
        # Utilisateurs récemment créés
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
@transition_allowed
def transition_dossier(request, pk, action: str):
    """Effectue une transition d'état sur un dossier en fonction du rôle et de l'action."""
    if request.method != "POST":
        messages.error(request, "Méthode non autorisée.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    dossier = get_object_or_404(DossierCredit, pk=pk)
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", None)

    # Récupérer le commentaire de retour s'il existe
    commentaire_retour = request.POST.get('commentaire_retour', '').strip()

    # Debug général
    print(f"?? DEBUG transition_dossier:")
    print(f"   - Utilisateur: {request.user.username}")
    print(f"   - Rôle: {role}")
    print(f"   - Action: {action}")
    print(f"   - Dossier: {dossier.reference}")
    print(f"   - Statut agent: '{dossier.statut_agent}'")
    print(f"   - Commentaire: '{commentaire_retour}'")
    
    # Message visible dans l'interface
    messages.info(request, f"?? DEBUG: Action '{action}' reçue pour dossier {dossier.reference} (statut: {dossier.statut_agent})")

    allowed = False
    de_statut = dossier.statut_agent
    vers_statut = None
    nouveau_statut_client = None
    action_log = None

    try:
        if role == UserRoles.GESTIONNAIRE and action == "transmettre_analyste":
            if dossier.statut_agent in [DossierStatutAgent.NOUVEAU, DossierStatutAgent.TRANSMIS_RESP_GEST]:
                vers_statut = DossierStatutAgent.TRANSMIS_ANALYSTE
                nouveau_statut_client = DossierStatutClient.EN_COURS_TRAITEMENT
                action_log = "TRANSITION"
                allowed = True

        elif role == UserRoles.GESTIONNAIRE and action == "retour_client":
            # Debug: afficher les valeurs pour comprendre le problème
            print(f"?? DEBUG retour_client:")
            print(f"   - dossier.statut_agent = '{dossier.statut_agent}' (type: {type(dossier.statut_agent)})")
            print(f"   - DossierStatutAgent.NOUVEAU = '{DossierStatutAgent.NOUVEAU}'")
            print(f"   - DossierStatutAgent.TRANSMIS_RESP_GEST = '{DossierStatutAgent.TRANSMIS_RESP_GEST}'")
            
            if dossier.statut_agent in [DossierStatutAgent.NOUVEAU, DossierStatutAgent.TRANSMIS_RESP_GEST]:
                if not commentaire_retour:
                    messages.error(request, "Un commentaire expliquant pourquoi le dossier est incomplet est requis.")
                    namespace = get_current_namespace(request)
                    return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)
                vers_statut = DossierStatutAgent.NOUVEAU  # Reste nouveau mais avec commentaire
                nouveau_statut_client = DossierStatutClient.SE_RAPPROCHER_GEST
                action_log = "RETOUR_CLIENT"
                allowed = True
                print(f"   ? Action retour_client autorisée")
            else:
                print(f"   ? Statut '{dossier.statut_agent}' non autorisé pour retour_client")

        elif role == UserRoles.ANALYSTE and action == "transmettre_ggr":
            if dossier.statut_agent in [DossierStatutAgent.TRANSMIS_ANALYSTE, DossierStatutAgent.EN_COURS_ANALYSE]:
                vers_statut = DossierStatutAgent.EN_COURS_VALIDATION_GGR
                nouveau_statut_client = DossierStatutClient.EN_COURS_TRAITEMENT
                action_log = "TRANSITION"
                allowed = True

        elif role == UserRoles.ANALYSTE and action == "retour_gestionnaire":
            if dossier.statut_agent in [DossierStatutAgent.TRANSMIS_ANALYSTE, DossierStatutAgent.EN_COURS_ANALYSE]:
                vers_statut = DossierStatutAgent.TRANSMIS_RESP_GEST
                nouveau_statut_client = DossierStatutClient.EN_COURS_TRAITEMENT
                action_log = "RETROU"
                allowed = True

        elif role == UserRoles.RESPONSABLE_GGR and action == "approuver":
            if dossier.statut_agent in [DossierStatutAgent.EN_COURS_VALIDATION_GGR, DossierStatutAgent.EN_ATTENTE_DECISION_DG]:
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
    except Exception:
        allowed = False

    if not allowed:
        messages.error(request, "Action non autorisée pour votre rôle ou l'état actuel du dossier.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    ancien_statut_client = dossier.statut_client
    dossier.statut_agent = vers_statut
    if nouveau_statut_client:
        dossier.statut_client = nouveau_statut_client
    dossier.acteur_courant = request.user
    dossier.save()

    # Préparer le commentaire système
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

    # Notifications internes + emails console
    try:
        # Personnaliser le message selon l'action
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
        notification = Notification.objects.create(
            utilisateur_cible=dossier.client,
            type="NOUVEAU_MESSAGE",
            titre=titre_notification,
            message=message_notification,
            canal="INTERNE",
        )
        
        # Fonction pour notifier un groupe d'utilisateurs
        def notifier_utilisateurs(role_cible, titre, message_template):
            """Notifie tous les utilisateurs d'un rôle donné"""
            utilisateurs = User.objects.filter(
                profile__role=role_cible,
                is_active=True
            )
            
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
                        expediteur=request.user.get_full_name() or request.user.username
                    ),
                    canal="INTERNE",
                )
                
                # Envoyer un email si possible
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
                                expediteur=request.user.get_full_name() or request.user.username
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=True,
                        )
                        print(f"✓ Email envoyé à {user.username} ({user.email})")
                        count += 1
                    except Exception as e:
                        print(f"✗ Erreur envoi email à {user.username}: {e}")
            
            if count > 0:
                messages.success(request, f"✓ {count} utilisateur(s) notifié(s) de l'arrivée du dossier.")
            return count
        
        # Notifier selon l'action
        if action == "transmettre_analyste":
            notifier_utilisateurs(
                UserRoles.ANALYSTE,
                f"🔔 Nouveau dossier à analyser • {dossier.reference}",
                (
                    "🔔 Nouveau message\n"
                    "Référence: {dossier_ref}\n"
                    "Client: {client_name}\n"
                    "Montant: {montant} FCFA\n"
                    "Produit: {produit}\n"
                    "Transmis par: {expediteur}"
                )
            )
        
        elif action == "transmettre_ggr":
            notifier_utilisateurs(
                UserRoles.RESPONSABLE_GGR,
                f"🔔 Dossier à valider • {dossier.reference}",
                (
                    "🔔 Nouveau message\n"
                    "Référence: {dossier_ref}\n"
                    "Client: {client_name}\n"
                    "Montant: {montant} FCFA\n"
                    "Produit: {produit}\n"
                    "Transmis par: {expediteur}"
                )
            )
        
        elif action == "approuver":
            notifier_utilisateurs(
                UserRoles.BOE,
                f"🔔 Dossier approuvé • {dossier.reference}",
                (
                    "🔔 Nouveau message\n"
                    "Référence: {dossier_ref}\n"
                    "Client: {client_name}\n"
                    "Montant: {montant} FCFA\n"
                    "Produit: {produit}\n"
                    "Approuvé par: {expediteur}"
                )
            )
        
        elif action == "retour_gestionnaire":
            notifier_utilisateurs(
                UserRoles.GESTIONNAIRE,
                f"🔔 Dossier retourné • {dossier.reference}",
                (
                    "🔔 Nouveau message\n"
                    "Référence: {dossier_ref}\n"
                    "Client: {client_name}\n"
                    "Montant: {montant} FCFA\n"
                    "Retourné par: {expediteur}"
                )
            )
        
        # Log pour debug
        print(f"? Notification créée: ID={notification.id}, Client={dossier.client.username}, Action={action}")
        
        # Ajouter un message de succès pour le gestionnaire
        if action == "retour_client":
            messages.info(request, f"? Notification envoyée au client {dossier.client.username}")
        if dossier.client.email:
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
            # Préparer le template HTML pour retour client
            html_message = None
            if action == "retour_client":
                try:
                    # URL du logo
                    logo_url = request.build_absolute_uri(static('suivi_demande/img/Credit_Du_Congo.png'))
                    site_url = request.build_absolute_uri('/')
                    
                    html_message = render_to_string('emails/retour_client.html', {
                        'dossier': dossier,
                        'commentaire_retour': commentaire_retour,
                        'logo_url': logo_url,
                        'site_url': site_url,
                    })
                except Exception as e:
                    print(f"Erreur lors de la génération de l'email HTML: {e}")
                    html_message = None
            try:
                send_mail(
                    subject=subject,
                    message=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[dossier.client.email],
                    fail_silently=False,  # Ne pas ignorer les erreurs
                    html_message=html_message,
                )
                print(f"? Email envoyé à {dossier.client.email} pour action {action}")
                if action == "retour_client":
                    messages.info(request, f"?? Email envoyé à {dossier.client.email}")
            except Exception as e:
                print(f"? Erreur envoi email: {e}")
                messages.warning(request, f"?? Erreur lors de l'envoi de l'email: {e}")
    except Exception as e:
        print(f"? Erreur notification: {e}")
        messages.error(request, f"? Erreur lors de la création de la notification: {e}")

    # Message de succès personnalisé selon l'action
    if action == "retour_client":
        messages.success(request, f"Le dossier {dossier.reference} a été retourné au client avec vos commentaires.")
    else:
        messages.success(request, "Transition effectuée avec succès.")
    
    namespace = get_current_namespace(request)
    return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

@login_required
def dossier_detail(request, pk):

    dossier = get_object_or_404(DossierCredit, pk=pk)
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)

    # Accès: le client ne peut voir que ses propres dossiers; les autres rôles peuvent consulter.
    if role == UserRoles.CLIENT and dossier.client_id != request.user.id:
        messages.error(request, "Accès refusé au dossier demandé.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    # Marquer les notifications liées au dossier comme lues (sans champ FK: match sur la référence)
    try:
        Notification.objects.filter(
            utilisateur_cible=request.user,
            lu=False,
        ).filter(
            Q(titre__icontains=dossier.reference) | Q(message__icontains=dossier.reference)
        ).update(lu=True)
    except Exception:
        pass

    # Permissions centralisées
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
                messages.success(request, "Commentaire ajouté.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)
        elif action == "upload_piece":
            if not can_upload:
                messages.error(request, "Vous ne pouvez pas déposer de pièce à ce stade.")
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

            f = request.FILES.get("fichier")
            type_piece = request.POST.get("type_piece") or "AUTRE"
            if not f:
                messages.error(request, "Aucun fichier sélectionné.")
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)
            # Validation taille
            file_size = getattr(f, "size", 0) or 0
            if file_size > getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024):
                max_mb = round(getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024) / (1024 * 1024), 2)
                messages.error(request, f"Fichier trop volumineux. Taille maximale autorisée: {max_mb} Mo.")
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)
            # Validation extension
            filename = getattr(f, "name", "")
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            allowed_exts = getattr(settings, "UPLOAD_ALLOWED_EXTS", {"pdf", "jpg", "jpeg", "png"})
            if ext not in allowed_exts:
                messages.error(request, f"Extension de fichier non autorisée ({ext}). Autorisées: {', '.join(sorted(allowed_exts))}.")
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)
            # Taille et type de base (MVP). On pourrait filtrer extensions ici.
            pj = PieceJointe.objects.create(
                dossier=dossier,
                fichier=f,
                type_piece=type_piece,
                taille=getattr(f, "size", 0) or 0,
                upload_by=request.user,
            )
            messages.success(request, "Pièce jointe téléchargée.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:dossier_detail", pk=dossier.pk)

    pieces = PieceJointe.objects.filter(dossier=dossier).order_by("-upload_at")
    commentaires = Commentaire.objects.filter(dossier=dossier).order_by("-created_at")
    journal = JournalAction.objects.filter(dossier=dossier).order_by("-timestamp")

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


@login_required
def notifications_list(request):

    qs = Notification.objects.filter(utilisateur_cible=request.user).order_by("-created_at")
    return render(request, "suivi_demande/notifications.html", {"notifications": qs})


@login_required
def notifications_mark_all_read(request):

    if request.method == "POST":
        Notification.objects.filter(utilisateur_cible=request.user, lu=False).update(lu=True)
        messages.success(request, "Toutes vos notifications ont Ã©tÃ© marquÃ©es comme lues.")
    namespace = get_current_namespace(request)
    return redirect(f"{namespace}:notifications_list")


@login_required
def notifications_mark_read(request, pk: int):

    if request.method == "POST":
        notif = get_object_or_404(Notification, pk=pk, utilisateur_cible=request.user)
        if not notif.lu:
            notif.lu = True
            notif.save(update_fields=["lu"])
        # Redirige vers la page prÃ©cÃ©dente si fournie
        namespace = get_current_namespace(request)
        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect(f"{namespace}:notifications_list")
    namespace = get_current_namespace(request)
    return redirect(f"{namespace}:notifications_list")


# --- Demande de crÃ©dit: Wizard ---

@login_required
def demande_start(request):
    # Réinitialiser la session
    request.session["demande_wizard"] = {}
    
    # Vérifier si le profil utilisateur est complet
    user_profile = getattr(request.user, 'profile', None)
    profile_complete = False
    
    if user_profile:
        # Vérifier si les informations essentielles sont présentes
        required_fields = ['telephone', 'adresse', 'date_naissance']
        profile_complete = all(getattr(user_profile, field, None) for field in required_fields)
    
    # Si profil complet, pré-remplir les données et aller à la vérification
    if profile_complete:
        # Pré-remplir les données de l'étape 1 avec les infos du profil
        step1_data = {
            'nom': request.user.last_name or '',
            'prenom': request.user.first_name or '',
            'date_naissance': user_profile.date_naissance.isoformat() if user_profile.date_naissance else '',
            'lieu_naissance': getattr(user_profile, 'lieu_naissance', ''),
            'nationalite': getattr(user_profile, 'nationalite', ''),
            'situation_familiale': getattr(user_profile, 'situation_familiale', ''),
            'nb_personnes_charge': getattr(user_profile, 'nb_personnes_charge', 0),
            'adresse': user_profile.adresse or '',
            'ville': getattr(user_profile, 'ville', ''),
            'pays': getattr(user_profile, 'pays', ''),
            'telephone': user_profile.telephone or '',
            'email': request.user.email or '',
            'cni': getattr(user_profile, 'cni', ''),
        }
        
        request.session["demande_wizard"] = {"step1": step1_data}
        request.session["profile_prefilled"] = True
        request.session.modified = True
        
        # Rediriger vers la page de vérification
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:demande_verification")
    else:
        # Profil incomplet, aller au formulaire classique
        request.session["profile_prefilled"] = False
        request.session.modified = True
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:demande_step1")


@login_required
def demande_verification(request):
    """
    Étape de vérification rapide pour les clients avec profil complet
    """
    data = request.session.get("demande_wizard", {})
    step1_data = data.get("step1", {})
    
    if not step1_data:
        # Pas de données pré-remplies, rediriger vers le début
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:demande_start")
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "confirm":
            # Utilisateur confirme les données, passer à l'étape 2
            messages.success(request, "Informations confirmées. Passons aux détails du crédit.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:demande_step2")
            
        elif action == "modify":
            # Utilisateur veut modifier, aller au formulaire complet
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:demande_step1")
            
        elif action == "update_profile":
            # Mettre à jour le profil avec les nouvelles données si modifiées
            form = DemandeStep1Form(request.POST)
            if form.is_valid():
                # Sauvegarder dans la session
                cleaned = form.cleaned_data.copy()
                dn = cleaned.get('date_naissance')
                try:
                    if isinstance(dn, (date, datetime)):
                        cleaned['date_naissance'] = dn.isoformat()
                except Exception:
                    pass
                
                data["step1"] = serialize_form_data(cleaned)
                request.session["demande_wizard"] = data
                request.session.modified = True
                
                # Optionnellement mettre à jour le profil utilisateur
                if request.POST.get("update_user_profile"):
                    user_profile = getattr(request.user, 'profile', None)
                    if user_profile:
                        user_profile.telephone = cleaned.get('numero_telephone', user_profile.telephone)
                        user_profile.adresse = cleaned.get('adresse_exacte', user_profile.adresse)
                        user_profile.save()
                        messages.success(request, "Votre profil a été mis à jour.")
                
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:demande_step2")
    
    # Préparer le formulaire avec les données pré-remplies
    form = DemandeStep1Form(initial=step1_data)
    
    ctx = {
        "form": form,
        "step1_data": step1_data,
        "step": "verification",
        "total_steps": 4,
        "profile_prefilled": True,
    }
    return render(request, "suivi_demande/demande_verification.html", ctx)


@login_required
def demande_step1(request):
    data = request.session.get("demande_wizard", {})
    initial = data.get("step1", {})
    
    # Si pas de données initiales et profil utilisateur disponible, pré-remplir
    if not initial and not request.session.get("profile_prefilled", False):
        user_profile = getattr(request.user, 'profile', None)
        if user_profile:
            full_name = (user_profile.full_name or '').strip() if hasattr(user_profile, 'full_name') else ''
            if not full_name:
                full_name = (request.user.get_full_name() or f"{request.user.last_name} {request.user.first_name}").strip()
            initial = {
                'nom_prenom': full_name,
                'numero_telephone': getattr(user_profile, 'telephone', ''),
                'adresse_exacte': getattr(user_profile, 'adresse', ''),
            }
            request.session["profile_prefilled"] = True
            request.session.modified = True
    if request.method == "POST":
        form = DemandeStep1Form(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data.copy()
            dn = cleaned.get('date_naissance')
            try:
                if isinstance(dn, (date, datetime)):
                    cleaned['date_naissance'] = dn.isoformat()
            except Exception:
                pass
            data["step1"] = serialize_form_data(cleaned)
            request.session["demande_wizard"] = data
            request.session.modified = True
            messages.success(request, "Ã‰tape 1 enregistrÃ©e.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:demande_step2")
    else:
        form = DemandeStep1Form(initial=initial)
    ctx = {
        "form": form,
        "step": 1,
        "total_steps": 4,
    }
    return render(request, "suivi_demande/demande_step1.html", ctx)


@login_required
def demande_step2(request):

    data = request.session.get("demande_wizard", {})
    initial = data.get("step2", {})
    if request.method == "POST":
        form = DemandeStep2Form(request.POST)
        if form.is_valid():
            data["step2"] = serialize_form_data(form.cleaned_data)
            request.session["demande_wizard"] = data
            request.session.modified = True
            messages.success(request, "Ã‰tape 2 enregistrÃ©e.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:demande_step3")
    else:
        form = DemandeStep2Form(initial=initial)
    ctx = {
        "form": form,
        "step": 2,
        "total_steps": 4,
    }
    return render(request, "suivi_demande/demande_step2.html", ctx)


@login_required
def demande_step3(request):
    data = request.session.get("demande_wizard", {})
    initial = data.get("step3", {})
    step2 = data.get("step2", {})

    def annuite_mensuelle(montant, taux_percent, duree_mois):
        try:
            P = float(montant)
            n = int(duree_mois)
            r = float(taux_percent) / 100.0 / 12.0
            if n <= 0:
                return 0.0
            if r <= 0:
                return round(P / n, 2)
            a = P * r / (1 - (1 + r) ** (-n))
            return round(a, 2)
        except Exception:
            return 0.0

    def capacite_40(step2dict):
        try:
            salaire = float(step2dict.get("salaire_net_moyen_fcfa", 0) or 0)
            # Total des échéances connues en cours
            credits = float(step2dict.get("total_echeances_credits_cours", 0) or 0)
            # Capacité brute 40% du salaire
            brute = max(0.0, salaire * 0.40)
            # Capacité dispo après crédits en cours
            nette = max(0.0, brute - credits)
            return round(nette, 2)
        except Exception:
            return 0.0

    echeance_calculee = None
    capacite_max = capacite_40(step2)

    if request.method == "POST":
        form = DemandeStep3Form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            echeance_calculee = annuite_mensuelle(cd["demande_montant_fcfa"], cd["demande_taux_pourcent"], cd["demande_duree_mois"])
            if echeance_calculee > capacite_max:
                messages.error(
                    request,
                    f"L'échéance estimée ({echeance_calculee:,.0f} FCFA) dépasse la capacité maximale (40%) de {capacite_max:,.0f} FCFA.",
                )
            else:
                cd["echeance_calculee"] = echeance_calculee
                data["step3"] = serialize_form_data(cd)
                request.session["demande_wizard"] = data
                request.session.modified = True
                messages.success(request, "Étape 3 enregistrée.")
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:demande_step4")
    else:
        form = DemandeStep3Form(initial=initial)
        if initial.get("demande_montant_fcfa") and initial.get("demande_taux_pourcent") and initial.get("demande_duree_mois"):
            echeance_calculee = annuite_mensuelle(initial.get("demande_montant_fcfa"), initial.get("demande_taux_pourcent"), initial.get("demande_duree_mois"))

    def map_items(step_dict: dict, labels: dict):
        items = []
        # preserve label ordering first
        for k, lbl in labels.items():
            if k in step_dict:
                items.append((lbl, step_dict.get(k)))
        # then add remaining keys
        for k, v in step_dict.items():
            if k not in labels:
                lbl = k.replace("_", " ")
                items.append((lbl, v))
        return items

    labels1 = {
        "nom_prenom": "Nom et prénom",
        "date_naissance": "Date de naissance",
        "nationalite": "Nationalité",
        "adresse_exacte": "Adresse exacte",
        "numero_telephone": "Téléphone",
        "emploi_occupe": "Emploi occupé",
        "statut_emploi": "Statut d'emploi",
        "anciennete_emploi": "Ancienneté emploi",
        "type_contrat": "Type de contrat",
        "nom_employeur": "Nom employeur",
        "lieu_emploi": "Lieu d'emploi",
        "employeur_client_banque": "Employeur client banque",
        "radical_employeur": "Radical employeur",
        "situation_famille": "Situation familiale",
        "nombre_personnes_charge": "Personnes à charge",
        "regime_matrimonial": "Régime matrimonial",
        "participation_enquetes": "Participation aux enquêtes",
        "salaire_conjoint": "Salaire conjoint (FCFA)",
        "emploi_conjoint": "Emploi conjoint",
        "statut_logement": "Statut logement",
        "numero_tf": "Numéro TF",
        "radical": "Radical (client)",
        "date_ouverture_compte": "Date ouverture compte",
        "date_domiciliation_salaire": "Date domiciliation salaire",
    }
    labels2 = {
        "salaire_net_moyen_fcfa": "Salaire net moyen (FCFA)",
        "echeances_prets_relevees": "Échéances prêts relevées (FCFA)",
        "total_echeances_credits_cours": "Total échéances crédits en cours (FCFA)",
        "salaire_net_avant_endettement_fcfa": "Salaire net avant endettement (FCFA)",
        "capacite_endettement_brute_fcfa": "Capacité d'endettement brute (FCFA)",
        "capacite_endettement_nette_fcfa": "Capacité d'endettement nette (FCFA)",
    }

    labels3 = {
        "objet_pret": "Objet du prêt",
        "demande_montant_fcfa": "Montant (FCFA)",
        "demande_duree_mois": "Durée (mois)",
        "demande_taux_pourcent": "Taux %",
        "demande_periodicite": "Périodicité",
        "demande_date_1ere_echeance": "Date 1re échéance",
        "demande_montant_echeance_fcfa": "Montant échéance (FCFA)",
        "echeance_calculee": "Échéance estimée (FCFA)",
    }

    recap1 = map_items(data.get("step1", {}), labels1)
    recap2 = map_items(data.get("step2", {}), labels2)
    recap3 = map_items(data.get("step3", {}), labels3)
    initial = data.get("step4", {})

    ctx = {
        "form": form,
        "step": 3,
        "total_steps": 4,
        "echeance_calculee": echeance_calculee,
        "capacite_max": capacite_max,
    }
    return render(request, "suivi_demande/demande_step3.html", ctx)
def demande_step4(request):
    data = request.session.get("demande_wizard", {})
    # Build human-readable recaps (ensure available in all render paths)
    def map_items(step_dict: dict, labels: dict):
        items = []
        for k, lbl in labels.items():
            if k in step_dict:
                items.append((lbl, step_dict.get(k)))
        for k, v in step_dict.items():
            if k not in labels:
                lbl = k.replace("_", " ")
                items.append((lbl, v))
        return items

    labels1 = {
        "nom_prenom": "Nom et prénom",
        "date_naissance": "Date de naissance",
        "nationalite": "Nationalité",
        "adresse_exacte": "Adresse exacte",
        "numero_telephone": "Téléphone",
        "telephone_travail": "Téléphone travail",
        "telephone_domicile": "Téléphone domicile",
        "emploi_occupe": "Emploi occupé",
        "statut_emploi": "Statut d'emploi",
        "anciennete_emploi": "Ancienneté emploi",
        "type_contrat": "Type de contrat",
        "nom_employeur": "Nom employeur",
        "lieu_emploi": "Lieu d'emploi",
        "employeur_client_banque": "Employeur client banque",
        "radical_employeur": "Radical employeur",
        "situation_famille": "Situation familiale",
        "nombre_personnes_charge": "Personnes à charge",
        "regime_matrimonial": "Régime matrimonial",
        "salaire_conjoint": "Salaire conjoint (FCFA)",
        "emploi_conjoint": "Emploi conjoint",
        "statut_logement": "Statut logement",
        "numero_tf": "Numéro TF",
        "logement_autres_precision": "Précision (logement)",
        "radical": "Radical (client)",
        "date_ouverture_compte": "Date ouverture compte",
        "date_domiciliation_salaire": "Date domiciliation salaire",
    }
    labels2 = {
        "salaire_net_moyen_fcfa": "Salaire net moyen (FCFA)",
        "echeances_prets_relevees": "Échéances prêts relevées (FCFA)",
        "total_echeances_credits_cours": "Total échéances crédits en cours (FCFA)",
        "salaire_net_avant_endettement_fcfa": "Salaire net avant endettement (FCFA)",
        "capacite_endettement_brute_fcfa": "Capacité d'endettement brute (FCFA)",
        "capacite_endettement_nette_fcfa": "Capacité d'endettement nette (FCFA)",
    }

    labels3 = {
        "nature_pret": "Type de crédit",
        "motif_credit": "Motif du crédit",
        "demande_montant_fcfa": "Montant (FCFA)",
        "demande_duree_mois": "Durée (mois)",
        "demande_taux_pourcent": "Taux %",
        "demande_periodicite": "Périodicité",
        "demande_date_1ere_echeance": "Date 1re échéance",
        "demande_montant_echeance_fcfa": "Montant échéance (FCFA)",
        "echeance_calculee": "Échéance estimée (FCFA)",
    }

    recap1 = map_items(data.get("step1", {}), labels1)
    recap2 = map_items(data.get("step2", {}), labels2)
    recap3 = map_items(data.get("step3", {}), labels3)
    initial = data.get("step4", {})

    if request.method == "POST":
        form = DemandeStep4Form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Étape 4: toutes les pièces sont obligatoires
            cni = request.FILES.get("cni")
            fiche = request.FILES.get("fiche_paie")
            releve = request.FILES.get("releve_bancaire")
            billet_ordre_f = request.FILES.get("billet_ordre")
            attestation_emp_f = request.FILES.get("attestation_employeur")
            attestation_dom_f = request.FILES.get("attestation_domiciliation")
            assurance_f = request.FILES.get("assurance_deces_invalidite")

            # Validation fichiers
            def validate_file(f):
                size = getattr(f, "size", 0) or 0
                if size > getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024):
                    max_mb = round(getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024) / (1024 * 1024), 2)
                    return f"Fichier trop volumineux (> {max_mb} Mo)"
                name = getattr(f, "name", "")
                ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
                allowed = getattr(settings, "UPLOAD_ALLOWED_EXTS", {"pdf", "jpg", "jpeg", "png"})
                if ext not in allowed:
                    return f"Extension non autorisée ({ext}). Autorisées: {', '.join(sorted(allowed))}."
                return None

            # Exiger la présence de toutes les pièces
            missing = []
            required_files = [
                ("Carte d'identité (CNI)", cni),
                ("Fiche de paie", fiche),
                ("Relevé bancaire", releve),
                ("Billet à ordre", billet_ordre_f),
                ("Attestation de l'employeur", attestation_emp_f),
                ("Attestation de domiciliation irrévocable", attestation_dom_f),
                ("Assurance décès-invalidité", assurance_f),
            ]
            for label, f in required_files:
                if not f:
                    missing.append(label)
            if missing:
                messages.error(request, "Veuillez joindre: " + ", ".join(missing) + ".")
                return render(request, "suivi_demande/demande_step4.html", {"form": form, "step": 4, "total_steps": 4, "recap": data, "recap1": recap1, "recap2": recap2, "recap3": recap3})

            # Valider tous les fichiers
            for label, f in required_files:
                err = validate_file(f)
                if err:
                    messages.error(request, f"{label}: {err}")
                    return render(request, "suivi_demande/demande_step4.html", {"form": form, "step": 4, "total_steps": 4, "recap": data, "recap1": recap1, "recap2": recap2, "recap3": recap3})

            # Créer le dossier à partir du wizard (MVP)
            step3 = data.get("step3", {})
            montant = step3.get("demande_montant_fcfa") or 0

            try:
                montant = Decimal(str(montant))
            except Exception:
                montant = Decimal("0")

            # Générer une référence simple (unique)
            ref = f"DOS-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"
            produit = "Crédit"

            # Déterminer l'utilisateur client à assigner au dossier
            client_user = request.user
            try:
                step1_data = data.get("step1", {})
                allow_follow = bool(step1_data.get("permettre_suivi_client"))
                client_user_id = step1_data.get("client_user_id")
                if allow_follow and client_user_id:
                    client_user = User.objects.get(pk=int(client_user_id))
            except Exception:
                client_user = request.user

            dossier = DossierCredit.objects.create(
                client=client_user,
                reference=ref,
                produit=produit,
                montant=montant,
                statut_agent=DossierStatutAgent.NOUVEAU,
                statut_client=DossierStatutClient.EN_ATTENTE,
                acteur_courant=request.user,
            )

            # Mettre à jour l'état du wizard et le consentement (Étape 4)
            try:
                dossier.wizard_current_step = 4
                dossier.wizard_completed = True
                dossier.consent_accepted = bool(cd.get("accepter_conditions", False))
                dossier.consent_accepted_at = timezone.now() if dossier.consent_accepted else None
                dossier.save(update_fields=[
                    "wizard_current_step",
                    "wizard_completed",
                    "consent_accepted",
                    "consent_accepted_at",
                ])
            except Exception:
                pass

            # Persister le canevas avec les données des étapes 1 à 3
            step1 = data.get("step1", {})
            step2 = data.get("step2", {})
            step3 = data.get("step3", {})
            try:
                # Normaliser les dates issues des steps (si chaînes)
                def _d(v):
                    if not v:
                        return None
                    if hasattr(v, 'year'):
                        return v
                    return parse_date(str(v))
                CanevasProposition.objects.create(
                    dossier=dossier,
                    # En-tête par défaut gardé (agence, code, etc.)
                    nom_prenom=step1.get("nom_prenom", ""),
                    date_naissance=_d(step1.get("date_naissance", None)),
                    nationalite=step1.get("nationalite", "CONGOLAISE"),
                    adresse_exacte=step1.get("adresse_exacte", ""),
                    numero_telephone=step1.get("numero_telephone", ""),
                    telephone_travail=step1.get("telephone_travail", ""),
                    telephone_domicile=step1.get("telephone_domicile", ""),
                    radical=step1.get("radical", ""),
                    date_ouverture_compte=_d(step1.get("date_ouverture_compte", None)),
                    date_domiciliation_salaire=_d(step1.get("date_domiciliation_salaire", None)),
                    emploi_occupe=step1.get("emploi_occupe", ""),
                    statut_emploi=step1.get("statut_emploi", "PRIVE"),
                    anciennete_emploi=step1.get("anciennete_emploi", ""),
                    type_contrat=step1.get("type_contrat", "CDI"),
                    nom_employeur=step1.get("nom_employeur", ""),
                    lieu_emploi=step1.get("lieu_emploi", ""),
                    employeur_client_banque=bool(step1.get("employeur_client_banque", False)),
                    radical_employeur=step1.get("radical_employeur", ""),
                    situation_famille=step1.get("situation_famille", "MARIE"),
                    nombre_personnes_charge=int(step1.get("nombre_personnes_charge", 0) or 0),
                    regime_matrimonial=step1.get("regime_matrimonial", ""),
                    participation_enquetes=step1.get("participation_enquetes", ""),
                    salaire_conjoint=step1.get("salaire_conjoint", 0) or 0,
                    emploi_conjoint=step1.get("emploi_conjoint", ""),
                    statut_logement=step1.get("statut_logement", ""),
                    numero_tf=step1.get("numero_tf", ""),
                    logement_autres_precision=step1.get("logement_autres_precision", ""),
                    # Nature du prêt en cours
                    nature_pret_cours=step1.get("nature_pret_cours", "NOKI") or "NOKI",
                    montant_origine_fcfa=step1.get("montant_origine_fcfa", 0) or 0,
                    date_derniere_echeance=_d(step1.get("date_derniere_echeance", None)),
                    montant_echeance_fcfa=step1.get("montant_echeance_fcfa", 0) or 0,
                    k_restant_du_fcfa=step1.get("k_restant_du_fcfa", 0) or 0,
                    # Section 2
                    salaire_net_moyen_fcfa=step2.get("salaire_net_moyen_fcfa", 0) or 0,
                    echeances_prets_relevees=step2.get("echeances_prets_relevees", 0) or 0,
                    total_echeances_credits_cours=step2.get("total_echeances_credits_cours", 0) or 0,
                    salaire_net_avant_endettement_fcfa=step2.get("salaire_net_avant_endettement_fcfa", 0) or 0,
                    capacite_endettement_brute_fcfa=step2.get("capacite_endettement_brute_fcfa", 0) or 0,
                    capacite_endettement_nette_fcfa=step2.get("capacite_endettement_nette_fcfa", 0) or 0,
                    # Section 3
                    nature_pret=step3.get("nature_pret", "PRET") or "PRET",
                    motif_credit=step3.get("motif_credit", ""),
                    demande_montant_fcfa=step3.get("demande_montant_fcfa", 0) or 0,
                    demande_duree_mois=int(step3.get("demande_duree_mois", 0) or 0),
                    demande_taux_pourcent=step3.get("demande_taux_pourcent", 0) or 0,
                    demande_periodicite=step3.get("demande_periodicite", "M"),
                    demande_montant_echeance_fcfa=step3.get("demande_montant_echeance_fcfa", 0) or 0,
                    demande_date_1ere_echeance=_d(step3.get("demande_date_1ere_echeance", None)),
                )
            except Exception as e:
                print(f"[ERROR] Sauvegarde CanevasProposition échouée: {e}")
                print(traceback.format_exc())
                messages.warning(request, f"Le récapitulatif du dossier n'a pas pu être créé. Erreur: {e}")

            # Journal crÃ©ation
            JournalAction.objects.create(
                dossier=dossier,
                action="CREATION",
                de_statut=None,
                vers_statut=DossierStatutAgent.NOUVEAU,
                acteur=request.user,
                commentaire_systeme="CrÃ©ation du dossier depuis le wizard Demande",
                meta={"wizard": True},
            )

            # Enregistrer les piÃ¨ces jointes
            try:
                # Enregistrer toutes les pièces obligatoires
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=cni,
                    type_piece="CNI",
                    taille=getattr(cni, "size", 0) or 0,
                    upload_by=request.user,
                )
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=fiche,
                    type_piece="FICHE_PAIE",
                    taille=getattr(fiche, "size", 0) or 0,
                    upload_by=request.user,
                )
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=releve,
                    type_piece="RELEVE_BANCAIRE",
                    taille=getattr(releve, "size", 0) or 0,
                    upload_by=request.user,
                )
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=billet_ordre_f,
                    type_piece="BILLET_ORDRE",
                    taille=getattr(billet_ordre_f, "size", 0) or 0,
                    upload_by=request.user,
                )
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=attestation_emp_f,
                    type_piece="ATTESTATION_EMPLOYEUR",
                    taille=getattr(attestation_emp_f, "size", 0) or 0,
                    upload_by=request.user,
                )
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=attestation_dom_f,
                    type_piece="ATTESTATION_DOMICILIATION",
                    taille=getattr(attestation_dom_f, "size", 0) or 0,
                    upload_by=request.user,
                )
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=assurance_f,
                    type_piece="ASSURANCE_DECES_INVALIDITE",
                    taille=getattr(assurance_f, "size", 0) or 0,
                    upload_by=request.user,
                )
            except Exception:
                messages.warning(request, "Pièces jointes non enregistrées, vous pourrez les ajouter depuis le dossier.")

            # Notification client
            try:
                Notification.objects.create(
                    utilisateur_cible=request.user,
                    type="DOSSIER_MAJ",
                    titre=f"Votre demande a Ã©tÃ© crÃ©Ã©e ({dossier.reference})",
                    message="Votre dossier a Ã©tÃ© crÃ©Ã© et transmis au gestionnaire.",
                    canal="INTERNE",
                )
                if request.user.email:
                    subject = f"[GGR] Demande crÃ©Ã©e: {dossier.reference}"
                    text_message = (
                        f"Bonjour,\n\nVotre demande a Ã©tÃ© crÃ©Ã©e avec la rÃ©fÃ©rence {dossier.reference}. "
                        f"Vous serez notifiÃ© des prochaines Ã©tapes.\n\nCeci est un message automatique."
                    )
                    html_message = render_to_string(
                        "emails/dossier_update_client.html",
                        {
                            "dossier": dossier,
                            "client": request.user,
                            "statut_client": dossier.get_statut_client_display(),
                            "logo_url": request.build_absolute_uri(static('suivi_demande/img/Credit_Du_Congo.png')),
                            "lien": request.build_absolute_uri(
                                redirect("dossier_detail", pk=dossier.pk).url
                            ),
                        },
                    )
                    send_mail(
                        subject=subject,
                        message=text_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[request.user.email],
                        fail_silently=True,
                        html_message=html_message,
                    )
            except Exception:
                pass

            # Nettoyer la session wizard
            try:
                del request.session["demande_wizard"]
            except KeyError:
                pass
            request.session.modified = True

            messages.success(request, "Demande soumise avec succès. Vous pouvez maintenant transmettre le dossier à l'analyste.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:transmettre_analyste_page", pk=dossier.pk)
    else:
        form = DemandeStep4Form(initial=initial)
    ctx = {
        "form": form,
        "step": 4,
        "total_steps": 4,
        "recap": data,
        "recap1": recap1,
        "recap2": recap2,
        "recap3": recap3,
    }
    return render(request, "suivi_demande/demande_step4.html", ctx)


@login_required
def transmettre_analyste_page(request, pk: int):
    dossier = get_object_or_404(DossierCredit, pk=pk)
    ctx = {
        "dossier": dossier,
    }
    return render(request, "suivi_demande/transmettre_analyste.html", ctx)


# === Vues d'administration ===

@login_required
def admin_users(request):
    """Vue d'administration pour gérer les utilisateurs et leurs rôles."""
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)
    
    # Seuls les SUPER_ADMIN peuvent accéder
    if role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Accès refusé. Droits administrateur requis.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")
    
    # Récupérer tous les utilisateurs avec leurs profils
    users_data = []
    for user in User.objects.all().order_by('username'):
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = None
        
        users_data.append({
            'user': user,
            'profile': profile
        })
    
    context = {
        'users': users_data,
        'roles': UserRoles.choices
    }
    return render(request, "suivi_demande/admin_users.html", context)


@login_required
def admin_change_role(request):
    """Changer le rôle d'un utilisateur."""
    if request.method != "POST":
        return redirect("admin_users")
    
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)
    
    # Seuls les SUPER_ADMIN peuvent modifier les rôles
    if role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Accès refusé. Droits administrateur requis.")
        return redirect("dashboard")
    
    user_id = request.POST.get('user_id')
    new_role = request.POST.get('role')
    
    try:
        user = User.objects.get(id=user_id)
        
        # Créer ou mettre à jour le profil
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'full_name': user.get_full_name() or user.username,
                'phone': '',
                'address': '',
                'role': new_role
            }
        )
        
        if not created:
            profile.role = new_role
            profile.save()
        
        messages.success(request, f"Rôle de {user.username} modifié vers {dict(UserRoles.choices)[new_role]}")
        
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la modification: {e}")
    
    return redirect("admin_users")


@login_required
def admin_activate_user(request, user_id):
    """Activer un utilisateur."""
    if request.method != "POST":
        return redirect("admin_users")
    
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)
    
    # Seuls les SUPER_ADMIN peuvent activer des utilisateurs
    if role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Accès refusé. Droits administrateur requis.")
        return redirect("dashboard")
    
    try:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        
        messages.success(request, f"Utilisateur {user.username} activé avec succès.")
        
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    except Exception as e:
        messages.error(request, f"Erreur lors de l'activation: {e}")
    
    return redirect("admin_users")


# =============================================================================
# VUES DE TEST POUR DIAGNOSTIQUER LES NOTIFICATIONS
# =============================================================================

@login_required
def test_notification_view(request):
    """Vue pour tester les notifications"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_test_notification':
            try:
                # Créer une notification de test
                notification = Notification.objects.create(
                    utilisateur_cible=request.user,
                    type="TEST",
                    titre="Test de notification",
                    message="Ceci est une notification de test créée manuellement.",
                    canal="INTERNE"
                )
                messages.success(request, f"? Notification de test créée (ID: {notification.id})")
            except Exception as e:
                messages.error(request, f"? Erreur: {e}")
        
        elif action == 'list_notifications':
            # Lister les notifications de l'utilisateur
            notifications = Notification.objects.filter(
                utilisateur_cible=request.user
            ).order_by('-created_at')[:10]
            
            context = {
                'notifications': notifications,
                'count': notifications.count()
            }
            return render(request, 'core/test_notifications.html', context)
    
    # Statistiques
    total_notifications = Notification.objects.filter(utilisateur_cible=request.user).count()
    unread_notifications = Notification.objects.filter(utilisateur_cible=request.user, lu=False).count()
    
    # Derniers dossiers de l'utilisateur (si client)
    dossiers = []
    if hasattr(request.user, 'profile') and request.user.profile.role == 'CLIENT':
        dossiers = DossierCredit.objects.filter(client=request.user).order_by('-date_soumission')[:5]
    
    context = {
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'dossiers': dossiers,
    }
    
    return render(request, 'core/test_notifications.html', context)


def test_notification_api(request):
    """API pour tester les notifications en AJAX"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    # Récupérer les notifications récentes
    notifications = Notification.objects.filter(
        utilisateur_cible=request.user
    ).order_by('-created_at')[:5]
    
    data = {
        'notifications': [
            {
                'id': n.id,
                'titre': n.titre,
                'message': n.message,
                'lu': n.lu,
                'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
                'type': n.type
            }
            for n in notifications
        ],
        'count': notifications.count(),
        'unread_count': Notification.objects.filter(utilisateur_cible=request.user, lu=False).count()
    }
    
    return JsonResponse(data)

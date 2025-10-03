# core/views.py
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.templatetags.static import static
from decimal import Decimal
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.db.models import Sum

from .forms import CreditApplicationForm, SignupForm
from .forms_demande import DemandeStep1Form, DemandeStep2Form
from .forms_demande_extra import DemandeStep3Form, DemandeStep4Form
from .models import (
    CreditApplication,
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    JournalAction,
    Notification,
    UserRoles,
    UserProfile,
    Commentaire,
    PieceJointe,
)
from .permissions import can_upload_piece, get_transition_flags
from .decorators import transition_allowed
from django.contrib.auth import get_user_model
from django.templatetags.static import static
from django.http import JsonResponse

User = get_user_model()


def home(request):
    return render(request, "home.html")


@login_required
def my_applications(request):
    # Afficher les dossiers créés via le wizard de demande
    dossiers = DossierCredit.objects.filter(client=request.user).order_by("-date_soumission")
    return render(request, "suivi_demande/my_applications.html", {"dossiers": dossiers})


@login_required
def create_application(request):
    if request.method == "POST":
        form = CreditApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.client = request.user
            app.status = "DRAFT"
            app.save()
            messages.success(request, "Dossier crÃ©Ã© avec succÃ¨s.")
            return redirect("my_applications")
    else:
        form = CreditApplicationForm()
    return render(request, "suivi_demande/create_application.html", {"form": form})


@login_required
def edit_application(request, pk):
    app = get_object_or_404(CreditApplication, pk=pk, client=request.user)
    if request.method == "POST":
        form = CreditApplicationForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, "Dossier modifiÃ© avec succÃ¨s.")
            return redirect("my_applications")
    else:
        form = CreditApplicationForm(instance=app)
    return render(request, "suivi_demande/edit_application.html", {"form": form, "application": app})


@login_required
def delete_application(request, pk):
    app = get_object_or_404(CreditApplication, pk=pk, client=request.user)
    if request.method == "POST":
        app.delete()
        messages.success(request, "Dossier supprimÃ© avec succÃ¨s.")
        return redirect("my_applications")
    return render(request, "suivi_demande/confirm_delete.html", {"application": app})


def signup(request):

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                "Votre compte a Ã©tÃ© crÃ©Ã©. Il sera activÃ© aprÃ¨s approbation par un administrateur.",
            )
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def pending_approval(request):

    if request.user.is_active:
        return redirect("dashboard")
    return render(request, "accounts/pending_approval.html")


@login_required
def dashboard(request):
    # Dashboard par rôle basé sur DossierCredit.
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)
    
    # Si pas de profil, créer un profil CLIENT par défaut
    if profile is None:
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
        'profile_exists': profile is not None,
        'role': role,
        'template_to_use': None
    }

    if role == UserRoles.CLIENT:
        debug_info['template_to_use'] = 'dashboard_client.html'
        dossiers = DossierCredit.objects.filter(client=request.user).order_by("-date_soumission")
        dossiers_approuves = dossiers.filter(statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS).count()
        montant_total = dossiers.aggregate(total=Sum('montant'))['total'] or 0
        context = {
            "mes_dossiers": dossiers,
            # compat
            "dossiers": dossiers,
            "dossiers_approuves": dossiers_approuves,
            "montant_total": montant_total,
            "debug_info": debug_info,
        }
        return render(request, "suivi_demande/dashboard_client.html", context)

    elif role == UserRoles.GESTIONNAIRE:
        # Dossiers dans le scope gestionnaire
        # En attente: Nouveaux ou RetournÃ©s vers le gestionnaire
        dossiers_pending = DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.NOUVEAU,
                DossierStatutAgent.TRANSMIS_RESP_GEST
            ]
        ).order_by("-date_soumission")

        # Dossiers rÃ©cents (les 5 derniers)
        recents = DossierCredit.objects.all().order_by("-date_soumission")[:5]

        # KPI simples
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
            statut_agent__in=[DossierStatutAgent.EN_COURS_VALIDATION_GGR, DossierStatutAgent.EN_ATTENTE_DECISION_DG]
        )
        en_attente_total = en_attente_qs.count()
        en_attente_today = en_attente_qs.filter(date_soumission__date=today).count()

        try:
            import statistics
            delais = []
            now = timezone.now()
            for d in DossierCredit.objects.order_by("-date_soumission")[:20]:
                if d.date_soumission:
                    delta = now - d.date_soumission
                    delais.append(delta.total_seconds() / 86400.0)
            delai_moyen_jours = round(statistics.mean(delais), 1) if delais else "â€”"
            variation_semaine = 0  # placeholder
        except Exception:
            delai_moyen_jours = "â€”"
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

        # Fournir des variables attendues par le template (dynamiques)
        dossiers_en_cours = DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.NOUVEAU,
                DossierStatutAgent.TRANSMIS_RESP_GEST,
                DossierStatutAgent.TRANSMIS_ANALYSTE,
                DossierStatutAgent.EN_COURS_ANALYSE,
            ]
        ).order_by("-date_soumission")

        from datetime import date
        today_date = timezone.now().date()
        dossiers_ce_mois = DossierCredit.objects.filter(
            date_soumission__year=today_date.year,
            date_soumission__month=today_date.month,
        ).count()

        approuves = DossierCredit.objects.filter(statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS).count()
        refuses = DossierCredit.objects.filter(statut_agent=DossierStatutAgent.REFUSE).count()
        total_decides = approuves + refuses
        taux_validation = round((approuves / total_decides) * 100, 1) if total_decides else 0

        portefeuille_total = DossierCredit.objects.aggregate(total=Sum('montant'))['total'] or 0

        dossiers_urgents = list(dossiers_pending[:5])
        mes_clients = []  # À brancher plus tard si relation de portefeuille

        debug_info['template_to_use'] = 'dashboard_gestionnaire.html'
        ctx = {
            "dossiers_pending": dossiers_pending,
            "recents": recents,
            "kpi": kpi,
            "dossiers": dossiers_en_cours,
            "dossiers_en_cours": dossiers_en_cours,
            "dossiers_urgents": dossiers_urgents,
            "dossiers_ce_mois": dossiers_ce_mois,
            "taux_validation": taux_validation,
            "portefeuille_total": portefeuille_total,
            "mes_clients": mes_clients,
            "debug_info": debug_info,
        }
        return render(request, "suivi_demande/dashboard_gestionnaire.html", ctx)

    elif role == UserRoles.ANALYSTE:
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=[DossierStatutAgent.TRANSMIS_ANALYSTE, DossierStatutAgent.EN_COURS_ANALYSE]
        ).order_by("-date_soumission")
        return render(request, "suivi_demande/dashboard_analyste.html", {"dossiers": dossiers})

    elif role == UserRoles.RESPONSABLE_GGR:
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=[DossierStatutAgent.EN_COURS_VALIDATION_GGR, DossierStatutAgent.EN_ATTENTE_DECISION_DG]
        ).order_by("-date_soumission")
        return render(request, "suivi_demande/dashboard_responsable_ggr_pro.html", {"dossiers": dossiers})

    elif role == UserRoles.BOE:
        dossiers = DossierCredit.objects.filter(
            statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS
        ).order_by("-date_soumission")
        return render(request, "suivi_demande/dashboard_boe.html", {"dossiers": dossiers})

    else:
        dossiers = DossierCredit.objects.all().order_by("-date_soumission")[:100]
        return render(request, "suivi_demande/dashboard_super_admin.html", {"dossiers": dossiers})





@login_required
@transition_allowed
def transition_dossier(request, pk, action: str):
    """Effectue une transition d'état sur un dossier en fonction du rôle et de l'action."""
    if request.method != "POST":
        messages.error(request, "Méthode non autorisée.")
        return redirect("dashboard")

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
                    return redirect("dossier_detail", pk=dossier.pk)
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
        return redirect("dashboard")

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
            message_notification = f"Votre dossier nécessite des compléments. Motif: {commentaire_retour}"
            titre_notification = f"Dossier {dossier.reference} - Compléments requis"
        else:
            message_notification = f"Nouveau statut: {dossier.get_statut_client_display()}."
            titre_notification = f"Votre dossier {dossier.reference} a été mis à jour"
        
        # Créer la notification
        notification = Notification.objects.create(
            utilisateur_cible=dossier.client,
            type="DOSSIER_MAJ",
            titre=titre_notification,
            message=message_notification,
            canal="INTERNE",
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
                    from django.template.loader import render_to_string
                    from django.contrib.staticfiles import finders
                    
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
    
    return redirect("dossier_detail", pk=dossier.pk)

@login_required
def dossier_detail(request, pk):

    dossier = get_object_or_404(DossierCredit, pk=pk)
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)

    # AccÃ¨s: le client ne peut voir que ses propres dossiers; les autres rÃ´les peuvent consulter.
    if role == UserRoles.CLIENT and dossier.client_id != request.user.id:
        messages.error(request, "AccÃ¨s refusÃ© au dossier demandÃ©.")
        return redirect("dashboard")

    # Permissions centralisÃ©es
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
                messages.success(request, "Commentaire ajoutÃ©.")
            return redirect("dossier_detail", pk=dossier.pk)
        elif action == "upload_piece":
            if not can_upload:
                messages.error(request, "Vous ne pouvez pas dÃ©poser de piÃ¨ce Ã  ce stade.")
                return redirect("dossier_detail", pk=dossier.pk)

            f = request.FILES.get("fichier")
            type_piece = request.POST.get("type_piece") or "AUTRE"
            if not f:
                messages.error(request, "Aucun fichier sÃ©lectionnÃ©.")
                return redirect("dossier_detail", pk=dossier.pk)
            # Validation taille
            file_size = getattr(f, "size", 0) or 0
            if file_size > getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024):
                max_mb = round(getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024) / (1024 * 1024), 2)
                messages.error(request, f"Fichier trop volumineux. Taille maximale autorisÃ©e: {max_mb} Mo.")
                return redirect("dossier_detail", pk=dossier.pk)
            # Validation extension
            filename = getattr(f, "name", "")
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            allowed_exts = getattr(settings, "UPLOAD_ALLOWED_EXTS", {"pdf", "jpg", "jpeg", "png"})
            if ext not in allowed_exts:
                messages.error(request, f"Extension de fichier non autorisÃ©e ({ext}). AutorisÃ©es: {', '.join(sorted(allowed_exts))}.")
                return redirect("dossier_detail", pk=dossier.pk)
            # Taille et type de base (MVP). On pourrait filtrer extensions ici.
            pj = PieceJointe.objects.create(
                dossier=dossier,
                fichier=f,
                type_piece=type_piece,
                taille=getattr(f, "size", 0) or 0,
                upload_by=request.user,
            )
            messages.success(request, "PiÃ¨ce jointe tÃ©lÃ©chargÃ©e.")
            return redirect("dossier_detail", pk=dossier.pk)

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
    return redirect("notifications_list")


@login_required
def notifications_mark_read(request, pk: int):

    if request.method == "POST":
        notif = get_object_or_404(Notification, pk=pk, utilisateur_cible=request.user)
        if not notif.lu:
            notif.lu = True
            notif.save(update_fields=["lu"])
        # Redirige vers la page prÃ©cÃ©dente si fournie
        return redirect(request.POST.get("next") or "notifications_list")
    return redirect("notifications_list")


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
        return redirect("demande_verification")
    else:
        # Profil incomplet, aller au formulaire classique
        request.session["profile_prefilled"] = False
        request.session.modified = True
        return redirect("demande_step1")


@login_required
def demande_verification(request):
    """
    Étape de vérification rapide pour les clients avec profil complet
    """
    data = request.session.get("demande_wizard", {})
    step1_data = data.get("step1", {})
    
    if not step1_data:
        # Pas de données pré-remplies, rediriger vers le début
        return redirect("demande_start")
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "confirm":
            # Utilisateur confirme les données, passer à l'étape 2
            messages.success(request, "Informations confirmées. Passons aux détails du crédit.")
            return redirect("demande_step2")
            
        elif action == "modify":
            # Utilisateur veut modifier, aller au formulaire complet
            return redirect("demande_step1")
            
        elif action == "update_profile":
            # Mettre à jour le profil avec les nouvelles données si modifiées
            form = DemandeStep1Form(request.POST)
            if form.is_valid():
                # Sauvegarder dans la session
                cleaned = form.cleaned_data.copy()
                dn = cleaned.get('date_naissance')
                try:
                    from datetime import date, datetime
                    if isinstance(dn, (date, datetime)):
                        cleaned['date_naissance'] = dn.isoformat()
                except Exception:
                    pass
                
                data["step1"] = cleaned
                request.session["demande_wizard"] = data
                request.session.modified = True
                
                # Optionnellement mettre à jour le profil utilisateur
                if request.POST.get("update_user_profile"):
                    user_profile = getattr(request.user, 'profile', None)
                    if user_profile:
                        user_profile.telephone = cleaned.get('telephone', user_profile.telephone)
                        user_profile.adresse = cleaned.get('adresse', user_profile.adresse)
                        user_profile.ville = cleaned.get('ville', getattr(user_profile, 'ville', ''))
                        user_profile.save()
                        messages.success(request, "Votre profil a été mis à jour.")
                
                return redirect("demande_step2")
    
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
            initial = {
                'nom': request.user.last_name or '',
                'prenom': request.user.first_name or '',
                'email': request.user.email or '',
                'telephone': getattr(user_profile, 'telephone', ''),
                'adresse': getattr(user_profile, 'adresse', ''),
                'ville': getattr(user_profile, 'ville', ''),
                'cni': getattr(user_profile, 'cni', ''),
            }
            request.session["profile_prefilled"] = True
            request.session.modified = True
    if request.method == "POST":
        form = DemandeStep1Form(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data.copy()
            dn = cleaned.get('date_naissance')
            try:
                from datetime import date, datetime
                if isinstance(dn, (date, datetime)):
                    cleaned['date_naissance'] = dn.isoformat()
            except Exception:
                pass
            data["step1"] = cleaned
            request.session["demande_wizard"] = data
            request.session.modified = True
            messages.success(request, "Ã‰tape 1 enregistrÃ©e.")
            return redirect("demande_step2")
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
            data["step2"] = form.cleaned_data
            request.session["demande_wizard"] = data
            request.session.modified = True
            messages.success(request, "Ã‰tape 2 enregistrÃ©e.")
            return redirect("demande_step3")
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
            salaire = float(step2dict.get("salaire_net_moyen", 0) or 0)
            autres = float(step2dict.get("autres_revenus", 0) or 0)
            charges = float(step2dict.get("charges_mensuelles", 0) or 0)
            # Nouveaux champs: si has_credits == 'OUI', prendre les mensualitÃ©s totales
            credits = 0.0
            try:
                if step2dict.get('has_credits') == 'OUI':
                    credits = float(step2dict.get('mensualites_totales', 0) or 0)
            except Exception:
                credits = 0.0
            dispo = max(0.0, salaire + autres - charges - credits)
            return round(dispo * 0.40, 2)
        except Exception:
            return 0.0

    echeance_calculee = None
    capacite_max = capacite_40(step2)

    if request.method == "POST":
        form = DemandeStep3Form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            echeance_calculee = annuite_mensuelle(cd["montant_demande"], cd["taux"], cd["duree_mois"])
            if echeance_calculee > capacite_max:
                messages.error(
                    request,
                    f"L'Ã©chÃ©ance estimÃ©e ({echeance_calculee:,.0f} FCFA) dÃ©passe la capacitÃ© maximale (40%) de {capacite_max:,.0f} FCFA.",
                )
            else:
                cd["echeance_calculee"] = echeance_calculee
                data["step3"] = cd
                request.session["demande_wizard"] = data
                request.session.modified = True
                messages.success(request, "Ã‰tape 3 enregistrÃ©e.")
                return redirect("demande_step4")
    else:
        form = DemandeStep3Form(initial=initial)
        if initial.get("montant_demande") and initial.get("taux") and initial.get("duree_mois"):
            echeance_calculee = annuite_mensuelle(initial.get("montant_demande"), initial.get("taux"), initial.get("duree_mois"))

    ctx = {
        "form": form,
        "step": 3,
        "total_steps": 4,
        "echeance_calculee": echeance_calculee,
        "capacite_max": capacite_max,
    }
    return render(request, "suivi_demande/demande_step3.html", ctx)


@login_required
def demande_step4(request):
    data = request.session.get("demande_wizard", {})
    # Build human-readable recaps
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
        "nom": "Nom",
        "prenom": "PrÃ©nom",
        "date_naissance": "Date de naissance",
        "lieu_naissance": "Lieu de naissance",
        "nationalite": "NationalitÃ©",
        "situation_familiale": "Situation familiale",
        "nb_personnes_charge": "Personnes Ã  charge",
        "adresse": "Adresse",
        "ville": "Ville",
        "pays": "Pays",
        "telephone": "TÃ©lÃ©phone",
        "email": "Email",
    }
    labels2 = {
        "statut_emploi": "Situation professionnelle",
        "employeur_nom": "Nom de l'employeur",
        "poste_occupe": "Poste occupÃ©",
        "anciennete": "AnciennetÃ©",
        "salaire_net_moyen": "Revenu mensuel net (FCFA)",
        "autres_revenus": "Autres revenus mensuels (FCFA)",
        "charges_mensuelles": "DÃ©penses mensuelles (FCFA)",
        "has_credits": "CrÃ©dits en cours",
        "montant_total_credits": "Montant total des crÃ©dits (FCFA)",
        "mensualites_totales": "MensualitÃ©s totales (FCFA)",
    }

    labels3 = {
        "nature_pret": "Nature du prÃªt",
        "objet": "Objet du prÃªt",
        "montant_demande": "Montant (FCFA)",
        "duree_mois": "DurÃ©e (mois)",
        "taux": "Taux %",
        "periodicite": "PÃ©riodicitÃ©",
        "date_premiere_echeance": "Date 1re Ã©chÃ©ance",
        "echeance_calculee": "Ã‰chÃ©ance estimÃ©e (FCFA)",
    }

    recap1 = map_items(data.get("step1", {}), labels1)
    recap2 = map_items(data.get("step2", {}), labels2)
    recap3 = map_items(data.get("step3", {}), labels3)
    initial = data.get("step4", {})
    if request.method == "POST":
        form = DemandeStep4Form(request.POST)
        if form.is_valid():
            data["step4"] = form.cleaned_data
            # Valider la prÃ©sence des fichiers requis
            cni = request.FILES.get("cni")
            fiche = request.FILES.get("fiche_paie")
            releve = request.FILES.get("releve_bancaire")
            missing = []
            if not cni:
                missing.append("Carte d'identitÃ© (CNI)")
            if not fiche:
                missing.append("Fiche de paie")
            if not releve:
                missing.append("RelevÃ© bancaire")
            if missing:
                messages.error(request, "Veuillez joindre les documents obligatoires: " + ", ".join(missing) + ".")
                return render(request, "suivi_demande/demande_step4.html", {"form": form, "step": 4, "total_steps": 4, "recap": data, "recap1": recap1, "recap2": recap2, "recap3": recap3})

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
                    return f"Extension non autorisÃ©e ({ext}). AutorisÃ©es: {', '.join(sorted(allowed))}."
                return None

            for label, f in [("CNI", cni), ("Fiche de paie", fiche), ("RelevÃ© bancaire", releve)]:
                err = validate_file(f)
                if err:
                    messages.error(request, f"{label}: {err}")
                    return render(request, "suivi_demande/demande_step4.html", {"form": form, "step": 4, "total_steps": 4, "recap": data, "recap1": recap1, "recap2": recap2, "recap3": recap3})

            # CrÃ©er le dossier Ã  partir du wizard (MVP)
            step3 = data.get("step3", {})
            montant = step3.get("montant_demande") or 0
            try:
                montant = Decimal(str(montant))
            except Exception:
                montant = Decimal("0")

            # GÃ©nÃ©rer une rÃ©fÃ©rence simple (unique)
            ref = f"DOS-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"
            produit = step3.get("nature_pret") or "CrÃ©dit"

            dossier = DossierCredit.objects.create(
                client=request.user,
                reference=ref,
                produit=produit,
                montant=montant,
                statut_agent=DossierStatutAgent.NOUVEAU,
                statut_client=DossierStatutClient.EN_ATTENTE,
                acteur_courant=request.user,
            )

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
            except Exception:
                messages.warning(request, "PiÃ¨ces jointes non enregistrÃ©es, vous pourrez les ajouter depuis le dossier.")

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

            messages.success(request, "Demande sou mise avec succÃ¨s.")
            return redirect("dossier_detail", pk=dossier.pk)
    else:
        form = DemandeStep4Form(initial=initial)
    ctx = {
        "form": form,
        "step": 4,
        "total_steps": 4,
        "recap": data,
    }
    return render(request, "suivi_demande/demande_step4.html", ctx)


# === Vues d'administration ===

@login_required
def admin_users(request):
    """Vue d'administration pour gérer les utilisateurs et leurs rôles."""
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)
    
    # Seuls les SUPER_ADMIN peuvent accéder
    if role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Accès refusé. Droits administrateur requis.")
        return redirect("dashboard")
    
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


@login_required
def test_retour_simple(request):
    """Page de test simplifiée pour le retour client"""
    
    # Récupérer les dossiers éligibles
    dossiers = DossierCredit.objects.filter(
        statut_agent__in=['NOUVEAU', 'TRANSMIS_RESP_GEST']
    ).order_by('-date_soumission')[:10]
    
    # Récupérer les notifications récentes
    notifications = Notification.objects.all().order_by('-created_at')[:10]
    
    context = {
        'dossiers': dossiers,
        'notifications': notifications,
    }
    
    return render(request, 'core/test_retour_simple.html', context)


@login_required
def debug_direct(request):
    """Page de debug ultra-simple pour identifier le problème exact"""
    
    debug_messages = []
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'test_notification':
            # Test simple de création de notification
            try:
                notification = Notification.objects.create(
                    utilisateur_cible=request.user,
                    type="DEBUG_TEST",
                    titre="Test Debug Direct",
                    message="Cette notification a été créée depuis la page de debug direct.",
                    canal="INTERNE"
                )
                debug_messages.append(f"? Notification créée avec succès ! ID: {notification.id}")
                messages.success(request, f"? Notification créée ! ID: {notification.id}")
            except Exception as e:
                debug_messages.append(f"? Erreur création notification: {e}")
                messages.error(request, f"? Erreur: {e}")
        
        elif action == 'test_retour':
            # Test de retour client direct
            dossier_id = request.POST.get('dossier_id')
            commentaire_retour = request.POST.get('commentaire_retour', 'Test direct')
            
            try:
                dossier = DossierCredit.objects.get(pk=dossier_id)
                debug_messages.append(f"?? Dossier trouvé: {dossier.reference}")
                
                # Vérifier le rôle
                profile = getattr(request.user, 'profile', None)
                role = getattr(profile, 'role', None)
                debug_messages.append(f"?? Rôle utilisateur: {role}")
                
                if role != UserRoles.GESTIONNAIRE:
                    debug_messages.append(f"? PROBLÈME: Rôle {role} != GESTIONNAIRE")
                    messages.error(request, f"? Votre rôle ({role}) n'est pas GESTIONNAIRE")
                else:
                    # Créer la notification directement
                    notification = Notification.objects.create(
                        utilisateur_cible=dossier.client,
                        type="RETOUR_TEST",
                        titre=f"Test Retour Dossier {dossier.reference}",
                        message=f"Test de retour: {commentaire_retour}",
                        canal="INTERNE"
                    )
                    debug_messages.append(f"? Notification créée pour {dossier.client.username} ! ID: {notification.id}")
                    messages.success(request, f"? Notification créée pour {dossier.client.username} !")
                    
                    # Créer l'entrée dans le journal
                    JournalAction.objects.create(
                        dossier=dossier,
                        action="RETOUR_CLIENT_TEST",
                        de_statut=dossier.statut_agent,
                        vers_statut=dossier.statut_agent,
                        acteur=request.user,
                        commentaire_systeme=f"Test direct: {commentaire_retour}",
                    )
                    debug_messages.append(f"? Journal d'action créé")
                    
            except DossierCredit.DoesNotExist:
                debug_messages.append(f"? Dossier {dossier_id} introuvable")
                messages.error(request, f"? Dossier introuvable")
            except Exception as e:
                debug_messages.append(f"? Erreur test retour: {e}")
                messages.error(request, f"? Erreur: {e}")
    
    # Récupérer les données pour affichage
    dossiers = DossierCredit.objects.all().order_by('-date_soumission')[:5]
    notifications = Notification.objects.all().order_by('-created_at')[:10]
    
    context = {
        'dossiers': dossiers,
        'notifications': notifications,
        'debug_messages': debug_messages,
    }
    
    return render(request, 'core/debug_direct.html', context)


@login_required
def force_retour_client(request, pk):
    """Vue de test qui force le retour client sans validation"""
    
    if request.method != 'POST':
        messages.error(request, "Méthode non autorisée")
        return redirect('dashboard')
    
    try:
        dossier = DossierCredit.objects.get(pk=pk)
        commentaire = request.POST.get('commentaire_retour', 'Test forcé sans validation')
        
        # Message de debug
        messages.info(request, f"?? FORCE TEST: Tentative de retour pour {dossier.reference}")
        
        # Créer la notification directement SANS validation
        notification = Notification.objects.create(
            utilisateur_cible=dossier.client,
            type="RETOUR_FORCE",
            titre=f"[TEST FORCÉ] Dossier {dossier.reference} - Compléments requis",
            message=f"Votre dossier nécessite des compléments. Motif: {commentaire}",
            canal="INTERNE"
        )
        
        # Créer l'entrée journal
        JournalAction.objects.create(
            dossier=dossier,
            action="RETOUR_CLIENT_FORCE",
            de_statut=dossier.statut_agent,
            vers_statut=dossier.statut_agent,  # Pas de changement de statut
            acteur=request.user,
            commentaire_systeme=f"Test forcé: {commentaire}",
        )
        
        messages.success(request, f"? SUCCÈS! Notification créée (ID: {notification.id}) pour {dossier.client.username}")
        messages.info(request, f"?? Le client {dossier.client.username} devrait voir cette notification")
        
        # Essayer d'envoyer un email simple
        if dossier.client.email:
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                send_mail(
                    subject=f"[TEST] Dossier {dossier.reference} - Compléments requis",
                    message=f"Test d'email automatique.\n\nMotif: {commentaire}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[dossier.client.email],
                    fail_silently=False,
                )
                messages.success(request, f"?? Email envoyé à {dossier.client.email}")
            except Exception as e:
                messages.warning(request, f"?? Erreur email: {e}")
        else:
            messages.warning(request, f"?? Client {dossier.client.username} n'a pas d'email")
            
    except DossierCredit.DoesNotExist:
        messages.error(request, "Dossier introuvable")
    except Exception as e:
        messages.error(request, f"? Erreur: {e}")
    
    return redirect('dashboard')


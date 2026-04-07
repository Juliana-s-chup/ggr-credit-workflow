"""
Vues du wizard de demande de credit (4 etapes).

Etape 1 : Informations personnelles du demandeur
Etape 2 : Capacite d'endettement
Etape 3 : Details du credit demande
Etape 4 : Recapitulatif, pieces jointes et soumission
"""

import logging
from datetime import date, datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils import timezone
from django.utils.dateparse import parse_date

from ..forms_demande import DemandeStep1Form, DemandeStep2Form, DemandeStep3Form, DemandeStep4Form
from ..models import (
    DossierCredit,
    DossierStatutAgent,
    DossierStatutClient,
    JournalAction,
    Notification,
    PieceJointe,
    CanevasProposition,
)
from ..utils import get_current_namespace
from .helpers import serialize_form_data

User = get_user_model()
logger = logging.getLogger("suivi_demande")


# ---------------------------------------------------------------------------
# Labels pour le recapitulatif (etape 4)
# ---------------------------------------------------------------------------

LABELS_STEP1 = {
    "nom_prenom": "Nom et prenom",
    "date_naissance": "Date de naissance",
    "nationalite": "Nationalite",
    "adresse_exacte": "Adresse exacte",
    "numero_telephone": "Telephone",
    "telephone_travail": "Telephone travail",
    "telephone_domicile": "Telephone domicile",
    "emploi_occupe": "Emploi occupe",
    "statut_emploi": "Statut d'emploi",
    "anciennete_emploi": "Anciennete emploi",
    "type_contrat": "Type de contrat",
    "nom_employeur": "Nom employeur",
    "lieu_emploi": "Lieu d'emploi",
    "employeur_client_banque": "Employeur client banque",
    "radical_employeur": "Radical employeur",
    "situation_famille": "Situation familiale",
    "nombre_personnes_charge": "Personnes a charge",
    "regime_matrimonial": "Regime matrimonial",
    "salaire_conjoint": "Salaire conjoint (FCFA)",
    "emploi_conjoint": "Emploi conjoint",
    "statut_logement": "Statut logement",
    "numero_tf": "Numero TF",
    "logement_autres_precision": "Precision (logement)",
    "radical": "Radical (client)",
    "date_ouverture_compte": "Date ouverture compte",
    "date_domiciliation_salaire": "Date domiciliation salaire",
}

LABELS_STEP2 = {
    "salaire_net_moyen_fcfa": "Salaire net moyen (FCFA)",
    "echeances_prets_relevees": "Echeances prets relevees (FCFA)",
    "total_echeances_credits_cours": "Total echeances credits en cours (FCFA)",
    "salaire_net_avant_endettement_fcfa": "Salaire net avant endettement (FCFA)",
    "capacite_endettement_brute_fcfa": "Capacite d'endettement brute (FCFA)",
    "capacite_endettement_nette_fcfa": "Capacite d'endettement nette (FCFA)",
}

LABELS_STEP3 = {
    "nature_pret": "Type de credit",
    "motif_credit": "Motif du credit",
    "demande_montant_fcfa": "Montant (FCFA)",
    "demande_duree_mois": "Duree (mois)",
    "demande_taux_pourcent": "Taux %",
    "demande_periodicite": "Periodicite",
    "demande_date_1ere_echeance": "Date 1re echeance",
    "demande_montant_echeance_fcfa": "Montant echeance (FCFA)",
    "echeance_calculee": "Echeance estimee (FCFA)",
}


# ---------------------------------------------------------------------------
# Fonctions utilitaires du wizard
# ---------------------------------------------------------------------------


def _map_items(step_dict, labels):
    """Transforme un dictionnaire de donnees en liste (label, valeur) pour le recap."""
    items = []
    for k, lbl in labels.items():
        if k in step_dict:
            items.append((lbl, step_dict.get(k)))
    for k, v in step_dict.items():
        if k not in labels:
            lbl = k.replace("_", " ")
            items.append((lbl, v))
    return items


def _annuite_mensuelle(montant, taux_percent, duree_mois):
    """Calcule l'annuite mensuelle d'un pret."""
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


def _capacite_40(step2dict):
    """Calcule la capacite d'endettement nette (40% du salaire - credits en cours)."""
    try:
        salaire = float(step2dict.get("salaire_net_moyen_fcfa", 0) or 0)
        credits = float(step2dict.get("total_echeances_credits_cours", 0) or 0)
        brute = max(0.0, salaire * 0.40)
        nette = max(0.0, brute - credits)
        return round(nette, 2)
    except Exception:
        return 0.0


def _validate_file(f):
    """Valide la taille et l'extension d'un fichier uploade."""
    size = getattr(f, "size", 0) or 0
    max_bytes = getattr(settings, "UPLOAD_MAX_BYTES", 5 * 1024 * 1024)
    if size > max_bytes:
        max_mb = round(max_bytes / (1024 * 1024), 2)
        return f"Fichier trop volumineux (> {max_mb} Mo)"
    name = getattr(f, "name", "")
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    allowed = getattr(settings, "UPLOAD_ALLOWED_EXTS", {"pdf", "jpg", "jpeg", "png"})
    if ext not in allowed:
        return f"Extension non autorisee ({ext}). Autorisees: {', '.join(sorted(allowed))}."
    return None


# ---------------------------------------------------------------------------
# Vues du wizard
# ---------------------------------------------------------------------------


@login_required
def demande_start(request):
    """Point d'entree du wizard : reinitialise la session et redirige."""
    request.session["demande_wizard"] = {}

    user_profile = getattr(request.user, "profile", None)
    profile_complete = False

    if user_profile:
        required_fields = ["telephone", "adresse", "date_naissance"]
        profile_complete = all(
            getattr(user_profile, field, None) for field in required_fields
        )

    if profile_complete:
        step1_data = {
            "nom": request.user.last_name or "",
            "prenom": request.user.first_name or "",
            "date_naissance": (
                user_profile.date_naissance.isoformat()
                if user_profile.date_naissance
                else ""
            ),
            "lieu_naissance": getattr(user_profile, "lieu_naissance", ""),
            "nationalite": getattr(user_profile, "nationalite", ""),
            "situation_familiale": getattr(user_profile, "situation_familiale", ""),
            "nb_personnes_charge": getattr(user_profile, "nb_personnes_charge", 0),
            "adresse": user_profile.adresse or "",
            "ville": getattr(user_profile, "ville", ""),
            "pays": getattr(user_profile, "pays", ""),
            "telephone": user_profile.telephone or "",
            "email": request.user.email or "",
            "cni": getattr(user_profile, "cni", ""),
        }

        request.session["demande_wizard"] = {"step1": step1_data}
        request.session["profile_prefilled"] = True
        request.session.modified = True

        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:demande_verification")
    else:
        request.session["profile_prefilled"] = False
        request.session.modified = True
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:demande_step1")


@login_required
def demande_verification(request):
    """Etape de verification rapide pour les clients avec profil complet."""
    data = request.session.get("demande_wizard", {})
    step1_data = data.get("step1", {})

    if not step1_data:
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:demande_start")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "confirm":
            messages.success(request, "Informations confirmees. Passons aux details du credit.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:demande_step2")

        elif action == "modify":
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:demande_step1")

        elif action == "update_profile":
            form = DemandeStep1Form(request.POST)
            if form.is_valid():
                cleaned = form.cleaned_data.copy()
                dn = cleaned.get("date_naissance")
                try:
                    if isinstance(dn, (date, datetime)):
                        cleaned["date_naissance"] = dn.isoformat()
                except Exception:
                    pass

                data["step1"] = serialize_form_data(cleaned)
                request.session["demande_wizard"] = data
                request.session.modified = True

                if request.POST.get("update_user_profile"):
                    user_profile = getattr(request.user, "profile", None)
                    if user_profile:
                        user_profile.telephone = cleaned.get(
                            "numero_telephone", user_profile.telephone
                        )
                        user_profile.adresse = cleaned.get(
                            "adresse_exacte", user_profile.adresse
                        )
                        user_profile.save()
                        messages.success(request, "Votre profil a ete mis a jour.")

                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:demande_step2")

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
    """Etape 1 : Informations personnelles du demandeur."""
    data = request.session.get("demande_wizard", {})
    initial = data.get("step1", {})

    if not initial and not request.session.get("profile_prefilled", False):
        user_profile = getattr(request.user, "profile", None)
        if user_profile:
            full_name = (
                (user_profile.full_name or "").strip()
                if hasattr(user_profile, "full_name")
                else ""
            )
            if not full_name:
                full_name = (
                    request.user.get_full_name()
                    or f"{request.user.last_name} {request.user.first_name}"
                ).strip()
            initial = {
                "nom_prenom": full_name,
                "numero_telephone": getattr(user_profile, "telephone", ""),
                "adresse_exacte": getattr(user_profile, "adresse", ""),
            }
            request.session["profile_prefilled"] = True
            request.session.modified = True

    if request.method == "POST":
        form = DemandeStep1Form(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data.copy()
            dn = cleaned.get("date_naissance")
            try:
                if isinstance(dn, (date, datetime)):
                    cleaned["date_naissance"] = dn.isoformat()
            except Exception:
                pass
            data["step1"] = serialize_form_data(cleaned)
            request.session["demande_wizard"] = data
            request.session.modified = True
            messages.success(request, "Etape 1 enregistree.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:demande_step2")
    else:
        form = DemandeStep1Form(initial=initial)

    ctx = {"form": form, "step": 1, "total_steps": 4}
    return render(request, "suivi_demande/demande_step1.html", ctx)


@login_required
def demande_step2(request):
    """Etape 2 : Capacite d'endettement."""
    data = request.session.get("demande_wizard", {})
    initial = data.get("step2", {})

    if request.method == "POST":
        form = DemandeStep2Form(request.POST)
        if form.is_valid():
            data["step2"] = serialize_form_data(form.cleaned_data)
            request.session["demande_wizard"] = data
            request.session.modified = True
            messages.success(request, "Etape 2 enregistree.")
            namespace = get_current_namespace(request)
            return redirect(f"{namespace}:demande_step3")
    else:
        form = DemandeStep2Form(initial=initial)

    ctx = {"form": form, "step": 2, "total_steps": 4}
    return render(request, "suivi_demande/demande_step2.html", ctx)


@login_required
def demande_step3(request):
    """Etape 3 : Details du credit demande."""
    data = request.session.get("demande_wizard", {})
    initial = data.get("step3", {})
    step2 = data.get("step2", {})

    echeance_calculee = None
    capacite_max = _capacite_40(step2)

    if request.method == "POST":
        form = DemandeStep3Form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            echeance_calculee = _annuite_mensuelle(
                cd["demande_montant_fcfa"],
                cd["demande_taux_pourcent"],
                cd["demande_duree_mois"],
            )
            if echeance_calculee > capacite_max:
                messages.error(
                    request,
                    f"L'echeance estimee ({echeance_calculee:,.0f} FCFA) depasse la capacite maximale (40%) de {capacite_max:,.0f} FCFA.",
                )
            else:
                cd["echeance_calculee"] = echeance_calculee
                data["step3"] = serialize_form_data(cd)
                request.session["demande_wizard"] = data
                request.session.modified = True
                messages.success(request, "Etape 3 enregistree.")
                namespace = get_current_namespace(request)
                return redirect(f"{namespace}:demande_step4")
    else:
        form = DemandeStep3Form(initial=initial)
        if (
            initial.get("demande_montant_fcfa")
            and initial.get("demande_taux_pourcent")
            and initial.get("demande_duree_mois")
        ):
            echeance_calculee = _annuite_mensuelle(
                initial.get("demande_montant_fcfa"),
                initial.get("demande_taux_pourcent"),
                initial.get("demande_duree_mois"),
            )

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
    """Etape 4 : Recapitulatif, pieces jointes et soumission finale."""
    data = request.session.get("demande_wizard", {})

    recap1 = _map_items(data.get("step1", {}), LABELS_STEP1)
    recap2 = _map_items(data.get("step2", {}), LABELS_STEP2)
    recap3 = _map_items(data.get("step3", {}), LABELS_STEP3)
    initial = data.get("step4", {})

    if request.method == "POST":
        form = DemandeStep4Form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Recuperer les fichiers
            files_map = {
                "Carte d'identite (CNI)": request.FILES.get("cni"),
                "Fiche de paie": request.FILES.get("fiche_paie"),
                "Releve bancaire": request.FILES.get("releve_bancaire"),
                "Billet a ordre": request.FILES.get("billet_ordre"),
                "Attestation de l'employeur": request.FILES.get("attestation_employeur"),
                "Attestation de domiciliation irrevocable": request.FILES.get("attestation_domiciliation"),
                "Assurance deces-invalidite": request.FILES.get("assurance_deces_invalidite"),
            }

            # Verifier que tous les fichiers sont presents
            missing = [label for label, f in files_map.items() if not f]
            if missing:
                messages.error(request, "Veuillez joindre: " + ", ".join(missing) + ".")
                return render(
                    request,
                    "suivi_demande/demande_step4.html",
                    {"form": form, "step": 4, "total_steps": 4, "recap": data, "recap1": recap1, "recap2": recap2, "recap3": recap3},
                )

            # Valider chaque fichier
            for label, f in files_map.items():
                err = _validate_file(f)
                if err:
                    messages.error(request, f"{label}: {err}")
                    return render(
                        request,
                        "suivi_demande/demande_step4.html",
                        {"form": form, "step": 4, "total_steps": 4, "recap": data, "recap1": recap1, "recap2": recap2, "recap3": recap3},
                    )

            # Creer le dossier
            dossier = _create_dossier_from_wizard(request, data, cd)

            # Enregistrer les pieces jointes
            _save_wizard_pieces(request, dossier, files_map)

            # Notification
            _notify_wizard_completion(request, dossier)

            # Nettoyer la session
            try:
                del request.session["demande_wizard"]
            except KeyError:
                pass
            request.session.modified = True

            messages.success(
                request,
                "Demande soumise avec succes. Vous pouvez maintenant transmettre le dossier a l'analyste.",
            )
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


# ---------------------------------------------------------------------------
# Helpers pour l'etape 4
# ---------------------------------------------------------------------------


def _create_dossier_from_wizard(request, data, cleaned_data):
    """Cree un DossierCredit et son CanevasProposition a partir des donnees du wizard."""
    step3 = data.get("step3", {})
    montant = step3.get("demande_montant_fcfa") or 0
    try:
        montant = Decimal(str(montant))
    except Exception:
        montant = Decimal("0")

    ref = f"DOS-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"

    # Determiner le client
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
        produit="credit",
        montant=montant,
        statut_agent=DossierStatutAgent.NOUVEAU,
        statut_client=DossierStatutClient.EN_ATTENTE,
        acteur_courant=request.user,
    )

    # Mettre a jour l'etat du wizard
    try:
        dossier.wizard_current_step = 4
        dossier.wizard_completed = True
        dossier.consent_accepted = bool(cleaned_data.get("accepter_conditions", False))
        dossier.consent_accepted_at = timezone.now() if dossier.consent_accepted else None
        dossier.save(
            update_fields=[
                "wizard_current_step",
                "wizard_completed",
                "consent_accepted",
                "consent_accepted_at",
            ]
        )
    except Exception:
        logger.exception("Erreur mise a jour wizard state")

    # Creer le canevas de proposition
    _create_canevas(dossier, data)

    # Journaliser
    JournalAction.objects.create(
        dossier=dossier,
        action="CREATION",
        de_statut=None,
        vers_statut=DossierStatutAgent.NOUVEAU,
        acteur=request.user,
        commentaire_systeme="Creation du dossier depuis le wizard Demande",
        meta={"wizard": True},
    )

    return dossier


def _create_canevas(dossier, data):
    """Cree le CanevasProposition a partir des donnees du wizard."""
    step1 = data.get("step1", {})
    step2 = data.get("step2", {})
    step3 = data.get("step3", {})

    def _d(v):
        if not v:
            return None
        if hasattr(v, "year"):
            return v
        return parse_date(str(v))

    try:
        CanevasProposition.objects.create(
            dossier=dossier,
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
            salaire_conjoint=Decimal(str(step1.get("salaire_conjoint", 0) or 0)),
            emploi_conjoint=step1.get("emploi_conjoint", ""),
            statut_logement=step1.get("statut_logement", ""),
            numero_tf=step1.get("numero_tf", ""),
            logement_autres_precision=step1.get("logement_autres_precision", ""),
            salaire_net_moyen_fcfa=Decimal(str(step2.get("salaire_net_moyen_fcfa", 0) or 0)),
            echeances_prets_relevees=Decimal(str(step2.get("echeances_prets_relevees", 0) or 0)),
            total_echeances_credits_cours=Decimal(str(step2.get("total_echeances_credits_cours", 0) or 0)),
            salaire_net_avant_endettement_fcfa=Decimal(str(step2.get("salaire_net_avant_endettement_fcfa", 0) or 0)),
            capacite_endettement_brute_fcfa=Decimal(str(step2.get("capacite_endettement_brute_fcfa", 0) or 0)),
            capacite_endettement_nette_fcfa=Decimal(str(step2.get("capacite_endettement_nette_fcfa", 0) or 0)),
            nature_pret=step3.get("nature_pret", "PRET"),
            motif_credit=step3.get("motif_credit", ""),
            demande_montant_fcfa=Decimal(str(step3.get("demande_montant_fcfa", 0) or 0)),
            demande_duree_mois=int(step3.get("demande_duree_mois", 0) or 0),
            demande_taux_pourcent=Decimal(str(step3.get("demande_taux_pourcent", 0) or 0)),
            demande_periodicite=step3.get("demande_periodicite", "M"),
            demande_montant_echeance_fcfa=Decimal(str(step3.get("demande_montant_echeance_fcfa", 0) or 0)),
            demande_date_1ere_echeance=_d(step3.get("demande_date_1ere_echeance", None)),
        )
    except Exception:
        logger.exception("Erreur lors de la creation du canevas de proposition")


def _save_wizard_pieces(request, dossier, files_map):
    """Enregistre les pieces jointes du wizard."""
    type_mapping = {
        "Carte d'identite (CNI)": "CNI",
        "Fiche de paie": "FICHE_PAIE",
        "Releve bancaire": "RELEVE_BANCAIRE",
        "Billet a ordre": "BILLET_ORDRE",
        "Attestation de l'employeur": "ATTESTATION_EMPLOYEUR",
        "Attestation de domiciliation irrevocable": "ATTESTATION_DOMICILIATION",
        "Assurance deces-invalidite": "ASSURANCE_DECES_INVALIDITE",
    }
    try:
        for label, f in files_map.items():
            if f:
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=f,
                    type_piece=type_mapping.get(label, "AUTRE"),
                    taille=getattr(f, "size", 0) or 0,
                    upload_by=request.user,
                )
    except Exception:
        logger.exception("Erreur lors de l'enregistrement des pieces jointes")
        messages.warning(
            request,
            "Pieces jointes non enregistrees, vous pourrez les ajouter depuis le dossier.",
        )


def _notify_wizard_completion(request, dossier):
    """Envoie les notifications apres la creation d'un dossier via le wizard."""
    try:
        Notification.objects.create(
            utilisateur_cible=request.user,
            type="DOSSIER_MAJ",
            titre=f"Votre demande a ete creee ({dossier.reference})",
            message="Votre dossier a ete cree et transmis au gestionnaire.",
            canal="INTERNE",
        )
        if request.user.email:
            subject = f"[GGR] Demande creee: {dossier.reference}"
            text_message = (
                f"Bonjour,\n\nVotre demande a ete creee avec la reference {dossier.reference}. "
                f"Vous serez notifie des prochaines etapes.\n\nCeci est un message automatique."
            )
            try:
                html_message = render_to_string(
                    "emails/dossier_update_client.html",
                    {
                        "dossier": dossier,
                        "client": request.user,
                        "statut_client": dossier.get_statut_client_display(),
                        "logo_url": request.build_absolute_uri(
                            static("suivi_demande/img/Credit_Du_Congo.png")
                        ),
                    },
                )
            except Exception:
                html_message = None

            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
                html_message=html_message,
            )
    except Exception:
        logger.exception("Erreur notification apres creation wizard")

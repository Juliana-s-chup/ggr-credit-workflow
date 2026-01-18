"""
Vues pour la gestion des utilisateurs et les rapports
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    DossierCredit,
    DossierStatutAgent,
    UserRoles,
    UserProfile,
)

User = get_user_model()


# ==========================================
# GESTION DES UTILISATEURS (SUPER ADMIN)
# ==========================================


@login_required
def admin_toggle_user_status(request, user_id):
    """Activer/Desactiver un utilisateur"""
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Acces refuse. Reserve aux Super Administrateurs.")
        return redirect("pro:dashboard")

    user = get_object_or_404(User, pk=user_id)

    if user == request.user:
        messages.error(request, "Vous ne pouvez pas desactiver votre propre compte.")
        return redirect("pro:dashboard")

    user.is_active = not user.is_active
    user.save()

    statut = "active" if user.is_active else "desactive"
    messages.success(request, f"L'utilisateur {user.username} a ete {statut}.")

    return redirect("pro:dashboard")


@login_required
def admin_change_user_role(request, user_id):
    """Changer le role d'un utilisateur"""
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Acces refuse.")
        return redirect("pro:dashboard")

    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        new_role = request.POST.get("role")
        valid_roles = [choice[0] for choice in UserRoles.choices]
        if new_role not in valid_roles:
            messages.error(request, "Role invalide.")
            return redirect("pro:dashboard")

        user_profile, created = UserProfile.objects.get_or_create(
            user=user, defaults={"role": new_role}
        )

        if not created:
            user_profile.role = new_role
            user_profile.save()

        messages.success(
            request,
            f"Le role de {user.username} a ete change en {user_profile.get_role_display()}.",
        )

    return redirect("pro:dashboard")


@login_required
def admin_edit_user(request, user_id):
    """Modifier un utilisateur existant"""
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Acces refuse. Reserve aux Super Administrateurs.")
        return redirect("pro:dashboard")

    user = get_object_or_404(User, pk=user_id)
    user_profile = getattr(user, "profile", None)

    if request.method == "POST":
        # Recuperer les donnees
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        role = request.POST.get("role", "")
        is_active = request.POST.get("is_active", "1") == "1"
        new_password = request.POST.get("new_password", "").strip()

        # Validations
        if not username:
            messages.error(request, "Le nom d'utilisateur est obligatoire.")
            return redirect("pro:dashboard")

        if not email:
            messages.error(request, "L'email est obligatoire.")
            return redirect("pro:dashboard")

        # Verifier unicite (sauf pour l'utilisateur actuel)
        if User.objects.filter(username=username).exclude(pk=user_id).exists():
            messages.error(request, f"Le nom d'utilisateur '{username}' est deje  utilise.")
            return redirect("pro:dashboard")

        if User.objects.filter(email=email).exclude(pk=user_id).exists():
            messages.error(request, f"L'email '{email}' est deje  utilise.")
            return redirect("pro:dashboard")

        # Valider le role
        if role:
            valid_roles = [choice[0] for choice in UserRoles.choices]
            if role not in valid_roles:
                messages.error(request, "Role invalide.")
                return redirect("pro:dashboard")

        try:
            # Mettre e  jour l'utilisateur
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = is_active

            # Changer le mot de passe si fourni
            if new_password:
                if len(new_password) < 8:
                    messages.error(request, "Le mot de passe doit contenir au moins 8 caracteres.")
                    return redirect("pro:dashboard")
                user.set_password(new_password)

            user.save()

            # Mettre e  jour le profil
            if user_profile:
                if role:
                    user_profile.role = role
                user_profile.full_name = f"{first_name} {last_name}".strip() or username
                user_profile.save()
            elif role:
                # Creer le profil s'il n'existe pas
                UserProfile.objects.create(
                    user=user,
                    role=role,
                    full_name=f"{first_name} {last_name}".strip() or username,
                    phone="",
                    address="",
                )

            messages.success(request, f"âœ… L'utilisateur '{username}' a ete modifie avec succes.")

        except Exception as e:
            messages.error(request, f"âŒ Erreur lors de la modification : {str(e)}")

    return redirect("pro:dashboard")


@login_required
def admin_create_user(request):
    """Creer un nouvel utilisateur"""
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Acces refuse. Reserve aux Super Administrateurs.")
        return redirect("pro:dashboard")

    if request.method == "POST":
        # Recuperer les donnees du formulaire
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")
        role = request.POST.get("role", "")
        is_active = request.POST.get("is_active", "1") == "1"

        # Validations
        if not username:
            messages.error(request, "Le nom d'utilisateur est obligatoire.")
            return redirect("pro:dashboard")

        if not email:
            messages.error(request, "L'email est obligatoire.")
            return redirect("pro:dashboard")

        if not password:
            messages.error(request, "Le mot de passe est obligatoire.")
            return redirect("pro:dashboard")

        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("pro:dashboard")

        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caracteres.")
            return redirect("pro:dashboard")

        if not role:
            messages.error(request, "Le role est obligatoire.")
            return redirect("pro:dashboard")

        valid_roles = [choice[0] for choice in UserRoles.choices]
        if role not in valid_roles:
            messages.error(request, "Role invalide.")
            return redirect("pro:dashboard")

        # Verifier si l'utilisateur existe deje
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Le nom d'utilisateur '{username}' existe deje .")
            return redirect("pro:dashboard")

        if User.objects.filter(email=email).exists():
            messages.error(request, f"L'email '{email}' est deje  utilise.")
            return redirect("pro:dashboard")

        try:
            # Creer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active,
            )

            # Creer le profil
            UserProfile.objects.create(
                user=user,
                role=role,
                full_name=f"{first_name} {last_name}".strip() or username,
                phone="",
                address="",
            )

            messages.success(
                request,
                f"âœ… L'utilisateur '{username}' a ete cree avec succes avec le role {dict(UserRoles.choices)[role]}.",
            )

        except Exception as e:
            messages.error(request, f"âŒ Erreur lors de la creation de l'utilisateur : {str(e)}")

    return redirect("pro:dashboard")


# ==========================================
# RAPPORTS
# ==========================================


@login_required
def generate_report(request):
    """Generer un rapport selon le role"""
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT) if profile else UserRoles.CLIENT

    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")
    statut = request.GET.get("statut")
    periode = request.GET.get("periode")

    # Filtrer selon le role
    if role == UserRoles.CLIENT:
        dossiers = DossierCredit.objects.filter(client=request.user)
        titre = "Mes Dossiers"
    elif role == UserRoles.GESTIONNAIRE:
        dossiers = DossierCredit.objects.all()
        titre = "Tous les Dossiers"
    elif role == UserRoles.ANALYSTE:
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.TRANSMIS_ANALYSTE,
                DossierStatutAgent.EN_COURS_ANALYSE,
            ]
        )
        titre = "Dossiers e  Analyser"
    elif role == UserRoles.RESPONSABLE_GGR:
        dossiers = DossierCredit.objects.filter(
            statut_agent__in=[
                DossierStatutAgent.EN_COURS_VALIDATION_GGR,
                DossierStatutAgent.EN_ATTENTE_DECISION_DG,
            ]
        )
        titre = "Dossiers e  Valider"
    elif role == UserRoles.BOE:
        dossiers = DossierCredit.objects.filter(
            statut_agent=DossierStatutAgent.APPROUVE_ATTENTE_FONDS
        )
        titre = "Dossiers e  Liberer"
    else:  # SUPER_ADMIN
        dossiers = DossierCredit.objects.all()
        titre = "Tous les Dossiers"

    # Filtres de date
    if date_debut:
        dossiers = dossiers.filter(date_soumission__gte=date_debut)
    if date_fin:
        dossiers = dossiers.filter(date_soumission__lte=date_fin)

    # Filtre par statut
    if statut:
        dossiers = dossiers.filter(statut_agent=statut)

    # Filtre par periode
    if periode:
        today = timezone.now().date()
        if periode == "M":  # Mois
            dossiers = dossiers.filter(
                date_soumission__year=today.year, date_soumission__month=today.month
            )
        elif periode == "Y":  # Annee
            dossiers = dossiers.filter(date_soumission__year=today.year)

    dossiers = dossiers.order_by("-date_soumission")

    # Statistiques
    total = dossiers.count()
    montant_total = dossiers.aggregate(total=Sum("montant"))["total"] or 0
    stats_statuts = (
        dossiers.values("statut_agent")
        .annotate(count=Count("id"), montant=Sum("montant"))
        .order_by("-count")
    )

    context = {
        "titre": titre,
        "dossiers": dossiers,
        "total": total,
        "montant_total": montant_total,
        "stats_statuts": stats_statuts,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "statut": statut,
        "periode": periode,
        "role": role,
    }

    return render(request, "rapports/rapport.html", context)

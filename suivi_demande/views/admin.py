"""
Vues d'administration : gestion des utilisateurs et roles.
Reservees au role SUPER_ADMIN.
"""

import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import UserProfile, UserRoles
from ..utils import get_current_namespace

User = get_user_model()
logger = logging.getLogger("suivi_demande")


@login_required
def admin_users(request):
    """Vue d'administration pour gerer les utilisateurs et leurs roles."""
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)

    if role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Acces refuse. Droits administrateur requis.")
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")

    users_data = []
    for user in User.objects.all().order_by("username"):
        try:
            user_profile = user.profile
        except UserProfile.DoesNotExist:
            user_profile = None
        users_data.append({"user": user, "profile": user_profile})

    context = {"users": users_data, "roles": UserRoles.choices}
    return render(request, "suivi_demande/admin_users.html", context)


@login_required
def admin_change_role(request):
    """Changer le role d'un utilisateur."""
    if request.method != "POST":
        return redirect("admin_users")

    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)

    if role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Acces refuse. Droits administrateur requis.")
        return redirect("dashboard")

    user_id = request.POST.get("user_id")
    new_role = request.POST.get("role")

    try:
        user = User.objects.get(id=user_id)
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "full_name": user.get_full_name() or user.username,
                "phone": "",
                "address": "",
                "role": new_role,
            },
        )
        if not created:
            user_profile.role = new_role
            user_profile.save()

        messages.success(
            request,
            f"Role de {user.username} modifie vers {dict(UserRoles.choices)[new_role]}",
        )
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

    if role != UserRoles.SUPER_ADMIN:
        messages.error(request, "Acces refuse. Droits administrateur requis.")
        return redirect("dashboard")

    try:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        messages.success(request, f"Utilisateur {user.username} active avec succes.")
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    except Exception as e:
        messages.error(request, f"Erreur lors de l'activation: {e}")

    return redirect("admin_users")

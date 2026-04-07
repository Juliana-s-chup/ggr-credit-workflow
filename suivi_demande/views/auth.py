"""
Vues d'authentification et d'inscription.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..forms import SignupForm
from ..models import UserProfile, UserRoles
from ..utils import get_current_namespace

logger = logging.getLogger("suivi_demande")


def signup(request):
    """Inscription d'un nouvel utilisateur (client ou professionnel)."""
    portal = (request.GET.get("as") or request.POST.get("as") or "client").lower()
    portal = "pro" if portal in ["pro", "professionnel", "prof"] else "client"

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                profile = getattr(user, "profile", None)
                if profile is None:
                    profile = UserProfile.objects.create(
                        user=user,
                        full_name=user.get_full_name() or user.username,
                        phone="",
                        address="",
                        role=UserRoles.CLIENT,
                    )
                if portal == "pro":
                    selected_role = form.cleaned_data.get("role")
                    allowed_roles = {
                        r for r, _ in UserRoles.choices if r != UserRoles.CLIENT
                    }
                    if selected_role in allowed_roles:
                        profile.role = selected_role
                    else:
                        profile.role = UserRoles.GESTIONNAIRE
                else:
                    profile.role = UserRoles.CLIENT
                profile.save(update_fields=["role"])
            except Exception:
                logger.exception("Erreur lors de la creation du profil utilisateur")

            messages.success(
                request,
                "Votre compte a ete cree. Il sera active apres approbation par un administrateur.",
            )
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form, "portal": portal})


@login_required
def pending_approval(request):
    """Page d'attente d'approbation pour les nouveaux comptes."""
    if request.user.is_active:
        namespace = get_current_namespace(request)
        return redirect(f"{namespace}:dashboard")
    return render(request, "accounts/pending_approval.html")

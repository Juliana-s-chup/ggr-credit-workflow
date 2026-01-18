"""
Vues de base : home, signup, pending_approval.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..forms import SignupForm


def home(request):
    """Page d'accueil."""
    return render(request, "home.html")


def signup(request):
    """Inscription d'un nouveau client."""
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
    """Page d'attente d'approbation."""
    return render(request, "accounts/pending_approval.html")

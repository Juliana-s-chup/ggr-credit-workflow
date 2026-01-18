"""
Vues pour les autorisations ponctuelles.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms_autorisation import AutorisationPonctuelleForm, EngagementLigneFormSet


@login_required
def autorisation_ponctuelle(request):
    if request.method == "POST":
        form = AutorisationPonctuelleForm(request.POST)
        formset = EngagementLigneFormSet(request.POST, prefix="eng")
        if form.is_valid() and formset.is_valid():
            messages.success(request, "Demande d'Autorisation Ponctuelle enregistree (simulation).")
            return redirect("suivi:dashboard")
    else:
        form = AutorisationPonctuelleForm()
        formset = EngagementLigneFormSet(prefix="eng")
    ctx = {
        "form": form,
        "formset": formset,
    }
    return render(request, "suivi_demande/autorisation_ponctuelle.html", ctx)

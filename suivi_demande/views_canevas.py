"""
Vues pour la gestion du Canevas de Proposition NOKI NOKI
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from .models import DossierCredit, CanevasProposition, JournalAction, UserRoles
from .forms_canevas import CanevasPropositionForm


@login_required
def canevas_create_or_edit(request, dossier_id):
    """Créer ou modifier le canevas de proposition pour un dossier."""
    dossier = get_object_or_404(DossierCredit, pk=dossier_id)

    # Vérifier les permissions (Gestionnaire ou Admin)
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", None)
    if role not in (UserRoles.GESTIONNAIRE, UserRoles.SUPER_ADMIN):
        messages.error(request, "Accès refusé. Réservé aux gestionnaires.")
        return redirect("suivi:dossier_detail", pk=dossier_id)

    # Récupérer ou créer le canevas
    try:
        canevas = dossier.canevas
        is_new = False
    except CanevasProposition.DoesNotExist:
        canevas = None
        is_new = True

    if request.method == "POST":
        form = CanevasPropositionForm(request.POST, instance=canevas)
        if form.is_valid():
            canevas = form.save(commit=False)
            if is_new:
                canevas.dossier = dossier

            # Calculer automatiquement la capacité d'endettement
            canevas.calculer_capacite_endettement()
            canevas.save()

            # Journaliser l'action
            JournalAction.objects.create(
                dossier=dossier,
                action="MISE_A_JOUR",
                de_statut=None,
                vers_statut=None,
                acteur=request.user,
                commentaire_systeme=f"Canevas de proposition {'créé' if is_new else 'modifié'}",
            )

            messages.success(
                request,
                f"✓ Canevas de proposition {'créé' if is_new else 'mis à jour'} avec succès.",
            )

            # Si nouveau canevas, rediriger vers upload documents
            if is_new:
                messages.info(
                    request,
                    "Canevas enregistré ! Veuillez maintenant uploader les documents requis.",
                )
                return redirect("suivi:upload_documents", dossier_id=dossier_id)
            else:
                return redirect("suivi:dossier_detail", pk=dossier_id)
        else:
            messages.error(request, "Erreur dans le formulaire. Veuillez corriger les champs.")
    else:
        # Pré-remplir avec les données du dossier et du client
        initial_data = {}
        if is_new:
            initial_data = {
                "nom_prenom": dossier.client.get_full_name() or dossier.client.username,
                "adresse_exacte": getattr(dossier.client.profile, "address", ""),
                "numero_telephone": getattr(dossier.client.profile, "phone", ""),
                "demande_montant_fcfa": dossier.montant,
                "proposition_montant_fcfa": dossier.montant,
                "objet_pret": dossier.produit,
            }
        form = CanevasPropositionForm(instance=canevas, initial=initial_data if is_new else None)

    context = {
        "form": form,
        "dossier": dossier,
        "is_new": is_new,
        "canevas": canevas,
    }
    return render(request, "suivi_demande/canevas_form.html", context)


@login_required
def canevas_view_pdf(request, dossier_id):
    """Générer et afficher le PDF du canevas de proposition."""
    dossier = get_object_or_404(DossierCredit, pk=dossier_id)

    try:
        canevas = dossier.canevas
    except CanevasProposition.DoesNotExist:
        messages.error(request, "Aucun canevas de proposition pour ce dossier.")
        return redirect("suivi:dossier_detail", pk=dossier_id)

    # Générer le PDF
    template_path = "suivi_demande/canevas_pdf.html"
    context = {
        "canevas": canevas,
        "dossier": dossier,
    }

    # Créer le PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="canevas_{dossier.reference}.pdf"'

    template = render_to_string(template_path, context)
    pisa_status = pisa.CreatePDF(template, dest=response)

    if pisa_status.err:
        messages.error(request, "Erreur lors de la génération du PDF.")
        return redirect("suivi:dossier_detail", pk=dossier_id)

    return response

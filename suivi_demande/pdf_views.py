# core/pdf_views.py
from io import BytesIO
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.contrib.staticfiles import finders
from django.utils import timezone
from xhtml2pdf import pisa

from .models import (
    DossierCredit,
    PieceJointe,
    UserRoles,
)


@login_required
def dossier_proposition_pdf(request, pk: int):
    dossier = get_object_or_404(DossierCredit, pk=pk)
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", UserRoles.CLIENT)

    # Access control: client owner or staff roles
    if role == UserRoles.CLIENT and dossier.client_id != request.user.id:
        messages.error(request, "Accès refusé au dossier.")
        return redirect("dashboard")

    pieces = PieceJointe.objects.filter(dossier=dossier).order_by("upload_at")

    # Optional placeholders (if later persisted on dossier)
    echeance_calculee = None
    capacite_max = None

    # Resolve logo to filesystem path for xhtml2pdf compatibility
    logo_rel = 'core/img/Credit_Du_Congo.png'
    logo_path = finders.find(logo_rel)

    context = {
        "dossier": dossier,
        "client": dossier.client,
        "date": timezone.now(),
        "logo_path": logo_path,
        "pieces": pieces,
        "echeance_calculee": echeance_calculee,
        "capacite_max": capacite_max,
    }

    html = render_to_string("pdf/proposition.html", context)
    result = BytesIO()
    pdf_status = pisa.CreatePDF(src=html, dest=result)
    if pdf_status.err:
        messages.error(request, "Impossible de générer le PDF de la proposition.")
        return redirect("dossier_detail", pk=dossier.pk)

    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=proposition_{dossier.reference}.pdf"
    return response

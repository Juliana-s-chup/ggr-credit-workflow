"""
Vues pour la gestion des documents d'un dossier de credit
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

from .models import DossierCredit, PieceJointe, UserRoles


# Categories de documents requis
CATEGORIES_DOCUMENTS = {
    "JURIDIQUE": {
        "label": "Documents Juridiques",
        "icon": "fas fa-gavel",
        "color": "primary",
        "documents": [
            {"type": "BILLET_ORDRE", "label": "Billet e  ordre", "obligatoire": True},
            {
                "type": "DOMICILIATION",
                "label": "Attestation de domiciliation irrevocable",
                "obligatoire": True,
            },
        ],
    },
    "EMPLOYEUR": {
        "label": "Documents Employeur",
        "icon": "fas fa-building",
        "color": "success",
        "documents": [
            {
                "type": "BULLETIN_1",
                "label": "Bulletin de salaire (Mois -1)",
                "obligatoire": True,
            },
            {
                "type": "BULLETIN_2",
                "label": "Bulletin de salaire (Mois -2)",
                "obligatoire": True,
            },
            {
                "type": "BULLETIN_3",
                "label": "Bulletin de salaire (Mois -3)",
                "obligatoire": True,
            },
            {
                "type": "ATTESTATION_EMPLOYEUR",
                "label": "Attestation de l'employeur",
                "obligatoire": True,
            },
        ],
    },
    "ASSURANCE": {
        "label": "Documents Assurance",
        "icon": "fas fa-shield-alt",
        "color": "warning",
        "documents": [
            {
                "type": "ASSURANCE_DECES",
                "label": "Assurance deces",
                "obligatoire": True,
            },
            {
                "type": "ASSURANCE_INVALIDITE",
                "label": "Assurance invalidite",
                "obligatoire": True,
            },
        ],
    },
    "IDENTITE": {
        "label": "Documents d'Identite",
        "icon": "fas fa-id-card",
        "color": "info",
        "documents": [
            {"type": "CNI", "label": "CNI ou Passeport", "obligatoire": True},
            {
                "type": "JUSTIF_DOMICILE",
                "label": "Justificatif de domicile",
                "obligatoire": False,
            },
        ],
    },
}


@login_required
def upload_documents(request, dossier_id):
    """Page d'upload des documents par categorie."""
    dossier = get_object_or_404(DossierCredit, pk=dossier_id)

    # Verifier les permissions (Gestionnaire ou Admin)
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", None)
    if role not in (UserRoles.GESTIONNAIRE, UserRoles.SUPER_ADMIN):
        messages.error(request, "Acces refuse. Reserve aux gestionnaires.")
        return redirect("suivi:dossier_detail", pk=dossier_id)

    # Verifier que le canevas existe
    try:
        canevas = dossier.canevas
    except:
        messages.warning(request, "Veuillez d'abord remplir le canevas de proposition.")
        return redirect("suivi:canevas_form", dossier_id=dossier_id)

    # Recuperer les documents deje  uploades
    documents_existants = PieceJointe.objects.filter(dossier=dossier)
    docs_par_type = {doc.type_piece: doc for doc in documents_existants}

    # Calculer la completude
    total_obligatoires = 0
    total_fournis = 0

    categories_status = {}
    for cat_key, cat_data in CATEGORIES_DOCUMENTS.items():
        cat_obligatoires = sum(1 for d in cat_data["documents"] if d["obligatoire"])
        cat_fournis = sum(
            1
            for d in cat_data["documents"]
            if d["obligatoire"] and d["type"] in docs_par_type
        )

        total_obligatoires += cat_obligatoires
        total_fournis += cat_fournis

        categories_status[cat_key] = {
            "label": cat_data["label"],
            "icon": cat_data["icon"],
            "color": cat_data["color"],
            "obligatoires": cat_obligatoires,
            "fournis": cat_fournis,
            "complet": cat_fournis == cat_obligatoires,
            "documents": [],
        }

        for doc in cat_data["documents"]:
            doc_info = {
                "type": doc["type"],
                "label": doc["label"],
                "obligatoire": doc["obligatoire"],
                "existe": doc["type"] in docs_par_type,
                "fichier": docs_par_type.get(doc["type"]),
            }
            categories_status[cat_key]["documents"].append(doc_info)

    pourcentage_completion = (
        int((total_fournis / total_obligatoires * 100)) if total_obligatoires > 0 else 0
    )
    dossier_complet = total_fournis == total_obligatoires

    context = {
        "dossier": dossier,
        "canevas": canevas,
        "categories": categories_status,
        "pourcentage_completion": pourcentage_completion,
        "dossier_complet": dossier_complet,
        "total_obligatoires": total_obligatoires,
        "total_fournis": total_fournis,
    }

    return render(request, "suivi_demande/upload_documents.html", context)


@login_required
def upload_document_ajax(request, dossier_id):
    """Upload d'un document via AJAX."""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Methode non autorisee"}, status=405
        )

    dossier = get_object_or_404(DossierCredit, pk=dossier_id)

    # Verifier les permissions
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", None)
    if role not in (UserRoles.GESTIONNAIRE, UserRoles.SUPER_ADMIN):
        return JsonResponse({"success": False, "error": "Acces refuse"}, status=403)

    type_piece = request.POST.get("type_piece")
    fichier = request.FILES.get("fichier")

    if not type_piece or not fichier:
        return JsonResponse(
            {"success": False, "error": "Donnees manquantes"}, status=400
        )

    # Supprimer l'ancien document du meme type s'il existe
    PieceJointe.objects.filter(dossier=dossier, type_piece=type_piece).delete()

    # Creer le nouveau document
    piece = PieceJointe.objects.create(
        dossier=dossier,
        fichier=fichier,
        type_piece=type_piece,
        taille=fichier.size,
        upload_by=request.user,
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Document uploade avec succes",
            "piece_id": piece.id,
            "filename": fichier.name,
        }
    )


@login_required
def delete_document_ajax(request, dossier_id, piece_id):
    """Supprimer un document via AJAX."""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Methode non autorisee"}, status=405
        )

    dossier = get_object_or_404(DossierCredit, pk=dossier_id)
    piece = get_object_or_404(PieceJointe, pk=piece_id, dossier=dossier)

    # Verifier les permissions
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", None)
    if role not in (UserRoles.GESTIONNAIRE, UserRoles.SUPER_ADMIN):
        return JsonResponse({"success": False, "error": "Acces refuse"}, status=403)

    piece.delete()

    return JsonResponse(
        {
            "success": True,
            "message": "Document supprime avec succes",
        }
    )

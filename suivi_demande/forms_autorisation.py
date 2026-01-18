"""
Formulaires pour les autorisations ponctuelles.
"""

from django import forms
from django.forms import formset_factory


class AutorisationPonctuelleForm(forms.Form):
    # En-tÃªte
    date = forms.DateField(label="Date", widget=forms.DateInput(attrs={"type": "date"}))
    fdc = forms.CharField(label="FDC", max_length=50)
    gestionnaire = forms.CharField(label="Gest", max_length=100)
    agence = forms.CharField(label="Agence", max_length=100)
    client = forms.CharField(label="Client", max_length=200)
    radical = forms.CharField(label="Radical", max_length=50)
    segment = forms.CharField(label="Segment", max_length=50, initial="PARTICULIER")

    # DonnÃ©es en FCFA
    salaire_moyen = forms.DecimalField(label="Salaire moyen (A)", max_digits=12, decimal_places=2)
    montant_echeance = forms.DecimalField(
        label="Montant Ã©chÃ©ance (B)", max_digits=12, decimal_places=2
    )
    disponible_ab = forms.DecimalField(
        label="Disponible (A-B)", max_digits=12, decimal_places=2, required=False
    )
    disponible_ab_div2 = forms.DecimalField(
        label="(A-B) / 2", max_digits=12, decimal_places=2, required=False
    )

    # Section 2 - Garanties
    garanties_deja_formalisees = forms.CharField(
        label="Garanties dÃ©jÃ  formalisÃ©es",
        widget=forms.Textarea(attrs={"rows": 2}),
        required=False,
    )

    # Section 3 - Mouvement et rentabilitÃ© (DonnÃ©es en M XAF)
    mouvement_2022 = forms.DecimalField(
        label="Mouvement 2022", max_digits=12, decimal_places=2, required=False
    )
    mouvement_2023 = forms.DecimalField(
        label="Mouvement 2023", max_digits=12, decimal_places=2, required=False
    )
    mouvement_2024 = forms.DecimalField(
        label="Mouvement 2024", max_digits=12, decimal_places=2, required=False
    )

    # Section 4 - Objet de la demande
    objet_demande = forms.CharField(
        label="Objet de la demande", widget=forms.Textarea(attrs={"rows": 2})
    )

    # Section 5 - Avis motivÃ©s
    avis_gestionnaire = forms.CharField(
        label="Gestionnaire", widget=forms.Textarea(attrs={"rows": 3}), required=False
    )
    avis_responsable_succursale = forms.CharField(
        label="Responsable Succursale", widget=forms.Textarea(attrs={"rows": 3}), required=False
    )
    avis_analyste_credit = forms.CharField(
        label="Analyste CrÃ©dit", widget=forms.Textarea(attrs={"rows": 3}), required=False
    )

    # Section 6 - DÃ©cision
    decision_ggr = forms.CharField(label="DÃ©cision GGR", required=False)
    decision_dg = forms.CharField(label="DÃ©cision DG", required=False)

    def clean(self):
        cleaned = super().clean()
        try:
            a = cleaned.get("salaire_moyen") or 0
            b = cleaned.get("montant_echeance") or 0
            cleaned["disponible_ab"] = a - b
            cleaned["disponible_ab_div2"] = (a - b) / 2
        except Exception:
            pass
        return cleaned


class EngagementLigneForm(forms.Form):
    NATURE_CHOICES = [
        ("NOKI NOKI", "NOKI NOKI"),
        ("DECOUVERT", "DÃ©couvert"),
        ("AUTRE", "Autre"),
    ]
    nature = forms.ChoiceField(label="Nature", choices=NATURE_CHOICES)
    lignes_credit = forms.DecimalField(
        label="Lignes de crÃ©dit", max_digits=12, decimal_places=2, required=False
    )
    validite = forms.DateField(
        label="ValiditÃ©", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    utilisation = forms.DecimalField(
        label="Utilisation", max_digits=12, decimal_places=2, required=False
    )
    depassement_en_cours = forms.DecimalField(
        label="DÃ©passement en cours", max_digits=12, decimal_places=2, required=False
    )
    montant_sollicite = forms.DecimalField(
        label="Montant sollicitÃ©", max_digits=12, decimal_places=2, required=False
    )
    depassement_accord = forms.DecimalField(
        label="DÃ©passement (en cas d'accord)", max_digits=12, decimal_places=2, required=False
    )
    engagement_accord = forms.DecimalField(
        label="Engagement (en cas d'accord)", max_digits=12, decimal_places=2, required=False
    )
    validite_depassement = forms.DateField(
        label="ValiditÃ© dÃ©passement",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )


EngagementLigneFormSet = formset_factory(EngagementLigneForm, extra=3, can_delete=True)

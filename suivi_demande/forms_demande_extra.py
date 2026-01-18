"""
Formulaires pour le wizard de demande de credit (etapes 3 et 4).
"""

from django import forms


class DemandeStep3Form(forms.Form):
    nature_pret = forms.ChoiceField(
        label="Type de credit",
        choices=[
            ("CAUTION", "Caution"),
            ("PRET", "Pret"),
            ("DECOUVERT", "Decouvert"),
        ],
    )
    motif_credit = forms.CharField(label="Motif du credit", max_length=200)
    demande_montant_fcfa = forms.DecimalField(
        label="Montant souhaite (FCFA)", max_digits=12, decimal_places=2
    )
    demande_duree_mois = forms.IntegerField(label="Duree (mois)")
    demande_taux_pourcent = forms.DecimalField(label="Taux %", max_digits=5, decimal_places=2)
    PERIODICITE = [
        ("M", "Mensuelle"),
        ("T", "Trimestrielle"),
        ("S", "Semestrielle"),
        ("A", "Annuelle"),
    ]
    demande_periodicite = forms.ChoiceField(label="Periodicite", choices=PERIODICITE)
    demande_montant_echeance_fcfa = forms.DecimalField(
        label="Montant echeance (FCFA)", max_digits=12, decimal_places=2, required=False
    )
    demande_date_1ere_echeance = forms.DateField(
        label="Date 1re echeance", widget=forms.DateInput(attrs={"type": "date"}), required=False
    )


class DemandeStep4Form(forms.Form):
    avis_conseiller_commercial = forms.ChoiceField(
        label="Avis conseiller",
        required=False,
        choices=[
            ("FAVORABLE", "Favorable"),
            ("DEFAVORABLE", "Defavorable"),
            ("RESERVE", "Avec reserve"),
        ],
    )
    avis_responsable_agence = forms.CharField(
        label="Avis responsable d'agence", max_length=200, required=False
    )
    avis_risque_contrepartie = forms.CharField(
        label="Avis risque contrepartie", widget=forms.Textarea, required=False
    )
    accepter_conditions = forms.BooleanField(
        label="Je certifie l'exactitude des informations et j'accepte les conditions generales.",
        required=True,
    )

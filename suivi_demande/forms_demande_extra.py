from django import forms


class DemandeStep3Form(forms.Form):
    # Détails du crédit
    NATURE_PRET = [
        ("PRET", "Prêt"),
        ("DECOUVERT", "Découvert"),
        ("CAUTION", "Caution"),
    ]
    nature_pret = forms.ChoiceField(label="Type de crédit", choices=NATURE_PRET)
    objet = forms.CharField(label="Motif du crédit", max_length=200)
    montant_demande = forms.DecimalField(label="Montant souhaité (FCFA)", min_value=0, max_digits=12, decimal_places=2)
    DUREES = [(str(m), f"{m} mois") for m in (12, 24, 36, 48, 60, 72)]
    duree_mois = forms.ChoiceField(label="Durée (mois)", choices=DUREES)
    taux = forms.DecimalField(label="Taux %", min_value=0, max_digits=5, decimal_places=2)
    PERIODICITE = [("M", "Mensuel")]
    periodicite = forms.ChoiceField(label="Périodicité", choices=PERIODICITE)
    date_premiere_echeance = forms.DateField(label="Date 1re échéance", widget=forms.DateInput(attrs={"type": "date"}))


class DemandeStep4Form(forms.Form):
    # Documents & Validation (MVP)
    accepter_conditions = forms.BooleanField(
        label="Je certifie l'exactitude des informations et j'accepte les conditions générales.")

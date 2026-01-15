"""
Formulaires pour le wizard de demande de crédit (étapes 1 et 2).
"""
from django import forms


class DemandeStep1Form(forms.Form):
    # Section 1: Renseignements sur le demandeur (aligné sur CanevasProposition)
    nom_prenom = forms.CharField(label="Nom & prénom", max_length=200)
    date_naissance = forms.DateField(label="Date de naissance", widget=forms.DateInput(attrs={"type": "date"}))
    nationalite = forms.CharField(label="Nationalité", max_length=100, initial="CONGOLAISE")

    adresse_exacte = forms.CharField(label="Adresse exacte", max_length=255, widget=forms.Textarea(attrs={"rows": 2}))
    telephone_travail = forms.CharField(label="N° de tél Travail", max_length=30, required=False)
    telephone_domicile = forms.CharField(label="N° de tél Domicile", max_length=30, required=False)
    numero_telephone = forms.CharField(label="N° de tél portable", max_length=30)

    emploi_occupe = forms.CharField(label="Emploi occupé", max_length=200)
    STATUT_EMPLOI = [("PRIVE", "Privé"), ("PUBLIC", "Public")]
    statut_emploi = forms.ChoiceField(label="Statut d'emploi", choices=STATUT_EMPLOI)
    anciennete_emploi = forms.CharField(label="Ancienneté emploi", max_length=100)
    TYPE_CONTRAT = [("CDI", "CDI"), ("CDD", "CDD"), ("STAGE", "Stage"), ("AUTRE", "Autre")]
    type_contrat = forms.ChoiceField(label="Type de contrat", widget=forms.RadioSelect, choices=TYPE_CONTRAT)

    nom_employeur = forms.CharField(label="Nom employeur", max_length=200)
    lieu_emploi = forms.CharField(label="Lieu d'emploi", max_length=200)
    employeur_client_banque = forms.BooleanField(label="Employeur client de la banque", required=False)
    radical_employeur = forms.CharField(label="Radical employeur", max_length=50, required=False)

    # Situation familiale (revient à l'étape 1)
    SITUATION_FAM = [("CELIBATAIRE", "Célibataire"), ("MARIE", "Marié(e)"), ("DIVORCE", "Divorcé(e)"), ("VEUF", "Veuf/Veuve")]
    situation_famille = forms.ChoiceField(label="Situation de famille", widget=forms.RadioSelect, choices=[
        ("CELIBATAIRE", "Célibataire"),
        ("MARIE", "Marié(e)"),
        ("DIVORCE", "Divorcé(e)"),
        ("VEUF", "Veuf/Veuve"),
    ])
    nombre_personnes_charge = forms.IntegerField(label="Nbr de personnes à charge", min_value=0, initial=0, required=False)
    regime_matrimonial = forms.ChoiceField(label="Régime matrimonial", required=False, widget=forms.RadioSelect, choices=[
        ("COMMUNAUTE", "Communauté des biens"),
        ("SEPARATION", "Séparation des biens"),
        ("PARTICIPATION", "Participation aux acquêts"),
        ("AUTRE", "Autres"),
    ])

    # Conjoint & logement
    salaire_conjoint = forms.DecimalField(label="Salaire conjoint (FCFA)", max_digits=12, decimal_places=2, required=False, initial=0)
    emploi_conjoint = forms.CharField(label="Emploi conjoint", max_length=200, required=False)
    statut_logement = forms.ChoiceField(label="Logement / habitation", required=False, choices=[
        ("LOCATAIRE", "Locataire"),
        ("PROPRIETAIRE", "Propriétaire"),
        ("AUTRES", "Autres (à préciser)"),
    ])
    numero_tf = forms.CharField(label="Numéro TF", max_length=100, required=False)
    logement_autres_precision = forms.CharField(label="Préciser (logement)", max_length=200, required=False)

    # (Portail PRO) Sélection d'un client existant (optionnel)
    client_identifier = forms.CharField(label="Client (email ou nom d'utilisateur)", required=False)
    permettre_suivi_client = forms.BooleanField(label="Permettre au client sélectionné de suivre ce dossier", required=False)

    

    radical = forms.CharField(label="Radical (client)", max_length=50, required=False)
    date_ouverture_compte = forms.DateField(label="Date d'ouverture de compte", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_domiciliation_salaire = forms.DateField(label="Date de domiciliation de salaire", required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        data = super().clean()
        try:
            if data.get("situation_famille") == "MARIE" and not data.get("regime_matrimonial"):
                self.add_error("regime_matrimonial", "Ce champ est requis pour un(e) marié(e).")
            # Validation optionnelle: client existant via identifiant (username/email)
            ident = (data.get("client_identifier") or "").strip()
            if ident:
                from django.contrib.auth import get_user_model
                from django.db.models import Q
                User = get_user_model()
                user = User.objects.filter(Q(username__iexact=ident) | Q(email__iexact=ident)).first()
                if not user:
                    self.add_error("client_identifier", "Aucun utilisateur avec cet identifiant (utilise email ou nom d'utilisateur).")
                else:
                    # Normaliser pour la suite du wizard (compatibilité avec la vue Étape 4)
                    data["client_user_id"] = user.pk
        except Exception:
            pass
        return data


class DemandeStep2Form(forms.Form):
    # Étape 2: Situation financière (capacité d'endettement)
    salaire_net_moyen_fcfa = forms.DecimalField(label="Salaire net moyen (FCFA)", max_digits=12, decimal_places=2)
    echeances_prets_relevees = forms.DecimalField(label="Échéances de prêts relevées (FCFA)", max_digits=12, decimal_places=2, initial=0, required=False)
    total_echeances_credits_cours = forms.DecimalField(label="Total échéances crédits en cours (FCFA)", max_digits=12, decimal_places=2, initial=0, required=False)

    salaire_net_avant_endettement_fcfa = forms.DecimalField(label="Salaire net avant endettement (FCFA)", max_digits=12, decimal_places=2, required=False)
    capacite_endettement_brute_fcfa = forms.DecimalField(label="Capacité d'endettement brute (FCFA)", max_digits=12, decimal_places=2, required=False)
    capacite_endettement_nette_fcfa = forms.DecimalField(label="Capacité d'endettement nette (FCFA)", max_digits=12, decimal_places=2, required=False)

    def clean(self):
        data = super().clean()
        try:
            salaire = data.get("salaire_net_moyen_fcfa") or 0
            total_ech = data.get("total_echeances_credits_cours") or 0
            # Capacité brute = 40% du salaire net moyen
            brute = salaire * 0.40
            # Net = brute - échéances en cours
            nette = brute - total_ech
            data["capacite_endettement_brute_fcfa"] = brute
            data["capacite_endettement_nette_fcfa"] = max(nette, 0)
            data["salaire_net_avant_endettement_fcfa"] = salaire - total_ech
        except Exception:
            pass
        return data

    
    
    
    
    

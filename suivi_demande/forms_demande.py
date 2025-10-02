from django import forms


class DemandeStep1Form(forms.Form):
    # Informations personnelles
    nom = forms.CharField(label="Nom", max_length=100)
    prenom = forms.CharField(label="Prénom", max_length=100)
    date_naissance = forms.DateField(label="Date de naissance", widget=forms.DateInput(attrs={"type": "date"}))
    lieu_naissance = forms.CharField(label="Lieu de naissance", max_length=120)

    # Nationalité en saisie libre
    nationalite = forms.CharField(label="Nationalité", max_length=100)

    SITUATION_FAM = [
        ("", "Sélectionnez..."),
        ("CELIBATAIRE", "Célibataire"),
        ("MARIE", "Marié(e)"),
        ("DIVORCE", "Divorcé(e)"),
        ("VEUF", "Veuf/Veuve"),
    ]
    situation_familiale = forms.ChoiceField(label="Situation familiale", choices=SITUATION_FAM)
    nb_personnes_charge = forms.IntegerField(label="Nombre de personnes à charge", min_value=0, initial=0)

    adresse = forms.CharField(label="Adresse", widget=forms.Textarea(attrs={"rows": 2}))
    ville = forms.CharField(label="Ville", max_length=100)
    # code_postal supprimé (non nécessaire)

    # Liste des pays du monde (valeur = libellé pays)
    PAYS_CHOICES = [
        ("", "Sélectionnez..."),
        ("Afghanistan", "Afghanistan"), ("Afrique du Sud", "Afrique du Sud"), ("Albanie", "Albanie"),
        ("Algérie", "Algérie"), ("Allemagne", "Allemagne"), ("Andorre", "Andorre"), ("Angola", "Angola"),
        ("Antigua-et-Barbuda", "Antigua-et-Barbuda"), ("Arabie saoudite", "Arabie saoudite"), ("Argentine", "Argentine"),
        ("Arménie", "Arménie"), ("Australie", "Australie"), ("Autriche", "Autriche"), ("Azerbaïdjan", "Azerbaïdjan"),
        ("Bahamas", "Bahamas"), ("Bahreïn", "Bahreïn"), ("Bangladesh", "Bangladesh"), ("Barbade", "Barbade"),
        ("Belgique", "Belgique"), ("Belize", "Belize"), ("Bénin", "Bénin"), ("Bhoutan", "Bhoutan"),
        ("Biélorussie", "Biélorussie"), ("Birmanie", "Birmanie"), ("Bolivie", "Bolivie"), ("Bosnie-Herzégovine", "Bosnie-Herzégovine"),
        ("Botswana", "Botswana"), ("Brésil", "Brésil"), ("Brunei", "Brunei"), ("Bulgarie", "Bulgarie"),
        ("Burkina Faso", "Burkina Faso"), ("Burundi", "Burundi"), ("Cambodge", "Cambodge"), ("Cameroun", "Cameroun"),
        ("Canada", "Canada"), ("Cap-Vert", "Cap-Vert"), ("Centrafrique", "Centrafrique"), ("Chili", "Chili"),
        ("Chine", "Chine"), ("Chypre", "Chypre"), ("Colombie", "Colombie"), ("Comores", "Comores"),
        ("Congo", "Congo"), ("République démocratique du Congo", "République démocratique du Congo"),
        ("Corée du Nord", "Corée du Nord"), ("Corée du Sud", "Corée du Sud"), ("Costa Rica", "Costa Rica"),
        ("Côte d'Ivoire", "Côte d'Ivoire"), ("Croatie", "Croatie"), ("Cuba", "Cuba"), ("Danemark", "Danemark"),
        ("Djibouti", "Djibouti"), ("Dominique", "Dominique"), ("Égypte", "Égypte"), ("Émirats arabes unis", "Émirats arabes unis"),
        ("Équateur", "Équateur"), ("Érythrée", "Érythrée"), ("Espagne", "Espagne"), ("Estonie", "Estonie"),
        ("Eswatini", "Eswatini"), ("États-Unis", "États-Unis"), ("Éthiopie", "Éthiopie"), ("Fidji", "Fidji"),
        ("Finlande", "Finlande"), ("France", "France"), ("Gabon", "Gabon"), ("Gambie", "Gambie"),
        ("Géorgie", "Géorgie"), ("Ghana", "Ghana"), ("Grèce", "Grèce"), ("Grenade", "Grenade"),
        ("Guatemala", "Guatemala"), ("Guinée", "Guinée"), ("Guinée-Bissau", "Guinée-Bissau"), ("Guinée équatoriale", "Guinée équatoriale"),
        ("Guyana", "Guyana"), ("Haïti", "Haïti"), ("Honduras", "Honduras"), ("Hongrie", "Hongrie"),
        ("Inde", "Inde"), ("Indonésie", "Indonésie"), ("Irak", "Irak"), ("Iran", "Iran"),
        ("Irlande", "Irlande"), ("Islande", "Islande"), ("Israël", "Israël"), ("Italie", "Italie"),
        ("Jamaïque", "Jamaïque"), ("Japon", "Japon"), ("Jordanie", "Jordanie"), ("Kazakhstan", "Kazakhstan"),
        ("Kenya", "Kenya"), ("Kirghizistan", "Kirghizistan"), ("Kiribati", "Kiribati"), ("Kosovo", "Kosovo"),
        ("Koweït", "Koweït"), ("Laos", "Laos"), ("Lesotho", "Lesotho"), ("Lettonie", "Lettonie"),
        ("Liban", "Liban"), ("Libéria", "Libéria"), ("Libye", "Libye"), ("Liechtenstein", "Liechtenstein"),
        ("Lituanie", "Lituanie"), ("Luxembourg", "Luxembourg"), ("Macédoine du Nord", "Macédoine du Nord"),
        ("Madagascar", "Madagascar"), ("Malaisie", "Malaisie"), ("Malawi", "Malawi"), ("Maldives", "Maldives"),
        ("Mali", "Mali"), ("Malte", "Malte"), ("Maroc", "Maroc"), ("Marshall", "Marshall"),
        ("Maurice", "Maurice"), ("Mauritanie", "Mauritanie"), ("Mexique", "Mexique"), ("Micronésie", "Micronésie"),
        ("Moldavie", "Moldavie"), ("Monaco", "Monaco"), ("Mongolie", "Mongolie"), ("Monténégro", "Monténégro"),
        ("Mozambique", "Mozambique"), ("Namibie", "Namibie"), ("Nauru", "Nauru"), ("Népal", "Népal"),
        ("Nicaragua", "Nicaragua"), ("Niger", "Niger"), ("Nigéria", "Nigéria"), ("Niue", "Niue"),
        ("Norvège", "Norvège"), ("Nouvelle-Zélande", "Nouvelle-Zélande"), ("Oman", "Oman"), ("Ouganda", "Ouganda"),
        ("Ouzbékistan", "Ouzbékistan"), ("Pakistan", "Pakistan"), ("Palaos", "Palaos"), ("Panama", "Panama"),
        ("Papouasie-Nouvelle-Guinée", "Papouasie-Nouvelle-Guinée"), ("Paraguay", "Paraguay"), ("Pays-Bas", "Pays-Bas"),
        ("Pérou", "Pérou"), ("Philippines", "Philippines"), ("Pologne", "Pologne"), ("Portugal", "Portugal"),
        ("Qatar", "Qatar"), ("Roumanie", "Roumanie"), ("Royaume-Uni", "Royaume-Uni"), ("Russie", "Russie"),
        ("Rwanda", "Rwanda"), ("Saint-Kitts-et-Nevis", "Saint-Kitts-et-Nevis"), ("Sainte-Lucie", "Sainte-Lucie"),
        ("Saint-Marin", "Saint-Marin"), ("Saint-Vincent-et-les-Grenadines", "Saint-Vincent-et-les-Grenadines"),
        ("Salomon", "Salomon"), ("Salvador", "Salvador"), ("Samoa", "Samoa"), ("Sao Tomé-et-Principe", "Sao Tomé-et-Principe"),
        ("Sénégal", "Sénégal"), ("Serbie", "Serbie"), ("Seychelles", "Seychelles"), ("Sierra Leone", "Sierra Leone"),
        ("Singapour", "Singapour"), ("Slovaquie", "Slovaquie"), ("Slovénie", "Slovénie"), ("Somalie", "Somalie"),
        ("Soudan", "Soudan"), ("Soudan du Sud", "Soudan du Sud"), ("Sri Lanka", "Sri Lanka"), ("Suède", "Suède"),
        ("Suisse", "Suisse"), ("Suriname", "Suriname"), ("Syrie", "Syrie"), ("Tadjikistan", "Tadjikistan"),
        ("Tanzanie", "Tanzanie"), ("Tchad", "Tchad"), ("Tchéquie", "Tchéquie"), ("Thaïlande", "Thaïlande"),
        ("Timor oriental", "Timor oriental"), ("Togo", "Togo"), ("Tonga", "Tonga"), ("Trinité-et-Tobago", "Trinité-et-Tobago"),
        ("Tunisie", "Tunisie"), ("Turkménistan", "Turkménistan"), ("Turquie", "Turquie"), ("Tuvalu", "Tuvalu"),
        ("Ukraine", "Ukraine"), ("Uruguay", "Uruguay"), ("Vanuatu", "Vanuatu"), ("Vatican", "Vatican"),
        ("Venezuela", "Venezuela"), ("Viêt Nam", "Viêt Nam"), ("Yémen", "Yémen"), ("Zambie", "Zambie"), ("Zimbabwe", "Zimbabwe"),
    ]
    pays = forms.ChoiceField(label="Pays", choices=PAYS_CHOICES)

    telephone = forms.CharField(label="Téléphone", max_length=30)
    email = forms.EmailField(label="Email")

    def clean_nationalite(self):
        val = self.cleaned_data.get("nationalite", "")
        if isinstance(val, str):
            val = val.strip()
            # Capitalisation simple: première lettre de chaque mot en majuscule
            val = val.title()
        return val

    def clean(self):
        data = super().clean()
        # Pré‑sélection pays par défaut si vide
        pays = data.get("pays")
        if not pays:
            data["pays"] = "Congo"
        # Nettoyage simple téléphone (trim)
        tel = data.get("telephone")
        if isinstance(tel, str):
            data["telephone"] = tel.strip()
        return data


class DemandeStep2Form(forms.Form):
    # Situation financière
    STATUT_PRO = [
        ("", "Sélectionnez..."),
        ("SALARIE", "Salarié"),
        ("INDEPENDANT", "Indépendant"),
        ("FONCTIONNAIRE", "Fonctionnaire"),
        ("RETRAITE", "Retraité"),
        ("SANS_EMPLOI", "Sans emploi"),
        ("ETUDIANT", "Étudiant"),
    ]
    statut_emploi = forms.ChoiceField(label="Situation professionnelle", choices=STATUT_PRO)

    employeur_nom = forms.CharField(label="Nom de l'employeur", max_length=150, required=False)
    poste_occupe = forms.CharField(label="Poste occupé", max_length=120, required=False)

    ANCIENNETE_CHOICES = [
        ("", "Sélectionnez..."),
        ("LT_1", "Moins d'un an"),
        ("Y1_3", "1 à 3 ans"),
        ("Y3_5", "3 à 5 ans"),
        ("GT_5", "Plus de 5 ans"),
    ]
    anciennete = forms.ChoiceField(label="Ancienneté", choices=ANCIENNETE_CHOICES, required=False)

    salaire_net_moyen = forms.DecimalField(label="Revenu mensuel net (FCFA)", min_value=0, max_digits=12, decimal_places=2)
    autres_revenus = forms.DecimalField(label="Autres revenus mensuels (FCFA)", min_value=0, max_digits=12, decimal_places=2, initial=0, required=False,
                                        help_text="Pensions, loyers, investissements, etc.")
    charges_mensuelles = forms.DecimalField(label="Dépenses mensuelles (FCFA)", min_value=0, max_digits=12, decimal_places=2, initial=0)

    # Crédits en cours
    has_credits = forms.ChoiceField(label="Avez-vous des crédits en cours ?", choices=[("NON", "Non"), ("OUI", "Oui")], initial="NON")
    montant_total_credits = forms.DecimalField(label="Montant total des crédits (FCFA)", min_value=0, max_digits=12, decimal_places=2, required=False)
    mensualites_totales = forms.DecimalField(label="Mensualités totales (FCFA)", min_value=0, max_digits=12, decimal_places=2, required=False)

    def clean(self):
        data = super().clean()
        if data.get("has_credits") == "OUI":
            if data.get("montant_total_credits") in (None, ""):
                self.add_error("montant_total_credits", "Ce champ est requis si vous avez des crédits en cours.")
            if data.get("mensualites_totales") in (None, ""):
                self.add_error("mensualites_totales", "Ce champ est requis si vous avez des crédits en cours.")
        return data

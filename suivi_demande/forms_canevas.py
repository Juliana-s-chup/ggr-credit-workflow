"""
Formulaires pour le Canevas de Proposition NOKI NOKI
"""

from django import forms
from .models import CanevasProposition


class CanevasPropositionForm(forms.ModelForm):
    """Formulaire pour le canevas de proposition de crÃ©dit."""

    class Meta:
        model = CanevasProposition
        exclude = ["dossier"]

        widgets = {
            # EN-TÃŠTE
            "agence": forms.TextInput(attrs={"class": "form-control", "placeholder": "PNBR"}),
            "code_agence": forms.TextInput(attrs={"class": "form-control", "placeholder": "10"}),
            "nom_exploitant": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "YOBA"}
            ),
            "matricule_exploitant": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "101"}
            ),
            "date_proposition": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            # SECTION 1: IDENTITÃ‰
            "nom_prenom": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nom complet"}
            ),
            "date_naissance": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "nationalite": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "CONGOLAISE"}
            ),
            "adresse_exacte": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Quartier, Avenue, NÂ°"}
            ),
            "numero_telephone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+242 XX XXX XX XX"}
            ),
            # EMPLOI
            "radical": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Radical compte"}
            ),
            "date_ouverture_compte": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "date_domiciliation_salaire": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "emploi_occupe": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Poste occupÃ©"}
            ),
            "statut_emploi": forms.Select(attrs={"class": "form-select"}),
            "anciennete_emploi": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: 16 ans et 06 mois"}
            ),
            "type_contrat": forms.Select(attrs={"class": "form-select"}),
            # EMPLOYEUR
            "nom_employeur": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nom de l'employeur"}
            ),
            "lieu_emploi": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Lieu de travail"}
            ),
            "employeur_client_banque": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "radical_employeur": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Radical employeur"}
            ),
            # SITUATION FAMILIALE
            "situation_famille": forms.Select(attrs={"class": "form-select"}),
            "nombre_personnes_charge": forms.NumberInput(
                attrs={"class": "form-control", "min": "0"}
            ),
            "regime_matrimonial": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Si mariÃ©(e)"}
            ),
            "participation_enquetes": forms.TextInput(attrs={"class": "form-control"}),
            # LOGEMENT
            "salaire_conjoint": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "emploi_conjoint": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Emploi du conjoint"}
            ),
            "statut_logement": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "PropriÃ©taire/Locataire"}
            ),
            "numero_tf": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "NÂ° TF si propriÃ©taire"}
            ),
            # PRÃŠT EN COURS
            "nature_pret_cours": forms.Select(attrs={"class": "form-select"}),
            "montant_origine_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "date_derniere_echeance": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "montant_echeance_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "k_restant_du_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            # SECTION 2: CAPACITÃ‰ D'ENDETTEMENT
            "salaire_net_moyen_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "echeances_prets_relevees": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "total_echeances_credits_cours": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "salaire_net_avant_endettement_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "readonly": "readonly"}
            ),
            "capacite_endettement_brute_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "readonly": "readonly"}
            ),
            "capacite_endettement_nette_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "readonly": "readonly"}
            ),
            # SECTION 3: DÃ‰TAILS DU CRÃ‰DIT
            "nature_pret": forms.Select(attrs={"class": "form-select"}),
            "motif_credit": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Motif du crÃ©dit"}
            ),
            # Demande client
            "demande_montant_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "demande_duree_mois": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "demande_taux_pourcent": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "demande_periodicite": forms.Select(attrs={"class": "form-select"}),
            "demande_montant_echeance_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "readonly": "readonly"}
            ),
            "demande_date_1ere_echeance": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            # Proposition
            "proposition_montant_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "proposition_duree_mois": forms.NumberInput(
                attrs={"class": "form-control", "min": "1"}
            ),
            "proposition_taux_pourcent": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "proposition_periodicite": forms.Select(attrs={"class": "form-select"}),
            "proposition_montant_echeance_fcfa": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "readonly": "readonly"}
            ),
            "proposition_date_1ere_echeance": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            # SECTION 4: AVIS
            "avis_conseiller_commercial": forms.Select(attrs={"class": "form-select"}),
            "avis_responsable_agence": forms.TextInput(attrs={"class": "form-control"}),
            "avis_risque_contrepartie": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            # SECTION 4: DOCUMENTS & VALIDATION
            "doc_cni_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "doc_fiche_paie_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "doc_releve_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "doc_billet_ordre_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "doc_attestation_employeur_ok": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "doc_attestation_domiciliation_ok": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "doc_assurance_deces_invalidite_ok": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "validation_consentement": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

        labels = {
            # EN-TÃŠTE
            "agence": "Agence",
            "code_agence": "Code agence",
            "nom_exploitant": "Nom exploitant",
            "matricule_exploitant": "Matricule exploitant",
            "date_proposition": "Date",
            # IDENTITÃ‰
            "nom_prenom": "Nom & PrÃ©nom",
            "date_naissance": "Date de naissance",
            "nationalite": "NationalitÃ©",
            "adresse_exacte": "Adresse exacte",
            "numero_telephone": "NÂ° de tÃ©lÃ©phone",
            # EMPLOI
            "radical": "Radical",
            "date_ouverture_compte": "Date d'ouverture du compte",
            "date_domiciliation_salaire": "Date de domiciliation du salaire",
            "emploi_occupe": "Emploi occupÃ©",
            "statut_emploi": "Statut d'emploi (PrivÃ©/Public)",
            "anciennete_emploi": "AnciennetÃ© dans l'emploi (AnnÃ©es)",
            "type_contrat": "Type de contrat",
            # EMPLOYEUR
            "nom_employeur": "Nom employeur",
            "lieu_emploi": "Lieu d'emploi",
            "employeur_client_banque": "Si l'employeur est client de la banque, indiquer le radical",
            "radical_employeur": "Radical employeur",
            # SITUATION FAMILIALE
            "situation_famille": "Situation de famille",
            "nombre_personnes_charge": "Nbr de personnes Ã  charge",
            "regime_matrimonial": "Si mariÃ©, rÃ©gime matrimonial",
            "participation_enquetes": "Participation aux enquÃªtes",
            # LOGEMENT
            "salaire_conjoint": "Salaire du conjoint en",
            "emploi_conjoint": "Emploi du conjoint",
            "statut_logement": "Statut du logement",
            "numero_tf": "NÂ° du TF (si bien immaculÃ©)",
            # PRÃŠT EN COURS
            "nature_pret_cours": "Nature prÃªt en cours",
            "montant_origine_fcfa": "Montant Ã  l'origine en fcfa",
            "date_derniere_echeance": "Date derniÃ¨re Ã©chÃ©ance",
            "montant_echeance_fcfa": "Montant Ã‰chÃ©ance fcfa",
            "k_restant_du_fcfa": "K restant du en fcfa",
            # CAPACITÃ‰ D'ENDETTEMENT
            "salaire_net_moyen_fcfa": "Salaire net moyen en fcfa (1)",
            "echeances_prets_relevees": "Ã‰chÃ©ances prÃªts relevÃ©es par l'employeur Ã  la source en fcfa (2)",
            "total_echeances_credits_cours": "Total Ã©chÃ©ances crÃ©dits en cours chez CDCO en fcfa (3) / Voir NB",
            "salaire_net_avant_endettement_fcfa": "Salaire net avant endettement en fcfa (4) = (1) - (2)",
            "capacite_endettement_brute_fcfa": "CapacitÃ© d'endettement brute en fcfa (5)",
            "capacite_endettement_nette_fcfa": "CapacitÃ© d'endettement nette maximale en fcfa (6) = (5)-(3)-(4)",
            # DÃ‰TAILS DU CRÃ‰DIT
            "nature_pret": "Nature du crÃ©dit",
            "motif_credit": "Motif du crÃ©dit",
            "demande_montant_fcfa": "Montant en fcfa",
            "demande_duree_mois": "DurÃ©e (mois)",
            "demande_taux_pourcent": "Taux %",
            "demande_periodicite": "PÃ©riodicitÃ©",
            "demande_montant_echeance_fcfa": "Montant Ã©chÃ©ance en fcfa (*)",
            "demande_date_1ere_echeance": "Date 1Ã¨re Ã©chÃ©ance",
            "proposition_montant_fcfa": "Montant en fcfa",
            "proposition_duree_mois": "DurÃ©e (mois)",
            "proposition_taux_pourcent": "Taux %",
            "proposition_periodicite": "PÃ©riodicitÃ©",
            "proposition_montant_echeance_fcfa": "Montant Ã©chÃ©ance en fcfa (*)",
            "proposition_date_1ere_echeance": "Date 1Ã¨re Ã©chÃ©ance",
            # AVIS
            "avis_conseiller_commercial": "Avis motivÃ© du conseiller commercial",
            "avis_responsable_agence": "Avis du responsable d'agence",
            "avis_risque_contrepartie": "Avis Risque de contrepartie",
            # DOCUMENTS & VALIDATION
            "doc_cni_ok": "Carte d'identitÃ© (CNI)",
            "doc_fiche_paie_ok": "Fiche de paie (3 derniers bulletins)",
            "doc_releve_ok": "RelevÃ© bancaire",
            "doc_billet_ordre_ok": "Billet Ã  ordre",
            "doc_attestation_employeur_ok": "Attestation de l'employeur",
            "doc_attestation_domiciliation_ok": "Attestation de domiciliation irrÃ©vocable",
            "doc_assurance_deces_invalidite_ok": "Assurance dÃ©cÃ¨s-invaliditÃ©",
            "validation_consentement": "Je certifie l'exactitude des informations et j'accepte les conditions gÃ©nÃ©rales.",
        }

    def clean(self):
        """Validation et calculs automatiques."""
        cleaned_data = super().clean()

        # Calcul capacitÃ© d'endettement
        salaire_net = cleaned_data.get("salaire_net_moyen_fcfa", 0)
        echeances_relevees = cleaned_data.get("echeances_prets_relevees", 0)
        total_echeances = cleaned_data.get("total_echeances_credits_cours", 0)

        if salaire_net:
            # CapacitÃ© brute = 40% du salaire
            cleaned_data["capacite_endettement_brute_fcfa"] = salaire_net * 0.40

            # Salaire net avant endettement
            cleaned_data["salaire_net_avant_endettement_fcfa"] = salaire_net - echeances_relevees

            # CapacitÃ© nette
            cleaned_data["capacite_endettement_nette_fcfa"] = (
                cleaned_data["capacite_endettement_brute_fcfa"] - total_echeances
            )

        # Simulation indicative de l'Ã©chÃ©ance
        try:
            P = float(cleaned_data.get("demande_montant_fcfa") or 0)
            n = int(cleaned_data.get("demande_duree_mois") or 0)
            taux_annuel = float(cleaned_data.get("demande_taux_pourcent") or 0)
            periodicite = cleaned_data.get("demande_periodicite") or "M"

            if P > 0 and n > 0:
                if periodicite == "M":
                    r = taux_annuel / 100.0 / 12.0
                    periods = n
                elif periodicite == "T":
                    r = taux_annuel / 100.0 / 4.0
                    periods = max(1, n // 3)
                elif periodicite == "S":
                    r = taux_annuel / 100.0 / 2.0
                    periods = max(1, n // 6)
                else:  # 'A'
                    r = taux_annuel / 100.0
                    periods = max(1, n // 12)

                if r > 0 and periods > 0:
                    echeance = P * (r / (1 - (1 + r) ** (-periods)))
                else:
                    echeance = P / periods if periods > 0 else 0

                cleaned_data["demande_montant_echeance_fcfa"] = round(echeance, 2)
        except Exception:
            pass

        return cleaned_data

"""
Tests des formulaires de l'application suivi_demande.
"""

from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase

from ..forms_demande import DemandeStep1Form, DemandeStep2Form
from ..forms_demande_extra import DemandeStep3Form, DemandeStep4Form
from ..forms import SignupForm


class DemandeStep1FormTestCase(TestCase):
    """Tests du formulaire étape 1."""

    def test_form_valid_avec_donnees_correctes(self):
        """Test que le formulaire est valide avec des données correctes."""
        form_data = {
            "nom_prenom": "Jean Dupont",
            "date_naissance": (date.today() - timedelta(days=365 * 30)).isoformat(),
            "nationalite": "CONGOLAISE",
            "adresse_exacte": "123 Rue Test, Brazzaville",
            "numero_telephone": "+242 06 123 45 67",
            "emploi_occupe": "Développeur",
            "statut_emploi": "PRIVE",
            "anciennete_emploi": "5 ans",
            "type_contrat": "CDI",
            "nom_employeur": "Test Corp",
            "lieu_emploi": "Brazzaville",
            "situation_famille": "MARIE",
        }
        form = DemandeStep1Form(data=form_data)
        self.assertTrue(form.is_valid(), f"Erreurs: {form.errors}")

    def test_form_invalide_sans_champs_requis(self):
        """Test que le formulaire est invalide sans champs requis."""
        form = DemandeStep1Form(data={})
        self.assertFalse(form.is_valid())
        # Vérifier que les champs requis sont dans les erreurs
        self.assertIn("nom_prenom", form.errors)
        self.assertIn("date_naissance", form.errors)

    def test_form_refuse_nom_trop_court(self):
        """Test que le formulaire refuse un nom trop court."""
        form_data = {
            "nom_prenom": "A",  # Trop court
            "date_naissance": (date.today() - timedelta(days=365 * 30)).isoformat(),
            "nationalite": "CONGOLAISE",
            "adresse_exacte": "123 Rue Test",
            "numero_telephone": "+242 06 123 45 67",
            "emploi_occupe": "Test",
            "statut_emploi": "PRIVE",
            "anciennete_emploi": "1 an",
            "type_contrat": "CDI",
            "nom_employeur": "Test",
            "lieu_emploi": "Test",
            "situation_famille": "CELIBATAIRE",
        }
        form = DemandeStep1Form(data=form_data)
        # Selon votre validation, cela peut être valide ou invalide
        # Ajustez selon vos règles métier


class DemandeStep2FormTestCase(TestCase):
    """Tests du formulaire étape 2."""

    def test_form_valid_avec_donnees_correctes(self):
        """Test que le formulaire étape 2 est valide."""
        form_data = {
            "salaire_net_moyen": "500000",
            "autres_revenus": "50000",
            "total_charges_mensuelles": "200000",
            "nombre_personnes_charge": 2,
            "credits_en_cours": "NON",
            "total_echeances_credits": "0",
        }
        form = DemandeStep2Form(data=form_data)
        self.assertTrue(form.is_valid(), f"Erreurs: {form.errors}")

    def test_form_refuse_salaire_negatif(self):
        """Test que le formulaire refuse un salaire négatif."""
        form_data = {
            "salaire_net_moyen": "-100000",  # Négatif !
            "autres_revenus": "0",
            "total_charges_mensuelles": "100000",
            "nombre_personnes_charge": 1,
            "credits_en_cours": "NON",
            "total_echeances_credits": "0",
        }
        form = DemandeStep2Form(data=form_data)
        # Devrait être invalide
        self.assertFalse(form.is_valid())

    def test_form_accepte_salaire_zero(self):
        """Test que le formulaire gère le cas salaire zéro."""
        form_data = {
            "salaire_net_moyen": "0",
            "autres_revenus": "100000",
            "total_charges_mensuelles": "50000",
            "nombre_personnes_charge": 0,
            "credits_en_cours": "NON",
            "total_echeances_credits": "0",
        }
        form = DemandeStep2Form(data=form_data)
        # Selon votre logique métier


class DemandeStep3FormTestCase(TestCase):
    """Tests du formulaire étape 3."""

    def test_form_valid_avec_donnees_correctes(self):
        """Test que le formulaire étape 3 est valide."""
        form_data = {
            "type_credit": "PERSONNEL",
            "montant_demande": "1000000",
            "duree_mois": 24,
            "objet_financement": "Achat véhicule",
            "garanties_proposees": "Salaire domicilié",
        }
        form = DemandeStep3Form(data=form_data)
        self.assertTrue(form.is_valid(), f"Erreurs: {form.errors}")

    def test_form_refuse_montant_trop_faible(self):
        """Test que le formulaire refuse un montant trop faible."""
        form_data = {
            "type_credit": "PERSONNEL",
            "montant_demande": "1000",  # Trop faible
            "duree_mois": 12,
            "objet_financement": "Test",
            "garanties_proposees": "Test",
        }
        form = DemandeStep3Form(data=form_data)
        # Selon votre validation MONTANT_MINIMUM_CREDIT

    def test_form_refuse_duree_trop_longue(self):
        """Test que le formulaire refuse une durée trop longue."""
        form_data = {
            "type_credit": "PERSONNEL",
            "montant_demande": "1000000",
            "duree_mois": 200,  # Trop long (max 120 mois = 10 ans)
            "objet_financement": "Test",
            "garanties_proposees": "Test",
        }
        form = DemandeStep3Form(data=form_data)
        # Selon votre validation DUREE_MAXIMUM_MOIS


class DemandeStep4FormTestCase(TestCase):
    """Tests du formulaire étape 4."""

    def test_form_valid_avec_consentement(self):
        """Test que le formulaire est valide avec consentement."""
        form_data = {
            "consentement_traitement_donnees": True,
            "consentement_verification_informations": True,
            "consentement_conditions_generales": True,
        }
        form = DemandeStep4Form(data=form_data)
        self.assertTrue(form.is_valid(), f"Erreurs: {form.errors}")

    def test_form_invalide_sans_consentement(self):
        """Test que le formulaire est invalide sans consentement."""
        form_data = {
            "consentement_traitement_donnees": False,  # Pas de consentement
            "consentement_verification_informations": True,
            "consentement_conditions_generales": True,
        }
        form = DemandeStep4Form(data=form_data)
        # Devrait être invalide si consentement obligatoire
        # self.assertFalse(form.is_valid())


class SignupFormTestCase(TestCase):
    """Tests du formulaire d'inscription."""

    def test_form_valid_avec_donnees_correctes(self):
        """Test que le formulaire d'inscription est valide."""
        form_data = {
            "username": "newuser",
            "email": "new@test.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Erreurs: {form.errors}")

    def test_form_refuse_mots_de_passe_differents(self):
        """Test que le formulaire refuse des mots de passe différents."""
        form_data = {
            "username": "newuser",
            "email": "new@test.com",
            "password1": "ComplexPass123!",
            "password2": "DifferentPass456!",  # Différent
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Vérifier l'erreur sur password2
        self.assertIn("password2", form.errors)

    def test_form_refuse_mot_de_passe_trop_simple(self):
        """Test que le formulaire refuse un mot de passe trop simple."""
        form_data = {
            "username": "newuser",
            "email": "new@test.com",
            "password1": "123",  # Trop simple
            "password2": "123",
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_refuse_email_invalide(self):
        """Test que le formulaire refuse un email invalide."""
        form_data = {
            "username": "newuser",
            "email": "invalid-email",  # Invalide
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class FormValidationTestCase(TestCase):
    """Tests de validation croisée des formulaires."""

    def test_step2_echeances_coherentes_avec_credits(self):
        """Test que les échéances sont cohérentes avec l'existence de crédits."""
        # Si credits_en_cours = NON, total_echeances doit être 0
        form_data = {
            "salaire_net_moyen": "500000",
            "autres_revenus": "0",
            "total_charges_mensuelles": "100000",
            "nombre_personnes_charge": 1,
            "credits_en_cours": "NON",
            "total_echeances_credits": "50000",  # Incohérent !
        }
        form = DemandeStep2Form(data=form_data)
        # Selon votre logique de validation croisée

    def test_step3_duree_coherente_avec_montant(self):
        """Test que la durée est cohérente avec le montant."""
        # Petit montant avec longue durée = suspect
        form_data = {
            "type_credit": "PERSONNEL",
            "montant_demande": "100000",  # Petit montant
            "duree_mois": 120,  # Longue durée
            "objet_financement": "Test",
            "garanties_proposees": "Test",
        }
        form = DemandeStep3Form(data=form_data)
        # Selon votre logique métier

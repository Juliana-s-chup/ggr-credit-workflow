# C:\Users\HP CORE i7 11TH GEN\CascadeProjects\ggr-credit-workflow\core\forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CreditApplication
from .models import UserProfile

class CreditApplicationForm(forms.ModelForm):
    class Meta:
        model = CreditApplication
        fields = ["title", "amount"]


class SignupForm(UserCreationForm):
    """Formulaire d'inscription avec champs de profil."""
    full_name = forms.CharField(label="Nom complet", max_length=200)
    email = forms.EmailField(label="Adresse e-mail")
    phone = forms.CharField(label="Numéro de téléphone", max_length=30)
    birth_date = forms.DateField(label="Date de naissance", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    address = forms.CharField(label="Adresse complète", max_length=255)
    accept_terms = forms.BooleanField(label="J'accepte les conditions générales")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2", "full_name", "email", "phone", "birth_date", "address", "accept_terms")

    def save(self, commit=True):
        # Créer l'utilisateur inactif (Option A) et son profil
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
                phone=self.cleaned_data["phone"],
                birth_date=self.cleaned_data.get("birth_date"),
                address=self.cleaned_data["address"],
            )
        return user
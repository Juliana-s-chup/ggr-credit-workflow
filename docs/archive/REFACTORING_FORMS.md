# 🔄 REFACTORING DES FORMULAIRES

## Problème : 5 fichiers de formulaires (TROP)

```
suivi_demande/
├── forms.py                    # 200 lignes
├── forms_demande.py            # 300 lignes
├── forms_canevas.py            # 250 lignes
├── forms_autorisation.py       # 150 lignes
└── forms_demande_extra.py      # 100 lignes ❌ DOUBLON
```

**Total** : 1000 lignes réparties en 5 fichiers = **SURCHARGE**

---

## Solution : Consolidation en 3 fichiers

### Structure cible :

```
suivi_demande/
├── forms/
│   ├── __init__.py             # Imports centralisés
│   ├── dossier_forms.py        # Formulaires dossier + demande
│   ├── canevas_forms.py        # Formulaires canevas
│   └── autorisation_forms.py   # Formulaires autorisation
```

---

## Plan de refactoring (2h)

### Étape 1 : Créer le dossier forms/

```bash
mkdir suivi_demande\forms
```

### Étape 2 : Consolider dossier_forms.py

```python
# suivi_demande/forms/dossier_forms.py
"""
Formulaires pour les dossiers de crédit.
Consolidation de forms.py + forms_demande.py + forms_demande_extra.py
"""
from django import forms
from ..models import DossierCredit

class DossierCreditForm(forms.ModelForm):
    """Formulaire principal de création de dossier."""
    
    class Meta:
        model = DossierCredit
        fields = ['produit', 'montant', 'duree_mois', 'objet']
    
    def clean_montant(self):
        montant = self.cleaned_data['montant']
        if montant <= 0:
            raise forms.ValidationError("Le montant doit être positif")
        if montant > 100000000:  # 100M FCFA
            raise forms.ValidationError("Montant trop élevé (max 100M)")
        return montant
    
    def clean_duree_mois(self):
        duree = self.cleaned_data['duree_mois']
        if duree <= 0 or duree > 360:  # Max 30 ans
            raise forms.ValidationError("Durée invalide (1-360 mois)")
        return duree


class DossierCreditUpdateForm(forms.ModelForm):
    """Formulaire de modification de dossier."""
    # ...


class DossierCreditSearchForm(forms.Form):
    """Formulaire de recherche de dossiers."""
    # ...
```

### Étape 3 : Garder canevas_forms.py

```python
# suivi_demande/forms/canevas_forms.py
"""
Formulaires pour le canevas de proposition.
Anciennement forms_canevas.py
"""
# Déplacer le contenu de forms_canevas.py ici
```

### Étape 4 : Garder autorisation_forms.py

```python
# suivi_demande/forms/autorisation_forms.py
"""
Formulaires pour les autorisations.
Anciennement forms_autorisation.py
"""
# Déplacer le contenu de forms_autorisation.py ici
```

### Étape 5 : Créer __init__.py

```python
# suivi_demande/forms/__init__.py
"""
Imports centralisés des formulaires.
"""
from .dossier_forms import (
    DossierCreditForm,
    DossierCreditUpdateForm,
    DossierCreditSearchForm,
)
from .canevas_forms import CanevasPropositionForm
from .autorisation_forms import AutorisationForm

__all__ = [
    'DossierCreditForm',
    'DossierCreditUpdateForm',
    'DossierCreditSearchForm',
    'CanevasPropositionForm',
    'AutorisationForm',
]
```

### Étape 6 : Mettre à jour les imports dans views

```python
# Avant
from .forms import DossierCreditForm
from .forms_demande import DossierDemandeForm
from .forms_canevas import CanevasPropositionForm

# Après
from .forms import (
    DossierCreditForm,
    CanevasPropositionForm,
    AutorisationForm,
)
```

### Étape 7 : Supprimer anciens fichiers

```bash
rm suivi_demande\forms.py
rm suivi_demande\forms_demande.py
rm suivi_demande\forms_demande_extra.py
rm suivi_demande\forms_canevas.py
rm suivi_demande\forms_autorisation.py
```

---

## Résultat

**Avant** : 5 fichiers, 1000 lignes, duplication  
**Après** : 3 fichiers, 800 lignes, pas de duplication

**Gain** : 
- ✅ -200 lignes (duplication supprimée)
- ✅ -2 fichiers
- ✅ Meilleure organisation
- ✅ Imports centralisés

---

## Temps estimé : 2 heures

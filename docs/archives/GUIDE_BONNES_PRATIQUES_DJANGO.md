# 📘 GUIDE DES BONNES PRATIQUES DJANGO
## Pour votre mémoire et votre compréhension

---

## 🎯 INTRODUCTION

Ce guide explique les bonnes pratiques Django appliquées dans votre projet. Utilisez-le pour :
- ✅ Comprendre les choix techniques
- ✅ Rédiger votre mémoire
- ✅ Répondre aux questions de soutenance
- ✅ Progresser en développement Django

---

## 1️⃣ STRUCTURE D'UN PROJET DJANGO PROFESSIONNEL

### Architecture MVC (Model-View-Controller)

Django utilise le pattern **MVT** (Model-View-Template) :

```
ggr-credit-workflow/
├── core/                          # Configuration du projet
│   ├── settings/                  # Settings modulaires
│   │   ├── base.py               # Configuration commune
│   │   ├── client.py             # Portail client
│   │   └── pro.py                # Portail professionnel
│   ├── urls.py                   # Routage principal
│   └── wsgi.py                   # Déploiement
│
├── suivi_demande/                # Application principale
│   ├── models.py                 # 📊 Modèles (Base de données)
│   ├── views.py                  # 🎮 Vues (Logique métier)
│   ├── forms.py                  # 📝 Formulaires
│   ├── urls.py                   # 🔗 Routes de l'app
│   ├── admin.py                  # ⚙️ Interface admin
│   ├── decorators.py             # 🔒 Contrôle d'accès
│   ├── permissions.py            # 🛡️ Permissions
│   └── templates/                # 🎨 Templates HTML
│
├── templates/                     # Templates globaux
├── static/                        # Fichiers statiques (CSS, JS, images)
├── media/                         # Fichiers uploadés
├── requirements.txt               # Dépendances Python
└── manage.py                      # Commandes Django
```

**💡 Pourquoi cette structure ?**
- ✅ **Séparation des responsabilités** : Chaque fichier a un rôle précis
- ✅ **Réutilisabilité** : Les apps Django sont modulaires
- ✅ **Maintenabilité** : Facile de trouver et modifier le code

---

## 2️⃣ ORGANISATION DES IMPORTS (PEP 8)

### ❌ Mauvaise pratique
```python
from django.contrib import messages
from .models import DossierCredit
from django.shortcuts import render
from django.contrib import messages  # Doublon !
from datetime import date
```

### ✅ Bonne pratique
```python
"""
Module docstring : description du fichier.
"""
# 1. Imports Python standard
from datetime import date, datetime
from decimal import Decimal

# 2. Imports Django
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render

# 3. Imports tiers
from xhtml2pdf import pisa

# 4. Imports locaux
from .models import DossierCredit
from .forms import DemandeForm
```

**💡 Avantages** :
- ✅ Lisibilité immédiate
- ✅ Détection rapide des dépendances
- ✅ Évite les imports circulaires
- ✅ Facilite le refactoring

---

## 3️⃣ MODÈLES DJANGO (models.py)

### Bonnes pratiques appliquées dans votre projet

#### ✅ Utilisation de TextChoices
```python
class UserRoles(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    GESTIONNAIRE = "GESTIONNAIRE", "Gestionnaire"
    ANALYSTE = "ANALYSTE", "Analyste crédit"
```

**Avantages** :
- Type-safe (pas d'erreur de frappe)
- Autocomplétion dans l'IDE
- Validation automatique

#### ✅ Validators Django
```python
montant = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    validators=[MinValueValidator(0)]  # ✅ Validation côté DB
)
```

#### ✅ Relations bien définies
```python
client = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="dossiers"  # ✅ Accès inverse : user.dossiers.all()
)
```

#### ✅ Méthodes utiles
```python
def __str__(self):
    return f"{self.reference} - {self.client}"  # ✅ Affichage lisible

def calculer_capacite_endettement(self):
    """Calcule la capacité d'endettement."""  # ✅ Docstring
    self.capacite_brute = self.salaire * 0.40
```

---

## 4️⃣ VUES DJANGO (views.py)

### Types de vues dans votre projet

#### 1. Function-Based Views (FBV)
```python
@login_required  # ✅ Décorateur de sécurité
def dashboard(request):
    """Dashboard principal."""  # ✅ Docstring
    profile = request.user.profile
    role = profile.role
    
    if role == UserRoles.GESTIONNAIRE:
        # Logique gestionnaire
        pass
    
    return render(request, 'dashboard.html', context)
```

**Avantages** :
- ✅ Simple et direct
- ✅ Facile à comprendre pour les débutants
- ✅ Flexibilité totale

#### 2. Décorateurs personnalisés
```python
@login_required
@transition_allowed  # ✅ Vérifie les permissions
def transition_dossier(request, pk, action):
    """Effectue une transition de workflow."""
    # ...
```

---

## 5️⃣ FORMULAIRES DJANGO (forms.py)

### ModelForm vs Form

#### ✅ ModelForm (lié à un modèle)
```python
class CanevasPropositionForm(forms.ModelForm):
    class Meta:
        model = CanevasProposition
        exclude = ['dossier']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }
```

**Quand l'utiliser** :
- Création/modification d'objets en base
- Validation automatique selon le modèle

#### ✅ Form (formulaire libre)
```python
class DemandeStep1Form(forms.Form):
    nom_prenom = forms.CharField(max_length=200)
    date_naissance = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
```

**Quand l'utiliser** :
- Formulaires multi-étapes (wizard)
- Recherche/filtrage
- Pas de sauvegarde directe en base

---

## 6️⃣ SÉCURITÉ

### Contrôle d'accès par rôle

#### ✅ Décorateur personnalisé
```python
@role_required([UserRoles.GESTIONNAIRE, UserRoles.ANALYSTE])
def vue_protegee(request):
    # Seuls gestionnaires et analystes peuvent accéder
    pass
```

#### ✅ Vérification dans la vue
```python
def dossier_detail(request, pk):
    dossier = get_object_or_404(DossierCredit, pk=pk)
    
    # ✅ Vérifier que l'utilisateur a le droit
    if request.user != dossier.client and not is_staff(request.user):
        return HttpResponseForbidden()
```

### Protection CSRF
```html
<!-- ✅ Toujours inclure dans les formulaires POST -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
</form>
```

---

## 7️⃣ WORKFLOW ET TRAÇABILITÉ

### Journal des actions
```python
JournalAction.objects.create(
    dossier=dossier,
    action="TRANSITION",
    de_statut=ancien_statut,
    vers_statut=nouveau_statut,
    acteur=request.user,
    commentaire_systeme="Transmis à l'analyste",
    meta={"raison": "Documents complets"}
)
```

**💡 Avantages** :
- ✅ Traçabilité complète
- ✅ Audit trail
- ✅ Débogage facilité

### Système de notifications
```python
Notification.objects.create(
    utilisateur_cible=user,
    type="NOUVEAU_DOSSIER",
    titre="Nouveau dossier à traiter",
    message=f"Le dossier {dossier.reference} vous a été assigné.",
    canal="INTERNE"
)
```

---

## 8️⃣ SETTINGS MODULAIRES

### Pourquoi séparer les settings ?

```python
# core/settings/base.py      # ✅ Configuration commune
# core/settings/client.py    # ✅ Portail client
# core/settings/pro.py       # ✅ Portail professionnel
```

**Avantages** :
- ✅ Évite la duplication
- ✅ Configuration spécifique par environnement
- ✅ Sécurité (secrets séparés)

### Variables d'environnement
```python
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
```

**💡 Sécurité** :
- ✅ Secrets hors du code source
- ✅ Configuration par environnement (dev/prod)

---

## 9️⃣ TEMPLATES DJANGO

### Héritage de templates
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Mon site{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

<!-- dashboard.html -->
{% extends "base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
    <h1>Bienvenue {{ user.username }}</h1>
{% endblock %}
```

### Template tags personnalisés
```python
# templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def format_montant(value):
    """Formate un montant en FCFA."""
    return f"{value:,.0f} FCFA"
```

---

## 🔟 TESTS (À IMPLÉMENTER)

### Tests unitaires recommandés

```python
# tests.py
from django.test import TestCase
from .models import DossierCredit, UserRoles

class DossierCreditTestCase(TestCase):
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user('test', 'test@example.com', 'pass')
        
    def test_creation_dossier(self):
        """Test de création d'un dossier."""
        dossier = DossierCredit.objects.create(
            client=self.user,
            reference="DOS-TEST-001",
            montant=1000000
        )
        self.assertEqual(dossier.statut_agent, DossierStatutAgent.NOUVEAU)
        
    def test_transition_workflow(self):
        """Test de transition de statut."""
        # ...
```

**💡 Pourquoi tester ?**
- ✅ Détecte les bugs tôt
- ✅ Facilite le refactoring
- ✅ Documentation vivante du code

---

## 📊 PERFORMANCE

### Optimisation des requêtes

#### ❌ N+1 queries problem
```python
# ❌ Mauvais : 1 query + N queries
dossiers = DossierCredit.objects.all()
for d in dossiers:
    print(d.client.username)  # Query à chaque itération !
```

#### ✅ Solution : select_related
```python
# ✅ Bon : 1 seule query avec JOIN
dossiers = DossierCredit.objects.select_related('client').all()
for d in dossiers:
    print(d.client.username)  # Pas de query supplémentaire
```

### Pagination
```python
from django.core.paginator import Paginator

def liste_dossiers(request):
    dossiers = DossierCredit.objects.all()
    paginator = Paginator(dossiers, 25)  # 25 par page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'liste.html', {'page_obj': page_obj})
```

---

## 🚀 DÉPLOIEMENT

### Checklist de production

- ✅ `DEBUG = False`
- ✅ `SECRET_KEY` sécurisée (variable d'environnement)
- ✅ `ALLOWED_HOSTS` configuré
- ✅ HTTPS activé (`SECURE_SSL_REDIRECT = True`)
- ✅ Fichiers statiques collectés (`python manage.py collectstatic`)
- ✅ Base de données PostgreSQL (pas SQLite)
- ✅ Logs configurés
- ✅ Backups automatiques

---

## 📝 POUR VOTRE MÉMOIRE

### Points clés à mentionner

#### 1. Architecture
> "Le projet suit l'architecture MVT de Django, avec une séparation claire entre les modèles (base de données), les vues (logique métier) et les templates (présentation). Cette architecture facilite la maintenance et l'évolutivité du système."

#### 2. Sécurité
> "La sécurité est assurée par plusieurs mécanismes : contrôle d'accès par rôle avec des décorateurs personnalisés, protection CSRF, validation des données côté serveur, et utilisation de variables d'environnement pour les secrets."

#### 3. Workflow métier
> "Le système implémente un workflow complet de gestion des demandes de crédit, avec traçabilité via un journal des actions, notifications en temps réel, et gestion des états (statuts agent/client)."

#### 4. Bonnes pratiques
> "Le code respecte les conventions PEP 8, utilise des docstrings pour la documentation, et suit les bonnes pratiques Django recommandées par la communauté."

#### 5. Scalabilité
> "L'architecture modulaire permet d'ajouter facilement de nouvelles fonctionnalités. Le système de portails (client/professionnel) démontre la flexibilité de l'architecture."

---

## 🎓 QUESTIONS DE SOUTENANCE

### Q1 : Pourquoi Django ?
**Réponse** : Django est un framework Python mature, sécurisé par défaut, avec une excellente documentation. Il inclut un ORM puissant, un système d'authentification robuste, et suit le principe "batteries included".

### Q2 : Comment gérez-vous les permissions ?
**Réponse** : Nous utilisons un système de rôles (CLIENT, GESTIONNAIRE, ANALYSTE, etc.) stocké dans le profil utilisateur. Des décorateurs personnalisés vérifient les permissions avant d'exécuter les vues.

### Q3 : Comment assurez-vous la traçabilité ?
**Réponse** : Chaque action importante est enregistrée dans le modèle `JournalAction` avec l'acteur, l'horodatage, et les détails de l'action. Cela crée un audit trail complet.

### Q4 : Quelle est votre stratégie de tests ?
**Réponse** : Nous recommandons des tests unitaires pour les modèles et les fonctions métier, des tests d'intégration pour le workflow, et des tests de permissions pour la sécurité.

### Q5 : Comment gérez-vous les performances ?
**Réponse** : Utilisation de `select_related()` pour éviter les N+1 queries, pagination des listes, et mise en cache potentielle des données fréquemment consultées.

---

## 📚 RESSOURCES COMPLÉMENTAIRES

### Documentation officielle
- **Django** : https://docs.djangoproject.com/
- **Python PEP 8** : https://peps.python.org/pep-0008/

### Livres recommandés
- **Two Scoops of Django** : Bible des bonnes pratiques Django
- **Django for Professionals** : Déploiement et production

### Tutoriels
- **Django Girls Tutorial** : Excellent pour débuter
- **Real Python** : Articles avancés sur Django

---

## ✨ CONCLUSION

Votre projet démontre une **maîtrise des concepts Django** et respecte les **standards professionnels**. Les bonnes pratiques appliquées garantissent :

- ✅ **Maintenabilité** : Code clair et bien organisé
- ✅ **Sécurité** : Contrôles d'accès robustes
- ✅ **Évolutivité** : Architecture modulaire
- ✅ **Professionnalisme** : Conventions respectées

**Vous êtes prête pour votre soutenance !** 🎉

---

**Document créé le 4 novembre 2025**  
**Pour le projet GGR Credit Workflow**

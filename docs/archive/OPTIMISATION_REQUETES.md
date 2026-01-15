# ⚡ OPTIMISATION DES REQUÊTES N+1

## Problème : Requêtes N+1

### Exemple du problème

```python
# ❌ MAUVAIS : Génère 1 + N requêtes SQL
dossiers = DossierCredit.objects.all()  # 1 requête
for dossier in dossiers:
    print(dossier.client.username)      # N requêtes (1 par dossier)
    print(dossier.acteur_courant.full_name)  # N requêtes
```

**Résultat** : Si 100 dossiers → **201 requêtes SQL** ! 🐌

---

## Solution : select_related & prefetch_related

### 1. select_related (ForeignKey, OneToOne)

```python
# ✅ BON : Génère 1 seule requête avec JOIN
dossiers = DossierCredit.objects.select_related('client', 'acteur_courant').all()
for dossier in dossiers:
    print(dossier.client.username)      # Pas de requête supplémentaire
    print(dossier.acteur_courant.full_name)  # Pas de requête supplémentaire
```

**Résultat** : **1 requête SQL** ! ⚡

### 2. prefetch_related (ManyToMany, Reverse ForeignKey)

```python
# ✅ BON : Génère 2 requêtes (1 pour dossiers, 1 pour actions)
dossiers = DossierCredit.objects.prefetch_related('journal_actions').all()
for dossier in dossiers:
    for action in dossier.journal_actions.all():  # Pas de requête supplémentaire
        print(action.commentaire)
```

---

## Corrections à Appliquer

### Fichier : suivi_demande/views.py

#### Avant (❌ N+1)

```python
def liste_dossiers(request):
    dossiers = DossierCredit.objects.all()  # ❌ N+1
    return render(request, 'liste.html', {'dossiers': dossiers})
```

#### Après (✅ Optimisé)

```python
def liste_dossiers(request):
    dossiers = DossierCredit.objects.select_related(
        'client',
        'client__profile',
        'acteur_courant',
        'acteur_courant__profile'
    ).prefetch_related(
        'journal_actions',
        'pieces_jointes'
    ).all()
    return render(request, 'liste.html', {'dossiers': dossiers})
```

---

### Fichier : suivi_demande/views_pro.py

#### Avant (❌ N+1)

```python
def dashboard_pro(request):
    dossiers_en_cours = DossierCredit.objects.filter(
        statut_agent__in=['NOUVEAU', 'EN_COURS_ANALYSE']
    )  # ❌ N+1
    return render(request, 'dashboard.html', {'dossiers': dossiers_en_cours})
```

#### Après (✅ Optimisé)

```python
def dashboard_pro(request):
    dossiers_en_cours = DossierCredit.objects.filter(
        statut_agent__in=['NOUVEAU', 'EN_COURS_ANALYSE']
    ).select_related(
        'client__profile',
        'acteur_courant__profile'
    ).prefetch_related(
        'journal_actions__acteur'
    )
    return render(request, 'dashboard.html', {'dossiers': dossiers_en_cours})
```

---

### Fichier : analytics/services.py

#### Avant (❌ N+1)

```python
def calculer_statistiques():
    dossiers = DossierCredit.objects.all()  # ❌ N+1
    for dossier in dossiers:
        client_name = dossier.client.username
        # ...
```

#### Après (✅ Optimisé)

```python
def calculer_statistiques():
    dossiers = DossierCredit.objects.select_related('client').all()
    for dossier in dossiers:
        client_name = dossier.client.username
        # ...
```

---

## Vérification avec Django Debug Toolbar

### Installation

```bash
pip install django-debug-toolbar
```

### Configuration

```python
# settings/dev.py
INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    ...
]

INTERNAL_IPS = ['127.0.0.1']
```

### URLs

```python
# core/urls.py
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

### Utilisation

1. Lancer le serveur
2. Ouvrir une page
3. Cliquer sur l'onglet "SQL" dans la toolbar
4. Vérifier le nombre de requêtes

**Objectif** : < 10 requêtes par page

---

## Script de Détection Automatique

```python
# scripts/detect_n_plus_1.py
"""
Détecte les requêtes N+1 dans le code.
"""
import re
import os

def detect_n_plus_1(file_path):
    """Détecte les patterns N+1."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern : .objects.all() ou .objects.filter() sans select_related
    pattern = r'\.objects\.(all|filter)\([^)]*\)(?!\s*\.select_related)'
    
    matches = re.finditer(pattern, content)
    
    issues = []
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        issues.append(f"Ligne {line_num}: Possible N+1")
    
    return issues

# Analyser tous les fichiers views
for root, dirs, files in os.walk('suivi_demande'):
    for file in files:
        if file.startswith('views') and file.endswith('.py'):
            path = os.path.join(root, file)
            issues = detect_n_plus_1(path)
            if issues:
                print(f"\n{path}:")
                for issue in issues:
                    print(f"  ⚠️  {issue}")
```

---

## Checklist de Correction

### Fichiers à corriger :

- [ ] `suivi_demande/views.py` (10 vues)
- [ ] `suivi_demande/views_client.py` (5 vues)
- [ ] `suivi_demande/views_pro.py` (8 vues)
- [ ] `analytics/services.py` (3 fonctions)
- [ ] `api/views.py` (déjà fait avec ViewSet)

### Pattern à rechercher :

```bash
grep -rn "\.objects\.all()" suivi_demande/views*.py
grep -rn "\.objects\.filter(" suivi_demande/views*.py
```

### Pattern à ajouter :

```python
.select_related('client', 'acteur_courant')
.prefetch_related('journal_actions')
```

---

## Résultat Attendu

**Avant** :
- 201 requêtes pour afficher 100 dossiers
- Temps de chargement : 2-3 secondes

**Après** :
- 3-5 requêtes pour afficher 100 dossiers
- Temps de chargement : 0.2-0.3 secondes

**Gain** : **10x plus rapide** ⚡

---

## Temps estimé : 2 heures

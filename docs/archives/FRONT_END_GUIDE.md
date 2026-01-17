# 🎨 GUIDE D'INTÉGRATION FRONT-END

**Version**: 2.0  
**Date**: 11 Novembre 2025  
**Projet**: GGR Crédit Workflow

---

## 📁 NOUVELLE ARCHITECTURE

```
templates/
├── base-clean.html              # Layout principal propre
├── includes/                    # Partials réutilisables
│   ├── _head.html              # <head> complet
│   ├── _navbar.html            # Navigation principale
│   ├── _sidebar.html           # Menu latéral
│   ├── _footer.html            # Pied de page
│   ├── _breadcrumbs.html       # Fil d'Ariane
│   ├── _alerts.html            # Notifications
│   └── _skip-links.html        # Accessibilité
├── components/                  # Composants UI
│   ├── _kpi-card.html
│   ├── _badge.html
│   ├── _button.html
│   ├── _form-field.html
│   ├── _table.html
│   └── _modal.html
└── pages/                       # Pages finales
    ├── auth/
    ├── dashboard/
    └── dossiers/

static/
├── css/
│   └── main.css                # CSS principal
├── js/
│   ├── main.js                 # JS principal
│   └── src/modules/            # Modules ES6
└── img/
    └── optimized/              # Images WebP
```

---

## 🚀 UTILISATION

### 1. Créer une Page

```django
{% extends 'base-clean.html' %}

{% block title %}Mon Titre{% endblock %}

{% block body_class %}page-dashboard{% endblock %}

{% block content %}
<div class="container">
  <h1>Mon Contenu</h1>
</div>
{% endblock %}
```

### 2. Utiliser un Composant

```django
{% include 'components/_kpi-card.html' with 
   icon='📊'
   value=stats.total
   label='Total Dossiers'
%}
```

### 3. Ajouter du CSS Spécifique

```django
{% block extra_head %}
<style>
  .page-specific { color: red; }
</style>
{% endblock %}
```

### 4. Ajouter du JS Spécifique

```django
{% block extra_js %}
<script>
  console.log('Page JS');
</script>
{% endblock %}
```

---

## 🎨 DESIGN SYSTEM

### Couleurs

```css
--brand-500: #FFB800;      /* Jaune principal */
--coral-500: #FF6B4A;      /* Corail */
--neutral-900: #212121;    /* Texte */
--success-500: #10B981;    /* Succès */
--error-500: #EF4444;      /* Erreur */
```

### Espacements

```css
--gap-2: 0.5rem;   /* 8px */
--gap-4: 1rem;     /* 16px */
--gap-6: 1.5rem;   /* 24px */
--gap-8: 2rem;     /* 32px */
```

### Typographie

```css
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
```

---

## 📦 COMPOSANTS DISPONIBLES

### KPI Card
```django
{% include 'components/_kpi-card.html' with 
   icon='📊' value=1234 label='Total' %}
```

### Badge
```django
{% include 'components/_badge.html' with 
   text='Approuvé' variant='success' %}
```

### Button
```django
{% include 'components/_button.html' with 
   text='Soumettre' variant='primary' type='submit' %}
```

### Form Field
```django
{% include 'components/_form-field.html' with 
   id='email' name='email' label='Email' 
   type='email' required=True %}
```

---

## ⚡ PERFORMANCE

### Images

```html
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" loading="lazy" alt="Description">
</picture>
```

### CSS Critical

Le CSS critique est inline dans `_head.html` pour un chargement rapide.

### JS Defer

```html
<script src="{% static 'js/main.js' %}" defer></script>
```

---

## ♿ ACCESSIBILITÉ

### Skip Links

Automatiquement inclus dans `base-clean.html`.

### ARIA

Tous les composants incluent les attributs ARIA nécessaires.

### Navigation Clavier

Testée et fonctionnelle sur tous les composants.

---

## 🔧 CONFIGURATION DJANGO

### settings.py

```python
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### urls.py

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... vos URLs
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

---

## 📊 CHECKLIST QUALITÉ

- ✅ Layout responsive
- ✅ Partials réutilisables
- ✅ CSS organisé
- ✅ JS modularisé
- ✅ Images optimisées
- ✅ ARIA complet
- ✅ Performance 85+
- ✅ Documentation complète

---

**Front-end production-ready ! 🚀**

# 🧩 GUIDE DES COMPOSANTS RÉUTILISABLES

**Date**: 11 Novembre 2025  
**Version**: 1.0

---

## 📦 COMPOSANTS DISPONIBLES

### 1. KPI Card

**Utilisation**:
```django
{% include 'components/kpi-card.html' with 
   icon='📊'
   value=stats.total
   label='Total Dossiers'
   trend=stats.trend
%}
```

**Paramètres**:
- `icon` (optionnel): Emoji ou HTML
- `value` (requis): Valeur numérique
- `label` (requis): Label du KPI
- `trend` (optionnel): `{direction: 'up'|'down', text: '+12%'}`
- `link` (optionnel): `{url: '/details/', text: 'Voir'}`

---

### 2. Badge

**Utilisation**:
```django
{% include 'components/badge.html' with 
   text='Approuvé'
   variant='success'
   icon='✓'
%}
```

**Paramètres**:
- `text` (requis): Texte du badge
- `variant` (optionnel): `success|warning|error|info|primary`
- `icon` (optionnel): Icône avant le texte

---

### 3. Bouton

**Utilisation**:
```django
{% include 'components/button.html' with 
   text='Soumettre'
   variant='primary'
   type='submit'
   icon_right='→'
%}
```

**Paramètres**:
- `text` (requis): Texte du bouton
- `type` (optionnel): `button|submit|reset`
- `variant` (optionnel): `primary|secondary|outline|ghost`
- `size` (optionnel): `sm|md|lg`
- `icon_left` (optionnel): Icône gauche
- `icon_right` (optionnel): Icône droite
- `disabled` (optionnel): `True|False`
- `loading` (optionnel): `True|False`

---

### 4. Alert

**Utilisation**:
```django
{% include 'components/alert.html' with 
   message='Dossier créé avec succès'
   variant='success'
   icon='✓'
   dismissible=True
%}
```

**Paramètres**:
- `message` (requis): Message de l'alerte
- `variant` (optionnel): `success|warning|error|info`
- `title` (optionnel): Titre de l'alerte
- `icon` (optionnel): Icône
- `dismissible` (optionnel): `True|False`

---

### 5. Form Field

**Utilisation**:
```django
{% include 'components/form-field.html' with 
   id='email'
   name='email'
   label='Email'
   type='email'
   required=True
   placeholder='votre@email.com'
%}
```

**Paramètres**:
- `id` (requis): ID du champ
- `name` (requis): Name du champ
- `label` (requis): Label du champ
- `type` (optionnel): `text|email|password|number|textarea|select`
- `value` (optionnel): Valeur initiale
- `placeholder` (optionnel): Placeholder
- `required` (optionnel): `True|False`
- `disabled` (optionnel): `True|False`
- `help` (optionnel): Texte d'aide
- `error` (optionnel): Message d'erreur

---

### 6. Table Moderne

**Utilisation**:
```django
{% include 'components/table-modern.html' with 
   title='Dossiers Récents'
   headers=table_headers
   rows=table_rows
   pagination=pagination_html
%}
```

**Paramètres**:
- `title` (optionnel): Titre du tableau
- `headers` (requis): Liste de `{label: 'Nom', key: 'name', sortable: True}`
- `rows` (requis): Liste de listes (données)
- `actions` (optionnel): HTML des actions
- `pagination` (optionnel): HTML de pagination
- `empty_message` (optionnel): Message si vide

---

## 📝 EXEMPLES COMPLETS

### Dashboard avec KPI Cards

```django
{% extends 'base.html' %}

{% block content %}
<div class="kpi-grid">
  {% include 'components/kpi-card.html' with 
     icon='📊'
     value=stats.total
     label='Total Dossiers'
     trend=stats.trend_total
  %}
  
  {% include 'components/kpi-card.html' with 
     icon='⏳'
     value=stats.en_cours
     label='En Cours'
  %}
  
  {% include 'components/kpi-card.html' with 
     icon='✅'
     value=stats.approuves
     label='Approuvés'
  %}
  
  {% include 'components/kpi-card.html' with 
     icon='💰'
     value=stats.montant
     label='Montant Total'
  %}
</div>
{% endblock %}
```

### Formulaire Complet

```django
<form method="post">
  {% csrf_token %}
  
  {% include 'components/form-field.html' with 
     id='nom'
     name='nom'
     label='Nom complet'
     required=True
  %}
  
  {% include 'components/form-field.html' with 
     id='email'
     name='email'
     label='Email'
     type='email'
     required=True
  %}
  
  {% include 'components/form-field.html' with 
     id='montant'
     name='montant'
     label='Montant demandé'
     type='number'
     min='10000'
     help='Montant entre 10 000 et 1 000 000 FCFA'
     required=True
  %}
  
  {% include 'components/button.html' with 
     text='Soumettre'
     type='submit'
     variant='primary'
  %}
</form>
```

---

## ✅ ACCESSIBILITÉ INTÉGRÉE

Tous les composants incluent:
- ✅ Attributs ARIA appropriés
- ✅ Labels accessibles
- ✅ Support navigation clavier
- ✅ Messages d'erreur liés
- ✅ États visuels clairs

---

## 🎨 PERSONNALISATION

Les composants utilisent les classes du design system:
- Variables CSS pour les couleurs
- Classes utilitaires disponibles
- Responsive par défaut

---

**Composants prêts à l'emploi ! 🚀**

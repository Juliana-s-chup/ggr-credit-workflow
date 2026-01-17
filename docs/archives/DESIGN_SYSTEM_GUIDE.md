# 🎨 GUIDE DU DESIGN SYSTEM - GGR CRÉDIT DU CONGO

**Version**: 2.0  
**Date**: 11 Novembre 2025  
**Basé sur**: Logo officiel Crédit du Congo

---

## 📊 PALETTE DE COULEURS OFFICIELLE

### Couleurs Primaires (du logo)

```css
--color-yellow-primary: #FFB800;   /* Jaune-or vif (haut du logo) */
--color-yellow-light: #FFC933;     /* Jaune clair (dégradé) */
--color-yellow-dark: #E6A600;      /* Jaune foncé */

--color-coral-primary: #FF6B4A;    /* Corail-rouge (bas du logo) */
--color-coral-light: #FF8566;      /* Corail clair */
--color-coral-dark: #E65137;       /* Corail foncé */

--color-black-wave: #1A1A1A;       /* Noir de la vague */
```

### Utilisation

- **Jaune (#FFB800)**: Boutons primaires, liens, éléments interactifs
- **Corail (#FF6B4A)**: Boutons secondaires, alertes importantes
- **Noir (#1A1A1A)**: Textes, titres, éléments sombres

---

## 🎯 COMPOSANTS

### Boutons

```html
<!-- Bouton primaire (jaune) -->
<button class="btn btn-primary">Action principale</button>

<!-- Bouton secondaire (corail) -->
<button class="btn btn-secondary">Action secondaire</button>

<!-- Bouton outline -->
<button class="btn btn-outline">Annuler</button>

<!-- Tailles -->
<button class="btn btn-sm">Petit</button>
<button class="btn btn-lg">Grand</button>
```

### Cards

```html
<div class="card">
  <div class="card-header">
    Titre de la carte
  </div>
  <div class="card-body">
    Contenu de la carte
  </div>
  <div class="card-footer">
    Pied de page
  </div>
</div>
```

### Formulaires

```html
<div class="form-group">
  <label class="form-label" for="email">Email</label>
  <input type="email" id="email" class="form-input" placeholder="votre@email.com">
  <span class="form-help">Nous ne partagerons jamais votre email</span>
</div>
```

### Badges

```html
<span class="badge badge-primary">Nouveau</span>
<span class="badge badge-success">Approuvé</span>
<span class="badge badge-warning">En attente</span>
<span class="badge badge-error">Refusé</span>
```

---

## 📱 RESPONSIVE

### Breakpoints

- **Mobile**: < 640px
- **Tablette**: 768px - 1023px
- **Desktop**: ≥ 1024px

### Approche Mobile-First

```css
/* Mobile par défaut */
.element { width: 100%; }

/* Tablette */
@media (min-width: 768px) {
  .element { width: 50%; }
}

/* Desktop */
@media (min-width: 1024px) {
  .element { width: 33.333%; }
}
```

---

## ✅ CHECKLIST D'INTÉGRATION

### 1. Remplacer l'ancien CSS

- [ ] Supprimer `charte_graphique.css`
- [ ] Supprimer tout CSS inline dans les templates
- [ ] Importer `design-system.css` dans `base.html`

### 2. Mettre à jour les templates

- [ ] Remplacer les anciennes classes par les nouvelles
- [ ] Utiliser les composants réutilisables
- [ ] Supprimer les `<style>` inline

### 3. Tester

- [ ] Tester sur mobile
- [ ] Tester sur tablette
- [ ] Tester sur desktop
- [ ] Vérifier l'accessibilité

---

## 🚀 PROCHAINES ÉTAPES

1. **Créer des composants Django réutilisables**
2. **Extraire le JavaScript inline**
3. **Optimiser les performances**
4. **Ajouter le dark mode**

---

**Note finale**: Ce design system unifie TOUTES les couleurs du projet. Plus de conflits !

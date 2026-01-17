# Tableau de bord BI - Workflow de traitement des dossiers de crédit

## Vue d'ensemble

La digitalisation du workflow de traitement des dossiers de crédit génère un volume important de données exploitables pour le suivi opérationnel et la prise de décision. Une couche analytique a été intégrée au-dessus de la base PostgreSQL pour offrir une meilleure visibilité sur la performance du processus.

---

## a) Indicateurs clés (KPI) proposés

Les données disponibles permettent de construire plusieurs indicateurs pertinents, notamment :

### 1. Nombre de dossiers traités par période (jour, semaine, mois)
- **Définition**: Dossiers ayant atteint un statut final (APPROUVE_ATTENTE_FONDS, FONDS_LIBERE, REFUSE)
- **Source**: Vue `vw_kpi_dossiers_traites`
- **Utilité**: Mesurer le volume d'activité et identifier les pics de charge

### 2. Durée moyenne de traitement
- **Définition**: Temps écoulé entre la soumission du dossier et la décision finale
- **Source**: Vue `vw_lead_time`
- **Formule**: `(date_decision - date_soumission) en jours`
- **Utilité**: Évaluer l'efficacité du processus et respecter les SLA

### 3. Taux d'acceptation / rejet des demandes de crédit
- **Définition**: 
  - Taux d'acceptation = (Dossiers approuvés / Dossiers traités) × 100
  - Taux de refus = (Dossiers refusés / Dossiers traités) × 100
- **Source**: Vue `vw_taux_acceptation`
- **Utilité**: Piloter la politique de crédit et ajuster les critères d'éligibilité

### 4. Répartition des dossiers par gestionnaire
- **Définition**: Nombre de dossiers actifs par gestionnaire/analyste
- **Source**: Vue `vw_charge_gestionnaires`
- **Utilité**: Équilibrer la charge de travail et optimiser l'allocation des ressources

### 5. Temps moyen passé dans chaque statut du workflow
- **Définition**: Durée moyenne entre deux transitions de statut
- **Source**: Vue `vw_stage_durations`
- **Technique**: Utilisation de la fonction LAG() pour calculer les deltas
- **Utilité**: Identifier les goulets d'étranglement et optimiser les étapes critiques

### 6. Nombre de dossiers renvoyés ou incomplets
- **Définition**: Dossiers ayant fait l'objet d'un retour client ou gestionnaire
- **Source**: Vue `vw_rework`
- **Utilité**: Mesurer la qualité des dossiers initiaux et cibler les améliorations

---

## b) Proposition d'un tableau de bord BI

Un tableau de bord interactif peut être construit via **Power BI** ou **Tableau**. Il inclut :

### Connexion à la base de données

**Configuration PostgreSQL:**
```
Host: localhost (ou serveur distant)
Port: 5434
Database: ggr_credit_workflow
User: [utilisateur lecture seule recommandé]
Password: [mot de passe sécurisé]
```

**Driver recommandé:**
- Power BI: PostgreSQL connector natif
- Tableau: PostgreSQL driver ODBC

### Visuels proposés

#### 1. Courbe d'évolution du nombre de dossiers traités par mois
- **Type**: Graphique en courbes (Line Chart)
- **Source**: `vw_kpi_dossiers_traites`
- **Axes**:
  - X: `mois` (date)
  - Y: `dossiers_traites` (nombre)
- **Séries supplémentaires**: `dossiers_approuves`, `dossiers_refuses`
- **Filtres**: Période (année, trimestre)

#### 2. Histogramme comparant les délais moyens entre gestionnaires
- **Type**: Graphique en barres (Bar Chart)
- **Source**: `vw_lead_time`
- **Axes**:
  - X: `gestionnaire_username`
  - Y: `AVG(lead_time_jours)`
- **Tri**: Par délai décroissant
- **Filtres**: Rôle (gestionnaire/analyste), période

#### 3. Camembert des statuts des dossiers en temps réel
- **Type**: Graphique en secteurs (Pie Chart)
- **Source**: `vw_statuts_snapshot`
- **Valeurs**: `nb_dossiers` ou `pourcentage`
- **Légende**: `statut_agent`
- **Couleurs**: Code couleur par statut (vert=approuvé, rouge=refusé, etc.)

#### 4. Heatmap des motifs de rejet
- **Type**: Carte thermique (Heatmap) ou Treemap
- **Source**: `vw_motifs_rejet`
- **Dimensions**: `motif_rejet` (catégorisé)
- **Mesure**: `COUNT(dossier_id)`
- **Note**: Si les motifs ne sont pas codifiés, une étape de catégorisation manuelle ou par NLP peut être nécessaire

#### 5. Table détaillée - Charge de travail
- **Type**: Table interactive
- **Source**: `vw_charge_gestionnaires`
- **Colonnes**: gestionnaire, nb_dossiers_actifs, nb_en_cours, nb_approuvés, montant_total
- **Tri**: Par charge décroissante

### Rafraîchissement des données

**Option 1: DirectQuery**
- Avantages: Données toujours à jour en temps réel
- Inconvénients: Latence possible selon la charge de la base

**Option 2: Import planifié**
- Avantages: Performances optimales
- Inconvénients: Données rafraîchies selon la planification (ex: toutes les heures, quotidien)
- **Recommandation**: Rafraîchissement toutes les 4 heures en journée

**Passerelle:**
- Si Power BI Service est utilisé, configurer une passerelle locale pour accéder à la base on-premise

---

## c) Justification

L'ajout d'un module BI apporte une véritable valeur ajoutée au projet car il permet à la Direction des Risques de :

### 1. Améliorer les décisions stratégiques
- **Visibilité en temps réel** sur les volumes, délais et taux d'acceptation
- **Identification rapide** des tendances et anomalies
- **Pilotage basé sur les données** plutôt que sur l'intuition

### 2. Optimiser la charge de travail
- **Équilibrage** de la répartition des dossiers entre gestionnaires
- **Détection** des goulets d'étranglement dans le workflow
- **Priorisation** des actions correctives sur les étapes critiques

### 3. Renforcer la conformité
- **Traçabilité complète** via le journal d'actions (`JournalAction`)
- **Audit trail** pour les contrôles internes et externes
- **Alignement RGPD**: données minimisées, pseudonymisation possible, accès contrôlé

### 4. Amélioration continue
- **Mesure de la qualité** via le taux de rework
- **Benchmarking** des performances entre gestionnaires
- **Suivi des SLA** et objectifs de délai

---

## Implémentation technique

### Étape 1: Création des vues SQL
Exécuter le script `db/analytics_views.sql` sur la base PostgreSQL:
```bash
psql -U postgres -d ggr_credit_workflow -f db/analytics_views.sql
```

### Étape 2: Connexion Power BI
1. Ouvrir Power BI Desktop
2. Obtenir des données > PostgreSQL
3. Saisir les informations de connexion
4. Sélectionner les vues `vw_*`
5. Charger les données (Import ou DirectQuery)

### Étape 3: Création des visuels
1. Créer une page "Vue d'ensemble" avec les KPI principaux
2. Créer une page "Analyse des délais" avec courbe et histogramme
3. Créer une page "Qualité" avec rework et motifs de rejet
4. Ajouter des filtres globaux (période, gestionnaire, produit)

### Étape 4: Publication et partage
1. Publier sur Power BI Service
2. Configurer le rafraîchissement planifié
3. Partager avec la Direction des Risques (RLS si nécessaire)

---

## Sécurité et RGPD

### Pseudonymisation
- Remplacer les noms/emails par des codes anonymes côté BI si nécessaire
- Exemple: `username` → `GEST_001`, `GEST_002`

### Row-Level Security (RLS)
- Configurer des rôles Power BI pour filtrer les données par périmètre
- Exemple: Un gestionnaire ne voit que ses propres dossiers

### Accès en lecture seule
- Créer un utilisateur PostgreSQL dédié avec privilèges SELECT uniquement
```sql
CREATE USER bi_reader WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE ggr_credit_workflow TO bi_reader;
GRANT USAGE ON SCHEMA public TO bi_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bi_reader;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO bi_reader;
```

---

## Maintenance et évolution

### Ajout de nouveaux KPI
1. Créer une nouvelle vue SQL dans `db/analytics_views.sql`
2. Documenter la vue (COMMENT ON VIEW)
3. Ajouter le visuel correspondant dans Power BI
4. Mettre à jour cette documentation

### Optimisation des performances
- Créer des index sur les colonnes fréquemment filtrées
- Matérialiser les vues si nécessaire (MATERIALIZED VIEW)
- Planifier un VACUUM régulier sur les tables sources

---

## Ressources complémentaires

- **Script SQL**: `db/analytics_views.sql`
- **Page Rapports intégrée**: `/pro/rapports/` (filtrage par rôle, export CSV)
- **Documentation PostgreSQL**: https://www.postgresql.org/docs/
- **Power BI Documentation**: https://docs.microsoft.com/power-bi/

---

## Contact et support

Pour toute question sur l'implémentation du tableau de bord BI, contacter l'équipe projet.

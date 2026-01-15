-- ============================================================================
-- VUES ANALYTIQUES POUR TABLEAU DE BORD BI (Power BI / Tableau)
-- Projet: Workflow de traitement des dossiers de crédit
-- Base de données: PostgreSQL
-- ============================================================================

-- Vue 1: Dossiers traités par période (mois)
-- Utilisée pour: Courbe d'évolution du nombre de dossiers traités par mois
CREATE OR REPLACE VIEW vw_kpi_dossiers_traites AS
SELECT 
    date_trunc('month', j.timestamp) AS mois,
    COUNT(DISTINCT j.dossier_id) AS dossiers_traites,
    SUM(CASE WHEN j.vers_statut IN ('APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE') THEN 1 ELSE 0 END) AS dossiers_approuves,
    SUM(CASE WHEN j.vers_statut = 'REFUSE' THEN 1 ELSE 0 END) AS dossiers_refuses
FROM suivi_demande_journalaction j
WHERE j.vers_statut IN ('APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE', 'REFUSE')
GROUP BY date_trunc('month', j.timestamp)
ORDER BY mois;

COMMENT ON VIEW vw_kpi_dossiers_traites IS 
'Nombre de dossiers traités (décision finale) par mois avec répartition approuvés/refusés';


-- Vue 2: Lead time (délai de traitement) par dossier
-- Utilisée pour: Histogramme comparant les délais moyens entre gestionnaires
CREATE OR REPLACE VIEW vw_lead_time AS
WITH finals AS (
    SELECT 
        dossier_id, 
        MIN(timestamp) AS ts_final
    FROM suivi_demande_journalaction
    WHERE vers_statut IN ('APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE', 'REFUSE')
    GROUP BY dossier_id
)
SELECT 
    d.id AS dossier_id,
    d.reference,
    d.client_id,
    u.username AS client_username,
    d.acteur_courant_id AS gestionnaire_id,
    g.username AS gestionnaire_username,
    d.date_soumission,
    f.ts_final AS date_decision,
    EXTRACT(EPOCH FROM (f.ts_final - d.date_soumission))/86400 AS lead_time_jours,
    d.statut_agent,
    d.montant,
    d.produit
FROM suivi_demande_dossiercredit d
JOIN finals f ON f.dossier_id = d.id
LEFT JOIN auth_user u ON u.id = d.client_id
LEFT JOIN auth_user g ON g.id = d.acteur_courant_id;

COMMENT ON VIEW vw_lead_time IS 
'Délai de traitement (en jours) entre soumission et décision finale par dossier avec infos gestionnaire';


-- Vue 3: Durées moyennes par statut (temps passé dans chaque étape)
-- Utilisée pour: Analyse des goulets d'étranglement du workflow
CREATE OR REPLACE VIEW vw_stage_durations AS
WITH j AS (
    SELECT 
        dossier_id, 
        timestamp, 
        vers_statut,
        LAG(timestamp) OVER (PARTITION BY dossier_id ORDER BY timestamp) AS prev_ts,
        LAG(vers_statut) OVER (PARTITION BY dossier_id ORDER BY timestamp) AS prev_statut
    FROM suivi_demande_journalaction
)
SELECT 
    prev_statut AS statut,
    COUNT(*) AS nb_transitions,
    AVG(EXTRACT(EPOCH FROM (timestamp - prev_ts))/86400) AS jours_moyens,
    MIN(EXTRACT(EPOCH FROM (timestamp - prev_ts))/86400) AS jours_min,
    MAX(EXTRACT(EPOCH FROM (timestamp - prev_ts))/86400) AS jours_max,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (timestamp - prev_ts))/86400) AS jours_mediane
FROM j
WHERE prev_ts IS NOT NULL
GROUP BY prev_statut
ORDER BY jours_moyens DESC;

COMMENT ON VIEW vw_stage_durations IS 
'Temps moyen passé dans chaque statut du workflow avec statistiques (min, max, médiane)';


-- Vue 4: Dossiers avec rework (retours client/gestionnaire)
-- Utilisée pour: Mesure de la qualité et identification des points de contrôle à renforcer
CREATE OR REPLACE VIEW vw_rework AS
SELECT 
    j.dossier_id,
    d.reference,
    d.client_id,
    u.username AS client_username,
    COUNT(*) AS nb_retours,
    STRING_AGG(DISTINCT j.action, ', ') AS types_retours,
    MIN(j.timestamp) AS premier_retour,
    MAX(j.timestamp) AS dernier_retour
FROM suivi_demande_journalaction j
JOIN suivi_demande_dossiercredit d ON d.id = j.dossier_id
LEFT JOIN auth_user u ON u.id = d.client_id
WHERE j.action IN ('RETOUR_CLIENT', 'RETOUR_GESTIONNAIRE')
GROUP BY j.dossier_id, d.reference, d.client_id, u.username;

COMMENT ON VIEW vw_rework IS 
'Dossiers ayant fait l''objet de retours (client ou gestionnaire) avec nombre et dates';


-- Vue 5: Snapshot des statuts actuels (pour camembert temps réel)
-- Utilisée pour: Camembert des statuts des dossiers en temps réel
CREATE OR REPLACE VIEW vw_statuts_snapshot AS
SELECT 
    statut_agent,
    COUNT(*) AS nb_dossiers,
    SUM(montant) AS montant_total,
    ROUND(COUNT(*)::numeric * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pourcentage
FROM suivi_demande_dossiercredit
GROUP BY statut_agent
ORDER BY nb_dossiers DESC;

COMMENT ON VIEW vw_statuts_snapshot IS 
'Répartition actuelle des dossiers par statut agent avec pourcentages';


-- Vue 6: Motifs de rejet (pour heatmap)
-- Utilisée pour: Heatmap des motifs de rejet
-- Note: Si les motifs ne sont pas codifiés, cette vue extrait les commentaires système
CREATE OR REPLACE VIEW vw_motifs_rejet AS
SELECT 
    d.id AS dossier_id,
    d.reference,
    d.produit,
    d.montant,
    j.commentaire_systeme AS motif_rejet,
    j.timestamp AS date_refus,
    j.acteur_id,
    u.username AS acteur_username
FROM suivi_demande_dossiercredit d
JOIN suivi_demande_journalaction j ON j.dossier_id = d.id
LEFT JOIN auth_user u ON u.id = j.acteur_id
WHERE d.statut_agent = 'REFUSE'
  AND j.vers_statut = 'REFUSE'
ORDER BY j.timestamp DESC;

COMMENT ON VIEW vw_motifs_rejet IS 
'Dossiers refusés avec motifs extraits des commentaires système du journal';


-- Vue 7: Charge de travail par gestionnaire
-- Utilisée pour: Histogramme de répartition de la charge
CREATE OR REPLACE VIEW vw_charge_gestionnaires AS
SELECT 
    u.id AS gestionnaire_id,
    u.username AS gestionnaire_username,
    p.role AS gestionnaire_role,
    COUNT(DISTINCT d.id) AS nb_dossiers_actifs,
    SUM(d.montant) AS montant_total_portefeuille,
    COUNT(DISTINCT CASE WHEN d.statut_agent NOT IN ('APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE', 'REFUSE') THEN d.id END) AS nb_dossiers_en_cours,
    COUNT(DISTINCT CASE WHEN d.statut_agent IN ('APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE') THEN d.id END) AS nb_dossiers_approuves,
    COUNT(DISTINCT CASE WHEN d.statut_agent = 'REFUSE' THEN d.id END) AS nb_dossiers_refuses
FROM auth_user u
JOIN suivi_demande_userprofile p ON p.user_id = u.id
LEFT JOIN suivi_demande_dossiercredit d ON d.acteur_courant_id = u.id
WHERE p.role IN ('GESTIONNAIRE', 'ANALYSTE')
GROUP BY u.id, u.username, p.role
ORDER BY nb_dossiers_actifs DESC;

COMMENT ON VIEW vw_charge_gestionnaires IS 
'Charge de travail par gestionnaire/analyste avec répartition par statut';


-- Vue 8: Taux d'acceptation/rejet global et par période
-- Utilisée pour: KPI et tendances
CREATE OR REPLACE VIEW vw_taux_acceptation AS
SELECT 
    date_trunc('month', j.timestamp) AS mois,
    COUNT(DISTINCT j.dossier_id) AS total_traites,
    COUNT(DISTINCT CASE WHEN j.vers_statut IN ('APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE') THEN j.dossier_id END) AS nb_approuves,
    COUNT(DISTINCT CASE WHEN j.vers_statut = 'REFUSE' THEN j.dossier_id END) AS nb_refuses,
    ROUND(
        COUNT(DISTINCT CASE WHEN j.vers_statut IN ('APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE') THEN j.dossier_id END)::numeric * 100.0 
        / NULLIF(COUNT(DISTINCT j.dossier_id), 0), 
        2
    ) AS taux_acceptation,
    ROUND(
        COUNT(DISTINCT CASE WHEN j.vers_statut = 'REFUSE' THEN j.dossier_id END)::numeric * 100.0 
        / NULLIF(COUNT(DISTINCT j.dossier_id), 0), 
        2
    ) AS taux_refus
FROM suivi_demande_journalaction j
WHERE j.vers_statut IN ('APPROUVE_ATTENTE_FONDS', 'FONDS_LIBERE', 'REFUSE')
GROUP BY date_trunc('month', j.timestamp)
ORDER BY mois;

COMMENT ON VIEW vw_taux_acceptation IS 
'Taux d''acceptation et de refus par mois pour analyse des tendances';


-- ============================================================================
-- INSTRUCTIONS D'UTILISATION
-- ============================================================================
-- 1. Exécuter ce script sur votre base PostgreSQL
-- 2. Connecter Power BI ou Tableau à la base via ODBC/PostgreSQL driver
-- 3. Importer les vues comme sources de données
-- 4. Créer les visuels recommandés:
--    - Courbe: vw_kpi_dossiers_traites (mois x dossiers_traites)
--    - Histogramme: vw_lead_time (gestionnaire_username x AVG(lead_time_jours))
--    - Camembert: vw_statuts_snapshot (statut_agent x nb_dossiers)
--    - Heatmap: vw_motifs_rejet (motif_rejet x COUNT)
--    - Table: vw_charge_gestionnaires
-- 5. Configurer le rafraîchissement (DirectQuery ou Import planifié)
-- ============================================================================

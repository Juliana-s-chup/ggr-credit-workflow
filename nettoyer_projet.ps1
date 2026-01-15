# Script de nettoyage automatique du projet GGR Credit Workflow
# Supprime tous les fichiers obsoletes et temporaires

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NETTOYAGE DU PROJET GGR CREDIT WORKFLOW" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$compteur = 0

# Fonction pour supprimer un fichier
function Supprimer-Fichier {
    param($fichier)
    if (Test-Path $fichier) {
        Remove-Item $fichier -Force
        Write-Host "[OK] Supprime: $fichier" -ForegroundColor Green
        return 1
    }
    return 0
}

Write-Host "1. Suppression des scripts temporaires..." -ForegroundColor Yellow
$compteur += Supprimer-Fichier "check_users.py"
$compteur += Supprimer-Fichier "create_test_users.py"
$compteur += Supprimer-Fichier "diagnostic_analyste.py"
$compteur += Supprimer-Fichier "fix_all_indentation.py"
$compteur += Supprimer-Fichier "fix_client_namespace.py"
$compteur += Supprimer-Fichier "fix_demande_start.py"
$compteur += Supprimer-Fichier "fix_indentation.py"
$compteur += Supprimer-Fichier "fix_missing_views.py"
$compteur += Supprimer-Fichier "fix_namespaces.py"
$compteur += Supprimer-Fichier "fix_views_namespace.py"
$compteur += Supprimer-Fichier "reset_all_passwords.py"
$compteur += Supprimer-Fichier "reset_password.py"
$compteur += Supprimer-Fichier "setup_superadmin_portal.py"
$compteur += Supprimer-Fichier "verifier_dossiers.py"

Write-Host ""
Write-Host "2. Suppression des scripts PowerShell temporaires..." -ForegroundColor Yellow
$compteur += Supprimer-Fichier "fix_encoding_complete.ps1"
$compteur += Supprimer-Fichier "update_core_to_suivi_demande.ps1"
$compteur += Supprimer-Fichier "update_core_to_suivi_demande_fixed.ps1"

Write-Host ""
Write-Host "3. Suppression des scripts de test..." -ForegroundColor Yellow
$compteur += Supprimer-Fichier "test_dashboard_final.py"
$compteur += Supprimer-Fichier "test_decimal_serialization.py"
$compteur += Supprimer-Fichier "test_demande_workflow.py"
$compteur += Supprimer-Fichier "test_gestionnaire_workflow.py"
$compteur += Supprimer-Fichier "test_import.py"
$compteur += Supprimer-Fichier "test_login_flow.py"
$compteur += Supprimer-Fichier "test_portals.py"
$compteur += Supprimer-Fichier "test_pro_login.py"

Write-Host ""
Write-Host "4. Suppression des fichiers en double dans core/..." -ForegroundColor Yellow
$compteur += Supprimer-Fichier "core\urls_client.py"
$compteur += Supprimer-Fichier "core\urls_pro.py"
$compteur += Supprimer-Fichier "core\wsgi_temp.py"

Write-Host ""
Write-Host "5. Suppression des fichiers temporaires..." -ForegroundColor Yellow
$compteur += Supprimer-Fichier ".env.local"
$compteur += Supprimer-Fichier "db.sqlite3"

Write-Host ""
Write-Host "6. Suppression de la documentation obsolete..." -ForegroundColor Yellow
$compteur += Supprimer-Fichier "CHAR centrale_OFFICIELLE.md"
$compteur += Supprimer-Fichier "CORRECTIONS_NAMESPACE.md"
$compteur += Supprimer-Fichier "CORRECTION_DASHBOARD_GESTIONNAIRE.md"
$compteur += Supprimer-Fichier "CORRECTION_DECIMAL_JSON.md"
$compteur += Supprimer-Fichier "CORRECTION_ERREUR_BOE.md"
$compteur += Supprimer-Fichier "CORRECTION_FINALE_NAVIGATION.md"
$compteur += Supprimer-Fichier "DASHBOARD_SUPERADMIN_CLEAN.md"
$compteur += Supprimer-Fichier "DEBUG_IMMEDIAT.md"
$compteur += Supprimer-Fichier "DIAGNOSTIC_DOSSIERS.md"
$compteur += Supprimer-Fichier "INTEGRATION_LOGO.md"
$compteur += Supprimer-Fichier "LOGO_AUTH_PAGES.md"
$compteur += Supprimer-Fichier "MIGRATION_STATUS.md"
$compteur += Supprimer-Fichier "NOTIFICATION_ANALYSTES.md"
$compteur += Supprimer-Fichier "PLAN_MEMOIRE.md"
$compteur += Supprimer-Fichier "PLAN_MODIFICATIONS_RAPPORTS.md"
$compteur += Supprimer-Fichier "PORTAILS_SEPARES_GUIDE.md"
$compteur += Supprimer-Fichier "RECAP_SESSION_FINAL.md"
$compteur += Supprimer-Fichier "RESUME_AMELIORATIONS.md"
$compteur += Supprimer-Fichier "RESUME_MIGRATION_PORTAILS.md"
$compteur += Supprimer-Fichier "RÉSUMÉ_CORRECTIONS.md"
$compteur += Supprimer-Fichier "SERVER_STARTED.md"
$compteur += Supprimer-Fichier "SOLUTION_ALLOWED_HOSTS.md"
$compteur += Supprimer-Fichier "SOLUTION_ANALYSTE.md"
$compteur += Supprimer-Fichier "SOLUTION_BOE_NOTIFICATIONS.md"
$compteur += Supprimer-Fichier "SOLUTION_CREATION_UTILISATEUR.md"
$compteur += Supprimer-Fichier "SOLUTION_FINALE_ALLOWED_HOSTS.md"
$compteur += Supprimer-Fichier "SOLUTION_FINALE_DOSSIERS.md"
$compteur += Supprimer-Fichier "SOLUTION_MODIFICATIONS_RAPPORTS.md"
$compteur += Supprimer-Fichier "SOLUTION_MODIFICATION_UTILISATEUR.md"
$compteur += Supprimer-Fichier "SOLUTION_NAMESPACE_PRO.md"
$compteur += Supprimer-Fichier "SOLUTION_SIMPLE_FINALE.md"
$compteur += Supprimer-Fichier "SOLUTION_SIMPLE_LOCALHOST.md"
$compteur += Supprimer-Fichier "SOLUTION_SUPER_ADMIN_FINAL.md"
$compteur += Supprimer-Fichier "TESTS_A_EFFECTUER.md"
$compteur += Supprimer-Fichier "TEST_CREATION_UTILISATEUR.md"
$compteur += Supprimer-Fichier "TEST_NAVIGATION_SECTIONS.md"
$compteur += Supprimer-Fichier "RECAP_FINAL_COMPLET.md"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NETTOYAGE TERMINE!" -ForegroundColor Green
Write-Host "$compteur fichiers supprimes" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Fichiers conserves:" -ForegroundColor Yellow
Write-Host "- manage.py"
Write-Host "- requirements.txt"
Write-Host "- README.md"
Write-Host "- .env et .env.example"
Write-Host "- core/ (configuration Django)"
Write-Host "- suivi_demande/ (application principale)"
Write-Host "- templates/ (tous les templates)"
Write-Host "- static/ (fichiers statiques)"
Write-Host "- ANALYSE_PROJET_COMPLETE.md"
Write-Host "- NETTOYAGE_PROJET.md"
Write-Host ""
Write-Host "IMPORTANT: Testez l'application apres le nettoyage!" -ForegroundColor Red
Write-Host "Commande: python manage.py runserver 0.0.0.0:8002" -ForegroundColor Yellow

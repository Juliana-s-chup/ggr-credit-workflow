# GUIDE DE NETTOYAGE DU PROJET

## FICHIERS A SUPPRIMER MANUELLEMENT

### 1. Scripts temporaires (racine) - 14 fichiers
```
check_users.py
create_test_users.py
diagnostic_analyste.py
fix_all_indentation.py
fix_client_namespace.py
fix_demande_start.py
fix_indentation.py
fix_missing_views.py
fix_namespaces.py
fix_views_namespace.py
reset_all_passwords.py
reset_password.py
setup_superadmin_portal.py
verifier_dossiers.py
```

### 2. Scripts PowerShell temporaires - 3 fichiers
```
fix_encoding_complete.ps1
update_core_to_suivi_demande.ps1
update_core_to_suivi_demande_fixed.ps1
```

### 3. Scripts de test temporaires - 8 fichiers
```
test_dashboard_final.py
test_decimal_serialization.py
test_demande_workflow.py
test_gestionnaire_workflow.py
test_import.py
test_login_flow.py
test_portals.py
test_pro_login.py
```

### 4. Fichiers en double dans core/ - 3 fichiers
```
core/urls_client.py
core/urls_pro.py
core/wsgi_temp.py
```

### 5. Fichiers temporaires - 2 fichiers
```
.env.local
db.sqlite3
```

### 6. Documentation obsolete - 35 fichiers
```
CHAR centrale_OFFICIELLE.md
CORRECTIONS_NAMESPACE.md
CORRECTION_DASHBOARD_GESTIONNAIRE.md
CORRECTION_DECIMAL_JSON.md
CORRECTION_ERREUR_BOE.md
CORRECTION_FINALE_NAVIGATION.md
DASHBOARD_SUPERADMIN_CLEAN.md
DEBUG_IMMEDIAT.md
DIAGNOSTIC_DOSSIERS.md
INTEGRATION_LOGO.md
LOGO_AUTH_PAGES.md
MIGRATION_STATUS.md
NOTIFICATION_ANALYSTES.md
PLAN_MEMOIRE.md
PLAN_MODIFICATIONS_RAPPORTS.md
PORTAILS_SEPARES_GUIDE.md
RECAP_SESSION_FINAL.md
RESUME_AMELIORATIONS.md
RESUME_MIGRATION_PORTAILS.md
RÉSUMÉ_CORRECTIONS.md
SERVER_STARTED.md
SOLUTION_ALLOWED_HOSTS.md
SOLUTION_ANALYSTE.md
SOLUTION_BOE_NOTIFICATIONS.md
SOLUTION_CREATION_UTILISATEUR.md
SOLUTION_FINALE_ALLOWED_HOSTS.md
SOLUTION_FINALE_DOSSIERS.md
SOLUTION_MODIFICATIONS_RAPPORTS.md
SOLUTION_MODIFICATION_UTILISATEUR.md
SOLUTION_NAMESPACE_PRO.md
SOLUTION_SIMPLE_FINALE.md
SOLUTION_SIMPLE_LOCALHOST.md
SOLUTION_SUPER_ADMIN_FINAL.md
TESTS_A_EFFECTUER.md
TEST_CREATION_UTILISATEUR.md
TEST_NAVIGATION_SECTIONS.md
```

## TOTAL: 65 FICHIERS A SUPPRIMER

## COMMANDES POWERSHELL POUR NETTOYAGE AUTOMATIQUE

```powershell
# Aller dans le repertoire du projet
cd "C:\Users\HP CORE i7 11TH GEN\CascadeProjects\ggr-credit-workflow"

# Supprimer les scripts temporaires
Remove-Item check_users.py, create_test_users.py, diagnostic_analyste.py -ErrorAction SilentlyContinue
Remove-Item fix_all_indentation.py, fix_client_namespace.py, fix_demande_start.py -ErrorAction SilentlyContinue
Remove-Item fix_indentation.py, fix_missing_views.py, fix_namespaces.py -ErrorAction SilentlyContinue
Remove-Item fix_views_namespace.py, reset_all_passwords.py, reset_password.py -ErrorAction SilentlyContinue
Remove-Item setup_superadmin_portal.py, verifier_dossiers.py -ErrorAction SilentlyContinue

# Supprimer les scripts PowerShell temporaires
Remove-Item fix_encoding_complete.ps1, update_core_to_suivi_demande.ps1 -ErrorAction SilentlyContinue
Remove-Item update_core_to_suivi_demande_fixed.ps1 -ErrorAction SilentlyContinue

# Supprimer les scripts de test
Remove-Item test_dashboard_final.py, test_decimal_serialization.py -ErrorAction SilentlyContinue
Remove-Item test_demande_workflow.py, test_gestionnaire_workflow.py -ErrorAction SilentlyContinue
Remove-Item test_import.py, test_login_flow.py, test_portals.py, test_pro_login.py -ErrorAction SilentlyContinue

# Supprimer les fichiers en double dans core/
Remove-Item core\urls_client.py, core\urls_pro.py, core\wsgi_temp.py -ErrorAction SilentlyContinue

# Supprimer les fichiers temporaires
Remove-Item .env.local, db.sqlite3 -ErrorAction SilentlyContinue

# Supprimer la documentation obsolete
Remove-Item "CHAR centrale_OFFICIELLE.md", CORRECTIONS_NAMESPACE.md -ErrorAction SilentlyContinue
Remove-Item CORRECTION_DASHBOARD_GESTIONNAIRE.md, CORRECTION_DECIMAL_JSON.md -ErrorAction SilentlyContinue
Remove-Item CORRECTION_ERREUR_BOE.md, CORRECTION_FINALE_NAVIGATION.md -ErrorAction SilentlyContinue
Remove-Item DASHBOARD_SUPERADMIN_CLEAN.md, DEBUG_IMMEDIAT.md -ErrorAction SilentlyContinue
Remove-Item DIAGNOSTIC_DOSSIERS.md, INTEGRATION_LOGO.md, LOGO_AUTH_PAGES.md -ErrorAction SilentlyContinue
Remove-Item MIGRATION_STATUS.md, NOTIFICATION_ANALYSTES.md, PLAN_MEMOIRE.md -ErrorAction SilentlyContinue
Remove-Item PLAN_MODIFICATIONS_RAPPORTS.md, PORTAILS_SEPARES_GUIDE.md -ErrorAction SilentlyContinue
Remove-Item RECAP_SESSION_FINAL.md, RESUME_AMELIORATIONS.md -ErrorAction SilentlyContinue
Remove-Item RESUME_MIGRATION_PORTAILS.md, "RÉSUMÉ_CORRECTIONS.md" -ErrorAction SilentlyContinue
Remove-Item SERVER_STARTED.md, SOLUTION_ALLOWED_HOSTS.md, SOLUTION_ANALYSTE.md -ErrorAction SilentlyContinue
Remove-Item SOLUTION_BOE_NOTIFICATIONS.md, SOLUTION_CREATION_UTILISATEUR.md -ErrorAction SilentlyContinue
Remove-Item SOLUTION_FINALE_ALLOWED_HOSTS.md, SOLUTION_FINALE_DOSSIERS.md -ErrorAction SilentlyContinue
Remove-Item SOLUTION_MODIFICATIONS_RAPPORTS.md, SOLUTION_MODIFICATION_UTILISATEUR.md -ErrorAction SilentlyContinue
Remove-Item SOLUTION_NAMESPACE_PRO.md, SOLUTION_SIMPLE_FINALE.md -ErrorAction SilentlyContinue
Remove-Item SOLUTION_SIMPLE_LOCALHOST.md, SOLUTION_SUPER_ADMIN_FINAL.md -ErrorAction SilentlyContinue
Remove-Item TESTS_A_EFFECTUER.md, TEST_CREATION_UTILISATEUR.md -ErrorAction SilentlyContinue
Remove-Item TEST_NAVIGATION_SECTIONS.md, RECAP_FINAL_COMPLET.md -ErrorAction SilentlyContinue

Write-Host "Nettoyage termine! 65 fichiers supprimes."
```

## VERIFICATION APRES NETTOYAGE

Verifier que l'application fonctionne toujours:

```powershell
# Demarrer le serveur
python manage.py runserver 0.0.0.0:8002
```

Puis tester:
- http://localhost:8002/
- Connexion
- Dashboard
- Toutes les fonctionnalites

## FICHIERS A CONSERVER

- manage.py
- requirements.txt
- README.md
- .env
- .env.example
- .gitignore
- start_server.bat
- start_portals.ps1
- start_portals_simple.ps1
- core/ (sauf fichiers supprimes)
- suivi_demande/ (tous)
- templates/ (tous)
- static/ (tous)
- media/
- logs/
- ANALYSE_PROJET_COMPLETE.md (ce fichier)
- NETTOYAGE_PROJET.md (ce fichier)

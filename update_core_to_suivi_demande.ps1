# Script de mise à jour : core → suivi_demande
# Exécuter ce script après avoir renommé le dossier core en suivi_demande

Write-Host "🔄 MISE À JOUR DES RÉFÉRENCES CORE → SUIVI_DEMANDE" -ForegroundColor Cyan
Write-Host "=" * 60

$projectPath = "c:\Users\HP CORE i7 11TH GEN\CascadeProjects\ggr-credit-workflow"

# 1. Mettre à jour les fichiers Python avec imports
Write-Host "📝 Mise à jour des imports Python..." -ForegroundColor Yellow

$pythonFiles = @(
    "$projectPath\suivi_demande\management\commands\fix_user_profiles.py",
    "$projectPath\suivi_demande\management\commands\seed_demo.py", 
    "$projectPath\suivi_demande\test_notifications.py",
    "$projectPath\suivi_demande\tests\test_negative_cases.py",
    "$projectPath\suivi_demande\tests\test_transitions_notifications.py"
)

foreach ($file in $pythonFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        $content = $content -replace "from core\.", "from suivi_demande."
        $content = $content -replace "import core\.", "import suivi_demande."
        $content = $content -replace "'core'", "'suivi_demande'"
        Set-Content $file $content -NoNewline
        Write-Host "✓ Mis à jour: $file" -ForegroundColor Green
    }
}

# 2. Mettre à jour les templates HTML
Write-Host "`n📄 Mise à jour des templates HTML..." -ForegroundColor Yellow

$templateFiles = @(
    "$projectPath\templates\base.html",
    "$projectPath\templates\core\dashboard_analyste_pro.html",
    "$projectPath\templates\core\dashboard_base.html", 
    "$projectPath\templates\core\dashboard_client_pro.html",
    "$projectPath\templates\core\dashboard_gestionnaire.html",
    "$projectPath\templates\core\dashboard_responsable_ggr_pro.html",
    "$projectPath\templates\core\dossier_detail.html",
    "$projectPath\templates\emails\dossier_a_traiter.html",
    "$projectPath\templates\emails\dossier_update_client.html",
    "$projectPath\templates\emails\retour_client.html"
)

foreach ($file in $templateFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        $content = $content -replace "core/css/", "suivi_demande/css/"
        $content = $content -replace "core/js/", "suivi_demande/js/"
        $content = $content -replace "'core/", "'suivi_demande/"
        $content = $content -replace '"core/', '"suivi_demande/'
        Set-Content $file $content -NoNewline
        Write-Host "✓ Mis à jour: $file" -ForegroundColor Green
    }
}

# 3. Renommer le dossier templates/core en templates/suivi_demande
Write-Host "`n📁 Renommage du dossier templates..." -ForegroundColor Yellow
$oldTemplateDir = "$projectPath\templates\core"
$newTemplateDir = "$projectPath\templates\suivi_demande"

if (Test-Path $oldTemplateDir) {
    if (Test-Path $newTemplateDir) {
        Remove-Item $newTemplateDir -Recurse -Force
    }
    Rename-Item $oldTemplateDir $newTemplateDir
    Write-Host "✓ Renommé: templates\core → templates\suivi_demande" -ForegroundColor Green
}

# 4. Mettre à jour les références dans les nouveaux templates
Write-Host "`n🔄 Mise à jour des références internes..." -ForegroundColor Yellow

Get-ChildItem "$projectPath\templates\suivi_demande" -Filter "*.html" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'extends "core/', 'extends "suivi_demande/'
    $content = $content -replace 'include "core/', 'include "suivi_demande/'
    Set-Content $_.FullName $content -NoNewline
    Write-Host "✓ Mis à jour: $($_.Name)" -ForegroundColor Green
}

# 5. Créer les nouvelles migrations
Write-Host "`n🗄️ Création des nouvelles migrations..." -ForegroundColor Yellow
Set-Location $projectPath

try {
    python manage.py makemigrations suivi_demande
    Write-Host "✓ Migrations créées" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erreur lors de la création des migrations: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Vérification finale
Write-Host "`n🔍 Vérification finale..." -ForegroundColor Yellow

$remainingCoreRefs = Get-ChildItem $projectPath -Recurse -Include "*.py", "*.html" | 
    Select-String -Pattern "from core\.|import core\.|core/css/|core/js/" | 
    Where-Object { $_.Line -notmatch "#.*from core" }

if ($remainingCoreRefs) {
    Write-Host "⚠️ Références 'core' restantes trouvées:" -ForegroundColor Yellow
    $remainingCoreRefs | ForEach-Object {
        Write-Host "  $($_.Filename):$($_.LineNumber) - $($_.Line.Trim())" -ForegroundColor Red
    }
} else {
    Write-Host "✅ Aucune référence 'core' restante trouvée!" -ForegroundColor Green
}

Write-Host "`n🎉 MISE À JOUR TERMINÉE!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host "Prochaines étapes:" -ForegroundColor Cyan
Write-Host "1. Tester l'application: python manage.py runserver" -ForegroundColor White
Write-Host "2. Vérifier que tous les dashboards fonctionnent" -ForegroundColor White
Write-Host "3. Faire les migrations si nécessaire: python manage.py migrate" -ForegroundColor White

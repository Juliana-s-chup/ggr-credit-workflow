# 🧹 SCRIPT DE NETTOYAGE AUTOMATIQUE DU PROJET
# Auteur: Cascade AI
# Date: 11 Novembre 2025
# Description: Nettoie automatiquement les fichiers inutiles du projet

Write-Host "🧹 NETTOYAGE AUTOMATIQUE DU PROJET GGR CREDIT WORKFLOW" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Demander confirmation
$confirmation = Read-Host "⚠️  Ce script va supprimer des fichiers. Continuer? (O/N)"
if ($confirmation -ne 'O' -and $confirmation -ne 'o') {
    Write-Host "❌ Annulé par l'utilisateur" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "📋 ÉTAPE 1: Sauvegarde Git..." -ForegroundColor Yellow
git add .
git commit -m "Sauvegarde avant nettoyage automatique"
Write-Host "✅ Sauvegarde créée" -ForegroundColor Green
Write-Host ""

# Compteurs
$filesDeleted = 0
$foldersDeleted = 0

Write-Host "📋 ÉTAPE 2: Suppression des fichiers inutiles à la racine..." -ForegroundColor Yellow

# Liste des fichiers à supprimer
$filesToDelete = @(
    "README_PROFESSIONNEL.md",
    "DEMARRAGE_RAPIDE.md",
    "INDEX_DOCUMENTATION.md",
    "ORGANISATION_TERMINEE.md",
    "RÉSUMÉ_CORRECTIONS.md",
    "env.example",
    "test_logging.py",
    "nettoyer_projet.ps1",
    "organiser_docs.ps1",
    "organiser_docs_simple.ps1"
)

foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  🗑️  Supprimé: $file" -ForegroundColor Gray
        $filesDeleted++
    }
}

Write-Host "✅ Fichiers racine nettoyés ($filesDeleted fichiers)" -ForegroundColor Green
Write-Host ""

Write-Host "📋 ÉTAPE 3: Déplacement des scripts..." -ForegroundColor Yellow

# Créer le dossier scripts s'il n'existe pas
if (-not (Test-Path "scripts")) {
    New-Item -ItemType Directory -Path "scripts" | Out-Null
}

# Déplacer les scripts
$scriptsToMove = @(
    "start_portals.ps1",
    "start_portals_simple.ps1",
    "start_server.bat"
)

foreach ($script in $scriptsToMove) {
    if (Test-Path $script) {
        Move-Item $script "scripts/" -Force
        Write-Host "  📦 Déplacé: $script → scripts/" -ForegroundColor Gray
    }
}

Write-Host "✅ Scripts déplacés" -ForegroundColor Green
Write-Host ""

Write-Host "📋 ÉTAPE 4: Création du dossier ML models..." -ForegroundColor Yellow

if (-not (Test-Path "analytics\ml_models")) {
    New-Item -ItemType Directory -Path "analytics\ml_models" | Out-Null
    Write-Host "  📁 Créé: analytics\ml_models\" -ForegroundColor Gray
}

Write-Host "✅ Dossier ML créé" -ForegroundColor Green
Write-Host ""

Write-Host "📋 ÉTAPE 5: Nettoyage des fichiers Python temporaires..." -ForegroundColor Yellow

# Supprimer __pycache__
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force
    Write-Host "  🗑️  Supprimé: $($_.FullName)" -ForegroundColor Gray
    $foldersDeleted++
}

# Supprimer .pyc
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "  🗑️  Supprimé: $($_.FullName)" -ForegroundColor Gray
    $filesDeleted++
}

Write-Host "✅ Fichiers Python temporaires nettoyés" -ForegroundColor Green
Write-Host ""

Write-Host "📋 ÉTAPE 6: Nettoyage du dossier docs/..." -ForegroundColor Yellow

# Fichiers essentiels à garder dans docs/
$docsToKeep = @(
    "GUIDE_UTILISATEUR.md",
    "DOCKER_GUIDE.md",
    "PRODUCTION_READY_GUIDE.md",
    "CHAPITRE_6.5_DATA_ANALYST.md",
    "INTEGRATION_MODULE_ANALYTICS.md",
    "RESUME_MODULE_ANALYTICS.md",
    "CORRECTIONS_ANALYTICS.md",
    "COMMANDES_ANALYTICS.md",
    "ERREURS_RESOLUES.md",
    "AUDIT_COMPLET_PROJET.md",
    "API_DOCUMENTATION.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md"
)

# Créer un dossier archive pour les anciens docs
if (-not (Test-Path "docs\archive")) {
    New-Item -ItemType Directory -Path "docs\archive" | Out-Null
}

# Déplacer les fichiers non essentiels vers archive
Get-ChildItem -Path "docs" -File | Where-Object {
    $_.Name -notin $docsToKeep -and $_.Name -notlike "*.png" -and $_.Name -notlike "*.jpg"
} | ForEach-Object {
    Move-Item $_.FullName "docs\archive\" -Force
    Write-Host "  📦 Archivé: $($_.Name)" -ForegroundColor Gray
    $filesDeleted++
}

Write-Host "✅ Documentation nettoyée" -ForegroundColor Green
Write-Host ""

Write-Host "📋 ÉTAPE 7: Nettoyage des logs..." -ForegroundColor Yellow

if (Test-Path "logs") {
    Get-ChildItem -Path "logs" -Filter "*.log" | ForEach-Object {
        Remove-Item $_.FullName -Force
        Write-Host "  🗑️  Supprimé: $($_.Name)" -ForegroundColor Gray
        $filesDeleted++
    }
}

Write-Host "✅ Logs nettoyés" -ForegroundColor Green
Write-Host ""

Write-Host "📋 ÉTAPE 8: Création du fichier .gitignore optimisé..." -ForegroundColor Yellow

$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/staticfiles
/static_root

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Tests
.coverage
htmlcov/
.pytest_cache/
.tox/

# Docs archive
docs/archive/

# ML Models
analytics/ml_models/*.pkl
analytics/ml_models/*.joblib
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent
Write-Host "✅ .gitignore mis à jour" -ForegroundColor Green
Write-Host ""

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🎉 NETTOYAGE TERMINÉ !" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 RÉSUMÉ:" -ForegroundColor Cyan
Write-Host "  • Fichiers supprimés: $filesDeleted" -ForegroundColor White
Write-Host "  • Dossiers supprimés: $foldersDeleted" -ForegroundColor White
Write-Host "  • Scripts déplacés: 3" -ForegroundColor White
Write-Host "  • Dossiers créés: 2" -ForegroundColor White
Write-Host ""
Write-Host "📋 PROCHAINES ÉTAPES:" -ForegroundColor Yellow
Write-Host "  1. Vérifier que tout fonctionne: python manage.py runserver" -ForegroundColor White
Write-Host "  2. Créer les migrations: python manage.py makemigrations analytics" -ForegroundColor White
Write-Host "  3. Appliquer les migrations: python manage.py migrate" -ForegroundColor White
Write-Host "  4. Lancer les tests: python manage.py test" -ForegroundColor White
Write-Host ""
Write-Host "✅ Projet nettoyé et optimisé !" -ForegroundColor Green
Write-Host ""

# Commit final
Write-Host "📋 Création du commit final..." -ForegroundColor Yellow
git add .
git commit -m "Nettoyage automatique du projet - Suppression fichiers inutiles"
Write-Host "✅ Commit créé" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 TERMINÉ ! Le projet est maintenant propre et organisé." -ForegroundColor Green

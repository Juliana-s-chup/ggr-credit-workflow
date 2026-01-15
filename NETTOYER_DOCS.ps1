# 🧹 NETTOYAGE AUTOMATIQUE DE LA DOCUMENTATION
# Réduit de 75 à 18 fichiers essentiels

Write-Host "🧹 NETTOYAGE DOCUMENTATION" -ForegroundColor Cyan
Write-Host "=" * 60

# Fichiers essentiels à garder
$essentiels = @(
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
    "RAPPORT_AUDIT_FINAL.md",
    "API_DOCUMENTATION.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CORRECTIONS_CRITIQUES_FAITES.md",
    "ERREURS_DASHBOARD_CORRIGEES.md"
)

# Créer dossier archive
if (-not (Test-Path "docs\archive")) {
    New-Item -ItemType Directory -Path "docs\archive" | Out-Null
}

# Déplacer fichiers non essentiels
$moved = 0
Get-ChildItem -Path "docs" -File | Where-Object {
    $_.Name -notin $essentiels -and $_.Extension -eq ".md"
} | ForEach-Object {
    Move-Item $_.FullName "docs\archive\" -Force
    Write-Host "  📦 Archivé: $($_.Name)" -ForegroundColor Gray
    $moved++
}

Write-Host ""
Write-Host "✅ $moved fichiers archivés" -ForegroundColor Green
Write-Host "✅ $(($essentiels | Measure-Object).Count) fichiers essentiels conservés" -ForegroundColor Green

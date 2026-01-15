# 🧹 NETTOYAGE FICHIERS RACINE
# Réduit de 25 à 12 fichiers essentiels

Write-Host "🧹 NETTOYAGE FICHIERS RACINE" -ForegroundColor Cyan
Write-Host "=" * 60

# Fichiers à supprimer
$aSupprimer = @(
    "README_PROFESSIONNEL.md",
    "DEMARRAGE_RAPIDE.md",
    "INDEX_DOCUMENTATION.md",
    "ORGANISATION_TERMINEE.md",
    "RÉSUMÉ_CORRECTIONS.md",
    "env.example",
    "test_logging.py",
    "TOUT_FONCTIONNE.md",
    "CORRECTION_IMMEDIATE.md",
    "SQLITE_SUPPRIME.md",
    "DEMARRER_POSTGRESQL.md"
)

# Scripts à déplacer vers scripts/
$scriptsADeplacer = @(
    "start_portals.ps1",
    "start_portals_simple.ps1",
    "start_server.bat",
    "nettoyer_projet.ps1",
    "organiser_docs.ps1",
    "organiser_docs_simple.ps1"
)

# Supprimer fichiers inutiles
$deleted = 0
foreach ($file in $aSupprimer) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  🗑️  Supprimé: $file" -ForegroundColor Gray
        $deleted++
    }
}

# Créer dossier scripts s'il n'existe pas
if (-not (Test-Path "scripts")) {
    New-Item -ItemType Directory -Path "scripts" | Out-Null
}

# Déplacer scripts
$moved = 0
foreach ($script in $scriptsADeplacer) {
    if (Test-Path $script) {
        Move-Item $script "scripts\" -Force
        Write-Host "  📦 Déplacé: $script → scripts\" -ForegroundColor Gray
        $moved++
    }
}

Write-Host ""
Write-Host "✅ $deleted fichiers supprimés" -ForegroundColor Green
Write-Host "✅ $moved scripts déplacés" -ForegroundColor Green
Write-Host "✅ Racine nettoyée (12 fichiers essentiels)" -ForegroundColor Green

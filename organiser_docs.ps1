# Script pour organiser tous les documents dans docs/

Write-Host "📚 Organisation de la documentation..." -ForegroundColor Cyan

# Documents vers docs/archives/
$archives = @(
    "ANALYSE_PROJET_COMPLETE.md",
    "RAPPORT_ANALYSE_FINAL.md",
    "RAPPORT_AMELIORATIONS_PROJET.md",
    "NETTOYAGE_PROJET.md",
    "RAPPORT_NETTOYAGE.md",
    "RÉSUMÉ_CORRECTIONS.md",
    "REFACTORING_SESSION_1.md",
    "REFACTORING_SESSION_2.md",
    "REFACTORING_FINAL_REPORT.md",
    "PROGRESSION_REFACTORING.md"
)

Write-Host "`n📦 Déplacement vers docs/archives/..." -ForegroundColor Yellow
foreach ($file in $archives) {
    if (Test-Path $file) {
        Move-Item $file docs\archives\ -Force
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $file (déjà déplacé ou introuvable)" -ForegroundColor Gray
    }
}

# Documents à supprimer (doublons)
$supprimer = @(
    "README.md",
    "DOCUMENTATION_FINALE.md",
    "LIRE_MOI_IMPORTANT.md"
)

Write-Host "`n🗑️  Suppression des doublons..." -ForegroundColor Yellow
foreach ($file in $supprimer) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✓ $file supprimé" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $file (déjà supprimé ou introuvable)" -ForegroundColor Gray
    }
}

# Autres documents à archiver
$autres_archives = @(
    "CHAR centrale_OFFICIELLE.md"
)

Write-Host "`n📦 Autres documents vers archives..." -ForegroundColor Yellow
foreach ($file in $autres_archives) {
    if (Test-Path $file) {
        Move-Item $file docs\archives\ -Force
        Write-Host "  ✓ $file" -ForegroundColor Green
    }
}

Write-Host "`n✅ Organisation terminée!" -ForegroundColor Green
Write-Host "`n📁 Structure finale:" -ForegroundColor Cyan
Write-Host "  Racine: README_PROFESSIONNEL.md, DEMARRAGE_RAPIDE.md, INDEX_DOCUMENTATION.md"
Write-Host "  docs/: 9 documents techniques"
Write-Host "  docs/soutenance/: 3 documents"
Write-Host "  docs/archives/: ~10 documents d historique"

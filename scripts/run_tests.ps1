# Script PowerShell pour lancer les tests avec couverture
# Usage: .\run_tests.ps1

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🚀 LANCEMENT DE LA SUITE DE TESTS COMPLÈTE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$ErrorCount = 0

# Fonction pour exécuter une commande et afficher le résultat
function Run-TestCommand {
    param(
        [string]$Command,
        [string]$Description
    )
    
    Write-Host "`n============================================================" -ForegroundColor Yellow
    Write-Host "🧪 $Description" -ForegroundColor Yellow
    Write-Host "============================================================`n" -ForegroundColor Yellow
    
    Invoke-Expression $Command
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n❌ ÉCHEC: $Description" -ForegroundColor Red
        return $false
    } else {
        Write-Host "`n✅ SUCCÈS: $Description" -ForegroundColor Green
        return $true
    }
}

# 1. Tests unitaires Django
$result1 = Run-TestCommand -Command "python manage.py test --verbosity=2" -Description "Tests unitaires Django"
if (-not $result1) { $ErrorCount++ }

# 2. Tests avec pytest et couverture
$result2 = Run-TestCommand -Command "pytest --cov=suivi_demande --cov=analytics --cov-report=html --cov-report=term-missing" -Description "Tests pytest avec couverture"
if (-not $result2) { $ErrorCount++ }

# 3. Vérification de la couverture minimale
$result3 = Run-TestCommand -Command "coverage report --fail-under=75" -Description "Vérification couverture >= 75%"
if (-not $result3) { $ErrorCount++ }

# 4. Génération du rapport HTML
$result4 = Run-TestCommand -Command "coverage html" -Description "Génération rapport HTML"
if (-not $result4) { $ErrorCount++ }

# Résumé final
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "📊 RÉSUMÉ DES TESTS" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$TotalTests = 4
$PassedTests = $TotalTests - $ErrorCount

Write-Host "✅ Tests réussis: $PassedTests/$TotalTests" -ForegroundColor Green
Write-Host "❌ Tests échoués: $ErrorCount/$TotalTests" -ForegroundColor Red

if ($ErrorCount -eq 0) {
    Write-Host "`n🎉 TOUS LES TESTS SONT PASSÉS !" -ForegroundColor Green
    Write-Host "`n📄 Rapport de couverture: htmlcov\index.html" -ForegroundColor Cyan
    
    # Ouvrir le rapport dans le navigateur
    $openReport = Read-Host "`nVoulez-vous ouvrir le rapport de couverture ? (O/N)"
    if ($openReport -eq "O" -or $openReport -eq "o") {
        Start-Process "htmlcov\index.html"
    }
    
    exit 0
} else {
    Write-Host "`n⚠️  CERTAINS TESTS ONT ÉCHOUÉ" -ForegroundColor Red
    exit 1
}

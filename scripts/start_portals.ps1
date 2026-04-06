# Script de démarrage des portails CLIENT et PROFESSIONNEL
# GGR Credit - Crédit du Congo

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEMARRAGE DES PORTAILS GGR CREDIT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Vérifier que nous sommes dans le bon répertoire
if (-Not (Test-Path "manage.py")) {
    Write-Host "[ERREUR] manage.py non trouve!" -ForegroundColor Red
    Write-Host "   Assurez-vous d'etre dans le repertoire du projet." -ForegroundColor Yellow
    exit 1
}

# Vérifier que l'environnement virtuel est activé
if (-Not $env:VIRTUAL_ENV) {
    Write-Host "[AVERTISSEMENT] Environnement virtuel non active" -ForegroundColor Yellow
    Write-Host "   Tentative d'activation..." -ForegroundColor Yellow
    
    if (Test-Path "venv\Scripts\Activate.ps1") {
        . .\venv\Scripts\Activate.ps1
        Write-Host "[OK] Environnement virtuel active" -ForegroundColor Green
    } else {
        Write-Host "[ERREUR] Impossible de trouver l'environnement virtuel" -ForegroundColor Red
        Write-Host "   Creez-le avec : python -m venv venv" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`nVerification du fichier hosts..." -ForegroundColor Yellow
$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$hostsContent = Get-Content $hostsPath -ErrorAction SilentlyContinue

if ($hostsContent -match "client.ggr-credit.local" -and $hostsContent -match "pro.ggr-credit.local") {
    Write-Host "[OK] Fichier hosts configure correctement" -ForegroundColor Green
} else {
    Write-Host "[AVERTISSEMENT] Le fichier hosts n'est pas configure!" -ForegroundColor Yellow
    Write-Host "`n   Ajoutez ces lignes au fichier hosts (en ADMIN):" -ForegroundColor Yellow
    Write-Host "   $hostsPath`n" -ForegroundColor Cyan
    Write-Host "   127.0.0.1 client.ggr-credit.local" -ForegroundColor White
    Write-Host "   127.0.0.1 pro.ggr-credit.local`n" -ForegroundColor White
    
    $response = Read-Host "   Continuer quand meme ? (O/N)"
    if ($response -ne "O" -and $response -ne "o") {
        exit 0
    }
}

Write-Host "`nDemarrage des portails...`n" -ForegroundColor Yellow

# Fonction pour demarrer un portail
function Start-Portal {
    param(
        [string]$Name,
        [string]$Settings,
        [int]$Port,
        [string]$Color
    )
    
    $command = "python manage.py runserver 0.0.0.0:$Port --settings=$Settings"
    
    Write-Host "  >> Demarrage $Name sur port $Port..." -ForegroundColor $Color
    
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Write-Host ''; Write-Host '========================================' -ForegroundColor $Color; Write-Host '  $Name' -ForegroundColor $Color; Write-Host '========================================' -ForegroundColor $Color; Write-Host ''; cd '$PWD'; .\venv\Scripts\Activate.ps1; $command"
    )
}

# Démarrer le portail CLIENT
Start-Portal -Name "PORTAIL CLIENT" -Settings "core.settings.client" -Port 8001 -Color "Blue"
Start-Sleep -Seconds 2

# Démarrer le portail PROFESSIONNEL
Start-Portal -Name "PORTAIL PROFESSIONNEL" -Settings "core.settings.pro" -Port 8002 -Color "Yellow"

Write-Host "`n[OK] Les portails demarrent dans des fenetres separees`n" -ForegroundColor Green

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  PORTAIL CLIENT" -ForegroundColor Cyan
Write-Host "  URL: http://client.ggr-credit.local:8001/login/" -ForegroundColor White
Write-Host "  Compte test: client1 / demo1234" -ForegroundColor Gray
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  PORTAIL PROFESSIONNEL" -ForegroundColor Cyan
Write-Host "  URL: http://pro.ggr-credit.local:8002/login/" -ForegroundColor White
Write-Host "  Compte test: gest1 / demo1234" -ForegroundColor Gray
Write-Host "====================================================`n" -ForegroundColor Cyan

Write-Host "CONSEILS:" -ForegroundColor Yellow
Write-Host "  - Attendez 5-10 secondes que les serveurs demarrent" -ForegroundColor White
Write-Host "  - Verifiez les logs dans les fenetres ouvertes" -ForegroundColor White
Write-Host "  - Fermez les fenetres pour arreter les serveurs" -ForegroundColor White

# Documentation
# Write-Host "" -ForegroundColor White
# Write-Host "Documentation:" -ForegroundColor Yellow
# Write-Host "  - Guide complet: PORTAILS_SEPARES_GUIDE.md" -ForegroundColor White
# Write-Host "  - Resume migration: RESUME_MIGRATION_PORTAILS.md" -ForegroundColor White

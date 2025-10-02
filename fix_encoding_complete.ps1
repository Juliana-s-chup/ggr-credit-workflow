# Script de correction complète de l'encodage
Write-Host "🔧 CORRECTION COMPLÈTE DE L'ENCODAGE UTF-8" -ForegroundColor Cyan

$projectPath = "c:\Users\HP CORE i7 11TH GEN\CascadeProjects\ggr-credit-workflow"

# 1. Corriger tous les fichiers Python avec problèmes d'encodage
Write-Host "📝 Correction des fichiers Python..." -ForegroundColor Yellow

$pythonFiles = Get-ChildItem "$projectPath\suivi_demande" -Recurse -Filter "*.py"

foreach ($file in $pythonFiles) {
    try {
        # Lire avec différents encodages pour récupérer le contenu
        $content = $null
        
        try {
            $content = Get-Content $file.FullName -Encoding UTF8 -Raw -ErrorAction Stop
        } catch {
            try {
                $content = Get-Content $file.FullName -Encoding Default -Raw -ErrorAction Stop
            } catch {
                $content = Get-Content $file.FullName -Encoding ASCII -Raw -ErrorAction Stop
            }
        }
        
        if ($content) {
            # Corriger les caractères corrompus
            $content = $content -replace "d'�tat", "d'état"
            $content = $content -replace "r�le", "rôle" 
            $content = $content -replace "cr��", "créé"
            $content = $content -replace "�l�ment", "élément"
            $content = $content -replace "�", "é"
            $content = $content -replace "�", "è"
            $content = $content -replace "�", "à"
            $content = $content -replace "�", "ç"
            
            # Ajouter l'en-tête d'encodage si absent
            if (-not ($content -match "# -\*- coding: utf-8 -\*-")) {
                $content = "# -*- coding: utf-8 -*-`n" + $content
            }
            
            # Réécrire en UTF-8 propre
            [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.Encoding]::UTF8)
            Write-Host "✓ Corrigé: $($file.Name)" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ Erreur sur: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 2. Vérifier la syntaxe Python
Write-Host "`n🔍 Vérification de la syntaxe..." -ForegroundColor Yellow

try {
    $checkResult = python manage.py check 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Syntaxe Python correcte !" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreurs détectées:" -ForegroundColor Red
        Write-Host $checkResult -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Impossible de vérifier la syntaxe" -ForegroundColor Red
}

Write-Host "`n🎉 CORRECTION TERMINÉE !" -ForegroundColor Green
Write-Host "Testez maintenant avec: python manage.py runserver" -ForegroundColor Cyan

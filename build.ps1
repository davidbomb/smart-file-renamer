# Build script pour Smart File Renamer
# Génère un exécutable portable Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Smart File Renamer - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Python est installé
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "   Téléchargez Python: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ $pythonVersion détecté" -ForegroundColor Green

# Créer un environnement virtuel si nécessaire
if (-not (Test-Path "venv")) {
    Write-Host "📦 Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
}

# Activer l'environnement virtuel
Write-Host "🔄 Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Installer les dépendances
Write-Host "📥 Installation des dépendances..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Construire l'exécutable
Write-Host "🔨 Construction de l'exécutable..." -ForegroundColor Yellow
pyinstaller --onefile --console --name "SmartFileRenamer" --icon=NONE main.py --clean

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ BUILD RÉUSSI!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "L'exécutable se trouve ici:" -ForegroundColor White
    Write-Host "  dist\SmartFileRenamer.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Utilisation:" -ForegroundColor White
    Write-Host '  .\dist\SmartFileRenamer.exe "C:\Chemin\Vers\Musique"' -ForegroundColor Gray
    Write-Host '  .\dist\SmartFileRenamer.exe --help' -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "❌ Erreur lors de la construction" -ForegroundColor Red
    exit 1
}


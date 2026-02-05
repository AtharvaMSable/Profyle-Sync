# Quick Start Script for Smart Resume Analyzer
# Run this in PowerShell after configuring .env file

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Smart Resume Analyzer - Quick Start" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-CommandExists {
    param($command)
    $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
}

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
if (Test-CommandExists python) {
    $pythonVersion = python --version
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check .env file
Write-Host "`nChecking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
    
    # Check if configured
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "your_supabase_project_url_here" -or $envContent -match "your_supabase_anon_key_here") {
        Write-Host "⚠ .env file needs configuration!" -ForegroundColor Red
        Write-Host "  Please update SUPABASE_URL and SUPABASE_KEY" -ForegroundColor Yellow
        Write-Host "  See UPGRADE_GUIDE.md for instructions" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host "  Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host "⚠ Please configure it before continuing!" -ForegroundColor Yellow
    exit 1
}

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes)" -ForegroundColor Gray

try {
    pip install -r requirements.txt --quiet
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Some dependencies may have failed" -ForegroundColor Yellow
}

# Download spaCy model
Write-Host "`nDownloading spaCy model..." -ForegroundColor Yellow
try {
    python -m spacy download en_core_web_sm 2>$null
    Write-Host "✓ spaCy model downloaded" -ForegroundColor Green
} catch {
    Write-Host "⚠ spaCy model download may have failed" -ForegroundColor Yellow
}

# Download NLTK data
Write-Host "`nDownloading NLTK data..." -ForegroundColor Yellow
try {
    python -c "import nltk; nltk.download('stopwords', quiet=True)"
    Write-Host "✓ NLTK data downloaded" -ForegroundColor Green
} catch {
    Write-Host "⚠ NLTK download may have failed" -ForegroundColor Yellow
}

# Create directories
Write-Host "`nCreating directories..." -ForegroundColor Yellow
@('categorized_resumes', 'temp') | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
        Write-Host "✓ Created: $_" -ForegroundColor Green
    }
}

# Success message
Write-Host "`n================================================" -ForegroundColor Green
Write-Host "  ✓ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Setup Supabase database:" -ForegroundColor White
Write-Host "   - Open Supabase SQL Editor" -ForegroundColor Gray
Write-Host "   - Run: database/supabase_setup.sql" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the application:" -ForegroundColor White
Write-Host "   streamlit run app_upgraded.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Access in browser:" -ForegroundColor White
Write-Host "   http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation:" -ForegroundColor White
Write-Host "   - README.md" -ForegroundColor Gray
Write-Host "   - UPGRADE_GUIDE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Happy Analyzing! 🎉" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Offer to start the app
$response = Read-Host "Would you like to start the app now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "`nStarting Smart Resume Analyzer..." -ForegroundColor Green
    streamlit run app_upgraded.py
}

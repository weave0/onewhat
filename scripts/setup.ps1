#!/usr/bin/env pwsh
# Installation script for OneWhat Translation System

Write-Host "🚀 OneWhat Translation System - Installation" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Check for CUDA
Write-Host "Checking CUDA availability..." -ForegroundColor Yellow
$cudaAvailable = $false
try {
    nvidia-smi | Out-Null
    $cudaAvailable = $true
    Write-Host "✅ NVIDIA GPU detected" -ForegroundColor Green
} catch {
    Write-Host "⚠️  No NVIDIA GPU detected - will use CPU" -ForegroundColor Yellow
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install PyTorch with CUDA support if available
if ($cudaAvailable) {
    Write-Host "Installing PyTorch with CUDA support..." -ForegroundColor Yellow
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
} else {
    Write-Host "Installing PyTorch (CPU-only)..." -ForegroundColor Yellow
    pip install torch torchvision torchaudio
}

# Install core dependencies
Write-Host "Installing core dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install development dependencies
$installDev = Read-Host "Install development dependencies? (y/N)"
if ($installDev -eq "y" -or $installDev -eq "Y") {
    Write-Host "Installing development dependencies..." -ForegroundColor Yellow
    pip install -r requirements-dev.txt
}

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path models | Out-Null
New-Item -ItemType Directory -Force -Path cache | Out-Null
New-Item -ItemType Directory -Force -Path data | Out-Null
New-Item -ItemType Directory -Force -Path logs | Out-Null
Write-Host "✅ Directories created" -ForegroundColor Green

# Copy environment file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env file created - please configure as needed" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file already exists" -ForegroundColor Yellow
}

# Download models (optional)
$downloadModels = Read-Host "Download models now? This may take a while. (y/N)"
if ($downloadModels -eq "y" -or $downloadModels -eq "Y") {
    Write-Host "Downloading models..." -ForegroundColor Yellow
    python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('facebook/nllb-200-distilled-600M'); AutoModelForSeq2SeqLM.from_pretrained('facebook/nllb-200-distilled-600M')"
    Write-Host "✅ Models downloaded" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Configure .env file with your settings" -ForegroundColor White
Write-Host "3. Run the API: python -m uvicorn src.api.main:app --reload" -ForegroundColor White
Write-Host "4. Visit http://localhost:8000/docs for API documentation" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor Cyan

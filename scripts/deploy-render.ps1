#!/usr/bin/env pwsh
# Deploy OneWhat to Render using their API

Write-Host "🚀 Deploying OneWhat to Render..." -ForegroundColor Cyan
Write-Host ""

# Check if render.yaml exists
if (!(Test-Path "render.yaml")) {
    Write-Host "❌ render.yaml not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ render.yaml found" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Deployment Configuration:" -ForegroundColor Yellow
Write-Host "   Repository: https://github.com/weave0/onewhat"
Write-Host "   Service: onewhat-api"
Write-Host "   Runtime: Docker"
Write-Host "   Models: Whisper v3 Large + NLLB-200 + XTTS v2"
Write-Host "   Disk: 20GB for model storage"
Write-Host ""

Write-Host "🔗 To complete deployment:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open: https://dashboard.render.com/select-repo?type=web" -ForegroundColor White
Write-Host ""
Write-Host "2. Select repository: weave0/onewhat" -ForegroundColor White
Write-Host ""
Write-Host "3. Render will detect render.yaml automatically!" -ForegroundColor Green
Write-Host "   (All settings pre-configured)" -ForegroundColor Green
Write-Host ""
Write-Host "4. Just click 'Apply' or 'Create Web Service'" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Build time: 15-20 minutes (downloads AI models)" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Your URLs after deployment:" -ForegroundColor Cyan
Write-Host "   Backend:  https://onewhat-api.onrender.com" -ForegroundColor White
Write-Host "   Frontend: https://onewhat-translator.netlify.app" -ForegroundColor White
Write-Host ""

# Open browser
Write-Host "Opening Render dashboard..." -ForegroundColor Cyan
Start-Process "https://dashboard.render.com/select-repo?type=web"

Write-Host ""
Write-Host "✨ Ready to deploy!" -ForegroundColor Green

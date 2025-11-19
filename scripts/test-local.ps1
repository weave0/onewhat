# Local Docker Testing Script
# Run this after docker build completes

Write-Host "`n🐋 OneWhat Local Docker Test" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Check if image exists
Write-Host "🔍 Checking for Docker image..." -ForegroundColor Yellow
$image = docker images onewhat-api:latest --format "{{.Repository}}:{{.Tag}}"

if (-not $image) {
    Write-Host "❌ Docker image not found!" -ForegroundColor Red
    Write-Host "   Run: docker build -f infrastructure/docker/Dockerfile -t onewhat-api:latest ." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found image: $image" -ForegroundColor Green
Write-Host ""

# Stop any existing container
Write-Host "🧹 Cleaning up existing containers..." -ForegroundColor Yellow
docker stop onewhat-api 2>$null
docker rm onewhat-api 2>$null

# Run the container
Write-Host "🚀 Starting container..." -ForegroundColor Cyan
docker run -d `
    --name onewhat-api `
    -p 8000:8000 `
    -e WHISPER_MODEL=base `
    -e WHISPER_DEVICE=cpu `
    -e NMT_MODEL=facebook/nllb-200-distilled-600M `
    -e NMT_DEVICE=cpu `
    -e TTS_DEVICE=cpu `
    -e LOG_LEVEL=INFO `
    -e CORS_ORIGINS='["*"]' `
    onewhat-api:latest

Write-Host "✅ Container started!" -ForegroundColor Green
Write-Host ""

# Wait for startup
Write-Host "⏳ Waiting for API to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test health endpoint
Write-Host "🏥 Testing health endpoint..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "✅ Health check passed!" -ForegroundColor Green
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Health check failed (models may still be loading)" -ForegroundColor Yellow
    Write-Host "   Check logs: docker logs onewhat-api" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🎉 Container is running!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Useful commands:" -ForegroundColor Cyan
Write-Host "   View logs:    docker logs -f onewhat-api" -ForegroundColor White
Write-Host "   Stop:         docker stop onewhat-api" -ForegroundColor White
Write-Host "   Restart:      docker restart onewhat-api" -ForegroundColor White
Write-Host "   Remove:       docker rm -f onewhat-api" -ForegroundColor White
Write-Host ""
Write-Host "🌐 API Endpoints:" -ForegroundColor Cyan
Write-Host "   Health:       http://localhost:8000/health" -ForegroundColor Blue
Write-Host "   Docs:         http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "   Translate:    http://localhost:8000/translate" -ForegroundColor Blue
Write-Host ""
Write-Host "🧪 Test translation:" -ForegroundColor Cyan
Write-Host '   $audio = Get-Item "path\to\audio.mp3"' -ForegroundColor Gray
Write-Host '   $form = @{ audio = $audio; source_language = "en"; target_language = "es" }' -ForegroundColor Gray
Write-Host '   Invoke-RestMethod -Uri "http://localhost:8000/translate" -Method Post -Form $form' -ForegroundColor Gray
Write-Host ""
Write-Host "🌍 Open API docs:" -ForegroundColor Cyan
Start-Process "http://localhost:8000/docs"

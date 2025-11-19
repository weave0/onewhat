# Complete automated deployment script
# This will deploy everything to Render without manual clicking

param(
    [string]$RenderApiKey = $env:RENDER_API_KEY
)

Write-Host "🚀 OneWhat Complete Deployment Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Render API key exists
if (-not $RenderApiKey) {
    Write-Host "❌ RENDER_API_KEY not found in environment" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please get your Render API key:" -ForegroundColor Yellow
    Write-Host "1. Go to https://dashboard.render.com/account/api-tokens" -ForegroundColor Yellow
    Write-Host "2. Create a new API token" -ForegroundColor Yellow
    Write-Host "3. Run: `$env:RENDER_API_KEY = 'your-token-here'" -ForegroundColor Yellow
    Write-Host "4. Re-run this script" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Render API key found" -ForegroundColor Green
Write-Host ""

# Get owner ID
Write-Host "🔍 Fetching owner information..." -ForegroundColor Cyan
try {
    $headers = @{
        "Authorization" = "Bearer $RenderApiKey"
    }
    $ownerResponse = Invoke-RestMethod -Uri "https://api.render.com/v1/owners" -Headers $headers
    $ownerId = $ownerResponse.owner.id
    $ownerName = $ownerResponse.owner.name
    
    Write-Host "✅ Owner: $ownerName ($ownerId)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Failed to get owner ID" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Service configuration
$serviceName = "onewhat-api"
$repo = "https://github.com/weave0/onewhat"
$branch = "main"

# Create the service payload - using proper Render API v1 schema
$payload = @{
    type = "web_service"
    name = $serviceName
    ownerId = $ownerId
    repo = $repo
    autoDeploy = "yes"
    branch = $branch
    rootDir = ""
    dockerfilePath = "infrastructure/docker/Dockerfile"
    serviceDetails = @{
        env = "docker"
        healthCheckPath = "/health"
        envVars = @(
            @{ key = "WHISPER_MODEL"; value = "base" }
            @{ key = "WHISPER_DEVICE"; value = "cpu" }
            @{ key = "NMT_MODEL"; value = "facebook/nllb-200-distilled-600M" }
            @{ key = "NMT_DEVICE"; value = "cpu" }
            @{ key = "TTS_DEVICE"; value = "cpu" }
            @{ key = "LOG_LEVEL"; value = "INFO" }
            @{ key = "MAX_AUDIO_SIZE_MB"; value = "25" }
            @{ key = "MODEL_CACHE_DIR"; value = "/tmp/models" }
            @{ key = "CORS_ORIGINS"; value = '["https://onewhat-translator.netlify.app"]' }
        )
    }
} | ConvertTo-Json -Depth 10

Write-Host "📦 Creating Render service: $serviceName" -ForegroundColor Cyan
Write-Host "   Repository: $repo" -ForegroundColor Gray
Write-Host "   Branch: $branch" -ForegroundColor Gray
Write-Host "   Plan: Free" -ForegroundColor Gray
Write-Host ""

# Create the service
try {
    $headers = @{
        "Authorization" = "Bearer $RenderApiKey"
        "Content-Type" = "application/json"
    }
    
    Write-Host "DEBUG: Sending payload:" -ForegroundColor Yellow
    Write-Host $payload -ForegroundColor Gray
    Write-Host ""
    
    $response = Invoke-RestMethod -Uri "https://api.render.com/v1/services" -Method Post -Headers $headers -Body $payload -ErrorAction Stop -ResponseHeadersVariable respHeaders -StatusCodeVariable statusCode
    
    Write-Host "DEBUG: Response received" -ForegroundColor Yellow
    Write-Host ($response | ConvertTo-Json -Depth 10) -ForegroundColor Gray
    Write-Host ""
    
    $serviceId = $response.id
    $serviceUrl = $response.serviceDetails.url
    
    Write-Host "✅ Service created successfully!" -ForegroundColor Green
    Write-Host "   Service ID: $serviceId" -ForegroundColor Gray
    Write-Host "   URL: $serviceUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏱️  Deployment started - this will take 15-20 minutes" -ForegroundColor Yellow
    Write-Host "   Models will download on first run" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 Monitor deployment at:" -ForegroundColor Cyan
    Write-Host "   https://dashboard.render.com/web/$serviceId" -ForegroundColor Blue
    Write-Host ""
    Write-Host "🌐 Your API will be available at:" -ForegroundColor Cyan
    Write-Host "   $serviceUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Wait for deployment to complete (~15 min)" -ForegroundColor White
    Write-Host "   2. Open https://onewhat-translator.netlify.app" -ForegroundColor White
    Write-Host "   3. Click Settings → Enter API URL: $serviceUrl" -ForegroundColor White
    Write-Host "   4. Test with a short audio file!" -ForegroundColor White
    Write-Host ""
    
    # Open dashboard
    Start-Process "https://dashboard.render.com/web/$serviceId"
    
    # Save service info
    @{
        serviceId = $serviceId
        serviceUrl = $serviceUrl
        frontendUrl = "https://onewhat-translator.netlify.app"
        deployed = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    } | ConvertTo-Json | Out-File "o:\OneWhat\deployment-info.json"
    
    Write-Host "✅ Deployment info saved to deployment-info.json" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Failed to create service" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try to get more details from the error
    if ($_.ErrorDetails) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "   1. Invalid API key - get new one at https://dashboard.render.com/account/api-tokens" -ForegroundColor Gray
    Write-Host "   2. Repository access - make sure repo is public" -ForegroundColor Gray
    Write-Host "   3. Service name taken - try a different name" -ForegroundColor Gray
    exit 1
}

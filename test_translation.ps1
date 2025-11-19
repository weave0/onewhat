# Test Netlify serverless functions
$baseUrl = "https://onewhat-translator.netlify.app/api"

Write-Host "`n=== Testing Health Endpoint ===" -ForegroundColor Cyan
try {
    $healthResponse = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "✓ Health check passed" -ForegroundColor Green
    $healthResponse | ConvertTo-Json
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
}

Write-Host "`n=== Testing Translation Endpoint ===" -ForegroundColor Cyan
$translateBody = @{
    text = "Hello, how are you today?"
    sourceLanguage = "eng_Latn"
    targetLanguage = "spa_Latn"
} | ConvertTo-Json

try {
    $translateResponse = Invoke-RestMethod -Uri "$baseUrl/translate" -Method Post -Body $translateBody -ContentType "application/json"
    Write-Host "✓ Translation test passed" -ForegroundColor Green
    $translateResponse | ConvertTo-Json
} catch {
    Write-Host "✗ Translation test failed: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "`n=== Testing Transcription Endpoint ===" -ForegroundColor Cyan
# For transcription we'd need actual audio, so just test the endpoint exists
try {
    # This should fail with 400 (missing audioBase64), not 404
    $transcribeResponse = Invoke-RestMethod -Uri "$baseUrl/transcribe" -Method Post -Body "{}" -ContentType "application/json" -ErrorAction Stop
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✓ Transcribe endpoint exists (returned 400 as expected for empty body)" -ForegroundColor Green
    } else {
        Write-Host "✗ Transcribe endpoint test failed: $_" -ForegroundColor Red
    }
}

Write-Host "`n=== Tests Complete ===" -ForegroundColor Cyan

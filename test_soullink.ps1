Write-Host "=== SoulLink API Test ===" -ForegroundColor Cyan

# 1. Health
Write-Host "`n[1] Health Check" -ForegroundColor Yellow
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing).Content | ConvertFrom-Json | Format-List

# 2. Onboarding
Write-Host "`n[2] Onboarding" -ForegroundColor Yellow
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/onboarding" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{"name":"Bruce","age":"34","gender":"male"}' `
    -UseBasicParsing).Content | ConvertFrom-Json | Format-List

# 3. Roster
Write-Host "`n[3] Roster" -ForegroundColor Yellow
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/roster" `
    -Method GET `
    -UseBasicParsing).Content | ConvertFrom-Json | Select-Object -ExpandProperty roster | Format-Table name, archetype, affection

# 4. Chat
Write-Host "`n[4] Chat with Adrian" -ForegroundColor Yellow
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/chat" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{"bot_name":"Adrian","message":"Hello Adrian, how are you?"}' `
    -UseBasicParsing).Content | ConvertFrom-Json | Format-List

# 5. Progression
Write-Host "`n[5] Progression" -ForegroundColor Yellow
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/progression" `
    -Method POST `
    -UseBasicParsing).Content | ConvertFrom-Json | Format-List

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
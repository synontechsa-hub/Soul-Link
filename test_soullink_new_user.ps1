Write-Host "=== SoulLink Full API Test ===" -ForegroundColor Cyan

# 1. Health
Write-Host "`n[1] Health Check" -ForegroundColor Yellow
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing).Content | ConvertFrom-Json | Format-List

# 2. Onboarding
Write-Host "`n[2] Onboarding" -ForegroundColor Yellow
$onboarding = (Invoke-WebRequest -Uri "http://127.0.0.1:8000/onboarding" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{"name":"Bruce","age":"34","gender":"male"}' `
    -UseBasicParsing).Content | ConvertFrom-Json
$onboarding.user_state.profile | Format-List
Write-Host "Milestones:" $onboarding.user_state.milestones -ForegroundColor Green

# 3. Roster
Write-Host "`n[3] Roster" -ForegroundColor Yellow
$roster = (Invoke-WebRequest -Uri "http://127.0.0.1:8000/roster" `
    -Method GET `
    -UseBasicParsing).Content | ConvertFrom-Json
$roster.roster | Format-Table name, archetype, affection, unlocked

Write-Host "`nTotal bots loaded:" $roster.roster.Count -ForegroundColor Cyan

# 4. Chat
Write-Host "`n[4] Chat with Adrian" -ForegroundColor Yellow
$chat = (Invoke-WebRequest -Uri "http://127.0.0.1:8000/chat" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{"bot_name":"Adrian","message":"Hello Adrian, how are you?"}' `
    -UseBasicParsing).Content | ConvertFrom-Json
$chat | Format-List

# 5. Progression
Write-Host "`n[5] Progression" -ForegroundColor Yellow
$progression = (Invoke-WebRequest -Uri "http://127.0.0.1:8000/progression" `
    -Method POST `
    -UseBasicParsing).Content | ConvertFrom-Json
$progression | Format-List

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "Reminder: To simulate a restart test, stop and restart uvicorn, then rerun this script." -ForegroundColor Magenta
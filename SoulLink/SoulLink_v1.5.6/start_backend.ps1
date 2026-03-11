# SoulLink Backend Startup Script (Windows)
# Fixes UTF-8 encoding issues on Windows console

# Set UTF-8 encoding for Python
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Write-Host "Starting SoulLink Backend..." -ForegroundColor Cyan
Write-Host "Working Directory: $(Get-Location)" -ForegroundColor Gray

# Navigate to project root if needed
if (-not (Test-Path ".\backend")) {
    Write-Host "Error: backend directory not found!" -ForegroundColor Red
    Write-Host "   Please run this script from the SoulLink_v1.5.6 root directory." -ForegroundColor Yellow
    exit 1
}

# Activate local .venv
$venvActivate = ".\.venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
    Write-Host "Error: .venv not found! Run setup.ps1 first." -ForegroundColor Red
    exit 1
}
Write-Host "Activating .venv..." -ForegroundColor DarkCyan
& $venvActivate

# Check if .env exists
if (-not (Test-Path ".\.env")) {
    Write-Host "Warning: .env file not found!" -ForegroundColor Yellow
}

# Start the server
Write-Host "Starting uvicorn server..." -ForegroundColor Green
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# If server exits
Write-Host "`nServer stopped." -ForegroundColor Red

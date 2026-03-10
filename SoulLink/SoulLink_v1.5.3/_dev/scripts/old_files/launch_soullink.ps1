# ====================================================================
# SOULLINK - ONE-CLICK LAUNCHER
# ====================================================================
# Purpose: Launch the entire SoulLink stack (Backend + Frontend)
# Usage: Run this script from the project root
# Author: Architect (with Claude)
# ====================================================================

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "        SOULLINK v1.5.3 [PHOENIX] - INITIALIZATION" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Store the project root (assuming script is in _dev/scripts/)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

Write-Host "[1/5] Verifying project structure..." -ForegroundColor Yellow

# Check critical directories
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: backend/ directory not found!" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: frontend/ directory not found!" -ForegroundColor Red
    exit 1
}

Write-Host "      OK Project structure verified" -ForegroundColor Green

# Check for .env file
Write-Host "[2/5] Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "      WARNING: .env not found in project root!" -ForegroundColor Red
    Write-Host "      Creating from template..." -ForegroundColor Yellow
    
    if (Test-Path "_dev\.env_example.txt") {
        Copy-Item "_dev\.env_example.txt" ".env"
        Write-Host "      OK .env created. Please configure your API keys!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "      Press any key to open .env for editing, or Ctrl+C to cancel..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        notepad ".env"
        Write-Host ""
        Write-Host "      Press any key when ready to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    else {
        Write-Host "      ERROR: _dev\.env_example.txt template not found!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "      OK Environment configured" -ForegroundColor Green

# Start Backend
Write-Host "[3/5] Starting Backend Server (uvicorn)..." -ForegroundColor Yellow
Write-Host "      URL: http://localhost:8000" -ForegroundColor Cyan

$BackendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\backend'; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -PassThru -WindowStyle Normal

if ($BackendProcess) {
    Write-Host "      OK Backend process started (PID: $($BackendProcess.Id))" -ForegroundColor Green
}
else {
    Write-Host "      ERROR: Failed to start backend!" -ForegroundColor Red
    exit 1
}

# Wait for backend to initialize
Write-Host "      Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test backend health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5 -UseBasicParsing
    Write-Host "      OK Backend is responding" -ForegroundColor Green
}
catch {
    Write-Host "      WARNING Backend may still be starting... (check the backend window)" -ForegroundColor Yellow
}

Write-Host ""

# Start Frontend
Write-Host "[4/5] Starting Frontend (Flutter)..." -ForegroundColor Yellow
Write-Host "      This may take a moment on first run..." -ForegroundColor Cyan

$FrontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\frontend'; flutter run -d windows" -PassThru -WindowStyle Normal

if ($FrontendProcess) {
    Write-Host "      OK Frontend process started (PID: $($FrontendProcess.Id))" -ForegroundColor Green
}
else {
    Write-Host "      ERROR: Failed to start frontend!" -ForegroundColor Red
    Write-Host "      Cleaning up backend..." -ForegroundColor Yellow
    Stop-Process -Id $BackendProcess.Id -Force
    exit 1
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "                    SOULLINK IS NOW RUNNING" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "Frontend:     Running in separate window" -ForegroundColor White
Write-Host ""
Write-Host "Backend PID:  $($BackendProcess.Id)" -ForegroundColor Gray
Write-Host "Frontend PID: $($FrontendProcess.Id)" -ForegroundColor Gray
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "[5/5] Monitoring processes..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to shut down all processes." -ForegroundColor Red
Write-Host ""

# Keep this window open and monitor processes
try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if processes are still running
        if (-not (Get-Process -Id $BackendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host "WARNING Backend process has stopped!" -ForegroundColor Red
            break
        }
        if (-not (Get-Process -Id $FrontendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host "WARNING Frontend process has stopped!" -ForegroundColor Red
            break
        }
    }
}
finally {
    # Cleanup on exit
    Write-Host ""
    Write-Host "=====================================================================" -ForegroundColor Cyan
    Write-Host "                    SHUTTING DOWN SOULLINK" -ForegroundColor Yellow
    Write-Host "=====================================================================" -ForegroundColor Cyan
    
    if (Get-Process -Id $BackendProcess.Id -ErrorAction SilentlyContinue) {
        Write-Host "Stopping Backend (PID: $($BackendProcess.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $BackendProcess.Id -Force
        Write-Host "OK Backend stopped" -ForegroundColor Green
    }
    
    if (Get-Process -Id $FrontendProcess.Id -ErrorAction SilentlyContinue) {
        Write-Host "Stopping Frontend (PID: $($FrontendProcess.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $FrontendProcess.Id -Force
        Write-Host "OK Frontend stopped" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "SoulLink has been shut down. See you in Link City, Architect." -ForegroundColor Cyan
    Write-Host ""
}

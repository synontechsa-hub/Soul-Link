# Legion — Bootstrap Setup Script
# Run once after cloning or after purging .venv to recreate the environment

Write-Host "Setting up Legion environment..." -ForegroundColor Cyan

# Create .venv
if (Test-Path ".\.venv") {
    Write-Host ".venv already exists. Skipping creation." -ForegroundColor Yellow
} else {
    Write-Host "Creating .venv..." -ForegroundColor DarkCyan
    python -m venv .venv
}

# Activate and install
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor DarkCyan
& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "   Activate manually: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   Run with: reflex run" -ForegroundColor Gray

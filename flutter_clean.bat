@echo off
TITLE SoulLink - Flutter Clean
REM Navigates to the frontend, cleans, and closes window
powershell -Command "Set-Location 'D:\Coding\SoulLink_v1.5.0\flutter_fronted'; Write-Host '🧹 Cleaning Flutter Build Artifacts...' -ForegroundColor Cyan; flutter clean"
exit
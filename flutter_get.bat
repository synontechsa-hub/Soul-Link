@echo off
TITLE SoulLink - Pub Get
REM Navigates to the frontend, gets packages, and closes window
powershell -Command "Set-Location 'D:\Coding\SoulLink_v1.5.0\flutter_fronted'; Write-Host '📦 Fetching SoulLink Dependencies...' -ForegroundColor Green; flutter pub get"
exit
@echo off
title SoulLink Launcher

echo ================================
echo   Starting SoulLink Backend
echo ================================
echo.

REM --- Backend ---
start "SoulLink Backend" cmd /k ^
cd /d D:\Coding\SoulLink_v1.5.0\backend ^& ^
D:\Coding\.venv\Scripts\Activate.bat ^& ^
uvicorn main:app --reload

timeout /t 5 >nul

echo ================================
echo   Starting SoulLink Frontend
echo ================================
echo.

REM --- Frontend ---
start "SoulLink Frontend" cmd /k ^
cd /d D:\Coding\SoulLink_v1.5.0\flutter_fronted ^& ^
flutter run -d windows

echo.
echo SoulLink is launching...
echo You may minimize this window.
echo.
pause

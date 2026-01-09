@echo off
REM Batch file to run Flutter commands in PowerShell

powershell -NoExit -Command "Set-Location 'D:\Coding\SoulLink_v1.5.0\flutter_fronted'; flutter clean; flutter pub get; flutter run -d windows"

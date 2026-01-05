@echo off
REM Batch file to run the character loader unit test

echo ============================================
echo Running SoulLink Character Loader Tests...
echo ============================================

REM Activate virtual environment if you have one
REM call venv\Scripts\activate

python -m unittest tests\test_character_loader.py

echo.
echo Tests finished.
pause

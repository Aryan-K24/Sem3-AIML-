@echo off
title Versight - Standalone AI E-Commerce Auditor
color 0B

echo ========================================================
echo         VERSIGHT - FORENSIC AI E-COMMERCE AUDITOR
echo ========================================================
echo.
echo Starting local web server...
echo.

:: Check python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.9+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

:: Ensure dependencies
echo Checking dependencies...
pip install -r requirements.txt --quiet

echo.
echo Launching Versight Web Application...
start "" http://127.0.0.1:5000

python server.py

pause

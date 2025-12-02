@echo off
REM Quick setup script for Windows
REM สคริปต์ติดตั้งสำหรับ Windows

echo ===================================================================
echo   YOLO Inspection System - Windows Setup
echo ===================================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found!
    echo Please install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python found
python --version

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo [5/5] Installing requirements...
pip install -r requirements-windows.txt

echo.
echo ===================================================================
echo   Setup Complete!
echo ===================================================================
echo.
echo To run the application:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run: python main.py
echo.
echo Or use: run_windows.bat
echo.
pause

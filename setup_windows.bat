@echo off
REM Setup YOLO Inspection System on Windows
REM ติดตั้งระบบตรวจสอบคุณภาพ YOLO บน Windows

echo ===================================================================
echo   YOLO Inspection System - Setup
echo   ติดตั้งระบบตรวจสอบคุณภาพ YOLO
echo ===================================================================
echo.

REM Check Python version
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found!
    echo Please install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python found
python --version
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)
python -m venv venv
echo Virtual environment created!
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo [4/4] Installing dependencies...
echo This may take several minutes...
echo.

REM Install PyQt6 first (no build tools needed!)
echo Installing PyQt6...
pip install PyQt6>=6.5.0
echo.

REM Install other requirements
echo Installing remaining dependencies...
pip install -r requirements.txt
echo.

echo ===================================================================
echo   Setup Complete!
echo   ติดตั้งเสร็จสมบูรณ์!
echo ===================================================================
echo.
echo Next steps:
echo   1. Place your YOLO model in: models/yolov8_defect.pt
echo   2. Run the application: run_windows.bat
echo   3. Or activate venv and run: python main.py
echo.
echo To activate virtual environment manually:
echo   venv\Scripts\activate.bat
echo.
pause

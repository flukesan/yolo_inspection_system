@echo off
REM Alternative: Use Conda to install PyQt5
REM แก้ปัญหาโดยใช้ Conda (แนะนำที่สุด!)

echo ===================================================================
echo   Install PyQt5 with Conda
echo ===================================================================
echo.

echo Checking for conda...
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Conda not found!
    echo.
    echo Please install Miniconda from:
    echo https://docs.conda.io/en/latest/miniconda.html
    echo.
    echo After installing, run this script again.
    pause
    exit /b 1
)

echo Conda found!
echo.

REM Create conda environment
echo [1/4] Creating conda environment...
conda create -n yolo_inspection python=3.10 -y
echo.

REM Activate environment
echo [2/4] Activating environment...
call conda activate yolo_inspection
echo.

REM Install PyQt5 from conda-forge (pre-built binaries)
echo [3/4] Installing PyQt5...
conda install -c conda-forge pyqt -y
echo.

REM Install other packages
echo [4/4] Installing other dependencies...
pip install ultralytics opencv-python torch torchvision numpy pillow
pip install pymodbus requests pandas openpyxl matplotlib python-dateutil pyyaml
echo.

echo ===================================================================
echo   Installation Complete!
echo ===================================================================
echo.
echo To use:
echo   1. Activate environment: conda activate yolo_inspection
echo   2. Run: python main.py
echo.
pause

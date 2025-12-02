@echo off
REM Run YOLO Inspection System on Windows
REM สคริปต์รันโปรแกรมบน Windows

echo ===================================================================
echo   YOLO Inspection System
echo   ระบบตรวจสอบคุณภาพชิ้นงานแบบเรียลไทม์
echo ===================================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Error: Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Set Qt environment variables (fixes some Qt issues)
set QT_QPA_PLATFORM=windows
set QT_DEBUG_PLUGINS=0

REM Run application
echo.
echo Starting YOLO Inspection System...
echo.
python main.py

REM Keep window open if error occurs
if %errorlevel% neq 0 (
    echo.
    echo Error occurred!
    pause
)

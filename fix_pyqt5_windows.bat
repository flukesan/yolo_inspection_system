@echo off
REM Quick Fix for PyQt5 Installation on Windows
REM แก้ปัญหาการติดตั้ง PyQt5 โดยไม่ต้อง Build Tools

echo ===================================================================
echo   PyQt5 Installation Fix - No Build Tools Required
echo ===================================================================
echo.

echo This will install PyQt5 pre-built binaries (no compilation needed)
echo.

REM Upgrade pip first
echo [1/3] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Uninstall existing PyQt5 packages
echo [2/3] Removing existing PyQt5...
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip -y
echo.

REM Install pre-built PyQt5 (no build required)
echo [3/3] Installing PyQt5 pre-built wheels...
pip install --only-binary :all: PyQt5==5.15.9
echo.

echo ===================================================================
echo   Installation Complete!
echo ===================================================================
echo.
echo Test it:
echo   python debug_qt.py
echo.
echo If successful, run:
echo   python main.py
echo.
pause

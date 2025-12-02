@echo off
REM Convert project to PyQt6
REM แปลงโปรเจคจาก PyQt5 เป็น PyQt6

echo ===================================================================
echo   Convert to PyQt6
echo   แปลงจาก PyQt5 ไปเป็น PyQt6 (ติดตั้งง่ายกว่าบน Windows!)
echo ===================================================================
echo.

echo [1/4] Uninstalling PyQt5...
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip pyqtgraph -y
echo.

echo [2/4] Installing PyQt6...
pip install PyQt6 pyqtgraph
echo.

echo [3/4] Converting Python files...
python convert_to_pyqt6.py
echo.

echo [4/4] Testing installation...
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 works!')"
echo.

echo ===================================================================
echo   Conversion Complete!
echo ===================================================================
echo.
echo You can now run:
echo   python main.py
echo.
pause

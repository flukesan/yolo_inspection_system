# Windows Quick Fix Guide
## แก้ปัญหา Qt Platform Plugin บน Windows

## ⚠️ Error ที่เจอ

```
qt.qpa.plugin: Could not find the Qt platform plugin "windows" in ""
This application failed to start because no Qt platform plugin could be initialized.
```

---

## 🔧 วิธีแก้ (ลองตามลำดับ)

### วิธีที่ 1: ติดตั้ง PyQt5 ใหม่ (แนะนำ!) ⭐

```bash
# ลบ PyQt5 เดิม
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip -y

# ติดตั้งใหม่
pip install PyQt5==5.15.9

# หรือติดตั้งแบบเต็ม
pip install PyQt5==5.15.9 PyQt5-Qt5==5.15.2 PyQt5-sip==12.11.0
```

### วิธีที่ 2: ใช้ Virtual Environment (แนะนำมาก!)

```bash
# สร้าง virtual environment
python -m venv venv

# Activate
# Windows CMD
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# Git Bash
source venv/Scripts/activate

# ติดตั้ง dependencies
pip install --upgrade pip
pip install -r requirements.txt

# รันโปรแกรม
python main.py
```

### วิธีที่ 3: ติดตั้ง PyQt5 แบบเฉพาะเจาะจง

```bash
pip install PyQt5==5.15.9 --force-reinstall --no-cache-dir
```

### วิธีที่ 4: ตั้งค่า Environment Variable

```bash
# Windows CMD
set QT_QPA_PLATFORM_PLUGIN_PATH=%CONDA_PREFIX%\Library\plugins\platforms

# Windows PowerShell
$env:QT_QPA_PLATFORM_PLUGIN_PATH="$env:CONDA_PREFIX\Library\plugins\platforms"

# หรือหา path ที่ถูกต้อง
python -c "import PyQt5; import os; print(os.path.dirname(PyQt5.__file__))"
```

### วิธีที่ 5: ใช้ Anaconda/Conda (แนะนำสำหรับ Windows)

```bash
# Install Conda if not installed
# Download from: https://docs.conda.io/en/latest/miniconda.html

# Create environment
conda create -n yolo_inspection python=3.10
conda activate yolo_inspection

# Install PyQt5 from conda-forge
conda install -c conda-forge pyqt

# Install other packages
pip install -r requirements.txt

# Run
python main.py
```

---

## 📋 One-Line Quick Fix

```bash
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip -y && pip install PyQt5==5.15.9 && python main.py
```

---

## 🔍 ตรวจสอบการติดตั้ง

```bash
# ตรวจสอบ PyQt5 version
pip show PyQt5

# ตรวจสอบ plugins path
python -c "import PyQt5.QtCore; print(PyQt5.QtCore.QLibraryInfo.location(PyQt5.QtCore.QLibraryInfo.PluginsPath))"

# ตรวจสอบว่า plugins มีหรือไม่
python -c "import os, PyQt5; print(os.listdir(os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins', 'platforms')))"
```

---

## 🆘 ถ้ายังไม่ได้

### Option 1: ใช้ PySide6 แทน

แก้ไขไฟล์เหล่านี้เปลี่ยนจาก PyQt5 เป็น PySide6:

```bash
# ติดตั้ง PySide6
pip uninstall PyQt5 -y
pip install PySide6

# จะต้องแก้ไข imports ในไฟล์:
# - ui/main_window.py
# - ui/widgets/*.py
# เปลี่ยนจาก: from PyQt5.QtWidgets import ...
# เป็น: from PySide6.QtWidgets import ...
```

### Option 2: Run in Compatibility Mode

สร้างไฟล์ `run_windows.bat`:

```batch
@echo off
set QT_DEBUG_PLUGINS=1
set QT_QPA_PLATFORM=windows
python main.py
pause
```

### Option 3: Portable Python + PyQt5

ดาวน์โหลด WinPython ที่มี PyQt5 built-in:
- https://winpython.github.io/

---

## 📦 Requirements for Windows

สร้างไฟล์ `requirements-windows.txt`:

```
# YOLO Inspection System - Windows Requirements

# Deep Learning & Computer Vision
ultralytics>=8.0.0
opencv-python>=4.8.0
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
pillow>=10.0.0

# GUI - Fixed versions for Windows
PyQt5==5.15.9
PyQt5-Qt5==5.15.2
PyQt5-sip==12.11.0
pyqtgraph>=0.13.0

# Communication
pymodbus>=3.5.0
requests>=2.31.0

# Data Processing & Reporting
pandas>=2.0.0
openpyxl>=3.1.0
matplotlib>=3.7.0

# Utilities
python-dateutil>=2.8.0
pyyaml>=6.0.0
```

ติดตั้ง:
```bash
pip install -r requirements-windows.txt
```

---

## 🎯 แนะนำสำหรับ Windows

### Setup แบบที่ดีที่สุด:

```bash
# 1. ใช้ Virtual Environment
python -m venv venv
venv\Scripts\activate

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. ติดตั้ง PyQt5 เวอร์ชันที่ทำงานได้ดี
pip install PyQt5==5.15.9

# 4. ติดตั้ง packages อื่นๆ
pip install ultralytics opencv-python torch torchvision numpy pillow
pip install pymodbus requests pandas openpyxl matplotlib python-dateutil pyyaml

# 5. รันโปรแกรม
python main.py
```

---

## 🔧 Debug Steps

ถ้ายังไม่ได้ ให้รัน debug script นี้:

```python
# debug_qt.py
import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)

try:
    import PyQt5
    print("\nPyQt5 version:", PyQt5.QtCore.PYQT_VERSION_STR)
    print("PyQt5 location:", PyQt5.__file__)

    from PyQt5 import QtCore
    print("\nQt version:", QtCore.QT_VERSION_STR)

    plugins_path = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.PluginsPath)
    print("Plugins path:", plugins_path)

    import os
    if os.path.exists(plugins_path):
        platforms_path = os.path.join(plugins_path, 'platforms')
        if os.path.exists(platforms_path):
            print("Platform plugins:", os.listdir(platforms_path))
        else:
            print("ERROR: platforms folder not found!")
    else:
        print("ERROR: plugins path not found!")

except Exception as e:
    print("\nERROR:", e)
    import traceback
    traceback.print_exc()
```

รัน:
```bash
python debug_qt.py
```

---

## 💡 Tips

1. **ใช้ Conda** ถ้าเป็นไปได้ (ง่ายที่สุดบน Windows)
2. **ใช้ Virtual Environment** เสมอ
3. **ติดตั้ง PyQt5 เวอร์ชัน 5.15.9** (stable บน Windows)
4. **อย่าผสม pip และ conda** ใน environment เดียวกัน
5. **ตรวจสอบ PATH** ว่าไม่มี Python หลายตัวขัดแย้งกัน

---

## 🚀 Alternative: Run with Docker Desktop

ถ้าติดตั้งไม่สำเร็จ ใช้ Docker Desktop บน Windows:

```bash
# Install Docker Desktop for Windows
# https://www.docker.com/products/docker-desktop/

# Run container (with VcXsrv for GUI)
# 1. Install VcXsrv: https://sourceforge.net/projects/vcxsrv/
# 2. Start XLaunch (Disable access control)
# 3. Run:

set DISPLAY=host.docker.internal:0
docker-compose up yolo-inspection
```

---

**Last Updated:** 2025-12-02
**Platform:** Windows 10/11

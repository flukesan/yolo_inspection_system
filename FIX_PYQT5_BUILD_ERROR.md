# Windows PyQt5 Installation Problem Fix
## แก้ปัญหา "Microsoft Visual C++ 14.0 or greater is required"

## ⚠️ Error ที่เจอ

```
error: Microsoft Visual C++ 14.0 or greater is required.
Get it with "Microsoft C++ Build Tools":
https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**สาเหตุ:** pip พยายาม compile PyQt5-sip จาก source แต่ไม่มี C++ compiler

---

## 🚀 วิธีแก้ (เรียงตามความง่าย)

### วิธีที่ 1: ใช้ Pre-built Wheels (ง่ายที่สุด!) ⭐⭐⭐⭐⭐

```bash
# Pull code ล่าสุด
git pull

# Run fix script
fix_pyqt5_windows.bat
```

หรือ Manual:
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Uninstall existing
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip -y

# Install pre-built only (no compilation)
pip install --only-binary :all: PyQt5==5.15.9
```

**ทำไมถึงได้:** ใช้ `--only-binary :all:` บังคับให้ pip download pre-built wheels แทนที่จะ compile

---

### วิธีที่ 2: ใช้ Conda (แนะนำมาก!) ⭐⭐⭐⭐⭐

```bash
# 1. ติดตั้ง Miniconda
# Download: https://docs.conda.io/en/latest/miniconda.html

# 2. Run setup script
git pull
setup_conda_windows.bat

# 3. Activate และ run
conda activate yolo_inspection
python main.py
```

หรือ Manual:
```bash
# Create environment
conda create -n yolo_inspection python=3.10 -y
conda activate yolo_inspection

# Install PyQt5 (pre-built from conda-forge)
conda install -c conda-forge pyqt -y

# Install other packages
pip install ultralytics opencv-python torch torchvision
pip install numpy pillow pymodbus requests pandas openpyxl

# Run
python main.py
```

**ทำไมถึงดี:** Conda มี pre-built binaries สำเร็จรูป ไม่ต้อง compile เลย

---

### วิธีที่ 3: ติดตั้ง Visual C++ Build Tools (ถ้าจำเป็น)

```bash
# 1. Download Visual Studio Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 2. ติดตั้งและเลือก:
#    - Desktop development with C++
#    - MSVC v142 or later
#    - Windows 10/11 SDK

# 3. Restart computer

# 4. ติดตั้ง PyQt5 ปกติ
pip install PyQt5
```

**ข้อเสีย:** ใช้เวลานาน (4-6 GB download), ซับซ้อน

---

### วิธีที่ 4: ใช้ PySide6 แทน PyQt5

```bash
# Uninstall PyQt5
pip uninstall PyQt5 -y

# Install PySide6 (easier to install on Windows)
pip install PySide6
```

**แต่:** ต้องแก้ไข code เปลี่ยนจาก PyQt5 เป็น PySide6

---

## 📋 เปรียบเทียบวิธี

| วิธี | ความยาก | เวลา | ความเสถียร | แนะนำ |
|------|---------|------|------------|-------|
| **Pre-built Wheels** | ⭐ | 1 min | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Conda** | ⭐⭐ | 5 min | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Build Tools** | ⭐⭐⭐⭐⭐ | 30 min | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **PySide6** | ⭐⭐ | 5 min | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## ✅ แนะนำ: ใช้ Conda!

**ทำไม:**
- ✅ ติดตั้งง่าย
- ✅ มี pre-built binaries
- ✅ จัดการ packages ได้ดี
- ✅ ไม่มีปัญหา compatibility
- ✅ รองรับ scientific packages

**ขั้นตอน:**

```bash
# 1. Download Miniconda
# https://docs.conda.io/en/latest/miniconda.html
# เลือก: Windows, 64-bit, Python 3.10

# 2. Install (ติ๊กถูก "Add to PATH")

# 3. เปิด Anaconda Prompt

# 4. Run
conda create -n yolo_inspection python=3.10 -y
conda activate yolo_inspection
conda install -c conda-forge pyqt -y
pip install ultralytics opencv-python torch torchvision numpy pillow
pip install pymodbus requests pandas openpyxl matplotlib python-dateutil pyyaml

# 5. Navigate to project folder
cd path\to\yolo_inspection_system

# 6. Run
python main.py
```

---

## 🔧 Troubleshooting

### ถ้า pre-built wheels ไม่ได้

```bash
# ลอง version อื่น
pip install --only-binary :all: PyQt5==5.15.7

# หรือไม่ระบุ version
pip install --only-binary :all: PyQt5
```

### ถ้ายังไม่ได้

```bash
# ใช้ unofficial wheels (Christoph Gohlke)
# Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt5
# เลือก: PyQt5-5.15.9-cp310-cp310-win_amd64.whl

pip install PyQt5-5.15.9-cp310-cp310-win_amd64.whl
```

### ตรวจสอบ Python version

```bash
python --version
# ควรเป็น 3.8 - 3.11 (PyQt5 รองรับ)
```

---

## 📝 Quick Commands

### Pre-built Wheels (แนะนำถ้าไม่มี Conda)
```bash
python -m pip install --upgrade pip
pip install --only-binary :all: PyQt5==5.15.9
python debug_qt.py
```

### Conda (แนะนำที่สุด!)
```bash
conda create -n yolo_inspection python=3.10 -y
conda activate yolo_inspection
conda install -c conda-forge pyqt -y
pip install ultralytics opencv-python torch torchvision
```

---

## 🎯 Script ที่ใช้ได้

### ใหม่ที่เพิ่มเข้ามา:

1. **fix_pyqt5_windows.bat**
   - ติดตั้ง PyQt5 แบบ pre-built
   - ไม่ต้อง Build Tools

2. **setup_conda_windows.bat**
   - Setup ด้วย Conda อัตโนมัติ
   - สร้าง environment
   - ติดตั้ง dependencies

---

**แนะนำให้ลอง:**

```bash
# Pull code
git pull

# วิธีที่ 1: Pre-built
fix_pyqt5_windows.bat

# วิธีที่ 2: Conda (ดีที่สุด!)
setup_conda_windows.bat
```

---

**Last Updated:** 2025-12-02
**Issue:** Microsoft Visual C++ Build Tools Required
**Solution:** Use pre-built wheels or Conda

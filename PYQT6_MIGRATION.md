# PyQt5 vs PyQt6 Migration Guide
## เปรียบเทียบและวิธีเปลี่ยนไปใช้ PyQt6

## 🎯 ทำไมต้องเปลี่ยนเป็น PyQt6?

### ข้อดี:
1. ✅ **ไม่ต้อง Visual C++ Build Tools** - มี pre-built wheels ครบ
2. ✅ **ติดตั้งง่ายบน Windows** - `pip install PyQt6` เสร็จทันที
3. ✅ **ทันสมัยกว่า** - Qt 6.x (รองรับ features ใหม่)
4. ✅ **Performance ดีกว่า** - Optimized สำหรับ modern systems
5. ✅ **รองรับ Python 3.8+** ดีกว่า

### ข้อเสีย:
1. ⚠️ API เปลี่ยนบางส่วน (แต่ไม่มาก)
2. ⚠️ บาง packages อาจยังไม่รองรับ PyQt6 (แต่ส่วนใหญ่รองรับแล้ว)

---

## 📊 เปรียบเทียบ

| Feature | PyQt5 | PyQt6 |
|---------|-------|-------|
| **Build Tools ต้องการ** | ⚠️ บางครั้ง (Windows) | ✅ ไม่ต้อง |
| **ติดตั้งบน Windows** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Pre-built Wheels** | บางเวอร์ชัน | ทุก platform |
| **Qt Version** | Qt 5.15 | Qt 6.5+ |
| **Python Support** | 3.5-3.11 | 3.8+ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **API Stability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🔄 การเปลี่ยนแปลง

### 1. Imports

```python
# PyQt5
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

# PyQt6 (เปลี่ยนแค่ 5 → 6)
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
```

### 2. Enums (บางตัว)

```python
# PyQt5
Qt.AlignCenter
Qt.AlignLeft
QMessageBox.Yes

# PyQt6 (ใช้ได้ทั้ง 2 แบบ)
Qt.AlignCenter              # Backward compatible
Qt.AlignmentFlag.AlignCenter  # New style

QMessageBox.Yes             # Backward compatible
QMessageBox.StandardButton.Yes  # New style
```

### 3. exec() method

```python
# PyQt5
app.exec_()
dialog.exec_()

# PyQt6
app.exec()    # ไม่มี underscore
dialog.exec()
```

### 4. pyqtSignal

```python
# PyQt5 & PyQt6 (เหมือนกัน)
from PyQt5.QtCore import pyqtSignal  # เก่า
from PyQt6.QtCore import pyqtSignal  # ใหม่

class MyWidget(QWidget):
    clicked = pyqtSignal()  # เหมือนกัน
```

---

## 🚀 วิธีเปลี่ยนไปใช้ PyQt6

### วิธีที่ 1: ใช้ Script อัตโนมัติ (แนะนำ!)

```bash
# Pull code ล่าสุด
git pull

# Run conversion script
python convert_to_pyqt6.py

# หรือใช้ .bat file บน Windows
convert_to_pyqt6.bat
```

### วิธีที่ 2: แก้ไขเอง

1. **แก้ไข imports:**
   ```bash
   # ใช้ Find & Replace ใน VS Code / Editor
   Find: from PyQt5
   Replace: from PyQt6
   ```

2. **ติดตั้ง PyQt6:**
   ```bash
   pip uninstall PyQt5 -y
   pip install PyQt6
   ```

3. **แก้ exec_() เป็น exec():**
   ```bash
   Find: .exec_()
   Replace: .exec()
   ```

4. **ทดสอบ:**
   ```bash
   python main.py
   ```

---

## 📋 Step-by-Step Guide

### สำหรับ YOLO Inspection System:

```bash
# 1. Backup (optional)
git commit -am "Backup before PyQt6 migration"

# 2. Run converter
python convert_to_pyqt6.py

# 3. Uninstall PyQt5
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip -y

# 4. Install PyQt6
pip install PyQt6

# 5. Test
python debug_qt.py

# 6. Run
python main.py
```

---

## 🔍 Testing After Migration

```python
# test_pyqt6.py
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt
import sys

def test():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle('PyQt6 Test')
    window.setGeometry(100, 100, 400, 200)

    label = QLabel('PyQt6 Works! ✓', window)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setGeometry(0, 0, 400, 200)
    label.setStyleSheet('font-size: 24px; color: green;')

    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    test()
```

---

## ⚠️ ปัญหาที่อาจเจอ

### 1. pyqtgraph compatibility

```bash
# อาจต้องติดตั้งเวอร์ชันใหม่
pip install --upgrade pyqtgraph
```

### 2. Some enums not found

```python
# ถ้าเจอ AttributeError
# เปลี่ยนจาก:
Qt.AlignCenter

# เป็น:
Qt.AlignmentFlag.AlignCenter
```

### 3. Signal/Slot ทำงานไม่ถูก

```python
# ตรวจสอบว่า import ถูกต้อง
from PyQt6.QtCore import pyqtSignal, pyqtSlot
```

---

## 💡 Tips

1. **ใช้ backward compatible enums** - Qt.AlignCenter ยังใช้ได้ (ไม่ต้องใช้ AlignmentFlag)
2. **ทดสอบ UI แต่ละส่วน** - ให้แน่ใจว่าทำงานถูกต้อง
3. **ตรวจสอบ third-party libraries** - ว่ารองรับ PyQt6
4. **อ่าน migration guide** - https://www.riverbankcomputing.com/static/Docs/PyQt6/

---

## 📦 Requirements Changes

### PyQt5:
```txt
PyQt5==5.15.9
PyQt5-Qt5==5.15.2
PyQt5-sip==12.11.0
```

### PyQt6:
```txt
PyQt6>=6.5.0
# ไม่ต้องมี PyQt6-Qt6 และ PyQt6-sip แยก (รวมอยู่แล้ว)
```

---

## ✅ แนะนำหรือไม่?

### ✅ แนะนำเปลี่ยน ถ้า:
- กำลังเริ่มโปรเจคใหม่
- มีปัญหาติดตั้ง PyQt5 บน Windows
- ต้องการ performance ดีกว่า
- ต้องการ Qt 6 features

### ⚠️ อาจรอก่อน ถ้า:
- โปรเจคใหญ่มาก ใช้ PyQt5 มานาน
- ใช้ libraries ที่ยังไม่รองรับ PyQt6
- ทีมยังไม่พร้อมเปลี่ยน

---

## 🎯 สรุป

**สำหรับ YOLO Inspection System:**

PyQt6 **ดีกว่า** เพราะ:
1. ✅ ติดตั้งง่ายบน Windows (ไม่ต้อง Build Tools)
2. ✅ การเปลี่ยนแปลง minimal (แค่ imports ส่วนใหญ่)
3. ✅ มี converter script ให้แล้ว
4. ✅ ใช้ packages เดียวกัน (ultralytics, opencv, etc.)

**คำแนะนำ:** ลองเปลี่ยนดู ไม่ยาก!

```bash
python convert_to_pyqt6.py
pip uninstall PyQt5 -y && pip install PyQt6
python main.py
```

---

**Last Updated:** 2025-12-02
**Migration Difficulty:** ⭐⭐ (Easy)

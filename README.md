# YOLO Inspection System
## ระบบตรวจสอบคุณภาพชิ้นงานแบบเรียลไทม์

ระบบตรวจสอบคุณภาพบนไลน์ผลิตด้วย YOLOv8 พร้อมส่วนติดต่อผู้ใช้แบบเรียลไทม์

## คุณสมบัติหลัก

### 🎥 การจัดการกล้อง
- รองรับกล้อง USB (USB Camera)
- รองรับกล้อง RTSP/IP Camera
- ปรับแต่งความละเอียดและ FPS ได้
- แสดงผลแบบเรียลไทม์

### 🤖 การตรวจจับด้วย YOLO
- ใช้ YOLOv8 สำหรับการตรวจจับ defect
- ปรับแต่ง confidence threshold และ IoU threshold
- รองรับทั้ง CPU และ GPU (CUDA)
- แสดงผล bounding box และ class บนภาพ

### 📊 สถิติและรายงาน
- แสดงสถิติการตรวจสอบแบบเรียลไทม์
- นับจำนวน OK/NG และอัตราของเสีย
- สร้างรายงาน Excel แบบอัตโนมัติ
- บันทึกข้อมูลลงฐานข้อมูล SQLite

### 🔧 ฟีเจอร์เพิ่มเติม
- เชื่อมต่อกับ PLC ผ่าน Modbus TCP
- แจ้งเตือนเมื่อพบ defect
- บันทึก log และภาพ defect
- UI แบบ Dark Theme
- ใช้ **PyQt6** (ติดตั้งง่าย ไม่ต้อง Visual C++ Build Tools!)

## ความต้องการระบบ

- **Python**: 3.10 หรือสูงกว่า
- **OS**: Windows 10/11, Linux, macOS
- **RAM**: 4GB ขึ้นไป (แนะนำ 8GB)
- **GPU** (Optional): NVIDIA GPU with CUDA support

---

## 🚀 การติดตั้งบน Windows (แนะนำ)

### ขั้นตอนที่ 1: ติดตั้ง Python

ดาวน์โหลดและติดตั้ง Python 3.10+ จาก https://www.python.org/

### ขั้นตอนที่ 2: รัน Setup Script

```bash
setup_windows.bat
```

Script นี้จะ:
- สร้าง virtual environment
- ติดตั้ง PyQt6 (ไม่ต้อง Build Tools!)
- ติดตั้ง dependencies ทั้งหมด

### ขั้นตอนที่ 3: เตรียมโมเดล YOLO

วางไฟล์โมเดล `.pt` ใน `models/yolov8_defect.pt`

หรือดาวน์โหลดโมเดลตัวอย่าง:
```bash
venv\Scripts\activate
python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); model.save('models/yolov8_defect.pt')"
```

### ขั้นตอนที่ 4: รันโปรแกรม

```bash
run_windows.bat
```

หรือ:
```bash
venv\Scripts\activate
python main.py
```

---

## 🐧 การติดตั้งบน Linux/macOS

### 1. ติดตั้ง Dependencies

```bash
# สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate

# ติดตั้ง packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. เตรียมโมเดล YOLO

```bash
# วางโมเดลใน models/
cp your_model.pt models/yolov8_defect.pt

# หรือใช้โมเดลตัวอย่าง
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt').save('models/yolov8_defect.pt')"
```

### 3. รันโปรแกรม

```bash
python main.py
```

---

## 🐳 การใช้งานกับ Docker

### วิธีที่ 1: ใช้ Scripts (แนะนำ)

```bash
# Build และ Run
./scripts/build_docker.sh
./scripts/run_docker.sh

# หยุดการทำงาน
./scripts/stop_docker.sh
```

### วิธีที่ 2: Docker Compose

```bash
# Allow X11 forwarding (สำหรับ GUI)
xhost +local:docker

# Build และ Run
docker-compose up --build

# เสร็จแล้วยกเลิก X11
xhost -local:docker
```

### ใช้ GPU

```bash
# ติดตั้ง NVIDIA Container Toolkit ก่อน
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

./scripts/run_docker_gpu.sh
```

สำหรับข้อมูลเพิ่มเติมดูที่: [DOCKER.md](DOCKER.md)

---

## 📖 การใช้งาน

### 1. เชื่อมต่อกล้อง

- คลิกปุ่ม **"🎥 เชื่อมต่อกล้อง"**
- เลือกกล้อง:
  - **USB**: `0`, `1`, `2`, ... (camera index)
  - **RTSP**: `rtsp://username:password@ip:port/path`

### 2. โหลดโมเดล YOLO

- คลิกเมนู **"ไฟล์ → ตั้งค่าโมเดล"**
- เลือกไฟล์โมเดล `.pt`
- ปรับ confidence threshold (0.0 - 1.0)

### 3. เริ่มตรวจสอบ

- คลิกปุ่ม **"▶ เริ่มตรวจสอบ"**
- ระบบจะเริ่มตรวจจับ defect แบบเรียลไทม์
- ดูสถิติและผลลัพธ์ในแผง Statistics

### 4. ดูรายงาน

- คลิกปุ่ม **"📊 รายงาน"**
- เลือกช่วงเวลา
- Export เป็น Excel

---

## ⚙️ การตั้งค่า

การตั้งค่าจะถูกบันทึกใน `config/app_config.json`

### ตัวอย่างการตั้งค่า

```json
{
  "camera": {
    "default_source": 0,
    "width": 1280,
    "height": 720,
    "fps": 30
  },
  "yolo": {
    "model_path": "models/yolov8_defect.pt",
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "device": "cuda"
  },
  "inspection": {
    "auto_start": false,
    "save_defect_images": true,
    "defect_save_path": "data/defects"
  },
  "plc": {
    "enabled": false,
    "host": "192.168.1.100",
    "port": 502
  }
}
```

---

## 🗂️ โครงสร้างโปรเจค

```
yolo_inspection_system/
├── main.py                      # Entry point
├── requirements.txt             # Dependencies (PyQt6)
├── setup_windows.bat            # Windows setup script
├── run_windows.bat              # Windows run script
├── debug_qt.py                  # Qt diagnostic tool
├── config/
│   ├── settings.py             # การตั้งค่าระบบ
│   └── app_config.json         # User settings
├── core/
│   ├── camera_manager.py       # จัดการกล้อง USB/RTSP
│   ├── yolo_detector.py        # ตรวจจับด้วย YOLO
│   ├── inspection_engine.py    # Logic การตรวจสอบ
│   └── data_logger.py          # บันทึกข้อมูล
├── ui/
│   ├── main_window.py          # หน้าต่างหลัก (PyQt6)
│   ├── widgets/
│   │   ├── camera_view.py      # แสดงภาพกล้อง
│   │   ├── control_panel.py    # ควบคุมระบบ
│   │   ├── statistics_panel.py # แสดงสถิติ
│   │   └── alert_panel.py      # แจ้งเตือน
│   └── dialogs/
│       ├── camera_settings.py  # ตั้งค่ากล้อง
│       ├── model_settings.py   # ตั้งค่า YOLO
│       └── report_dialog.py    # สร้างรายงาน
├── models/
│   ├── yolov8_defect.pt        # โมเดล YOLO (ต้องเตรียมเอง)
│   └── class_names.txt         # ชื่อ class
├── utils/
│   ├── database.py             # จัดการ SQLite
│   ├── image_processor.py      # ประมวลผลภาพ
│   ├── plc_communication.py    # เชื่อมต่อ PLC
│   └── report_generator.py     # สร้างรายงาน
├── data/                        # ฐานข้อมูลและ logs
├── reports/                     # รายงาน Excel
└── resources/                   # Icons, sounds, styles
```

---

## 🔧 Troubleshooting

### ปัญหา: PyQt6 ไม่ติดตั้ง

```bash
# ตรวจสอบ Python version
python --version  # ควรเป็น 3.10+

# ติดตั้ง PyQt6 ใหม่
pip uninstall PyQt6 -y
pip install PyQt6
```

### ปัญหา: Qt platform plugin error

รัน debug script:
```bash
python debug_qt.py
```

### ปัญหา: กล้องเปิดไม่ได้

```bash
# Windows - ตรวจสอบ camera index
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"

# Linux - ตรวจสอบ video devices
ls /dev/video*
```

### ปัญหา: CUDA ไม่ทำงาน

```bash
# ตรวจสอบ PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# ถ้า False ให้ติดตั้ง PyTorch สำหรับ CUDA
# https://pytorch.org/get-started/locally/
```

ดู [TROUBLESHOOTING.md](TROUBLESHOOTING.md) สำหรับข้อมูลเพิ่มเติม

---

## 📦 Dependencies

### Core Libraries
- **ultralytics** >= 8.0.0 - YOLOv8
- **opencv-python** >= 4.8.0 - Computer Vision
- **torch** >= 2.0.0 - Deep Learning
- **PyQt6** >= 6.5.0 - GUI Framework (ไม่ต้อง Build Tools!)

### Data & Communication
- **pandas** >= 2.0.0 - Data Processing
- **openpyxl** >= 3.1.0 - Excel Reports
- **pymodbus** >= 3.5.0 - PLC Communication

### Utilities
- **matplotlib** >= 3.7.0 - Plotting
- **pyqtgraph** >= 0.13.0 - Real-time Plotting

ดูรายการทั้งหมดใน [requirements.txt](requirements.txt)

---

## 🎯 ฟีเจอร์ที่วางแผนไว้

- [ ] รองรับ Multi-Camera
- [ ] Cloud Dashboard
- [ ] AI Training Interface
- [ ] Mobile App Integration
- [ ] Advanced Analytics

---

## 📝 License

MIT License - ใช้งานได้อย่างอิสระ

---

## 🤝 Contributing

ยินดีรับ Pull Requests และ Issues!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

สำหรับคำถามและข้อเสนอแนะ กรุณาเปิด Issue ใน GitHub Repository

---

## 🙏 Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - YOLOv8 Framework
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI Framework
- [OpenCV](https://opencv.org/) - Computer Vision Library

---

**หมายเหตุ**: โปรเจคนี้ใช้ **PyQt6** แทน PyQt5 เพื่อความง่ายในการติดตั้งบน Windows (ไม่ต้อง Visual C++ Build Tools)

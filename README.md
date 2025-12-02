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

## โครงสร้างโปรเจค

```
yolo_inspection_system/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config/
│   ├── __init__.py
│   ├── settings.py        # การตั้งค่าระบบ
│   └── camera_profiles.json
├── core/
│   ├── __init__.py
│   ├── camera_manager.py  # จัดการกล้อง USB/RTSP
│   ├── yolo_detector.py   # ตรวจจับด้วย YOLO
│   ├── inspection_engine.py  # Logic การตรวจสอบ
│   └── data_logger.py     # บันทึกข้อมูล
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # หน้าต่างหลัก
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
│   ├── yolov8_defect.pt   # โมเดล YOLO (ต้องเตรียมเอง)
│   └── class_names.txt    # ชื่อ class
├── utils/
│   ├── __init__.py
│   ├── database.py        # จัดการ SQLite
│   ├── image_processor.py # ประมวลผลภาพ
│   ├── plc_communication.py  # เชื่อมต่อ PLC
│   └── report_generator.py   # สร้างรายงาน
└── resources/
    ├── icons/
    ├── sounds/
    └── styles/
```

## การติดตั้ง

### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 2. เตรียมโมเดล YOLO

วางไฟล์โมเดล YOLOv8 (.pt) ในโฟลเดอร์ `models/`:
```bash
models/yolov8_defect.pt
```

หรือโหลดโมเดลตัวอย่าง:
```bash
# ใช้โมเดล YOLOv8 pre-trained
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### 3. ปรับแต่งการตั้งค่า

แก้ไขไฟล์ `config/app_config.json` (จะถูกสร้างอัตโนมัติเมื่อรันครั้งแรก)

---

## 🐳 การใช้งานกับ Docker

### ความต้องการ

- Docker 20.10+
- Docker Compose 1.29+
- (Optional) NVIDIA Docker สำหรับ GPU

### วิธีที่ 1: ใช้ Scripts (แนะนำ)

#### รันด้วย CPU

```bash
# Build image
./scripts/build_docker.sh

# Run container
./scripts/run_docker.sh
```

#### รันด้วย GPU

```bash
# ติดตั้ง NVIDIA Docker runtime ก่อน
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Run container with GPU
./scripts/run_docker_gpu.sh
```

#### หยุดการทำงาน

```bash
./scripts/stop_docker.sh
```

### วิธีที่ 2: ใช้ Docker Compose โดยตรง

#### รันปกติ (CPU)

```bash
# Allow X11 forwarding
xhost +local:docker

# Build and run
docker-compose up --build yolo-inspection

# เมื่อเสร็จให้ยกเลิก X11 permission
xhost -local:docker
```

#### รันแบบ GPU

```bash
xhost +local:docker
docker-compose --profile gpu up --build yolo-inspection-gpu
xhost -local:docker
```

#### รันแบบ Headless (ไม่มี GUI)

```bash
docker-compose --profile headless up --build yolo-inspection-headless
```

### วิธีที่ 3: ใช้ Docker โดยตรง

```bash
# Build image
docker build -t yolo-inspection:latest .

# Run container
xhost +local:docker
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/reports:/app/reports \
  --device=/dev/video0:/dev/video0 \
  --network host \
  --privileged \
  yolo-inspection:latest

xhost -local:docker
```

### การใช้ Camera ใน Docker

Docker container สามารถเข้าถึงกล้อง USB ผ่าน device mapping:

```yaml
devices:
  - /dev/video0:/dev/video0  # กล้องตัวแรก
  - /dev/video1:/dev/video1  # กล้องตัวที่สอง
```

ตรวจสอบกล้องที่มี:
```bash
ls /dev/video*
```

### การใช้ RTSP Camera

สำหรับ RTSP camera ไม่ต้อง mount device แค่ตั้งค่า RTSP URL ในไฟล์ config:

```json
{
  "camera": {
    "default_source": "rtsp://admin:password@192.168.1.100:554/stream"
  }
}
```

### ข้อควรระวัง

1. **X11 Permission**: ต้อง run `xhost +local:docker` ก่อนเพื่อให้ container เข้าถึง X server
2. **Camera Access**: ต้องใช้ `--privileged` หรือ mount `/dev/video*` อย่างถูกต้อง
3. **GPU**: ต้องติดตั้ง NVIDIA Docker runtime สำหรับใช้ GPU
4. **Network**: ใช้ `network_mode: "host"` เพื่อให้เข้าถึง PLC/RTSP camera ได้ง่าย

### Volumes

Data ที่สำคัญถูก mount เป็น volumes:
- `./config` → การตั้งค่า
- `./data` → ฐานข้อมูล
- `./models` → โมเดล YOLO
- `./reports` → รายงาน
- `./logs` → Log files

---

## การใช้งาน

### รันโปรแกรม

```bash
python main.py
```

### ขั้นตอนการใช้งาน

1. **เชื่อมต่อกล้อง**
   - คลิกปุ่ม "🎥 เชื่อมต่อกล้อง"
   - เลือกกล้อง USB (0, 1, ...) หรือ RTSP URL

2. **โหลดโมเดล YOLO**
   - คลิกปุ่ม "📦 โหลดโมเดล"
   - เลือกไฟล์โมเดล .pt

3. **เริ่มการตรวจสอบ**
   - คลิกปุ่ม "▶ เริ่ม"
   - ระบบจะเริ่มตรวจสอบแบบเรียลไทม์

4. **ดูผลลัพธ์**
   - ดูภาพพร้อม bounding box ทางซ้าย
   - ดูสถิติทางขวา
   - ดู log การแจ้งเตือนด้านล่าง

5. **สร้างรายงาน**
   - คลิกปุ่ม "📊 สร้างรายงาน"
   - เลือกช่วงเวลา
   - รายงานจะถูกบันทึกในโฟลเดอร์ `reports/`

## การตั้งค่า

### การตั้งค่ากล้อง

```json
{
  "camera": {
    "default_source": 0,
    "width": 1280,
    "height": 720,
    "fps": 30
  }
}
```

### การตั้งค่า YOLO

```json
{
  "yolo": {
    "model_path": "models/yolov8_defect.pt",
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "device": "cuda"
  }
}
```

### การตั้งค่า PLC (Optional)

```json
{
  "plc": {
    "enabled": true,
    "ip_address": "192.168.1.10",
    "port": 502,
    "unit_id": 1
  }
}
```

## การเทรนโมเดล YOLO

### 1. เตรียมข้อมูล

สร้างโครงสร้างข้อมูลตามรูปแบบ YOLO:
```
dataset/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

### 2. สร้างไฟล์ dataset.yaml

```yaml
path: ./dataset
train: images/train
val: images/val

nc: 2  # จำนวน classes
names: ['OK', 'Defect']
```

### 3. เทรนโมเดล

```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolov8n.pt')

# Train
results = model.train(
    data='dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='defect_detection'
)

# Export
model.export(format='onnx')  # optional
```

## API Reference

### CameraManager

```python
from core import CameraManager

camera = CameraManager()
camera.connect(source=0, width=1280, height=720, fps=30)
frame = camera.get_frame()
camera.disconnect()
```

### YOLODetector

```python
from core import YOLODetector

detector = YOLODetector()
detector.load_model('models/yolov8_defect.pt', device='cuda')
detections = detector.detect(image)
annotated = detector.draw_detections(image, detections)
```

### InspectionEngine

```python
from core import InspectionEngine

engine = InspectionEngine(camera_manager, yolo_detector, data_logger)
engine.start()
result = engine.inspect_once()
stats = engine.get_statistics()
engine.stop()
```

## Troubleshooting

### ปัญหา: ไม่สามารถเชื่อมต่อกล้อง

```bash
# ตรวจสอบกล้องที่เชื่อมต่อ (Linux)
ls /dev/video*

# ตรวจสอบกล้องด้วย OpenCV
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### ปัญหา: CUDA out of memory

ลดขนาดรูปภาพหรือใช้ CPU:
```json
{
  "yolo": {
    "device": "cpu",
    "img_size": 320
  }
}
```

### ปัญหา: FPS ต่ำ

- ลด resolution ของกล้อง
- ใช้ GPU แทน CPU
- ปิด auto_save หรือ save_defect_only

## License

MIT License

## Credits

- YOLOv8: [Ultralytics](https://github.com/ultralytics/ultralytics)
- PyQt5: [Riverbank Computing](https://www.riverbankcomputing.com/software/pyqt/)
- OpenCV: [OpenCV](https://opencv.org/)

## Support

หากพบปัญหาหรือมีคำถาม:
- เปิด Issue บน GitHub
- ติดต่อทีมพัฒนา

---

**สร้างโดย:** AI Assistant
**เวอร์ชัน:** 1.0
**วันที่อัพเดทล่าสุด:** 2025-12-02

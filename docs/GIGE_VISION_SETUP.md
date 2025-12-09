# GigE Vision Camera Setup Guide

คู่มือการติดตั้งและใช้งานกล้อง GigE Vision กับระบบตรวจสอบคุณภาพ

## 📋 ข้อกำหนดระบบ

### 1. Hardware Requirements
- **Network Card**: Gigabit Ethernet (1000 Mbps)
- **Network Cable**: CAT5e หรือสูงกว่า
- **Camera**: GigE Vision compliant camera (Basler, Allied Vision, FLIR, etc.)

### 2. Software Requirements
- Python 3.10+
- Harvesters library (ติดตั้งอัตโนมัติผ่าน requirements.txt)
- GenTL Producer จาก camera vendor (.cti file)

---

## 🔧 การติดตั้ง

### ขั้นตอนที่ 1: ติดตั้ง Python Dependencies

```bash
pip install -r requirements.txt
```

### ขั้นตอนที่ 2: ติดตั้ง Camera Vendor SDK

เลือกติดตั้ง SDK ตาม vendor ของกล้อง:

#### **Basler Camera (แนะนำ)**
1. ดาวน์โหลด Pylon Software Suite จาก: https://www.baslerweb.com/en/downloads/software-downloads/
2. ติดตั้ง Pylon
3. GenTL Producer path:
   - **Linux**: `/opt/pylon/lib/gentlproducer.cti` หรือ `/opt/pylon/lib/pylonCXP/lib/gentlproducer.cti`
   - **Windows**: `C:\Program Files\Basler\pylon 7\Runtime\x64\ProducerGEV.cti`

#### **Allied Vision Camera**
1. ดาวน์โหลด Vimba SDK จาก: https://www.alliedvision.com/en/products/software/
2. ติดตั้ง Vimba SDK
3. GenTL Producer path:
   - **Linux**: `/opt/VimbaGigETL/bin/VimbaGigETL.cti`
   - **Windows**: `C:\Program Files\Allied Vision\VimbaGigETL\bin\VimbaGigETL.cti`

#### **FLIR/Point Grey Camera**
1. ดาวน์โหลด Spinnaker SDK จาก: https://www.flir.com/products/spinnaker-sdk/
2. ติดตั้ง Spinnaker SDK
3. GenTL Producer path:
   - **Linux**: `/opt/spinnaker/lib/flir-gentl/FLIR_GenTL.cti`
   - **Windows**: `C:\Program Files\FLIR Systems\Spinnaker\bin64\vs2015\FLIR_GenTL.cti`

### ขั้นตอนที่ 3: ตั้งค่า Network

1. เชื่อมต่อกล้องเข้ากับ Gigabit Ethernet port
2. ตั้งค่า network interface:
   - **IP Address**: Static IP (แนะนำ 192.168.1.x)
   - **Subnet Mask**: 255.255.255.0
   - **MTU Size**: 9000 (Jumbo Frames - แนะนำสำหรับประสิทธิภาพสูงสุด)

**Linux:**
```bash
# ตั้งค่า Static IP
sudo ifconfig eth0 192.168.1.10 netmask 255.255.255.0

# เปิดใช้ Jumbo Frames
sudo ifconfig eth0 mtu 9000
```

**Windows:**
1. Control Panel → Network and Sharing Center → Change adapter settings
2. Right-click network adapter → Properties
3. Internet Protocol Version 4 (TCP/IPv4) → Properties
4. ใส่ IP address และ subnet mask
5. Advanced → Configure → Jumbo Packet → Enable (9000 bytes)

---

## ⚙️ การตั้งค่าในระบบ

### วิธีที่ 1: ใช้ UI (แนะนำ)

1. เปิดแอปพลิเคชัน
2. ไปที่ **กล้อง** → **ตั้งค่ากล้อง**
3. เลือกประเภทกล้อง: **GigE Vision**
4. กรอกข้อมูล:
   - **GenTL Producer (.cti)**: เลือกไฟล์ .cti จาก SDK ที่ติดตั้ง
   - **Camera ID**:
     - `0` สำหรับกล้องตัวแรก
     - หรือ Serial Number
     - หรือ IP Address ของกล้อง
   - **Resolution**: ตั้งตามที่กล้องรองรับ
   - **FPS**: อัตราเฟรมที่ต้องการ
   - **Exposure**: เวลา exposure (microseconds)
   - **Gain**: ค่า gain

5. กดบันทึก

### วิธีที่ 2: แก้ไข config/settings.json

```json
{
  "camera": {
    "type": "gige",
    "gentl_path": "/opt/pylon/lib/gentlproducer.cti",
    "camera_id": 0,
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "exposure": 10000,
    "gain": 5
  }
}
```

### วิธีที่ 3: ใช้ Code

```python
from core import CameraManager

camera_manager = CameraManager()

# เชื่อมต่อด้วย camera index
camera_manager.connect(
    camera_type="gige",
    source={
        'gentl_path': '/opt/pylon/lib/gentlproducer.cti',
        'camera_id': 0
    },
    width=1920,
    height=1080,
    fps=30,
    exposure_time=10000,  # microseconds
    gain=5.0
)

# หรือเชื่อมต่อด้วย serial number
camera_manager.connect(
    camera_type="gige",
    source={
        'gentl_path': '/opt/pylon/lib/gentlproducer.cti',
        'camera_id': '12345678'  # camera serial number
    },
    width=1920,
    height=1080
)

# ดึงภาพ
frame = camera_manager.get_frame()
```

---

## 🔍 การแก้ไขปัญหา

### ปัญหา: ไม่พบกล้อง

**วิธีแก้:**
1. ตรวจสอบว่ากล้องเชื่อมต่อกับ network แล้ว (ดู LED บนกล้อง)
2. ตรวจสอบว่า IP address ของ PC และกล้องอยู่ใน subnet เดียวกัน
3. ปิด firewall ชั่วคราว
4. ใช้ vendor tool เช่น Pylon Viewer, Vimba Viewer เพื่อตรวจสอบว่าเห็นกล้องหรือไม่

### ปัญหา: Frame rate ต่ำ

**วิธีแก้:**
1. เปิดใช้ Jumbo Frames (MTU 9000)
2. ปิด Firewall หรือเพิ่ม exception สำหรับ GigE Vision
3. ลด resolution หรือ ROI
4. ตรวจสอบว่าใช้ Gigabit Ethernet (ไม่ใช่ 100 Mbps)

### ปัญหา: Dropped frames / Timeout

**วิธีแก้:**
1. เพิ่ม packet size
2. เพิ่ม network buffer size
3. ใช้ dedicated network card สำหรับกล้อง
4. ลด bandwidth (ลด fps หรือ resolution)

### ปัญหา: Import Error - Harvesters not found

**วิธีแก้:**
```bash
pip install harvesters genicam
```

---

## 📊 Camera Vendors และ GenTL Producer Paths

| Vendor | Product Line | Linux Path | Windows Path |
|--------|--------------|------------|--------------|
| Basler | ace, dart, pulse | `/opt/pylon/lib/gentlproducer.cti` | `C:\Program Files\Basler\pylon 7\Runtime\x64\ProducerGEV.cti` |
| Allied Vision | Manta, Prosilica | `/opt/VimbaGigETL/bin/VimbaGigETL.cti` | `C:\Program Files\Allied Vision\VimbaGigETL\bin\VimbaGigETL.cti` |
| FLIR | Blackfly, Oryx | `/opt/spinnaker/lib/flir-gentl/FLIR_GenTL.cti` | `C:\Program Files\FLIR Systems\Spinnaker\bin64\vs2015\FLIR_GenTL.cti` |
| JAI | GO, SP series | `/opt/jai/lib/libJAI_GenTL.cti` | `C:\Program Files\JAI\SDK\library\CPP\bin\GenTL_JAI_ENU_CLProtocol64.cti` |
| Matrix Vision | mvBlueCOUGAR | `/opt/mvIMPACT_Acquire/lib/x86_64/mvGenTLProducer.cti` | `C:\Program Files\MATRIX VISION\mvIMPACT Acquire\bin\x64\mvGenTLProducer.cti` |

---

## 🚀 Performance Tips

1. **Jumbo Frames**: เปิดใช้ MTU 9000 สำหรับ bandwidth สูงสุด
2. **Dedicated Network**: ใช้ network card แยกสำหรับกล้อง (ไม่ร่วมกับ internet)
3. **Static IP**: ใช้ Static IP เพื่อหลีกเลี่ยง DHCP delay
4. **Direct Connection**: เชื่อมกล้องตรงกับ PC (ไม่ผ่าน switch ถ้าเป็นไปได้)
5. **Interrupt Coalescing**: ปิด interrupt coalescing บน network card
6. **CPU Affinity**: ตั้ง process ให้ทำงานบน specific CPU cores

---

## 📚 Resources

- [Harvesters Documentation](https://github.com/genicam/harvesters)
- [GenICam Standard](https://www.emva.org/standards-technology/genicam/)
- [Basler Knowledge Base](https://www.baslerweb.com/en/support/knowledge-base/)
- [EMVA GigE Vision](https://www.emva.org/standards-technology/genicam/gige-vision/)

---

## ✅ ตรวจสอบว่าระบบพร้อมใช้งาน

```python
from core.camera_backends import GigEBackend

# ตรวจสอบว่า Harvesters ติดตั้งแล้ว
try:
    backend = GigEBackend()
    print("✓ GigE Vision พร้อมใช้งาน!")
except RuntimeError as e:
    print(f"✗ {e}")
```

---

สำหรับคำถามเพิ่มเติมหรือปัญหาเฉพาะเจาะจง กรุณาตรวจสอบ documentation ของ camera vendor ที่คุณใช้

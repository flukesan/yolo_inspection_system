# Docker Quick Fix Guide
## แก้ปัญหา Docker ด่วน

## ⚠️ Error ที่เจอ

### 1. DISPLAY variable is not set
```
WARNING: The DISPLAY variable is not set. Defaulting to a blank string.
```

### 2. ContainerConfig KeyError
```
KeyError: 'ContainerConfig'
```

---

## 🔧 วิธีแก้ (Quick Fix)

### ขั้นตอนที่ 1: ลบ Containers เก่า

```bash
# ลบ containers เก่าทั้งหมด
docker-compose down --remove-orphans
docker rm -f $(docker ps -aq --filter name=yolo) 2>/dev/null || true

# ลบ volumes (ถ้าจำเป็น)
docker volume prune -f
```

### ขั้นตอนที่ 2: Set DISPLAY Variable

```bash
# Set DISPLAY
export DISPLAY=:0

# หรือ ถ้าใช้ WSL2
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# ตรวจสอบ
echo $DISPLAY
```

### ขั้นตอนที่ 3: Allow X11

```bash
# Allow Docker access X server
xhost +local:docker
```

### ขั้นตอนที่ 4: Run ใหม่

```bash
# Run ด้วย script
./scripts/run_docker.sh

# หรือ run manual
export DISPLAY=:0
docker-compose up --build yolo-inspection
```

---

## 📋 One-Line Fix

รัน commands เหล่านี้ทีละบรรทัด:

```bash
cd yolo_inspection_system
docker-compose down --remove-orphans
docker rm -f $(docker ps -aq --filter name=yolo) 2>/dev/null || true
export DISPLAY=:0
xhost +local:docker
docker-compose up --build yolo-inspection
```

---

## 🚀 Alternative: ใช้ Docker Run โดยตรง

ถ้า docker-compose ยังมีปัญหา ใช้ docker run แทน:

```bash
# Set DISPLAY
export DISPLAY=:0
xhost +local:docker

# Build
docker build -t yolo-inspection:latest .

# Run
docker run -it --rm \
  --name yolo_inspection \
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

# Cleanup
xhost -local:docker
```

---

## 🔍 สาเหตุของปัญหา

### 1. DISPLAY not set
- Docker container ต้องการ DISPLAY variable เพื่อแสดง GUI
- ถ้าไม่ set จะไม่สามารถเชื่อมต่อ X server

### 2. ContainerConfig KeyError
- เกิดจาก container เก่าที่ image เปลี่ยนไป
- Docker Compose พยายาม reuse container แต่ config ไม่ตรงกัน
- **วิธีแก้:** ลบ container เก่าและสร้างใหม่

---

## ✅ Verification

ตรวจสอบว่าแก้ไขสำเร็จ:

```bash
# 1. ตรวจสอบ DISPLAY
echo $DISPLAY
# ควรได้: :0 หรือ <IP>:0

# 2. ตรวจสอบ containers
docker ps --filter name=yolo
# ควรเห็น container ที่กำลังรัน

# 3. ตรวจสอบ logs
docker logs yolo_inspection_system
# ควรไม่เห็น error
```

---

## 🔧 Scripts ที่ใช้แก้ปัญหา

### clean_docker.sh
```bash
./scripts/clean_docker.sh
```
ลบ containers, images, volumes เก่าทั้งหมด

### run_docker.sh (Updated)
```bash
./scripts/run_docker.sh
```
ตอนนี้จะ:
- Set DISPLAY อัตโนมัติ
- ลบ containers เก่า
- Allow X11
- Run container ใหม่

---

## 📱 Platform-Specific

### Linux
```bash
export DISPLAY=:0
xhost +local:docker
```

### macOS
```bash
# Install XQuartz first
brew install --cask xquartz

# Start XQuartz
open -a XQuartz

# Allow connections
xhost +localhost

# Set DISPLAY
export DISPLAY=host.docker.internal:0
```

### Windows WSL2
```bash
# Install VcXsrv or Xming

# Set DISPLAY
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# Allow connections
# (Configure in VcXsrv: Disable access control)
```

---

## 🆘 ถ้ายังไม่ได้

### Option 1: Clean Everything
```bash
# Nuclear option - ลบทุกอย่าง
docker-compose down -v
docker system prune -a --volumes
docker rmi $(docker images -q yolo*)

# Build ใหม่ทั้งหมด
docker-compose build --no-cache
docker-compose up
```

### Option 2: ใช้ Headless Mode
```bash
# รันโดยไม่มี GUI
docker-compose --profile headless up yolo-inspection-headless
```

### Option 3: Debug Mode
```bash
# Run แบบ interactive เพื่อ debug
docker run -it --rm yolo-inspection:latest /bin/bash

# ใน container
python3 -c "import os; print(os.environ.get('DISPLAY'))"
```

---

## 📝 Common Errors & Solutions

| Error | Solution |
|-------|----------|
| DISPLAY not set | `export DISPLAY=:0` |
| ContainerConfig | `docker-compose down && docker-compose up` |
| Permission denied | `xhost +local:docker` |
| Cannot connect to X | `xhost +SI:localuser:root` |
| Container already exists | `docker rm -f <container>` |

---

## 🎯 Best Practice

1. **ก่อนรันทุกครั้ง:**
   ```bash
   export DISPLAY=:0
   xhost +local:docker
   ```

2. **ใช้ scripts:**
   ```bash
   ./scripts/run_docker.sh  # จะทำทุกอย่างอัตโนมัติ
   ```

3. **หลังรันเสร็จ:**
   ```bash
   xhost -local:docker  # เพื่อความปลอดภัย
   ```

---

## 📞 Need More Help?

ถ้ายังแก้ไม่ได้:

1. รันคำสั่งนี้แล้วส่ง output มา:
   ```bash
   echo "=== Docker Info ===" >> debug.log
   docker --version >> debug.log
   docker-compose --version >> debug.log
   echo "=== DISPLAY ===" >> debug.log
   echo $DISPLAY >> debug.log
   echo "=== Containers ===" >> debug.log
   docker ps -a >> debug.log
   echo "=== Images ===" >> debug.log
   docker images >> debug.log
   cat debug.log
   ```

2. ดูใน **TROUBLESHOOTING.md** สำหรับรายละเอียดเพิ่มเติม

---

**Last Updated:** 2025-12-02
**Applies to:** Docker Compose 1.29.2+, Docker 20.10+

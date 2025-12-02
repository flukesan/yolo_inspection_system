# Troubleshooting Guide
## คู่มือแก้ไขปัญหา YOLO Inspection System

## 🐳 Docker Build Issues

### ปัญหา: Cannot install packages (Exit code 100)

**อาการ:**
```
failed to solve: process "/bin/sh -c apt-get update && apt-get install..."
did not complete successfully: exit code: 100
```

**สาเหตุ:**
- Package repository ไม่สามารถเข้าถึงได้
- Package ชื่อไม่ถูกต้องหรือไม่มีใน repository
- Network ไม่เสถียร

**แก้ไข:**

#### วิธีที่ 1: ใช้ Dockerfile อื่น

ระบบมี Dockerfile หลายแบบให้เลือก:

```bash
# ทดสอบ build ทั้งหมด
./scripts/test_docker_build.sh

# หรือทดสอบแบบ manual

# 1. ลอง Ubuntu-based (แนะนำ)
docker build -f Dockerfile.ubuntu -t yolo-inspection:ubuntu .

# 2. ลอง Minimal version
docker build -f Dockerfile.minimal -t yolo-inspection:minimal .

# 3. ถ้าได้ ให้เปลี่ยนเป็น Dockerfile หลัก
mv Dockerfile Dockerfile.old
mv Dockerfile.ubuntu Dockerfile  # หรือ Dockerfile.minimal
```

#### วิธีที่ 2: อัพเดท Package Lists

```bash
# Clear Docker cache
docker system prune -a

# Pull base image ใหม่
docker pull python:3.10-slim

# Build อีกครั้ง
docker build -t yolo-inspection .
```

#### วิธีที่ 3: แก้ Network Issues

```bash
# ใช้ DNS อื่น
docker build --network=host -t yolo-inspection .

# หรือตั้งค่า DNS ใน Docker daemon
sudo nano /etc/docker/daemon.json
```

เพิ่ม:
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

แล้ว restart:
```bash
sudo systemctl restart docker
```

#### วิธีที่ 4: Build แบบมี Cache

```bash
# Build without cache
docker build --no-cache -t yolo-inspection .
```

---

## 📦 Package Installation Issues

### ปัญหา: libxcb-* packages ไม่พบ

**อาการ:**
```
E: Unable to locate package libxcb-icccm4
```

**แก้ไข:**

ใช้ Dockerfile.ubuntu แทน:

```bash
# Dockerfile.ubuntu ใช้ Ubuntu base ที่มี packages ครบกว่า
docker build -f Dockerfile.ubuntu -t yolo-inspection .
```

หรือแก้ไข Dockerfile ลบ packages ที่ไม่จำเป็น:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make \
    libgl1 libglib2.0-0 libgomp1 \
    libx11-6 libxext6 libxrender1 \
    libsm6 libice6 \
    v4l-utils wget git \
    && rm -rf /var/lib/apt/lists/*
```

---

## 🖥️ GUI Issues

### ปัญหา: GUI ไม่แสดง / Qt platform plugin error

**อาการ:**
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

**แก้ไข:**

#### 1. ตรวจสอบ X11 Permission

```bash
# Allow Docker access
xhost +local:docker

# Run container
docker run ...

# Revoke when done
xhost -local:docker
```

#### 2. ตรวจสอบ DISPLAY Variable

```bash
# ตรวจสอบ
echo $DISPLAY

# ถ้าว่าง ให้ set
export DISPLAY=:0

# หรือ
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

#### 3. ติดตั้ง X11 Server

**Linux:**
```bash
# มีอยู่แล้วปกติ
```

**macOS:**
```bash
# Install XQuartz
brew install --cask xquartz

# Start XQuartz
open -a XQuartz

# Allow connections
xhost +localhost
```

**Windows (WSL2):**
```bash
# Install VcXsrv หรือ Xming
# Download จาก: https://sourceforge.net/projects/vcxsrv/

# ใน WSL2
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

#### 4. ใช้ Headless Mode

ถ้าไม่ต้องการ GUI:

```bash
# Run headless version
docker-compose --profile headless up yolo-inspection-headless

# หรือ set environment
docker run -e QT_QPA_PLATFORM=offscreen ...
```

---

## 📹 Camera Issues

### ปัญหา: ไม่สามารถเข้าถึงกล้อง

**อาการ:**
```
Cannot open camera: 0
Permission denied
```

**แก้ไข:**

#### 1. ตรวจสอบกล้อง

```bash
# ดูกล้องที่มี
ls -l /dev/video*

# Output ควรเป็น:
# crw-rw----+ 1 root video 81, 0 Dec  2 10:00 /dev/video0
```

#### 2. ให้ Permission

```bash
# วิธีที่ 1: chmod (temporary)
sudo chmod 666 /dev/video0

# วิธีที่ 2: เพิ่ม user ใน video group (permanent)
sudo usermod -aG video $USER

# Logout และ login ใหม่
```

#### 3. ตรวจสอบ Device Mapping

ใน `docker-compose.yml`:
```yaml
devices:
  - /dev/video0:/dev/video0
  - /dev/video1:/dev/video1  # ถ้ามีหลายกล้อง
```

#### 4. ใช้ Privileged Mode

```yaml
privileged: true
```

หรือ:
```bash
docker run --privileged --device=/dev/video0 ...
```

#### 5. ทดสอบกล้อง

```bash
# ทดสอบด้วย v4l2
v4l2-ctl --list-devices

# ทดสอบด้วย Python
python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

---

## 🎮 GPU Issues

### ปัญหา: GPU ไม่ถูกใช้งาน

**อาการ:**
```
CUDA not available
```

**แก้ไข:**

#### 1. ติดตั้ง NVIDIA Docker Runtime

```bash
# Add repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# Restart Docker
sudo systemctl restart docker
```

#### 2. ทดสอบ GPU

```bash
# ทดสอบ nvidia-smi
nvidia-smi

# ทดสอบใน Docker
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

#### 3. ใช้ GPU Profile

```bash
# ใช้ GPU version
./scripts/run_docker_gpu.sh

# หรือ
docker-compose --profile gpu up yolo-inspection-gpu
```

#### 4. ตรวจสอบ Runtime Config

```yaml
# ใน docker-compose.yml
services:
  yolo-inspection-gpu:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=all
```

---

## 🔌 PLC Connection Issues

### ปัญหา: ไม่สามารถเชื่อมต่อ PLC

**แก้ไข:**

#### 1. ใช้ Host Network

```yaml
network_mode: "host"
```

#### 2. ตรวจสอบ Firewall

```bash
# Allow Modbus TCP port (502)
sudo ufw allow 502/tcp
```

#### 3. ทดสอบการเชื่อมต่อ

```bash
# Ping PLC
ping 192.168.1.10

# ทดสอบ port
telnet 192.168.1.10 502
```

---

## 💾 Data Persistence Issues

### ปัญหา: ข้อมูลหายเมื่อ restart container

**แก้ไข:**

ตรวจสอบ volumes ใน `docker-compose.yml`:

```yaml
volumes:
  - ./config:/app/config
  - ./data:/app/data
  - ./models:/app/models
  - ./reports:/app/reports
```

สร้าง directories:
```bash
mkdir -p config data models reports logs
```

---

## 🐛 Common Python Errors

### ปัญหา: Module not found

**อาการ:**
```
ModuleNotFoundError: No module named 'ultralytics'
```

**แก้ไข:**

```bash
# Rebuild image
docker-compose build --no-cache

# หรือติดตั้ง manual
docker exec -it yolo_inspection_system pip install ultralytics
```

### ปัญหา: YOLO model not found

**แก้ไข:**

```bash
# ตรวจสอบว่า mount models folder ถูกต้อง
ls -la models/

# ควรมีไฟล์ .pt
# models/yolov8_defect.pt

# ถ้าไม่มี ให้ copy เข้าไป
cp your_model.pt models/yolov8_defect.pt
```

---

## 📊 Performance Issues

### ปัญหา: FPS ต่ำ

**แก้ไข:**

#### 1. ใช้ GPU

```bash
./scripts/run_docker_gpu.sh
```

#### 2. ลด Resolution

แก้ `config/app_config.json`:
```json
{
  "camera": {
    "width": 640,
    "height": 480
  }
}
```

#### 3. เพิ่ม Resources

```yaml
# ใน docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
```

---

## 🔍 Debug Tips

### เข้าไปใน Container

```bash
# Run container แบบ interactive
docker run -it --rm yolo-inspection:latest /bin/bash

# หรือเข้า container ที่กำลังรัน
docker exec -it yolo_inspection_system /bin/bash
```

### ดู Logs

```bash
# Docker logs
docker logs yolo_inspection_system

# Follow logs
docker logs -f yolo_inspection_system

# docker-compose logs
docker-compose logs -f
```

### ตรวจสอบ Processes

```bash
# ดู running containers
docker ps

# ดู images
docker images

# ดู volumes
docker volume ls
```

---

## 📞 Getting Help

ถ้ายังแก้ไขไม่ได้:

1. **รวบรวมข้อมูล:**
   ```bash
   docker version
   docker-compose version
   uname -a
   nvidia-smi  # ถ้ามี GPU
   ```

2. **Check logs:**
   ```bash
   docker logs yolo_inspection_system > docker.log
   cat docker.log
   ```

3. **Clean install:**
   ```bash
   docker-compose down
   docker system prune -a
   ./scripts/build_docker.sh
   ./scripts/run_docker.sh
   ```

---

## ✅ Quick Fixes Checklist

- [ ] ลอง Dockerfile.ubuntu แทน Dockerfile
- [ ] Run `xhost +local:docker`
- [ ] ตรวจสอบ `/dev/video*` permissions
- [ ] Clear Docker cache: `docker system prune -a`
- [ ] ใช้ host network: `network_mode: "host"`
- [ ] Rebuild: `docker-compose build --no-cache`
- [ ] ตรวจสอบ volumes mounting
- [ ] Test camera: `ls /dev/video*`
- [ ] Test GPU: `nvidia-smi`

---

**Last Updated:** 2025-12-02

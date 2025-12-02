# Docker Deployment Guide
## คู่มือการใช้งาน Docker สำหรับ YOLO Inspection System

## 🚀 Quick Start

### สำหรับผู้ใช้ทั่วไป (CPU)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd yolo_inspection_system

# 2. วางโมเดล YOLO
cp your_model.pt models/yolov8_defect.pt

# 3. Run!
./scripts/run_docker.sh
```

### สำหรับผู้ใช้ที่มี NVIDIA GPU

```bash
# 1. ติดตั้ง NVIDIA Docker runtime
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# 2. Run with GPU
./scripts/run_docker_gpu.sh
```

---

## 📋 ข้อกำหนด

### พื้นฐาน
- Docker 20.10 ขึ้นไป
- Docker Compose 1.29 ขึ้นไป
- Linux (Ubuntu 20.04+, Debian 11+, หรือ distro อื่นๆ)
- X11 Server (สำหรับ GUI)

### สำหรับ GPU (Optional)
- NVIDIA GPU with CUDA support
- NVIDIA Driver 470.57.02+
- NVIDIA Docker runtime

### การตรวจสอบข้อกำหนด

```bash
# ตรวจสอบ Docker
docker --version
docker-compose --version

# ตรวจสอบ NVIDIA GPU (ถ้ามี)
nvidia-smi

# ตรวจสอบ NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

---

## 🏗️ Architecture

### Docker Images

ระบบใช้ `python:3.10-slim` เป็น base image พร้อม dependencies:
- OpenCV
- PyQt5
- YOLOv8 (Ultralytics)
- และอื่นๆ ตาม requirements.txt

### Services

**1. yolo-inspection** (Default - CPU)
- รัน GUI บน X11
- ใช้ CPU สำหรับ inference
- Mount camera devices

**2. yolo-inspection-gpu** (GPU Profile)
- รัน GUI บน X11
- ใช้ NVIDIA GPU
- ต้องมี NVIDIA Docker runtime

**3. yolo-inspection-headless** (Headless Profile)
- รันโดยไม่มี GUI
- สำหรับ production/server
- บันทึกผลลงฐานข้อมูล

---

## 📁 Volumes

Data persistence ผ่าน Docker volumes:

| Host Path | Container Path | Description |
|-----------|----------------|-------------|
| `./config` | `/app/config` | การตั้งค่าระบบ |
| `./data` | `/app/data` | ฐานข้อมูล SQLite |
| `./models` | `/app/models` | โมเดล YOLO |
| `./reports` | `/app/reports` | รายงาน Excel/PDF |
| `./logs` | `/app/logs` | Log files |

---

## 🎮 การใช้งาน

### 1. Build Image

```bash
# ใช้ script
./scripts/build_docker.sh

# หรือใช้ docker-compose
docker-compose build yolo-inspection
```

### 2. Run Container

#### Option A: ใช้ Scripts (ง่ายที่สุด)

```bash
# CPU
./scripts/run_docker.sh

# GPU
./scripts/run_docker_gpu.sh

# Stop
./scripts/stop_docker.sh
```

#### Option B: ใช้ Docker Compose

```bash
# CPU version
xhost +local:docker
docker-compose up yolo-inspection
xhost -local:docker

# GPU version
xhost +local:docker
docker-compose --profile gpu up yolo-inspection-gpu
xhost -local:docker

# Headless version (no GUI)
docker-compose --profile headless up yolo-inspection-headless

# Stop all
docker-compose down
```

#### Option C: ใช้ Docker โดยตรง

```bash
# Build
docker build -t yolo-inspection:latest .

# Run
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

---

## 🎥 Camera Configuration

### USB Camera

```bash
# หากล้องที่มี
ls /dev/video*

# Output:
# /dev/video0
# /dev/video1
```

Mount ใน docker-compose.yml:
```yaml
devices:
  - /dev/video0:/dev/video0
  - /dev/video1:/dev/video1
```

### RTSP Camera

ไม่ต้อง mount device แค่ตั้งค่าใน `config/app_config.json`:

```json
{
  "camera": {
    "default_source": "rtsp://username:password@192.168.1.100:554/stream"
  }
}
```

---

## 🖥️ X11 Forwarding

### Linux

```bash
# Allow Docker to access X server
xhost +local:docker

# Run container...

# Revoke access when done
xhost -local:docker
```

### macOS

```bash
# Install XQuartz
brew install --cask xquartz

# Allow connections
xhost +localhost

# Get IP
IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')

# Run with display
docker run -e DISPLAY=$IP:0 ...
```

### Windows (WSL2)

```bash
# Install VcXsrv or Xming

# In WSL2
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# Run container
docker run -e DISPLAY=$DISPLAY ...
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DISPLAY` | `:0` | X11 display |
| `QT_X11_NO_MITSHM` | `1` | Fix Qt shared memory |
| `NVIDIA_VISIBLE_DEVICES` | `all` | GPU devices |
| `QT_QPA_PLATFORM` | `xcb` | Qt platform (offscreen for headless) |

---

## 🔧 Troubleshooting

### ปัญหา: GUI ไม่แสดง

```bash
# ตรวจสอบ X11 permission
xhost | grep "access control"

# Allow access
xhost +local:docker

# ตรวจสอบ DISPLAY variable
echo $DISPLAY
```

### ปัญหา: ไม่สามารถเข้าถึงกล้อง

```bash
# ตรวจสอบกล้อง
ls -l /dev/video*

# ให้ permission
sudo chmod 666 /dev/video0

# หรือเพิ่ม user เข้า video group
sudo usermod -aG video $USER
```

### ปัญหา: GPU ไม่ทำงาน

```bash
# ตรวจสอบ NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# ติดตั้ง NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### ปัญหา: Permission denied

```bash
# ให้ permission scripts
chmod +x scripts/*.sh

# Run as current user
docker-compose run --user $(id -u):$(id -g) yolo-inspection
```

---

## 🚀 Production Deployment

### 1. Headless Mode

สำหรับ production server ที่ไม่มี GUI:

```bash
# Run in background
docker-compose --profile headless up -d yolo-inspection-headless

# View logs
docker-compose logs -f yolo-inspection-headless

# Stop
docker-compose --profile headless down
```

### 2. Auto Restart

ตั้งค่า restart policy:

```yaml
services:
  yolo-inspection:
    restart: always  # หรือ unless-stopped
```

### 3. Resource Limits

จำกัด resources:

```yaml
services:
  yolo-inspection:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          memory: 4G
```

### 4. Logging

Configure logging:

```yaml
services:
  yolo-inspection:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 📊 Performance

### CPU Performance

- inference time: 50-200ms (ขึ้นอยู่กับ CPU)
- Recommended: 4+ cores

### GPU Performance

- inference time: 10-30ms (ขึ้นอยู่กับ GPU)
- Recommended: NVIDIA GTX 1060+

---

## 🔒 Security

### Best Practices

1. ไม่ใช้ `--privileged` ในproduction
2. Mount เฉพาะ devices ที่จำเป็น
3. ใช้ read-only volumes ที่เป็นไปได้
4. จำกัด network access
5. ใช้ non-root user

### Example Secure Configuration

```yaml
services:
  yolo-inspection:
    user: "1000:1000"
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CAP_SYS_ADMIN  # สำหรับ device access
```

---

## 📝 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [NVIDIA Docker](https://github.com/NVIDIA/nvidia-docker)
- [X11 Forwarding](https://wiki.ros.org/docker/Tutorials/GUI)

---

**Last Updated:** 2025-12-02

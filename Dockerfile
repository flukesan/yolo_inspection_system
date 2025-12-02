# Dockerfile for YOLO Inspection System - Optimized
# Fixed: sqlite3-python issue + smaller image size
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:0 \
    QT_X11_NO_MITSHM=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    gcc \
    g++ \
    make \
    # Core libraries for OpenCV
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    # X11 core
    libx11-6 \
    libxext6 \
    libxrender1 \
    libsm6 \
    libice6 \
    # Qt5 essentials
    libxcb1 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libfontconfig1 \
    libfreetype6 \
    # GStreamer for video
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    # Camera support
    v4l-utils \
    # Utilities
    wget \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
# Note: sqlite3 is built-in with Python, no need to install
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    ultralytics>=8.0.0 \
    opencv-python-headless>=4.8.0 \
    torch>=2.0.0 \
    torchvision>=0.15.0 \
    numpy>=1.24.0 \
    pillow>=10.0.0 \
    PyQt5>=5.15.0 \
    pyqtgraph>=0.13.0 \
    pymodbus>=3.5.0 \
    requests>=2.31.0 \
    pandas>=2.0.0 \
    openpyxl>=3.1.0 \
    matplotlib>=3.7.0 \
    python-dateutil>=2.8.0 \
    pyyaml>=6.0.0

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data \
    /app/models \
    /app/reports \
    /app/logs \
    /app/config

# Set permissions
RUN chmod +x /app/main.py

# Default command
CMD ["python", "main.py"]

# Dockerfile for YOLO Inspection System
# Optimized for stability and compatibility
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
    # Qt5 essentials (PyQt5 runtime dependencies)
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

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

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

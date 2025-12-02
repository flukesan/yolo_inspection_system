# Dockerfile for YOLO Inspection System
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # GUI dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    # PyQt5 dependencies
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    # Video device access
    v4l-utils \
    # Utilities
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

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

# Expose any ports if needed (for web interface in future)
# EXPOSE 8080

# Default command
CMD ["python", "main.py"]

"""
Multi-source Camera Capture Module.

Supports:
  - USB / Built-in webcam:    source=0, 1, ...
  - RTSP stream:              source="rtsp://user:pass@ip:554/stream"
  - IP Camera (HTTP/MJPEG):   source="http://ip:port/video"
  - GigE Vision (gstreamer):  source="gstreamer:aravissrc ..."
  - Video file (test):        source="/path/to/video.mp4"
"""

import cv2
import base64
import threading
import time
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class CameraConfig:
    source: str = "0"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    jpeg_quality: int = 65           # 0-100, lower = faster streaming
    reconnect_delay: float = 2.0      # seconds between reconnect attempts
    fallback_enabled: bool = True     # use color bars if camera unavailable


class CameraCapture:
    """Multi-source camera capture with auto-reconnect and fallback."""

    def __init__(self, config: CameraConfig):
        self.config = config
        self._cap: Optional[cv2.VideoCapture] = None
        self._lock = threading.Lock()
        self._last_frame: Optional[bytes] = None
        self._last_frame_ts: float = 0
        self._running = False
        self._source_type = self._detect_source(config.source)
        self._fallback_frame = self._generate_fallback()

    # ── source detection ──────────────────────────────────────────

    @staticmethod
    def _detect_source(source: str) -> str:
        """Detect camera source type from URI."""
        s = str(source).strip()
        if s.isdigit():
            return "usb"
        if s.startswith("rtsp://") or s.startswith("rtsps://"):
            return "rtsp"
        if s.startswith("http://") or s.startswith("https://"):
            return "http"
        if s.startswith("gstreamer:") or s.startswith("gst:"):
            return "gstreamer"
        if s.endswith(".mp4") or s.endswith(".avi") or s.endswith(".mkv"):
            return "file"
        return "unknown"

    # ── open / close ──────────────────────────────────────────────

    def open(self, timeout: float = 5.0) -> bool:
        """Open the configured camera source. Returns True on success.
        
        Args:
            timeout: Max seconds to wait for camera to open (USB cameras can hang).
        """
        result = [False]  # mutable for thread capture
        
        def _open():
            try:
                src = self.config.source
                if self._source_type == "gstreamer":
                    pipeline = src.split(":", 1)[1] if ":" in src else src
                    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
                elif self._source_type == "usb":
                    cap = cv2.VideoCapture(int(src))
                else:
                    cap = cv2.VideoCapture(src)

                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
                    cap.set(cv2.CAP_PROP_FPS, self.config.fps)
                    with self._lock:
                        self._close_unlocked()
                        self._cap = cap
                        self._running = True
                    result[0] = True
            except Exception:
                pass

        with self._lock:
            self._close_unlocked()

        # Run open in a thread with timeout (prevents hang on headless)
        t = threading.Thread(target=_open, daemon=True)
        t.start()
        t.join(timeout=timeout)

        if not result[0]:
            with self._lock:
                self._close_unlocked()
            return False

        return True

    def close(self):
        with self._lock:
            self._close_unlocked()
            self._running = False

    def _close_unlocked(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    @property
    def is_opened(self) -> bool:
        with self._lock:
            return self._cap is not None and self._cap.isOpened()

    # ── frame capture & encode ────────────────────────────────────

    def read_frame(self) -> Tuple[bool, Optional[bytes]]:
        """
        Read one frame, encode as JPEG, return (success, jpeg_bytes).
        Thread-safe.
        """
        with self._lock:
            if self._cap is None or not self._cap.isOpened():
                return False, None

            ret, frame = self._cap.read()
            if not ret or frame is None:
                return False, None

            # Resize if needed
            h, w = frame.shape[:2]
            if w != self.config.width or h != self.config.height:
                frame = cv2.resize(frame, (self.config.width, self.config.height))

            success, jpeg = cv2.imencode(
                ".jpg", frame,
                [cv2.IMWRITE_JPEG_QUALITY, self.config.jpeg_quality]
            )
            if not success:
                return False, None

            self._last_frame = jpeg.tobytes()
            self._last_frame_ts = time.time()
            return True, self._last_frame

    def read_base64(self) -> Tuple[bool, Optional[str]]:
        """Read frame and return as base64 string."""
        success, jpeg = self.read_frame()
        if success and jpeg:
            return True, base64.b64encode(jpeg).decode("ascii")
        return False, None

    # ── fallback frame ────────────────────────────────────────────

    @staticmethod
    def _generate_fallback() -> bytes:
        """Generate a 'No Signal' fallback frame."""
        import numpy as np
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Color bars (simple)
        colors = [
            (255, 255, 255),  # White
            (255, 255, 0),    # Cyan
            (0, 255, 0),      # Green
            (255, 0, 255),    # Magenta
            (0, 0, 255),      # Red
            (0, 255, 255),    # Yellow
            (255, 0, 0),      # Blue
            (0, 0, 0),        # Black
        ]
        bar_w = 640 // len(colors)
        for i, c in enumerate(colors):
            frame[:, i * bar_w:(i + 1) * bar_w] = c
        # Text
        cv2.putText(frame, "NO SIGNAL", (180, 260),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        cv2.putText(frame, "Camera disconnected", (130, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        success, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return jpeg.tobytes() if success else b""

    def get_fallback_base64(self) -> str:
        return base64.b64encode(self._fallback_frame).decode("ascii")

    # ── info ──────────────────────────────────────────────────────

    @property
    def info(self) -> dict:
        with self._lock:
            actual_w = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH) if self._cap else 0
            actual_h = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT) if self._cap else 0
            actual_fps = self._cap.get(cv2.CAP_PROP_FPS) if self._cap else 0
        return {
            "source": str(self.config.source),
            "type": self._source_type,
            "configured": f"{self.config.width}x{self.config.height}@{self.config.fps}fps",
            "actual": f"{int(actual_w)}x{int(actual_h)}@{actual_fps:.1f}fps",
            "connected": self.is_opened,
        }

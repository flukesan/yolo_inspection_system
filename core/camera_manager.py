"""
Camera Manager - จัดการกล้อง USB/RTSP/GigE Vision
Manages camera connections and frame capture with multiple backends
"""
import threading
from typing import Optional, Tuple, Dict, Any
import numpy as np
from .camera_backends import BaseCameraBackend, OpenCVBackend, GigEBackend


class CameraManager:
    """
    จัดการการเชื่อมต่อและการอ่านภาพจากกล้องหลายประเภท

    รองรับ:
    - USB Camera (OpenCV)
    - RTSP Camera (OpenCV)
    - IP Camera (OpenCV)
    - GigE Vision Camera (Harvesters/GenICam)
    """

    # Camera type constants
    TYPE_USB = "usb"
    TYPE_RTSP = "rtsp"
    TYPE_IP = "ip"
    TYPE_GIGE = "gige"

    def __init__(self):
        """Initialize Camera Manager"""
        self.backend: Optional[BaseCameraBackend] = None
        self.camera_type = None

    def connect(self, camera_type: str = TYPE_USB, source: Any = 0,
                width: int = 1280, height: int = 720, fps: int = 30,
                **kwargs) -> bool:
        """
        เชื่อมต่อกล้อง

        Args:
            camera_type: ประเภทกล้อง ("usb", "rtsp", "ip", "gige")
            source: Camera source
                - USB/RTSP/IP: 0, 1, ... for USB or URL string
                - GigE: dict {'gentl_path': '/path/to/producer.cti', 'camera_id': 0}
                       or just GenTL producer path string
            width: Frame width
            height: Frame height
            fps: Target FPS
            **kwargs: Additional camera parameters
                OpenCV: exposure, gain, buffer_size
                GigE: gentl_path, camera_id, exposure_time, gain

        Returns:
            True if successful

        Examples:
            # USB Camera
            manager.connect(camera_type="usb", source=0, width=1280, height=720)

            # RTSP Camera
            manager.connect(camera_type="rtsp", source="rtsp://192.168.1.100:554/stream")

            # GigE Vision Camera (Basler example)
            manager.connect(
                camera_type="gige",
                source={'gentl_path': '/opt/pylon/lib/gentlproducer.cti', 'camera_id': 0},
                width=1920, height=1080,
                exposure_time=10000,  # microseconds
                gain=5.0
            )
        """
        try:
            # Disconnect existing camera
            self.disconnect()

            # Create appropriate backend
            camera_type = camera_type.lower()

            if camera_type in [self.TYPE_USB, self.TYPE_RTSP, self.TYPE_IP]:
                print(f"สร้าง OpenCV backend สำหรับ {camera_type.upper()} camera")
                self.backend = OpenCVBackend()

            elif camera_type == self.TYPE_GIGE:
                print("สร้าง GigE Vision backend")
                try:
                    self.backend = GigEBackend()
                except RuntimeError as e:
                    print(f"✗ {e}")
                    return False

            else:
                print(f"✗ ไม่รองรับประเภทกล้อง: {camera_type}")
                print(f"  ประเภทที่รองรับ: {self.TYPE_USB}, {self.TYPE_RTSP}, {self.TYPE_IP}, {self.TYPE_GIGE}")
                return False

            # Connect using backend
            success = self.backend.connect(source, width, height, fps, **kwargs)

            if success:
                self.camera_type = camera_type
            else:
                self.backend = None
                self.camera_type = None

            return success

        except Exception as e:
            print(f"✗ Error in camera manager: {e}")
            import traceback
            traceback.print_exc()
            return False

    def disconnect(self) -> None:
        """ตัดการเชื่อมต่อกล้อง"""
        if self.backend is not None:
            self.backend.disconnect()
            self.backend = None
            self.camera_type = None

    def get_frame(self) -> Optional[np.ndarray]:
        """
        ดึงภาพล่าสุดจากกล้อง

        Returns:
            Frame หรือ None ถ้าไม่มี
        """
        if self.backend is not None:
            return self.backend.get_frame()
        return None

    def is_connected(self) -> bool:
        """
        ตรวจสอบว่ากล้องเชื่อมต่ออยู่หรือไม่

        Returns:
            True if connected
        """
        return self.backend is not None and self.backend.is_connected()

    def get_info(self) -> Dict[str, Any]:
        """
        ดึงข้อมูลกล้อง

        Returns:
            Camera information dictionary
        """
        if self.backend is not None:
            info = self.backend.get_info()
            info['camera_type'] = self.camera_type
            return info
        return {
            'camera_type': None,
            'connected': False
        }

    def capture_image(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        จับภาพนิ่ง

        Args:
            save_path: Path to save image (optional)

        Returns:
            Captured frame
        """
        if self.backend is not None:
            return self.backend.capture_image(save_path)
        return None

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.disconnect()

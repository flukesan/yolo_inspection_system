"""
Base Camera Backend - Abstract base class สำหรับ camera backends
Abstract interface for different camera types
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import numpy as np


class BaseCameraBackend(ABC):
    """Abstract base class สำหรับ camera backend ทุกประเภท"""

    def __init__(self):
        """Initialize camera backend"""
        self.is_connected_flag = False
        self.camera_info = {}

    @abstractmethod
    def connect(self, source: Any, width: int = 1280, height: int = 720,
                fps: int = 30, **kwargs) -> bool:
        """
        เชื่อมต่อกล้อง

        Args:
            source: Camera source (depends on backend type)
            width: Frame width
            height: Frame height
            fps: Target FPS
            **kwargs: Additional camera parameters

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """ตัดการเชื่อมต่อกล้อง"""
        pass

    @abstractmethod
    def get_frame(self) -> Optional[np.ndarray]:
        """
        ดึงภาพล่าสุดจากกล้อง

        Returns:
            Frame หรือ None ถ้าไม่มี
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        ตรวจสอบว่ากล้องเชื่อมต่ออยู่หรือไม่

        Returns:
            True if connected
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        ดึงข้อมูลกล้อง

        Returns:
            Camera information dictionary
        """
        pass

    def capture_image(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        จับภาพนิ่ง

        Args:
            save_path: Path to save image (optional)

        Returns:
            Captured frame
        """
        import cv2
        frame = self.get_frame()

        if frame is not None and save_path:
            cv2.imwrite(save_path, frame)
            print(f"✓ บันทึกภาพ: {save_path}")

        return frame

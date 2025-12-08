"""
ไฟล์การตั้งค่าระบบ
System Settings Configuration
"""
import json
import os
from typing import Dict, Any


class Settings:
    """จัดการการตั้งค่าระบบทั้งหมด"""

    DEFAULT_SETTINGS = {
        # Camera Settings
        "camera": {
            "default_source": 0,
            "width": 1280,
            "height": 720,
            "fps": 30,
            "rtsp_url": "",
            "default_profile": None  # Default camera profile name
        },

        # Camera Profiles (บันทึก camera settings ที่ใช้บ่อย)
        "camera_profiles": {
            # "Camera Name": {
            #     "type": "usb" or "rtsp",
            #     "source": 0 or "rtsp://...",
            #     "width": 1280,
            #     "height": 720,
            #     "fps": 30
            # }
        },

        # YOLO Model Settings
        "yolo": {
            "model_path": "models/yolov8_defect.pt",
            "confidence_threshold": 0.5,
            "iou_threshold": 0.45,
            "device": "cuda",  # cuda หรือ cpu
            "img_size": 640,
            "default_profile": None  # Default model profile name
        },

        # Model Profiles (บันทึก model settings สำหรับชิ้นงานต่างๆ)
        "model_profiles": {
            # "Profile Name": {
            #     "model_type": "detection" | "segmentation" | "classification" | "pose",
            #     "model_path": "models/yolov8_defect.pt",
            #     "device": "cpu" or "cuda",
            #     "confidence_threshold": 0.5,
            #     "iou_threshold": 0.45,
            #     "img_size": 640
            # }
        },

        # Inspection Settings
        "inspection": {
            "auto_save": True,
            "save_defect_only": True,
            "inspection_interval": 0.1,  # วินาที
            "alert_on_defect": True,
            "alert_sound": True
        },

        # Database Settings
        "database": {
            "path": "data/inspection.db",
            "auto_backup": True,
            "backup_interval": 24  # ชั่วโมง
        },

        # PLC Communication Settings
        "plc": {
            "enabled": False,
            "ip_address": "192.168.1.10",
            "port": 502,
            "unit_id": 1,
            "trigger_address": 0,
            "result_address": 1
        },

        # Report Settings
        "report": {
            "output_path": "reports/",
            "auto_generate": True,
            "interval": "daily",  # daily, weekly, monthly
            "format": "excel"  # excel, pdf
        },

        # UI Settings
        "ui": {
            "theme": "dark",
            "language": "th",
            "show_statistics": True,
            "show_log": True,
            "auto_scroll_log": True
        },

        # Snapshot Training Settings
        "snapshot_training": {
            "output_dir": "training_images",
            "image_size": "640x640",
            "file_prefix": "train_image",
            "resize_mode": "crop"  # letterbox, crop, stretch
        }
    }

    def __init__(self, config_file: str = "config/app_config.json"):
        """
        Initialize Settings

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load()

    def load(self) -> bool:
        """โหลดการตั้งค่าจากไฟล์"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self._update_nested_dict(self.settings, loaded_settings)
                print(f"✓ โหลดการตั้งค่าจาก {self.config_file}")
                return True
            else:
                print(f"! ไม่พบไฟล์ config ใช้ค่าเริ่มต้น")
                self.save()  # สร้างไฟล์ config ใหม่
                return False
        except Exception as e:
            print(f"✗ Error loading settings: {e}")
            return False

    def save(self) -> bool:
        """บันทึกการตั้งค่าลงไฟล์"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            print(f"✓ บันทึกการตั้งค่าไปยัง {self.config_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving settings: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        ดึงค่าการตั้งค่า

        Args:
            key_path: Path to setting (e.g., "camera.width")
            default: Default value if not found

        Returns:
            Setting value
        """
        keys = key_path.split('.')
        value = self.settings

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """
        ตั้งค่า

        Args:
            key_path: Path to setting (e.g., "camera.width")
            value: Value to set
        """
        keys = key_path.split('.')
        current = self.settings

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _update_nested_dict(self, base_dict: Dict, update_dict: Dict) -> None:
        """อัพเดท nested dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._update_nested_dict(base_dict[key], value)
            else:
                base_dict[key] = value

    def reset_to_default(self) -> None:
        """รีเซ็ตการตั้งค่ากลับเป็นค่าเริ่มต้น"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save()

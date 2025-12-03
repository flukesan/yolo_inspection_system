#!/usr/bin/env python3
"""
YOLO Inspection System - Main Entry Point
ระบบตรวจสอบคุณภาพชิ้นงานแบบเรียลไทม์ด้วย YOLO

Author: AI Assistant
Version: 1.0
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Settings
from core import CameraManager, YOLODetector, InspectionEngine, DataLogger
from utils import Database, ImageProcessor, PLCCommunication, ReportGenerator
from ui import MainWindow


class AppController:
    """Application Controller - จัดการ components ทั้งหมด"""

    def __init__(self):
        """Initialize Application Controller"""
        print("=" * 60)
        print("  YOLO Inspection System")
        print("  ระบบตรวจสอบคุณภาพชิ้นงานแบบเรียลไทม์")
        print("=" * 60)

        # Load settings
        print("\n[1/7] โหลดการตั้งค่า...")
        self.settings = Settings("config/app_config.json")

        # Initialize database
        print("[2/7] เชื่อมต่อฐานข้อมูล...")
        db_path = self.settings.get('database.path', 'data/inspection.db')
        self.database = Database(db_path)

        # Initialize core components
        print("[3/7] สร้าง Camera Manager...")
        self.camera_manager = CameraManager()

        print("[4/7] สร้าง YOLO Detector...")
        self.yolo_detector = YOLODetector()

        print("[5/7] สร้าง Data Logger...")
        self.data_logger = DataLogger(
            db_manager=self.database,
            output_dir=self.settings.get('database.path', 'data/inspections').replace('.db', '')
        )

        print("[6/7] สร้าง Inspection Engine...")
        self.inspection_engine = InspectionEngine(
            camera_manager=self.camera_manager,
            yolo_detector=self.yolo_detector,
            data_logger=self.data_logger
        )

        # Initialize utilities
        print("[7/7] สร้าง Report Generator...")
        self.report_generator = ReportGenerator(
            database=self.database,
            output_dir=self.settings.get('report.output_path', 'reports')
        )

        # PLC Communication (optional)
        self.plc = None
        if self.settings.get('plc.enabled', False):
            print("[Optional] เชื่อมต่อ PLC...")
            self.plc = PLCCommunication(
                ip=self.settings.get('plc.ip_address'),
                port=self.settings.get('plc.port'),
                unit_id=self.settings.get('plc.unit_id')
            )
            self.plc.connect()

        print("\n✓ เริ่มต้นระบบสำเร็จ!\n")

    def connect_camera(self, source=None, width=None, height=None, fps=None) -> bool:
        """
        เชื่อมต่อกล้อง

        Args:
            source: Camera source (index or RTSP URL). If None, use settings.
            width: Frame width. If None, use settings.
            height: Frame height. If None, use settings.
            fps: Frame rate. If None, use settings.

        Returns:
            bool: True if connected successfully
        """
        try:
            # Use provided parameters or fall back to settings
            if source is None:
                source = self.settings.get('camera.default_source', 0)
            if width is None:
                width = self.settings.get('camera.width', 1280)
            if height is None:
                height = self.settings.get('camera.height', 720)
            if fps is None:
                fps = self.settings.get('camera.fps', 30)

            return self.camera_manager.connect(source, width, height, fps)

        except Exception as e:
            print(f"✗ Error connecting camera: {e}")
            return False

    def disconnect_camera(self) -> bool:
        """
        ตัดการเชื่อมต่อกล้อง

        Returns:
            bool: True if disconnected successfully
        """
        try:
            self.camera_manager.disconnect()
            print("✓ ตัดการเชื่อมต่อกล้องสำเร็จ")
            return True
        except Exception as e:
            print(f"✗ Error disconnecting camera: {e}")
            return False

    def load_model(self, model_path=None, device=None, conf_threshold=None,
                   iou_threshold=None, img_size=None) -> bool:
        """
        โหลดโมเดล YOLO

        Args:
            model_path: Path to model file. If None, use settings.
            device: Device (cpu/cuda). If None, use settings.
            conf_threshold: Confidence threshold. If None, use settings.
            iou_threshold: IOU threshold. If None, use settings.
            img_size: Image size. If None, use settings.

        Returns:
            bool: True if loaded successfully
        """
        try:
            # Use provided parameters or fall back to settings
            if model_path is None:
                model_path = self.settings.get('yolo.model_path', 'models/yolov8_defect.pt')
            if device is None:
                device = self.settings.get('yolo.device', 'cpu')
            if conf_threshold is None:
                conf_threshold = self.settings.get('yolo.confidence_threshold', 0.5)
            if iou_threshold is None:
                iou_threshold = self.settings.get('yolo.iou_threshold', 0.45)
            if img_size is None:
                img_size = self.settings.get('yolo.img_size', 640)

            return self.yolo_detector.load_model(
                model_path=model_path,
                device=device,
                conf_threshold=conf_threshold,
                iou_threshold=iou_threshold,
                img_size=img_size
            )

        except Exception as e:
            print(f"✗ Error loading model: {e}")
            return False

    def start_inspection(self):
        """เริ่มการตรวจสอบ"""
        self.inspection_engine.start()

    def stop_inspection(self):
        """หยุดการตรวจสอบ"""
        self.inspection_engine.stop()

    def cleanup(self):
        """ทำความสะอาดก่อนปิดโปรแกรม"""
        print("\nทำความสะอาดระบบ...")

        # Stop inspection
        if self.inspection_engine:
            self.inspection_engine.stop()

        # Disconnect camera
        if self.camera_manager:
            self.camera_manager.disconnect()

        # Disconnect PLC
        if self.plc:
            self.plc.disconnect()

        # Close database
        if self.database:
            self.database.close()

        print("✓ ทำความสะอาดเสร็จสิ้น")


def main():
    """Main function"""
    # Note: PyQt6 enables High DPI scaling by default
    # Qt.AA_EnableHighDpiScaling and Qt.AA_UseHighDpiPixmaps are removed in PyQt6

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("YOLO Inspection System")
    app.setOrganizationName("YourCompany")

    # Create app controller
    controller = AppController()

    # Create and show main window
    window = MainWindow(controller)
    window.set_app_controller(controller)
    window.show()

    # Run application
    exit_code = app.exec()

    # Cleanup
    controller.cleanup()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

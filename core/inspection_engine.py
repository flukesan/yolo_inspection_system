"""
Inspection Engine - Logic การตรวจสอบคุณภาพ
Main inspection logic and workflow
"""
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import numpy as np


class InspectionEngine:
    """จัดการ Logic การตรวจสอบคุณภาพ"""

    def __init__(self, camera_manager=None, yolo_detector=None, data_logger=None):
        """
        Initialize Inspection Engine

        Args:
            camera_manager: CameraManager instance
            yolo_detector: YOLODetector instance
            data_logger: DataLogger instance
        """
        self.camera_manager = camera_manager
        self.yolo_detector = yolo_detector
        self.data_logger = data_logger

        # Inspection state
        self.is_running = False
        self.is_paused = False
        self.auto_save = True
        self.save_defect_only = True
        self.alert_on_defect = True

        # Statistics
        self.total_inspections = 0
        self.total_ok = 0
        self.total_defects = 0
        self.defect_counts = {}  # {class_name: count}
        self.start_time = None
        self.last_inspection_time = None

        # Callbacks
        self.on_inspection_complete: Optional[Callable] = None
        self.on_defect_detected: Optional[Callable] = None

    def start(self) -> None:
        """เริ่มการตรวจสอบ"""
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        print("✓ เริ่มการตรวจสอบคุณภาพ")

    def stop(self) -> None:
        """หยุดการตรวจสอบ"""
        self.is_running = False
        self.is_paused = False
        print("✓ หยุดการตรวจสอบคุณภาพ")

    def pause(self) -> None:
        """พักการตรวจสอบ"""
        self.is_paused = True
        print("⏸ พักการตรวจสอบ")

    def resume(self) -> None:
        """ดำเนินการตรวจสอบต่อ"""
        self.is_paused = False
        print("▶ ดำเนินการตรวจสอบต่อ")

    def inspect_once(self) -> Optional[Dict[str, Any]]:
        """
        ตรวจสอบ 1 ครั้ง

        Returns:
            Inspection result dictionary
        """
        if not self.is_running or self.is_paused:
            return None

        try:
            # Get frame from camera
            if self.camera_manager is None or not self.camera_manager.is_connected():
                print("! กล้องไม่ได้เชื่อมต่อ")
                return None

            frame = self.camera_manager.get_frame()
            if frame is None:
                return None

            # Detect using YOLO
            if self.yolo_detector is None or not self.yolo_detector.is_loaded():
                print("! โมเดล YOLO ยังไม่ได้โหลด")
                return None

            start_time = time.time()
            detections = self.yolo_detector.detect(frame)
            detection_time = (time.time() - start_time) * 1000  # ms

            # Analyze results based on model type
            model_type = self.yolo_detector.model_type

            if model_type == 'classification':
                # For classification: check if detected class is "defect" class
                has_defect = False
                if len(detections) > 0:
                    # Check if class name indicates defect
                    class_name = detections[0]['class_name'].lower()
                    # Classes that indicate defect/NG
                    defect_classes = ['defect', 'bad', 'ng', 'fail', 'scratch', 'crack', 'dent']
                    has_defect = any(defect in class_name for defect in defect_classes)
            else:
                # For detection/segmentation/pose: any detection means defect
                has_defect = len(detections) > 0

            result_status = "NG" if has_defect else "OK"

            # Create inspection result
            inspection_result = {
                'timestamp': datetime.now(),
                'status': result_status,
                'has_defect': has_defect,
                'num_defects': len(detections),
                'detections': detections,
                'detection_time_ms': round(detection_time, 2),
                'image': frame,
                'annotated_image': None
            }

            # Draw detections (always draw, even if empty - for live view)
            if len(detections) > 0:
                annotated = self.yolo_detector.draw_detections(frame, detections)
                inspection_result['annotated_image'] = annotated
            else:
                # No detections - use original frame for display
                inspection_result['annotated_image'] = frame

            # Update statistics
            self._update_statistics(inspection_result)

            # Save to database
            if self.auto_save:
                if not self.save_defect_only or has_defect:
                    self._save_result(inspection_result)

            # Trigger callbacks
            if self.on_inspection_complete:
                self.on_inspection_complete(inspection_result)

            if has_defect and self.on_defect_detected:
                self.on_defect_detected(inspection_result)

            self.last_inspection_time = time.time()

            return inspection_result

        except Exception as e:
            print(f"✗ Error during inspection: {e}")
            return None

    def _update_statistics(self, result: Dict[str, Any]) -> None:
        """อัพเดทสถิติ"""
        self.total_inspections += 1

        if result['status'] == 'OK':
            self.total_ok += 1
        else:
            self.total_defects += 1

            # Count defects by class
            for det in result['detections']:
                class_name = det['class_name']
                self.defect_counts[class_name] = self.defect_counts.get(class_name, 0) + 1

    def _save_result(self, result: Dict[str, Any]) -> None:
        """บันทึกผลลัพธ์ลงฐานข้อมูล"""
        if self.data_logger is None:
            return

        try:
            # Prepare data for logging
            log_data = {
                'timestamp': result['timestamp'],
                'status': result['status'],
                'num_defects': result['num_defects'],
                'detection_time_ms': result['detection_time_ms'],
                'detections': result['detections']
            }

            # Save image if has defect
            image_path = None
            if result['has_defect'] and result['annotated_image'] is not None:
                image_path = self.data_logger.save_image(
                    result['annotated_image'],
                    result['timestamp']
                )
                log_data['image_path'] = image_path

            # Log to database
            self.data_logger.log_inspection(log_data)

        except Exception as e:
            print(f"✗ Error saving result: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        ดึงสถิติการตรวจสอบ

        Returns:
            Statistics dictionary
        """
        elapsed_time = 0
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time

        # Calculate rates
        defect_rate = 0
        if self.total_inspections > 0:
            defect_rate = (self.total_defects / self.total_inspections) * 100

        # Calculate throughput
        throughput = 0
        if elapsed_time > 0:
            throughput = self.total_inspections / elapsed_time * 60  # per minute

        return {
            'total_inspections': self.total_inspections,
            'total_ok': self.total_ok,
            'total_defects': self.total_defects,
            'defect_rate': round(defect_rate, 2),
            'defect_counts': self.defect_counts.copy(),
            'elapsed_time_sec': round(elapsed_time, 1),
            'throughput_per_min': round(throughput, 1),
            'is_running': self.is_running,
            'is_paused': self.is_paused
        }

    def reset_statistics(self) -> None:
        """รีเซ็ตสถิติ"""
        self.total_inspections = 0
        self.total_ok = 0
        self.total_defects = 0
        self.defect_counts = {}
        self.start_time = time.time()
        print("✓ รีเซ็ตสถิติ")

    def set_camera_manager(self, camera_manager) -> None:
        """ตั้งค่า CameraManager"""
        self.camera_manager = camera_manager

    def set_yolo_detector(self, yolo_detector) -> None:
        """ตั้งค่า YOLODetector"""
        self.yolo_detector = yolo_detector

    def set_data_logger(self, data_logger) -> None:
        """ตั้งค่า DataLogger"""
        self.data_logger = data_logger

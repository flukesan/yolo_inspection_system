"""
Inspection Engine - Logic การตรวจสอบคุณภาพ
Main inspection logic and workflow
"""
import os
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
        self.save_ok_images = True  # บันทึกรูป OK
        self.save_ng_images = True  # บันทึกรูป NG
        self.alert_on_defect = True

        # Statistics
        self.total_inspections = 0
        self.total_ok = 0
        self.total_defects = 0
        self.defect_counts = {}  # {class_name: count}
        self.start_time = None
        self.stop_time = None  # Track when inspection stops
        self.last_inspection_time = None

        # Callbacks
        self.on_inspection_complete: Optional[Callable] = None
        self.on_defect_detected: Optional[Callable] = None

    def start(self) -> None:
        """เริ่มการตรวจสอบ"""
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        self.stop_time = None  # Reset stop time when starting
        print("✓ เริ่มการตรวจสอบคุณภาพ")

    def stop(self) -> None:
        """หยุดการตรวจสอบ"""
        self.is_running = False
        self.is_paused = False
        self.stop_time = time.time()  # Record stop time for throughput calculation
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

            # Get validation rules from yolo_detector if available
            validation_rules = getattr(self.yolo_detector, 'validation_rules', None)

            # Perform validation if rules are enabled
            validation_result = self.validate_detections(detections, validation_rules)

            # Analyze results based on model type
            model_type = self.yolo_detector.model_type

            # Determine if we should count this inspection in statistics
            # For detection/segmentation/pose: only count when objects are detected
            # For classification: always count (it classifies the whole image)
            should_count = True
            if model_type in ['detection', 'segmentation', 'pose']:
                # Only count if there are detections (objects in frame)
                should_count = len(detections) > 0

            # Determine Pass/Fail status
            if validation_result['enabled']:
                # If validation is enabled, use validation result
                has_defect = not validation_result['pass']
                result_status = "OK" if validation_result['pass'] else "NG"
            else:
                # Otherwise, use default logic
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
            timestamp_obj = datetime.now()
            inspection_result = {
                'timestamp': timestamp_obj,
                'status': result_status,
                'has_defect': has_defect,
                'num_defects': len(detections),
                'detections': detections,
                'detection_time_ms': round(detection_time, 2),
                'image': frame,
                'annotated_image': None,
                'should_count': should_count,  # Flag to indicate if this should be counted in stats
                'validation_result': validation_result  # Validation result
            }

            # Prepare overlay information
            timestamp_str = timestamp_obj.strftime("%Y-%m-%d %H:%M:%S")

            # Get model name from path (extract filename without extension)
            model_name = "Unknown"
            if self.yolo_detector and self.yolo_detector.model_path:
                model_name = os.path.splitext(os.path.basename(self.yolo_detector.model_path))[0]

            # Only show status if we're counting this inspection (has objects)
            display_status = result_status if should_count else None

            # Draw detections with overlay info (always draw for live view)
            annotated = self.yolo_detector.draw_detections(
                frame,
                detections,
                timestamp=timestamp_str,
                model_name=model_name,
                status=display_status  # None when no objects detected
            )
            inspection_result['annotated_image'] = annotated

            # Update statistics (only if should_count is True)
            if should_count:
                self._update_statistics(inspection_result)

            # Save to database
            if self.auto_save:
                # Determine if we should save based on status and settings
                should_save = False
                if result_status == "OK" and self.save_ok_images:
                    should_save = True
                elif result_status == "NG" and self.save_ng_images:
                    should_save = True

                if should_save:
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

            # Save image (both OK and NG, separated by folder)
            image_path = None
            if result['annotated_image'] is not None:
                status = result['status']  # "OK" or "NG"
                image_path = self.data_logger.save_image(
                    result['annotated_image'],
                    result['timestamp'],
                    status=status
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
            # Use stop_time if inspection has stopped, otherwise use current time
            if self.stop_time is not None:
                elapsed_time = self.stop_time - self.start_time
            else:
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

    def validate_detections(self, detections: List[Dict], validation_rules: Dict) -> Dict[str, Any]:
        """
        ตรวจสอบ detections ตามเงื่อนไขที่กำหนด

        Args:
            detections: List of detection results
            validation_rules: Validation rules from model profile

        Returns:
            {
                'enabled': True/False,
                'pass': True/False,
                'pass_condition': 'all'/'any',
                'rules_results': [
                    {
                        'type': 'count_exact',
                        'class_name': 'A1',
                        'expected': 5,
                        'actual': 5,
                        'pass': True
                    },
                    ...
                ]
            }
        """
        if validation_rules is None or not validation_rules.get("enabled", False):
            return {
                'enabled': False,
                'pass': None,
                'pass_condition': None,
                'rules_results': []
            }

        # Count detections by class
        class_counts = {}
        class_positions = {}  # Store bounding box centers

        for det in detections:
            class_name = det['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

            # Calculate center of bounding box for position checks
            bbox = det.get('bbox', [])
            if len(bbox) >= 4:
                x1, y1, x2, y2 = bbox[:4]
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                if class_name not in class_positions:
                    class_positions[class_name] = []
                class_positions[class_name].append((center_x, center_y))

        # Check each rule
        rules = validation_rules.get('rules', [])
        pass_condition = validation_rules.get('pass_condition', 'all')
        rules_results = []
        passes = []

        for rule in rules:
            rule_type = rule.get('type', '')
            class_name = rule.get('class_name', '')

            if rule_type == 'count_exact':
                # Count exact: จำนวนต้องเท่ากับที่กำหนด
                expected = rule.get('expected', 0)
                actual = class_counts.get(class_name, 0)
                is_pass = (actual == expected)

                rules_results.append({
                    'type': 'count_exact',
                    'class_name': class_name,
                    'expected': expected,
                    'actual': actual,
                    'pass': is_pass,
                    'message': f"{class_name}: {actual}/{expected}"
                })
                passes.append(is_pass)

            elif rule_type == 'presence_check':
                # Presence check: มีหรือไม่มี
                must_exist = rule.get('must_exist', True)
                actual = class_counts.get(class_name, 0)
                exists = actual > 0

                if must_exist:
                    is_pass = exists
                    message = f"{class_name}: {'พบ' if exists else 'ไม่พบ'} (ต้องมี)"
                else:
                    is_pass = not exists
                    message = f"{class_name}: {'พบ' if exists else 'ไม่พบ'} (ต้องไม่มี)"

                rules_results.append({
                    'type': 'presence_check',
                    'class_name': class_name,
                    'must_exist': must_exist,
                    'exists': exists,
                    'pass': is_pass,
                    'message': message
                })
                passes.append(is_pass)

            elif rule_type == 'position_check':
                # Position check: ตรวจสอบตำแหน่ง
                zone = rule.get('zone', {})
                zone_x = zone.get('x', 0)
                zone_y = zone.get('y', 0)
                zone_w = zone.get('width', 100)
                zone_h = zone.get('height', 100)

                positions = class_positions.get(class_name, [])
                in_zone_count = 0

                for pos_x, pos_y in positions:
                    # Check if position is inside zone
                    if (zone_x <= pos_x <= zone_x + zone_w and
                        zone_y <= pos_y <= zone_y + zone_h):
                        in_zone_count += 1

                total_count = len(positions)
                is_pass = (in_zone_count == total_count and total_count > 0)

                rules_results.append({
                    'type': 'position_check',
                    'class_name': class_name,
                    'zone': zone,
                    'in_zone': in_zone_count,
                    'total': total_count,
                    'pass': is_pass,
                    'message': f"{class_name}: {in_zone_count}/{total_count} ในโซน"
                })
                passes.append(is_pass)

        # Determine overall pass based on pass_condition
        if len(passes) == 0:
            overall_pass = True  # No rules = pass
        elif pass_condition == 'all':
            overall_pass = all(passes)
        else:  # 'any'
            overall_pass = any(passes)

        return {
            'enabled': True,
            'pass': overall_pass,
            'pass_condition': pass_condition,
            'rules_results': rules_results
        }

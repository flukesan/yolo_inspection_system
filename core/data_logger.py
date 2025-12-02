"""
Data Logger - บันทึกข้อมูลการตรวจสอบ
Logs inspection results to database and files
"""
import os
import cv2
from datetime import datetime
from typing import Dict, Any, Optional
import json


class DataLogger:
    """บันทึกข้อมูลการตรวจสอบ"""

    def __init__(self, db_manager=None, output_dir: str = "data/inspections"):
        """
        Initialize Data Logger

        Args:
            db_manager: Database manager instance
            output_dir: Directory for saving images
        """
        self.db_manager = db_manager
        self.output_dir = output_dir

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "json"), exist_ok=True)

        # Statistics
        self.total_logs = 0

    def log_inspection(self, data: Dict[str, Any]) -> bool:
        """
        บันทึกผลการตรวจสอบ

        Args:
            data: Inspection data dictionary

        Returns:
            True if successful
        """
        try:
            timestamp = data.get('timestamp', datetime.now())

            # Save to database
            if self.db_manager is not None:
                self.db_manager.insert_inspection(data)

            # Save JSON log
            self._save_json_log(data, timestamp)

            self.total_logs += 1
            return True

        except Exception as e:
            print(f"✗ Error logging inspection: {e}")
            return False

    def save_image(self, image, timestamp: datetime, prefix: str = "defect") -> str:
        """
        บันทึกภาพ

        Args:
            image: Image to save
            timestamp: Timestamp
            prefix: Filename prefix

        Returns:
            Path to saved image
        """
        try:
            # Generate filename
            filename = f"{prefix}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
            filepath = os.path.join(self.output_dir, "images", filename)

            # Save image
            cv2.imwrite(filepath, image)
            return filepath

        except Exception as e:
            print(f"✗ Error saving image: {e}")
            return ""

    def _save_json_log(self, data: Dict[str, Any], timestamp: datetime) -> None:
        """บันทึก JSON log"""
        try:
            # Prepare JSON data
            json_data = {
                'timestamp': timestamp.isoformat(),
                'status': data.get('status'),
                'num_defects': data.get('num_defects', 0),
                'detection_time_ms': data.get('detection_time_ms', 0),
                'detections': data.get('detections', []),
                'image_path': data.get('image_path', '')
            }

            # Generate filename
            filename = f"log_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
            filepath = os.path.join(self.output_dir, "json", filename)

            # Save JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"✗ Error saving JSON log: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        ดึงสถิติการบันทึก

        Returns:
            Statistics dictionary
        """
        return {
            'total_logs': self.total_logs,
            'output_dir': self.output_dir
        }

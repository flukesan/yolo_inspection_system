"""
Camera View Widget - แสดงภาพจากกล้อง
Display camera feed and inspection results
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np


class CameraView(QWidget):
    """Widget แสดงภาพจากกล้อง"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

        # Timer for updating frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Current frame
        self.current_frame = None
        self.camera_manager = None
        self.show_annotations = True

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2b2b2b; border: 1px solid #444;")
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setScaledContents(False)

        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def set_camera_manager(self, camera_manager):
        """ตั้งค่า Camera Manager"""
        self.camera_manager = camera_manager

    def start(self, fps: int = 30):
        """เริ่มแสดงผล"""
        interval = int(1000 / fps)  # ms
        self.timer.start(interval)

    def stop(self):
        """หยุดแสดงผล"""
        self.timer.stop()
        self.image_label.clear()

    def update_frame(self):
        """อัพเดทเฟรม"""
        if self.camera_manager is None:
            return

        frame = self.camera_manager.get_frame()
        if frame is not None:
            self.current_frame = frame
            self.display_frame(frame)

    def display_frame(self, frame: np.ndarray):
        """แสดงภาพ"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # Scale to label size while keeping aspect ratio
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)

        except Exception as e:
            print(f"✗ Error displaying frame: {e}")

    def display_result(self, annotated_frame: np.ndarray):
        """แสดงผลการตรวจสอบ"""
        if annotated_frame is not None and self.show_annotations:
            self.display_frame(annotated_frame)

    def set_show_annotations(self, show: bool):
        """ตั้งค่าการแสดง annotations"""
        self.show_annotations = show

    def get_current_frame(self):
        """ดึงภาพปัจจุบัน"""
        return self.current_frame

    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        # Refresh display when widget is resized
        if self.current_frame is not None:
            self.display_frame(self.current_frame)

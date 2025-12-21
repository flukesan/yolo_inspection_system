"""
Multi-Shot Capture Dialog
Guided capture dialog สำหรับ training mode
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QProgressBar, QGroupBox,
                             QRadioButton, QButtonGroup, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QImage
import cv2
import numpy as np
import time


class MultiShotCaptureDialog(QDialog):
    """Dialog สำหรับ guided multi-shot capture"""

    # Signals
    capture_completed = pyqtSignal(list, str, int)  # (shots, class_name, workpiece_id)

    def __init__(self, camera_manager, settings, parent=None):
        """
        Initialize dialog

        Args:
            camera_manager: CameraManager instance
            settings: Settings instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.camera = camera_manager
        self.settings = settings
        self.shots = []
        self.current_shot = 0
        self.is_capturing = False
        self.countdown_timer = None
        self.preview_timer = None

        self.setWindowTitle("Multi-Shot Capture - Training Mode")
        self.setModal(True)
        self.setMinimumSize(800, 700)
        self.setup_ui()
        self.load_settings()
        self.start_preview()

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📸 Multi-Shot Capture")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Settings Section
        settings_group = self.create_settings_section()
        layout.addWidget(settings_group)

        # Camera Preview
        preview_group = self.create_preview_section()
        layout.addWidget(preview_group)

        # Progress Section
        progress_group = self.create_progress_section()
        layout.addWidget(progress_group)

        # Instructions
        instructions_group = self.create_instructions_section()
        layout.addWidget(instructions_group)

        # Buttons
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ เริ่มถ่าย")
        self.start_btn.clicked.connect(self.start_capture_sequence)
        self.start_btn.setStyleSheet("""
            QPushButton {
                padding: 15px 30px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)

        self.next_btn = QPushButton("→ ถัดไป (Space)")
        self.next_btn.clicked.connect(self.capture_next_shot)
        self.next_btn.setEnabled(False)
        self.next_btn.setStyleSheet("""
            QPushButton {
                padding: 15px 30px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)

        cancel_btn = QPushButton("✖ ยกเลิก")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 15px 30px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.next_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def create_settings_section(self):
        """สร้าง settings section"""
        group = QGroupBox("⚙ การตั้งค่า")
        layout = QHBoxLayout()

        # Class selection
        class_label = QLabel("Class:")
        self.class_ok_radio = QRadioButton("OK")
        self.class_ng_radio = QRadioButton("NG")
        self.class_ok_radio.setChecked(True)

        class_group = QButtonGroup()
        class_group.addButton(self.class_ok_radio)
        class_group.addButton(self.class_ng_radio)

        # Shots selector
        shots_label = QLabel("จำนวน Shots:")
        self.shots_combo = QComboBox()
        self.shots_combo.addItems(["2", "3", "4", "6", "9"])
        self.shots_combo.setCurrentText("4")

        # Interval selector
        interval_label = QLabel("ระยะห่าง:")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1.0 วินาที", "2.0 วินาที", "3.0 วินาที", "5.0 วินาที"])
        self.interval_combo.setCurrentText("2.0 วินาที")

        layout.addWidget(class_label)
        layout.addWidget(self.class_ok_radio)
        layout.addWidget(self.class_ng_radio)
        layout.addSpacing(20)
        layout.addWidget(shots_label)
        layout.addWidget(self.shots_combo)
        layout.addSpacing(20)
        layout.addWidget(interval_label)
        layout.addWidget(self.interval_combo)
        layout.addStretch()

        group.setLayout(layout)
        return group

    def create_preview_section(self):
        """สร้าง camera preview section"""
        group = QGroupBox("👁 Camera Preview")
        layout = QVBoxLayout()

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setStyleSheet("border: 2px solid #ddd; background-color: #000;")

        layout.addWidget(self.preview_label)
        group.setLayout(layout)
        return group

    def create_progress_section(self):
        """สร้าง progress section"""
        group = QGroupBox("📊 ความคืบหน้า")
        layout = QVBoxLayout()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)

        # Status label
        self.status_label = QLabel("พร้อมเริ่มถ่าย")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12))

        # Countdown label
        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.countdown_label.setStyleSheet("color: #FF5722;")

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(self.countdown_label)

        group.setLayout(layout)
        return group

    def create_instructions_section(self):
        """สร้าง instructions section"""
        group = QGroupBox("ℹ คำแนะนำ")

        instructions = """
        <ul style='line-height: 1.8;'>
            <li><b>Auto Mode:</b> กด "เริ่มถ่าย" แล้วหมุน/เลื่อนชิ้นงานตาม countdown</li>
            <li><b>Manual Mode:</b> กด "ถัดไป" (หรือ Space Bar) เมื่อพร้อมถ่าย</li>
            <li>แต่ละ shot ควรมีมุมมอง/ตำแหน่งที่แตกต่างกัน</li>
            <li>ภาพจะถูกบันทึกเป็น: {class}/wp{id}_shot{n}.jpg</li>
        </ul>
        """

        label = QLabel(instructions)
        label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        group.setLayout(layout)

        return group

    def load_settings(self):
        """โหลด settings"""
        training_settings = self.settings.get('snapshot_training', {})

        # Load multi-shot settings
        num_shots = training_settings.get('multishot_shots', 4)
        interval = training_settings.get('multishot_interval', 2.0)

        self.shots_combo.setCurrentText(str(num_shots))
        self.interval_combo.setCurrentText(f"{interval} วินาที")

    def start_preview(self):
        """เริ่ม camera preview"""
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)
        self.preview_timer.start(33)  # ~30 FPS

    def update_preview(self):
        """อัพเดท preview"""
        if self.camera is None:
            return

        frame = self.camera.get_frame()
        if frame is None:
            return

        # Convert to QPixmap
        height, width = frame.shape[:2]
        bytes_per_line = 3 * width

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # Scale to fit
        scaled_pixmap = pixmap.scaled(
            self.preview_label.width(),
            self.preview_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.preview_label.setPixmap(scaled_pixmap)

    def start_capture_sequence(self):
        """เริ่ม capture sequence"""
        self.shots = []
        self.current_shot = 0
        self.is_capturing = True

        # Disable start button
        self.start_btn.setEnabled(False)

        # Get settings
        num_shots = int(self.shots_combo.currentText())
        auto_advance = True  # For now, always auto

        if auto_advance:
            # Auto mode - capture immediately then countdown
            self.capture_next_shot()
        else:
            # Manual mode - enable next button
            self.next_btn.setEnabled(True)
            self.status_label.setText(f"Shot 1/{num_shots}: กด 'ถัดไป' เมื่อพร้อม")

    def capture_next_shot(self):
        """Capture next shot"""
        num_shots = int(self.shots_combo.currentText())

        # Capture frame
        frame = self.camera.get_frame()
        if frame is not None:
            self.shots.append(frame.copy())
            self.current_shot += 1

            # Update progress
            progress = int((self.current_shot / num_shots) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"✓ Captured shot {self.current_shot}/{num_shots}")

            # Check if done
            if self.current_shot >= num_shots:
                self.finish_capture()
                return

            # Start countdown for next shot
            self.start_countdown()

    def start_countdown(self):
        """เริ่ม countdown"""
        interval_text = self.interval_combo.currentText()
        interval = float(interval_text.split()[0])

        self.countdown_seconds = int(interval)
        self.update_countdown()

        # Start countdown timer
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)  # 1 second

    def update_countdown(self):
        """อัพเดท countdown"""
        if self.countdown_seconds > 0:
            self.countdown_label.setText(str(self.countdown_seconds))
            self.countdown_seconds -= 1
        else:
            # Stop timer
            if self.countdown_timer:
                self.countdown_timer.stop()

            self.countdown_label.setText("")
            self.capture_next_shot()

    def finish_capture(self):
        """เสร็จสิ้นการ capture"""
        self.is_capturing = False
        self.progress_bar.setValue(100)
        self.status_label.setText(f"✓ เสร็จสมบูรณ์! ถ่ายได้ {len(self.shots)} ภาพ")

        # Stop timers
        if self.countdown_timer:
            self.countdown_timer.stop()

        # Get class name
        class_name = "OK" if self.class_ok_radio.isChecked() else "NG"

        # Import here to avoid circular import
        from utils.multishot_capture import get_next_workpiece_id

        # Get output dir
        output_dir = self.settings.get('snapshot_training.output_dir', 'training_images')

        # Get next workpiece ID
        workpiece_id = get_next_workpiece_id(output_dir, class_name)

        # Emit signal
        self.capture_completed.emit(self.shots, class_name, workpiece_id)

        # Show success message
        QMessageBox.information(
            self,
            "สำเร็จ",
            f"ถ่ายภาพ {len(self.shots)} ภาพสำเร็จ!\n"
            f"Class: {class_name}\n"
            f"Workpiece ID: wp{workpiece_id:03d}"
        )

        # Ask if want to continue
        reply = QMessageBox.question(
            self,
            "ถ่ายต่อหรือไม่?",
            "ต้องการถ่ายชิ้นงานถัดไปหรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Reset for next capture
            self.reset_for_next()
        else:
            # Close dialog
            self.accept()

    def reset_for_next(self):
        """Reset สำหรับถ่ายชิ้นงานถัดไป"""
        self.shots = []
        self.current_shot = 0
        self.progress_bar.setValue(0)
        self.status_label.setText("พร้อมเริ่มถ่าย")
        self.countdown_label.setText("")
        self.start_btn.setEnabled(True)
        self.next_btn.setEnabled(False)

    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key.Key_Space and self.next_btn.isEnabled():
            self.capture_next_shot()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle close event"""
        if self.preview_timer:
            self.preview_timer.stop()
        if self.countdown_timer:
            self.countdown_timer.stop()
        event.accept()

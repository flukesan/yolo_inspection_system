"""
Camera Settings Dialog - ตั้งค่ากล้อง
Dialog for camera configuration
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QComboBox, QPushButton,
                             QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt


class CameraSettingsDialog(QDialog):
    """Dialog สำหรับตั้งค่ากล้อง"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("ตั้งค่ากล้อง")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Camera Type
        type_group = QGroupBox("ประเภทกล้อง")
        type_layout = QFormLayout()

        self.camera_type = QComboBox()
        self.camera_type.addItems(["USB Camera", "RTSP Camera", "IP Camera"])
        type_layout.addRow("ประเภท:", self.camera_type)

        type_group.setLayout(type_layout)

        # Camera Source
        source_group = QGroupBox("แหล่งที่มา")
        source_layout = QFormLayout()

        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("0 สำหรับ USB, URL สำหรับ RTSP/IP")
        source_layout.addRow("Source:", self.source_input)

        source_group.setLayout(source_layout)

        # Resolution
        resolution_group = QGroupBox("ความละเอียด")
        resolution_layout = QFormLayout()

        self.width_input = QSpinBox()
        self.width_input.setRange(320, 3840)
        self.width_input.setValue(1280)
        self.width_input.setSingleStep(160)
        resolution_layout.addRow("ความกว้าง:", self.width_input)

        self.height_input = QSpinBox()
        self.height_input.setRange(240, 2160)
        self.height_input.setValue(720)
        self.height_input.setSingleStep(120)
        resolution_layout.addRow("ความสูง:", self.height_input)

        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 120)
        self.fps_input.setValue(30)
        resolution_layout.addRow("FPS:", self.fps_input)

        resolution_group.setLayout(resolution_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("บันทึก")
        self.save_btn.clicked.connect(self.save_settings)

        self.cancel_btn = QPushButton("ยกเลิก")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        # Add all to main layout
        layout.addWidget(type_group)
        layout.addWidget(source_group)
        layout.addWidget(resolution_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_settings(self):
        """โหลดการตั้งค่า"""
        self.source_input.setText(str(self.settings.get('camera.default_source', 0)))
        self.width_input.setValue(self.settings.get('camera.width', 1280))
        self.height_input.setValue(self.settings.get('camera.height', 720))
        self.fps_input.setValue(self.settings.get('camera.fps', 30))

    def save_settings(self):
        """บันทึกการตั้งค่า"""
        # Parse source (convert to int if possible)
        source_str = self.source_input.text()
        try:
            source = int(source_str)
        except ValueError:
            source = source_str

        self.settings.set('camera.default_source', source)
        self.settings.set('camera.width', self.width_input.value())
        self.settings.set('camera.height', self.height_input.value())
        self.settings.set('camera.fps', self.fps_input.value())

        self.settings.save()
        self.accept()

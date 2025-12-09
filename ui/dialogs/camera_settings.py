"""
Camera Settings Dialog - ตั้งค่ากล้อง
Dialog for camera configuration (USB/RTSP/IP/GigE Vision)
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QComboBox, QPushButton,
                             QGroupBox, QFormLayout, QFileDialog, QTextEdit,
                             QCheckBox)
from PyQt6.QtCore import Qt


class CameraSettingsDialog(QDialog):
    """Dialog สำหรับตั้งค่ากล้อง (รองรับ USB/RTSP/IP/GigE Vision)"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
        self.load_settings()

        # Connect signals
        self.camera_type.currentTextChanged.connect(self.on_camera_type_changed)

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("ตั้งค่ากล้อง")
        self.setModal(True)
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        # Camera Type
        type_group = QGroupBox("ประเภทกล้อง")
        type_layout = QFormLayout()

        self.camera_type = QComboBox()
        self.camera_type.addItems(["USB Camera", "RTSP Camera", "IP Camera", "GigE Vision"])
        type_layout.addRow("ประเภท:", self.camera_type)

        type_group.setLayout(type_layout)

        # Camera Source
        source_group = QGroupBox("แหล่งที่มา / Camera Source")
        source_layout = QFormLayout()

        # USB/RTSP/IP Source
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("0 สำหรับ USB, URL สำหรับ RTSP/IP")
        source_layout.addRow("Source:", self.source_input)

        # GigE Vision Settings
        self.gentl_label = QLabel("GenTL Producer (.cti):")
        gentl_input_layout = QHBoxLayout()
        self.gentl_input = QLineEdit()
        self.gentl_input.setPlaceholderText("/opt/pylon/lib/gentlproducer.cti")
        self.gentl_browse_btn = QPushButton("เลือกไฟล์...")
        self.gentl_browse_btn.clicked.connect(self.browse_gentl)
        gentl_input_layout.addWidget(self.gentl_input)
        gentl_input_layout.addWidget(self.gentl_browse_btn)

        self.camera_id_label = QLabel("Camera ID:")
        self.camera_id_input = QLineEdit()
        self.camera_id_input.setPlaceholderText("0 (index), serial number, or IP")

        source_layout.addRow(self.gentl_label, gentl_input_layout)
        source_layout.addRow(self.camera_id_label, self.camera_id_input)

        source_group.setLayout(source_layout)

        # Resolution & Performance
        resolution_group = QGroupBox("ความละเอียดและประสิทธิภาพ")
        resolution_layout = QFormLayout()

        self.width_input = QSpinBox()
        self.width_input.setRange(320, 4096)
        self.width_input.setValue(1280)
        self.width_input.setSingleStep(160)
        resolution_layout.addRow("ความกว้าง:", self.width_input)

        self.height_input = QSpinBox()
        self.height_input.setRange(240, 3072)
        self.height_input.setValue(720)
        self.height_input.setSingleStep(120)
        resolution_layout.addRow("ความสูง:", self.height_input)

        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 120)
        self.fps_input.setValue(30)
        resolution_layout.addRow("FPS:", self.fps_input)

        resolution_group.setLayout(resolution_layout)

        # Camera Parameters (Advanced)
        params_group = QGroupBox("พารามิเตอร์กล้อง (Advanced)")
        params_layout = QFormLayout()

        self.exposure_input = QSpinBox()
        self.exposure_input.setRange(0, 100000)
        self.exposure_input.setValue(0)
        self.exposure_input.setSpecialValueText("Auto")
        params_layout.addRow("Exposure (μs):", self.exposure_input)

        self.gain_input = QSpinBox()
        self.gain_input.setRange(0, 100)
        self.gain_input.setValue(0)
        self.gain_input.setSpecialValueText("Auto")
        params_layout.addRow("Gain:", self.gain_input)

        params_group.setLayout(params_layout)

        # Help Text
        help_group = QGroupBox("💡 คำแนะนำ")
        help_layout = QVBoxLayout()
        self.help_text = QTextEdit()
        self.help_text.setReadOnly(True)
        self.help_text.setMaximumHeight(100)
        self.help_text.setHtml(self._get_help_text("USB Camera"))
        help_layout.addWidget(self.help_text)
        help_group.setLayout(help_layout)

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
        layout.addWidget(params_group)
        layout.addWidget(help_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Initial visibility
        self.on_camera_type_changed(self.camera_type.currentText())

    def browse_gentl(self):
        """เปิด file dialog เพื่อเลือก GenTL producer file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "เลือก GenTL Producer File",
            "",
            "GenTL Producer (*.cti);;All Files (*)"
        )
        if file_path:
            self.gentl_input.setText(file_path)

    def on_camera_type_changed(self, camera_type: str):
        """เปลี่ยนการแสดงผลตาม camera type ที่เลือก"""
        is_gige = camera_type == "GigE Vision"

        # Show/hide GigE specific fields
        self.gentl_label.setVisible(is_gige)
        self.gentl_input.setVisible(is_gige)
        self.gentl_browse_btn.setVisible(is_gige)
        self.camera_id_label.setVisible(is_gige)
        self.camera_id_input.setVisible(is_gige)

        # Show/hide source field for USB/RTSP/IP
        self.source_input.setVisible(not is_gige)

        # Update help text
        self.help_text.setHtml(self._get_help_text(camera_type))

    def _get_help_text(self, camera_type: str) -> str:
        """สร้าง help text ตาม camera type"""
        help_texts = {
            "USB Camera": """
                <b>USB Camera</b><br>
                • Source: ใส่ตัวเลข 0, 1, 2, ... (camera index)<br>
                • ตัวอย่าง: 0 (กล้องตัวแรก), 1 (กล้องตัวที่สอง)
            """,
            "RTSP Camera": """
                <b>RTSP Camera</b><br>
                • Source: ใส่ RTSP URL<br>
                • ตัวอย่าง: rtsp://192.168.1.100:554/stream<br>
                • รูปแบบ: rtsp://[username:password@]host:port/path
            """,
            "IP Camera": """
                <b>IP Camera</b><br>
                • Source: ใส่ HTTP/RTSP URL<br>
                • ตัวอย่าง: http://192.168.1.100/video.mjpg
            """,
            "GigE Vision": """
                <b>GigE Vision Camera (Industrial)</b><br>
                • GenTL Producer: ไฟล์ .cti จาก camera vendor<br>
                &nbsp;&nbsp;- Basler: /opt/pylon/lib/gentlproducer.cti<br>
                &nbsp;&nbsp;- Allied Vision: /opt/VimbaGigETL/bin/VimbaGigETL.cti<br>
                • Camera ID: 0 (index), serial number, หรือ IP address<br>
                • <b>หมายเหตุ:</b> ต้องติดตั้ง SDK ของ camera vendor ก่อน
            """
        }
        return help_texts.get(camera_type, "")

    def load_settings(self):
        """โหลดการตั้งค่า"""
        # Load camera type
        camera_type_map = {
            "usb": "USB Camera",
            "rtsp": "RTSP Camera",
            "ip": "IP Camera",
            "gige": "GigE Vision"
        }
        saved_type = self.settings.get('camera.type', 'usb')
        display_type = camera_type_map.get(saved_type, "USB Camera")
        index = self.camera_type.findText(display_type)
        if index >= 0:
            self.camera_type.setCurrentIndex(index)

        # Load source
        self.source_input.setText(str(self.settings.get('camera.default_source', 0)))

        # Load GigE settings
        self.gentl_input.setText(self.settings.get('camera.gentl_path', ''))
        self.camera_id_input.setText(str(self.settings.get('camera.camera_id', 0)))

        # Load resolution
        self.width_input.setValue(self.settings.get('camera.width', 1280))
        self.height_input.setValue(self.settings.get('camera.height', 720))
        self.fps_input.setValue(self.settings.get('camera.fps', 30))

        # Load advanced parameters
        self.exposure_input.setValue(self.settings.get('camera.exposure', 0))
        self.gain_input.setValue(self.settings.get('camera.gain', 0))

    def save_settings(self):
        """บันทึกการตั้งค่า"""
        # Map display name to internal type
        camera_type_map = {
            "USB Camera": "usb",
            "RTSP Camera": "rtsp",
            "IP Camera": "ip",
            "GigE Vision": "gige"
        }
        camera_type = camera_type_map[self.camera_type.currentText()]
        self.settings.set('camera.type', camera_type)

        # Save source (for USB/RTSP/IP)
        if camera_type != "gige":
            source_str = self.source_input.text()
            try:
                source = int(source_str)
            except ValueError:
                source = source_str
            self.settings.set('camera.default_source', source)

        # Save GigE settings
        if camera_type == "gige":
            self.settings.set('camera.gentl_path', self.gentl_input.text())

            # Parse camera_id (int or string)
            camera_id_str = self.camera_id_input.text()
            try:
                camera_id = int(camera_id_str)
            except ValueError:
                camera_id = camera_id_str
            self.settings.set('camera.camera_id', camera_id)

        # Save resolution
        self.settings.set('camera.width', self.width_input.value())
        self.settings.set('camera.height', self.height_input.value())
        self.settings.set('camera.fps', self.fps_input.value())

        # Save advanced parameters
        self.settings.set('camera.exposure', self.exposure_input.value())
        self.settings.set('camera.gain', self.gain_input.value())

        self.settings.save()
        self.accept()

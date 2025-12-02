"""
Control Panel Widget - ควบคุมระบบ
Main control panel for inspection system
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGroupBox, QLabel, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ControlPanel(QWidget):
    """Panel ควบคุมระบบ"""

    # Signals
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    camera_connect_clicked = pyqtSignal()
    load_model_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    report_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self.is_paused = False
        self.setup_ui()

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()

        # Camera Control Group
        camera_group = QGroupBox("การควบคุมกล้อง")
        camera_layout = QVBoxLayout()

        self.connect_camera_btn = QPushButton("🎥 เชื่อมต่อกล้อง")
        self.connect_camera_btn.clicked.connect(self.camera_connect_clicked.emit)
        self.connect_camera_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.camera_status_label = QLabel("สถานะ: ไม่ได้เชื่อมต่อ")
        self.camera_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

        camera_layout.addWidget(self.connect_camera_btn)
        camera_layout.addWidget(self.camera_status_label)
        camera_group.setLayout(camera_layout)

        # Model Control Group
        model_group = QGroupBox("โมเดล YOLO")
        model_layout = QVBoxLayout()

        self.load_model_btn = QPushButton("📦 โหลดโมเดล")
        self.load_model_btn.clicked.connect(self.load_model_clicked.emit)
        self.load_model_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)

        self.model_status_label = QLabel("สถานะ: ยังไม่ได้โหลด")
        self.model_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

        model_layout.addWidget(self.load_model_btn)
        model_layout.addWidget(self.model_status_label)
        model_group.setLayout(model_layout)

        # Inspection Control Group
        inspection_group = QGroupBox("การตรวจสอบ")
        inspection_layout = QVBoxLayout()

        # Control buttons
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ เริ่ม")
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.start_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        self.pause_btn = QPushButton("⏸ พัก")
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        self.stop_btn = QPushButton("⏹ หยุด")
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.stop_btn)

        inspection_layout.addLayout(btn_layout)
        inspection_group.setLayout(inspection_layout)

        # Settings & Report Group
        tools_group = QGroupBox("เครื่องมือ")
        tools_layout = QVBoxLayout()

        self.settings_btn = QPushButton("⚙ ตั้งค่า")
        self.settings_btn.clicked.connect(self.settings_clicked.emit)

        self.report_btn = QPushButton("📊 สร้างรายงาน")
        self.report_btn.clicked.connect(self.report_clicked.emit)

        tools_layout.addWidget(self.settings_btn)
        tools_layout.addWidget(self.report_btn)
        tools_group.setLayout(tools_layout)

        # Add all groups to main layout
        layout.addWidget(camera_group)
        layout.addWidget(model_group)
        layout.addWidget(inspection_group)
        layout.addWidget(tools_group)
        layout.addStretch()

        self.setLayout(layout)

    def _on_start_clicked(self):
        """จัดการปุ่มเริ่ม"""
        if self.is_paused:
            self.pause_btn.setText("⏸ พัก")
            self.is_paused = False
        else:
            self.is_running = True
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)

        self.start_clicked.emit()

    def _on_pause_clicked(self):
        """จัดการปุ่มพัก"""
        if self.is_paused:
            self.pause_btn.setText("⏸ พัก")
            self.is_paused = False
        else:
            self.pause_btn.setText("▶ ดำเนินการต่อ")
            self.is_paused = True

        self.pause_clicked.emit()

    def _on_stop_clicked(self):
        """จัดการปุ่มหยุด"""
        self.is_running = False
        self.is_paused = False
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ พัก")
        self.stop_btn.setEnabled(False)
        self.stop_clicked.emit()

    def update_camera_status(self, connected: bool, info: str = ""):
        """อัพเดทสถานะกล้อง"""
        if connected:
            self.camera_status_label.setText(f"สถานะ: เชื่อมต่อแล้ว {info}")
            self.camera_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.connect_camera_btn.setText("🎥 ตัดการเชื่อมต่อ")
        else:
            self.camera_status_label.setText("สถานะ: ไม่ได้เชื่อมต่อ")
            self.camera_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            self.connect_camera_btn.setText("🎥 เชื่อมต่อกล้อง")

    def update_model_status(self, loaded: bool, info: str = ""):
        """อัพเดทสถานะโมเดล"""
        if loaded:
            self.model_status_label.setText(f"สถานะ: โหลดแล้ว {info}")
            self.model_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.model_status_label.setText("สถานะ: ยังไม่ได้โหลด")
            self.model_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

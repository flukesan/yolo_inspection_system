"""
Model Settings Dialog - ตั้งค่าโมเดล YOLO
Dialog for YOLO model configuration
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QDoubleSpinBox, QComboBox, QPushButton,
                             QGroupBox, QFormLayout, QFileDialog)
from PyQt6.QtCore import Qt


class ModelSettingsDialog(QDialog):
    """Dialog สำหรับตั้งค่าโมเดล YOLO"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("ตั้งค่าโมเดล YOLO")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Model Path
        model_group = QGroupBox("โมเดล")
        model_layout = QVBoxLayout()

        path_layout = QHBoxLayout()
        self.model_path_input = QLineEdit()
        self.model_path_input.setPlaceholderText("เส้นทางไปยังไฟล์โมเดล .pt")

        browse_btn = QPushButton("เรียกดู...")
        browse_btn.clicked.connect(self.browse_model)

        path_layout.addWidget(QLabel("Model Path:"))
        path_layout.addWidget(self.model_path_input)
        path_layout.addWidget(browse_btn)

        model_layout.addLayout(path_layout)
        model_group.setLayout(model_layout)

        # Detection Parameters
        params_group = QGroupBox("พารามิเตอร์การตรวจจับ")
        params_layout = QFormLayout()

        self.conf_threshold = QDoubleSpinBox()
        self.conf_threshold.setRange(0.0, 1.0)
        self.conf_threshold.setSingleStep(0.05)
        self.conf_threshold.setValue(0.5)
        params_layout.addRow("Confidence Threshold:", self.conf_threshold)

        self.iou_threshold = QDoubleSpinBox()
        self.iou_threshold.setRange(0.0, 1.0)
        self.iou_threshold.setSingleStep(0.05)
        self.iou_threshold.setValue(0.45)
        params_layout.addRow("IoU Threshold:", self.iou_threshold)

        self.device_combo = QComboBox()
        self.device_combo.addItems(["cpu", "cuda"])
        params_layout.addRow("Device:", self.device_combo)

        params_group.setLayout(params_layout)

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
        layout.addWidget(model_group)
        layout.addWidget(params_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_model(self):
        """เรียกดูไฟล์โมเดล"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "เลือกไฟล์โมเดล",
            "",
            "YOLO Models (*.pt *.pth)"
        )
        if filename:
            self.model_path_input.setText(filename)

    def load_settings(self):
        """โหลดการตั้งค่า"""
        self.model_path_input.setText(self.settings.get('yolo.model_path', ''))
        self.conf_threshold.setValue(self.settings.get('yolo.confidence_threshold', 0.5))
        self.iou_threshold.setValue(self.settings.get('yolo.iou_threshold', 0.45))

        device = self.settings.get('yolo.device', 'cpu')
        index = self.device_combo.findText(device)
        if index >= 0:
            self.device_combo.setCurrentIndex(index)

    def save_settings(self):
        """บันทึกการตั้งค่า"""
        self.settings.set('yolo.model_path', self.model_path_input.text())
        self.settings.set('yolo.confidence_threshold', self.conf_threshold.value())
        self.settings.set('yolo.iou_threshold', self.iou_threshold.value())
        self.settings.set('yolo.device', self.device_combo.currentText())

        self.settings.save()
        self.accept()

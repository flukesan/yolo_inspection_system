"""
Snapshot Training Settings Dialog
Dialog for configuring snapshot training mode settings
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QComboBox, QFileDialog,
                             QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt


class SnapshotTrainingSettingsDialog(QDialog):
    """Dialog สำหรับตั้งค่า Snapshot Training Mode"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Snapshot Training Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()

        # Output Directory Group
        dir_group = QGroupBox("โฟลเดอร์บันทึกรูป")
        dir_layout = QHBoxLayout()

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("เลือกโฟลเดอร์สำหรับเก็บรูป")

        browse_btn = QPushButton("📁 เลือกโฟลเดอร์")
        browse_btn.clicked.connect(self.browse_output_dir)

        dir_layout.addWidget(self.output_dir_edit)
        dir_layout.addWidget(browse_btn)
        dir_group.setLayout(dir_layout)

        # Image Settings Group
        img_group = QGroupBox("การตั้งค่ารูปภาพ")
        img_form = QFormLayout()

        # Image size
        self.image_size_combo = QComboBox()
        self.image_size_combo.addItems([
            "416x416",
            "640x640",
            "800x800",
            "1024x1024",
            "1280x1280"
        ])
        self.image_size_combo.setCurrentText("640x640")

        # File prefix
        self.file_prefix_edit = QLineEdit()
        self.file_prefix_edit.setPlaceholderText("train_image")
        self.file_prefix_edit.setText("train_image")

        img_form.addRow("ขนาดรูปภาพ:", self.image_size_combo)
        img_form.addRow("ชื่อไฟล์เริ่มต้น:", self.file_prefix_edit)

        # Info label
        info_label = QLabel("รูปแบบชื่อไฟล์: {prefix}_{YYYYMMDD_HHMMSS}.jpg")
        info_label.setStyleSheet("color: #888; font-size: 11px; font-style: italic;")
        img_form.addRow("", info_label)

        img_group.setLayout(img_form)

        # Buttons
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("💾 บันทึก")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_btn = QPushButton("❌ ยกเลิก")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        # Add all groups to main layout
        layout.addWidget(dir_group)
        layout.addWidget(img_group)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def browse_output_dir(self):
        """เลือกโฟลเดอร์สำหรับบันทึกรูป"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "เลือกโฟลเดอร์สำหรับบันทึกรูป",
            self.output_dir_edit.text() or "."
        )
        if directory:
            self.output_dir_edit.setText(directory)

    def load_settings(self):
        """โหลด settings ปัจจุบัน"""
        training_settings = self.settings.get('snapshot_training', {})

        output_dir = training_settings.get('output_dir', 'training_images')
        image_size = training_settings.get('image_size', '640x640')
        file_prefix = training_settings.get('file_prefix', 'train_image')

        self.output_dir_edit.setText(output_dir)
        self.image_size_combo.setCurrentText(image_size)
        self.file_prefix_edit.setText(file_prefix)

    def save_settings(self):
        """บันทึก settings"""
        output_dir = self.output_dir_edit.text().strip()
        image_size = self.image_size_combo.currentText()
        file_prefix = self.file_prefix_edit.text().strip()

        # Validation
        if not output_dir:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกโฟลเดอร์สำหรับบันทึกรูป")
            return

        if not file_prefix:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "คำเตือน", "กรุณาระบุชื่อไฟล์เริ่มต้น")
            return

        # Save to settings
        self.settings['snapshot_training'] = {
            'output_dir': output_dir,
            'image_size': image_size,
            'file_prefix': file_prefix
        }

        self.settings.save()
        self.accept()

    def get_settings(self):
        """ดึง settings ที่บันทึกไว้"""
        return self.settings.get('snapshot_training', {
            'output_dir': 'training_images',
            'image_size': '640x640',
            'file_prefix': 'train_image'
        })

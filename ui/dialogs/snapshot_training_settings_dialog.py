"""
Snapshot Training Settings Dialog
Dialog for configuring snapshot training mode settings
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QComboBox, QFileDialog,
                             QGroupBox, QFormLayout, QSpinBox, QCheckBox, QDoubleSpinBox)
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

        # Image Width
        self.width_spin = QSpinBox()
        self.width_spin.setRange(128, 4096)
        self.width_spin.setSingleStep(32)
        self.width_spin.setValue(640)
        self.width_spin.setSuffix(" px")
        img_form.addRow("Width:", self.width_spin)

        # Image Height
        self.height_spin = QSpinBox()
        self.height_spin.setRange(128, 4096)
        self.height_spin.setSingleStep(32)
        self.height_spin.setValue(640)
        self.height_spin.setSuffix(" px")
        img_form.addRow("Height:", self.height_spin)

        # File prefix
        self.file_prefix_edit = QLineEdit()
        self.file_prefix_edit.setPlaceholderText("train_image")
        self.file_prefix_edit.setText("train_image")
        img_form.addRow("ชื่อไฟล์เริ่มต้น:", self.file_prefix_edit)

        # Resize mode
        self.resize_mode_combo = QComboBox()
        self.resize_mode_combo.addItems([
            "Letterbox (รักษาสัดส่วน + padding)",
            "Crop (รักษาสัดส่วน ไม่มี padding)",
            "Stretch (บังคับขนาด อาจบิดเบี้ยว)"
        ])
        self.resize_mode_combo.setCurrentIndex(1)  # Default to Crop
        img_form.addRow("วิธีการ Resize:", self.resize_mode_combo)

        # Info label
        info_label = QLabel("รูปแบบชื่อไฟล์: {prefix}_{YYYYMMDD_HHMMSS}.jpg")
        info_label.setStyleSheet("color: #888; font-size: 11px; font-style: italic;")
        img_form.addRow("", info_label)

        img_group.setLayout(img_form)

        # Multi-Shot Settings Group
        multishot_group = QGroupBox("Multi-Shot Capture (ถ่ายหลายภาพต่อชิ้นงาน)")
        multishot_form = QFormLayout()

        # Enable multi-shot
        self.multishot_enabled = QCheckBox("เปิดใช้งาน Multi-Shot Mode")
        self.multishot_enabled.setToolTip("ถ่ายภาพหลายมุม/หลายส่วนต่อชิ้นงาน")
        self.multishot_enabled.stateChanged.connect(self.toggle_multishot_options)
        multishot_form.addRow("", self.multishot_enabled)

        # Shots per workpiece
        self.shots_per_workpiece = QSpinBox()
        self.shots_per_workpiece.setRange(2, 9)
        self.shots_per_workpiece.setValue(4)
        self.shots_per_workpiece.setToolTip("จำนวนภาพที่จะถ่ายต่อชิ้นงาน")
        multishot_form.addRow("จำนวน Shots:", self.shots_per_workpiece)

        # Shot interval
        self.shot_interval = QDoubleSpinBox()
        self.shot_interval.setRange(0.5, 10.0)
        self.shot_interval.setSingleStep(0.5)
        self.shot_interval.setValue(2.0)
        self.shot_interval.setSuffix(" วินาที")
        self.shot_interval.setToolTip("ระยะเวลาระหว่างการถ่ายแต่ละภาพ")
        multishot_form.addRow("ระยะห่าง:", self.shot_interval)

        # Auto advance
        self.auto_advance = QCheckBox("ถ่ายอัตโนมัติ (Auto-advance)")
        self.auto_advance.setChecked(True)
        self.auto_advance.setToolTip("ถ่ายอัตโนมัติตาม interval หรือรอกด Space Bar")
        multishot_form.addRow("", self.auto_advance)

        # Info label
        multishot_info = QLabel(
            "💡 Multi-Shot Mode: ถ่ายภาพหลายมุมต่อชิ้นงาน\n"
            "   - เหมาะสำหรับชิ้นงานขนาดใหญ่\n"
            "   - รูปแบบชื่อ: {class}/wp{id:03d}_shot{n}.jpg"
        )
        multishot_info.setStyleSheet("color: #888; font-size: 10px; padding: 5px;")
        multishot_form.addRow("", multishot_info)

        multishot_group.setLayout(multishot_form)

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
        layout.addWidget(multishot_group)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def toggle_multishot_options(self):
        """เปิด/ปิด multishot options ตามสถานะ checkbox"""
        enabled = self.multishot_enabled.isChecked()
        self.shots_per_workpiece.setEnabled(enabled)
        self.shot_interval.setEnabled(enabled)
        self.auto_advance.setEnabled(enabled)

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
        file_prefix = training_settings.get('file_prefix', 'train_image')
        resize_mode = training_settings.get('resize_mode', 'crop')

        # Load width and height (support legacy image_size format)
        if 'width' in training_settings and 'height' in training_settings:
            width = training_settings.get('width', 640)
            height = training_settings.get('height', 640)
        else:
            # Legacy support: parse image_size "640x640"
            image_size = training_settings.get('image_size', '640x640')
            try:
                width, height = map(int, image_size.split('x'))
            except:
                width, height = 640, 640

        self.output_dir_edit.setText(output_dir)
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
        self.file_prefix_edit.setText(file_prefix)

        # Set resize mode
        if resize_mode == 'letterbox':
            self.resize_mode_combo.setCurrentIndex(0)
        elif resize_mode == 'crop':
            self.resize_mode_combo.setCurrentIndex(1)
        elif resize_mode == 'stretch':
            self.resize_mode_combo.setCurrentIndex(2)

        # Load multi-shot settings
        multishot_enabled = training_settings.get('multishot_enabled', False)
        multishot_shots = training_settings.get('multishot_shots', 4)
        multishot_interval = training_settings.get('multishot_interval', 2.0)
        multishot_auto = training_settings.get('multishot_auto_advance', True)

        self.multishot_enabled.setChecked(multishot_enabled)
        self.shots_per_workpiece.setValue(multishot_shots)
        self.shot_interval.setValue(multishot_interval)
        self.auto_advance.setChecked(multishot_auto)

        # Toggle multishot options
        self.toggle_multishot_options()

    def save_settings(self):
        """บันทึก settings"""
        output_dir = self.output_dir_edit.text().strip()
        width = self.width_spin.value()
        height = self.height_spin.value()
        file_prefix = self.file_prefix_edit.text().strip()

        # Get resize mode
        resize_mode_index = self.resize_mode_combo.currentIndex()
        if resize_mode_index == 0:
            resize_mode = 'letterbox'
        elif resize_mode_index == 1:
            resize_mode = 'crop'
        else:  # 2
            resize_mode = 'stretch'

        # Validation
        if not output_dir:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกโฟลเดอร์สำหรับบันทึกรูป")
            return

        if not file_prefix:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "คำเตือน", "กรุณาระบุชื่อไฟล์เริ่มต้น")
            return

        # Save to settings using set() method
        self.settings.set('snapshot_training.output_dir', output_dir)
        self.settings.set('snapshot_training.width', width)
        self.settings.set('snapshot_training.height', height)
        self.settings.set('snapshot_training.file_prefix', file_prefix)
        self.settings.set('snapshot_training.resize_mode', resize_mode)

        # Save multi-shot settings
        self.settings.set('snapshot_training.multishot_enabled', self.multishot_enabled.isChecked())
        self.settings.set('snapshot_training.multishot_shots', self.shots_per_workpiece.value())
        self.settings.set('snapshot_training.multishot_interval', self.shot_interval.value())
        self.settings.set('snapshot_training.multishot_auto_advance', self.auto_advance.isChecked())

        self.settings.save()
        self.accept()

    def get_settings(self):
        """ดึง settings ที่บันทึกไว้"""
        return self.settings.get('snapshot_training', {
            'output_dir': 'training_images',
            'image_size': '640x640',
            'file_prefix': 'train_image'
        })

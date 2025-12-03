"""
Model Profiles Dialog - จัดการ Model Profiles
Manage YOLO model profiles for different inspection types
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QGroupBox, QLineEdit, QComboBox, QSpinBox,
                             QMessageBox, QFileDialog, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os


class ModelProfilesDialog(QDialog):
    """Dialog สำหรับจัดการ Model Profiles"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.modified = False
        self.selected_profile = None  # Store selected profile for loading
        self.setup_ui()
        self.load_profiles()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("จัดการ Model Profiles")
        self.setMinimumSize(900, 650)

        layout = QVBoxLayout()

        # Title
        title_label = QLabel("จัดการ YOLO Model Profiles")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel("จัดการโมเดล YOLO สำหรับการตรวจสอบชิ้นงานประเภทต่างๆ")
        desc_label.setStyleSheet("color: #888; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # Main content
        content_layout = QHBoxLayout()

        # Left side - Profile list
        left_layout = QVBoxLayout()

        list_label = QLabel("Model Profiles ที่บันทึกไว้:")
        left_layout.addWidget(list_label)

        self.profile_list = QListWidget()
        self.profile_list.itemClicked.connect(self.on_profile_selected)
        left_layout.addWidget(self.profile_list)

        # Profile buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ เพิ่ม")
        self.add_btn.clicked.connect(self.on_add_profile)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("🗑️ ลบ")
        self.delete_btn.clicked.connect(self.on_delete_profile)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        self.set_default_btn = QPushButton("⭐ ตั้งเป็นค่าเริ่มต้น")
        self.set_default_btn.clicked.connect(self.on_set_default)
        self.set_default_btn.setEnabled(False)
        button_layout.addWidget(self.set_default_btn)

        left_layout.addLayout(button_layout)

        # Load button (separate row)
        load_layout = QHBoxLayout()
        self.load_btn = QPushButton("📦 โหลดโมเดลนี้")
        self.load_btn.clicked.connect(self.on_load_profile)
        self.load_btn.setEnabled(False)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        load_layout.addWidget(self.load_btn)
        left_layout.addLayout(load_layout)

        content_layout.addLayout(left_layout, stretch=2)

        # Right side - Profile details
        right_group = QGroupBox("รายละเอียดโมเดล")
        right_layout = QVBoxLayout()

        # Profile name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("ชื่อ Profile:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("เช่น: Defect Detection v1, Scratch Inspection")
        self.name_edit.textChanged.connect(self.on_profile_modified)
        name_layout.addWidget(self.name_edit)
        right_layout.addLayout(name_layout)

        # Model type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("ประเภทโมเดล:"))
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems([
            "Object Detection (ตรวจจับวัตถุ)",
            "Segmentation (ตัดเส้นขอบวัตถุ)",
            "Classification (จำแนกประเภท)",
            "Pose Estimation (ตรวจจับท่าทาง)"
        ])
        self.model_type_combo.currentTextChanged.connect(self.on_model_type_changed)
        type_layout.addWidget(self.model_type_combo)

        # Add help text
        type_help = QLabel("(เลือกให้ตรงกับไฟล์โมเดล)")
        type_help.setStyleSheet("color: #888; font-size: 10px;")
        type_layout.addWidget(type_help)

        right_layout.addLayout(type_layout)

        # Model path
        path_group = QGroupBox("ไฟล์โมเดล")
        path_layout = QVBoxLayout()

        path_input_layout = QHBoxLayout()
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setPlaceholderText("models/yolov8_defect.pt")
        self.model_path_edit.textChanged.connect(self.on_profile_modified)
        path_input_layout.addWidget(self.model_path_edit)

        self.browse_btn = QPushButton("📁 เลือกไฟล์")
        self.browse_btn.clicked.connect(self.on_browse_model)
        path_input_layout.addWidget(self.browse_btn)

        path_layout.addLayout(path_input_layout)

        # File status
        self.file_status_label = QLabel("")
        self.file_status_label.setStyleSheet("font-size: 10px;")
        path_layout.addWidget(self.file_status_label)

        path_group.setLayout(path_layout)
        right_layout.addWidget(path_group)

        # Detection settings
        detection_group = QGroupBox("การตั้งค่าการตรวจจับ")
        detection_layout = QVBoxLayout()

        # Confidence threshold
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Confidence Threshold:"))
        self.conf_spin = QDoubleSpinBox()
        self.conf_spin.setMinimum(0.01)
        self.conf_spin.setMaximum(1.0)
        self.conf_spin.setSingleStep(0.05)
        self.conf_spin.setValue(0.5)
        self.conf_spin.setDecimals(2)
        self.conf_spin.valueChanged.connect(self.on_profile_modified)
        conf_layout.addWidget(self.conf_spin)
        conf_layout.addWidget(QLabel("(0.01-1.0)"))
        detection_layout.addLayout(conf_layout)

        # IOU threshold
        iou_layout = QHBoxLayout()
        iou_layout.addWidget(QLabel("IOU Threshold:"))
        self.iou_spin = QDoubleSpinBox()
        self.iou_spin.setMinimum(0.01)
        self.iou_spin.setMaximum(1.0)
        self.iou_spin.setSingleStep(0.05)
        self.iou_spin.setValue(0.45)
        self.iou_spin.setDecimals(2)
        self.iou_spin.valueChanged.connect(self.on_profile_modified)
        iou_layout.addWidget(self.iou_spin)
        iou_layout.addWidget(QLabel("(0.01-1.0)"))
        detection_layout.addLayout(iou_layout)

        # Image size
        img_layout = QHBoxLayout()
        img_layout.addWidget(QLabel("Image Size:"))
        self.img_size_combo = QComboBox()
        self.img_size_combo.addItems(["320", "480", "640", "800", "1024", "1280"])
        self.img_size_combo.setCurrentText("640")
        self.img_size_combo.currentTextChanged.connect(self.on_profile_modified)
        img_layout.addWidget(self.img_size_combo)
        img_layout.addWidget(QLabel("(pixels)"))
        detection_layout.addLayout(img_layout)

        detection_group.setLayout(detection_layout)
        right_layout.addWidget(detection_group)

        # Device settings
        device_group = QGroupBox("อุปกรณ์")
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        self.device_combo.addItems(["cpu", "cuda"])
        self.device_combo.setCurrentText("cpu")
        self.device_combo.currentTextChanged.connect(self.on_profile_modified)
        device_layout.addWidget(self.device_combo)

        help_label = QLabel("(cuda = GPU, cpu = CPU)")
        help_label.setStyleSheet("color: #888; font-size: 10px;")
        device_layout.addWidget(help_label)

        device_group.setLayout(device_layout)
        right_layout.addWidget(device_group)

        # Save button
        self.save_profile_btn = QPushButton("💾 บันทึก Profile นี้")
        self.save_profile_btn.clicked.connect(self.on_save_profile)
        self.save_profile_btn.setEnabled(False)
        right_layout.addWidget(self.save_profile_btn)

        right_layout.addStretch()
        right_group.setLayout(right_layout)
        content_layout.addWidget(right_group, stretch=3)

        layout.addLayout(content_layout)

        # Dialog buttons
        button_box = QHBoxLayout()
        button_box.addStretch()

        close_btn = QPushButton("ปิด")
        close_btn.clicked.connect(self.accept)
        button_box.addWidget(close_btn)

        layout.addLayout(button_box)
        self.setLayout(layout)

    def load_profiles(self):
        """โหลด profiles จาก settings"""
        self.profile_list.clear()

        profiles = self.settings.get("model_profiles", {})
        default_profile = self.settings.get("yolo", {}).get("default_profile", None)

        for profile_name, profile_data in profiles.items():
            item = QListWidgetItem(profile_name)

            # Mark default profile
            if profile_name == default_profile:
                item.setText(f"⭐ {profile_name}")
                item.setData(Qt.ItemDataRole.UserRole, {"is_default": True, **profile_data})
            else:
                item.setData(Qt.ItemDataRole.UserRole, {"is_default": False, **profile_data})

            self.profile_list.addItem(item)

    def on_profile_selected(self, item):
        """เมื่อเลือก profile"""
        self.delete_btn.setEnabled(True)
        self.set_default_btn.setEnabled(True)
        self.load_btn.setEnabled(True)

        profile_data = item.data(Qt.ItemDataRole.UserRole)

        # Remove star from name if present
        profile_name = item.text().replace("⭐ ", "")
        self.name_edit.setText(profile_name)

        # Set model type
        model_type = profile_data.get("model_type", "detection")
        type_map = {
            "detection": "Object Detection (ตรวจจับวัตถุ)",
            "segmentation": "Segmentation (ตัดเส้นขอบวัตถุ)",
            "classification": "Classification (จำแนกประเภท)",
            "pose": "Pose Estimation (ตรวจจับท่าทาง)"
        }
        self.model_type_combo.setCurrentText(type_map.get(model_type, "Object Detection (ตรวจจับวัตถุ)"))

        # Set model path
        self.model_path_edit.setText(profile_data.get("model_path", ""))
        self.update_file_status(profile_data.get("model_path", ""))

        # Set detection settings
        self.conf_spin.setValue(profile_data.get("confidence_threshold", 0.5))
        self.iou_spin.setValue(profile_data.get("iou_threshold", 0.45))
        self.img_size_combo.setCurrentText(str(profile_data.get("img_size", 640)))

        # Set device
        self.device_combo.setCurrentText(profile_data.get("device", "cpu"))

    def on_profile_modified(self):
        """เมื่อแก้ไข profile"""
        self.save_profile_btn.setEnabled(True)

        # Update file status when path changes
        if hasattr(self, 'model_path_edit'):
            self.update_file_status(self.model_path_edit.text())

    def on_model_type_changed(self, model_type_text):
        """เมื่อเปลี่ยนประเภทโมเดล"""
        self.on_profile_modified()

        # Show info about model type
        type_info = {
            "Object Detection (ตรวจจับวัตถุ)": "ไฟล์: yolov8*.pt (เช่น yolov8n.pt, yolov8s.pt)",
            "Segmentation (ตัดเส้นขอบวัตถุ)": "ไฟล์: yolov8*-seg.pt (เช่น yolov8n-seg.pt)",
            "Classification (จำแนกประเภท)": "ไฟล์: yolov8*-cls.pt (เช่น yolov8n-cls.pt)",
            "Pose Estimation (ตรวจจับท่าทาง)": "ไฟล์: yolov8*-pose.pt (เช่น yolov8n-pose.pt)"
        }

        info_text = type_info.get(model_type_text, "")
        if info_text:
            # Update model path placeholder
            self.model_path_edit.setPlaceholderText(info_text.replace("ไฟล์: ", "models/"))

    def update_file_status(self, path):
        """อัพเดทสถานะไฟล์"""
        if not path:
            self.file_status_label.setText("")
            return

        if os.path.exists(path):
            file_size = os.path.getsize(path) / (1024 * 1024)  # MB
            self.file_status_label.setText(f"✓ ไฟล์พบ: {file_size:.1f} MB")
            self.file_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
        else:
            self.file_status_label.setText("✗ ไม่พบไฟล์")
            self.file_status_label.setStyleSheet("color: #f44336; font-size: 10px;")

    def on_browse_model(self):
        """เลือกไฟล์โมเดล"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "เลือกไฟล์โมเดล YOLO",
            "",
            "YOLO Models (*.pt *.pth);;All Files (*.*)"
        )

        if file_path:
            self.model_path_edit.setText(file_path)
            self.update_file_status(file_path)
            self.on_profile_modified()

    def on_add_profile(self):
        """เพิ่ม profile ใหม่"""
        # Clear form
        self.name_edit.clear()
        self.model_type_combo.setCurrentText("Object Detection (ตรวจจับวัตถุ)")
        self.model_path_edit.clear()
        self.conf_spin.setValue(0.5)
        self.iou_spin.setValue(0.45)
        self.img_size_combo.setCurrentText("640")
        self.device_combo.setCurrentText("cpu")
        self.file_status_label.setText("")

        self.name_edit.setFocus()
        self.save_profile_btn.setEnabled(True)

    def on_save_profile(self):
        """บันทึก profile"""
        profile_name = self.name_edit.text().strip()

        if not profile_name:
            QMessageBox.warning(self, "คำเตือน", "กรุณาใส่ชื่อ Profile")
            return

        model_path = self.model_path_edit.text().strip()
        if not model_path:
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกไฟล์โมเดล")
            return

        # Warn if file doesn't exist
        if not os.path.exists(model_path):
            reply = QMessageBox.question(
                self,
                "ไฟล์ไม่พบ",
                "ไม่พบไฟล์โมเดลที่ระบุ\nต้องการบันทึก Profile ต่อหรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Get model type
        model_type_text = self.model_type_combo.currentText()
        type_reverse_map = {
            "Object Detection (ตรวจจับวัตถุ)": "detection",
            "Segmentation (ตัดเส้นขอบวัตถุ)": "segmentation",
            "Classification (จำแนกประเภท)": "classification",
            "Pose Estimation (ตรวจจับท่าทาง)": "pose"
        }
        model_type = type_reverse_map.get(model_type_text, "detection")

        # Create profile data
        profile_data = {
            "model_type": model_type,
            "model_path": model_path,
            "device": self.device_combo.currentText(),
            "confidence_threshold": self.conf_spin.value(),
            "iou_threshold": self.iou_spin.value(),
            "img_size": int(self.img_size_combo.currentText())
        }

        # Save to settings
        profiles = self.settings.get("model_profiles", {})
        profiles[profile_name] = profile_data
        self.settings.set("model_profiles", profiles)
        self.settings.save()

        # Reload list
        self.load_profiles()

        self.modified = True
        self.save_profile_btn.setEnabled(False)

        QMessageBox.information(self, "สำเร็จ", f"บันทึก Profile '{profile_name}' เรียบร้อยแล้ว")

    def on_delete_profile(self):
        """ลบ profile"""
        item = self.profile_list.currentItem()
        if not item:
            return

        profile_name = item.text().replace("⭐ ", "")

        reply = QMessageBox.question(
            self,
            "ยืนยันการลบ",
            f"ต้องการลบ Profile '{profile_name}' หรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from settings
            profiles = self.settings.get("model_profiles", {})
            if profile_name in profiles:
                del profiles[profile_name]
                self.settings.set("model_profiles", profiles)

                # If it was default, clear default
                if item.data(Qt.ItemDataRole.UserRole).get("is_default"):
                    yolo_settings = self.settings.get("yolo", {})
                    yolo_settings["default_profile"] = None
                    self.settings.set("yolo", yolo_settings)

                self.settings.save()
                self.load_profiles()
                self.modified = True

                QMessageBox.information(self, "สำเร็จ", f"ลบ Profile '{profile_name}' เรียบร้อยแล้ว")

    def on_set_default(self):
        """ตั้งเป็น profile เริ่มต้น"""
        item = self.profile_list.currentItem()
        if not item:
            return

        profile_name = item.text().replace("⭐ ", "")

        # Update settings
        yolo_settings = self.settings.get("yolo", {})
        yolo_settings["default_profile"] = profile_name
        self.settings.set("yolo", yolo_settings)
        self.settings.save()

        # Reload list
        self.load_profiles()
        self.modified = True

        QMessageBox.information(self, "สำเร็จ", f"ตั้ง '{profile_name}' เป็น Profile เริ่มต้นแล้ว")

    def on_load_profile(self):
        """โหลดโมเดลด้วย profile ที่เลือก"""
        item = self.profile_list.currentItem()
        if not item:
            return

        profile_name = item.text().replace("⭐ ", "")
        profile_data = item.data(Qt.ItemDataRole.UserRole)

        # Store selected profile data
        self.selected_profile = {
            "name": profile_name,
            "model_type": profile_data.get("model_type", "detection"),
            "model_path": profile_data.get("model_path", ""),
            "device": profile_data.get("device", "cpu"),
            "confidence_threshold": profile_data.get("confidence_threshold", 0.5),
            "iou_threshold": profile_data.get("iou_threshold", 0.45),
            "img_size": profile_data.get("img_size", 640)
        }

        # Close dialog and return Accepted
        self.accept()

"""
Camera Profiles Dialog - จัดการ Camera Profiles
Manage camera profiles (USB and RTSP)
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QGroupBox, QLineEdit, QComboBox, QSpinBox,
                             QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CameraProfilesDialog(QDialog):
    """Dialog สำหรับจัดการ Camera Profiles"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.modified = False
        self.selected_profile = None  # Store selected profile for connection
        self.setup_ui()
        self.load_profiles()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("จัดการ Camera Profiles")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        # Title
        title_label = QLabel("จัดการ Camera Profiles")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Main content
        content_layout = QHBoxLayout()

        # Left side - Profile list
        left_layout = QVBoxLayout()

        list_label = QLabel("Camera Profiles ที่บันทึกไว้:")
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

        # Connect button (separate row)
        connect_layout = QHBoxLayout()
        self.connect_btn = QPushButton("🔌 เชื่อมต่อด้วย Profile นี้")
        self.connect_btn.clicked.connect(self.on_connect_profile)
        self.connect_btn.setEnabled(False)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        connect_layout.addWidget(self.connect_btn)
        left_layout.addLayout(connect_layout)

        content_layout.addLayout(left_layout, stretch=2)

        # Right side - Profile details
        right_group = QGroupBox("รายละเอียด")
        right_layout = QVBoxLayout()

        # Profile name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("ชื่อ Profile:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("เช่น: กล้องหน้า, IP Camera 1")
        self.name_edit.textChanged.connect(self.on_profile_modified)
        name_layout.addWidget(self.name_edit)
        right_layout.addLayout(name_layout)

        # Camera type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("ประเภท:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["USB Camera", "RTSP/IP Camera"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        right_layout.addLayout(type_layout)

        # USB Camera settings
        self.usb_group = QGroupBox("การตั้งค่า USB Camera")
        usb_layout = QVBoxLayout()

        usb_source_layout = QHBoxLayout()
        usb_source_layout.addWidget(QLabel("Camera Index:"))
        self.usb_index_spin = QSpinBox()
        self.usb_index_spin.setMinimum(0)
        self.usb_index_spin.setMaximum(10)
        self.usb_index_spin.setValue(0)
        self.usb_index_spin.valueChanged.connect(self.on_profile_modified)
        usb_source_layout.addWidget(self.usb_index_spin)
        usb_layout.addLayout(usb_source_layout)

        self.usb_group.setLayout(usb_layout)
        right_layout.addWidget(self.usb_group)

        # RTSP Camera settings
        self.rtsp_group = QGroupBox("การตั้งค่า RTSP/IP Camera")
        rtsp_layout = QVBoxLayout()

        rtsp_url_layout = QVBoxLayout()
        rtsp_url_layout.addWidget(QLabel("RTSP URL:"))
        self.rtsp_url_edit = QLineEdit()
        self.rtsp_url_edit.setPlaceholderText("rtsp://username:password@192.168.1.100:554/stream")
        self.rtsp_url_edit.textChanged.connect(self.on_profile_modified)
        rtsp_url_layout.addWidget(self.rtsp_url_edit)

        # Help text
        help_label = QLabel("ตัวอย่าง:\n"
                           "• rtsp://admin:12345@192.168.1.100:554/stream1\n"
                           "• rtsp://192.168.1.100/live\n"
                           "• http://192.168.1.100:8080/video")
        help_label.setStyleSheet("color: #888; font-size: 10px;")
        rtsp_url_layout.addWidget(help_label)

        rtsp_layout.addLayout(rtsp_url_layout)
        self.rtsp_group.setLayout(rtsp_layout)
        right_layout.addWidget(self.rtsp_group)

        # Resolution settings
        res_group = QGroupBox("ความละเอียด")
        res_layout = QHBoxLayout()

        res_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setMinimum(320)
        self.width_spin.setMaximum(3840)
        self.width_spin.setSingleStep(160)
        self.width_spin.setValue(1280)
        self.width_spin.valueChanged.connect(self.on_profile_modified)
        res_layout.addWidget(self.width_spin)

        res_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setMinimum(240)
        self.height_spin.setMaximum(2160)
        self.height_spin.setSingleStep(120)
        self.height_spin.setValue(720)
        self.height_spin.valueChanged.connect(self.on_profile_modified)
        res_layout.addWidget(self.height_spin)

        res_layout.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setMinimum(1)
        self.fps_spin.setMaximum(120)
        self.fps_spin.setValue(30)
        self.fps_spin.valueChanged.connect(self.on_profile_modified)
        res_layout.addWidget(self.fps_spin)

        res_group.setLayout(res_layout)
        right_layout.addWidget(res_group)

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

        # Update UI based on type
        self.on_type_changed(self.type_combo.currentText())

    def load_profiles(self):
        """โหลด profiles จาก settings"""
        self.profile_list.clear()

        profiles = self.settings.get("camera_profiles", {})
        default_profile = self.settings.get("camera", {}).get("default_profile", None)

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
        self.connect_btn.setEnabled(True)

        profile_data = item.data(Qt.ItemDataRole.UserRole)

        # Remove star from name if present
        profile_name = item.text().replace("⭐ ", "")
        self.name_edit.setText(profile_name)

        # Set type
        camera_type = profile_data.get("type", "usb")
        if camera_type == "usb":
            self.type_combo.setCurrentText("USB Camera")
            self.usb_index_spin.setValue(int(profile_data.get("source", 0)))
        else:
            self.type_combo.setCurrentText("RTSP/IP Camera")
            self.rtsp_url_edit.setText(profile_data.get("source", ""))

        # Set resolution
        self.width_spin.setValue(profile_data.get("width", 1280))
        self.height_spin.setValue(profile_data.get("height", 720))
        self.fps_spin.setValue(profile_data.get("fps", 30))

    def on_type_changed(self, camera_type):
        """เมื่อเปลี่ยนประเภทกล้อง"""
        if camera_type == "USB Camera":
            self.usb_group.setVisible(True)
            self.rtsp_group.setVisible(False)
        else:
            self.usb_group.setVisible(False)
            self.rtsp_group.setVisible(True)

        self.on_profile_modified()

    def on_profile_modified(self):
        """เมื่อแก้ไข profile"""
        self.save_profile_btn.setEnabled(True)

    def on_add_profile(self):
        """เพิ่ม profile ใหม่"""
        # Clear form
        self.name_edit.clear()
        self.usb_index_spin.setValue(0)
        self.rtsp_url_edit.clear()
        self.width_spin.setValue(1280)
        self.height_spin.setValue(720)
        self.fps_spin.setValue(30)

        self.name_edit.setFocus()
        self.save_profile_btn.setEnabled(True)

    def on_save_profile(self):
        """บันทึก profile"""
        profile_name = self.name_edit.text().strip()

        if not profile_name:
            QMessageBox.warning(self, "คำเตือน", "กรุณาใส่ชื่อ Profile")
            return

        # Get camera type and source
        camera_type = "usb" if self.type_combo.currentText() == "USB Camera" else "rtsp"

        if camera_type == "usb":
            source = self.usb_index_spin.value()
        else:
            source = self.rtsp_url_edit.text().strip()
            if not source:
                QMessageBox.warning(self, "คำเตือน", "กรุณาใส่ RTSP URL")
                return

        # Create profile data
        profile_data = {
            "type": camera_type,
            "source": source,
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "fps": self.fps_spin.value()
        }

        # Save to settings
        profiles = self.settings.get("camera_profiles", {})
        profiles[profile_name] = profile_data
        self.settings.set("camera_profiles", profiles)
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
            profiles = self.settings.get("camera_profiles", {})
            if profile_name in profiles:
                del profiles[profile_name]
                self.settings.set("camera_profiles", profiles)

                # If it was default, clear default
                if item.data(Qt.ItemDataRole.UserRole).get("is_default"):
                    camera_settings = self.settings.get("camera", {})
                    camera_settings["default_profile"] = None
                    self.settings.set("camera", camera_settings)

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
        camera_settings = self.settings.get("camera", {})
        camera_settings["default_profile"] = profile_name
        self.settings.set("camera", camera_settings)
        self.settings.save()

        # Reload list
        self.load_profiles()
        self.modified = True

        QMessageBox.information(self, "สำเร็จ", f"ตั้ง '{profile_name}' เป็น Profile เริ่มต้นแล้ว")

    def on_connect_profile(self):
        """เชื่อมต่อด้วย profile ที่เลือก"""
        item = self.profile_list.currentItem()
        if not item:
            return

        profile_name = item.text().replace("⭐ ", "")
        profile_data = item.data(Qt.ItemDataRole.UserRole)

        # Store selected profile data
        self.selected_profile = {
            "name": profile_name,
            "type": profile_data.get("type", "usb"),
            "source": profile_data.get("source", 0),
            "width": profile_data.get("width", 1280),
            "height": profile_data.get("height", 720),
            "fps": profile_data.get("fps", 30)
        }

        # Close dialog and return Accepted
        self.accept()

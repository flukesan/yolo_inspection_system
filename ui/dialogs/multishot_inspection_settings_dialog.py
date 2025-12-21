"""
Multi-Shot Inspection Settings Dialog
Dialog สำหรับตั้งค่า multi-shot inspection
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt


class MultiShotInspectionSettingsDialog(QDialog):
    """Dialog สำหรับตั้งค่า Multi-Shot Inspection"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Multi-Shot Inspection Settings")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()

        # Enable Multi-Shot Group
        enable_group = QGroupBox("Multi-Shot Inspection")
        enable_layout = QVBoxLayout()

        self.enable_multishot = QCheckBox("เปิดใช้งาน Multi-Shot Inspection")
        self.enable_multishot.setToolTip("เปิดใช้งานการตรวจสอบแบบหลายภาพ")
        self.enable_multishot.stateChanged.connect(self.toggle_multishot_options)
        enable_layout.addWidget(self.enable_multishot)

        info_label = QLabel(
            "💡 Multi-Shot Inspection จะถ่ายภาพหลายมุมแล้วรวมผลลัพธ์\n"
            "   เหมาะสำหรับชิ้นงานขนาดใหญ่หรือต้องการความแม่นยำสูง"
        )
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        enable_layout.addWidget(info_label)

        enable_group.setLayout(enable_layout)

        # Configuration Group
        config_group = QGroupBox("การตั้งค่า Multi-Shot")
        config_form = QFormLayout()

        # Number of shots
        self.shots_spin = QSpinBox()
        self.shots_spin.setRange(2, 9)
        self.shots_spin.setValue(4)
        self.shots_spin.setToolTip("จำนวนภาพที่จะถ่ายต่อชิ้นงาน")
        config_form.addRow("จำนวน Shots:", self.shots_spin)

        # Shot interval
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.5, 10.0)
        self.interval_spin.setSingleStep(0.5)
        self.interval_spin.setValue(2.0)
        self.interval_spin.setSuffix(" วินาที")
        self.interval_spin.setToolTip("ระยะเวลาระหว่างการถ่ายแต่ละภาพ")
        config_form.addRow("ระยะห่าง:", self.interval_spin)

        # Aggregation strategy
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "Majority Vote (≥50%)",
            "Unanimous (100%)",
            "Any Detection (≥1)",
            "Confidence Weighted"
        ])
        self.strategy_combo.setCurrentIndex(0)
        self.strategy_combo.setToolTip("วิธีการรวมผลลัพธ์จากหลายภาพ")
        self.strategy_combo.currentIndexChanged.connect(self.update_strategy_description)
        config_form.addRow("กลยุทธ์:", self.strategy_combo)

        # Strategy description
        self.strategy_desc = QLabel()
        self.strategy_desc.setWordWrap(True)
        self.strategy_desc.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        config_form.addRow("", self.strategy_desc)

        config_group.setLayout(config_form)

        # Save Options Group
        save_group = QGroupBox("ตัวเลือกการบันทึก")
        save_layout = QVBoxLayout()

        self.save_all_shots = QCheckBox("บันทึกภาพทุก shots")
        self.save_all_shots.setChecked(True)
        self.save_all_shots.setToolTip("บันทึกภาพทั้งหมดที่ถ่ายสำหรับการ audit")
        save_layout.addWidget(self.save_all_shots)

        self.save_report = QCheckBox("บันทึก Aggregation Report")
        self.save_report.setChecked(True)
        self.save_report.setToolTip("บันทึกรายงานการรวมผลลัพธ์เป็น JSON")
        save_layout.addWidget(self.save_report)

        save_group.setLayout(save_layout)

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

        # Add all groups to layout
        layout.addWidget(enable_group)
        layout.addWidget(config_group)
        layout.addWidget(save_group)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Update strategy description
        self.update_strategy_description()

    def toggle_multishot_options(self):
        """เปิด/ปิด options ตาม checkbox"""
        enabled = self.enable_multishot.isChecked()

        # Find all widgets to enable/disable
        for widget in [self.shots_spin, self.interval_spin, self.strategy_combo,
                       self.save_all_shots, self.save_report]:
            widget.setEnabled(enabled)

    def update_strategy_description(self):
        """อัพเดทคำอธิบาย strategy"""
        descriptions = {
            0: "✓ แนะนำ: Defect ต้องปรากฏใน >50% ของภาพ\n  เหมาะสำหรับการใช้งานทั่วไป",
            1: "🔒 เข้มงวด: Defect ต้องปรากฏใน 100% ของภาพ\n  ลด false positive สูง",
            2: "⚡ ไว: Defect ปรากฏในภาพใดก็ได้\n  ตรวจจับทุกความเป็นไปได้",
            3: "📊 สถิติ: คำนวณถ่วงน้ำหนักจาก confidence\n  เหมาะสำหรับ quality audit"
        }

        idx = self.strategy_combo.currentIndex()
        self.strategy_desc.setText(descriptions.get(idx, ""))

    def load_settings(self):
        """โหลด settings"""
        inspection_settings = self.settings.get('inspection', {})

        # Load multi-shot settings
        enabled = inspection_settings.get('multishot_enabled', False)
        shots = inspection_settings.get('multishot_shots', 4)
        interval = inspection_settings.get('multishot_interval', 2.0)
        strategy = inspection_settings.get('multishot_strategy', 'majority_vote')
        save_shots = inspection_settings.get('multishot_save_all_shots', True)
        save_rep = inspection_settings.get('multishot_save_report', True)

        self.enable_multishot.setChecked(enabled)
        self.shots_spin.setValue(shots)
        self.interval_spin.setValue(interval)

        # Map strategy to combo index
        strategy_map = {
            'majority_vote': 0,
            'unanimous': 1,
            'any': 2,
            'confidence_weighted': 3
        }
        self.strategy_combo.setCurrentIndex(strategy_map.get(strategy, 0))

        self.save_all_shots.setChecked(save_shots)
        self.save_report.setChecked(save_rep)

        # Toggle options
        self.toggle_multishot_options()

    def save_settings(self):
        """บันทึก settings"""
        # Map combo index to strategy
        strategy_map = {
            0: 'majority_vote',
            1: 'unanimous',
            2: 'any',
            3: 'confidence_weighted'
        }

        # Save settings
        self.settings.set('inspection.multishot_enabled', self.enable_multishot.isChecked())
        self.settings.set('inspection.multishot_shots', self.shots_spin.value())
        self.settings.set('inspection.multishot_interval', self.interval_spin.value())
        self.settings.set('inspection.multishot_strategy', strategy_map[self.strategy_combo.currentIndex()])
        self.settings.set('inspection.multishot_save_all_shots', self.save_all_shots.isChecked())
        self.settings.set('inspection.multishot_save_report', self.save_report.isChecked())

        self.settings.save()

        QMessageBox.information(
            self,
            "สำเร็จ",
            "บันทึกการตั้งค่า Multi-Shot Inspection เรียบร้อย"
        )

        self.accept()

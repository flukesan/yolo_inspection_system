"""
Validation Rules Dialog - กำหนดเงื่อนไขการตรวจสอบคุณภาพ
Configure validation rules for quality inspection
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QGroupBox, QLineEdit, QComboBox, QSpinBox,
                             QMessageBox, QCheckBox, QDoubleSpinBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ValidationRulesDialog(QDialog):
    """Dialog สำหรับกำหนด Validation Rules"""

    def __init__(self, validation_rules=None, parent=None):
        """
        Initialize Validation Rules Dialog

        Args:
            validation_rules: Existing validation rules dict
            parent: Parent widget
        """
        super().__init__(parent)
        self.validation_rules = validation_rules or {
            "enabled": False,
            "pass_condition": "all",
            "rules": []
        }
        self.setup_ui()
        self.load_rules()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("กำหนดเงื่อนไขการตรวจสอบคุณภาพ")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        # Title
        title_label = QLabel("เงื่อนไขการตรวจสอบคุณภาพ (Validation Rules)")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel("กำหนดเงื่อนไขการตรวจจับวัตถุเพื่อตัดสินผลการตรวจสอบ (Pass/Fail)")
        desc_label.setStyleSheet("color: #888; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # Enable validation
        self.enable_checkbox = QCheckBox("เปิดใช้งานการตรวจสอบตามเงื่อนไข")
        self.enable_checkbox.setChecked(self.validation_rules.get("enabled", False))
        self.enable_checkbox.stateChanged.connect(self.on_enable_changed)
        layout.addWidget(self.enable_checkbox)

        # Settings group
        settings_group = QGroupBox("การตั้งค่า")
        settings_layout = QVBoxLayout()

        # Pass condition
        pass_condition_layout = QHBoxLayout()
        pass_condition_layout.addWidget(QLabel("เงื่อนไขผ่าน (Pass Condition):"))

        self.pass_condition_combo = QComboBox()
        self.pass_condition_combo.addItems([
            "ทุกเงื่อนไขต้องผ่าน (All)",
            "อย่างใดอย่างหนึ่งผ่าน (Any)"
        ])
        current_condition = self.validation_rules.get("pass_condition", "all")
        self.pass_condition_combo.setCurrentIndex(0 if current_condition == "all" else 1)
        pass_condition_layout.addWidget(self.pass_condition_combo)

        # Add help text
        help_label = QLabel("(All = ทุกเงื่อนไขต้องผ่าน, Any = เงื่อนไขใดเงื่อนไขหนึ่งผ่าน)")
        help_label.setStyleSheet("color: #888; font-size: 10px;")
        pass_condition_layout.addWidget(help_label)
        pass_condition_layout.addStretch()

        settings_layout.addLayout(pass_condition_layout)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Rules table
        rules_group = QGroupBox("รายการเงื่อนไข")
        rules_layout = QVBoxLayout()

        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(4)
        self.rules_table.setHorizontalHeaderLabels([
            "ประเภท", "Class Name", "เงื่อนไข", "รายละเอียด"
        ])

        # Set column widths
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # Set selection behavior
        self.rules_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.rules_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        rules_layout.addWidget(self.rules_table)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_count_btn = QPushButton("➕ เพิ่มเงื่อนไขนับจำนวน")
        self.add_count_btn.clicked.connect(self.on_add_count_rule)
        button_layout.addWidget(self.add_count_btn)

        self.add_presence_btn = QPushButton("➕ เพิ่มเงื่อนไขมี/ไม่มี")
        self.add_presence_btn.clicked.connect(self.on_add_presence_rule)
        button_layout.addWidget(self.add_presence_btn)

        self.add_position_btn = QPushButton("➕ เพิ่มเงื่อนไขตำแหน่ง")
        self.add_position_btn.clicked.connect(self.on_add_position_rule)
        button_layout.addWidget(self.add_position_btn)

        button_layout.addStretch()

        self.edit_btn = QPushButton("✏️ แก้ไข")
        self.edit_btn.clicked.connect(self.on_edit_rule)
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️ ลบ")
        self.delete_btn.clicked.connect(self.on_delete_rule)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        rules_layout.addLayout(button_layout)

        # Enable selection changed event
        self.rules_table.itemSelectionChanged.connect(self.on_selection_changed)

        rules_group.setLayout(rules_layout)
        layout.addWidget(rules_group)

        # Dialog buttons
        dialog_button_layout = QHBoxLayout()
        dialog_button_layout.addStretch()

        save_btn = QPushButton("💾 บันทึก")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        dialog_button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("ยกเลิก")
        cancel_btn.clicked.connect(self.reject)
        dialog_button_layout.addWidget(cancel_btn)

        layout.addLayout(dialog_button_layout)

        self.setLayout(layout)

        # Update enabled state
        self.on_enable_changed()

    def on_enable_changed(self):
        """เมื่อเปลี่ยนสถานะเปิด/ปิด"""
        enabled = self.enable_checkbox.isChecked()
        self.pass_condition_combo.setEnabled(enabled)
        self.rules_table.setEnabled(enabled)
        self.add_count_btn.setEnabled(enabled)
        self.add_presence_btn.setEnabled(enabled)
        self.add_position_btn.setEnabled(enabled)
        self.edit_btn.setEnabled(enabled and len(self.rules_table.selectedItems()) > 0)
        self.delete_btn.setEnabled(enabled and len(self.rules_table.selectedItems()) > 0)

    def on_selection_changed(self):
        """เมื่อเลือก row ใน table"""
        has_selection = len(self.rules_table.selectedItems()) > 0
        enabled = self.enable_checkbox.isChecked()
        self.edit_btn.setEnabled(enabled and has_selection)
        self.delete_btn.setEnabled(enabled and has_selection)

    def load_rules(self):
        """โหลด rules ลงใน table"""
        self.rules_table.setRowCount(0)

        rules = self.validation_rules.get("rules", [])
        for rule in rules:
            self.add_rule_to_table(rule)

    def add_rule_to_table(self, rule):
        """เพิ่ม rule ลงใน table"""
        row = self.rules_table.rowCount()
        self.rules_table.insertRow(row)

        rule_type = rule.get("type", "")
        class_name = rule.get("class_name", "")

        # Type column
        type_map = {
            "count_exact": "นับจำนวน",
            "presence_check": "มี/ไม่มี",
            "position_check": "ตำแหน่ง"
        }
        type_item = QTableWidgetItem(type_map.get(rule_type, rule_type))
        type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.rules_table.setItem(row, 0, type_item)

        # Class name column
        class_item = QTableWidgetItem(class_name)
        class_item.setFlags(class_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.rules_table.setItem(row, 1, class_item)

        # Condition column
        condition_text = ""
        detail_text = ""

        if rule_type == "count_exact":
            expected = rule.get("expected", 0)
            condition_text = f"จำนวนต้องเท่ากับ"
            detail_text = f"{expected} ชิ้น"
        elif rule_type == "presence_check":
            must_exist = rule.get("must_exist", True)
            condition_text = "ต้องมี" if must_exist else "ต้องไม่มี"
            detail_text = ""
        elif rule_type == "position_check":
            zone = rule.get("zone", {})
            condition_text = "ต้องอยู่ในโซน"
            detail_text = f"X:{zone.get('x',0)}, Y:{zone.get('y',0)}, W:{zone.get('width',0)}, H:{zone.get('height',0)}"

        condition_item = QTableWidgetItem(condition_text)
        condition_item.setFlags(condition_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.rules_table.setItem(row, 2, condition_item)

        detail_item = QTableWidgetItem(detail_text)
        detail_item.setFlags(detail_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.rules_table.setItem(row, 3, detail_item)

        # Store rule data in first item
        type_item.setData(Qt.ItemDataRole.UserRole, rule)

    def on_add_count_rule(self):
        """เพิ่มเงื่อนไขนับจำนวน"""
        dialog = CountRuleDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            self.add_rule_to_table(rule)

    def on_add_presence_rule(self):
        """เพิ่มเงื่อนไขมี/ไม่มี"""
        dialog = PresenceRuleDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            self.add_rule_to_table(rule)

    def on_add_position_rule(self):
        """เพิ่มเงื่อนไขตำแหน่ง"""
        dialog = PositionRuleDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            self.add_rule_to_table(rule)

    def on_edit_rule(self):
        """แก้ไข rule"""
        row = self.rules_table.currentRow()
        if row < 0:
            return

        # Get rule data
        type_item = self.rules_table.item(row, 0)
        rule = type_item.data(Qt.ItemDataRole.UserRole)

        rule_type = rule.get("type", "")

        # Open appropriate dialog
        dialog = None
        if rule_type == "count_exact":
            dialog = CountRuleDialog(rule=rule, parent=self)
        elif rule_type == "presence_check":
            dialog = PresenceRuleDialog(rule=rule, parent=self)
        elif rule_type == "position_check":
            dialog = PositionRuleDialog(rule=rule, parent=self)

        if dialog and dialog.exec() == QDialog.DialogCode.Accepted:
            # Update rule
            updated_rule = dialog.get_rule()

            # Remove old row and add new one
            self.rules_table.removeRow(row)
            self.rules_table.insertRow(row)

            # Re-populate with updated data
            self.add_rule_to_table(updated_rule)

    def on_delete_rule(self):
        """ลบ rule"""
        row = self.rules_table.currentRow()
        if row < 0:
            return

        reply = QMessageBox.question(
            self,
            "ยืนยันการลบ",
            "ต้องการลบเงื่อนไขนี้หรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.rules_table.removeRow(row)

    def get_validation_rules(self):
        """ดึง validation rules ที่กำหนด"""
        rules = []

        for row in range(self.rules_table.rowCount()):
            type_item = self.rules_table.item(row, 0)
            rule = type_item.data(Qt.ItemDataRole.UserRole)
            rules.append(rule)

        return {
            "enabled": self.enable_checkbox.isChecked(),
            "pass_condition": "all" if self.pass_condition_combo.currentIndex() == 0 else "any",
            "rules": rules
        }


class CountRuleDialog(QDialog):
    """Dialog สำหรับกำหนดเงื่อนไขนับจำนวน"""

    def __init__(self, rule=None, parent=None):
        super().__init__(parent)
        self.rule = rule or {}
        self.setup_ui()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("เงื่อนไขนับจำนวน (Count Exact)")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Class name
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Class Name:"))
        self.class_name_edit = QLineEdit()
        self.class_name_edit.setPlaceholderText("เช่น: A1, B1, C1")
        self.class_name_edit.setText(self.rule.get("class_name", ""))
        class_layout.addWidget(self.class_name_edit)
        layout.addLayout(class_layout)

        # Expected count
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("จำนวนที่ต้องการ:"))
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(0)
        self.count_spin.setMaximum(9999)
        self.count_spin.setValue(self.rule.get("expected", 1))
        count_layout.addWidget(self.count_spin)
        count_layout.addWidget(QLabel("ชิ้น"))
        count_layout.addStretch()
        layout.addLayout(count_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("ตกลง")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("ยกเลิก")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_rule(self):
        """ดึง rule ที่กำหนด"""
        return {
            "type": "count_exact",
            "class_name": self.class_name_edit.text().strip(),
            "expected": self.count_spin.value()
        }


class PresenceRuleDialog(QDialog):
    """Dialog สำหรับกำหนดเงื่อนไขมี/ไม่มี"""

    def __init__(self, rule=None, parent=None):
        super().__init__(parent)
        self.rule = rule or {}
        self.setup_ui()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("เงื่อนไขมี/ไม่มี (Presence Check)")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Class name
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Class Name:"))
        self.class_name_edit = QLineEdit()
        self.class_name_edit.setPlaceholderText("เช่น: defect, scratch")
        self.class_name_edit.setText(self.rule.get("class_name", ""))
        class_layout.addWidget(self.class_name_edit)
        layout.addLayout(class_layout)

        # Must exist
        exist_layout = QHBoxLayout()
        exist_layout.addWidget(QLabel("เงื่อนไข:"))
        self.exist_combo = QComboBox()
        self.exist_combo.addItems(["ต้องมี (Must Exist)", "ต้องไม่มี (Must Not Exist)"])
        must_exist = self.rule.get("must_exist", True)
        self.exist_combo.setCurrentIndex(0 if must_exist else 1)
        exist_layout.addWidget(self.exist_combo)
        exist_layout.addStretch()
        layout.addLayout(exist_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("ตกลง")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("ยกเลิก")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_rule(self):
        """ดึง rule ที่กำหนด"""
        return {
            "type": "presence_check",
            "class_name": self.class_name_edit.text().strip(),
            "must_exist": self.exist_combo.currentIndex() == 0
        }


class PositionRuleDialog(QDialog):
    """Dialog สำหรับกำหนดเงื่อนไขตำแหน่ง"""

    def __init__(self, rule=None, parent=None):
        super().__init__(parent)
        self.rule = rule or {}
        self.setup_ui()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("เงื่อนไขตำแหน่ง (Position Check)")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Class name
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Class Name:"))
        self.class_name_edit = QLineEdit()
        self.class_name_edit.setPlaceholderText("เช่น: A1, B1")
        self.class_name_edit.setText(self.rule.get("class_name", ""))
        class_layout.addWidget(self.class_name_edit)
        layout.addLayout(class_layout)

        # Zone group
        zone_group = QGroupBox("โซนที่ต้องการ (Pixels)")
        zone_layout = QVBoxLayout()

        zone = self.rule.get("zone", {})

        # X
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setMinimum(0)
        self.x_spin.setMaximum(9999)
        self.x_spin.setValue(zone.get("x", 0))
        x_layout.addWidget(self.x_spin)
        x_layout.addStretch()
        zone_layout.addLayout(x_layout)

        # Y
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setMinimum(0)
        self.y_spin.setMaximum(9999)
        self.y_spin.setValue(zone.get("y", 0))
        y_layout.addWidget(self.y_spin)
        y_layout.addStretch()
        zone_layout.addLayout(y_layout)

        # Width
        w_layout = QHBoxLayout()
        w_layout.addWidget(QLabel("Width:"))
        self.w_spin = QSpinBox()
        self.w_spin.setMinimum(1)
        self.w_spin.setMaximum(9999)
        self.w_spin.setValue(zone.get("width", 100))
        w_layout.addWidget(self.w_spin)
        w_layout.addStretch()
        zone_layout.addLayout(w_layout)

        # Height
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Height:"))
        self.h_spin = QSpinBox()
        self.h_spin.setMinimum(1)
        self.h_spin.setMaximum(9999)
        self.h_spin.setValue(zone.get("height", 100))
        h_layout.addWidget(self.h_spin)
        h_layout.addStretch()
        zone_layout.addLayout(h_layout)

        zone_group.setLayout(zone_layout)
        layout.addWidget(zone_group)

        # Help text
        help_label = QLabel("หมายเหตุ: วัตถุต้องอยู่ในโซนที่กำหนด (ตรวจสอบจากจุดศูนย์กลางของ bounding box)")
        help_label.setStyleSheet("color: #888; font-size: 10px;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("ตกลง")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("ยกเลิก")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_rule(self):
        """ดึง rule ที่กำหนด"""
        return {
            "type": "position_check",
            "class_name": self.class_name_edit.text().strip(),
            "zone": {
                "x": self.x_spin.value(),
                "y": self.y_spin.value(),
                "width": self.w_spin.value(),
                "height": self.h_spin.value()
            }
        }

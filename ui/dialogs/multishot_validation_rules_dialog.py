"""
Multi-Shot Validation Rules Dialog
Dialog สำหรับตั้งค่า validation rules สำหรับ multi-shot validator
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QFormLayout,
                             QSpinBox, QComboBox, QCheckBox, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import json


class MultiShotValidationRulesDialog(QDialog):
    """Dialog สำหรับตั้งค่า Multi-Shot Validation Rules"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Multi-Shot Validation Rules")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.validation_rules = []
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("⚙ Multi-Shot Validation Rules")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Enable Group
        enable_group = QGroupBox("Validation Mode")
        enable_layout = QVBoxLayout()

        self.enable_validation = QCheckBox("เปิดใช้งาน Validation Rules")
        self.enable_validation.setToolTip("ใช้ validation rules แทน defect detection")
        self.enable_validation.stateChanged.connect(self.toggle_validation_options)
        enable_layout.addWidget(self.enable_validation)

        info_label = QLabel(
            "💡 Validation Rules ใช้สำหรับตรวจนับจำนวนชิ้นส่วนที่แน่นอน\n"
            "   เช่น แต่ละจุดต้องมี nut=10, bolt=30"
        )
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        enable_layout.addWidget(info_label)

        enable_group.setLayout(enable_layout)

        # Strategy Group
        strategy_group = QGroupBox("Validation Strategy")
        strategy_form = QFormLayout()

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "Unanimous (ทุกจุดต้อง pass)",
            "Majority Vote (>50% ต้อง pass)"
        ])
        self.strategy_combo.setCurrentIndex(0)
        self.strategy_combo.setToolTip("วิธีการรวมผลการตรวจสอบจากทุกจุด")
        strategy_form.addRow("Strategy:", self.strategy_combo)

        strategy_group.setLayout(strategy_form)

        # Rules Table Group
        rules_group = QGroupBox("📋 Validation Rules")
        rules_layout = QVBoxLayout()

        # Info
        rules_info = QLabel(
            "กำหนดจำนวนชิ้นส่วนที่ต้องตรวจพบในแต่ละจุด (shot)"
        )
        rules_info.setStyleSheet("color: #666; font-size: 11px;")
        rules_layout.addWidget(rules_info)

        # Table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels([
            "Rule Type", "Class Name", "Expected", "Tolerance/Range", "Actions"
        ])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.rules_table.setAlternatingRowColors(True)
        rules_layout.addWidget(self.rules_table)

        # Rule buttons
        rule_btn_layout = QHBoxLayout()

        add_exact_btn = QPushButton("➕ Add Count Exact")
        add_exact_btn.clicked.connect(self.add_count_exact_rule)
        add_exact_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        add_range_btn = QPushButton("➕ Add Count Range")
        add_range_btn.clicked.connect(self.add_count_range_rule)
        add_range_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)

        rule_btn_layout.addWidget(add_exact_btn)
        rule_btn_layout.addWidget(add_range_btn)
        rule_btn_layout.addStretch()

        rules_layout.addLayout(rule_btn_layout)
        rules_group.setLayout(rules_layout)

        # Main buttons
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

        # Add all groups
        layout.addWidget(enable_group)
        layout.addWidget(strategy_group)
        layout.addWidget(rules_group)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def toggle_validation_options(self):
        """เปิด/ปิด options ตาม checkbox"""
        enabled = self.enable_validation.isChecked()
        self.strategy_combo.setEnabled(enabled)
        self.rules_table.setEnabled(enabled)

    def add_count_exact_rule(self):
        """เพิ่ม count exact rule"""
        row = self.rules_table.rowCount()
        self.rules_table.insertRow(row)

        # Rule type
        type_item = QTableWidgetItem("count_exact")
        type_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.rules_table.setItem(row, 0, type_item)

        # Class name (editable)
        class_item = QTableWidgetItem("class_name")
        self.rules_table.setItem(row, 1, class_item)

        # Expected (editable)
        expected_item = QTableWidgetItem("10")
        self.rules_table.setItem(row, 2, expected_item)

        # Tolerance (editable)
        tolerance_item = QTableWidgetItem("0")
        self.rules_table.setItem(row, 3, tolerance_item)

        # Delete button
        delete_btn = QPushButton("🗑 ลบ")
        delete_btn.clicked.connect(lambda: self.delete_rule(row))
        delete_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.rules_table.setCellWidget(row, 4, delete_btn)

    def add_count_range_rule(self):
        """เพิ่ม count range rule"""
        row = self.rules_table.rowCount()
        self.rules_table.insertRow(row)

        # Rule type
        type_item = QTableWidgetItem("count_range")
        type_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.rules_table.setItem(row, 0, type_item)

        # Class name (editable)
        class_item = QTableWidgetItem("class_name")
        self.rules_table.setItem(row, 1, class_item)

        # Min (editable)
        min_item = QTableWidgetItem("5")
        self.rules_table.setItem(row, 2, min_item)

        # Max (editable)
        max_item = QTableWidgetItem("15")
        self.rules_table.setItem(row, 3, max_item)

        # Delete button
        delete_btn = QPushButton("🗑 ลบ")
        delete_btn.clicked.connect(lambda: self.delete_rule(row))
        delete_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.rules_table.setCellWidget(row, 4, delete_btn)

    def delete_rule(self, row):
        """ลบ rule"""
        self.rules_table.removeRow(row)

    def load_settings(self):
        """โหลด settings"""
        inspection_settings = self.settings.get('inspection', {})

        # Load validation settings
        enabled = inspection_settings.get('multishot_validation_enabled', False)
        strategy = inspection_settings.get('multishot_validation_strategy', 'unanimous')
        rules = inspection_settings.get('multishot_validation_rules', [])

        self.enable_validation.setChecked(enabled)

        # Map strategy
        strategy_map = {
            'unanimous': 0,
            'majority_vote': 1
        }
        self.strategy_combo.setCurrentIndex(strategy_map.get(strategy, 0))

        # Load rules into table
        self.rules_table.setRowCount(0)
        for rule in rules:
            rule_type = rule.get('type')
            if rule_type == 'count_exact':
                row = self.rules_table.rowCount()
                self.rules_table.insertRow(row)

                self.rules_table.setItem(row, 0, QTableWidgetItem("count_exact"))
                self.rules_table.setItem(row, 1, QTableWidgetItem(rule.get('class_name', '')))
                self.rules_table.setItem(row, 2, QTableWidgetItem(str(rule.get('expected', 0))))
                self.rules_table.setItem(row, 3, QTableWidgetItem(str(rule.get('tolerance', 0))))

                delete_btn = QPushButton("🗑 ลบ")
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_rule(r))
                self.rules_table.setCellWidget(row, 4, delete_btn)

            elif rule_type == 'count_range':
                row = self.rules_table.rowCount()
                self.rules_table.insertRow(row)

                self.rules_table.setItem(row, 0, QTableWidgetItem("count_range"))
                self.rules_table.setItem(row, 1, QTableWidgetItem(rule.get('class_name', '')))
                self.rules_table.setItem(row, 2, QTableWidgetItem(str(rule.get('min', 0))))
                self.rules_table.setItem(row, 3, QTableWidgetItem(str(rule.get('max', 999))))

                delete_btn = QPushButton("🗑 ลบ")
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_rule(r))
                self.rules_table.setCellWidget(row, 4, delete_btn)

        # Toggle options
        self.toggle_validation_options()

    def save_settings(self):
        """บันทึก settings"""
        # Map combo index to strategy
        strategy_map = {
            0: 'unanimous',
            1: 'majority_vote'
        }

        # Collect rules from table
        rules = []
        for row in range(self.rules_table.rowCount()):
            rule_type = self.rules_table.item(row, 0).text()
            class_name = self.rules_table.item(row, 1).text()

            if rule_type == 'count_exact':
                try:
                    expected = int(self.rules_table.item(row, 2).text())
                    tolerance = int(self.rules_table.item(row, 3).text())

                    rules.append({
                        'type': 'count_exact',
                        'class_name': class_name,
                        'expected': expected,
                        'tolerance': tolerance
                    })
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "ข้อผิดพลาด",
                        f"Rule row {row+1}: Expected และ Tolerance ต้องเป็นตัวเลข"
                    )
                    return

            elif rule_type == 'count_range':
                try:
                    min_val = int(self.rules_table.item(row, 2).text())
                    max_val = int(self.rules_table.item(row, 3).text())

                    if min_val > max_val:
                        QMessageBox.warning(
                            self,
                            "ข้อผิดพลาด",
                            f"Rule row {row+1}: Min ต้องน้อยกว่าหรือเท่ากับ Max"
                        )
                        return

                    rules.append({
                        'type': 'count_range',
                        'class_name': class_name,
                        'min': min_val,
                        'max': max_val
                    })
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "ข้อผิดพลาด",
                        f"Rule row {row+1}: Min และ Max ต้องเป็นตัวเลข"
                    )
                    return

        # Save settings
        self.settings.set('inspection.multishot_validation_enabled', self.enable_validation.isChecked())
        self.settings.set('inspection.multishot_validation_strategy', strategy_map[self.strategy_combo.currentIndex()])
        self.settings.set('inspection.multishot_validation_rules', rules)

        self.settings.save()

        QMessageBox.information(
            self,
            "สำเร็จ",
            f"บันทึกการตั้งค่า Validation Rules เรียบร้อย\n"
            f"จำนวน Rules: {len(rules)}"
        )

        self.accept()

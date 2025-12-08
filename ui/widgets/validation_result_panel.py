"""
Validation Result Panel - แสดงผลการตรวจสอบตามเงื่อนไข
Display validation results for quality inspection
"""
from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                              QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class ValidationResultPanel(QGroupBox):
    """แสดงผลการตรวจสอบตามเงื่อนไข"""

    def __init__(self, parent=None):
        super().__init__("การตรวจสอบตามเงื่อนไข (Validation)", parent)
        self.setup_ui()

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()

        # Status label
        self.status_label = QLabel("ยังไม่มีเงื่อนไขการตรวจสอบ")
        self.status_label.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(self.status_label)

        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels([
            "เงื่อนไข", "ผลลัพธ์", "สถานะ"
        ])

        # Set column widths
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Hide table initially
        self.rules_table.setVisible(False)
        self.rules_table.setMaximumHeight(200)

        layout.addWidget(self.rules_table)

        self.setLayout(layout)

    def update_validation_result(self, validation_result):
        """
        อัพเดทผลการตรวจสอบ

        Args:
            validation_result: Validation result dictionary from inspection_engine
        """
        if validation_result is None or not validation_result.get('enabled', False):
            # No validation or disabled
            self.status_label.setText("ยังไม่มีเงื่อนไขการตรวจสอบ")
            self.status_label.setStyleSheet("font-size: 12px; color: #888;")
            self.rules_table.setVisible(False)
            return

        # Get validation info
        overall_pass = validation_result.get('pass', False)
        pass_condition = validation_result.get('pass_condition', 'all')
        rules_results = validation_result.get('rules_results', [])

        # Update status label
        pass_text = "ทุกเงื่อนไข" if pass_condition == "all" else "เงื่อนไขใดเงื่อนไขหนึ่ง"
        if overall_pass:
            self.status_label.setText(f"✓ ผ่านการตรวจสอบ ({pass_text})")
            self.status_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #4CAF50;"
            )
        else:
            self.status_label.setText(f"✗ ไม่ผ่านการตรวจสอบ ({pass_text})")
            self.status_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #f44336;"
            )

        # Update rules table
        self.rules_table.setRowCount(len(rules_results))
        self.rules_table.setVisible(len(rules_results) > 0)

        for row, rule_result in enumerate(rules_results):
            rule_type = rule_result.get('type', '')
            class_name = rule_result.get('class_name', '')
            is_pass = rule_result.get('pass', False)
            message = rule_result.get('message', '')

            # Column 0: เงื่อนไข
            condition_text = ""
            if rule_type == 'count_exact':
                expected = rule_result.get('expected', 0)
                condition_text = f"{class_name}: ต้องเท่ากับ {expected} ชิ้น"
            elif rule_type == 'presence_check':
                must_exist = rule_result.get('must_exist', True)
                condition_text = f"{class_name}: {'ต้องมี' if must_exist else 'ต้องไม่มี'}"
            elif rule_type == 'position_check':
                zone = rule_result.get('zone', {})
                condition_text = f"{class_name}: ต้องอยู่ในโซน (X:{zone.get('x')}, Y:{zone.get('y')})"

            condition_item = QTableWidgetItem(condition_text)
            condition_item.setFlags(condition_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.rules_table.setItem(row, 0, condition_item)

            # Column 1: ผลลัพธ์
            result_text = message
            result_item = QTableWidgetItem(result_text)
            result_item.setFlags(result_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.rules_table.setItem(row, 1, result_item)

            # Column 2: สถานะ
            status_text = "✓ ผ่าน" if is_pass else "✗ ไม่ผ่าน"
            status_item = QTableWidgetItem(status_text)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Set color
            if is_pass:
                status_item.setForeground(QColor(76, 175, 80))  # Green
                status_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            else:
                status_item.setForeground(QColor(244, 67, 54))  # Red
                status_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))

            self.rules_table.setItem(row, 2, status_item)

    def clear(self):
        """ล้างผลการตรวจสอบ"""
        self.status_label.setText("ยังไม่มีเงื่อนไขการตรวจสอบ")
        self.status_label.setStyleSheet("font-size: 12px; color: #888;")
        self.rules_table.setRowCount(0)
        self.rules_table.setVisible(False)

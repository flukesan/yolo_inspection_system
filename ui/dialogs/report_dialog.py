"""
Report Dialog - สร้างรายงาน
Dialog for generating reports
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox, QFormLayout,
                             QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate


class ReportDialog(QDialog):
    """Dialog สำหรับสร้างรายงาน"""

    def __init__(self, report_generator, parent=None):
        super().__init__(parent)
        self.report_generator = report_generator
        self.setup_ui()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("สร้างรายงาน")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Report Type
        type_group = QGroupBox("ประเภทรายงาน")
        type_layout = QFormLayout()

        self.report_type = QComboBox()
        self.report_type.addItems(["รายงานวันนี้", "รายงานสัปดาห์นี้", "รายงานเดือนนี้", "กำหนดเอง"])
        self.report_type.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addRow("ประเภท:", self.report_type)

        type_group.setLayout(type_layout)

        # Date Range (for custom)
        self.date_group = QGroupBox("ช่วงวันที่")
        date_layout = QFormLayout()

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        date_layout.addRow("จาก:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addRow("ถึง:", self.end_date)

        self.date_group.setLayout(date_layout)
        self.date_group.setEnabled(False)

        # Buttons
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("สร้างรายงาน")
        self.generate_btn.clicked.connect(self.generate_report)

        self.cancel_btn = QPushButton("ยกเลิก")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.cancel_btn)

        # Add all to main layout
        layout.addWidget(type_group)
        layout.addWidget(self.date_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_type_changed(self, index):
        """จัดการเมื่อเปลี่ยนประเภทรายงาน"""
        self.date_group.setEnabled(index == 3)  # Enable for "กำหนดเอง"

    def generate_report(self):
        """สร้างรายงาน"""
        report_type = self.report_type.currentText()

        try:
            filepath = ""

            if report_type == "รายงานวันนี้":
                filepath = self.report_generator.generate_daily_report()
            elif report_type == "รายงานสัปดาห์นี้":
                filepath = self.report_generator.generate_weekly_report()
            elif report_type == "รายงานเดือนนี้":
                filepath = self.report_generator.generate_monthly_report()
            elif report_type == "กำหนดเอง":
                start = self.start_date.date().toString("yyyy-MM-dd")
                end = self.end_date.date().toString("yyyy-MM-dd")
                filepath = self.report_generator.generate_excel_report(start, end)

            if filepath:
                QMessageBox.information(
                    self,
                    "สำเร็จ",
                    f"สร้างรายงานสำเร็จ:\n{filepath}"
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "เกิดข้อผิดพลาด",
                    "ไม่สามารถสร้างรายงานได้"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "ข้อผิดพลาด",
                f"เกิดข้อผิดพลาด: {str(e)}"
            )

"""
Statistics Panel Widget - แสดงสถิติ
Display inspection statistics and metrics
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class StatisticsPanel(QWidget):
    """Panel แสดงสถิติการตรวจสอบ"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

        # Timer for updating statistics
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second

        self.inspection_engine = None

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()

        # Overall Statistics Group
        overall_group = QGroupBox("สถิติรวม")
        overall_layout = QVBoxLayout()

        # Total inspections
        self.total_label = self._create_stat_label("ตรวจสอบทั้งหมด:", "0")
        overall_layout.addLayout(self.total_label)

        # OK count
        self.ok_label = self._create_stat_label("ผ่าน (OK):", "0", "#4CAF50")
        overall_layout.addLayout(self.ok_label)

        # NG count
        self.ng_label = self._create_stat_label("ไม่ผ่าน (NG):", "0", "#f44336")
        overall_layout.addLayout(self.ng_label)

        # Defect rate
        self.defect_rate_label = self._create_stat_label("อัตราของเสีย:", "0.00%", "#FF9800")
        overall_layout.addLayout(self.defect_rate_label)

        # Throughput
        self.throughput_label = self._create_stat_label("ความเร็ว:", "0 ชิ้น/นาที")
        overall_layout.addLayout(self.throughput_label)

        overall_group.setLayout(overall_layout)

        # Defect Details Group
        defect_group = QGroupBox("รายละเอียด Defect")
        defect_layout = QVBoxLayout()

        self.defect_table = QTableWidget()
        self.defect_table.setColumnCount(2)
        self.defect_table.setHorizontalHeaderLabels(["ประเภท Defect", "จำนวน"])
        self.defect_table.horizontalHeader().setStretchLastSection(True)
        self.defect_table.setAlternatingRowColors(True)
        self.defect_table.setMaximumHeight(200)

        defect_layout.addWidget(self.defect_table)
        defect_group.setLayout(defect_layout)

        # Add groups to main layout
        layout.addWidget(overall_group)
        layout.addWidget(defect_group)
        layout.addStretch()

        self.setLayout(layout)

    def _create_stat_label(self, title: str, value: str, color: str = "#ffffff"):
        """สร้าง label สำหรับแสดงสถิติ"""
        layout = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px;")

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        value_label.setAlignment(Qt.AlignRight)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        # Store value label in dictionary for updating
        if not hasattr(self, '_value_labels'):
            self._value_labels = {}
        self._value_labels[title] = value_label

        return layout

    def set_inspection_engine(self, engine):
        """ตั้งค่า Inspection Engine"""
        self.inspection_engine = engine

    def update_display(self):
        """อัพเดทการแสดงผล"""
        if self.inspection_engine is None:
            return

        try:
            stats = self.inspection_engine.get_statistics()

            # Update overall statistics using dictionary
            if hasattr(self, '_value_labels'):
                self._value_labels["ตรวจสอบทั้งหมด:"].setText(str(stats['total_inspections']))
                self._value_labels["ผ่าน (OK):"].setText(str(stats['total_ok']))
                self._value_labels["ไม่ผ่าน (NG):"].setText(str(stats['total_defects']))
                self._value_labels["อัตราของเสีย:"].setText(f"{stats['defect_rate']:.2f}%")
                self._value_labels["ความเร็ว:"].setText(f"{stats['throughput_per_min']:.1f} ชิ้น/นาที")

            # Update defect table
            self.update_defect_table(stats['defect_counts'])

        except Exception as e:
            print(f"✗ Error updating statistics display: {e}")

    def update_defect_table(self, defect_counts: dict):
        """อัพเดทตาราง defect"""
        try:
            self.defect_table.setRowCount(len(defect_counts))

            for i, (class_name, count) in enumerate(defect_counts.items()):
                # Defect class name
                class_item = QTableWidgetItem(class_name)
                class_item.setFlags(Qt.ItemIsEnabled)

                # Count
                count_item = QTableWidgetItem(str(count))
                count_item.setFlags(Qt.ItemIsEnabled)
                count_item.setTextAlignment(Qt.AlignCenter)

                self.defect_table.setItem(i, 0, class_item)
                self.defect_table.setItem(i, 1, count_item)

        except Exception as e:
            print(f"✗ Error updating defect table: {e}")

    def reset(self):
        """รีเซ็ตสถิติ"""
        if hasattr(self, '_value_labels'):
            self._value_labels["ตรวจสอบทั้งหมด:"].setText("0")
            self._value_labels["ผ่าน (OK):"].setText("0")
            self._value_labels["ไม่ผ่าน (NG):"].setText("0")
            self._value_labels["อัตราของเสีย:"].setText("0.00%")
            self._value_labels["ความเร็ว:"].setText("0 ชิ้น/นาที")
        self.defect_table.setRowCount(0)

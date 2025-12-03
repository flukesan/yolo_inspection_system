"""
Alert Panel Widget - แจ้งเตือน
Display alerts and notifications
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QGroupBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from datetime import datetime


class AlertPanel(QWidget):
    """Panel แสดงการแจ้งเตือนและ log"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.max_lines = 1000
        self.auto_scroll = True
        self.setup_ui()

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()

        # Alert/Log Group
        log_group = QGroupBox("Log และการแจ้งเตือน")
        log_layout = QVBoxLayout()

        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #444;
            }
        """)

        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)

        layout.addWidget(log_group)
        self.setLayout(layout)

    def add_log(self, message: str, level: str = "INFO"):
        """
        เพิ่ม log

        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color based on level
        colors = {
            "INFO": "#d4d4d4",
            "WARNING": "#FFA500",
            "ERROR": "#FF0000",
            "SUCCESS": "#00FF00",
            "DEFECT": "#FF6B6B"
        }
        color = colors.get(level, "#d4d4d4")

        # Icons
        icons = {
            "INFO": "ℹ",
            "WARNING": "⚠",
            "ERROR": "✗",
            "SUCCESS": "✓",
            "DEFECT": "🔴"
        }
        icon = icons.get(level, "•")

        # Format message
        formatted_message = f'<span style="color: #888;">[{timestamp}]</span> <span style="color: {color};">{icon} {message}</span>'

        # Add to log
        self.log_text.append(formatted_message)

        # Auto scroll to bottom
        if self.auto_scroll:
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)

        # Limit number of lines
        self._limit_lines()

    def add_info(self, message: str):
        """เพิ่ม info log"""
        self.add_log(message, "INFO")

    def add_warning(self, message: str):
        """เพิ่ม warning log"""
        self.add_log(message, "WARNING")

    def add_error(self, message: str):
        """เพิ่ม error log"""
        self.add_log(message, "ERROR")

    def add_success(self, message: str):
        """เพิ่ม success log"""
        self.add_log(message, "SUCCESS")

    def add_defect_alert(self, defect_info: str):
        """เพิ่มการแจ้งเตือน defect"""
        self.add_log(f"พบ DEFECT: {defect_info}", "DEFECT")

    def clear(self):
        """ล้าง log"""
        self.log_text.clear()

    def set_auto_scroll(self, enabled: bool):
        """ตั้งค่า auto scroll"""
        self.auto_scroll = enabled

    def _limit_lines(self):
        """จำกัดจำนวนบรรทัด"""
        # Get current text
        text = self.log_text.toPlainText()
        lines = text.split('\n')

        # Keep only last N lines
        if len(lines) > self.max_lines:
            lines = lines[-self.max_lines:]
            self.log_text.setPlainText('\n'.join(lines))

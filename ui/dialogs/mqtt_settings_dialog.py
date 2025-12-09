"""
MQTT Settings Dialog - ตั้งค่าการเชื่อมต่อ MQTT
Configure MQTT connection settings for DeviceWise
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QSpinBox, QGroupBox,
                             QComboBox, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MQTTSettingsDialog(QDialog):
    """Dialog สำหรับตั้งค่า MQTT Connection"""

    def __init__(self, settings, mqtt_client=None, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.mqtt_client = mqtt_client
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("MQTT Connection Settings")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Title
        title_label = QLabel("MQTT Connection Settings")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel("ตั้งค่าการเชื่อมต่อ MQTT สำหรับส่งข้อมูลไปยัง DeviceWise")
        desc_label.setStyleSheet("color: #888; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # Enable MQTT
        self.enable_mqtt_checkbox = QCheckBox("เปิดใช้งาน MQTT Connection")
        self.enable_mqtt_checkbox.stateChanged.connect(self.on_enable_changed)
        layout.addWidget(self.enable_mqtt_checkbox)

        # Configuration Group
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()

        # Client ID Type
        client_id_layout = QHBoxLayout()
        client_id_layout.addWidget(QLabel("Client ID Type:"))
        self.client_id_type_combo = QComboBox()
        self.client_id_type_combo.addItems(["MAC Address", "Custom ID"])
        client_id_layout.addWidget(self.client_id_type_combo)
        client_id_layout.addStretch()
        config_layout.addLayout(client_id_layout)

        # Custom Client ID (hidden by default)
        self.custom_id_layout = QHBoxLayout()
        self.custom_id_layout.addWidget(QLabel("Custom Client ID:"))
        self.custom_id_edit = QLineEdit()
        self.custom_id_edit.setPlaceholderText("Enter custom client ID")
        self.custom_id_layout.addWidget(self.custom_id_edit)
        config_layout.addLayout(self.custom_id_layout)
        self.custom_id_edit.setVisible(False)
        self.custom_id_layout.itemAt(0).widget().setVisible(False)

        # Connection Type
        conn_type_layout = QHBoxLayout()
        conn_type_layout.addWidget(QLabel("Connection Type:"))
        self.conn_type_combo = QComboBox()
        self.conn_type_combo.addItems(["MQTT", "MQTT over SSL/TLS"])
        conn_type_layout.addWidget(self.conn_type_combo)
        conn_type_layout.addStretch()
        config_layout.addLayout(conn_type_layout)

        # Broker Host
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Broker Host:"))
        self.broker_host_edit = QLineEdit()
        self.broker_host_edit.setPlaceholderText("localhost or IP address")
        host_layout.addWidget(self.broker_host_edit)
        config_layout.addLayout(host_layout)

        # Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setMinimum(1)
        self.port_spin.setMaximum(65535)
        self.port_spin.setValue(1883)
        port_layout.addWidget(self.port_spin)
        port_layout.addStretch()
        config_layout.addLayout(port_layout)

        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (seconds):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(1)
        self.timeout_spin.setMaximum(60)
        self.timeout_spin.setValue(3)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        config_layout.addLayout(timeout_layout)

        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Optional")
        username_layout.addWidget(self.username_edit)
        config_layout.addLayout(username_layout)

        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Optional")
        password_layout.addWidget(self.password_edit)
        config_layout.addLayout(password_layout)

        # Heartbeat Interval
        heartbeat_layout = QHBoxLayout()
        heartbeat_layout.addWidget(QLabel("Heartbeat Interval (sec):"))
        self.heartbeat_spin = QSpinBox()
        self.heartbeat_spin.setMinimum(10)
        self.heartbeat_spin.setMaximum(600)
        self.heartbeat_spin.setValue(60)
        heartbeat_layout.addWidget(self.heartbeat_spin)
        heartbeat_layout.addStretch()
        config_layout.addLayout(heartbeat_layout)

        # Topic
        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("MQTT Topic:"))
        self.topic_edit = QLineEdit()
        self.topic_edit.setPlaceholderText("yolo/inspection")
        self.topic_edit.setText("yolo/inspection")
        topic_layout.addWidget(self.topic_edit)
        config_layout.addLayout(topic_layout)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Connection Status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Test Connection Button
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("🔌 Test Connection")
        self.test_btn.clicked.connect(self.on_test_connection)
        test_layout.addWidget(self.test_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)

        # Dialog Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.on_save)
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
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect signals
        self.client_id_type_combo.currentTextChanged.connect(self.on_client_id_type_changed)

    def on_enable_changed(self):
        """เมื่อเปลี่ยนสถานะ enable/disable"""
        enabled = self.enable_mqtt_checkbox.isChecked()
        # Enable/disable all controls
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item.widget() and item.widget() != self.enable_mqtt_checkbox:
                item.widget().setEnabled(enabled)

    def on_client_id_type_changed(self, text):
        """เมื่อเปลี่ยนประเภท Client ID"""
        is_custom = (text == "Custom ID")
        self.custom_id_edit.setVisible(is_custom)
        self.custom_id_layout.itemAt(0).widget().setVisible(is_custom)

    def load_settings(self):
        """โหลดการตั้งค่าจาก settings"""
        mqtt_settings = self.settings.get("mqtt", {})

        self.enable_mqtt_checkbox.setChecked(mqtt_settings.get("enabled", False))
        self.broker_host_edit.setText(mqtt_settings.get("broker_host", ""))
        self.port_spin.setValue(mqtt_settings.get("port", 1883))
        self.timeout_spin.setValue(mqtt_settings.get("timeout", 3))
        self.username_edit.setText(mqtt_settings.get("username", ""))
        self.password_edit.setText(mqtt_settings.get("password", ""))
        self.heartbeat_spin.setValue(mqtt_settings.get("heartbeat_interval", 60))
        self.topic_edit.setText(mqtt_settings.get("topic", "yolo/inspection"))

        client_id_type = mqtt_settings.get("client_id_type", "mac")
        if client_id_type == "custom":
            self.client_id_type_combo.setCurrentText("Custom ID")
            self.custom_id_edit.setText(mqtt_settings.get("client_id", ""))
        else:
            self.client_id_type_combo.setCurrentText("MAC Address")

        # Update status
        if self.mqtt_client and self.mqtt_client.is_connected():
            self.status_label.setText("Status: Connected ✓")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.status_label.setText("Status: Disconnected")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")

        self.on_enable_changed()

    def on_test_connection(self):
        """ทดสอบการเชื่อมต่อ MQTT"""
        broker_host = self.broker_host_edit.text().strip()
        if not broker_host:
            QMessageBox.warning(self, "Warning", "Please enter Broker Host")
            return

        try:
            # Import MQTT client
            from core.mqtt_client import MQTTClient

            # Create test client
            client_id = None
            if self.client_id_type_combo.currentText() == "Custom ID":
                client_id = self.custom_id_edit.text().strip()

            test_client = MQTTClient(
                broker_host=broker_host,
                port=self.port_spin.value(),
                client_id=client_id,
                username=self.username_edit.text().strip() or None,
                password=self.password_edit.text().strip() or None,
                timeout=self.timeout_spin.value(),
                heartbeat_interval=self.heartbeat_spin.value()
            )

            # Try to connect
            if test_client.connect():
                self.status_label.setText("Status: Connected ✓")
                self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                QMessageBox.information(self, "Success", "MQTT Connection successful!")
                test_client.disconnect()
            else:
                self.status_label.setText("Status: Connection Failed")
                self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
                QMessageBox.critical(self, "Error", "Failed to connect to MQTT Broker")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection test failed:\n{str(e)}")

    def on_save(self):
        """บันทึกการตั้งค่า"""
        # Validate
        if self.enable_mqtt_checkbox.isChecked():
            if not self.broker_host_edit.text().strip():
                QMessageBox.warning(self, "Warning", "Please enter Broker Host")
                return

        # Prepare settings
        client_id_type = "custom" if self.client_id_type_combo.currentText() == "Custom ID" else "mac"
        client_id = self.custom_id_edit.text().strip() if client_id_type == "custom" else None

        mqtt_settings = {
            "enabled": self.enable_mqtt_checkbox.isChecked(),
            "broker_host": self.broker_host_edit.text().strip(),
            "port": self.port_spin.value(),
            "timeout": self.timeout_spin.value(),
            "username": self.username_edit.text().strip(),
            "password": self.password_edit.text().strip(),
            "heartbeat_interval": self.heartbeat_spin.value(),
            "topic": self.topic_edit.text().strip(),
            "client_id_type": client_id_type,
            "client_id": client_id
        }

        # Save to settings
        self.settings.set("mqtt", mqtt_settings)
        self.settings.save()

        QMessageBox.information(self, "Success", "MQTT settings saved successfully!")
        self.accept()

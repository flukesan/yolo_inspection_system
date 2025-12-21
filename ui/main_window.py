"""
Main Window - หน้าต่างหลัก
Main application window for YOLO Inspection System
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QMenuBar, QFileDialog, QMessageBox,
                             QStatusBar, QLabel)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction
import os
import cv2
import numpy as np
from datetime import datetime

from .widgets.camera_view import CameraView
from .widgets.control_panel import ControlPanel
from .widgets.statistics_panel import StatisticsPanel
from .widgets.alert_panel import AlertPanel
from .widgets.validation_result_panel import ValidationResultPanel
from .dialogs.camera_profiles_dialog import CameraProfilesDialog
from .dialogs.model_profiles_dialog import ModelProfilesDialog
from .dialogs.snapshot_training_settings_dialog import SnapshotTrainingSettingsDialog
from .dialogs.mqtt_settings_dialog import MQTTSettingsDialog
from .dialogs.multishot_capture_dialog import MultiShotCaptureDialog
from .dialogs.multishot_inspection_settings_dialog import MultiShotInspectionSettingsDialog
from .dialogs.multishot_result_dialog import MultiShotResultDialog


class MainWindow(QMainWindow):
    """หน้าต่างหลักของโปรแกรม"""

    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()

        # Timer for inspection loop
        self.inspection_timer = QTimer()
        self.inspection_timer.timeout.connect(self.run_inspection)

    def setup_ui(self):
        """สร้าง UI"""
        self.setWindowTitle("YOLO Inspection System - ระบบตรวจสอบคุณภาพชิ้นงาน")
        self.setMinimumSize(1400, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()

        # Left side - Camera View and Alert Panel
        left_layout = QVBoxLayout()

        self.camera_view = CameraView()
        self.alert_panel = AlertPanel()

        left_layout.addWidget(self.camera_view, stretch=3)
        left_layout.addWidget(self.alert_panel, stretch=1)

        # Right side - Control and Statistics Panels
        right_layout = QVBoxLayout()

        self.control_panel = ControlPanel()
        self.statistics_panel = StatisticsPanel()
        self.validation_result_panel = ValidationResultPanel()

        right_layout.addWidget(self.control_panel, stretch=1)
        right_layout.addWidget(self.statistics_panel, stretch=1)
        right_layout.addWidget(self.validation_result_panel, stretch=1)

        # Add to main layout
        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(right_layout, stretch=1)

        central_widget.setLayout(main_layout)

        # Apply dark theme
        self.apply_dark_theme()

        # Log startup
        self.alert_panel.add_info("ระบบเริ่มต้นแล้ว")

    def setup_menu(self):
        """สร้าง menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&ไฟล์")

        open_action = QAction("เปิดโมเดล...", self)
        open_action.triggered.connect(self.on_load_model)
        file_menu.addAction(open_action)

        model_profiles_action = QAction("📦 จัดการ Model Profiles...", self)
        model_profiles_action.triggered.connect(self.on_model_profiles)
        file_menu.addAction(model_profiles_action)

        file_menu.addSeparator()

        exit_action = QAction("ออก", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Camera menu
        camera_menu = menubar.addMenu("&กล้อง")

        connect_camera_action = QAction("เชื่อมต่อกล้อง...", self)
        connect_camera_action.triggered.connect(self.on_connect_camera)
        camera_menu.addAction(connect_camera_action)

        camera_menu.addSeparator()

        camera_profiles_action = QAction("📹 จัดการ Camera Profiles...", self)
        camera_profiles_action.triggered.connect(self.on_camera_profiles)
        camera_menu.addAction(camera_profiles_action)

        # Tools menu
        tools_menu = menubar.addMenu("เครื่อง&มือ")

        settings_action = QAction("ตั้งค่า...", self)
        settings_action.triggered.connect(self.on_settings)
        tools_menu.addAction(settings_action)

        snapshot_training_settings_action = QAction("📚 ตั้งค่า Snapshot Training...", self)
        snapshot_training_settings_action.triggered.connect(self.on_snapshot_training_settings)
        tools_menu.addAction(snapshot_training_settings_action)

        mqtt_settings_action = QAction("📡 ตั้งค่า MQTT Connection...", self)
        mqtt_settings_action.triggered.connect(self.on_mqtt_settings)
        tools_menu.addAction(mqtt_settings_action)

        tools_menu.addSeparator()

        # Multi-Shot submenu
        multishot_menu = tools_menu.addMenu("🎬 Multi-Shot")

        multishot_capture_action = QAction("📸 Multi-Shot Capture (Training)", self)
        multishot_capture_action.setToolTip("ถ่ายภาพหลายมุมสำหรับการเทรน")
        multishot_capture_action.triggered.connect(self.on_multishot_capture)
        multishot_menu.addAction(multishot_capture_action)

        multishot_inspection_action = QAction("🔍 Multi-Shot Inspection", self)
        multishot_inspection_action.setToolTip("ตรวจสอบชิ้นงานด้วยหลายมุม")
        multishot_inspection_action.triggered.connect(self.on_multishot_inspection)
        multishot_menu.addAction(multishot_inspection_action)

        multishot_menu.addSeparator()

        multishot_settings_action = QAction("⚙ Multi-Shot Settings", self)
        multishot_settings_action.triggered.connect(self.on_multishot_settings)
        multishot_menu.addAction(multishot_settings_action)

        tools_menu.addSeparator()

        report_action = QAction("สร้างรายงาน...", self)
        report_action.triggered.connect(self.on_generate_report)
        tools_menu.addAction(report_action)

        # Help menu
        help_menu = menubar.addMenu("&ช่วยเหลือ")

        about_action = QAction("เกี่ยวกับ...", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def setup_statusbar(self):
        """สร้าง status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Status labels
        self.camera_status = QLabel("กล้อง: ไม่ได้เชื่อมต่อ")
        self.model_status = QLabel("โมเดล: ไม่ได้โหลด")
        self.fps_status = QLabel("FPS: 0")

        self.statusbar.addPermanentWidget(self.camera_status)
        self.statusbar.addPermanentWidget(self.model_status)
        self.statusbar.addPermanentWidget(self.fps_status)

        self.statusbar.showMessage("พร้อมใช้งาน")

    def setup_connections(self):
        """ตั้งค่า signal/slot connections"""
        # Control panel signals
        self.control_panel.start_clicked.connect(self.on_start_inspection)
        self.control_panel.stop_clicked.connect(self.on_stop_inspection)
        self.control_panel.pause_clicked.connect(self.on_pause_inspection)
        self.control_panel.snapshot_clicked.connect(self.on_snapshot_inspection)
        self.control_panel.camera_connect_clicked.connect(self.on_connect_camera)
        self.control_panel.load_model_clicked.connect(self.on_load_model)
        self.control_panel.settings_clicked.connect(self.on_settings)
        self.control_panel.report_clicked.connect(self.on_generate_report)

    def set_app_controller(self, controller):
        """ตั้งค่า application controller"""
        self.app_controller = controller

        # Set components
        if hasattr(controller, 'camera_manager'):
            self.camera_view.set_camera_manager(controller.camera_manager)

        if hasattr(controller, 'inspection_engine'):
            self.statistics_panel.set_inspection_engine(controller.inspection_engine)

    def on_connect_camera(self):
        """จัดการการเชื่อมต่อ/ตัดการเชื่อมต่อกล้อง"""
        if not self.app_controller:
            return

        # Check current connection state from control panel
        if self.control_panel.camera_connected:
            # Currently connected - disconnect
            self.disconnect_camera()
        else:
            # Currently disconnected - connect
            success = self.app_controller.connect_camera()
            if success:
                self.camera_view.start(30)
                info = self.app_controller.camera_manager.get_info()
                info_str = f"({info['width']}x{info['height']})"
                self.control_panel.update_camera_status(True, info_str)
                self.camera_status.setText(f"กล้อง: เชื่อมต่อแล้ว {info_str}")
                self.alert_panel.add_success("เชื่อมต่อกล้องสำเร็จ")
            else:
                self.alert_panel.add_error("ไม่สามารถเชื่อมต่อกล้อง")

    def disconnect_camera(self):
        """ตัดการเชื่อมต่อกล้อง"""
        if not self.app_controller:
            return

        # Stop camera view first
        self.camera_view.stop()

        # Disconnect camera
        success = self.app_controller.disconnect_camera()
        if success:
            self.control_panel.update_camera_status(False)
            self.camera_status.setText("กล้อง: ไม่ได้เชื่อมต่อ")
            self.alert_panel.add_info("ตัดการเชื่อมต่อกล้องแล้ว")
        else:
            self.alert_panel.add_error("ไม่สามารถตัดการเชื่อมต่อกล้อง")

    def on_load_model(self):
        """จัดการการโหลดโมเดล"""
        if self.app_controller:
            success = self.app_controller.load_model()
            if success:
                stats = self.app_controller.yolo_detector.get_stats()
                info_str = f"({stats['num_classes']} classes)"
                self.control_panel.update_model_status(True, info_str)
                self.model_status.setText(f"โมเดล: โหลดแล้ว {info_str}")
                self.alert_panel.add_success(f"โหลดโมเดลสำเร็จ - {', '.join(stats['class_names'])}")
            else:
                self.alert_panel.add_error("ไม่สามารถโหลดโมเดล")

    def on_start_inspection(self):
        """เริ่มการตรวจสอบ"""
        if self.app_controller:
            self.app_controller.start_inspection()
            self.inspection_timer.start(100)  # Check every 100ms
            self.camera_view.set_inspecting(True)  # Enable inspection mode for camera view
            self.alert_panel.add_success("เริ่มการตรวจสอบ")
            self.statusbar.showMessage("กำลังตรวจสอบ...")

    def on_stop_inspection(self):
        """หยุดการตรวจสอบ"""
        if self.app_controller:
            self.app_controller.stop_inspection()
            self.inspection_timer.stop()
            self.camera_view.set_inspecting(False)  # Disable inspection mode for camera view
            self.alert_panel.add_info("หยุดการตรวจสอบ")
            self.statusbar.showMessage("พร้อมใช้งาน")

    def on_pause_inspection(self):
        """พักการตรวจสอบ"""
        if self.app_controller:
            if self.app_controller.inspection_engine.is_paused:
                self.app_controller.inspection_engine.resume()
                self.alert_panel.add_info("ดำเนินการตรวจสอบต่อ")
            else:
                self.app_controller.inspection_engine.pause()
                self.alert_panel.add_warning("พักการตรวจสอบ")

    def on_snapshot_inspection(self):
        """ตรวจสอบแบบ Snapshot/Trigger (จับภาพและตรวจสอบ 1 ครั้ง)"""
        if not self.app_controller:
            return

        # Check snapshot mode
        snapshot_mode = self.control_panel.get_snapshot_mode()

        if snapshot_mode == 'training':
            # Training mode - save image for training
            self.save_snapshot_for_training()
            return

        # Detection mode - continue with inspection
        # Check if camera is connected
        if not self.app_controller.camera_manager or not self.app_controller.camera_manager.is_connected():
            self.alert_panel.add_error("กรุณาเชื่อมต่อกล้องก่อนใช้งาน Snapshot")
            return

        # Check if model is loaded
        if not self.app_controller.yolo_detector or not self.app_controller.yolo_detector.is_loaded():
            self.alert_panel.add_error("กรุณาโหลดโมเดลก่อนใช้งาน Snapshot")
            return

        # Temporarily enable inspection mode (for displaying result)
        was_running = self.app_controller.inspection_engine.is_running
        if not was_running:
            self.app_controller.inspection_engine.is_running = True

        # Perform single inspection
        result = self.app_controller.inspection_engine.inspect_once()

        # Restore running state
        if not was_running:
            self.app_controller.inspection_engine.is_running = False

        if result:
            # Check if there were any objects to count
            should_count = result.get('should_count', True)

            if not should_count:
                # No objects detected - display message and keep showing camera view
                self.camera_view.set_inspecting(True)

                # Update camera view with annotated image (shows Date/Time, Model, but no Status)
                if result['annotated_image'] is not None:
                    self.camera_view.display_result(result['annotated_image'])

                # Log that no objects were detected
                self.alert_panel.add_info("✓ Snapshot: Not detect object")
                self.statusbar.showMessage("Snapshot: Not detect object", 5000)

                # Schedule to clear inspection mode after 3 seconds
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(3000, lambda: self.camera_view.set_inspecting(False))
                return

            # Objects were detected - show status and count statistics
            # Enable inspection mode to show annotated image
            self.camera_view.set_inspecting(True)

            # Update camera view with annotated image
            if result['annotated_image'] is not None:
                self.camera_view.display_result(result['annotated_image'])

            # Log result with more detailed info
            status_text = "✓ OK" if result['status'] == 'OK' else "✗ NG"
            defect_info = ""
            if result['status'] == 'NG':
                defect_classes = [det['class_name'] for det in result['detections']]
                defect_info = f" - {result['num_defects']} defect(s): {', '.join(defect_classes)}"
                self.alert_panel.add_defect_alert(f"Snapshot: {status_text}{defect_info}")
            else:
                self.alert_panel.add_success(f"Snapshot: {status_text} - ไม่พบข้อบกพร่อง")

            # Update statistics display
            self.statistics_panel.update_display()

            # Update status bar
            self.statusbar.showMessage(f"Snapshot: {status_text}{defect_info}", 5000)  # Show for 5 seconds

            # Schedule to clear inspection mode after 3 seconds
            # (so user can see the result, then camera view returns to normal)
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.camera_view.set_inspecting(False))

        else:
            self.alert_panel.add_error("Snapshot: เกิดข้อผิดพลาดในการตรวจสอบ")

    def save_snapshot_for_training(self):
        """บันทึกภาพสำหรับเทรนโมเดล"""
        if not self.app_controller:
            return

        # Check if camera is connected
        if not self.app_controller.camera_manager or not self.app_controller.camera_manager.is_connected():
            self.alert_panel.add_error("กรุณาเชื่อมต่อกล้องก่อนใช้งาน Snapshot")
            return

        # Get training settings
        training_settings = self.app_controller.settings.get('snapshot_training', {
            'output_dir': 'training_images',
            'image_size': '640x640',
            'file_prefix': 'train_image',
            'resize_mode': 'crop'
        })

        output_dir = training_settings.get('output_dir', 'training_images')
        image_size_str = training_settings.get('image_size', '640x640')
        file_prefix = training_settings.get('file_prefix', 'train_image')
        resize_mode = training_settings.get('resize_mode', 'crop')

        # Parse image size
        try:
            width, height = map(int, image_size_str.split('x'))
        except:
            width, height = 640, 640

        # Create output directory if not exists
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            self.alert_panel.add_error(f"ไม่สามารถสร้างโฟลเดอร์: {e}")
            return

        # Get frame from camera
        frame = self.app_controller.camera_manager.get_frame()
        if frame is None:
            self.alert_panel.add_error("ไม่สามารถจับภาพจากกล้องได้")
            return

        # Resize image based on selected mode
        if resize_mode == 'letterbox':
            resized_frame = self.letterbox_resize(frame, (width, height))
        elif resize_mode == 'crop':
            resized_frame = self.crop_resize(frame, (width, height))
        else:  # stretch
            resized_frame = cv2.resize(frame, (width, height))

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{file_prefix}_{timestamp}.jpg"
        filepath = os.path.join(output_dir, filename)

        # Save image
        try:
            cv2.imwrite(filepath, resized_frame)
            self.alert_panel.add_success(f"✓ บันทึกรูป: {filename}")
            self.statusbar.showMessage(f"บันทึกรูปเรียบร้อย: {filepath}", 5000)

            # Briefly show the captured image
            self.camera_view.set_inspecting(True)
            self.camera_view.display_result(resized_frame)

            # Return to normal view after 1 second
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self.camera_view.set_inspecting(False))

        except Exception as e:
            self.alert_panel.add_error(f"ไม่สามารถบันทึกรูป: {e}")

    def letterbox_resize(self, image, target_size):
        """
        Resize image with letterbox (preserve aspect ratio + padding)
        This is the same method YOLO uses for training

        Args:
            image: Input image (numpy array)
            target_size: Target size tuple (width, height)

        Returns:
            Resized image with letterbox padding
        """
        target_w, target_h = target_size
        h, w = image.shape[:2]

        # Calculate scaling factor to fit image into target size
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Resize image preserving aspect ratio
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Create new image with target size (filled with gray color)
        letterbox_img = np.full((target_h, target_w, 3), 114, dtype=np.uint8)  # Gray padding

        # Calculate padding offsets (center the image)
        top = (target_h - new_h) // 2
        left = (target_w - new_w) // 2

        # Place resized image on letterbox
        letterbox_img[top:top + new_h, left:left + new_w] = resized

        return letterbox_img

    def crop_resize(self, image, target_size):
        """
        Resize image with center crop (preserve aspect ratio, no padding)
        Image is scaled to fit target, then center cropped

        Args:
            image: Input image (numpy array)
            target_size: Target size tuple (width, height)

        Returns:
            Resized and cropped image (exact target size, no distortion)
        """
        target_w, target_h = target_size
        h, w = image.shape[:2]

        # Calculate scaling to fill target (larger scale)
        scale = max(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Resize image preserving aspect ratio
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Calculate crop offsets (center crop)
        crop_x = (new_w - target_w) // 2
        crop_y = (new_h - target_h) // 2

        # Crop to target size
        cropped = resized[crop_y:crop_y + target_h, crop_x:crop_x + target_w]

        return cropped

    def on_snapshot_training_settings(self):
        """เปิด dialog ตั้งค่า Snapshot Training"""
        if self.app_controller and hasattr(self.app_controller, 'settings'):
            dialog = SnapshotTrainingSettingsDialog(self.app_controller.settings, self)
            result = dialog.exec()

            if result:
                self.alert_panel.add_success("✓ บันทึกการตั้งค่า Snapshot Training เรียบร้อย")

    def on_mqtt_settings(self):
        """เปิด dialog ตั้งค่า MQTT Connection"""
        if self.app_controller and hasattr(self.app_controller, 'settings'):
            mqtt_client = getattr(self.app_controller, 'mqtt_client', None)
            dialog = MQTTSettingsDialog(self.app_controller.settings, mqtt_client, self)
            result = dialog.exec()

            if result:
                # Reload MQTT settings and reconnect if needed
                mqtt_settings = self.app_controller.settings.get('mqtt', {})
                if mqtt_settings.get('enabled', False):
                    # Disconnect existing client if any
                    if mqtt_client:
                        mqtt_client.disconnect()

                    # Create new MQTT client
                    from core.mqtt_client import MQTTClient
                    client_id = None
                    if mqtt_settings.get('client_id_type') == 'custom':
                        client_id = mqtt_settings.get('client_id')

                    self.app_controller.mqtt_client = MQTTClient(
                        broker_host=mqtt_settings.get('broker_host'),
                        port=mqtt_settings.get('port', 1883),
                        client_id=client_id,
                        username=mqtt_settings.get('username') or None,
                        password=mqtt_settings.get('password') or None,
                        timeout=mqtt_settings.get('timeout', 3),
                        heartbeat_interval=mqtt_settings.get('heartbeat_interval', 60)
                    )

                    if self.app_controller.mqtt_client.connect():
                        # Update inspection engine
                        self.app_controller.inspection_engine.mqtt_client = self.app_controller.mqtt_client
                        self.app_controller.inspection_engine.mqtt_topic = mqtt_settings.get('topic', 'yolo/inspection')
                        self.alert_panel.add_success("✓ เชื่อมต่อ MQTT Broker สำเร็จ")
                    else:
                        self.alert_panel.add_error("✗ ไม่สามารถเชื่อมต่อ MQTT Broker ได้")
                else:
                    # Disable MQTT
                    if mqtt_client:
                        mqtt_client.disconnect()
                        self.app_controller.mqtt_client = None
                        self.app_controller.inspection_engine.mqtt_client = None
                    self.alert_panel.add_info("MQTT Connection ถูกปิดใช้งาน")

    def on_multishot_capture(self):
        """เปิด Multi-Shot Capture Dialog สำหรับ training"""
        if not self.app_controller:
            return

        if not self.app_controller.camera_manager.is_connected():
            self.alert_panel.add_error("กรุณาเชื่อมต่อกล้องก่อน")
            return

        dialog = MultiShotCaptureDialog(
            self.app_controller.camera_manager,
            self.app_controller.settings,
            parent=self
        )

        # Connect signal
        dialog.capture_completed.connect(self.on_multishot_training_captured)

        # Show dialog
        dialog.exec()

    def on_multishot_training_captured(self, shots, class_name, workpiece_id):
        """Handle เมื่อถ่าย multi-shot training เสร็จ"""
        try:
            from utils.multishot_capture import MultiShotCapture

            # Get settings
            output_dir = self.app_controller.settings.get('snapshot_training.output_dir', 'training_images')
            width = self.app_controller.settings.get('snapshot_training.width', 640)
            height = self.app_controller.settings.get('snapshot_training.height', 640)
            resize_mode = self.app_controller.settings.get('snapshot_training.resize_mode', 'crop')

            # Save training shots
            capture = MultiShotCapture(self.app_controller.camera_manager, num_shots=len(shots))

            metadata = capture.save_training_shots(
                shots=shots,
                workpiece_id=workpiece_id,
                class_name=class_name,
                output_dir=output_dir,
                width=width,
                height=height,
                resize_mode=resize_mode
            )

            self.alert_panel.add_success(f"✓ บันทึก {len(shots)} ภาพสำหรับ wp{workpiece_id:03d} ({class_name})")

        except Exception as e:
            self.alert_panel.add_error(f"✗ Error saving training shots: {e}")

    def on_multishot_inspection(self):
        """เรียก Multi-Shot Inspection"""
        if not self.app_controller:
            return

        if not self.app_controller.camera_manager.is_connected():
            self.alert_panel.add_error("กรุณาเชื่อมต่อกล้องก่อน")
            return

        if not hasattr(self.app_controller, 'yolo_detector') or self.app_controller.yolo_detector is None:
            self.alert_panel.add_error("กรุณาโหลด YOLO model ก่อน")
            return

        try:
            from core.multishot_inspector import MultiShotInspector
            from utils.multishot_capture import MultiShotCapture

            # Get settings
            num_shots = self.app_controller.settings.get('inspection.multishot_shots', 4)
            interval = self.app_controller.settings.get('inspection.multishot_interval', 2.0)
            strategy = self.app_controller.settings.get('inspection.multishot_strategy', 'majority_vote')
            conf_threshold = self.app_controller.settings.get('yolo.confidence_threshold', 0.5)

            # Create inspector
            inspector = MultiShotInspector(
                model=self.app_controller.yolo_detector.model,
                strategy=strategy,
                conf_threshold=conf_threshold
            )

            # Create capture helper
            capture = MultiShotCapture(
                self.app_controller.camera_manager,
                num_shots=num_shots,
                interval=interval
            )

            self.alert_panel.add_info(f"เริ่ม Multi-Shot Inspection ({num_shots} shots)...")

            # Capture shots
            shots = capture.capture_sequence(
                auto_advance=True,
                progress_callback=lambda current, total: self.statusbar.showMessage(f"Capturing shot {current}/{total}..."),
                countdown_callback=lambda secs: self.statusbar.showMessage(f"Next shot in {secs}s...")
            )

            if not shots:
                self.alert_panel.add_error("ไม่สามารถถ่ายภาพได้")
                return

            self.statusbar.showMessage("Analyzing...")

            # Inspect
            result = inspector.inspect(shots, save_annotated=True)

            # Show result dialog
            dialog = MultiShotResultDialog(result, parent=self)
            dialog.exec()

            # Log result
            decision = result['final_decision']['result']
            confidence = result['final_decision']['confidence']
            total_defects = result['final_decision']['total_defects']

            if decision == 'NG':
                self.alert_panel.add_defect_alert(f"Multi-Shot: {decision} - {total_defects} defects (Confidence: {confidence})")
            else:
                self.alert_panel.add_success(f"Multi-Shot: {decision} (Confidence: {confidence})")

            self.statusbar.showMessage(f"Multi-Shot Inspection: {decision}")

        except Exception as e:
            self.alert_panel.add_error(f"✗ Multi-Shot Inspection Error: {e}")
            import traceback
            traceback.print_exc()

    def on_multishot_settings(self):
        """เปิด Multi-Shot Inspection Settings Dialog"""
        if self.app_controller and hasattr(self.app_controller, 'settings'):
            dialog = MultiShotInspectionSettingsDialog(self.app_controller.settings, self)
            result = dialog.exec()

            if result:
                self.alert_panel.add_success("✓ บันทึกการตั้งค่า Multi-Shot Inspection เรียบร้อย")

    def run_inspection(self):
        """รันการตรวจสอบ 1 รอบ"""
        if self.app_controller:
            result = self.app_controller.inspection_engine.inspect_once()

            if result:
                # Update camera view with annotated image
                if result['annotated_image'] is not None:
                    self.camera_view.display_result(result['annotated_image'])

                # Update validation result panel
                if 'validation_result' in result:
                    self.validation_result_panel.update_validation_result(result['validation_result'])

                # Log result
                if result['status'] == 'NG':
                    defect_info = f"{result['num_defects']} defects detected"
                    self.alert_panel.add_defect_alert(defect_info)

                # Update FPS
                if hasattr(self.app_controller, 'camera_manager'):
                    fps = self.app_controller.camera_manager.fps
                    self.fps_status.setText(f"FPS: {fps:.1f}")

    def on_camera_profiles(self):
        """เปิด Camera Profiles Dialog"""
        if self.app_controller and hasattr(self.app_controller, 'settings'):
            dialog = CameraProfilesDialog(self.app_controller.settings, self)
            result = dialog.exec()

            if result:
                # Check if user clicked "Connect" button
                if dialog.selected_profile:
                    self.connect_with_profile(dialog.selected_profile)
                elif dialog.modified:
                    self.alert_panel.add_success("บันทึกการตั้งค่า Camera Profiles แล้ว")
        else:
            QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่สามารถเปิด Camera Profiles ได้")

    def connect_with_profile(self, profile):
        """เชื่อมต่อกล้องด้วย profile"""
        if not self.app_controller:
            return

        try:
            # Get camera type and source
            camera_type = profile.get('type', 'usb')
            source = profile['source']
            width = profile['width']
            height = profile['height']
            fps = profile['fps']

            # Prepare additional parameters
            kwargs = {}

            # Add exposure and gain if specified
            if 'exposure' in profile and profile['exposure'] > 0:
                if camera_type == 'gige':
                    kwargs['exposure_time'] = profile['exposure']
                else:
                    kwargs['exposure'] = profile['exposure']

            if 'gain' in profile and profile['gain'] > 0:
                kwargs['gain'] = profile['gain']

            # Connect camera with profile settings
            success = self.app_controller.connect_camera(
                camera_type=camera_type,
                source=source,
                width=width,
                height=height,
                fps=fps,
                **kwargs
            )

            if success:
                self.camera_view.start(30)
                info_str = f"({width}x{height} @ {fps}fps)"
                self.control_panel.update_camera_status(True, info_str)
                camera_type_display = {
                    'usb': 'USB',
                    'rtsp': 'RTSP',
                    'ip': 'IP',
                    'gige': 'GigE'
                }.get(camera_type, camera_type.upper())
                self.camera_status.setText(f"กล้อง: {profile['name']} ({camera_type_display}) {info_str}")
                self.alert_panel.add_success(f"เชื่อมต่อกล้อง '{profile['name']}' สำเร็จ")
            else:
                self.alert_panel.add_error(f"ไม่สามารถเชื่อมต่อกล้อง '{profile['name']}'")
                QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถเชื่อมต่อกล้อง\n\nProfile: {profile['name']}\nType: {camera_type}\nSource: {source}")
        except Exception as e:
            self.alert_panel.add_error(f"Error: {str(e)}")
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาด:\n{str(e)}")

    def on_model_profiles(self):
        """เปิด Model Profiles Dialog"""
        if self.app_controller and hasattr(self.app_controller, 'settings'):
            dialog = ModelProfilesDialog(self.app_controller.settings, self)
            result = dialog.exec()

            if result:
                # Check if user clicked "Load" button
                if dialog.selected_profile:
                    self.load_with_profile(dialog.selected_profile)
                elif dialog.modified:
                    self.alert_panel.add_success("บันทึกการตั้งค่า Model Profiles แล้ว")
        else:
            QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่สามารถเปิด Model Profiles ได้")

    def load_with_profile(self, profile):
        """โหลดโมเดลด้วย profile"""
        if not self.app_controller:
            return

        try:
            # Load model with profile settings
            success = self.app_controller.load_model(
                model_type=profile.get('model_type', 'detection'),
                model_path=profile['model_path'],
                device=profile['device'],
                conf_threshold=profile['confidence_threshold'],
                iou_threshold=profile['iou_threshold'],
                img_size=profile['img_size'],
                validation_rules=profile.get('validation_rules', None)
            )

            if success:
                stats = self.app_controller.yolo_detector.get_stats()
                info_str = f"({stats['num_classes']} classes)"
                self.control_panel.update_model_status(True, info_str)
                self.model_status.setText(f"โมเดล: {profile['name']} {info_str}")
                self.alert_panel.add_success(f"โหลดโมเดล '{profile['name']}' สำเร็จ")
            else:
                self.alert_panel.add_error(f"ไม่สามารถโหลดโมเดล '{profile['name']}'")
                QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถโหลดโมเดล\n\nProfile: {profile['name']}\nPath: {profile['model_path']}")
        except Exception as e:
            self.alert_panel.add_error(f"Error: {str(e)}")
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาด:\n{str(e)}")

    def on_settings(self):
        """เปิดหน้าต่างตั้งค่า"""
        self.alert_panel.add_info("เปิดหน้าต่างตั้งค่า (ยังไม่ได้สร้าง)")
        # TODO: Open settings dialog

    def on_generate_report(self):
        """สร้างรายงาน"""
        if self.app_controller and hasattr(self.app_controller, 'report_generator'):
            filepath = self.app_controller.report_generator.generate_daily_report()
            if filepath:
                self.alert_panel.add_success(f"สร้างรายงานสำเร็จ: {filepath}")
                QMessageBox.information(self, "สำเร็จ", f"สร้างรายงานที่: {filepath}")
            else:
                self.alert_panel.add_error("ไม่สามารถสร้างรายงาน")

    def on_about(self):
        """แสดงข้อมูลเกี่ยวกับโปรแกรม"""
        QMessageBox.about(
            self,
            "เกี่ยวกับ YOLO Inspection System",
            "<h2>YOLO Inspection System</h2>"
            "<p>ระบบตรวจสอบคุณภาพชิ้นงานแบบเรียลไทม์ด้วย YOLO</p>"
            "<p>Version: 1.0</p>"
            "<p>Powered by YOLOv8 & PyQt5</p>"
        )

    def apply_dark_theme(self):
        """ใช้ธีมสีเข้ม"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                padding: 8px;
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 3px;
                color: white;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
            QStatusBar {
                background-color: #1e1e1e;
                color: #aaa;
            }
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #2b2b2b;
                border: 1px solid #444;
                gridline-color: #444;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: white;
                padding: 5px;
                border: 1px solid #555;
            }
        """)

    def closeEvent(self, event):
        """จัดการเมื่อปิดโปรแกรม"""
        reply = QMessageBox.question(
            self,
            "ออกจากโปรแกรม",
            "คุณต้องการออกจากโปรแกรมหรือไม่?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Stop inspection
            if self.app_controller:
                self.app_controller.cleanup()

            self.alert_panel.add_info("ปิดโปรแกรม")
            event.accept()
        else:
            event.ignore()

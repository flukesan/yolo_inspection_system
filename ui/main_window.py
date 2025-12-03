"""
Main Window - หน้าต่างหลัก
Main application window for YOLO Inspection System
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QMenuBar, QFileDialog, QMessageBox,
                             QStatusBar, QLabel)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction

from .widgets.camera_view import CameraView
from .widgets.control_panel import ControlPanel
from .widgets.statistics_panel import StatisticsPanel
from .widgets.alert_panel import AlertPanel
from .dialogs.camera_profiles_dialog import CameraProfilesDialog


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

        right_layout.addWidget(self.control_panel, stretch=1)
        right_layout.addWidget(self.statistics_panel, stretch=1)

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
        """จัดการการเชื่อมต่อกล้อง"""
        if self.app_controller:
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
            self.alert_panel.add_success("เริ่มการตรวจสอบ")
            self.statusbar.showMessage("กำลังตรวจสอบ...")

    def on_stop_inspection(self):
        """หยุดการตรวจสอบ"""
        if self.app_controller:
            self.app_controller.stop_inspection()
            self.inspection_timer.stop()
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

    def run_inspection(self):
        """รันการตรวจสอบ 1 รอบ"""
        if self.app_controller:
            result = self.app_controller.inspection_engine.inspect_once()

            if result:
                # Update camera view with annotated image
                if result['annotated_image'] is not None:
                    self.camera_view.display_result(result['annotated_image'])

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
            # Connect camera with profile settings
            success = self.app_controller.connect_camera(
                source=profile['source'],
                width=profile['width'],
                height=profile['height'],
                fps=profile['fps']
            )

            if success:
                self.camera_view.start(30)
                info_str = f"({profile['width']}x{profile['height']} @ {profile['fps']}fps)"
                self.control_panel.update_camera_status(True, info_str)
                self.camera_status.setText(f"กล้อง: {profile['name']} {info_str}")
                self.alert_panel.add_success(f"เชื่อมต่อกล้อง '{profile['name']}' สำเร็จ")
            else:
                self.alert_panel.add_error(f"ไม่สามารถเชื่อมต่อกล้อง '{profile['name']}'")
                QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถเชื่อมต่อกล้อง\n\nProfile: {profile['name']}\nSource: {profile['source']}")
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

"""
Multi-Shot Result Dialog
แสดงผลการตรวจสอบแบบ multi-shot พร้อม visualization
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QScrollArea, QWidget,
                             QGridLayout, QTextEdit, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QFont
import cv2
import numpy as np


class MultiShotResultDialog(QDialog):
    """Dialog แสดงผลการตรวจสอบ multi-shot"""

    def __init__(self, result, parent=None):
        """
        Initialize dialog

        Args:
            result: Multi-shot inspection result dictionary
            parent: Parent widget
        """
        super().__init__(parent)
        self.result = result
        self.setWindowTitle("Multi-Shot Inspection Result")
        self.setModal(True)
        self.setMinimumSize(1000, 700)
        self.setup_ui()

    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📊 Multi-Shot Inspection Result")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Summary Section
        summary_group = self.create_summary_section()
        layout.addWidget(summary_group)

        # Shots Grid Section
        shots_group = self.create_shots_section()
        layout.addWidget(shots_group)

        # Aggregation Details Section
        details_group = self.create_aggregation_details()
        layout.addWidget(details_group)

        # Buttons
        btn_layout = QHBoxLayout()

        close_btn = QPushButton("✓ ปิด")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def create_summary_section(self):
        """สร้าง summary section"""
        group = QGroupBox("📋 สรุปผลการตรวจสอบ")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QHBoxLayout()

        final_decision = self.result.get('final_decision', {})
        decision = final_decision.get('result', 'UNKNOWN')
        confidence = final_decision.get('confidence', 'UNKNOWN')
        total_defects = final_decision.get('total_defects', 0)
        inference_time = final_decision.get('total_inference_time_ms', 0)

        # Decision Card
        decision_color = "#f44336" if decision == "NG" else "#4CAF50"
        decision_label = QLabel(f"<h1 style='color: {decision_color};'>{decision}</h1>")
        decision_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Confidence Card
        confidence_text = f"""
        <div style='text-align: center;'>
            <p style='font-size: 14px; color: #666; margin: 5px;'>Confidence</p>
            <p style='font-size: 24px; font-weight: bold; margin: 5px;'>{confidence}</p>
        </div>
        """
        confidence_label = QLabel(confidence_text)
        confidence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Stats Card
        stats_text = f"""
        <div style='text-align: center;'>
            <p style='font-size: 14px; color: #666; margin: 5px;'>Total Defects</p>
            <p style='font-size: 24px; font-weight: bold; color: #f44336; margin: 5px;'>{total_defects}</p>
        </div>
        """
        stats_label = QLabel(stats_text)
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Time Card
        time_text = f"""
        <div style='text-align: center;'>
            <p style='font-size: 14px; color: #666; margin: 5px;'>Inference Time</p>
            <p style='font-size: 20px; font-weight: bold; margin: 5px;'>{inference_time:.1f} ms</p>
        </div>
        """
        time_label = QLabel(time_text)
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(decision_label)
        layout.addWidget(confidence_label)
        layout.addWidget(stats_label)
        layout.addWidget(time_label)

        group.setLayout(layout)
        return group

    def create_shots_section(self):
        """สร้าง shots grid section"""
        group = QGroupBox("🎬 Individual Shots")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)

        container = QWidget()
        grid = QGridLayout()

        shots = self.result.get('shots', [])
        cols = 2  # 2 columns

        for idx, shot in enumerate(shots):
            row = idx // cols
            col = idx % cols

            shot_widget = self.create_shot_widget(shot)
            grid.addWidget(shot_widget, row, col)

        container.setLayout(grid)
        scroll.setWidget(container)

        group_layout = QVBoxLayout()
        group_layout.addWidget(scroll)
        group.setLayout(group_layout)

        return group

    def create_shot_widget(self, shot):
        """สร้าง widget สำหรับแสดง 1 shot"""
        widget = QGroupBox(f"Shot {shot.get('shot_id', '?')}")
        widget.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout()

        # Image (if available)
        annotated = shot.get('annotated_image')
        if annotated is not None:
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Convert to QPixmap
            if isinstance(annotated, np.ndarray):
                height, width = annotated.shape[:2]
                bytes_per_line = 3 * width

                # Convert BGR to RGB
                rgb_image = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

                q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)

                # Scale to fit
                scaled_pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                img_label.setPixmap(scaled_pixmap)

            layout.addWidget(img_label)

        # Detection info
        detections = shot.get('detections', [])
        inference_time = shot.get('inference_time_ms', 0)

        info_text = f"""
        <div style='padding: 5px;'>
            <p><b>Detections:</b> {len(detections)}</p>
            <p><b>Inference Time:</b> {inference_time:.2f} ms</p>
        </div>
        """

        if detections:
            info_text += "<p><b>Found:</b></p><ul>"
            for det in detections:
                class_name = det.get('class', 'Unknown')
                conf = det.get('confidence', 0)
                info_text += f"<li>{class_name} ({conf:.2f})</li>"
            info_text += "</ul>"
        else:
            info_text += "<p style='color: #4CAF50;'><b>✓ No defects</b></p>"

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        widget.setLayout(layout)
        return widget

    def create_aggregation_details(self):
        """สร้าง aggregation details section"""
        group = QGroupBox("🔄 Aggregation Details")

        layout = QVBoxLayout()

        aggregation = self.result.get('aggregation', {})
        method = aggregation.get('method', 'unknown')
        confirmed_defects = aggregation.get('confirmed_defects', [])
        defect_votes = aggregation.get('defect_votes', {})

        # Method info
        method_label = QLabel(f"<b>Strategy:</b> {method}")
        layout.addWidget(method_label)

        # Votes table
        if defect_votes:
            votes_text = "<b>Defect Votes:</b><br>"
            votes_text += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
            votes_text += "<tr><th>Defect Class</th><th>Votes</th></tr>"

            for defect_class, votes in defect_votes.items():
                votes_text += f"<tr><td>{defect_class}</td><td>{votes}</td></tr>"

            votes_text += "</table>"

            votes_label = QLabel(votes_text)
            votes_label.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(votes_label)

        # Confirmed defects
        if confirmed_defects:
            confirmed_text = "<br><b>Confirmed Defects:</b><br>"
            confirmed_text += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
            confirmed_text += "<tr><th>Class</th><th>Votes</th><th>Vote %</th><th>Avg Conf</th><th>Status</th></tr>"

            for defect in confirmed_defects:
                class_name = defect.get('class', 'Unknown')
                votes = defect.get('votes', 0)
                vote_pct = defect.get('vote_percentage', 0)
                avg_conf = defect.get('avg_confidence', 0)
                status = defect.get('status', 'UNKNOWN')

                confirmed_text += f"<tr>"
                confirmed_text += f"<td>{class_name}</td>"
                confirmed_text += f"<td>{votes}</td>"
                confirmed_text += f"<td>{vote_pct:.1f}%</td>"
                confirmed_text += f"<td>{avg_conf:.3f}</td>"
                confirmed_text += f"<td><b>{status}</b></td>"
                confirmed_text += f"</tr>"

            confirmed_text += "</table>"

            confirmed_label = QLabel(confirmed_text)
            confirmed_label.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(confirmed_label)
        else:
            no_defects_label = QLabel("<p style='color: #4CAF50; font-size: 14px;'><b>✓ No confirmed defects</b></p>")
            layout.addWidget(no_defects_label)

        group.setLayout(layout)
        return group

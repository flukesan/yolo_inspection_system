"""
YOLO Detector - ตรวจจับชิ้นงานด้วย YOLO
YOLO-based defect detection
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import time


class YOLODetector:
    """ตรวจจับ defect ด้วย YOLO"""

    def __init__(self, model_path: str = None):
        """
        Initialize YOLO Detector

        Args:
            model_path: Path to YOLO model (.pt file)
        """
        self.model = None
        self.model_path = model_path
        self.model_type = 'detection'  # detection, segmentation, classification, pose
        self.class_names = []
        self.device = 'cpu'
        self.conf_threshold = 0.5
        self.iou_threshold = 0.45
        self.img_size = 640

        # Statistics
        self.total_detections = 0
        self.avg_inference_time = 0
        self.inference_times = []

    def load_model(self, model_type: str = 'detection', model_path: str = '',
                   device: str = 'cpu', conf_threshold: float = 0.5,
                   iou_threshold: float = 0.45, img_size: int = 640) -> bool:
        """
        โหลดโมเดล YOLO

        Args:
            model_type: Type of model ('detection', 'segmentation', 'classification', 'pose')
            model_path: Path to model file
            device: Device to use ('cpu' or 'cuda')
            conf_threshold: Confidence threshold
            iou_threshold: IoU threshold for NMS
            img_size: Input image size

        Returns:
            True if successful
        """
        try:
            print(f"กำลังโหลดโมเดล YOLO: {model_path}")
            print(f"  - ประเภท: {model_type}")

            # Try to import ultralytics
            try:
                from ultralytics import YOLO
            except ImportError:
                print("✗ กรุณาติดตั้ง ultralytics: pip install ultralytics")
                return False

            # Load model
            self.model = YOLO(model_path)
            self.model_path = model_path
            self.model_type = model_type
            self.device = device
            self.conf_threshold = conf_threshold
            self.iou_threshold = iou_threshold
            self.img_size = img_size

            # Get class names
            if hasattr(self.model, 'names'):
                self.class_names = list(self.model.names.values())
            else:
                self.class_names = []

            # Determine model type from file name if not specified correctly
            if '-seg' in model_path.lower():
                self.model_type = 'segmentation'
            elif '-cls' in model_path.lower():
                self.model_type = 'classification'
            elif '-pose' in model_path.lower():
                self.model_type = 'pose'

            print(f"✓ โหลดโมเดล YOLO สำเร็จ")
            print(f"  - Device: {device}")
            print(f"  - Type: {self.model_type}")
            print(f"  - Classes: {len(self.class_names)} ({', '.join(self.class_names)})")
            print(f"  - Confidence: {conf_threshold}")

            return True

        except Exception as e:
            print(f"✗ Error loading YOLO model: {e}")
            return False

    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        ตรวจจับ object ในภาพ (รองรับทุกประเภทโมเดล)

        Args:
            image: Input image (BGR format)

        Returns:
            List of detections, each containing:
                - type: Model type used
                - class_id: Class ID
                - class_name: Class name
                - confidence: Detection confidence
                - bbox: Bounding box [x1, y1, x2, y2] (สำหรับ detection, segmentation, pose)
                - center: Center point (x, y) (สำหรับ detection, segmentation, pose)
                - mask: Segmentation mask (สำหรับ segmentation เท่านั้น)
                - keypoints: Pose keypoints (สำหรับ pose เท่านั้น)
        """
        if self.model is None:
            print("! โมเดลยังไม่ได้โหลด")
            return []

        try:
            start_time = time.time()

            # Run inference
            results = self.model.predict(
                source=image,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                imgsz=self.img_size,
                device=self.device,
                verbose=False
            )

            # Process results based on model type
            detections = []

            if results and len(results) > 0:
                result = results[0]

                # Classification model (ไม่มี bounding boxes)
                if self.model_type == 'classification':
                    if hasattr(result, 'probs') and result.probs is not None:
                        probs = result.probs.cpu().numpy()
                        top_class_id = int(probs.top1)
                        top_conf = float(probs.top1conf)
                        class_name = self.class_names[top_class_id] if top_class_id < len(self.class_names) else f"Class_{top_class_id}"

                        detection = {
                            'type': 'classification',
                            'class_id': top_class_id,
                            'class_name': class_name,
                            'confidence': top_conf
                        }
                        detections.append(detection)

                # Detection / Segmentation / Pose models (มี bounding boxes)
                elif result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes.cpu().numpy()

                    for idx, box in enumerate(boxes):
                        # Extract box data
                        xyxy = box.xyxy[0].astype(int)  # [x1, y1, x2, y2]
                        conf = float(box.conf[0])
                        cls_id = int(box.cls[0])

                        # Get class name
                        class_name = self.class_names[cls_id] if cls_id < len(self.class_names) else f"Class_{cls_id}"

                        # Calculate center
                        center_x = int((xyxy[0] + xyxy[2]) / 2)
                        center_y = int((xyxy[1] + xyxy[3]) / 2)

                        detection = {
                            'type': self.model_type,
                            'class_id': cls_id,
                            'class_name': class_name,
                            'confidence': conf,
                            'bbox': xyxy.tolist(),
                            'center': (center_x, center_y)
                        }

                        # Add segmentation mask if available
                        if self.model_type == 'segmentation' and hasattr(result, 'masks') and result.masks is not None:
                            masks = result.masks.cpu().numpy()
                            if idx < len(masks.data):
                                detection['mask'] = masks.data[idx]

                        # Add pose keypoints if available
                        if self.model_type == 'pose' and hasattr(result, 'keypoints') and result.keypoints is not None:
                            keypoints = result.keypoints.cpu().numpy()
                            if idx < len(keypoints.data):
                                detection['keypoints'] = keypoints.data[idx].tolist()

                        detections.append(detection)

            # Update statistics
            inference_time = (time.time() - start_time) * 1000  # ms
            self.inference_times.append(inference_time)
            if len(self.inference_times) > 100:
                self.inference_times.pop(0)
            self.avg_inference_time = np.mean(self.inference_times)
            self.total_detections += len(detections)

            return detections

        except Exception as e:
            print(f"✗ Error during detection: {e}")
            import traceback
            traceback.print_exc()
            return []

    def draw_detections(self, image: np.ndarray, detections: List[Dict[str, Any]],
                        show_conf: bool = True, show_class: bool = True,
                        timestamp: str = None, model_name: str = None,
                        status: str = None) -> np.ndarray:
        """
        วาด bounding box และ label บนภาพ (รองรับทุกประเภทโมเดล)

        Args:
            image: Input image
            detections: List of detections from detect()
            show_conf: Show confidence score
            show_class: Show class name
            timestamp: Timestamp string to display (optional)
            model_name: Model name to display (optional)
            status: Inspection status "OK" or "NG" (optional)

        Returns:
            Annotated image
        """
        annotated = image.copy()
        h, w = image.shape[:2]

        # Draw overlay information at top (Date/Time, Model, Status)
        if timestamp or model_name or status:
            # Create semi-transparent overlay at top
            overlay = annotated.copy()
            overlay_height = 80
            cv2.rectangle(overlay, (0, 0), (w, overlay_height), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, annotated, 0.5, 0, annotated)

            # Font settings
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            font_thickness = 2
            text_color = (255, 255, 255)  # White text on dark background

            y_offset = 30  # Starting Y position

            # Left side: Date/Time and Model name
            if timestamp:
                date_text = f"Date : {timestamp}"
                cv2.putText(annotated, date_text, (15, y_offset),
                           font, font_scale, text_color, font_thickness)

            if model_name:
                model_text = f"Model: {model_name}"
                cv2.putText(annotated, model_text, (15, y_offset + 35),
                           font, font_scale, text_color, font_thickness)

            # Right side: Status (OK/NG)
            if status:
                status_text = f"Status: {status}"
                # Choose color based on status
                if status == "OK":
                    status_color = (0, 255, 0)  # Green for OK
                else:  # NG
                    status_color = (0, 0, 255)  # Red for NG

                # Get text size to align right
                (text_w, text_h), _ = cv2.getTextSize(status_text, font, 1.2, 3)
                status_x = w - text_w - 15

                # Draw status with larger font
                cv2.putText(annotated, status_text, (status_x, y_offset + 10),
                           font, 1.2, status_color, 3)

        # Define colors for different classes
        colors = [
            (0, 255, 0),    # Green - OK
            (0, 0, 255),    # Red - Defect
            (255, 0, 0),    # Blue
            (0, 255, 255),  # Yellow
            (255, 0, 255),  # Magenta
            (255, 255, 0),  # Cyan
        ]

        for idx, det in enumerate(detections):
            class_id = det['class_id']
            class_name = det['class_name']
            conf = det['confidence']
            det_type = det.get('type', 'detection')

            # Select color
            color = colors[class_id % len(colors)]

            # Handle Classification (no bounding box)
            if det_type == 'classification' or 'bbox' not in det:
                # Draw full image bounding box for classification
                h, w = image.shape[:2]
                border_thickness = 8

                # Draw thick border around image
                cv2.rectangle(annotated, (border_thickness, border_thickness),
                            (w - border_thickness, h - border_thickness), color, border_thickness)

                # Prepare label
                label_parts = []
                if show_class:
                    label_parts.append(f"Class: {class_name}")
                if show_conf:
                    label_parts.append(f"{conf:.2%}")

                label = " - ".join(label_parts)

                # Draw label background (center top)
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.2
                font_thickness = 3
                (label_w, label_h), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)

                # Center position
                x_pos = (w - label_w) // 2
                y_pos = 50

                # Draw background rectangle
                cv2.rectangle(annotated,
                            (x_pos - 10, y_pos - label_h - 15),
                            (x_pos + label_w + 10, y_pos + 10),
                            color, -1)

                # Draw text
                cv2.putText(annotated, label, (x_pos, y_pos),
                          font, font_scale, (255, 255, 255), font_thickness)

                continue

            # Handle Detection/Segmentation/Pose (with bounding boxes)
            if 'bbox' in det:
                x1, y1, x2, y2 = det['bbox']

                # Draw bounding box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

                # Prepare label
                label_parts = []
                if show_class:
                    label_parts.append(class_name)
                if show_conf:
                    label_parts.append(f"{conf:.2f}")

                label = " ".join(label_parts)

                # Draw label background
                (label_w, label_h), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                cv2.rectangle(annotated, (x1, y1 - label_h - 10),
                             (x1 + label_w, y1), color, -1)

                # Draw label text
                cv2.putText(annotated, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Draw center point if available
                if 'center' in det:
                    center_x, center_y = det['center']
                    cv2.circle(annotated, (center_x, center_y), 5, color, -1)

                # Draw pose keypoints if available
                if det_type == 'pose' and 'keypoints' in det:
                    keypoints = det['keypoints']
                    for kp in keypoints:
                        if len(kp) >= 2:  # x, y coordinates
                            kp_x, kp_y = int(kp[0]), int(kp[1])
                            cv2.circle(annotated, (kp_x, kp_y), 3, (0, 255, 0), -1)

        return annotated

    def get_stats(self) -> Dict[str, Any]:
        """
        ดึงสถิติการตรวจจับ

        Returns:
            Statistics dictionary
        """
        return {
            'total_detections': self.total_detections,
            'avg_inference_time_ms': round(self.avg_inference_time, 2),
            'model_loaded': self.model is not None,
            'num_classes': len(self.class_names),
            'class_names': self.class_names
        }

    def is_loaded(self) -> bool:
        """
        ตรวจสอบว่าโมเดลโหลดแล้วหรือไม่

        Returns:
            True if model is loaded
        """
        return self.model is not None

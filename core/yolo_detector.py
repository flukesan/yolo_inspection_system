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
        self.class_names = []
        self.device = 'cpu'
        self.conf_threshold = 0.5
        self.iou_threshold = 0.45
        self.img_size = 640

        # Statistics
        self.total_detections = 0
        self.avg_inference_time = 0
        self.inference_times = []

    def load_model(self, model_path: str, device: str = 'cpu',
                   conf_threshold: float = 0.5, iou_threshold: float = 0.45,
                   img_size: int = 640) -> bool:
        """
        โหลดโมเดล YOLO

        Args:
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

            # Try to import ultralytics
            try:
                from ultralytics import YOLO
            except ImportError:
                print("✗ กรุณาติดตั้ง ultralytics: pip install ultralytics")
                return False

            # Load model
            self.model = YOLO(model_path)
            self.model_path = model_path
            self.device = device
            self.conf_threshold = conf_threshold
            self.iou_threshold = iou_threshold
            self.img_size = img_size

            # Get class names
            if hasattr(self.model, 'names'):
                self.class_names = list(self.model.names.values())
            else:
                self.class_names = []

            print(f"✓ โหลดโมเดล YOLO สำเร็จ")
            print(f"  - Device: {device}")
            print(f"  - Classes: {len(self.class_names)} ({', '.join(self.class_names)})")
            print(f"  - Confidence: {conf_threshold}")

            return True

        except Exception as e:
            print(f"✗ Error loading YOLO model: {e}")
            return False

    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        ตรวจจับ object ในภาพ

        Args:
            image: Input image (BGR format)

        Returns:
            List of detections, each containing:
                - class_id: Class ID
                - class_name: Class name
                - confidence: Detection confidence
                - bbox: Bounding box [x1, y1, x2, y2]
                - center: Center point (x, y)
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

            # Process results
            detections = []

            if results and len(results) > 0:
                result = results[0]

                if result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes.cpu().numpy()

                    for box in boxes:
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
                            'class_id': cls_id,
                            'class_name': class_name,
                            'confidence': conf,
                            'bbox': xyxy.tolist(),
                            'center': (center_x, center_y)
                        }

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
            return []

    def draw_detections(self, image: np.ndarray, detections: List[Dict[str, Any]],
                        show_conf: bool = True, show_class: bool = True) -> np.ndarray:
        """
        วาด bounding box และ label บนภาพ

        Args:
            image: Input image
            detections: List of detections from detect()
            show_conf: Show confidence score
            show_class: Show class name

        Returns:
            Annotated image
        """
        annotated = image.copy()

        # Define colors for different classes
        colors = [
            (0, 255, 0),    # Green - OK
            (0, 0, 255),    # Red - Defect
            (255, 0, 0),    # Blue
            (0, 255, 255),  # Yellow
            (255, 0, 255),  # Magenta
            (255, 255, 0),  # Cyan
        ]

        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_id = det['class_id']
            class_name = det['class_name']
            conf = det['confidence']

            # Select color
            color = colors[class_id % len(colors)]

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

            # Draw center point
            center_x, center_y = det['center']
            cv2.circle(annotated, (center_x, center_y), 5, color, -1)

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

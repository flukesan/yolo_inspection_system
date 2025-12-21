"""
Multi-Shot Capture Utilities
Helper functions สำหรับการถ่ายภาพแบบ multi-shot
"""
import os
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import numpy as np
import cv2


class MultiShotCapture:
    """
    Multi-shot capture helper for both training and inspection modes
    """

    def __init__(self, camera_manager, num_shots: int = 4, interval: float = 2.0):
        """
        Initialize Multi-Shot Capture

        Args:
            camera_manager: CameraManager instance
            num_shots: Number of shots per workpiece
            interval: Time between shots in seconds
        """
        self.camera = camera_manager
        self.num_shots = num_shots
        self.interval = interval

    def capture_sequence(
        self,
        auto_advance: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        countdown_callback: Optional[Callable[[float], None]] = None
    ) -> List[np.ndarray]:
        """
        Capture a sequence of shots

        Args:
            auto_advance: Auto capture after interval or wait for manual trigger
            progress_callback: Callback(current_shot, total_shots)
            countdown_callback: Callback(seconds_remaining)

        Returns:
            List of captured frames
        """
        shots = []

        for shot_num in range(1, self.num_shots + 1):
            # Progress callback
            if progress_callback:
                progress_callback(shot_num, self.num_shots)

            # Get frame from camera
            frame = self.camera.get_frame()
            if frame is None:
                print(f"⚠ Warning: Failed to capture shot {shot_num}")
                continue

            shots.append(frame.copy())
            print(f"✓ Captured shot {shot_num}/{self.num_shots}")

            # Wait for next shot (except last one)
            if shot_num < self.num_shots:
                if auto_advance:
                    # Countdown
                    for remaining in range(int(self.interval), 0, -1):
                        if countdown_callback:
                            countdown_callback(remaining)
                        time.sleep(1)
                else:
                    # Wait for manual trigger (handled by caller)
                    pass

        return shots

    def save_training_shots(
        self,
        shots: List[np.ndarray],
        workpiece_id: int,
        class_name: str,
        output_dir: str,
        width: int = 640,
        height: int = 640,
        resize_mode: str = 'crop'
    ) -> Dict[str, Any]:
        """
        Save captured shots for training dataset

        Args:
            shots: List of captured frames
            workpiece_id: Workpiece identifier
            class_name: OK or NG
            output_dir: Base output directory
            width: Target width
            height: Target height
            resize_mode: Resize mode (crop, letterbox, stretch)

        Returns:
            Metadata dictionary
        """
        # Create class directory
        class_dir = os.path.join(output_dir, class_name)
        os.makedirs(class_dir, exist_ok=True)

        saved_files = []
        timestamp = datetime.now()

        for shot_num, frame in enumerate(shots, 1):
            # Resize frame
            resized = self._resize_frame(frame, width, height, resize_mode)

            # Generate filename
            filename = f"wp{workpiece_id:03d}_shot{shot_num}.jpg"
            filepath = os.path.join(class_dir, filename)

            # Save image
            cv2.imwrite(filepath, resized)
            saved_files.append(filename)

            print(f"  Saved: {filepath}")

        # Create metadata
        metadata = {
            'workpiece_id': f"wp{workpiece_id:03d}",
            'class': class_name,
            'capture_mode': 'multi_shot',
            'shots_total': len(shots),
            'timestamp': timestamp.isoformat(),
            'shots': [
                {
                    'shot_id': i + 1,
                    'filename': f,
                    'timestamp': timestamp.isoformat()
                }
                for i, f in enumerate(saved_files)
            ]
        }

        # Save metadata
        metadata_path = os.path.join(class_dir, f"wp{workpiece_id:03d}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return metadata

    def save_inspection_shots(
        self,
        shots: List[np.ndarray],
        output_dir: str,
        inspection_id: str = None
    ) -> str:
        """
        Save captured shots for inspection

        Args:
            shots: List of captured frames
            output_dir: Output directory
            inspection_id: Inspection identifier

        Returns:
            Path to saved directory
        """
        if inspection_id is None:
            inspection_id = f"multishot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create inspection directory
        shot_dir = os.path.join(output_dir, inspection_id)
        os.makedirs(shot_dir, exist_ok=True)

        for shot_num, frame in enumerate(shots, 1):
            filename = f"shot{shot_num}.jpg"
            filepath = os.path.join(shot_dir, filename)
            cv2.imwrite(filepath, frame)

        return shot_dir

    def _resize_frame(
        self,
        frame: np.ndarray,
        width: int,
        height: int,
        mode: str = 'crop'
    ) -> np.ndarray:
        """
        Resize frame with different modes

        Args:
            frame: Input frame
            width: Target width
            height: Target height
            mode: Resize mode (crop, letterbox, stretch)

        Returns:
            Resized frame
        """
        h, w = frame.shape[:2]
        target_w, target_h = width, height

        if mode == 'stretch':
            # Simple resize (may distort)
            return cv2.resize(frame, (target_w, target_h))

        elif mode == 'letterbox':
            # Letterbox resize (maintain aspect ratio with padding)
            scale = min(target_w / w, target_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)

            resized = cv2.resize(frame, (new_w, new_h))

            # Create black canvas
            canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)

            # Center the image
            y_offset = (target_h - new_h) // 2
            x_offset = (target_w - new_w) // 2
            canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

            return canvas

        else:  # crop
            # Crop to maintain aspect ratio
            scale = max(target_w / w, target_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)

            resized = cv2.resize(frame, (new_w, new_h))

            # Crop center
            y_offset = (new_h - target_h) // 2
            x_offset = (new_w - target_w) // 2
            cropped = resized[y_offset:y_offset + target_h, x_offset:x_offset + target_w]

            return cropped


def get_next_workpiece_id(output_dir: str, class_name: str) -> int:
    """
    Get next available workpiece ID

    Args:
        output_dir: Base output directory
        class_name: Class name (OK/NG)

    Returns:
        Next workpiece ID
    """
    class_dir = os.path.join(output_dir, class_name)

    if not os.path.exists(class_dir):
        return 1

    # Find existing workpiece IDs
    existing_ids = set()
    for filename in os.listdir(class_dir):
        if filename.startswith('wp') and '_shot' in filename:
            try:
                # Extract ID from "wp001_shot1.jpg"
                wp_id = int(filename[2:5])
                existing_ids.add(wp_id)
            except:
                pass

    if not existing_ids:
        return 1

    return max(existing_ids) + 1

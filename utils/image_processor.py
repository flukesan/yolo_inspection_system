"""
Image Processor - ประมวลผลภาพ
Image processing utilities
"""
import cv2
import numpy as np
from typing import Tuple, Optional


class ImageProcessor:
    """ประมวลผลภาพ"""

    @staticmethod
    def resize(image: np.ndarray, width: int = None, height: int = None,
               keep_aspect: bool = True) -> np.ndarray:
        """
        ปรับขนาดภาพ

        Args:
            image: Input image
            width: Target width
            height: Target height
            keep_aspect: Keep aspect ratio

        Returns:
            Resized image
        """
        if width is None and height is None:
            return image

        h, w = image.shape[:2]

        if keep_aspect:
            if width is not None and height is None:
                ratio = width / w
                height = int(h * ratio)
            elif height is not None and width is None:
                ratio = height / h
                width = int(w * ratio)
            else:
                ratio = min(width / w, height / h)
                width = int(w * ratio)
                height = int(h * ratio)

        return cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)

    @staticmethod
    def rotate(image: np.ndarray, angle: float) -> np.ndarray:
        """
        หมุนภาพ

        Args:
            image: Input image
            angle: Rotation angle (degrees)

        Returns:
            Rotated image
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)

        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (w, h))

        return rotated

    @staticmethod
    def crop(image: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """
        ครอปภาพ

        Args:
            image: Input image
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner

        Returns:
            Cropped image
        """
        return image[y1:y2, x1:x2]

    @staticmethod
    def enhance_contrast(image: np.ndarray, clip_limit: float = 2.0,
                        tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
        """
        เพิ่มความคมชัดด้วย CLAHE

        Args:
            image: Input image
            clip_limit: Clip limit for CLAHE
            tile_grid_size: Tile grid size

        Returns:
            Enhanced image
        """
        if len(image.shape) == 3:
            # Convert to LAB
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            l = clahe.apply(l)

            # Merge and convert back
            lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            enhanced = clahe.apply(image)

        return enhanced

    @staticmethod
    def denoise(image: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        ลดสัญญาณรบกวน

        Args:
            image: Input image
            strength: Denoising strength

        Returns:
            Denoised image
        """
        if len(image.shape) == 3:
            denoised = cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)
        else:
            denoised = cv2.fastNlMeansDenoising(image, None, strength, 7, 21)

        return denoised

    @staticmethod
    def adjust_brightness(image: np.ndarray, value: int) -> np.ndarray:
        """
        ปรับความสว่าง

        Args:
            image: Input image
            value: Brightness adjustment (-100 to 100)

        Returns:
            Adjusted image
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        v = cv2.add(v, value)
        v = np.clip(v, 0, 255)

        hsv = cv2.merge([h, s, v])
        adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return adjusted

    @staticmethod
    def draw_text(image: np.ndarray, text: str, position: Tuple[int, int],
                  font_scale: float = 1.0, color: Tuple[int, int, int] = (255, 255, 255),
                  thickness: int = 2, bg_color: Optional[Tuple[int, int, int]] = None) -> np.ndarray:
        """
        เขียนข้อความบนภาพ

        Args:
            image: Input image
            text: Text to draw
            position: Position (x, y)
            font_scale: Font scale
            color: Text color (BGR)
            thickness: Text thickness
            bg_color: Background color (BGR) or None

        Returns:
            Image with text
        """
        result = image.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX

        if bg_color is not None:
            (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            x, y = position
            cv2.rectangle(result, (x, y - text_h - baseline),
                         (x + text_w, y + baseline), bg_color, -1)

        cv2.putText(result, text, position, font, font_scale, color, thickness)

        return result

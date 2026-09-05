import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any
from app.core.config import settings

class ImageQualityService:
    """
    Image Quality Assessment Service for HortiSentry.
    Evaluates blur using OpenCV Laplacian variance, brightness level, and minimum dimensions.
    Returns structured visual quality metadata.
    """

    @classmethod
    def analyze_quality(cls, image: Image.Image) -> Dict[str, Any]:
        width, height = image.size

        # 1. Dimension validation
        if width < settings.MIN_IMAGE_DIMENSION or height < settings.MIN_IMAGE_DIMENSION:
            return {
                "is_valid": False,
                "is_blur_detected": False,
                "is_exposure_issue": False,
                "blur_score": 0.0,
                "brightness_score": 0.0,
                "width": width,
                "height": height,
                "quality_message": f"Image dimension ({width}x{height}) is too small for reliable analysis."
            }

        # Convert PIL Image to RGB NumPy array
        rgb_array = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2GRAY)

        # 2. Blur Detection via Laplacian Variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_score = round(float(laplacian_var), 2)
        is_blur_detected = blur_score < settings.BLUR_THRESHOLD

        # 3. Brightness / Exposure Calculation
        brightness_score = round(float(np.mean(gray)), 2)
        is_exposure_issue = (
            brightness_score < settings.MIN_BRIGHTNESS or 
            brightness_score > settings.MAX_BRIGHTNESS
        )

        # Formulate human-readable status message
        quality_messages = []
        if is_blur_detected:
            quality_messages.append(f"Image appears blurry (Score: {blur_score} < threshold {settings.BLUR_THRESHOLD}).")
        if brightness_score < settings.MIN_BRIGHTNESS:
            quality_messages.append("Image is too dark for clear symptom observation.")
        elif brightness_score > settings.MAX_BRIGHTNESS:
            quality_messages.append("Image is overexposed / too bright.")

        if quality_messages:
            quality_message = " ".join(quality_messages) + " Expert review recommended."
            is_valid = False
        else:
            quality_message = "Image quality is acceptable for AI observation."
            is_valid = True

        return {
            "is_valid": is_valid,
            "is_blur_detected": is_blur_detected,
            "is_exposure_issue": is_exposure_issue,
            "blur_score": blur_score,
            "brightness_score": brightness_score,
            "width": width,
            "height": height,
            "quality_message": quality_message
        }

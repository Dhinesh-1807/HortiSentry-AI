import time
import hashlib
from typing import Dict, Any, List
from PIL import Image
from app.ml.interfaces import Predictor
from app.services.crop_service import CropConfigLoader
from app.core.config import settings

class DemoPredictor(Predictor):
    """
    Deterministic Demonstration Predictor used when ML_MODE = DEMO or real PyTorch model weights are unavailable.
    Explicitly tags predictions with "is_demo_mode": True.
    Does NOT fabricate real ML performance metrics.
    """

    def predict(self, image: Image.Image, crop_key: str = "tomato") -> Dict[str, Any]:
        start_time = time.time()

        # Fetch available classes dynamically from crop configuration
        crop_details = CropConfigLoader.get_crop_details(crop_key)
        if crop_details and "disease_classes" in crop_details:
            classes = [c["key"] for c in crop_details["disease_classes"]]
        else:
            classes = ["Healthy", "Early Blight", "Late Blight", "Leaf Spot"]

        # Deterministic class selection based on image dimensions & hash
        img_bytes = image.tobytes()
        img_hash = int(hashlib.md5(img_bytes).hexdigest(), 16)
        
        # Pick class deterministically
        predicted_index = img_hash % len(classes)
        predicted_class = classes[predicted_index]

        # Generate deterministic mock probabilities for demo purposes
        # Note: Confidences are mock baseline values for functional demonstration
        confidence_base = 0.65 + ((img_hash % 30) / 100.0) # 0.65 - 0.94
        confidence = round(confidence_base, 2)

        top_predictions: List[Dict[str, Any]] = []
        remaining_prob = 1.0 - confidence
        
        top_predictions.append({
            "class": predicted_class,
            "confidence": confidence
        })

        other_classes = [c for c in classes if c != predicted_class]
        if other_classes:
            share = remaining_prob / len(other_classes)
            for c in other_classes:
                top_predictions.append({
                    "class": c,
                    "confidence": round(share, 3)
                })

        inference_time = round((time.time() - start_time) * 1000, 2)
        needs_review = confidence < settings.CONFIDENCE_THRESHOLD

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "top_predictions": top_predictions,
            "model_version": "demo-v1",
            "inference_time_ms": inference_time,
            "is_demo_mode": True,
            "needs_expert_review": needs_review
        }

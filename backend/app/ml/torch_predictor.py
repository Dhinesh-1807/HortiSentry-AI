import os
import sys
import time
import logging
from typing import Dict, Any, List
from pathlib import Path
import torch
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.interfaces import Predictor
from app.core.config import settings
from ml.transforms import get_eval_transforms
from ml.model import HortiSentryMobileNetV3
from ml.checkpoint import load_checkpoint

logger = logging.getLogger(__name__)

class TorchPredictor(Predictor):
    """
    Production PyTorch Predictor loaded from exported artifact.
    Executes real inference, returning top-3 softmax probabilities and tagging is_demo_mode = False.
    """

    def __init__(self, artifact_path: str = None):
        if artifact_path is None:
            artifact_path = settings.MODEL_PATH
        self.artifact_path = Path(artifact_path)
        self.model = None
        self.classes: List[str] = ["Healthy", "Early_Blight", "Late_Blight", "Septoria_Leaf_Spot"]
        self.transform = None
        self.model_version = "tomato-v1"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_model()

    def _load_model(self):
        if not self.artifact_path.exists():
            raise FileNotFoundError(f"PyTorch model artifact not found at {self.artifact_path}")
        
        logger.info(f"Loading PyTorch model artifact from {self.artifact_path}")
        checkpoint = load_checkpoint(self.artifact_path, map_location="cpu")
        
        self.model_version = checkpoint.get("model_version", "tomato-v1")
        self.classes = checkpoint.get("classes", self.classes)
        image_size = checkpoint.get("image_size", 224)

        self.model = HortiSentryMobileNetV3(num_classes=len(self.classes), pretrained=False).to(self.device)
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()

        self.transform = get_eval_transforms(image_size=image_size)
        logger.info(f"Loaded TorchPredictor model version '{self.model_version}' with {len(self.classes)} classes on {self.device}.")

    def predict(self, image: Image.Image, crop_key: str = "tomato") -> Dict[str, Any]:
        if self.model is None or self.transform is None:
            raise RuntimeError("TorchPredictor model is not initialized.")

        start_time = time.time()
        
        # Ensure RGB PIL image
        pil_img = image.convert("RGB")
        tensor_img = self.transform(pil_img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor_img)
            probs = torch.softmax(outputs, dim=1).squeeze(0)

        inference_time_ms = round((time.time() - start_time) * 1000.0, 2)

        # Top-3 predictions
        k = min(3, len(self.classes))
        top_prob, top_indices = torch.topk(probs, k=k)

        top_predictions: List[Dict[str, Any]] = []
        for p, idx in zip(top_prob.tolist(), top_indices.tolist()):
            cls_name = self.classes[idx]
            # Map canonical name to user-friendly label if needed
            top_predictions.append({
                "class": cls_name,
                "confidence": round(p, 4)
            })

        predicted_class = self.classes[top_indices[0].item()]
        confidence = round(top_prob[0].item(), 4)

        needs_expert_review = confidence < settings.CONFIDENCE_THRESHOLD

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "top_predictions": top_predictions,
            "model_version": self.model_version,
            "inference_time_ms": inference_time_ms,
            "is_demo_mode": False,
            "needs_expert_review": needs_expert_review
        }

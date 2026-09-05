from abc import ABC, abstractmethod
from typing import Dict, Any, List
from PIL import Image

class ImagePreprocessor(ABC):
    @abstractmethod
    def preprocess(self, image: Image.Image) -> Any:
        """Preprocess PIL Image into model input format (e.g. Tensor or Array)."""
        pass

class ModelLoader(ABC):
    @abstractmethod
    def load_model(self, model_path: str) -> Any:
        """Load trained PyTorch / ONNX model weights."""
        pass

    @abstractmethod
    def is_model_available(self) -> bool:
        """Return True if real trained weights are loaded and active."""
        pass

class Predictor(ABC):
    @abstractmethod
    def predict(self, image: Image.Image, crop_key: str = "tomato") -> Dict[str, Any]:
        """
        Evaluate image and return standardized prediction dictionary:
        {
            "predicted_class": str,
            "confidence": float,
            "top_predictions": List[Dict[str, float]],
            "model_version": str,
            "inference_time_ms": float,
            "is_demo_mode": bool,
            "needs_expert_review": bool
        }
        """
        pass

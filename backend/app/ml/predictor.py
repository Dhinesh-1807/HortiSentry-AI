import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image

from app.ml.interfaces import Predictor
from app.ml.demo_predictor import DemoPredictor
from app.ml.vision_provider import (
    PyTorchTomatoVisionProvider,
    PyTorchPotatoVisionProvider,
    VisualSymptomAnalyzerProvider,
    VisionAnalysisResult
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class MLSafetyWrapper(Predictor):
    """
    ML Service Safety Wrapper supporting multi-crop trained vision providers (Tomato-v1, Potato-v1)
    and VisualSymptomAnalyzerProvider for non-model crops.
    """

    def __init__(self):
        self.demo_predictor = DemoPredictor()
        self.tomato_provider = None
        self.potato_provider = None
        self.visual_analyzer_provider = VisualSymptomAnalyzerProvider()
        self.real_model_available = False
        self._check_model_status()

    def _check_model_status(self):
        from app.ml.torch_predictor import TorchPredictor

        # Tomato Model Loading
        tomato_path = Path(settings.MODEL_PATH)
        if tomato_path.exists():
            try:
                tp_tomato = TorchPredictor(artifact_path=str(tomato_path))
                self.tomato_provider = PyTorchTomatoVisionProvider(torch_predictor=tp_tomato)
                logger.info(f"Real PyTorch Tomato model loaded successfully from {tomato_path}")
            except Exception as e:
                logger.error(f"Failed to load PyTorch Tomato model from {tomato_path}: {e}")
                self.tomato_provider = None
        else:
            self.tomato_provider = None

        # Potato Model Loading
        potato_path = Path(settings.POTATO_MODEL_PATH)
        if potato_path.exists():
            try:
                tp_potato = TorchPredictor(artifact_path=str(potato_path))
                self.potato_provider = PyTorchPotatoVisionProvider(torch_predictor=tp_potato)
                logger.info(f"Real PyTorch Potato model loaded successfully from {potato_path}")
            except Exception as e:
                logger.error(f"Failed to load PyTorch Potato model from {potato_path}: {e}")
                self.potato_provider = None
        else:
            self.potato_provider = None

        self.real_model_available = (self.tomato_provider is not None) or (self.potato_provider is not None)
        
        if settings.ML_MODE == "REAL":
            logger.info(f"ML Service operating in REAL MODE (Tomato: {'ACTIVE' if self.tomato_provider else 'INACTIVE'}, Potato: {'ACTIVE' if self.potato_provider else 'INACTIVE'})")
        else:
            logger.info("ML Service operating in DEMO MODE.")

    def reload_model(self):
        """Re-evaluate model status and reload real predictors if available."""
        self._check_model_status()

    @property
    def real_predictor(self):
        if self.tomato_provider:
            return self.tomato_provider.torch_predictor
        elif self.potato_provider:
            return self.potato_provider.torch_predictor
        return None

    def get_ml_mode(self) -> str:
        return "REAL" if self.real_model_available else "DEMO"

    def get_registered_models(self) -> Dict[str, Any]:
        return {
            "tomato": {
                "model_id": "tomato-v1",
                "status": "ACTIVE" if self.tomato_provider else "INACTIVE",
                "provider_type": "trained_model" if self.tomato_provider else "visual_assessment"
            },
            "potato": {
                "model_id": "potato-v1",
                "status": "ACTIVE" if self.potato_provider else "INACTIVE",
                "provider_type": "trained_model" if self.potato_provider else "visual_assessment"
            }
        }

    def predict(self, image: Image.Image, crop_key: str = "tomato") -> Dict[str, Any]:
        result = self.analyze_vision(image, crop_key=crop_key)
        is_demo = (settings.ML_MODE == "DEMO") or result.is_demo_mode
        return {
            "predicted_class": result.predicted_class,
            "confidence": result.confidence,
            "top_predictions": [
                {"class": c["class"], "confidence": c["visual_confidence"]}
                for c in result.disease_candidates
            ],
            "model_version": "demo-v1" if is_demo else result.model_version,
            "inference_time_ms": result.inference_time_ms,
            "is_demo_mode": is_demo,
            "needs_expert_review": result.confidence < settings.CONFIDENCE_THRESHOLD,
            "provider_type": result.provider_type
        }

    def analyze_vision(
        self,
        image: Image.Image,
        crop_key: str = "tomato",
        user_symptoms: Optional[List[str]] = None
    ) -> VisionAnalysisResult:
        crop_k = crop_key.lower()

        # Tomato trained model provider
        if crop_k == "tomato" and settings.ML_MODE == "REAL" and self.tomato_provider:
            try:
                return self.tomato_provider.analyze_image(image, crop_key=crop_k, user_symptoms=user_symptoms)
            except Exception as e:
                logger.error(f"Error in PyTorch Tomato provider: {e}. Falling back to visual assessment provider.")

        # Potato trained model provider
        if crop_k == "potato" and settings.ML_MODE == "REAL" and self.potato_provider:
            try:
                return self.potato_provider.analyze_image(image, crop_key=crop_k, user_symptoms=user_symptoms)
            except Exception as e:
                logger.error(f"Error in PyTorch Potato provider: {e}. Falling back to visual assessment provider.")

        # Multi-crop visual symptom analyzer provider
        return self.visual_analyzer_provider.analyze_image(image, crop_key=crop_k, user_symptoms=user_symptoms)

ml_service = MLSafetyWrapper()

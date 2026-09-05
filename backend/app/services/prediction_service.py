import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image
from sqlalchemy.orm import Session

from app.ml.predictor import ml_service
from app.models.models import Prediction, ModelVersion, Observation
from app.core.config import settings, BASE_DIR

logger = logging.getLogger(__name__)

def load_escalation_config() -> dict:
    config_path = BASE_DIR / "config" / "escalation.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {
        "confidence_thresholds": {"high_confidence": 0.85, "review_recommended": 0.60, "low_confidence": 0.60},
        "risk_levels": {
            "high_risk_diseases": ["Late_Blight", "Bacterial_Spot", "Anthracnose", "Wilt", "Fruit_Rot"],
            "medium_risk_diseases": ["Early_Blight", "Septoria_Leaf_Spot", "Target_Spot", "Leaf_Spot"],
            "low_risk_diseases": ["Healthy", "Powdery_Mildew"]
        }
    }

class PredictionService:
    """
    Service responsible for orchestrating ML predictions, determining condition names,
    calculating disease risk levels, and recommending actions.
    """

    @classmethod
    def determine_risk_and_action(
        cls,
        crop_key: str,
        predicted_class: str,
        confidence: float
    ) -> Tuple[str, str, str, bool]:
        config = load_escalation_config()
        risk_cfg = config.get("risk_levels", {})
        high_risk_list = risk_cfg.get("high_risk_diseases", [])
        medium_risk_list = risk_cfg.get("medium_risk_diseases", [])

        # 1. Human-friendly condition title (Section 13 requirement: "Possible Tomato Leaf Spot")
        formatted_class = predicted_class.replace("_", " ").replace("Tomato", "").replace("Potato", "").strip()
        if predicted_class.lower() in ["healthy"]:
            predicted_condition = f"Possible Healthy {crop_key.capitalize()} Foliage"
            base_risk = "LOW"
        else:
            predicted_condition = f"Possible {crop_key.capitalize()} {formatted_class}"
            base_risk = "MEDIUM"

        # Check high risk diseases
        for hr in high_risk_list:
            if hr.lower() in predicted_class.lower():
                base_risk = "HIGH"
                break

        # Check medium risk diseases if not already high
        if base_risk != "HIGH":
            for mr in medium_risk_list:
                if mr.lower() in predicted_class.lower():
                    base_risk = "MEDIUM"
                    break

        # 2. Recommended action & Expert review flag
        needs_expert_review = False
        if base_risk == "HIGH":
            recommended_action = "High-risk symptom pattern. Immediate quarantine and expert review required."
            needs_expert_review = True
        elif confidence < 0.60:
            recommended_action = "Low AI observation confidence. Expert agricultural review required."
            needs_expert_review = True
        elif confidence < 0.85:
            recommended_action = "Moderate observation confidence. Monitor closely and expert review recommended."
            needs_expert_review = True
        else:
            if base_risk == "LOW":
                recommended_action = "Foliage appears normal. Continue standard monitoring and maintenance."
                needs_expert_review = False
            else:
                recommended_action = "Observation recorded with high AI confidence. Routine monitoring recommended."
                needs_expert_review = False

        return predicted_condition, base_risk, recommended_action, needs_expert_review

    @classmethod
    def run_prediction(
        cls, 
        db: Session, 
        observation_id: str, 
        image: Image.Image, 
        crop_key: str = "tomato"
    ) -> Prediction:
        
        # 1. Run prediction via ML Safety Wrapper
        pred_result = ml_service.predict(image, crop_key=crop_key)

        # 2. Lookup or reference model version
        version_name = pred_result.get("model_version", "tomato-v1")
        model_version_rec = db.query(ModelVersion).filter(ModelVersion.version_name == version_name).first()
        model_version_id = model_version_rec.id if model_version_rec else None

        # 3. Determine condition description, risk level, and recommendation
        predicted_condition, risk_level, recommended_action, needs_expert_review = cls.determine_risk_and_action(
            crop_key=crop_key,
            predicted_class=pred_result["predicted_class"],
            confidence=pred_result["confidence"]
        )

        # 4. Create Prediction DB record
        prediction = Prediction(
            observation_id=observation_id,
            model_version_id=model_version_id,
            model_name="HortiSentry-MobileNet",
            predicted_class=pred_result["predicted_class"],
            predicted_condition=predicted_condition,
            confidence=pred_result["confidence"],
            risk_level=risk_level,
            recommended_action=recommended_action,
            needs_expert_review=needs_expert_review,
            top_predictions=pred_result["top_predictions"],
            inference_time_ms=pred_result["inference_time_ms"],
            is_demo_mode=pred_result["is_demo_mode"]
        )

        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        logger.info(
            f"Generated prediction for Observation {observation_id}: "
            f"Condition='{prediction.predicted_condition}', Conf={prediction.confidence:.2f}, "
            f"Risk={prediction.risk_level}, NeedsReview={prediction.needs_expert_review}"
        )
        return prediction

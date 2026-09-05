import yaml
import logging
from datetime import datetime
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.models.models import Observation, Escalation, ExpertReview, Prediction
from app.core.config import settings, BASE_DIR
from app.core.constants import EscalationReason, EscalationStatus, ObservationStatus, ReviewStatus, AuditAction
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

def load_escalation_config() -> dict:
    config_path = BASE_DIR / "config" / "escalation.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {
        "confidence_thresholds": {"high_confidence": 0.85, "review_recommended": 0.60, "low_confidence": 0.60},
        "risk_levels": {"high_risk_diseases": ["Late_Blight", "Bacterial_Spot", "Anthracnose", "Wilt", "Fruit_Rot"]},
        "quality_escalation": {"escalate_on_blur": True, "escalate_on_exposure": True, "escalate_on_unknown_symptom": True}
    }

class EscalationService:
    """
    Escalation Engine Service. Evaluates AI confidence scores, disease risk levels,
    and image quality metadata to determine expert review routing based on config/escalation.yaml.
    """

    @classmethod
    def evaluate_and_escalate(
        cls,
        db: Session,
        observation: Observation,
        prediction: Prediction,
        quality_data: dict
    ) -> Tuple[bool, Optional[Escalation]]:
        
        # Check existing escalation to prevent duplicate records
        existing = db.query(Escalation).filter(Escalation.observation_id == observation.id).first()
        if existing:
            return (existing.status != EscalationStatus.RESOLVED, existing)

        config = load_escalation_config()
        thresholds = config.get("confidence_thresholds", {})
        high_conf = thresholds.get("high_confidence", 0.85)
        low_conf = thresholds.get("low_confidence", 0.60)
        high_risk_diseases = config.get("risk_levels", {}).get("high_risk_diseases", [])

        escalation_required = False
        reason = None
        escalation_status = EscalationStatus.SUBMITTED

        # Rule 1: Poor image quality trigger
        if not quality_data.get("is_valid", True) or quality_data.get("is_blur_detected", False) or quality_data.get("is_exposure_issue", False):
            escalation_required = True
            reason = EscalationReason.POOR_IMAGE_QUALITY

        # Rule 2: Unknown symptom trigger
        elif observation.symptoms and any("unknown" in str(s).lower() for s in observation.symptoms):
            escalation_required = True
            reason = EscalationReason.UNKNOWN_CLASS

        # Rule 3: High-risk disease condition trigger regardless of confidence
        elif prediction.risk_level == "HIGH" or any(hr.lower() in prediction.predicted_class.lower() for hr in high_risk_diseases):
            escalation_required = True
            reason = EscalationReason.HIGH_RISK_CONDITION

        # Rule 4: Low AI confidence threshold trigger (< 0.60)
        elif prediction.confidence < low_conf:
            escalation_required = True
            reason = EscalationReason.LOW_CONFIDENCE

        # Rule 5: Medium AI confidence threshold trigger (0.60 <= conf < 0.85)
        elif prediction.confidence < high_conf:
            escalation_required = True
            reason = EscalationReason.LOW_CONFIDENCE
            escalation_status = EscalationStatus.RECOMMENDED

        # Rule 6: Normal observation (conf >= 0.85 and low risk)
        else:
            escalation_required = False

        if escalation_required:
            now = datetime.utcnow()
            observation.escalation_time = now
            escalation = cls._create_escalation_and_queue_review(
                db=db,
                observation=observation,
                reason=reason,
                escalation_status=escalation_status
            )
            observation.status = ObservationStatus.EXPERT_REVIEW_REQUIRED
            observation.risk_level = prediction.risk_level
            db.commit()

            AuditService.record(
                db=db,
                action=AuditAction.CASE_ESCALATED,
                user_id=observation.user_id,
                entity_type="Observation",
                entity_id=observation.id,
                details={"reason": reason, "status": escalation_status, "confidence": prediction.confidence}
            )

            # In-App Notification
            if observation.user_id:
                NotificationService.create_notification(
                    db=db,
                    user_id=observation.user_id,
                    observation_id=observation.id,
                    title="Observation Escalated for Expert Review",
                    message=f"AI-assisted analysis ({prediction.predicted_condition}, {int(prediction.confidence * 100)}% confidence) requires agricultural expert review."
                )

            logger.info(f"Observation {observation.id} automatically escalated to Expert Queue. Reason: {reason}")
            return (True, escalation)
        else:
            observation.status = ObservationStatus.COMPLETED
            observation.risk_level = prediction.risk_level
            db.commit()

            if observation.user_id:
                NotificationService.create_notification(
                    db=db,
                    user_id=observation.user_id,
                    observation_id=observation.id,
                    title="AI Observation Completed",
                    message=f"AI-assisted observation recorded: {prediction.predicted_condition} with {int(prediction.confidence * 100)}% confidence. Routine monitoring recommended."
                )

            return (False, None)

    @classmethod
    def manual_farmer_escalate(
        cls,
        db: Session,
        observation: Observation,
        user_notes: Optional[str] = None
    ) -> Escalation:
        """Allows farmers to manually request expert review at any time."""
        existing = db.query(Escalation).filter(Escalation.observation_id == observation.id).first()
        if existing:
            existing.reason = EscalationReason.MANUAL_FARMER_REQUEST
            if existing.status == EscalationStatus.RESOLVED:
                existing.status = EscalationStatus.SUBMITTED
            observation.status = ObservationStatus.EXPERT_REVIEW_REQUIRED
            
            review = db.query(ExpertReview).filter(ExpertReview.observation_id == observation.id).first()
            if not review:
                review = ExpertReview(observation_id=observation.id, review_status=ReviewStatus.PENDING)
                db.add(review)
            elif review.review_status == ReviewStatus.COMPLETED:
                review.review_status = ReviewStatus.PENDING

            if user_notes:
                if observation.notes:
                    observation.notes += f" | Escalation Note: {user_notes}"
                else:
                    observation.notes = f"Escalation Note: {user_notes}"

            observation.escalation_time = datetime.utcnow()
            db.commit()
            return existing

        now = datetime.utcnow()
        observation.escalation_time = now
        escalation = cls._create_escalation_and_queue_review(
            db=db,
            observation=observation,
            reason=EscalationReason.MANUAL_FARMER_REQUEST,
            escalation_status=EscalationStatus.SUBMITTED
        )
        observation.status = ObservationStatus.EXPERT_REVIEW_REQUIRED

        if user_notes:
            if observation.notes:
                observation.notes += f" | Escalation Note: {user_notes}"
            else:
                observation.notes = f"Escalation Note: {user_notes}"

        db.commit()

        AuditService.record(
            db=db,
            action=AuditAction.CASE_ESCALATED,
            user_id=observation.user_id,
            entity_type="Observation",
            entity_id=observation.id,
            details={"reason": "MANUAL_FARMER_REQUEST"}
        )

        return escalation

    @classmethod
    def _create_escalation_and_queue_review(
        cls,
        db: Session,
        observation: Observation,
        reason: str,
        escalation_status: str
    ) -> Escalation:
        escalation = Escalation(
            observation_id=observation.id,
            reason=reason,
            status=escalation_status,
            created_at=datetime.utcnow()
        )
        db.add(escalation)

        review = db.query(ExpertReview).filter(ExpertReview.observation_id == observation.id).first()
        if not review:
            review = ExpertReview(
                observation_id=observation.id,
                review_status=ReviewStatus.PENDING,
                started_at=None,
                completed_at=None
            )
            db.add(review)

        return escalation

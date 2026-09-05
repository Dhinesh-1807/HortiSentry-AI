import os
import io
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from PIL import Image
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.models import Observation, ObservationImage, Crop, Prediction, Escalation, ExpertReview
from app.services.crop_service import CropConfigLoader
from app.services.media_storage_service import media_storage_service
from app.services.image_quality_service import ImageQualityService
from app.services.prediction_service import PredictionService
from app.services.escalation_service import EscalationService
from app.services.audit_service import AuditService
from app.core.constants import ObservationStatus, AuditAction

logger = logging.getLogger(__name__)

class ObservationService:
    """
    Observation Business Logic Service. Orchestrates observation creation, image ingestion,
    quality auditing, multi-class prediction, auto-escalation, and retrieval.
    """

    @classmethod
    def create_observation(
        cls,
        db: Session,
        crop_id: str,
        crop_stage: str,
        symptoms: List[str],
        village: str,
        district: str,
        state: str,
        file_bytes: bytes,
        original_filename: str,
        notes: Optional[str] = None,
        variety: Optional[str] = None,
        farmer_confidence: Optional[float] = 0.7,
        symptom_observed_at: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:

        # 1. Validate Crop Selection (Mandatory)
        if not crop_id or not str(crop_id).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crop selection is mandatory. Please select a valid target crop."
            )

        crop = db.query(Crop).filter(Crop.id == crop_id.lower()).first()
        if not crop:
            crop = db.query(Crop).filter(Crop.key == crop_id.lower()).first()

        if not crop:
            crop_meta = CropConfigLoader.get_crop_details(crop_id.lower())
            if crop_meta and crop_meta.get("is_active", True):
                crop = Crop(
                    key=crop_meta["key"],
                    display_name=crop_meta["display_name"],
                    description=crop_meta.get("description", ""),
                    is_active=True
                )
                db.add(crop)
                db.commit()
                db.refresh(crop)

        if not crop or not crop.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or inactive crop ID/key '{crop_id}'."
            )

        # 2. Validate Crop Stage & Symptoms against dynamic YAML configuration
        crop_config = CropConfigLoader.get_crop_details(crop.key)
        if crop_config:
            valid_stages = [s["key"].upper() for s in crop_config.get("stages", [])]
            if crop_stage.upper() not in valid_stages:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid crop stage '{crop_stage}'. Allowed: {', '.join(valid_stages)}"
                )

        if not symptoms or len(symptoms) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one symptom must be selected."
            )

        # Edge Case 6: Duplicate observation detection
        ten_mins_ago = datetime.utcnow() - timedelta(minutes=10)
        recent_dup = db.query(Observation).filter(
            Observation.crop_id == crop.id,
            Observation.crop_stage == crop_stage.upper(),
            Observation.location_village == village.strip(),
            Observation.created_at >= ten_mins_ago
        )
        if user_id:
            recent_dup = recent_dup.filter(Observation.user_id == user_id)
        if recent_dup.first():
            dup_note = "[System: Possible duplicate observation submitted within 10 minutes]"
            notes = f"{notes} | {dup_note}" if notes else dup_note

        # 3. Store Image via MediaStorageService
        saved_path, unique_name, size_bytes, width, height, mime_type = media_storage_service.save_image(
            file_bytes, original_filename
        )

        # 4. Open PIL Image for quality analysis & prediction
        pil_image = media_storage_service.validate_file(file_bytes, original_filename)
        quality_data = ImageQualityService.analyze_quality(pil_image)

        # 5. Create Observation DB Record
        now = datetime.utcnow()
        first_symptom_ts = symptom_observed_at or now
        observation = Observation(
            user_id=user_id,
            crop_id=crop.id,
            crop_stage=crop_stage.upper(),
            variety=variety.strip() if variety else None,
            farmer_confidence=float(farmer_confidence) if farmer_confidence is not None else 0.7,
            symptoms=symptoms,
            location_village=village.strip(),
            location_district=district.strip(),
            location_state=state.strip(),
            notes=notes.strip() if notes else None,
            symptom_observed_at=symptom_observed_at,
            first_symptom_time=first_symptom_ts,
            submitted_at=now,
            ai_analysis_time=now,
            status=ObservationStatus.SUBMITTED
        )
        db.add(observation)
        db.flush()

        # 6. Save ObservationImage DB Record
        obs_image = ObservationImage(
            observation_id=observation.id,
            image_path=saved_path,
            file_name=unique_name,
            file_size_bytes=size_bytes,
            width=width,
            height=height,
            mime_type=mime_type,
            is_blur_detected=quality_data["is_blur_detected"],
            is_exposure_issue=quality_data["is_exposure_issue"],
            blur_score=quality_data["blur_score"]
        )
        db.add(obs_image)
        db.flush()

        # 7. Execute AI Prediction
        prediction = PredictionService.run_prediction(
            db=db,
            observation_id=observation.id,
            image=pil_image,
            crop_key=crop.key
        )
        observation.risk_level = prediction.risk_level

        # 8. Evaluate Escalation Engine
        is_escalated, escalation = EscalationService.evaluate_and_escalate(
            db=db,
            observation=observation,
            prediction=prediction,
            quality_data=quality_data
        )

        # 9. Trigger AI Evidence Review
        ai_review_data = None
        try:
            from app.services.ai_review_service import AIReviewService
            ai_review_data = AIReviewService.create_or_get_ai_review(
                db=db,
                observation_id=observation.id
            )
        except Exception as e:
            logger.error(f"Error auto-triggering AI review for observation {observation.id}: {e}")

        db.commit()
        db.refresh(observation)

        AuditService.record(
            db=db,
            action=AuditAction.OBSERVATION_CREATED,
            user_id=user_id,
            entity_type="Observation",
            entity_id=observation.id,
            details={"crop": crop.display_name, "stage": crop_stage, "risk": prediction.risk_level}
        )

        return {
            "observation_id": observation.id,
            "status": observation.status,
            "crop": crop.display_name,
            "crop_stage": observation.crop_stage,
            "variety": observation.variety,
            "farmer_confidence": observation.farmer_confidence,
            "risk_level": observation.risk_level,
            "submitted_at": observation.submitted_at,
            "first_symptom_time": observation.first_symptom_time,
            "image": {
                "id": obs_image.id,
                "file_name": obs_image.file_name,
                "width": obs_image.width,
                "height": obs_image.height
            },
            "quality_analysis": quality_data,
            "prediction": {
                "id": prediction.id,
                "predicted_class": prediction.predicted_class,
                "predicted_condition": prediction.predicted_condition,
                "confidence": prediction.confidence,
                "risk_level": prediction.risk_level,
                "recommended_action": prediction.recommended_action,
                "needs_expert_review": prediction.needs_expert_review,
                "top_predictions": prediction.top_predictions,
                "model_version": prediction.model_version.version_name if prediction.model_version else "demo-v1",
                "inference_time_ms": prediction.inference_time_ms,
                "is_demo_mode": prediction.is_demo_mode
            },
            "ai_review": ai_review_data,
            "escalation": {
                "is_escalated": is_escalated,
                "reason": escalation.reason if escalation else None,
                "status": escalation.status if escalation else "NOT_REQUIRED"
            }
        }

    @classmethod
    def analyze_observation(cls, db: Session, observation_id: str) -> Dict[str, Any]:
        """Re-runs AI inference on an existing observation."""
        observation = cls.get_observation_by_id(db, observation_id)
        if not observation.images:
            raise HTTPException(status_code=400, detail="Observation has no uploaded image to analyze.")
        obs_img = observation.images[0]
        
        try:
            pil_image = Image.open(obs_img.image_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read stored observation image: {e}")

        quality_data = ImageQualityService.analyze_quality(pil_image)
        prediction = PredictionService.run_prediction(
            db=db,
            observation_id=observation.id,
            image=pil_image,
            crop_key=observation.crop.key if observation.crop else "tomato"
        )
        observation.ai_analysis_time = datetime.utcnow()
        observation.risk_level = prediction.risk_level

        is_escalated, escalation = EscalationService.evaluate_and_escalate(
            db=db,
            observation=observation,
            prediction=prediction,
            quality_data=quality_data
        )
        db.commit()

        AuditService.record(
            db=db,
            action=AuditAction.AI_ANALYSIS_PERFORMED,
            user_id=observation.user_id,
            entity_type="Observation",
            entity_id=observation.id,
            details={"condition": prediction.predicted_condition, "confidence": prediction.confidence}
        )

        return {
            "observation_id": observation.id,
            "status": observation.status,
            "prediction": {
                "id": prediction.id,
                "predicted_class": prediction.predicted_class,
                "predicted_condition": prediction.predicted_condition,
                "confidence": prediction.confidence,
                "risk_level": prediction.risk_level,
                "recommended_action": prediction.recommended_action,
                "needs_expert_review": prediction.needs_expert_review,
                "is_demo_mode": prediction.is_demo_mode
            },
            "is_escalated": is_escalated,
            "escalation_reason": escalation.reason if escalation else None
        }

    @classmethod
    def get_observation_by_id(cls, db: Session, observation_id: str) -> Observation:
        observation = db.query(Observation).filter(Observation.id == observation_id).first()
        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Observation with ID '{observation_id}' not found."
            )
        return observation

    @classmethod
    def list_observations(
        cls,
        db: Session,
        crop_id: Optional[str] = None,
        obs_status: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Observation]:
        query = db.query(Observation)
        if crop_id:
            query = query.filter(Observation.crop_id == crop_id)
        if obs_status:
            query = query.filter(Observation.status == obs_status.upper())
        if user_id:
            query = query.filter(Observation.user_id == user_id)

        return query.order_by(Observation.created_at.desc()).offset(offset).limit(limit).all()

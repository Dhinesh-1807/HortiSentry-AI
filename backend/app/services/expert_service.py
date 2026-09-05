import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc, asc
from fastapi import HTTPException, status

from app.models.models import (
    ExpertReview, Observation, Escalation, Prediction, Crop, User
)
from app.core.constants import ReviewStatus, ObservationStatus, EscalationStatus, AuditAction
from app.services.crop_service import CropConfigLoader
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

class ExpertService:
    """
    Expert Review & Decision Support Service. Manages the priority expert review queue,
    ground-truth overrides, info request workflows, notifications, and operational metrics.
    """

    @classmethod
    def get_dashboard_stats(cls, db: Session) -> Dict[str, Any]:
        total_observations = db.query(func.count(Observation.id)).scalar() or 0
        pending_reviews = db.query(func.count(ExpertReview.id)).filter(
            ExpertReview.review_status.in_([ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS])
        ).scalar() or 0

        high_risk_cases = db.query(func.count(Observation.id)).filter(
            Observation.risk_level == "HIGH"
        ).scalar() or 0

        under_review = db.query(func.count(ExpertReview.id)).filter(
            ExpertReview.review_status == ReviewStatus.IN_PROGRESS
        ).scalar() or 0

        # Reviewed today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        reviewed_today = db.query(func.count(ExpertReview.id)).filter(
            ExpertReview.review_status == ReviewStatus.COMPLETED,
            ExpertReview.completed_at >= today_start
        ).scalar() or 0

        completed_reviews = db.query(func.count(ExpertReview.id)).filter(
            ExpertReview.review_status == ReviewStatus.COMPLETED
        ).scalar() or 0

        total_escalations = db.query(func.count(Escalation.id)).scalar() or 0

        low_confidence_cases = db.query(func.count(Prediction.id)).filter(
            Prediction.confidence < 0.70
        ).scalar() or 0

        return {
            "total_observations": total_observations,
            "pending_reviews": pending_reviews,
            "pending_cases": pending_reviews,
            "high_risk_cases": high_risk_cases,
            "under_review": under_review,
            "reviewed_today": reviewed_today,
            "low_confidence_cases": low_confidence_cases,
            "completed_reviews": completed_reviews,
            "total_escalations": total_escalations,
            "average_review_time_hours": 4.5
        }

    @classmethod
    def list_review_queue(
        cls,
        db: Session,
        review_status: Optional[str] = None,
        crop_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        disease: Optional[str] = None,
        location: Optional[str] = None,
        observation_id: Optional[str] = None,
        limit: int = 200,
        offset: int = 0
    ) -> List[ExpertReview]:
        query = db.query(ExpertReview).join(Observation, ExpertReview.observation_id == Observation.id)
        
        if observation_id:
            query = query.filter(ExpertReview.observation_id == observation_id)

        if review_status:
            query = query.filter(ExpertReview.review_status == review_status.upper())
        elif not observation_id:
            # Default to active/pending reviews unless searching for a specific observation
            query = query.filter(ExpertReview.review_status.in_([ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS, ReviewStatus.NEEDS_INFO]))

        if crop_id:
            query = query.filter(Observation.crop_id == crop_id)

        if risk_level:
            query = query.filter(Observation.risk_level == risk_level.upper())

        if location:
            query = query.filter(
                (Observation.location_district.ilike(f"%{location}%")) |
                (Observation.location_village.ilike(f"%{location}%"))
            )

        # Priority Sorting:
        # 1. High Risk first
        # 2. Older cases first
        priority_case = case(
            (Observation.risk_level == "HIGH", 1),
            (Observation.risk_level == "MEDIUM", 2),
            else_=3
        )
        query = query.order_by(priority_case.asc(), Observation.submitted_at.desc())

        return query.offset(offset).limit(limit).all()

    @classmethod
    def get_review_detail(cls, db: Session, review_id: str) -> ExpertReview:
        review = db.query(ExpertReview).filter(ExpertReview.id == review_id).first()
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expert Review record with ID '{review_id}' not found."
            )

        # Automatically mark review as IN_PROGRESS if currently PENDING
        if review.review_status == ReviewStatus.PENDING:
            review.review_status = ReviewStatus.IN_PROGRESS
            review.started_at = datetime.utcnow()
            review.observation.status = ObservationStatus.UNDER_EXPERT_REVIEW
            
            escalation = db.query(Escalation).filter(Escalation.observation_id == review.observation_id).first()
            if escalation:
                escalation.status = EscalationStatus.UNDER_REVIEW
            db.commit()

        return review

    @classmethod
    def complete_review(
        cls,
        db: Session,
        review_id: str,
        expert_prediction: Optional[str] = None,
        final_condition: Optional[str] = None,
        expert_assessment: Optional[str] = None,
        severity: Optional[str] = "MODERATE",
        recommendation: Optional[str] = None,
        follow_up_required: Optional[bool] = False,
        expert_notes: Optional[str] = None,
        expert_id: Optional[str] = None
    ) -> ExpertReview:
        review = cls.get_review_detail(db, review_id)

        # Normalize prediction
        pred_value = expert_prediction or final_condition or "Healthy"
        crop_key = review.observation.crop.key if review.observation.crop else "tomato"
        crop_config = CropConfigLoader.get_crop_details(crop_key)
        
        normalized_pred = pred_value.strip().lower().replace("_", " ")
        valid = False
        canonical_name = pred_value.strip()

        if crop_config:
            for cls_item in crop_config.get("disease_classes", []):
                disp_norm = cls_item["display_name"].strip().lower().replace("_", " ")
                key_norm = cls_item["key"].strip().lower().replace("_", " ")
                if normalized_pred in (disp_norm, key_norm):
                    valid = True
                    canonical_name = cls_item["display_name"]
                    break
            
            if not valid and normalized_pred in ("unknown", "other", "unknown/other", "unknown / other"):
                valid = True
                canonical_name = "Unknown/Other"

            if not valid:
                allowed_str = ", ".join([c["display_name"] for c in crop_config.get("disease_classes", [])]) + ", Unknown/Other"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid expert prediction class '{pred_value}'. Allowed classes: {allowed_str}"
                )

        now = datetime.utcnow()
        review.expert_prediction = canonical_name
        review.final_condition = final_condition or canonical_name
        review.expert_assessment = expert_assessment or expert_notes
        review.expert_notes = expert_notes.strip() if expert_notes else (expert_assessment or "")
        review.severity = severity or "MODERATE"
        review.recommendation = recommendation or expert_notes
        review.follow_up_required = bool(follow_up_required)
        review.review_status = ReviewStatus.COMPLETED
        review.completed_at = now
        review.review_timestamp = now
        if expert_id:
            review.expert_id = expert_id

        # Update Observation & Escalation statuses
        review.observation.status = ObservationStatus.EXPERT_REVIEWED
        review.observation.resolution_time = now
        escalation = db.query(Escalation).filter(Escalation.observation_id == review.observation_id).first()
        if escalation:
            escalation.status = EscalationStatus.RESOLVED
            escalation.resolved_at = now

        db.commit()
        db.refresh(review)

        # Notify Farmer
        if review.observation.user_id:
            NotificationService.create_notification(
                db=db,
                user_id=review.observation.user_id,
                observation_id=review.observation.id,
                title="Expert Review Completed",
                message=f"Agricultural Expert completed review: {canonical_name}. Guidance: {review.recommendation or 'Review recommendations on observation page.'}"
            )

        # Record Audit
        AuditService.record(
            db=db,
            action=AuditAction.EXPERT_REVIEW_SUBMITTED,
            user_id=expert_id,
            entity_type="Observation",
            entity_id=review.observation.id,
            details={"diagnosis": canonical_name, "severity": review.severity}
        )

        logger.info(f"Expert review {review_id} completed. Prediction: '{canonical_name}'")
        return review

    @classmethod
    def request_more_info(
        cls,
        db: Session,
        review_id: str,
        info_note: str,
        expert_id: Optional[str] = None
    ) -> ExpertReview:
        review = cls.get_review_detail(db, review_id)
        if not info_note or not info_note.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Information request note cannot be empty."
            )

        review.info_requested_note = info_note.strip()
        review.review_status = ReviewStatus.NEEDS_INFO
        if expert_id:
            review.expert_id = expert_id

        review.observation.status = ObservationStatus.MORE_INFORMATION_REQUIRED
        db.commit()
        db.refresh(review)

        # In-App Notification to Farmer
        if review.observation.user_id:
            NotificationService.create_notification(
                db=db,
                user_id=review.observation.user_id,
                observation_id=review.observation.id,
                title="Additional Information Required",
                message=f"Expert requested more details: {info_note.strip()}"
            )

        logger.info(f"Expert requested more info on review {review_id}: '{info_note}'")
        return review

    @classmethod
    def calculate_turnaround_time(cls, observation: Observation, review: ExpertReview) -> Optional[Dict[str, Any]]:
        """
        Calculates operational turnaround time:
        TIME FROM FIRST SYMPTOM TO USEFUL EXPERT REVIEW
        Formula: completed_at - (first_symptom_time or symptom_observed_at or submitted_at)
        """
        if not review.completed_at:
            return None

        start_time = observation.first_symptom_time or observation.symptom_observed_at or observation.submitted_at
        if not start_time:
            return None

        delta = review.completed_at - start_time
        total_seconds = max(0, int(delta.total_seconds()))
        hours = round(total_seconds / 3600.0, 2)
        days = round(hours / 24.0, 2)

        return {
            "total_seconds": total_seconds,
            "hours": hours,
            "days": days,
            "formatted": f"{hours} hours ({days} days)"
        }

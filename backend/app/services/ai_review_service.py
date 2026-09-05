import os
import logging
from typing import Dict, Any, Optional, List
from PIL import Image
from sqlalchemy.orm import Session

from app.models.models import Observation, AIReview, ReviewEvidence, Escalation
from app.evidence.service import EvidenceEngineService
from app.evidence.models import AIReviewOutput
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIReviewService:
    """Service handling database persistence and expert escalation triggers for AI Evidence Reviews."""

    @classmethod
    def create_or_get_ai_review(
        cls,
        db: Session,
        observation_id: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        obs = db.query(Observation).filter(Observation.id == observation_id).first()
        if not obs:
            raise ValueError(f"Observation with ID '{observation_id}' not found.")

        # Check existing AI review
        if not force_refresh:
            existing = db.query(AIReview).filter(AIReview.observation_id == observation_id).order_by(AIReview.created_at.desc()).first()
            if existing:
                return cls._format_db_ai_review(db, existing)

        # Load image if available
        image = None
        if obs.images:
            img_record = obs.images[0]
            if os.path.exists(img_record.image_path):
                try:
                    image = Image.open(img_record.image_path).convert("RGB")
                except Exception as e:
                    logger.error(f"Error reading observation image at {img_record.image_path}: {e}")

        # Crop key
        crop_key = obs.crop.key if obs.crop else "tomato"

        # Generate Evidence Review
        ai_output: AIReviewOutput = EvidenceEngineService.generate_ai_evidence_review(
            image=image,
            crop=crop_key,
            user_symptoms=obs.symptoms or []
        )

        # Save AIReview to DB
        db_review = AIReview(
            observation_id=observation_id,
            crop_key=crop_key,
            summary=ai_output.observation_summary,
            primary_candidate=ai_output.primary_candidate,
            vision_confidence=ai_output.vision_confidence,
            evidence_confidence=ai_output.evidence_confidence,
            overall_confidence=ai_output.overall_confidence,
            severity=ai_output.severity_estimate,
            recommended_actions=ai_output.recommended_immediate_actions,
            prevention_monitoring=ai_output.prevention_monitoring,
            what_to_watch=ai_output.what_to_watch_next,
            evidence_is_mixed=ai_output.evidence_is_mixed,
            conflict_notes=ai_output.conflict_notes,
            is_demo_mode=(settings.ML_MODE == "DEMO"),
            provider_info=f"EvidenceEngine-v1 ({crop_key})"
        )
        db.add(db_review)
        db.flush()

        # Save ReviewEvidence items
        for ev in ai_output.sources_used:
            db_ev = ReviewEvidence(
                ai_review_id=db_review.id,
                source_name=ev.source_name,
                source_url=ev.url,
                title=ev.title,
                evidence_text=ev.evidence_text,
                relevance_score=ev.relevance_score,
                authority_tier=ev.authority_tier
            )
            db.add(db_ev)

        # Expert Escalation Trigger Check
        needs_escalation = (
            ai_output.overall_confidence < settings.CONFIDENCE_THRESHOLD or
            ai_output.evidence_is_mixed or
            ai_output.severity_estimate.upper() == "HIGH"
        )

        if needs_escalation:
            # Check existing escalation
            existing_esc = db.query(Escalation).filter(Escalation.observation_id == observation_id).first()
            if not existing_esc:
                reason = "LOW_CONFIDENCE" if ai_output.overall_confidence < settings.CONFIDENCE_THRESHOLD else "MIXED_EVIDENCE"
                esc = Escalation(
                    observation_id=observation_id,
                    reason=reason,
                    status="SUBMITTED"
                )
                db.add(esc)
                obs.status = "PENDING_REVIEW"

                from app.models.models import ExpertReview
                from app.core.constants import ReviewStatus
                existing_rev = db.query(ExpertReview).filter(ExpertReview.observation_id == observation_id).first()
                if not existing_rev:
                    db.add(ExpertReview(observation_id=observation_id, review_status=ReviewStatus.PENDING))

                logger.info(f"Triggered escalation for observation {observation_id} (Reason: {reason})")

        db.commit()
        db.refresh(db_review)
        return cls._format_db_ai_review(db, db_review)

    @classmethod
    def get_ai_review_by_obs_id(cls, db: Session, observation_id: str) -> Optional[Dict[str, Any]]:
        review = db.query(AIReview).filter(AIReview.observation_id == observation_id).order_by(AIReview.created_at.desc()).first()
        if not review:
            return None
        return cls._format_db_ai_review(db, review)

    @classmethod
    def get_ai_review_sources(cls, db: Session, observation_id: str) -> List[Dict[str, Any]]:
        review = db.query(AIReview).filter(AIReview.observation_id == observation_id).order_by(AIReview.created_at.desc()).first()
        if not review:
            return []
        sources = db.query(ReviewEvidence).filter(ReviewEvidence.ai_review_id == review.id).all()
        return [
            {
                "id": s.id,
                "source_name": s.source_name,
                "source_url": s.source_url,
                "title": s.title,
                "evidence_text": s.evidence_text,
                "relevance_score": s.relevance_score,
                "authority_tier": s.authority_tier
            }
            for s in sources
        ]

    @classmethod
    def _format_db_ai_review(cls, db: Session, review: AIReview) -> Dict[str, Any]:
        sources = db.query(ReviewEvidence).filter(ReviewEvidence.ai_review_id == review.id).all()
        return {
            "id": review.id,
            "observation_id": review.observation_id,
            "crop_key": review.crop_key,
            "observation_summary": review.summary,
            "primary_candidate": review.primary_candidate,
            "vision_confidence": review.vision_confidence,
            "evidence_confidence": review.evidence_confidence,
            "overall_confidence": review.overall_confidence,
            "severity_estimate": review.severity,
            "recommended_immediate_actions": review.recommended_actions,
            "prevention_monitoring": review.prevention_monitoring,
            "what_to_watch_next": review.what_to_watch,
            "evidence_is_mixed": review.evidence_is_mixed,
            "conflict_notes": review.conflict_notes,
            "is_demo_mode": review.is_demo_mode,
            "provider_info": review.provider_info,
            "created_at": review.created_at.isoformat() if review.created_at else "",
            "sources": [
                {
                    "id": s.id,
                    "source_name": s.source_name,
                    "source_url": s.source_url,
                    "title": s.title,
                    "evidence_text": s.evidence_text,
                    "relevance_score": s.relevance_score,
                    "authority_tier": s.authority_tier
                }
                for s in sources
            ]
        }

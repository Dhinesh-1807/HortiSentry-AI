import logging
from typing import List, Optional, Dict, Any
from PIL import Image

from app.ml.vision_provider import VisionAnalysisResult
from app.ml.predictor import ml_service
from app.evidence.models import AIReviewOutput
from app.evidence.retrieval import EvidenceRetrievalService
from app.evidence.ranking import EvidenceRanker
from app.evidence.review_generator import AIReviewGenerator
from app.evidence.cache import global_evidence_cache

logger = logging.getLogger(__name__)

class EvidenceEngineService:
    """Main Orchestration Service for AI Evidence Engine."""

    @classmethod
    def generate_ai_evidence_review(
        cls,
        image: Optional[Image.Image],
        crop: str,
        user_symptoms: Optional[List[str]] = None,
        location_state: Optional[str] = None,
        location_district: Optional[str] = None,
        farmer_requested_expert: bool = False,
        vision_result_override: Optional[VisionAnalysisResult] = None
    ) -> AIReviewOutput:
        crop_k = crop.lower()
        symptoms = user_symptoms if user_symptoms else []

        # 1. Vision Analysis
        if vision_result_override:
            vision_res = vision_result_override
        elif image:
            vision_res = ml_service.analyze_vision(image, crop_key=crop_k, user_symptoms=symptoms)
        else:
            # Fallback vision result if image omitted
            vision_res = ml_service.analyze_vision(Image.new("RGB", (224, 224), (100, 150, 100)), crop_key=crop_k, user_symptoms=symptoms)

        primary_candidate = vision_res.predicted_class

        # 2. Check Cache
        district_str = location_district or ""
        cached_evidence = global_evidence_cache.get(
            crop=crop_k,
            disease_candidate=primary_candidate,
            symptoms=vision_res.visible_symptoms,
            location_district=district_str
        )

        if cached_evidence:
            raw_evidence = cached_evidence
        else:
            retrieval_svc = EvidenceRetrievalService()
            raw_evidence = retrieval_svc.retrieve_evidence(
                crop=crop_k,
                disease_candidate=primary_candidate,
                symptoms=vision_res.visible_symptoms,
                max_sources=8
            )
            # Store in cache
            global_evidence_cache.set(
                crop=crop_k,
                disease_candidate=primary_candidate,
                symptoms=vision_res.visible_symptoms,
                items=raw_evidence,
                location_district=district_str
            )

        # 3. Rank Evidence
        ranked_evidence = EvidenceRanker.rank_evidence(raw_evidence)

        # 4. Generate Review
        ai_review = AIReviewGenerator.generate_review(
            crop=crop_k,
            vision_result=vision_res,
            ranked_evidence=ranked_evidence,
            location_state=location_state,
            location_district=location_district,
            farmer_requested_expert=farmer_requested_expert
        )

        logger.info(
            f"Generated AI Evidence Review for crop '{crop_k}', primary '{primary_candidate}', "
            f"overall_conf={ai_review.overall_confidence}, mixed={ai_review.evidence_is_mixed}, "
            f"escalation={ai_review.escalation_recommended}"
        )
        return ai_review

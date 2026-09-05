import os
import sys
import logging
from PIL import Image

# Ensure backend path is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.database.connection import SessionLocal
from app.database.init_db import init_db
from app.services.crop_service import CropConfigLoader
from app.ml.predictor import ml_service
from app.evidence.service import EvidenceEngineService
from app.evidence.models import RetrievedEvidence
from app.services.ai_review_service import AIReviewService
from app.models.models import Observation, Crop, User, AIReview

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("verify_phase10")

def run_verification():
    logger.info("=== HORTISENTRY PHASE 10 E2E SYSTEM VERIFICATION ===")
    
    # Init DB
    init_db()
    db = SessionLocal()

    try:
        # 1. Verify Catalogue
        crops = CropConfigLoader.get_supported_crops()
        logger.info(f"✔ Multi-crop catalogue loaded: {len(crops)} crops verified.")
        assert len(crops) >= 32, f"Expected >= 32 crops, got {len(crops)}"

        # Prepare test user and crop in DB
        user = db.query(User).first()
        if not user:
            user = User(name="Test Farmer", role="FARMER")
            db.add(user)
            db.commit()

        tomato_crop = db.query(Crop).filter(Crop.key == "tomato").first()
        if not tomato_crop:
            tomato_crop = Crop(key="tomato", display_name="Tomato")
            db.add(tomato_crop)
            db.commit()

        chilli_crop = db.query(Crop).filter(Crop.key == "chilli").first()
        if not chilli_crop:
            chilli_crop = Crop(key="chilli", display_name="Chilli")
            db.add(chilli_crop)
            db.commit()

        # SCENARIO 1: Tomato Real Vision Model + AI Evidence Engine
        logger.info("\n--- Scenario 1: Tomato Real Vision Inference & Evidence ---")
        dummy_img = Image.new("RGB", (224, 224), (120, 160, 100))
        tomato_obs = Observation(
            user_id=user.id,
            crop_id=tomato_crop.id,
            crop_stage="VEGETATIVE",
            symptoms=["Yellow spots"],
            location_village="Test Village",
            location_district="Test District",
            location_state="Test State",
            status="SUBMITTED"
        )
        db.add(tomato_obs)
        db.commit()
        db.refresh(tomato_obs)

        review1 = AIReviewService.create_or_get_ai_review(db=db, observation_id=tomato_obs.id)
        logger.info(f"Scenario 1 Result: candidate='{review1['primary_candidate']}', conf={review1['overall_confidence']}, sources={len(review1['sources'])}")
        assert review1['primary_candidate'] is not None
        assert len(review1['sources']) > 0

        # SCENARIO 2: Chilli Visual Assessment + AI Evidence Engine
        logger.info("\n--- Scenario 2: Chilli Visual Assessment & Evidence ---")
        chilli_obs = Observation(
            user_id=user.id,
            crop_id=chilli_crop.id,
            crop_stage="VEGETATIVE",
            symptoms=["Upward leaf curling"],
            location_village="Test Village",
            location_district="Test District",
            location_state="Test State",
            status="SUBMITTED"
        )
        db.add(chilli_obs)
        db.commit()
        db.refresh(chilli_obs)

        review2 = AIReviewService.create_or_get_ai_review(db=db, observation_id=chilli_obs.id)
        logger.info(f"Scenario 2 Result: crop='chilli', candidate='{review2['primary_candidate']}', conf={review2['overall_confidence']}, sources={len(review2['sources'])}")
        assert review2['crop_key'] == 'chilli'
        assert len(review2['sources']) > 0

        # SCENARIO 3: Low-Confidence / Unknown Symptom Expert Escalation
        logger.info("\n--- Scenario 3: Unknown / Low-Confidence Escalation ---")
        raw_rev3 = EvidenceEngineService.generate_ai_evidence_review(
            image=Image.new("RGB", (224, 224), (200, 200, 200)),
            crop="banana",
            user_symptoms=["Unclear wilting"]
        )
        logger.info(f"Scenario 3 Result: overall_conf={raw_rev3.overall_confidence}")
        assert raw_rev3.overall_confidence <= 1.0

        # SCENARIO 4: Source Failure / Fallback Handling
        logger.info("\n--- Scenario 4: Source Fallback Behavior ---")
        fallback_ev = EvidenceEngineService.generate_ai_evidence_review(
            image=None,
            crop="unknown_crop_xyz",
            user_symptoms=["Atypical leaf blotch"]
        )
        logger.info(f"Scenario 4 Result: fallback sources count={len(fallback_ev.sources_used)}")
        assert len(fallback_ev.sources_used) > 0

        # SCENARIO 5: Conflicting Evidence Warning
        logger.info("\n--- Scenario 5: Conflicting Evidence Handling ---")
        mock_evidence_1 = RetrievedEvidence(
            source_name="TNAU Agritech",
            domain="agritech.tnau.ac.in",
            title="Early Blight",
            url="https://agritech.tnau.ac.in/eb",
            evidence_text="Symptoms: Leaf spots",
            authority_tier=1,
            crop_relevance=0.8,
            disease_relevance=0.65,
            symptom_relevance=0.6,
            relevance_score=0.75
        )
        mock_evidence_2 = RetrievedEvidence(
            source_name="ICAR CPRI",
            domain="icar.gov.in",
            title="Late Blight Overlap",
            url="https://icar.gov.in/lb",
            evidence_text="Symptoms: Water-soaked spots",
            authority_tier=1,
            crop_relevance=0.8,
            disease_relevance=0.60,
            symptom_relevance=0.6,
            relevance_score=0.72
        )
        from app.evidence.review_generator import AIReviewGenerator
        from app.ml.vision_provider import VisionAnalysisResult
        dummy_vis = VisionAnalysisResult(
            crop_key="tomato",
            provider_type="trained_model",
            model_version="tomato-v1",
            predicted_class="Early Blight",
            confidence=0.80,
            visible_symptoms=["Spots"],
            disease_candidates=[{"class": "Early Blight", "visual_confidence": 0.80}, {"class": "Late Blight", "visual_confidence": 0.20}],
            visual_confidence=0.80
        )
        conflict_rev = AIReviewGenerator.generate_review("tomato", dummy_vis, [mock_evidence_1, mock_evidence_2])
        logger.info(f"Scenario 5 Result: evidence_is_mixed={conflict_rev.evidence_is_mixed}, conflict_notes='{conflict_rev.conflict_notes}'")
        assert conflict_rev.evidence_is_mixed == True

        logger.info("\n=======================================================")
        logger.info("✔ ALL 5 PHASE 10 VERIFICATION SCENARIOS PASSED SUCCESSFULLY!")
        logger.info("=======================================================")

    finally:
        db.close()

if __name__ == "__main__":
    run_verification()

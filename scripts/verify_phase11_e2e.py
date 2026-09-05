import sys
import os
import io
import time
import logging
from pathlib import Path
from PIL import Image

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
backend_dir = PROJECT_ROOT / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.ml.predictor import ml_service
from app.database.connection import SessionLocal
from app.models.models import Observation, AIReview, ReviewEvidence, Escalation, ExpertReview

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Phase11_E2E")

client = TestClient(app)

def create_test_image_bytes(color=(100, 160, 80), size=(300, 300)):
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def run_phase11_e2e():
    logger.info("==================================================================")
    logger.info("HORTISENTRY PHASE 11: E2E AI EVIDENCE ENGINE VERIFICATION SCRIPT")
    logger.info("==================================================================")

    passed_scenarios = 0
    total_scenarios = 6

    # ----------------------------------------------------
    # SCENARIO 1: Tomato Observation Flow with Dedicated PyTorch Model
    # ----------------------------------------------------
    logger.info("\n--- Scenario 1: Tomato Observation & AI Evidence Review ---")
    test_img_path = PROJECT_ROOT / "data" / "test" / "Healthy" / "Healthy_01005.JPG"
    if test_img_path.exists():
        with open(test_img_path, "rb") as f:
            img_bytes = f.read()
    else:
        img_bytes = create_test_image_bytes()

    res1 = client.post(
        "/api/observations",
        data={
            "crop_id": "tomato",
            "crop_stage": "FRUITING",
            "symptoms": '["Concentric brown leaf lesions", "Yellow halo"]',
            "village": "Coimbatore Rural",
            "district": "Coimbatore",
            "state": "Tamil Nadu"
        },
        files={"file": ("tomato_leaf.jpg", img_bytes, "image/jpeg")}
    )
    assert res1.status_code == 201, f"Scenario 1 submission failed: {res1.text}"
    data1 = res1.json()
    obs_id_1 = data1["observation_id"]
    logger.info(f"Observation created successfully. ID: {obs_id_1}")

    # Fetch AI Review
    res1_rev = client.get(f"/api/ai-review/{obs_id_1}")
    assert res1_rev.status_code == 200, f"Failed to fetch AI review: {res1_rev.text}"
    review1 = res1_rev.json()
    assert review1["primary_candidate"] is not None
    assert len(review1["sources"]) > 0
    logger.info(f"Scenario 1 Passed: AI Review Ready for Tomato. Primary: '{review1['primary_candidate']}', Sources: {len(review1['sources'])}")
    passed_scenarios += 1

    # ----------------------------------------------------
    # SCENARIO 2: Non-Tomato Crop (Chilli) Visual Assessment Flow
    # ----------------------------------------------------
    logger.info("\n--- Scenario 2: Non-Tomato Crop (Chilli) Visual Assessment & AI Review ---")
    chilli_bytes = create_test_image_bytes(color=(140, 60, 40))
    res2 = client.post(
        "/api/observations",
        data={
            "crop_id": "chilli",
            "crop_stage": "VEGETATIVE",
            "symptoms": '["Leaf curl", "Stunted growth"]',
            "village": "Guntur East",
            "district": "Guntur",
            "state": "Andhra Pradesh"
        },
        files={"file": ("chilli_leaf.jpg", chilli_bytes, "image/jpeg")}
    )
    assert res2.status_code == 201, f"Scenario 2 submission failed: {res2.text}"
    obs_id_2 = res2.json()["observation_id"]

    res2_rev = client.get(f"/api/ai-review/{obs_id_2}")
    assert res2_rev.status_code == 200
    review2 = res2_rev.json()
    assert review2["crop_key"] == "chilli"
    assert len(review2["sources"]) > 0
    logger.info(f"Scenario 2 Passed: Non-tomato AI Review generated for Chilli. Candidates: {review2['primary_candidate']}")
    passed_scenarios += 1

    # ----------------------------------------------------
    # SCENARIO 3: Low Confidence / Uncertain Case Escalation
    # ----------------------------------------------------
    logger.info("\n--- Scenario 3: Low Confidence / Uncertain Case Escalation ---")
    dark_bytes = create_test_image_bytes(color=(5, 5, 5))
    res3 = client.post(
        "/api/observations",
        data={
            "crop_id": "brinjal",
            "crop_stage": "FLOWERING",
            "symptoms": '["Unknown spots"]',
            "village": "Village",
            "district": "District",
            "state": "State"
        },
        files={"file": ("dark.jpg", dark_bytes, "image/jpeg")}
    )
    assert res3.status_code == 201
    obs_id_3 = res3.json()["observation_id"]

    res3_obs = client.get(f"/api/observations/{obs_id_3}")
    assert res3_obs.status_code == 200
    obs3_data = res3_obs.json()
    assert obs3_data["escalation"]["is_escalated"] is True
    logger.info(f"Scenario 3 Passed: Low confidence observation correctly escalated to Expert Queue. Reason: {obs3_data['escalation']['reason']}")
    passed_scenarios += 1

    # ----------------------------------------------------
    # SCENARIO 4: Web Search Unavailability Graceful Fallback
    # ----------------------------------------------------
    logger.info("\n--- Scenario 4: Web Search Unavailability Graceful Fallback ---")
    old_provider = os.getenv("SEARCH_PROVIDER", "local")
    os.environ["SEARCH_PROVIDER"] = "custom_web_unreachable"

    try:
        res4 = client.post(
            "/api/observations",
            data={
                "crop_id": "potato",
                "crop_stage": "VEGETATIVE",
                "symptoms": '["Water soaked lesions"]',
                "village": "Hassan",
                "district": "Hassan",
                "state": "Karnataka"
            },
            files={"file": ("potato.jpg", create_test_image_bytes(), "image/jpeg")}
        )
        assert res4.status_code == 201
        obs_id_4 = res4.json()["observation_id"]
        res4_rev = client.get(f"/api/ai-review/{obs_id_4}")
        assert res4_rev.status_code == 200
        review4 = res4_rev.json()
        assert len(review4["sources"]) > 0
        logger.info(f"Scenario 4 Passed: Graceful fallback executed successfully. Sources retrieved: {len(review4['sources'])}")
        passed_scenarios += 1
    finally:
        os.environ["SEARCH_PROVIDER"] = old_provider

    # ----------------------------------------------------
    # SCENARIO 5: Conflicting Evidence Sources Handling
    # ----------------------------------------------------
    logger.info("\n--- Scenario 5: Conflicting Evidence Sources Handling ---")
    from app.evidence.review_generator import AIReviewGenerator
    from app.evidence.models import RetrievedEvidence
    from app.ml.vision_provider import VisionAnalysisResult

    vision_res = VisionAnalysisResult(
        crop_key="tomato",
        provider_type="trained_model",
        model_version="tomato-v1",
        predicted_class="Early Blight",
        confidence=0.72,
        visual_confidence=0.72,
        visible_symptoms=["Yellow spots", "Necrotic lesion"],
        disease_candidates=[
            {"class": "Early Blight", "visual_confidence": 0.52},
            {"class": "Septoria Leaf Spot", "visual_confidence": 0.48}
        ]
    )

    ev1 = RetrievedEvidence(
        source_name="TNAU Agritech", domain="agritech.tnau.ac.in", title="Early Blight Advisory",
        url="https://agritech.tnau.ac.in/eb", evidence_text="Concentric ring spots.", authority_tier=1, disease_relevance=0.65
    )
    ev2 = RetrievedEvidence(
        source_name="ICAR Advisory", domain="icar.gov.in", title="Septoria Spot Advisory",
        url="https://icar.gov.in/septoria", evidence_text="Small circular gray spots.", authority_tier=1, disease_relevance=0.60
    )

    conflict_review = AIReviewGenerator.generate_review("tomato", vision_res, [ev1, ev2])
    assert conflict_review.evidence_is_mixed is True
    assert conflict_review.escalation_recommended is True
    assert conflict_review.conflict_notes is not None
    logger.info(f"Scenario 5 Passed: Mixed evidence correctly flagged. Conflict note: '{conflict_review.conflict_notes[:60]}...'")
    passed_scenarios += 1

    # ----------------------------------------------------
    # SCENARIO 6: Farmer-Requested Expert Verification Workflow
    # ----------------------------------------------------
    logger.info("\n--- Scenario 6: Farmer-Requested Manual Expert Verification ---")
    res6 = client.post(
        "/api/observations",
        data={
            "crop_id": "tomato",
            "crop_stage": "HARVEST",
            "symptoms": '["Leaf spot"]',
            "village": "Salem Rural",
            "district": "Salem",
            "state": "Tamil Nadu"
        },
        files={"file": ("tomato_harvest.jpg", create_test_image_bytes(), "image/jpeg")}
    )
    obs_id_6 = res6.json()["observation_id"]

    # Farmer requests manual expert review
    res6_esc = client.post(
        f"/api/observations/{obs_id_6}/escalate",
        json={"reason_notes": "Farmer requests official extension officer confirmation before treatment."}
    )
    assert res6_esc.status_code == 200

    # Expert reviews queue
    res6_queue = client.get("/api/expert/reviews")
    assert res6_queue.status_code == 200
    queue_6 = res6_queue.json()
    item_6 = next((r for r in queue_6 if r["observation_id"] == obs_id_6), None)
    assert item_6 is not None

    # Expert completes diagnosis
    res6_comp = client.post(
        f"/api/expert/reviews/{item_6['review_id']}/complete",
        json={"expert_prediction": "Septoria Leaf Spot", "expert_notes": "Confirmed Septoria Leaf Spot."}
    )
    assert res6_comp.status_code == 200

    # Decision Preservation Verification
    db = SessionLocal()
    ai_rev_db = db.query(AIReview).filter(AIReview.observation_id == obs_id_6).first()
    exp_rev_db = db.query(ExpertReview).filter(ExpertReview.observation_id == obs_id_6).first()
    assert ai_rev_db is not None
    assert exp_rev_db is not None
    assert exp_rev_db.expert_prediction == "Septoria Leaf Spot"
    db.close()

    logger.info("Scenario 6 Passed: Manual escalation, expert diagnosis override, and AI review preservation verified.")
    passed_scenarios += 1

    logger.info("==================================================================")
    logger.info(f"PHASE 11 E2E VERIFICATION COMPLETE: {passed_scenarios}/{total_scenarios} SCENARIOS PASSED (100%)")
    logger.info("==================================================================")

if __name__ == "__main__":
    run_phase11_e2e()

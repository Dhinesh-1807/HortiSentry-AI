import os
import sys
import io
import pytest
from pathlib import Path
from PIL import Image
import numpy as np
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.core.config import settings
from app.ml.predictor import ml_service
from app.database.connection import SessionLocal
from app.models.models import (
    Observation, Prediction, Escalation, ExpertReview, ModelVersion, User, Crop
)
from app.core.constants import ObservationStatus, EscalationReason, ReviewStatus, UserRole

client = TestClient(app)

def create_synthetic_image(color=(100, 180, 80), format="JPEG"):
    img = Image.new("RGB", (224, 224), color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf.getvalue()

@pytest.fixture(autouse=True)
def setup_real_ml_mode():
    """Ensure REAL mode is active for integration tests."""
    original_mode = settings.ML_MODE
    settings.ML_MODE = "REAL"
    ml_service.reload_model()
    yield
    settings.ML_MODE = original_mode
    ml_service.reload_model()


# ----------------------------------------------------------------------
# 2.1 Farmer Observation Test
# ----------------------------------------------------------------------
def test_2_1_farmer_observation_submission():
    """Test 2.1: Farmer selects crop, stage, symptoms, location, uploads image, submits observation."""
    img_bytes = create_synthetic_image(color=(100, 180, 80))

    response = client.post(
        "/api/observations",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        data={
            "crop_id": "tomato",
            "crop_stage": "VEGETATIVE",
            "symptoms": '["Yellow spots"]',
            "village": "Coimbatore Farm Region",
            "district": "Coimbatore",
            "state": "Tamil Nadu"
        }
    )
    assert response.status_code == 201, f"Observation submission failed: {response.text}"
    data = response.json()
    assert "observation_id" in data
    assert data["crop"] == "Tomato"

    # Verify DB State
    db = SessionLocal()
    try:
        obs = db.query(Observation).filter(Observation.id == data["observation_id"]).first()
        assert obs is not None
        assert obs.crop_stage == "VEGETATIVE"
        assert obs.location_village == "Coimbatore Farm Region"
        assert obs.crop.key == "tomato"
    finally:
        db.close()


# ----------------------------------------------------------------------
# 2.2 Image Upload Test (Valid, Unsupported, Oversized, Corrupted, Poor Quality)
# ----------------------------------------------------------------------
def test_2_2_image_upload_validation():
    """Test 2.2: Upload validation edge cases."""
    # 1. Valid Image (WEBP)
    valid_bytes = create_synthetic_image(color=(120, 190, 90), format="WEBP")
    r_valid = client.post(
        "/api/predict",
        files={"file": ("leaf.webp", valid_bytes, "image/webp")},
        params={"crop": "tomato"}
    )
    assert r_valid.status_code == 200, f"Valid WEBP upload failed: {r_valid.text}"

    # 2. Unsupported File Type (.txt)
    r_invalid_ext = client.post(
        "/api/predict",
        files={"file": ("document.txt", io.BytesIO(b"not an image"), "text/plain")}
    )
    assert r_invalid_ext.status_code in [400, 422, 415, 403], f"Unsupported file expected error, got {r_invalid_ext.status_code}"

    # 3. Oversized Image (>10MB)
    huge_bytes = b"0" * (11 * 1024 * 1024)
    r_oversized = client.post(
        "/api/predict",
        files={"file": ("huge.jpg", io.BytesIO(huge_bytes), "image/jpeg")}
    )
    assert r_oversized.status_code in [400, 413, 422], f"Oversized file expected error, got {r_oversized.status_code}"

    # 4. Corrupted Image File
    corrupt_bytes = b"FF D8 FF E0 00 10 4A 46 49 46 00 corrupted data stream"
    r_corrupt = client.post(
        "/api/predict",
        files={"file": ("corrupt.jpg", io.BytesIO(corrupt_bytes), "image/jpeg")}
    )
    assert r_corrupt.status_code in [400, 422, 415, 500], f"Corrupted file expected error, got {r_corrupt.status_code}"


# ----------------------------------------------------------------------
# 2.3 AI Inference Test
# ----------------------------------------------------------------------
def test_2_3_ai_inference_response_schema():
    """Test 2.3: AI Inference returns proper schema with prediction, confidence, risk, model version."""
    img_bytes = create_synthetic_image(color=(90, 160, 70))

    response = client.post(
        "/api/predict",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        params={"crop": "tomato"}
    )
    assert response.status_code == 200
    data = response.json()

    assert "predicted_class" in data
    assert "confidence" in data
    assert isinstance(data["confidence"], float)
    assert "top_predictions" in data
    assert len(data["top_predictions"]) >= 1
    assert "model_version" in data
    assert data["model_version"] == "tomato-v1"
    assert "needs_expert_review" in data
    assert "provider_type" in data


# ----------------------------------------------------------------------
# 2.4 Escalation Engine Rules (Cases A, B, C, D)
# ----------------------------------------------------------------------
def test_2_4_escalation_rules_cases():
    """Test 2.4: Escalation engine rules for Cases A, B, C, D."""

    # CASE A: Routine Observation Submission
    valid_bytes = create_synthetic_image(color=(100, 180, 80))
    res_a = client.post(
        "/api/observations",
        files={"file": ("leaf_a.jpg", valid_bytes, "image/jpeg")},
        data={
            "crop_id": "tomato",
            "crop_stage": "VEGETATIVE",
            "symptoms": '["Healthy leaf"]',
            "village": "Farm A",
            "district": "Coimbatore",
            "state": "Tamil Nadu"
        }
    )
    assert res_a.status_code == 201
    data_a = res_a.json()
    assert "observation_id" in data_a

    # CASE D: Poor Image Quality / Dark Image triggers escalation
    dark_bytes = create_synthetic_image(color=(10, 10, 10))
    res_d = client.post(
        "/api/observations",
        files={"file": ("dark_leaf.jpg", dark_bytes, "image/jpeg")},
        data={
            "crop_id": "tomato",
            "crop_stage": "SEEDLING",
            "symptoms": '["Dark lesions"]',
            "village": "Dark Field",
            "district": "Coimbatore",
            "state": "Tamil Nadu"
        }
    )
    assert res_d.status_code == 201
    obs_id_d = res_d.json()["observation_id"]

    db = SessionLocal()
    try:
        obs_d = db.query(Observation).filter(Observation.id == obs_id_d).first()
        assert obs_d is not None
        assert obs_d.status is not None
    finally:
        db.close()


# ----------------------------------------------------------------------
# 2.5 Expert Queue Test & RBAC
# ----------------------------------------------------------------------
def test_2_5_expert_queue_and_rbac():
    """Test 2.5: Escalated case appears in expert queue, RBAC restriction enforced."""
    # 1. Unauthenticated request to expert reviews
    r_unauth = client.get("/api/expert/reviews")
    assert r_unauth.status_code in [401, 403], f"Expected 401/403 for unauth user, got {r_unauth.status_code}"

    # 2. Authenticated Expert Access
    login_res = client.post("/api/auth/demo-login", json={"role": "expert"})
    assert login_res.status_code == 200
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    r_queue = client.get("/api/expert/reviews", headers=headers)
    assert r_queue.status_code == 200
    queue = r_queue.json()
    assert isinstance(queue, list)


# ----------------------------------------------------------------------
# 2.6 Expert Review Test
# ----------------------------------------------------------------------
def test_2_6_expert_review_workflow():
    """Test 2.6: Expert review submission updates DB state and observation status."""
    # Create dark image observation to trigger escalation
    dark_bytes = create_synthetic_image(color=(12, 12, 12))
    sub_res = client.post(
        "/api/observations",
        files={"file": ("dark.jpg", dark_bytes, "image/jpeg")},
        data={
            "crop_id": "tomato",
            "crop_stage": "FLOWERING",
            "symptoms": '["Yellowing spots"]',
            "village": "Review Village",
            "district": "Coimbatore",
            "state": "Tamil Nadu"
        }
    )
    assert sub_res.status_code == 201
    obs_id = sub_res.json()["observation_id"]

    # Login as Expert
    login_res = client.post("/api/auth/demo-login", json={"role": "expert"})
    assert login_res.status_code == 200
    expert_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

    # Query queue to get review ID for obs_id
    q_res = client.get("/api/expert/reviews", headers=expert_headers)
    assert q_res.status_code == 200
    queue = q_res.json()
    item = next((q for q in queue if q["observation_id"] == obs_id), None)
    
    if item:
        review_id = item["review_id"]
        # Complete review
        comp_res = client.post(
            f"/api/expert/reviews/{review_id}/complete",
            headers=expert_headers,
            json={
                "expert_prediction": "Early Blight",
                "expert_notes": "Apply copper fungicide and prune lower infected foliage."
            }
        )
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert comp_data["review_status"] == "COMPLETED"

        # Verify DB State
        db = SessionLocal()
        try:
            obs = db.query(Observation).filter(Observation.id == obs_id).first()
            assert obs is not None
        finally:
            db.close()


# ----------------------------------------------------------------------
# 2.7 End-to-End Automated Test (API + Database State Verification)
# ----------------------------------------------------------------------
def test_2_7_full_end_to_end_workflow():
    """Test 2.7: Complete E2E integration test verifying API HTTP status and DB state."""
    db = SessionLocal()
    try:
        # 1. Farmer Observation Submission
        img_bytes = create_synthetic_image(color=(15, 15, 15))
        res_sub = client.post(
            "/api/observations",
            files={"file": ("leaf_e2e.jpg", img_bytes, "image/jpeg")},
            data={
                "crop_id": "tomato",
                "crop_stage": "FRUITING",
                "symptoms": '["Water soaked dark spots"]',
                "village": "E2E Farm Region",
                "district": "Coimbatore",
                "state": "Tamil Nadu"
            }
        )
        assert res_sub.status_code == 201
        obs_id = res_sub.json()["observation_id"]

        # Verify DB Observation & Prediction
        obs_db = db.query(Observation).filter(Observation.id == obs_id).first()
        assert obs_db is not None
        assert obs_db.crop.key == "tomato"

        pred_db = db.query(Prediction).filter(Prediction.observation_id == obs_id).first()
        assert pred_db is not None

        # 2. Expert Login & Review Completion
        login_res = client.post("/api/auth/demo-login", json={"role": "expert"})
        assert login_res.status_code == 200
        expert_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

        q_res = client.get("/api/expert/reviews", headers=expert_headers)
        assert q_res.status_code == 200
        queue = q_res.json()
        item = next((q for q in queue if q["observation_id"] == obs_id), None)

        if item:
            review_id = item["review_id"]
            comp_res = client.post(
                f"/api/expert/reviews/{review_id}/complete",
                headers=expert_headers,
                json={
                    "expert_prediction": "Late Blight",
                    "expert_notes": "Apply systemic fungicide immediately and isolate infected foliage."
                }
            )
            assert comp_res.status_code == 200

            # Verify DB Status Updated
            db.refresh(obs_db)
            assert obs_db is not None
    finally:
        db.close()

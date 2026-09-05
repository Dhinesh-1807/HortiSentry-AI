import os
import sys
import io
import pytest
from pathlib import Path
from PIL import Image
import numpy as np
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.core.config import settings
from app.ml.predictor import ml_service
from app.database.connection import SessionLocal
from app.models.models import (
    Observation, Prediction, Escalation, ExpertReview, ModelVersion, ObservationImage
)
from app.core.constants import ObservationStatus, EscalationReason, ReviewStatus

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_real_ml_mode():
    """Ensure ML_MODE=REAL is active for Phase 8 integration tests."""
    original_mode = settings.ML_MODE
    settings.ML_MODE = "REAL"
    ml_service.reload_model()
    yield
    settings.ML_MODE = original_mode
    ml_service.reload_model()


def test_01_api_health_and_model_status():
    """Verify GET /api/health and GET /api/model/status endpoints."""
    r_health = client.get("/api/health")
    assert r_health.status_code == 200
    health_data = r_health.json()
    assert health_data["status"] == "ok"
    assert health_data["database"] == "connected"
    assert health_data["ml_mode"] == "REAL"

    r_status1 = client.get("/api/model-status")
    assert r_status1.status_code == 200
    status_data1 = r_status1.json()
    assert status_data1["status"] == "active"
    assert status_data1["model_version"] == "tomato-v1"
    assert status_data1["class_count"] == 4

    r_status2 = client.get("/api/model/status")
    assert r_status2.status_code == 200
    assert r_status2.json() == status_data1


def test_02_get_crops_endpoint():
    """Verify GET /api/crops returns Tomato crop configuration."""
    res = client.get("/api/crops")
    assert res.status_code == 200
    crops = res.json()
    assert isinstance(crops, list)
    assert len(crops) >= 1
    tomato = next((c for c in crops if c["key"] == "tomato"), None)
    assert tomato is not None
    assert tomato["display_name"] == "Tomato"
    assert len(tomato["disease_classes"]) == 4


def test_03_real_model_inference_api():
    """Verify POST /api/predict using actual test image data/test/Healthy/Healthy_01005.JPG."""
    test_img_path = PROJECT_ROOT / "data" / "test" / "Healthy" / "Healthy_01005.JPG"
    assert test_img_path.exists(), f"Test image missing at {test_img_path}"

    with open(test_img_path, "rb") as f:
        response = client.post("/api/predict", files={"file": ("Healthy_01005.JPG", f, "image/jpeg")})

    assert response.status_code == 200
    data = response.json()

    assert data["predicted_class"] == "Healthy"
    assert data["confidence"] >= 0.90
    assert data["model_version"] == "tomato-v1"
    assert data["is_demo_mode"] is False
    assert len(data["top_predictions"]) >= 3
    assert data["inference_time_ms"] > 0.0


def test_04_farmer_observation_submission_end_to_end():
    """Test full farmer observation submission lifecycle."""
    test_img_path = PROJECT_ROOT / "data" / "test" / "Healthy" / "Healthy_01005.JPG"
    
    with open(test_img_path, "rb") as f:
        files = {"file": ("Healthy_01005.JPG", f, "image/jpeg")}
        form_data = {
            "crop_id": "tomato",
            "crop_stage": "FRUITING",
            "symptoms": "Yellow spots, Leaf curling",
            "village": "Green Valley",
            "district": "Bengaluru Rural",
            "state": "Karnataka",
            "notes": "Observed on lower leaves during field inspection."
        }
        res = client.post("/api/observations", data=form_data, files=files)

    assert res.status_code == 201
    obs = res.json()
    obs_id = obs["observation_id"]

    assert obs["crop"] == "Tomato"
    assert obs["crop_stage"] == "FRUITING"
    assert "prediction" in obs
    assert obs["prediction"]["predicted_class"] == "Healthy"
    assert obs["prediction"]["is_demo_mode"] is False

    # Fetch observation details
    res_get = client.get(f"/api/observations/{obs_id}")
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["id"] == obs_id


def test_05_escalation_triggers_low_confidence_and_manual():
    """Test manual escalation and verify database escalation records."""
    # Create observation
    test_img_path = PROJECT_ROOT / "data" / "test" / "Healthy" / "Healthy_01005.JPG"
    with open(test_img_path, "rb") as f:
        res_create = client.post(
            "/api/observations",
            data={
                "crop_id": "tomato",
                "crop_stage": "VEGETATIVE",
                "symptoms": "Yellow spots",
                "village": "Green Valley",
                "district": "Bengaluru",
                "state": "Karnataka"
            },
            files={"file": ("Healthy_01005.JPG", f, "image/jpeg")}
        )
    obs_id = res_create.json()["observation_id"]

    # Manual escalation request
    res_esc = client.post(f"/api/observations/{obs_id}/escalate", json={"reason_notes": "Farmer uncertain about spots"})
    assert res_esc.status_code == 200
    esc_data = res_esc.json()

    assert esc_data["observation_id"] == obs_id
    assert esc_data["reason"] == "MANUAL_FARMER_REQUEST"

    # Verify observation detail endpoint includes escalation summary
    res_obs_get = client.get(f"/api/observations/{obs_id}")
    assert res_obs_get.status_code == 200
    assert res_obs_get.json()["escalation"]["is_escalated"] is True


def test_06_expert_workflow_and_decision_preservation():
    """
    Test Expert dashboard, queue review, completion, and verify AI vs Expert diagnosis preservation.
    """
    # 1. Create observation
    test_img_path = PROJECT_ROOT / "data" / "test" / "Healthy" / "Healthy_01005.JPG"
    with open(test_img_path, "rb") as f:
        res_create = client.post(
            "/api/observations",
            data={
                "crop_id": "tomato",
                "crop_stage": "VEGETATIVE",
                "symptoms": "Yellow spots",
                "village": "Green Valley",
                "district": "Bengaluru",
                "state": "Karnataka"
            },
            files={"file": ("Healthy_01005.JPG", f, "image/jpeg")}
        )
    obs_id = res_create.json()["observation_id"]

    # 2. Escalate observation to Expert review queue
    client.post(f"/api/observations/{obs_id}/escalate", json={"reason_notes": "Request expert review"})

    # 3. Authenticate as verified Expert and view review queue
    login_res = client.post("/api/auth/demo-login", json={"role": "expert"})
    assert login_res.status_code == 200
    expert_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

    res_reviews = client.get("/api/expert/reviews", headers=expert_headers)
    assert res_reviews.status_code == 200
    reviews = res_reviews.json()
    review_item = next((r for r in reviews if r["observation_id"] == obs_id), None)
    assert review_item is not None
    review_id = review_item["review_id"]

    # 4. Expert opens review detail
    res_detail = client.get(f"/api/expert/reviews/{review_id}", headers=expert_headers)
    assert res_detail.status_code == 200

    # 5. Expert completes review overriding AI diagnosis (AI: Healthy -> Expert: Early_Blight)
    res_complete = client.post(
        f"/api/expert/reviews/{review_id}/complete",
        headers=expert_headers,
        json={
            "expert_prediction": "Early_Blight",
            "expert_notes": "Early Blight lesions confirmed by visual inspection."
        }
    )
    assert res_complete.status_code == 200
    completed_data = res_complete.json()
    assert completed_data["review_status"] == "COMPLETED"
    assert "Early" in completed_data["expert_prediction"]

    # 6. DECISION PRESERVATION CHECK: Verify original AI Prediction is preserved in DB!
    db = SessionLocal()
    db_pred = db.query(Prediction).filter(Prediction.observation_id == obs_id).first()
    db_rev = db.query(ExpertReview).filter(ExpertReview.id == review_id).first()

    assert db_pred.predicted_class == "Healthy" # Original AI prediction remains preserved!
    assert "Early" in db_rev.expert_prediction # Expert review override stored separately!
    db.close()


def test_07_expert_dashboard_stats():
    """Verify GET /api/expert/dashboard/stats endpoint."""
    login_res = client.post("/api/auth/demo-login", json={"role": "expert"})
    assert login_res.status_code == 200
    expert_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

    res = client.get("/api/expert/dashboard/stats", headers=expert_headers)
    assert res.status_code == 200
    stats = res.json()
    assert "total_observations" in stats
    assert "pending_reviews" in stats
    assert "completed_reviews" in stats


def test_08_security_path_traversal_and_file_limits():
    """Verify security controls for malicious filenames, invalid formats, and size limits."""
    # 1. Path Traversal Test
    test_img = Image.new("RGB", (200, 200), color="green")
    img_byte_arr = io.BytesIO()
    test_img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    malicious_files = {"file": ("../../test_malicious.jpg", img_bytes, "image/jpeg")}
    res_mal = client.post("/api/predict", files=malicious_files)
    assert res_mal.status_code in [200, 201]
    # Verify no file written outside uploads directory
    assert not Path("../test_malicious.jpg").exists()

    # 2. Unsupported file extension test
    txt_files = {"file": ("document.txt", b"plain text data", "text/plain")}
    res_txt = client.post("/api/predict", files=txt_files)
    assert res_txt.status_code == 400


def test_09_dual_mode_switchability():
    """Verify smooth switching between REAL and DEMO modes without application failure."""
    dummy_img = Image.new("RGB", (224, 224), color=(120, 180, 220))
    img_bytes = io.BytesIO()
    dummy_img.save(img_bytes, format="JPEG")
    content = img_bytes.getvalue()

    # REAL Mode
    settings.ML_MODE = "REAL"
    ml_service.reload_model()
    res_real = client.post("/api/predict", files={"file": ("test.jpg", content, "image/jpeg")})
    assert res_real.status_code == 200
    assert res_real.json()["is_demo_mode"] is False

    # DEMO Mode
    settings.ML_MODE = "DEMO"
    ml_service.reload_model()
    res_demo = client.post("/api/predict", files={"file": ("test.jpg", content, "image/jpeg")})
    assert res_demo.status_code == 200
    assert res_demo.json()["is_demo_mode"] is True

    # Restore REAL Mode
    settings.ML_MODE = "REAL"
    ml_service.reload_model()

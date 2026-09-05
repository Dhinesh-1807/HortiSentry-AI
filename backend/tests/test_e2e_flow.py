import pytest
from tests.conftest import create_synthetic_image_bytes

def test_full_backend_end_to_end_lifecycle(client):
    """
    End-to-End Integration Test for HortiSentry Backend Core.
    Validates complete lifecycle from farmer submission to expert diagnosis.
    """

    # 1. Health & Config Verification
    health_res = client.get("/api/health")
    assert health_res.status_code == 200
    assert health_res.json()["database"] == "connected"

    crops_res = client.get("/api/crops")
    assert crops_res.status_code == 200
    assert len(crops_res.json()) > 0
    assert crops_res.json()[0]["key"] == "tomato"

    # 2. Farmer Observation Submission
    test_img = create_synthetic_image_bytes(color=(120, 180, 90), size=(400, 400), add_sharp_pattern=True)
    obs_response = client.post(
        "/api/observations",
        data={
            "crop_id": "tomato",
            "crop_stage": "FRUITING",
            "symptoms": '["Yellow spots", "Leaf curling"]',
            "village": "Sunrise Farm",
            "district": "Central District",
            "state": "Agri Pradesh",
            "notes": "Noticed yellow spots spreading rapidly on lower leaves.",
            "symptom_observed_at": "2026-08-30T10:00:00Z"
        },
        files={"file": ("tomato_leaf_symptom.jpg", test_img, "image/jpeg")}
    )

    assert obs_response.status_code == 201
    obs_data = obs_response.json()
    obs_id = obs_data["observation_id"]
    assert obs_id is not None
    assert isinstance(obs_data["prediction"]["is_demo_mode"], bool)

    # 3. Manual Escalation Trigger
    esc_response = client.post(
        f"/api/observations/{obs_id}/escalate",
        json={"reason_notes": "Farmer requested expert review for field guidance"}
    )
    assert esc_response.status_code == 200
    assert esc_response.json()["reason"] == "MANUAL_FARMER_REQUEST"

    # Authenticate as verified Expert
    login_res = client.post("/api/auth/demo-login", json={"role": "expert"})
    assert login_res.status_code == 200
    expert_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

    # 4. Expert Dashboard Stats Audit
    stats_response = client.get("/api/expert/dashboard/stats", headers=expert_headers)
    assert stats_response.status_code == 200
    assert stats_response.json()["pending_reviews"] >= 1

    # 5. Expert Queue Fetching
    queue_response = client.get("/api/expert/reviews", headers=expert_headers)
    assert queue_response.status_code == 200
    reviews = queue_response.json()
    target_review = next((r for r in reviews if r["observation_id"] == obs_id), None)
    assert target_review is not None
    review_id = target_review["review_id"]

    # 6. Expert Review Detail & State Transition to IN_PROGRESS
    detail_response = client.get(f"/api/expert/reviews/{review_id}", headers=expert_headers)
    assert detail_response.status_code == 200
    detail_data = detail_response.json()
    assert detail_data["review_status"] == "IN_PROGRESS"
    assert detail_data["location"] == "Sunrise Farm, Central District, Agri Pradesh"

    # 7. Expert Complete Review with Authoritative Ground Truth
    complete_response = client.post(
        f"/api/expert/reviews/{review_id}/complete",
        headers=expert_headers,
        json={
            "expert_prediction": "Early Blight",
            "expert_notes": "Confirmed Early Blight (Alternaria solani). Apply copper-based organic fungicide and remove infected lower foliage."
        }
    )
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    assert complete_data["review_status"] == "COMPLETED"
    assert "Early Blight" in complete_data["expert_prediction"]

    # 8. Final Observation Inspection to Verify Resolution
    final_obs_res = client.get(f"/api/observations/{obs_id}")
    assert final_obs_res.status_code == 200
    final_obs = final_obs_res.json()
    assert final_obs["expert_review"]["status"] == "COMPLETED"
    assert "Early Blight" in final_obs["expert_review"]["expert_prediction"]

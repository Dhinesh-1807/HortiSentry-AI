import pytest
from tests.conftest import create_synthetic_image_bytes

def test_expert_workflow(client):
    # 1. Submit observation that triggers escalation (e.g. low brightness/dark image)
    dark_bytes = create_synthetic_image_bytes(color=(10, 10, 10), add_sharp_pattern=False)
    sub_res = client.post(
        "/api/observations",
        data={
            "crop_id": "tomato",
            "crop_stage": "SEEDLING",
            "symptoms": '["Yellow spots"]',
            "village": "Dark Field",
            "district": "North District",
            "state": "Agri State"
        },
        files={"file": ("dark_leaf.jpg", dark_bytes, "image/jpeg")}
    )
    assert sub_res.status_code == 201
    obs_id = sub_res.json()["observation_id"]

    # Authenticate as verified Expert
    login_res = client.post("/api/auth/demo-login", json={"role": "expert"})
    assert login_res.status_code == 200
    expert_token = login_res.json()["token"]
    expert_headers = {"Authorization": f"Bearer {expert_token}"}

    # 2. Check Dashboard Stats
    stats_res = client.get("/api/expert/dashboard/stats", headers=expert_headers)
    assert stats_res.status_code == 200
    assert stats_res.json()["total_observations"] >= 1
    assert stats_res.json()["pending_reviews"] >= 1

    # 3. List Review Queue
    queue_res = client.get("/api/expert/reviews", headers=expert_headers)
    assert queue_res.status_code == 200
    queue = queue_res.json()
    assert len(queue) >= 1
    review_id = queue[0]["review_id"]

    # 4. Get Review Detail
    detail_res = client.get(f"/api/expert/reviews/{review_id}", headers=expert_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["review_status"] == "IN_PROGRESS"

    # 5. Complete Review
    comp_res = client.post(
        f"/api/expert/reviews/{review_id}/complete",
        headers=expert_headers,
        json={
            "expert_prediction": "Early Blight",
            "expert_notes": "Prune lower infected leaves and avoid overhead irrigation."
        }
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["review_status"] == "COMPLETED"
    assert "Early Blight" in comp_data["expert_prediction"]

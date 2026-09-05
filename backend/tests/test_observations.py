import io
import pytest
from tests.conftest import create_synthetic_image_bytes

def test_create_valid_observation(client):
    img_bytes = create_synthetic_image_bytes()
    
    response = client.post(
        "/api/observations",
        data={
            "crop_id": "tomato",
            "crop_stage": "VEGETATIVE",
            "symptoms": '["Yellow spots", "Leaf curling"]',
            "village": "Green Valley",
            "district": "Horti District",
            "state": "State Agri"
        },
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "observation_id" in data
    assert data["crop"] == "Tomato"
    assert isinstance(data["prediction"]["is_demo_mode"], bool)
    assert 0.0 <= data["prediction"]["confidence"] <= 1.0

def test_create_observation_invalid_crop(client):
    img_bytes = create_synthetic_image_bytes()
    
    response = client.post(
        "/api/observations",
        data={
            "crop_id": "invalid_crop_xyz",
            "crop_stage": "VEGETATIVE",
            "symptoms": '["Yellow spots"]',
            "village": "Village",
            "district": "District",
            "state": "State"
        },
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )
    
    assert response.status_code == 400
    assert "Invalid or inactive crop" in response.json()["detail"]

def test_manual_escalate(client):
    img_bytes = create_synthetic_image_bytes()
    res = client.post(
        "/api/observations",
        data={
            "crop_id": "tomato",
            "crop_stage": "FRUITING",
            "symptoms": '["Dark lesions"]',
            "village": "Village",
            "district": "District",
            "state": "State"
        },
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )
    obs_id = res.json()["observation_id"]

    esc_res = client.post(
        f"/api/observations/{obs_id}/escalate",
        json={"reason_notes": "Farmer concerned about spreading spots"}
    )
    assert esc_res.status_code == 200
    esc_data = esc_res.json()
    assert esc_data["reason"] == "MANUAL_FARMER_REQUEST"

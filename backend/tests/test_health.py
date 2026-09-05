def test_health_check_endpoint(client):
    """Test /api/health endpoint response structure and values."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["ml_mode"] in ["DEMO", "REAL"]
    assert "app_name" in data
    assert "environment" in data

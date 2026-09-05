import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.constants import UserRole

client = TestClient(app)

def test_security_utilities():
    raw_pass = "SecurePass123!"
    hashed = hash_password(raw_pass)
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

    token = create_access_token({"sub": "user-123", "role": "FARMER"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["role"] == "FARMER"

def test_auth_demo_logins():
    # 1. Farmer Demo Login
    res_farmer = client.post("/api/auth/demo-login", json={"role": "farmer"})
    assert res_farmer.status_code == 200
    data_farmer = res_farmer.json()
    assert "token" in data_farmer
    assert data_farmer["user"]["role"] == "FARMER"
    assert "HS-FARMER" in data_farmer["user"]["farmer_code"]

    # 2. Expert Demo Login
    res_expert = client.post("/api/auth/demo-login", json={"role": "expert"})
    assert res_expert.status_code == 200
    data_expert = res_expert.json()
    assert "token" in data_expert
    assert data_expert["user"]["role"] == "EXPERT"

    # 3. Admin Demo Login
    res_admin = client.post("/api/auth/demo-login", json={"role": "admin"})
    assert res_admin.status_code == 200
    data_admin = res_admin.json()
    assert "token" in data_admin
    assert data_admin["user"]["role"] == "ADMIN"

def test_auth_registration_and_login():
    reg_email = "new_farmer_test@hortisentry.demo"
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "New Test Farmer",
            "email": reg_email,
            "password": "Password123!",
            "role": "FARMER",
            "location": "Madurai, Tamil Nadu"
        }
    )
    # 201 Created or 400 if already exists from prior run
    if reg_res.status_code == 201:
        reg_data = reg_res.json()
        assert "token" not in reg_data
        assert "message" in reg_data
        assert reg_data["user"]["email"] == reg_email
        assert reg_data["user"]["role"] == "FARMER"

    # Login
    login_res = client.post(
        "/api/auth/login",
        json={"email": reg_email, "password": "Password123!"}
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "token" in login_data

    # Current User Profile
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login_data['token']}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == reg_email

def test_admin_endpoints(client):
    # Authenticate as Admin
    login_res = client.post("/api/auth/demo-login", json={"role": "admin"})
    assert login_res.status_code == 200
    admin_token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Dashboard
    dash_res = client.get("/api/admin/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash = dash_res.json()
    assert "total_farmers" in dash
    assert "total_observations" in dash
    assert "pending_reviews" in dash

    # 2. Analytics & KPI
    analytics_res = client.get("/api/admin/analytics", headers=headers)
    assert analytics_res.status_code == 200
    analytics = analytics_res.json()
    assert "time_to_expert_kpi" in analytics
    assert "baseline_comparison" in analytics
    kpi = analytics["time_to_expert_kpi"]
    assert "average_hours" in kpi
    assert "target_hours" in kpi
    assert kpi["target_hours"] == 6.0
    base = analytics["baseline_comparison"]
    assert base["baseline_review_time_hours"] == 48.0
    assert base["improvement_percentage"] > 0

    # 3. Model & Dataset Metrics
    m_res = client.get("/api/admin/model-metrics", headers=headers)
    assert m_res.status_code == 200
    assert "accuracy" in m_res.json()

    d_res = client.get("/api/admin/dataset-metrics", headers=headers)
    assert d_res.status_code == 200

    # 4. Users List
    u_res = client.get("/api/admin/users", headers=headers)
    assert u_res.status_code == 200
    assert len(u_res.json()["users"]) > 0

    # 5. Audit Logs
    audit_res = client.get("/api/admin/audit-logs", headers=headers)
    assert audit_res.status_code == 200
    assert isinstance(audit_res.json(), list)

def test_notifications_endpoints():
    # Login as demo farmer
    login_res = client.post("/api/auth/demo-login", json={"role": "farmer"})
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch notifications
    notifs_res = client.get("/api/notifications", headers=headers)
    assert notifs_res.status_code == 200
    notifs = notifs_res.json()
    assert "unread_count" in notifs
    assert "items" in notifs

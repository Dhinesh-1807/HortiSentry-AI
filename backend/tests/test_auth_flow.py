import pytest
from app.core.constants import VerificationStatus, AccountStatus, UserRole

def test_01_register_new_farmer(client):
    """TEST 1: Register new Farmer -> Account created, no automatic login, redirect to Login message."""
    res = client.post(
        "/api/auth/register",
        json={
            "name": "Ramu Farmer",
            "email": "ramu.farmer@hortisentry.demo",
            "password": "FarmerPassword123!",
            "role": "FARMER",
            "location": "Thanjavur, Tamil Nadu"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert "token" not in data, "Must NOT automatically return a login token on registration"
    assert data["message"] == "Registration successful! Please sign in with your new account."
    assert data["user"]["role"] == "FARMER"
    assert data["user"]["verification_status"] == "NOT_REQUIRED"
    assert data["user"]["account_status"] == "ACTIVE"

def test_02_login_new_farmer(client):
    """TEST 2: Login with newly registered Farmer -> Farmer Dashboard access."""
    # Register first
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Kavitha Farmer",
            "email": "kavitha.farmer@hortisentry.demo",
            "password": "FarmerPassword123!",
            "role": "FARMER",
            "location": "Salem, Tamil Nadu"
        }
    )
    assert reg_res.status_code == 201
    assert "token" not in reg_res.json()

    # Login
    res = client.post(
        "/api/auth/login",
        json={
            "email": "kavitha.farmer@hortisentry.demo",
            "password": "FarmerPassword123!"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["role"] == "FARMER"
    assert data["user"]["verification_status"] == "NOT_REQUIRED"

def test_03_register_new_expert(client):
    """TEST 3: Register new Expert -> Account created, no auto login, status = PENDING."""
    res = client.post(
        "/api/auth/register",
        json={
            "name": "Dr. Subash Chandra",
            "email": "dr.subash@horti.res.in",
            "password": "ExpertPassword123!",
            "role": "EXPERT",
            "location": "ICAR Central Horticulture Institute"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert "token" not in data, "Must NOT automatically return a login token on expert registration"
    assert data["message"] == "Registration successful! Please sign in with your new account."
    assert data["user"]["role"] == "EXPERT"
    assert data["user"]["verification_status"] == "PENDING"
    assert data["user"]["account_status"] == "ACTIVE"

def test_04_login_as_pending_expert(client):
    """TEST 4: Login as pending Expert -> Expert Portal access DENIED."""
    # Register pending expert
    client.post(
        "/api/auth/register",
        json={
            "name": "Dr. Subash Chandra",
            "email": "dr.subash@horti.res.in",
            "password": "ExpertPassword123!",
            "role": "EXPERT",
            "location": "ICAR Central Horticulture Institute"
        }
    )

    # Login
    res = client.post(
        "/api/auth/login",
        json={
            "email": "dr.subash@horti.res.in",
            "password": "ExpertPassword123!"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["role"] == "EXPERT"
    assert data["user"]["verification_status"] == "PENDING"

    # Try accessing expert API with this pending token -> must return HTTP 403
    pending_headers = {"Authorization": f"Bearer {data['token']}"}
    portal_res = client.get("/api/expert/dashboard/stats", headers=pending_headers)
    assert portal_res.status_code == 403
    assert "awaiting verification" in portal_res.json()["detail"].lower()

def test_05_admin_approves_expert(client):
    """TEST 5: Admin approves the Expert -> Expert verification_status = VERIFIED."""
    # 1. Register expert
    client.post(
        "/api/auth/register",
        json={
            "name": "Dr. Subash Chandra",
            "email": "dr.subash@horti.res.in",
            "password": "ExpertPassword123!",
            "role": "EXPERT"
        }
    )

    # 2. Admin login
    admin_login = client.post("/api/auth/demo-login", json={"role": "admin"})
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Find expert user id
    verif_res = client.get("/api/admin/expert-verifications", headers=admin_headers)
    assert verif_res.status_code == 200
    experts = verif_res.json()
    target_expert = next((e for e in experts if e["email"] == "dr.subash@horti.res.in"), None)
    assert target_expert is not None
    assert target_expert["verification_status"] == "PENDING"
    expert_id = target_expert["id"]

    # 4. Admin approves expert
    approve_res = client.post(
        f"/api/admin/expert-verifications/{expert_id}/verify",
        headers=admin_headers,
        json={"action": "APPROVE"}
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["expert"]["verification_status"] == "VERIFIED"

def test_06_verified_expert_logs_in(client):
    """TEST 6: Verified Expert logs in -> Expert Dashboard access allowed."""
    # 1. Register and approve
    client.post(
        "/api/auth/register",
        json={
            "name": "Dr. Subash Chandra",
            "email": "dr.subash@horti.res.in",
            "password": "ExpertPassword123!",
            "role": "EXPERT"
        }
    )
    admin_login = client.post("/api/auth/demo-login", json={"role": "admin"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['token']}"}
    verif_res = client.get("/api/admin/expert-verifications", headers=admin_headers)
    target_expert = next(e for e in verif_res.json() if e["email"] == "dr.subash@horti.res.in")
    client.post(
        f"/api/admin/expert-verifications/{target_expert['id']}/verify",
        headers=admin_headers,
        json={"action": "APPROVE"}
    )

    # 2. Expert logs in
    res = client.post(
        "/api/auth/login",
        json={
            "email": "dr.subash@horti.res.in",
            "password": "ExpertPassword123!"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["verification_status"] == "VERIFIED"
    assert data["user"]["role"] == "EXPERT"

    # 3. Verified expert accesses expert dashboard
    expert_headers = {"Authorization": f"Bearer {data['token']}"}
    dash_res = client.get("/api/expert/dashboard/stats", headers=expert_headers)
    assert dash_res.status_code == 200

def test_07_farmer_tries_expert_direct_access(client):
    """TEST 7: Farmer tries to access Expert Dashboard API directly -> Access denied."""
    farmer_login = client.post("/api/auth/demo-login", json={"role": "farmer"})
    assert farmer_login.status_code == 200
    farmer_token = farmer_login.json()["token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}

    res = client.get("/api/expert/dashboard/stats", headers=farmer_headers)
    assert res.status_code == 403
    assert "Expert role required" in res.json()["detail"]

def test_08_farmer_tries_expert_api(client):
    """TEST 8: Farmer tries Expert API -> HTTP 403."""
    farmer_login = client.post("/api/auth/demo-login", json={"role": "farmer"})
    farmer_headers = {"Authorization": f"Bearer {farmer_login.json()['token']}"}

    cases_res = client.get("/api/expert/cases", headers=farmer_headers)
    assert cases_res.status_code == 403
    assert "Expert role required" in cases_res.json()["detail"]

def test_09_pending_expert_tries_expert_api(client):
    """TEST 9: Pending Expert tries Expert API -> HTTP 403."""
    client.post(
        "/api/auth/register",
        json={
            "name": "Dr. Pending Expert",
            "email": "pending.expert@horti.res.in",
            "password": "ExpertPassword123!",
            "role": "EXPERT"
        }
    )
    login_res = client.post(
        "/api/auth/login",
        json={"email": "pending.expert@horti.res.in", "password": "ExpertPassword123!"}
    )
    pending_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

    res = client.get("/api/expert/reviews", headers=pending_headers)
    assert res.status_code == 403
    assert "awaiting verification" in res.json()["detail"].lower()

def test_10_verified_expert_accesses_expert_api(client):
    """TEST 10: Verified Expert accesses Expert API -> Access allowed (HTTP 200)."""
    login_res = client.post("/api/auth/demo-login", json={"role": "expert"})
    expert_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

    res = client.get("/api/expert/reviews", headers=expert_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_11_rejected_expert_logs_in(client):
    """TEST 11: Rejected Expert logs in -> Expert Portal access denied."""
    # 1. Register expert
    client.post(
        "/api/auth/register",
        json={
            "name": "Dr. Rejected Expert",
            "email": "rejected.expert@horti.res.in",
            "password": "ExpertPassword123!",
            "role": "EXPERT"
        }
    )

    # 2. Admin rejects the expert
    admin_login = client.post("/api/auth/demo-login", json={"role": "admin"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['token']}"}

    verif_res = client.get("/api/admin/expert-verifications", headers=admin_headers)
    target = next((e for e in verif_res.json() if e["email"] == "rejected.expert@horti.res.in"), None)
    assert target is not None

    reject_res = client.post(
        f"/api/admin/expert-verifications/{target['id']}/verify",
        headers=admin_headers,
        json={"action": "REJECT"}
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["expert"]["verification_status"] == "REJECTED"

    # 3. Rejected expert logs in
    login_res = client.post(
        "/api/auth/login",
        json={"email": "rejected.expert@horti.res.in", "password": "ExpertPassword123!"}
    )
    assert login_res.status_code == 200
    assert login_res.json()["user"]["verification_status"] == "REJECTED"

    # 4. Accessing expert API -> HTTP 403 with rejection explanation
    rejected_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}
    portal_res = client.get("/api/expert/dashboard/stats", headers=rejected_headers)
    assert portal_res.status_code == 403
    assert "not approved" in portal_res.json()["detail"].lower()

def test_12_suspended_expert_logs_in(client):
    """TEST 12: Suspended Expert logs in -> Expert Portal access denied."""
    # 1. Register expert
    client.post(
        "/api/auth/register",
        json={
            "name": "Dr. Suspended Expert",
            "email": "suspended.expert@horti.res.in",
            "password": "ExpertPassword123!",
            "role": "EXPERT"
        }
    )

    # 2. Admin approves and then suspends the expert
    admin_login = client.post("/api/auth/demo-login", json={"role": "admin"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['token']}"}

    verif_res = client.get("/api/admin/expert-verifications", headers=admin_headers)
    target = next((e for e in verif_res.json() if e["email"] == "suspended.expert@horti.res.in"), None)
    assert target is not None

    suspend_res = client.post(
        f"/api/admin/expert-verifications/{target['id']}/verify",
        headers=admin_headers,
        json={"action": "SUSPEND"}
    )
    assert suspend_res.status_code == 200
    assert suspend_res.json()["expert"]["verification_status"] == "SUSPENDED"

    # 3. Suspended expert attempts login or uses token
    login_res = client.post(
        "/api/auth/login",
        json={"email": "suspended.expert@horti.res.in", "password": "ExpertPassword123!"}
    )
    if login_res.status_code == 200:
        assert login_res.json()["user"]["verification_status"] == "SUSPENDED"
        suspended_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}
        portal_res = client.get("/api/expert/dashboard/stats", headers=suspended_headers)
        assert portal_res.status_code == 403
        assert "suspended" in portal_res.json()["detail"].lower()
    else:
        assert login_res.status_code == 403
        assert "suspended" in login_res.json()["detail"].lower()

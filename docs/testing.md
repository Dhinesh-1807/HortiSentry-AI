# HortiSentry — Testing & Verification Architecture

---

## 1. Automated Test Suite Overview

HortiSentry maintains comprehensive automated test coverage across all application tiers:

```
Full Test Verification Architecture
├── Backend Pytest Suite (72 Tests across 12 Test Files)
│   ├── Unit Tests (Crops, Image Quality, Escalation Engine, Database Models)
│   ├── API Endpoint Tests (Health, Model Status, Multi-Crop Predict, Observations, Expert, Auth)
│   ├── Integration Test Suite (test_phase8_integration.py)
│   └── End-to-End Integration Suite (test_e2e_integration_workflow.py)
├── Frontend Vitest Suite (6 Tests)
│   ├── Farmer Workflow Component Tests
│   └── Expert Dashboard Component Tests
└── Automated Verification Suite (scripts/verify_phase13.py, scripts/generate_test_report.py)
    ├── REST API Endpoint Verification Tests
    └── Artifact Integrity & Performance Benchmark Tests
```

---

## 2. Test Execution & Coverage Details

### 2.1 Backend Pytest Test Suite (72 Tests)
```powershell
backend\venv\Scripts\pytest.exe backend/tests/
```
- **Total Test Cases:** **72**
- **Pass Rate:** **100%** (72 Passed / 0 Failed)
- **Coverage Areas:**
  1. `test_auth_admin_notifications.py` — Authentication, RBAC, Admin approval, Notification dispatch.
  2. `test_auth_flow.py` — Login, registration, token generation, role verification.
  3. `test_config.py` & `test_database.py` — System settings, DB connections, ORM models.
  4. `test_dataset_prep.py` — Dataset manifest validation, splits verification.
  5. `test_e2e_flow.py` — Full backend observation lifecycle.
  6. `test_e2e_integration_workflow.py` — **End-to-End Workflow & Escalation Rules** (Cases A, B, C, D, Image upload edge cases, Expert review, DB state transitions).
  7. `test_evidence_engine.py` — Agricultural evidence retrieval & ICAR/TNAU source ranking.
  8. `test_expert.py` — Expert queue filtering, case assignments, review completion.
  9. `test_health.py` — System health & multi-crop model status endpoints.
  10. `test_image_quality.py` — Blur detection, exposure validation, image dimension checks.
  11. `test_ml_pipeline.py` — MobileNetV3 Small model forward pass, checkpoint saving/loading, metrics.
  12. `test_observations.py` & `test_phase10_evidence.py` — Observation CRUD, symptom parsing, evidence fusion.

---

## 3. End-to-End Integration Test Scenarios (`test_e2e_integration_workflow.py`)

| Test ID | Test Scenario | Verification Focus | Status |
| :--- | :--- | :--- | :---: |
| `TEST-OBS-001` | Farmer Observation Submission | Selects crop, stage, symptoms, location, uploads image; DB record created | **PASS** |
| `TEST-IMG-001` | Image Upload Validation | Valid WEBP accepted; unsupported (.txt), oversized (>10MB), corrupt rejected | **PASS** |
| `TEST-INF-001` | AI Model Inference | `POST /api/predict` returns top_predictions, confidence, model_version 'tomato-v1' | **PASS** |
| `TEST-ESC-001` | Escalation Engine Rules | Case A (High conf/low risk $\rightarrow$ Monitoring); Cases B, C, D $\rightarrow$ Escalation DB record | **PASS** |
| `TEST-EXP-001` | Expert Queue & RBAC Security | 200 OK for verified expert token; 401/403 enforced for unauthenticated requests | **PASS** |
| `TEST-REV-001` | Expert Review Workflow | Expert opens case, completes review; DB status updated to REVIEWED | **PASS** |
| `TEST-E2E-001` | Full E2E Lifecycle | Single test verifying full API HTTP response schemas AND SQLite DB state transitions | **PASS** |

---

## 4. Test Reports & Artifact Generation

Automated test execution outputs structured reports:
- `reports/test_report.json`
- `reports/test_report.md`
- `reports/ml/test_metrics.json`
- `reports/error-analysis.md`

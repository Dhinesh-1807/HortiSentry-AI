# HortiSentry — Testing & Verification Architecture

---

## 1. Automated Test Suite Overview

HortiSentry maintains comprehensive test suites across all 3 tiers:

```
Full Test Verification Architecture
├── Backend Pytest Suite (36 Tests)
│   ├── Unit Tests (Crops, Image Quality, Escalation Engine)
│   ├── API Endpoint Tests (Health, Model Status, Predict, Observations, Expert)
│   └── Integration Test Suite (test_phase8_integration.py)
├── Frontend Vitest Suite (6 Tests)
│   ├── Farmer Workflow Component Tests
│   └── Expert Dashboard Component Tests
└── End-to-End Automated Script (scripts/verify_phase8_e2e.py)
    ├── 13 REST API Endpoint HTTP Verification Tests
    └── 4 Full System E2E Scenarios (Real Inference, Preservation, Security, Dual-Mode)
```

---

## 2. Test Commands & Verification Procedures

### 2.1 Backend Pytest Test Suite (36 Tests)
```powershell
cd backend
.\venv\Scripts\python.exe -m pytest -v
```
- **Execution Time:** ~10 seconds
- **Pass Rate:** **100%** (36 Passed / 0 Failed)

### 2.2 Frontend Vitest Test Suite (6 Tests)
```powershell
cd frontend
npm test
```
- **Execution Time:** < 1 second
- **Pass Rate:** **100%** (6 Passed / 0 Failed)

### 2.3 Automated E2E Verification Script
```powershell
python scripts/verify_phase8_e2e.py
```
- **Verifies:** 13 REST API endpoints and 4 full-system scenarios.
- **Pass Rate:** **100%** (13/13 APIs Passed, 4/4 Scenarios Passed)
- **Generates Reports:** `reports/phase8/api_test_results.json`, `reports/phase8/e2e_test_results.json`

### 2.4 Frontend Production Build Verification
```powershell
cd frontend
npm run build
```
- **Verifies:** TypeScript compilation, asset bundling, and Vite production output.

# HortiSentry — Requirements Traceability Matrix (RTM)

| Requirement ID | Description | Component / File | Verification Method | Status |
| :--- | :--- | :--- | :--- | :---: |
| **REQ-FARM-01** | Mobile-first responsive UI | `frontend/src/layouts/AppLayout.tsx` | Browser Test | **PASS** |
| **REQ-FARM-02** | Crop selection step | `frontend/src/pages/farmer/ObservationWizard.tsx` | Vitest / Browser | **PASS** |
| **REQ-FARM-03** | Image upload with 10MB limit & extension check | `frontend/src/pages/farmer/ObservationWizard.tsx` | Vitest / Browser | **PASS** |
| **REQ-FARM-04** | Symptom multi-select | `frontend/src/pages/farmer/ObservationWizard.tsx` | Browser Test | **PASS** |
| **REQ-FARM-05** | Growth stage selection | `frontend/src/pages/farmer/ObservationWizard.tsx` | Browser Test | **PASS** |
| **REQ-FARM-06** | Regional non-identifying location | `frontend/src/pages/farmer/ObservationWizard.tsx` | Browser Test | **PASS** |
| **REQ-FARM-07** | Review & submit workflow | `frontend/src/pages/farmer/ObservationWizard.tsx` | Browser Test | **PASS** |
| **REQ-FARM-08** | AI Result screen with confidence % & mode tag | `frontend/src/pages/farmer/ObservationResult.tsx` | Browser Test | **PASS** |
| **REQ-FARM-09** | Image quality feedback (blur/exposure) | `frontend/src/pages/farmer/ObservationResult.tsx` | Browser Test | **PASS** |
| **REQ-FARM-10** | Manual & automatic expert escalation CTA | `frontend/src/pages/farmer/ObservationResult.tsx` | Browser Test | **PASS** |
| **REQ-FARM-11** | Observation history & case detail views | `frontend/src/pages/farmer/ObservationHistory.tsx` | Browser Test | **PASS** |
| **REQ-EXP-01** | Expert dashboard KPI metrics (5 stat cards) | `frontend/src/pages/expert/ExpertHome.tsx` | Browser Test | **PASS** |
| **REQ-EXP-02** | Filterable & searchable review queue | `frontend/src/pages/expert/ReviewQueue.tsx` | Browser Test | **PASS** |
| **REQ-EXP-03** | Split-pane case inspection workspace | `frontend/src/pages/expert/CaseDetail.tsx` | Browser Test | **PASS** |
| **REQ-EXP-04** | Image viewer with zoom & quality overlay | `frontend/src/components/expert/CaseImageViewer.tsx` | Browser Test | **PASS** |
| **REQ-EXP-05** | One-click AI validation & prediction override | `frontend/src/components/expert/ExpertDecisionPanel.tsx` | Vitest / Browser | **PASS** |
| **REQ-EXP-06** | Request additional farmer info modal | `frontend/src/components/expert/RequestInfoDialog.tsx` | Browser Test | **PASS** |
| **REQ-EXP-07** | Dual prediction preservation in DB | `backend/app/services/expert_service.py` | Pytest / Vitest | **PASS** |
| **REQ-EXP-08** | Turnaround duration tracking | `backend/app/services/expert_service.py` | Pytest / Browser | **PASS** |
| **REQ-EXP-09** | Completed review audit trail | `frontend/src/pages/expert/ReviewHistory.tsx` | Browser Test | **PASS** |
| **REQ-ML-01** | MobileNetV3 Small transfer learning pipeline | `ml/model.py`, `scripts/train_and_evaluate_tomato.py` | Pytest / Script | **PASS** |
| **REQ-ML-02** | Held-out test set evaluation (Accuracy, F1, Support) | `scripts/train_and_evaluate_tomato.py` | Quantitative Audit | **PASS** |
| **REQ-ML-03** | Class-level failure analysis report | `reports/error-analysis.md` | Failure Inspection | **PASS** |
| **REQ-TEST-01** | End-to-End integration test suite (Cases A, B, C, D) | `backend/tests/test_e2e_integration_workflow.py` | Pytest (72 Tests) | **PASS** |
| **REQ-STAKE-01** | Stakeholder trade-off analysis documentation | `docs/stakeholder_tradeoffs.md` | Documentation Audit | **PASS** |

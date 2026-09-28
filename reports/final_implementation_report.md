# HortiSentry — Areas to Improve & Next Steps Implementation Report

## Executive Summary
This report records the complete implementation and quantitative verification of the three requested improvement areas in the existing HortiSentry codebase:
1. **MobileNetV3 Small Supervised Training & Quantitative Validation**
2. **End-to-End Integration Testing & Escalation Workflow Verification**
3. **Stakeholder Trade-off Documentation & System Architecture Alignment**

---

## 1. MODEL: Training & Quantitative Validation

- **Training Status:** **COMPLETE & VALIDATED**
- **Model Version:** `tomato-v1` (`TomatoMobileNetV3` architecture with MobileNetV3 Small backbone)
- **Dataset Version:** 6,271 tomato leaf images across 4 canonical classes (`Healthy`, `Early_Blight`, `Late_Blight`, `Septoria_Leaf_Spot`)
- **Dataset Split:** Train: 4,386 images (70%), Validation: 938 images (15%), Test: 947 images (15% held-out test set)
- **Quantitative Test Set Metrics (N=947):**
  - **Test Accuracy:** **99.37%** (941 / 947 correct)
  - **Macro F1 Score:** **0.9927 (99.27%)**
  - **Weighted F1 Score:** **0.9937 (99.37%)**
  - **Per-Class Metrics:**
    - `Healthy`: Precision = 0.9959, Recall = **1.0000**, F1 = **0.9979** (Support: 241)
    - `Early_Blight`: Precision = 0.9801, Recall = 0.9867, F1 = **0.9834** (Support: 150)
    - `Late_Blight`: Precision = 0.9930, Recall = 0.9862, F1 = **0.9896** (Support: 289)
    - `Septoria_Leaf_Spot`: Precision = **1.0000**, Recall = **1.0000**, F1 = **1.0000** (Support: 267)
  - **Average Inference Latency:** **9.55 ms / image** (~104.7 images/second on CPU)
- **Confusion Matrix Status:** **GENERATED & VERIFIED** (`reports/confusion_matrix.png` & `reports/confusion_matrix.csv`)
  ```
  Raw Counts (Test Set N=947):
  True \ Pred | Healthy | Early_Blight | Late_Blight | Septoria_Leaf_Spot
  Healthy     |   241   |      0       |      0      |        0
  Early_Blight|     0   |    148       |      2      |        0
  Late_Blight |     1   |      3       |    285      |        0
  Septoria    |     0   |      0       |      0      |      267
  ```
- **Class-Level Failure Analysis Status:** **COMPLETE & DOCUMENTED** (`reports/error-analysis.md`, `reports/error-analysis.json`, `reports/error-analysis.csv`)
  - Total misclassifications: 6 out of 947 test images (0.63% error rate).
  - Failure pattern 1: Early Blight vs Late Blight lesion overlap (5 samples; concentric ring halos mimicking water-soaked borders).
  - Failure pattern 2: Background foliage area ratio (1 sample; tiny peripheral lesion on large green leaf).
  - System Mitigation: All disease-to-disease misclassifications yielded confidence scores $< 0.70$, automatically triggering HortiSentry's confidence threshold to escalate cases to human agronomists.

---

## 2. INTEGRATION: End-to-End Workflow Verification

- **Farmer $\rightarrow$ Backend Integration:** **PASS** (Wizard submission with crop, stage, symptoms, location, and photo upload verified via `POST /api/observations`).
- **Image Upload Validation:** **PASS** (WEBP/JPG/PNG processed cleanly; unsupported `.txt`, oversized $>10\text{MB}$, and corrupted headers rejected with proper HTTP 4xx error codes).
- **AI Inference Execution:** **PASS** (MobileNetV3 model executes real-time inference via `POST /api/predict`, returning predictions, top-3 probabilities, confidence, and `tomato-v1` versioning).
- **Escalation Engine:** **PASS** (Routine high-confidence cases assigned monitoring status; Cases B, C, D with low confidence, high risk, or dark images automatically create DB `Escalation` records).
- **Expert Queue & RBAC Security:** **PASS** (Queue endpoint enforces role-based authorization; returns review tasks for verified agronomists, blocks unauthenticated users with 401/403).
- **Expert Review Completion:** **PASS** (Agronomists inspect cases, submit diagnostic assessments via `POST /api/expert/reviews/{id}/complete`, storing authoritative reviews in DB).
- **Farmer Status Update:** **PASS** (Observation status transitions seamlessly from `SUBMITTED` $\rightarrow$ `EXPERT_REVIEW_REQUIRED` $\rightarrow$ `REVIEWED`).

---

## 3. TESTING: Test Execution Summary

- **Total Backend Test Suite:** **72 Tests** across 12 test files.
- **Passed:** **72 (100.0%)**
- **Failed:** **0 (0.0%)**
- **Automated Integration Test File:** `backend/tests/test_e2e_integration_workflow.py` (7/7 PASSED).
- **Test Execution Reports Generated:** `reports/test_report.json` & `reports/test_report.md`.

---

## 4. STAKEHOLDER ANALYSIS: Trade-Off Alignment

- **Farmer Trade-Offs Documented:** **YES** (`docs/stakeholder_tradeoffs.md`). Balances minimal data-entry friction (structured symptom checkboxes) against the risk of user fatigue from excessive mandatory fields.
- **Cooperative / Buyer Trade-Offs Documented:** **YES** (`docs/stakeholder_tradeoffs.md`). Balances strict produce quality assurance & early disease detection (*Late Blight*) against unverified automated diagnosis.
- **Expert Workload Trade-Offs Documented:** **YES** (`docs/stakeholder_tradeoffs.md`). Balances agronomist queue capacity against over-escalation of routine cases using a 0.70 engineering confidence threshold.
- **AI Screening vs. Human Verification Documented:** **YES** (`docs/stakeholder_tradeoffs.md`). Establishes AI as decision support; certified human agronomists retain binding review authority for uncertain/high-risk cases.

---

## 5. DOCUMENTATION: Updated Files

The following documentation suite files were created or updated:
1. `README.md` — Core system principles & overview.
2. `docs/ml_model.md` — Model architecture, quantitative test evaluation, confusion matrix, failure analysis, and trade-off summary.
3. `docs/testing.md` — 72-test backend suite breakdown, E2E integration test scenarios, and verification procedures.
4. `docs/architecture.md` — Multi-crop tier specifications, mermaid diagrams, state machines, and security architecture.
5. `docs/risk-register.md` — Updated risk register with R-01 through R-08 risks and mitigations.
6. `docs/requirements-traceability.md` — Requirements traceability matrix mapping REQ-ML-01..03, REQ-TEST-01, REQ-STAKE-01.
7. `docs/stakeholder_tradeoffs.md` — Comprehensive stakeholder trade-off analysis.

---

## 6. KNOWN LIMITATIONS

1. **In-Situ Field Background Variance:** While MobileNetV3 Small achieves 99.37% accuracy on benchmark test foliage, complex field backgrounds with mixed weeds or heavy shadows may benefit from ongoing field dataset expansion.
2. **Prototype Escalation Threshold:** The 0.70 confidence threshold serves as an engineering rule-of-thumb; further empirical tuning across regional cooperative pilot deployments is recommended.

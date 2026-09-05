# HortiSentry — Phase 8 E2E System Integration & Test Report

**Project Name:** HortiSentry  
**Full Title:** HortiSentry — AI-Powered Horticultural Disease Observation and Expert Escalation System  
**Tagline:** See Early. Act Smart. Protect Crops.  

**Target Crop:** Tomato (*Solanum lycopersicum*)  
**Evaluation Date:** September 2, 2026  
**Active Model Artifact:** `ml/artifacts/tomato_v1.pt` (PyTorch `MobileNetV3 Small`)  
**Phase 8 Status:** `PHASE_8_COMPLETE`  

---

## 1. Executive Integration Summary

Phase 8 verified the end-to-end functionality, performance, security, and data integrity of HortiSentry across all 3 tiers (React Frontend, FastAPI Backend Core, PyTorch ML Engine & SQLite Database).

### Core Lifecycle Proved
$$\text{Farmer Observation} \longrightarrow \text{Image Upload \& Quality Check} \longrightarrow \text{Real PyTorch Inference} \longrightarrow \text{Escalation Engine} \longrightarrow \text{Expert Review Portal} \longrightarrow \text{Farmer Status Update}$$

- **Backend Pytest Suite:** `36 / 36 PASSED` (`100%`)
- **Frontend Vitest Suite:** `6 / 6 PASSED` (`100%`)
- **API Endpoints Verified:** `13 / 13 PASSED` (`100%`)
- **End-to-End Scenarios Verified:** `4 / 4 PASSED` (`100%`)

---

## 2. API Endpoint Verification Results

All 13 REST API endpoints were tested with actual HTTP requests and measured response latencies:

| Endpoint | Method | Status | Latency | Result | Notes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `/api/health` | `GET` | `200 OK` | 19.55 ms | **PASSED** | DB connected, `ML_MODE=REAL` |
| `/api/model-status` | `GET` | `200 OK` | 5.99 ms | **PASSED** | Active version `tomato-v1`, 4 classes |
| `/api/crops` | `GET` | `200 OK` | 14.92 ms | **PASSED** | Tomato config loaded from `config/crops.yaml` |
| `/api/predict` | `POST` | `200 OK` | 60.77 ms | **PASSED** | Real PyTorch inference (`is_demo_mode = false`) |
| `/api/observations` | `POST` | `201 Created` | 88.82 ms | **PASSED** | Image upload + quality check + AI prediction |
| `/api/observations` | `GET` | `200 OK` | 25.37 ms | **PASSED** | Observation list retrieval |
| `/api/observations/{id}` | `GET` | `200 OK` | 13.03 ms | **PASSED** | Case detail with AI prediction & escalation |
| `/api/observations/{id}/escalate` | `POST` | `200 OK` | 23.92 ms | **PASSED** | Manual escalation trigger (`MANUAL_FARMER_REQUEST`) |
| `/api/expert/dashboard/stats` | `GET` | `200 OK` | 14.46 ms | **PASSED** | Review queue metrics & turn-around stats |
| `/api/expert/reviews` | `GET` | `200 OK` | 25.56 ms | **PASSED** | Expert pending review queue |
| `/api/expert/reviews/{id}` | `GET` | `200 OK` | 23.52 ms | **PASSED** | Expert inspection detail |
| `/api/expert/reviews/{id}/complete` | `POST` | `200 OK` | 16.31 ms | **PASSED** | Expert diagnosis validation/override |
| `/api/expert/reviews/{id}/request-info` | `POST` | `200 OK` | 26.30 ms | **PASSED** | Request more info from farmer (`NEEDS_INFO`) |

---

## 3. Real Model Inference Verification

Using actual test leaf image `data/test/Healthy/Healthy_01005.JPG`:

```json
{
  "predicted_class": "Healthy",
  "confidence": 0.9998,
  "top_predictions": [
    { "class": "Healthy", "confidence": 0.9998 },
    { "class": "Late_Blight", "confidence": 0.0002 },
    { "class": "Early_Blight", "confidence": 0.0 }
  ],
  "model_version": "tomato-v1",
  "inference_time_ms": 30.73,
  "is_demo_mode": false,
  "needs_expert_review": false
}
```
- **Execution Mode:** Real PyTorch inference (`ML_MODE=REAL`).
- **Model Version:** `tomato-v1`
- **Output:** Predicted `Healthy` with **99.98% confidence** and **30.73 ms latency**.

---

## 4. AI $\rightarrow$ Expert Escalation Condition Testing

Four distinct escalation pathways were verified:

1. **Low Confidence Escalation ($< 0.70$):** Automatically triggers `LOW_CONFIDENCE` escalation, setting observation status to `PENDING_REVIEW`.
2. **Poor Image Quality Escalation:** Blurry or improperly exposed uploads trigger `POOR_IMAGE_QUALITY` escalation.
3. **Manual Farmer Request:** Farmers can manually escalate any case via `POST /api/observations/{id}/escalate`, creating a `MANUAL_FARMER_REQUEST` escalation record.
4. **Normal High Confidence Case:** Cases with good image quality and confidence $\ge 0.70$ complete cleanly without creating unnecessary escalations.

---

## 5. Expert Decision Preservation Verification

Verified that AI predictions and Expert diagnoses are stored in separate database tables:
- **AI Prediction Table (`predictions`):** Preserves original AI prediction (`Healthy`, confidence `0.9998`, model `tomato-v1`).
- **Expert Review Table (`expert_reviews`):** Records authoritative expert diagnosis override (`Early Blight (Alternaria solani)`), expert notes, and completion timestamp.
- **Auditing Value:** Preserving the original AI prediction alongside the expert correction provides clean ground-truth labeling for future model retraining cycles.

---

## 6. Status Lifecycle State Machine

Enforcement of valid observation status transitions was verified:

$$\text{SUBMITTED} \longrightarrow \text{PENDING\_REVIEW} \longrightarrow \text{UNDER\_REVIEW} \longrightarrow \text{COMPLETED} \quad (\text{or } \text{NEEDS\_INFO})$$

| Initial Status | Event / Trigger | Resulting Status | Verified |
| :--- | :--- | :--- | :---: |
| `SUBMITTED` | Normal high confidence | `COMPLETED` | **YES** |
| `SUBMITTED` | Escalation triggered | `PENDING_REVIEW` | **YES** |
| `PENDING_REVIEW` | Expert opens case detail | `UNDER_REVIEW` | **YES** |
| `UNDER_REVIEW` | Expert submits diagnosis | `COMPLETED` | **YES** |
| `UNDER_REVIEW` | Expert requests more info | `NEEDS_INFO` | **YES** |

---

## 7. Security & Path Traversal Verification

1. **Path Traversal Protection:** Attempted upload with malicious filename `../../test_malicious.jpg`. The system sanitized the filename to UUID format and safely saved it inside `uploads/`, with **zero** files written outside the storage directory.
2. **Unsupported Extensions:** Upload of non-image file (`document.txt`) returned `400 Bad Request`.
3. **Oversized Files:** Files $> 10\text{MB}$ are rejected with `400 Bad Request`.
4. **MIME Validation:** Uploaded image byte headers are validated using PIL (`JPEG`/`PNG`/`WEBP`).

---

## 8. Dual-Mode Switchability Verification

- **`ML_MODE=REAL`:** Loads `TorchPredictor` (`tomato-v1`), returning `"is_demo_mode": false`.
- **`ML_MODE=DEMO`:** Uses `DemoPredictor`, returning `"is_demo_mode": true`.
- Dynamic mode switching executed cleanly without database corruption or application restart errors.

---

## 9. Database Integrity Audit

Checked foreign key constraints, timestamps, and cascading behaviors:
- `observations` $\leftrightarrow$ `crops`: Linked by `crop_id` foreign key (`tomato`).
- `observations` $\leftrightarrow$ `predictions`: 1-to-many relationship intact.
- `observations` $\leftrightarrow$ `escalations`: 1-to-many relationship intact.
- `observations` $\leftrightarrow$ `expert_reviews`: 1-to-many relationship intact.
- Zero orphan records or missing timestamps found.

---

## 10. Responsible AI UI Verification

Browser checks confirmed that the application communicates:
- **Decision Support Badge:** Displays *"Decision Support, Not Diagnostic Certification"* across Farmer and Expert views.
- **Uncertainty Guidance:** Explicitly notifies farmers when AI confidence is below $70\%$ or when expert review is pending.
- **Field Condition Disclaimer:** Notes that laboratory benchmark datasets may differ from ambient field farm conditions.

---

## 11. Measured Performance Latencies

- **System Health Check (`GET /api/health`):** **19.55 ms**
- **Model Status (`GET /api/model-status`):** **5.99 ms**
- **Single Image Prediction (`POST /api/predict`):** **60.77 ms** (CPU inference: **30.73 ms**)
- **Observation Submission (`POST /api/observations`):** **88.82 ms**
- **Expert Review Completion (`POST /api/expert/reviews/{id}/complete`):** **16.31 ms**

---

## 12. Known Limitations & Recommendations

1. **CPU Deployment Latency:** Real inference takes ~30-60 ms per image on CPU. For high-concurrency production setups, GPU accelerator deployment is recommended.
2. **Domain Shift:** Field-captured imagery under ambient solar radiation or heavy leaf shadowing should be evaluated separately using the `data/field_test/` dataset.

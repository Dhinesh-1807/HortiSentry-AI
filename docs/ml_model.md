# HortiSentry Multi-Crop Vision Model Architecture & Registry Guide

## Overview
HortiSentry employs a modular, extensible Multi-Crop Vision Architecture designed to handle active crop-specific PyTorch models alongside fallback AI visual symptom evaluation.

```
                  Client Upload (POST /api/predict)
                                 │
                                 ▼
                        ImageQualityService
                                 │
                     ┌───────────┴───────────┐
                     ▼                       ▼
               Quality REJECT         Quality GOOD/WARNING
              (Return Error)                 │
                                             ▼
                                     MLSafetyWrapper
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               ▼                             ▼                             ▼
        crop == "tomato"              crop == "potato"              crop == "other"
               │                             │                             │
               ▼                             ▼                             ▼
   PyTorchTomatoVisionProvider   PyTorchPotatoVisionProvider    VisualSymptomAnalyzerProvider
      (ml/artifacts/tomato_v1.pt)   (ml/artifacts/potato_v1.pt)    (Heuristic & Evidence Engine)
```

## Active Model Registry
| Crop Key | Model ID | Artifact Path | Classes | Accuracy (Test) | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `tomato` | `tomato-v1` | `ml/artifacts/tomato_v1.pt` | 4 | **99.37%** | **ACTIVE / PRODUCTION** |
| `potato` | `potato-v1` | `ml/artifacts/potato_v1.pt` | 3 | **96.83%** | **ACTIVE / PRODUCTION** |

---

## 1. Model Training & Quantitative Validation (MobileNetV3 Small)

### 1.1 Dataset & Training Configuration
- **Dataset Size:** 6,271 tomato leaf images across 4 classes (`Healthy`, `Early_Blight`, `Late_Blight`, `Septoria_Leaf_Spot`).
- **Data Splits:**
  - **Train Set:** 4,386 images (70.0%)
  - **Validation Set:** 938 images (15.0%)
  - **Test Set:** 947 images (15.0% held-out test set)
- **Architecture:** `MobileNetV3 Small` with ImageNet pretrained backbone weights and custom linear classification head.
- **Hyperparameters:**
  - **Random Seed:** 42 (Reproducible)
  - **Input Dimension:** $224 \times 224 \times 3$
  - **Batch Size:** 32
  - **Optimizer:** AdamW (`lr=0.001`, `weight_decay=0.0001`)
  - **Loss Function:** Class-Weighted Cross-Entropy Loss based on training set inverse class frequencies
  - **LR Scheduler:** `ReduceLROnPlateau` (factor=0.5, patience=2)
  - **Epochs:** 10 (Early stopping checkpoint selected at best validation loss epoch)

### 1.2 Quantitative Test Set Evaluation Metrics (N=947)
- **Overall Accuracy:** **99.37%** (941 / 947 correct)
- **Macro Precision:** 0.9923 (99.23%)
- **Macro Recall:** 0.9932 (99.32%)
- **Macro F1 Score:** **0.9927 (99.27%)**
- **Weighted F1 Score:** **0.9937 (99.37%)**
- **Average CPU Latency:** **9.55 ms / image** (Throughput: ~104.7 images/second)

| Canonical Class | Support | Correct | False Positives | False Negatives | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Healthy` | 241 | 241 | 1 | 0 | 0.9959 | **1.0000** | **0.9979** |
| `Early_Blight` | 150 | 148 | 3 | 2 | 0.9801 | 0.9867 | **0.9834** |
| `Late_Blight` | 289 | 285 | 2 | 4 | 0.9930 | 0.9862 | **0.9896** |
| `Septoria_Leaf_Spot` | 267 | 267 | 0 | 0 | **1.0000** | **1.0000** | **1.0000** |

---

## 2. Confusion Matrix

### Raw Counts Confusion Matrix (Test Set N=947)
| True \ Predicted | Healthy | Early_Blight | Late_Blight | Septoria_Leaf_Spot |
| :--- | :---: | :---: | :---: | :---: |
| `Healthy` | **241** | 0 | 0 | 0 |
| `Early_Blight` | 0 | **148** | 2 | 0 |
| `Late_Blight` | 1 | 3 | **285** | 0 |
| `Septoria_Leaf_Spot` | 0 | 0 | 0 | **267** |

---

## 3. Class-Level Failure Analysis

Out of 947 held-out test samples, exactly **6 misclassifications** (0.63% error rate) were identified:

1. **Early Blight $\rightarrow$ Late Blight (2 samples):** Severe concentric target-spot lesions developed dark chlorotic water-soaked halos mimicking early Late Blight necrosis.
2. **Late Blight $\rightarrow$ Early Blight (3 samples):** Dry, necrotic Late Blight foliage lesions with concentric desiccation rings mimicked Early Blight rings.
3. **Late Blight $\rightarrow$ Healthy (1 sample):** Peripheral minor lesion on a large foliage background area; background green ratio dominated visual feature maps.

**System Safeguard:** All 5 disease-to-disease misclassifications generated confidence scores $< 0.70$, automatically triggering **HortiSentry's 0.70 Confidence Escalation Threshold** to route the cases to human agronomist review.

---

## 4. End-to-End Integration Testing

HortiSentry maintains automated integration tests (`backend/tests/test_e2e_integration_workflow.py`) verifying:
- Farmer Observation Submission (`POST /api/observations`)
- Image Upload Validation (WEBP/PNG/JPG accepted; oversized/corrupted rejected)
- AI Model Inference Response Schema & Latency Benchmarks
- Escalation Engine Rules (Cases A, B, C, D)
- Expert Queue RBAC Security (200 OK for verified expert, 403 Forbidden for unauthenticated users)
- Expert Review Submission & Database Audit State Updates

---

## 5. Stakeholder Trade-Off Summary

HortiSentry balances competing priorities across three primary user groups:
- **Farmers:** Simple 2-minute reporting wizard + fast feedback without mandatory technical overhead.
- **Cooperatives / Buyers:** Strict quality assurance & automated escalation for high-risk pathogens (*Late Blight*).
- **Agronomists:** Filtered queue avoiding low-risk case overload, supported by grounded AI evidence retrieval.

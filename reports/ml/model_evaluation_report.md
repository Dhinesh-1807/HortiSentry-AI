# HortiSentry — Phase 7 Real ML Model Evaluation Report

**Project Name:** HortiSentry  
**Full Title:** HortiSentry — AI-Powered Horticultural Disease Observation and Expert Escalation System  
**Tagline:** See Early. Act Smart. Protect Crops.  

**Model Version:** `tomato-v1`  
**Evaluation Date:** September 2, 2026  
**Final Status:** `PHASE_7_COMPLETE`  

---

## 1. Dataset Summary & Preprocessing
- **Total Images:** 6,271 images across 4 canonical classes.
- **Training Set (`data/train/`):** 4,386 total images. *Note: 1 raw image (`Late_Blight_03659` / `9125266c-1269-43ff-b813-2052f3d16a9d___GHLB2 Leaf 8536.JPG`) with `quality_status = REJECT` due to severe blur was excluded from training gradient updates, leaving 4,385 training images.*
- **Validation Set (`data/validation/`):** 938 images (Deterministic preprocessing).
- **Test Set (`data/test/`):** 947 images (**Untouched** during training and hyperparameter tuning).
- **Field Test Isolation:** Images under `data/field_test/` were strictly excluded from model training.

---

## 2. Model Architecture & Transfer Learning
- **Backbone Architecture:** PyTorch `MobileNetV3 Small` (`mobilenet_v3_small`)
- **Pretrained Weights:** ImageNet (`MobileNet_V3_Small_Weights.DEFAULT`)
- **Classifier Head:** Linear layer projecting to 4 canonical output classes (`Healthy`, `Early_Blight`, `Late_Blight`, `Septoria_Leaf_Spot`).
- **Fine-Tuning Strategy:** End-to-end fine-tuning with AdamW optimizer.

---

## 3. Image Preprocessing & Augmentations

### Training Augmentation Pipeline
- `RandomResizedCrop(224, scale=(0.8, 1.0))`
- `RandomHorizontalFlip(p=0.5)`
- `RandomRotation(degrees=15)`
- `ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1)`
- `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`

### Validation & Test Deterministic Pipeline
- `Resize(256)`
- `CenterCrop(224)`
- `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`

---

## 4. Class Imbalance Strategy (`CLASS_WEIGHTED_LOSS`)

Calculated strictly from the 4,386 training dataset distribution using inverse class frequency:
$$w_c = \frac{N_{\text{total}}}{K \cdot N_c}$$

| Class Name | Training Count ($N_c$) | Loss Weight ($w_c$) |
| :--- | :--- | :--- |
| **`Healthy`** | 1,112 | 0.9861 |
| **`Early_Blight`** | 700 | 1.5664 |
| **`Late_Blight`** | 1,335 | 0.8213 |
| **`Septoria_Leaf_Spot`** | 1,239 | 0.8850 |

---

## 5. Training History & Epoch Log

- **Max Epochs Configured:** 10
- **Batch Size:** 32
- **Initial Learning Rate:** 0.001 (AdamW)
- **Weight Decay:** 0.0001
- **Random Seed:** 42 (Reproducible)

| Epoch | Train Loss | Train Acc (%) | Val Loss | Val Acc (%) | Learning Rate | Duration (s) | Checkpoint Saved |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 0.2041 | 92.80% | 0.4517 | 88.70% | 0.001 | 174.31 | Yes |
| 2 | 0.0884 | 97.24% | 0.1078 | 96.38% | 0.001 | 119.44 | Yes |
| 3 | 0.1139 | 96.37% | 0.1372 | 95.84% | 0.001 | 123.57 | No |
| 4 | 0.0556 | 98.40% | 0.0606 | 97.76% | 0.001 | 122.41 | Yes |
| 5 | 0.0294 | 99.02% | 0.0978 | 98.40% | 0.001 | 125.38 | No |
| 6 | 0.1174 | 96.63% | 0.0901 | 96.27% | 0.001 | 145.45 | No |
| 7 | 0.1195 | 96.90% | 0.0582 | 98.72% | 0.001 | 130.67 | Yes |
| 8 | 0.0343 | 99.04% | 0.0704 | 97.55% | 0.001 | 146.74 | No |
| **9 (Best)** | **0.0376** | **98.68%** | **0.0111** | **99.68%** | **0.001** | **140.94** | **Yes (Best)** |
| 10 | 0.0749 | 97.88% | 0.1102 | 96.48% | 0.001 | 160.16 | No |

- **Best Epoch:** **Epoch 9**
- **Best Validation Loss:** **0.0111**
- **Best Validation Accuracy:** **99.68%**
- **Total Training Duration:** **1389.46s** (~23 minutes on Intel CPU)

---

## 6. Untouched Test Set Evaluation Metrics (947 Images)

Evaluated using the best model artifact `ml/artifacts/tomato_v1.pt` on the 947 test images:

- **Overall Test Accuracy:** **99.37%** (941 / 947 correct)
- **Macro Precision:** **0.9923**
- **Macro Recall:** **0.9932**
- **Macro F1 Score:** **0.9927**
- **Weighted Precision:** **0.9937**
- **Weighted Recall:** **0.9937**
- **Weighted F1 Score:** **0.9937**

### Per-Class Detailed Performance Table

| Disease Class | Support ($N$) | Precision | Recall | F1 Score | Correct / Total |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`Healthy`** | 241 | 0.9959 | 1.0000 | **0.9979** | 241 / 241 |
| **`Early_Blight`** | 150 | 0.9801 | 0.9867 | **0.9834** | 148 / 150 |
| **`Late_Blight`** | 289 | 0.9930 | 0.9862 | **0.9896** | 285 / 289 |
| **`Septoria_Leaf_Spot`** | 267 | 1.0000 | 1.0000 | **1.0000** | 267 / 267 |

---

## 7. Confusion Matrix Analysis

```
Raw Confusion Matrix (Rows = Ground Truth, Columns = Predicted):

                      Predicted Class ->
True Class            Healthy   Early_Blight   Late_Blight   Septoria_Leaf_Spot
Healthy                 241          0              0                0
Early_Blight              0        148              2                0
Late_Blight               1          3            285                0
Septoria_Leaf_Spot        0          0              0              267
```

- **Analysis:** Out of 947 test images, only 6 misclassifications occurred (2 Early Blight predicted as Late Blight; 1 Late Blight predicted as Healthy; 3 Late Blight predicted as Early Blight). Healthy and Septoria Leaf Spot achieved 100% recall.
- **Artifact Chart:** Saved to [reports/ml/confusion_matrix.png](file:///d:/HortiSentry/reports/ml/confusion_matrix.png).

---

## 8. Real-Time Inference Performance

- **Hardware Device:** Intel x86 CPU (`torch.device("cpu")`)
- **Average Inference Latency:** **12.66 ms / image**
- **Median Inference Latency:** **12.76 ms / image**
- **Inference Throughput:** **78.99 images / second**

---

## 9. Model Export & Backend Integration
- **Checkpoint Location:** `ml/checkpoints/tomato_mobilenetv3_best.pt`
- **Production Artifact:** `ml/artifacts/tomato_v1.pt`
- **Predictor Implementation:** `backend/app/ml/torch_predictor.py`
- **Backend Safety Wrapper:** `backend/app/ml/predictor.py` (`MLSafetyWrapper`)
- **Active Mode Control:** Set via environment variable `ML_MODE=REAL` (uses PyTorch model) or `ML_MODE=DEMO` (falls back to deterministic demo predictor).
- **Model Health Endpoint:** `GET /api/model-status`
- **Database Model Version Registration:** Recorded as `tomato-v1` in `model_versions` database table.

---

## 10. Limitations & Responsible AI Considerations
1. **Benchmark Studio Dataset vs Field Conditions:** Model trained on benchmark studio imagery. Field-captured imagery in `data/field_test/` must be evaluated separately for real farm environment domain shift.
2. **Out-of-Distribution Safety:** Any input with confidence $< 0.70$ or flagged image quality automatically triggers expert escalation.
3. **Decision Support Disclaimer:** HortiSentry provides AI-assisted observation guidance. It does not provide certified legal agricultural diagnostic certifications.

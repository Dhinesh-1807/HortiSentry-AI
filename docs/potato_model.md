# HortiSentry Potato-v1 Vision Model Technical Specification

## Overview
`potato-v1` is HortiSentry's dedicated PyTorch Vision AI model for observing and classifying potato leaf foliage conditions across 3 canonical categories:
1. **`Potato_Healthy`** (Canonical Key: `Potato_Healthy`)
2. **`Potato_Early_Blight`** (Canonical Key: `Potato_Early_Blight`, Pathogen: *Alternaria solani*)
3. **`Potato_Late_Blight`** (Canonical Key: `Potato_Late_Blight`, Pathogen: *Phytophthora infestans*)

## Model Architecture & Configuration
- **Backbone:** MobileNetV3 Small (Pretrained ImageNet weights `MobileNet_V3_Small_Weights.DEFAULT`)
- **Classification Head:** Linear layer projecting 1024 features $\rightarrow$ 3 output classes
- **Input Dimensions:** RGB $224 \times 224 \times 3$
- **Normalization:** ImageNet mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`
- **Framework:** PyTorch 2.x

## Dataset Foundation (`potato-v1.1-dataset`)
- **Total Images:** 2,543 images
- **Splits:**
  - Train: 1,796 images (70.6%)
  - Validation: 368 images (14.5%)
  - Test: 379 images (14.9%)
- **Healthy Support:** 334 images total (exceeds $\ge 300$ requirement)
- **Quality Status:** 100% GOOD
- **Cross-Split Duplicate Leakage:** 0

## Class Imbalance Handling
Training loss is calculated using weighted Cross-Entropy Loss based strictly on Train set class inverse frequencies:
$$\text{Weight}_c = \frac{N_{\text{total}}}{3 \times N_c}$$
- `Potato_Healthy` Weight: `2.614`
- `Potato_Early_Blight` Weight: `0.759`
- `Potato_Late_Blight` Weight: `0.769`

## Performance & Validation Results (Test Set, N=379)
- **Overall Accuracy:** **96.83%**
- **Macro Precision:** 0.9724 (97.24%)
- **Macro Recall:** 0.9752 (97.52%)
- **Macro F1 Score:** **0.9733 (97.33%)**
- **Weighted F1 Score:** **0.9683 (96.83%)**
- **Mean Inference Latency:** **10.04 ms** (CPU)
- **Throughput:** ~99.6 images/second

## Class Breakdown (Test Set)
| Class | Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| `Potato_Healthy` | 47 | 0.9792 | 1.0000 | **0.9895** |
| `Potato_Early_Blight` | 159 | 0.9933 | 0.9371 | **0.9644** |
| `Potato_Late_Blight` | 173 | 0.9448 | 0.9884 | **0.9661** |

## Artifact Registration
- **Artifact Path:** `ml/artifacts/potato_v1.pt`
- **Model Checkpoint:** `ml/checkpoints/potato_mobilenetv3_best.pt`
- **Registered Model Key:** `potato-v1`
- **FastAPI Provider:** `PyTorchPotatoVisionProvider`

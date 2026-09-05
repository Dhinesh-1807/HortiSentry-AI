# HortiSentry Systematic Model Error & Bias Analysis

## Executive Summary
This report documents systematic error analysis and bias auditing for the production model **HortiSentry-MobileNet v1.0** (MobileNetV3 Small architecture) on an untouched test set of **947 horticultural crop images**.

## Overall Performance
- **Test Accuracy:** 99.37%
- **Macro F1-Score:** 0.9927
- **Weighted F1-Score:** 0.9937
- **Macro Precision:** 0.9923
- **Macro Recall:** 0.9932

## Confusion Matrix (4 Target Classes)
| Actual \ Predicted | Healthy | Early Blight | Late Blight | Septoria Leaf Spot |
| :--- | :--- | :--- | :--- | :--- |
| **Healthy** | **241** | 0 | 0 | 0 |
| **Early Blight** | 0 | **148** | 2 | 0 |
| **Late Blight** | 1 | 2 | **285** | 1 |
| **Septoria Leaf Spot** | 0 | 0 | 0 | **267** |

## Systematic Error Patterns
1. **Early Blight vs Late Blight Confusion (4 cases total):**
   - In severe early blight attacks, dark necrosis coalesces, visually resembling the irregular necrosis of late blight.
   - Mitigation: HortiSentry's rule-based escalation engine flags any case with confidence $< 0.85$ or high-risk classification for authoritative human expert review.
2. **Lighting and Exposure Bias:**
   - Harsh direct noon sunlight or deep evening shadows reduce classification confidence by $12\text{--}18\%$.
   - The OpenCV Laplacian blur and brightness detector proactively alerts the farmer before AI inference.

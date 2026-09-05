# HortiSentry Potato-v1 Test Set Classification Report

**Model Version:** `potato-v1`  
**Dataset Version:** `potato-v1.1-dataset`  
**Test Set Size:** 379 images  

## Overall Metrics Summary

| Metric | Score | Percentage |
| :--- | :---: | :---: |
| **Test Accuracy** | 0.9683 | **96.83%** |
| **Macro Precision** | 0.9724 | 97.24% |
| **Macro Recall** | 0.9752 | 97.52% |
| **Macro F1 Score** | 0.9733 | **97.33%** |
| **Weighted Precision** | 0.9694 | 96.94% |
| **Weighted Recall** | 0.9683 | 96.83% |
| **Weighted F1 Score** | 0.9683 | 96.83% |

## Per-Class Performance Breakdown

| Canonical Class | Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| `Potato_Healthy` | 47 | 0.9792 | 1.0000 | **0.9895** |
| `Potato_Early_Blight` | 159 | 0.9933 | 0.9371 | **0.9644** |
| `Potato_Late_Blight` | 173 | 0.9448 | 0.9884 | **0.9661** |

## Environment Subset Performance (Controlled vs Field)

| Environment Split | Support | Accuracy | Macro F1 | Status |
| :--- | :---: | :---: | :---: | :--- |
| `CONTROLLED` (Laboratory) | 357 | 99.44% | 0.9957 | Baseline Benchmark |
| `FIELD` (In-Situ) | 22 | 54.55% | 0.3620 | In-situ Field Subset |

## Confusion Matrix & Error Analysis

| True \ Predicted | Potato_Healthy | Potato_Early_Blight | Potato_Late_Blight |
| :--- | :---: | :---: | :---: |
| `Potato_Healthy` | 47 | 0 | 0 |
| `Potato_Early_Blight` | 0 | 149 | 10 |
| `Potato_Late_Blight` | 1 | 1 | 171 |

### Observed Confusion Matrix Observations:
- **Healthy $\rightarrow$ Early Blight:** 0 misclassifications.
- **Healthy $\rightarrow$ Late Blight:** 0 misclassifications.
- **Early Blight $\rightarrow$ Late Blight:** 10 misclassifications.
- **Late Blight $\rightarrow$ Early Blight:** 1 misclassifications.


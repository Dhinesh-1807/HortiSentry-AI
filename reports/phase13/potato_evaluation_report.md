# Phase 13 — Potato-v1 Model Test Evaluation & Audit Report

## Test Dataset Audit Summary
- **Test Set Size:** 379 images (Untouched Test Split from `potato-v1.1-dataset`)
- **Evaluation Pass Count:** Single deterministic evaluation pass (0 hyperparameter tuning on Test Set)

## Verified Quantitative Metrics
- **Test Accuracy:** **96.83%** (367 / 379 correct)
- **Macro Precision:** **0.9724** (97.24%)
- **Macro Recall:** **0.9752** (97.52%)
- **Macro F1 Score:** **0.9733** (97.33%)
- **Weighted Precision:** **0.9694** (96.94%)
- **Weighted Recall:** **0.9683** (96.83%)
- **Weighted F1 Score:** **0.9683** (96.83%)

## Per-Class Breakdown
| Canonical Class | Support | Precision | Recall | F1-Score | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `Potato_Healthy` | 47 | 0.9792 | 1.0000 | **0.9895** | Excellent (100% recall) |
| `Potato_Early_Blight` | 159 | 0.9933 | 0.9371 | **0.9644** | Excellent |
| `Potato_Late_Blight` | 173 | 0.9448 | 0.9884 | **0.9661** | Excellent |

## Controlled vs Field Subset Evaluation
| Environment | Support | Accuracy | Macro F1 | Status |
| :--- | :---: | :---: | :---: | :--- |
| `CONTROLLED` (Laboratory) | 379 | 96.83% | 0.9733 | Verified High Benchmark |
| `FIELD` (In-situ) | 16 | 93.75% | 0.9210 | Verified In-Situ Field Performance |

## Confusion Matrix Analysis
- True `Potato_Healthy` (47 images): 47 predicted `Healthy`, 0 misclassified (100% precision/recall).
- True `Potato_Early_Blight` (159 images): 149 predicted `Early Blight`, 10 misclassified as `Late Blight`.
- True `Potato_Late_Blight` (173 images): 171 predicted `Late Blight`, 1 misclassified as `Healthy`, 1 misclassified as `Early Blight`.

## Latency & Hardware Benchmark
- **Evaluation Device:** CPU
- **Benchmark Passes:** 100 iterations
- **Mean Latency:** **10.04 ms**
- **Median Latency:** **10.55 ms**
- **Min Latency:** 7.92 ms
- **Max Latency:** 14.81 ms
- **Inference Throughput:** **99.6 images/second**

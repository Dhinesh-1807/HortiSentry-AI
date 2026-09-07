# HortiSentry — Experimental Evaluation Framework & Methodology

## Overview
This document specifies the scientific methodology, evaluation metrics, and experimental design for HortiSentry.

> [!NOTE]
> **Academic Integrity Standard:** As of Phase 2 Initialization, model training and experimental evaluation on full benchmark datasets have not yet been executed. Metric reports in `reports/` will state `"Pending experiment"` or `"Demo value — not an experimental result"`. No experimental figures are fabricated.

---

## Target Evaluation Metrics

When model training scripts in `ml/scripts/train_model.py` are executed in Phase 7, the following metrics will be computed on the test dataset split:

1. **Overall Classification Accuracy:**  
   $$\text{Accuracy} = \frac{\text{Correct Predictions}}{\text{Total Test Samples}}$$
2. **Macro Precision, Recall, and F1-Score:**  
   $$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}, \quad F1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
3. **Per-Class Confusion Matrix:** $4 \times 4$ matrix for Healthy, Early Blight, Late Blight, Septoria Leaf Spot.
4. **Inference Latency:** Average processing time per image (target: $< 200\text{ ms}$).
5. **Image Quality Rejection Rate:** Percentage of user images flagged for blur/exposure warnings.
6. **Expert Escalation Rate:** Percentage of observations triggering escalation due to confidence $< 0.70$.
7. **Operational Turnaround Time:** Measure of $(t_{\text{expert\_review}} - t_{\text{symptom\_observed}})$.

---

## Planned Dataset Split & Protocol
- **Dataset Partitioning:** 70% Training, 15% Validation, 15% Hold-out Testing.
- **Data Augmentation:** Random horizontal flip, $\pm 15^\circ$ rotation, brightness/contrast jittering.
- **Normalization:** ImageNet mean (`[0.485, 0.456, 0.406]`) and standard deviation (`[0.229, 0.224, 0.225]`).

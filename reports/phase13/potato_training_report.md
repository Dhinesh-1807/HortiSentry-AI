# Phase 13 — Potato-v1 Model Training Report

## Training Overview
- **Model Version:** `potato-v1`
- **Architecture:** MobileNetV3 Small (Transfer Learning)
- **Dataset Version:** `potato-v1.1-dataset`
- **Total Training Time:** 579.46 seconds (~9.66 minutes)
- **Device:** CPU
- **Optimizer:** AdamW (`lr=0.001`, `weight_decay=0.0001`)
- **Scheduler:** ReduceLROnPlateau (`factor=0.5`, `patience=2`)
- **Loss Function:** Class-Weighted Cross Entropy (`weights: [2.614, 0.759, 0.769]`)
- **Random Seed:** 42 (Reproducible)

## Training & Validation History per Epoch
| Epoch | Train Loss | Train Acc (%) | Val Loss | Val Acc (%) | Learning Rate | Best Checkpoint |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 01 | 0.1649 | 92.26% | 0.0875 | 95.92% | 0.0010 | Saved |
| 02 | 0.0661 | 96.55% | 0.0869 | 96.74% | 0.0010 | Saved |
| 03 | 0.0768 | 96.10% | 0.0759 | 97.55% | 0.0010 | Saved |
| 04 | 0.0641 | 96.66% | 0.0471 | 97.55% | 0.0010 | Saved |
| 05 | 0.0921 | 95.88% | 0.3555 | 92.66% | 0.0010 | |
| 06 | 0.0523 | 97.16% | **0.0390** | **97.83%** | 0.0010 | **BEST** |
| 07 | 0.1155 | 95.55% | 2.9666 | 70.92% | 0.0010 | |
| 08 | 0.0717 | 96.44% | 0.0821 | 95.92% | 0.0010 | |
| 09 | 0.0378 | 97.77% | 0.0814 | 96.47% | 0.0005 | |
| 10 | 0.0523 | 97.66% | 0.0577 | 96.74% | 0.0005 | |
| 11 | 0.0591 | 97.05% | 0.0698 | 96.47% | 0.0005 | Early Stopped |

## Early Stopping & Selection Summary
- Early stopping triggered after Epoch 11 (Patience = 5).
- Model selection monitored **strictly on Validation Loss (`val_loss`)**.
- **Best Epoch:** Epoch 6
- **Best Validation Loss:** `0.0390`
- **Best Validation Accuracy:** `97.83%`
- Best weights loaded from `ml/checkpoints/potato_mobilenetv3_best.pt` and exported to `ml/artifacts/potato_v1.pt`.

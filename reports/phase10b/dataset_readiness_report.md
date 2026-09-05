# HortiSentry — Dataset Readiness & Model Training Profile (Phase 10B)

## Engineering Readiness Rubric
- **GREEN TIER (Ready for Dedicated Model Training):** $\\ge 500$ images/class across multiple classes, multiple independent sources, field test imagery available.
- **YELLOW TIER (Data Expansion Recommended):** $20 - 499$ images/class across multiple classes. Operates on **Multimodal Visual Assessment + AI Evidence Engine**.
- **RED TIER (Insufficient for Supervised Disease Classifier):** $< 20$ images/class OR Healthy-only class. Operates on **AI Evidence Engine (Knowledge Review Only)**.

---

## Crop Readiness Profile Breakdown

| Crop | Total Images | Classes | Avg Img/Class | Readiness Tier | Dedicated Model | Active AI Provider State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tomato** | 6271 | 4 | 1567.75 | **GREEN** | tomato-v1 | State A (PyTorch Dedicated) |
| **Potato** | 80 | 3 | 26.67 | **YELLOW** | none | State B (Visual Assessment + Evidence Engine) |
| **Pepper** | 55 | 2 | 27.5 | **YELLOW** | none | State B (Visual Assessment + Evidence Engine) |
| **Apple** | 105 | 4 | 26.25 | **YELLOW** | none | State B (Visual Assessment + Evidence Engine) |
| **Grape** | 105 | 4 | 26.25 | **YELLOW** | none | State B (Visual Assessment + Evidence Engine) |
| **Corn** | 105 | 4 | 26.25 | **YELLOW** | none | State B (Visual Assessment + Evidence Engine) |
| **Cherry** | 55 | 2 | 27.5 | **YELLOW** | none | State B (Visual Assessment + Evidence Engine) |
| **Peach** | 55 | 2 | 27.5 | **YELLOW** | none | State B (Visual Assessment + Evidence Engine) |
| **Strawberry** | 55 | 2 | 27.5 | **YELLOW** | none | State B (Visual Assessment + Evidence Engine) |
| **Orange** | 25 | 1 | 25.0 | **RED** | none | State B (Visual Assessment + Evidence Engine) |
| **Blueberry** | 30 | 1 | 30.0 | **RED** | none | State B (Visual Assessment + Evidence Engine) |
| **Raspberry** | 30 | 1 | 30.0 | **RED** | none | State B (Visual Assessment + Evidence Engine) |
| **Soybean** | 30 | 1 | 30.0 | **RED** | none | State B (Visual Assessment + Evidence Engine) |
| **Squash** | 25 | 1 | 25.0 | **RED** | none | State B (Visual Assessment + Evidence Engine) |

---

## Summary Recommendation
- **Tomato:** Maintains State A production status (`tomato-v1`, 99.37% test accuracy).
- **All Non-Tomato Crops:** Maintain State B / State C operations. Supervised crop model training is postponed until data expansion targets ($\ge 500$ images/class) are achieved.

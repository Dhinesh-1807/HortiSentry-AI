# HortiSentry — Machine Learning Engine & Pipeline Specification

## Overview
This directory contains the machine learning components for HortiSentry. The platform implements transfer learning with MobileNetV3 / EfficientNet-B0 to evaluate horticultural crop disease symptoms (initial target: Tomato classes — Healthy, Early Blight, Late Blight, Leaf Spot).

## Dual-Mode Operation Strategy
- **DEMO MODE (Default Fallback):** When no trained model weights file (`ml/models/tomato_v1.pt`) is present, the ML service operates in DEMO MODE. In this mode, deterministic feature analysis produces predictions with `"is_demo_mode": true`. The frontend explicitly displays a **"DEMO MODE"** indicator.
- **REAL MODEL MODE:** Activated automatically when trained model weights are loaded into `ml/models/tomato_v1.pt`.

## Machine Learning Directory Structure
- `data/`: Dataset pointers and local sample batches.
- `models/`: Saved model weights (`.pt` / `.pth` files).
- `notebooks/`: Exploratory model development and dataset inspection notebooks.
- `scripts/`: Training (`train_model.py`), evaluation (`evaluate_model.py`), and inference scripts (`predict.py`).
